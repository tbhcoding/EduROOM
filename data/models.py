from data.database import db
from utils.auth import hash_password, verify_password
from datetime import datetime

# Import realtime client for WebSocket updates
try:
    from utils.websocket_client import realtime
    REALTIME_ENABLED = True
except ImportError:
    REALTIME_ENABLED = False

class UserModel:
    @staticmethod
    def authenticate(id_number, password):
        """Authenticate user by ID number and password only"""
        db.connect()
        query = "SELECT * FROM users WHERE id_number = %s AND is_active = TRUE"
        user = db.fetch_one(query, (id_number,))
        db.disconnect()
        
        if user and verify_password(password, user['password_hash']):
            return user
        return None
    
    @staticmethod
    def authenticate_with_email(email, id_number, password):
        """Authenticate user by email, ID number, and password"""
        db.connect()
        query = "SELECT * FROM users WHERE email = %s AND id_number = %s AND is_active = TRUE"
        user = db.fetch_one(query, (email, id_number))
        db.disconnect()
        
        if user and verify_password(password, user['password_hash']):
            return user
        return None
    
    @staticmethod
    def create_user(email, id_number, password, role, full_name):
        """Create a new user"""
        db.connect()
        password_hash = hash_password(password)
        query = """
            INSERT INTO users (email, id_number, password_hash, role, full_name)
            VALUES (%s, %s, %s, %s, %s)
        """
        user_id = db.execute_query(query, (email, id_number, password_hash, role, full_name))
        db.disconnect()
        return user_id
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        db.connect()
        query = "SELECT * FROM users WHERE id = %s"
        user = db.fetch_one(query, (user_id,))
        db.disconnect()
        return user
    
    @staticmethod
    def check_email_exists(email):
        """Check if email already exists"""
        db.connect()
        query = "SELECT id FROM users WHERE email = %s"
        result = db.fetch_one(query, (email,))
        db.disconnect()
        return result is not None
    
    @staticmethod
    def check_id_number_exists(id_number):
        """Check if ID number already exists"""
        db.connect()
        query = "SELECT id FROM users WHERE id_number = %s"
        result = db.fetch_one(query, (id_number,))
        db.disconnect()
        return result is not None
    
    # In models.py - add new method
    @staticmethod
    def check_account_status(email, id_number):
        """Check if account exists but is disabled"""
        db.connect()
        query = "SELECT is_active FROM users WHERE email = %s AND id_number = %s"
        user = db.fetch_one(query, (email, id_number))
        db.disconnect()
        
        if user and not user['is_active']:
            return False, "Your account has been deactivated. Please contact an administrator."
        return True, None
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """Change user password after verifying current password"""
        db.connect()
        
        # First, get the user's current password hash
        query = "SELECT password_hash FROM users WHERE id = %s"
        user = db.fetch_one(query, (user_id,))
        
        if not user:
            db.disconnect()
            return False, "User not found"
        
        # Verify current password
        if not verify_password(current_password, user['password_hash']):
            db.disconnect()
            return False, "Current password is incorrect"
        
        # Hash new password and update
        new_password_hash = hash_password(new_password)
        update_query = "UPDATE users SET password_hash = %s WHERE id = %s"
        result = db.execute_query(update_query, (new_password_hash, user_id))
        db.disconnect()
        
        if result is None:  # Check if update failed
            return False, "Error updating password"
        
        return True, "Password changed successfully"

    # ==================== USER MANAGEMENT (Admin) ====================
    
    @staticmethod
    def get_all_users():
        """Get all users for admin management"""
        db.connect()
        query = """
            SELECT id, email, id_number, role, full_name, is_active, created_at
            FROM users
            ORDER BY created_at DESC
        """
        users = db.fetch_all(query)
        db.disconnect()
        return users if users else []
    
    @staticmethod
    def get_users_by_role(role):
        """Get users filtered by role"""
        db.connect()
        query = """
            SELECT id, email, id_number, role, full_name, is_active, created_at
            FROM users
            WHERE role = %s
            ORDER BY created_at DESC
        """
        users = db.fetch_all(query, (role,))
        db.disconnect()
        return users if users else []
    
    @staticmethod
    def toggle_user_status(user_id):
        """Toggle user active/inactive status"""
        db.connect()
        # First get current status
        query = "SELECT is_active FROM users WHERE id = %s"
        user = db.fetch_one(query, (user_id,))
        
        if not user:
            db.disconnect()
            return False, "User not found"
        
        new_status = not user['is_active']
        update_query = "UPDATE users SET is_active = %s WHERE id = %s"
        result = db.execute_query(update_query, (new_status, user_id))
        db.disconnect()
        
        if result is None:
            return False, "Error updating user status"
        
        status_text = "activated" if new_status else "deactivated"
        return True, f"User {status_text} successfully"
    
    @staticmethod
    def delete_user(user_id):
        """Permanently delete a user (use with caution)"""
        db.connect()
        
        # Check if user exists
        check_query = "SELECT id, full_name FROM users WHERE id = %s"
        user = db.fetch_one(check_query, (user_id,))
        
        if not user:
            db.disconnect()
            return False, "User not found"
        
        # Delete the user (cascades to reservations due to FK)
        delete_query = "DELETE FROM users WHERE id = %s"
        result = db.execute_query(delete_query, (user_id,))
        db.disconnect()
        
        if result is None:
            return False, "Error deleting user"
        
        return True, f"User '{user['full_name']}' deleted successfully"
    
    @staticmethod
    def update_user_role(user_id, new_role):
        """Update a user's role"""
        db.connect()
        
        # Validate role
        valid_roles = ['admin', 'faculty', 'student']
        if new_role not in valid_roles:
            db.disconnect()
            return False, f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        
        update_query = "UPDATE users SET role = %s WHERE id = %s"
        result = db.execute_query(update_query, (new_role, user_id))
        db.disconnect()
        
        if result is None:
            return False, "Error updating user role"
        
        return True, f"User role updated to {new_role}"
    
    @staticmethod
    def update_user_profile(user_id, full_name=None, email=None):
        """Update user profile fields"""
        db.connect()
        
        updates = []
        params = []
        
        if full_name:
            updates.append("full_name = %s")
            params.append(full_name)
        
        if email:
            # Check if email already exists for another user
            check_query = "SELECT id FROM users WHERE email = %s AND id != %s"
            existing = db.fetch_one(check_query, (email, user_id))
            if existing:
                db.disconnect()
                return False, "Email already in use by another user"
            updates.append("email = %s")
            params.append(email)
        
        if not updates:
            db.disconnect()
            return False, "No fields to update"
        
        params.append(user_id)
        update_query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
        result = db.execute_query(update_query, tuple(params))
        db.disconnect()
        
        if result is None:
            return False, "Error updating profile"
        
        return True, "Profile updated successfully"
    
    @staticmethod
    def admin_reset_password(user_id, new_password):
        """Admin reset password without requiring current password"""
        db.connect()
        
        new_password_hash = hash_password(new_password)
        update_query = "UPDATE users SET password_hash = %s WHERE id = %s"
        result = db.execute_query(update_query, (new_password_hash, user_id))
        db.disconnect()
        
        if result is None:
            return False, "Error resetting password"
        
        return True, "Password reset successfully"
    
    @staticmethod
    def get_user_stats():
        """Get user statistics for admin dashboard"""
        db.connect()
        query = """
            SELECT 
                COUNT(*) as total_users,
                SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) as admin_count,
                SUM(CASE WHEN role = 'faculty' THEN 1 ELSE 0 END) as faculty_count,
                SUM(CASE WHEN role = 'student' THEN 1 ELSE 0 END) as student_count,
                SUM(CASE WHEN is_active = TRUE THEN 1 ELSE 0 END) as active_count,
                SUM(CASE WHEN is_active = FALSE THEN 1 ELSE 0 END) as inactive_count
            FROM users
        """
        result = db.fetch_one(query)
        db.disconnect()
        return result if result else {
            'total_users': 0, 'admin_count': 0, 'faculty_count': 0,
            'student_count': 0, 'active_count': 0, 'inactive_count': 0
        }
class ClassroomModel:
    @staticmethod
    def get_all_classrooms():
        """Get all classrooms"""
        db.connect()
        query = "SELECT * FROM classrooms ORDER BY room_name"
        classrooms = db.fetch_all(query)
        db.disconnect()
        return classrooms
    
    @staticmethod
    def get_classroom_by_id(classroom_id):
        """Get classroom by ID"""
        db.connect()
        query = "SELECT * FROM classrooms WHERE id = %s"
        classroom = db.fetch_one(query, (classroom_id,))
        db.disconnect()
        return classroom

    @staticmethod
    def get_classroom_reservations(classroom_id):
        """Get all reservations for a specific classroom with user details"""
        db.connect()
        query = """
            SELECT 
                r.id,
                r.reservation_date,
                r.start_time,
                r.end_time,
                r.purpose,
                r.status,
                u.full_name as reserved_by
            FROM reservations r
            JOIN users u ON r.user_id = u.id
            WHERE r.classroom_id = %s
            ORDER BY r.reservation_date DESC, r.start_time ASC
        """
        reservations = db.fetch_all(query, (classroom_id,))
        db.disconnect()
        return reservations

class ReservationModel:
    @staticmethod
    def get_user_reservations(user_id):
        """Get all reservations for a user"""
        db.connect()
        query = """
            SELECT r.*, c.room_name, c.building, c.image_url
            FROM reservations r
            JOIN classrooms c ON r.classroom_id = c.id
            WHERE r.user_id = %s
            ORDER BY r.reservation_date DESC, r.start_time DESC
        """
        reservations = db.fetch_all(query, (user_id,))
        db.disconnect()
        return reservations
    
    @staticmethod
    def get_all_reservations():
        """Get all reservations (for admin)"""
        db.connect()
        query = """
            SELECT r.*, c.room_name, c.building, c.image_url, u.full_name, u.email
            FROM reservations r
            JOIN classrooms c ON r.classroom_id = c.id
            JOIN users u ON r.user_id = u.id
            ORDER BY r.created_at DESC
        """
        reservations = db.fetch_all(query)
        db.disconnect()
        return reservations
    
    @staticmethod
    def check_availability(classroom_id, reservation_date, start_time, end_time, exclude_reservation_id=None):
        """Check if a classroom is available for the given date and time range."""
        db.connect()
        
        query = """
            SELECT COUNT(*) as count FROM reservations
            WHERE classroom_id = %s 
            AND reservation_date = %s
            AND status IN ('approved', 'pending', 'ongoing')
            AND start_time < %s   -- Existing reservation starts before new ends
            AND end_time > %s     -- Existing reservation ends after new starts
        """
        
        params = [classroom_id, reservation_date, end_time, start_time]
        
        if exclude_reservation_id:
            query += " AND id != %s"
            params.append(exclude_reservation_id)
        
        result = db.fetch_one(query, tuple(params))
        db.disconnect()
        
        return result['count'] == 0

    @staticmethod
    def get_occupied_slots(classroom_id, reservation_date):
        """Get all occupied time slots for a classroom on a specific date"""
        db.connect()
        query = """
            SELECT start_time, end_time, purpose, status
            FROM reservations
            WHERE classroom_id = %s 
            AND reservation_date = %s
            AND status IN ('approved', 'pending', 'ongoing')
            ORDER BY start_time
        """
        results = db.fetch_all(query, (classroom_id, reservation_date))
        db.disconnect()
        return results if results else []
    
    @staticmethod
    def get_reservation_by_id(reservation_id):
        """Get a single reservation by ID"""
        db.connect()
        query = """
            SELECT r.*, c.room_name, c.building, c.image_url
            FROM reservations r
            JOIN classrooms c ON r.classroom_id = c.id
            WHERE r.id = %s
        """
        reservation = db.fetch_one(query, (reservation_id,))
        db.disconnect()
        return reservation
    
    @staticmethod
    def update_reservation(reservation_id, reservation_date, start_time, end_time, purpose):
        """Update an existing reservation"""
        db.connect()
        query = """
            UPDATE reservations 
            SET reservation_date = %s, start_time = %s, end_time = %s, purpose = %s, status = 'pending'
            WHERE id = %s
        """
        result = db.execute_query(query, (reservation_date, start_time, end_time, purpose, reservation_id))
        db.disconnect()
        return result is not None
    
    @staticmethod
    def cancel_reservation(reservation_id):
        """Cancel a reservation"""
        db.connect()
        query = "UPDATE reservations SET status = 'cancelled' WHERE id = %s"
        result = db.execute_query(query, (reservation_id,))
        db.disconnect()
        return result is not None
    
    @staticmethod
    def set_ongoing(reservation_id):
        """Set reservation status to ongoing"""
        db.connect()
        query = "UPDATE reservations SET status = 'ongoing' WHERE id = %s AND status = 'approved'"
        result = db.execute_query(query, (reservation_id,))
        db.disconnect()
        return result is not None
    
    @staticmethod
    def set_done(reservation_id):
        """Set reservation status to done"""
        db.connect()
        query = "UPDATE reservations SET status = 'done' WHERE id = %s AND status = 'ongoing'"
        result = db.execute_query(query, (reservation_id,))
        db.disconnect()
        return result is not None
    
    @staticmethod
    def update_reservation_statuses():
        """
        Automatically update reservation statuses based on current date/time.
        - approved → ongoing: when current time is within reservation time range
        - ongoing → done: when current time is past end_time
        Returns True on success.
        """
        db.connect()
        
        # Set approved reservations to ongoing if current time is within their time range
        ongoing_query = """
            UPDATE reservations 
            SET status = 'ongoing' 
            WHERE status = 'approved'
            AND reservation_date = CURDATE()
            AND start_time <= CURTIME()
            AND end_time > CURTIME()
        """
        db.execute_query(ongoing_query)
        
        # Set ongoing reservations to done if current time is past end_time
        done_query = """
            UPDATE reservations 
            SET status = 'done' 
            WHERE status = 'ongoing'
            AND (
                reservation_date < CURDATE()
                OR (reservation_date = CURDATE() AND end_time <= CURTIME())
            )
        """
        db.execute_query(done_query)
        
        # Also mark approved reservations from past dates as done
        past_done_query = """
            UPDATE reservations 
            SET status = 'done' 
            WHERE status = 'approved'
            AND reservation_date < CURDATE()
        """
        db.execute_query(past_done_query)
        
        db.disconnect()
        return True
    
    @staticmethod
    def can_modify_reservation(reservation_id, user_id):
        """Check if user can modify this reservation"""
        db.connect()
        query = """
            SELECT id FROM reservations 
            WHERE id = %s AND user_id = %s AND status IN ('pending', 'approved')
        """
        result = db.fetch_one(query, (reservation_id, user_id))
        db.disconnect()
        return result is not None

    @staticmethod
    def get_reservations_by_classroom_and_date(classroom_id, reservation_date):
        """Get all approved/ongoing reservations for a classroom on a specific date"""
        db.connect()
        query = """
            SELECT id, classroom_id, reservation_date, start_time, end_time, status
            FROM reservations
            WHERE classroom_id = %s 
            AND reservation_date = %s
            AND status IN ('approved', 'ongoing')
            ORDER BY start_time
        """
        reservations = db.fetch_all(query, (classroom_id, reservation_date))
        db.disconnect()
        return reservations
    
    @staticmethod
    def get_available_classrooms(reservation_date, start_time, end_time):
        """Get all classrooms that are available for the given date and time range"""
        db.connect()
        query = """
            SELECT c.* 
            FROM classrooms c
            WHERE c.id NOT IN (
                SELECT DISTINCT r.classroom_id
                FROM reservations r
                WHERE r.reservation_date = %s
                AND r.status IN ('approved', 'ongoing')
                AND (
                    (r.start_time < %s AND r.end_time > %s) OR
                    (r.start_time < %s AND r.end_time > %s) OR
                    (r.start_time >= %s AND r.end_time <= %s)
                )
            )
            ORDER BY c.room_name
        """
        classrooms = db.fetch_all(query, (
            reservation_date, 
            end_time, start_time,  # overlaps start
            end_time, start_time,  # overlaps end
            start_time, end_time   # contained within
        ))
        db.disconnect()
        return classrooms

    @staticmethod
    def create_reservation(classroom_id, user_id, reservation_date, start_time, end_time, purpose):
        """Create a new reservation and notify admins"""
        db.connect()
        query = """
            INSERT INTO reservations 
            (classroom_id, user_id, reservation_date, start_time, end_time, purpose)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        reservation_id = db.execute_query(
            query, 
            (classroom_id, user_id, reservation_date, start_time, end_time, purpose)
        )
        
        # Get room name for notification
        room_query = "SELECT room_name FROM classrooms WHERE id = %s"
        room = db.fetch_one(room_query, (classroom_id,))
        
        db.disconnect()
        
        # Notify admins about new reservation
        if room and reservation_id:
            from data.models import NotificationModel
            NotificationModel.notify_new_reservation(reservation_id, room['room_name'])
        
            if REALTIME_ENABLED and realtime.connected:
                realtime.send("new_reservation", {
                    "reservation_id": reservation_id,
                    "room_name": room['room_name'],
                    "message": f"New reservation for {room['room_name']}"
                })
        
        return reservation_id


    @staticmethod
    def approve_reservation(reservation_id):
        """Approve a reservation and notify the faculty member"""
        db.connect()
        
        # Get reservation details before updating
        details_query = """
            SELECT r.user_id, r.classroom_id, c.room_name, r.reservation_date, r.start_time, r.end_time
            FROM reservations r
            JOIN classrooms c ON r.classroom_id = c.id
            WHERE r.id = %s
        """
        reservation = db.fetch_one(details_query, (reservation_id,))
        
        # Update status to approved
        query = "UPDATE reservations SET status = 'approved' WHERE id = %s"
        db.execute_query(query, (reservation_id,))
        
        db.disconnect()
        
        # Notify the faculty member about approval
        if reservation:
            from data.models import NotificationModel
            
            date_str = reservation['reservation_date'].strftime('%B %d, %Y') if hasattr(reservation['reservation_date'], 'strftime') else str(reservation['reservation_date'])
            message = f"Your reservation for {reservation['room_name']} on {date_str} has been approved"
            
            # Create notification in database
            NotificationModel.create_notification(
                user_id=reservation['user_id'],
                message=message,
                reservation_id=reservation_id
            )
            
            # Send real-time WebSocket notification
            if REALTIME_ENABLED and realtime.connected:
                realtime.send("reservation_approved", {
                    "reservation_id": reservation_id,
                    "user_id": reservation['user_id'],
                    "room_name": reservation['room_name'],
                    "message": message
                })
        
        return True

    @staticmethod
    def reject_reservation(reservation_id):
        """Reject a reservation and notify the faculty member"""
        db.connect()
        
        # Get reservation details before updating
        details_query = """
            SELECT r.user_id, r.classroom_id, c.room_name, r.reservation_date, r.start_time, r.end_time
            FROM reservations r
            JOIN classrooms c ON r.classroom_id = c.id
            WHERE r.id = %s
        """
        reservation = db.fetch_one(details_query, (reservation_id,))
        
        # Update status to rejected
        query = "UPDATE reservations SET status = 'rejected' WHERE id = %s"
        db.execute_query(query, (reservation_id,))
        
        db.disconnect()
        
        # Notify the faculty member about rejection
        if reservation:
            from data.models import NotificationModel
            
            date_str = reservation['reservation_date'].strftime('%B %d, %Y') if hasattr(reservation['reservation_date'], 'strftime') else str(reservation['reservation_date'])
            message = f"Your reservation for {reservation['room_name']} on {date_str} has been rejected"
            
            # Create notification in database
            NotificationModel.create_notification(
                user_id=reservation['user_id'],
                message=message,
                reservation_id=reservation_id
            )
            
            # Send real-time WebSocket notification
            if REALTIME_ENABLED and realtime.connected:
                realtime.send("reservation_rejected", {
                    "reservation_id": reservation_id,
                    "user_id": reservation['user_id'],
                    "room_name": reservation['room_name'],
                    "message": message
                })
        return True

class ActivityLogModel:
    @staticmethod
    def log_activity(user_id, action, details=None, ip_address=None):
        """Log user activity"""
        db.connect()
        query = """
            INSERT INTO activity_logs (user_id, action, details, ip_address)
            VALUES (%s, %s, %s, %s)
        """
        db.execute_query(query, (user_id, action, details, ip_address))
        db.disconnect()

class NotificationModel:
    @staticmethod
    def create_notification(user_id, message, reservation_id=None):
        """Create a new notification for a user"""
        db.connect()
        query = """
            INSERT INTO notifications (user_id, message, reservation_id)
            VALUES (%s, %s, %s)
        """
        notification_id = db.execute_query(query, (user_id, message, reservation_id))
        db.disconnect()
        return notification_id
    
    @staticmethod
    def get_user_notifications(user_id, limit=5, unread_only=False):
        """Get notifications for a user"""
        db.connect()
        
        if unread_only:
            query = """
                SELECT * FROM notifications
                WHERE user_id = %s AND is_read = FALSE
                ORDER BY created_at DESC
                LIMIT %s
            """
        else:
            query = """
                SELECT * FROM notifications
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """
        
        notifications = db.fetch_all(query, (user_id, limit))
        db.disconnect()
        return notifications if notifications else []
    
    @staticmethod
    def get_unread_count(user_id):
        """Get count of unread notifications for a user"""
        db.connect()
        query = """
            SELECT COUNT(*) as count 
            FROM notifications
            WHERE user_id = %s AND is_read = FALSE
        """
        result = db.fetch_one(query, (user_id,))
        db.disconnect()
        return result['count'] if result else 0
    
    @staticmethod
    def mark_as_read(notification_id):
        """Mark a notification as read"""
        db.connect()
        query = "UPDATE notifications SET is_read = TRUE WHERE id = %s"
        db.execute_query(query, (notification_id,))
        db.disconnect()
        return True
    
    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all notifications as read for a user"""
        db.connect()
        query = "UPDATE notifications SET is_read = TRUE WHERE user_id = %s"
        db.execute_query(query, (user_id,))
        db.disconnect()
        return True
    
    @staticmethod
    def delete_notification(notification_id):
        """Delete a notification"""
        db.connect()
        query = "DELETE FROM notifications WHERE id = %s"
        db.execute_query(query, (notification_id,))
        db.disconnect()
        return True
    
    @staticmethod
    def notify_new_reservation(reservation_id, room_name):
        """Notify all admins about a new reservation"""
        db.connect()
        
        # Get all admin users
        admin_query = "SELECT id FROM users WHERE role = 'admin' AND is_active = TRUE"
        admins = db.fetch_all(admin_query)
        
        if admins:
            message = f"New Reservation for {room_name}"
            for admin in admins:
                NotificationModel.create_notification(admin['id'], message, reservation_id)
        
        db.disconnect()
    
    @staticmethod
    def notify_reservation_approved(user_id, reservation_id, room_name):
        """Notify faculty member that their reservation was approved"""
        message = f"Reservation for {room_name} approved"
        return NotificationModel.create_notification(user_id, message, reservation_id)
    
    @staticmethod
    def notify_reservation_rejected(user_id, reservation_id, room_name):
        """Notify faculty member that their reservation was rejected"""
        message = f"Reservation for {room_name} rejected"
        return NotificationModel.create_notification(user_id, message, reservation_id)