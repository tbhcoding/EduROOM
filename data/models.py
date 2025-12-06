from data.database import db
from utils.auth import hash_password, verify_password
from datetime import datetime

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
        db.execute_query(update_query, (new_password_hash, user_id))
        db.disconnect()
        
        return True, "Password changed successfully"


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
    def create_reservation(classroom_id, user_id, reservation_date, start_time, end_time, purpose):
        """Create a new reservation"""
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
        db.disconnect()
        return reservation_id
    
    @staticmethod
    def get_user_reservations(user_id):
        """Get all reservations for a user"""
        db.connect()
        query = """
            SELECT r.*, c.room_name, c.building
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
            SELECT r.*, c.room_name, c.building, u.full_name, u.email
            FROM reservations r
            JOIN classrooms c ON r.classroom_id = c.id
            JOIN users u ON r.user_id = u.id
            ORDER BY r.created_at DESC
        """
        reservations = db.fetch_all(query)
        db.disconnect()
        return reservations
    
    @staticmethod
    def approve_reservation(reservation_id):
        """Approve a reservation"""
        db.connect()
        query = "UPDATE reservations SET status = 'approved' WHERE id = %s"
        db.execute_query(query, (reservation_id,))
        db.disconnect()
        return True
    
    @staticmethod
    def reject_reservation(reservation_id):
        """Reject a reservation"""
        db.connect()
        query = "UPDATE reservations SET status = 'rejected' WHERE id = %s"
        db.execute_query(query, (reservation_id,))
        db.disconnect()
        return True
    
    @staticmethod
    def check_availability(classroom_id, reservation_date, start_time, end_time, exclude_reservation_id=None):
        """Check if classroom is available at given time"""
        db.connect()
        query = """
            SELECT COUNT(*) as count FROM reservations
            WHERE classroom_id = %s 
            AND reservation_date = %s
            AND status = 'approved'
            AND (
                (start_time < %s AND end_time > %s) OR
                (start_time < %s AND end_time > %s) OR
                (start_time >= %s AND end_time <= %s)
            )
        """
        params = [classroom_id, reservation_date, end_time, start_time, end_time, start_time, start_time, end_time]
        
        if exclude_reservation_id:
            query += " AND id != %s"
            params.append(exclude_reservation_id)
        
        result = db.fetch_one(query, tuple(params))
        db.disconnect()
        return result['count'] == 0
    
    @staticmethod
    def get_reservation_by_id(reservation_id):
        """Get a single reservation by ID"""
        db.connect()
        query = """
            SELECT r.*, c.room_name, c.building
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
        
