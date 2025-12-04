"""
Analytics Module
================
Provides data aggregation and analysis for dashboard visualizations

Features:
- Reservation statistics and trends
- Classroom utilization metrics
- User activity analytics
- Time-based patterns
"""

from data.database import db
from datetime import datetime, timedelta

class AnalyticsModel:
    """Analytics model for dashboard data"""
    
    @staticmethod
    def get_reservation_summary():
        """
        Get overall reservation statistics
        
        Returns:
            dict: Summary statistics including total, pending, approved, rejected counts
        """
        db.connect()
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected
            FROM reservations
        """
        result = db.fetch_one(query)
        db.disconnect()
        return result or {"total": 0, "pending": 0, "approved": 0, "rejected": 0}
    
    @staticmethod
    def get_reservations_by_status():
        """
        Get reservation counts grouped by status
        
        Returns:
            list: List of dicts with status and count
        """
        db.connect()
        query = """
            SELECT 
                status,
                COUNT(*) as count
            FROM reservations
            GROUP BY status
        """
        results = db.fetch_all(query)
        db.disconnect()
        return results
    
    @staticmethod
    def get_popular_classrooms(limit=5):
        """
        Get most frequently reserved classrooms
        
        Args:
            limit (int): Number of top classrooms to return
            
        Returns:
            list: List of classrooms with reservation counts
        """
        db.connect()
        query = """
            SELECT 
                c.room_name,
                c.building,
                COUNT(r.id) as reservation_count
            FROM classrooms c
            LEFT JOIN reservations r ON c.id = r.classroom_id
            GROUP BY c.id, c.room_name, c.building
            ORDER BY reservation_count DESC
            LIMIT %s
        """
        results = db.fetch_all(query, (limit,))
        db.disconnect()
        return results
    
    @staticmethod
    def get_reservations_by_date(days=7):
        """
        Get reservation counts for the last N days
        
        Args:
            days (int): Number of days to look back
            
        Returns:
            list: List of dicts with date and count
        """
        db.connect()
        query = """
            SELECT 
                DATE(reservation_date) as date,
                COUNT(*) as count
            FROM reservations
            WHERE reservation_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            GROUP BY DATE(reservation_date)
            ORDER BY date
        """
        results = db.fetch_all(query, (days,))
        db.disconnect()
        return results
    
    @staticmethod
    def get_reservations_by_time_slot():
        """
        Get reservation distribution by time of day
        
        Returns:
            list: List of time slots with counts
        """
        db.connect()
        query = """
            SELECT 
                HOUR(start_time) as hour,
                COUNT(*) as count
            FROM reservations
            WHERE status = 'approved'
            GROUP BY HOUR(start_time)
            ORDER BY hour
        """
        results = db.fetch_all(query)
        db.disconnect()
        return results
    
    @staticmethod
    def get_faculty_activity():
        """
        Get reservation counts by faculty member
        
        Returns:
            list: List of faculty with reservation counts
        """
        db.connect()
        query = """
            SELECT 
                u.full_name,
                COUNT(r.id) as reservation_count
            FROM users u
            LEFT JOIN reservations r ON u.id = r.user_id
            WHERE u.role = 'faculty'
            GROUP BY u.id, u.full_name
            ORDER BY reservation_count DESC
        """
        results = db.fetch_all(query)
        db.disconnect()
        return results
    
    @staticmethod
    def get_classroom_utilization():
        """
        Calculate utilization rate for each classroom
        
        Returns:
            list: List of classrooms with utilization percentages
        """
        db.connect()
        query = """
            SELECT 
                c.room_name,
                c.building,
                COUNT(r.id) as total_reservations,
                SUM(CASE WHEN r.status = 'approved' THEN 1 ELSE 0 END) as approved_reservations
            FROM classrooms c
            LEFT JOIN reservations r ON c.id = r.classroom_id
            GROUP BY c.id, c.room_name, c.building
            ORDER BY total_reservations DESC
        """
        results = db.fetch_all(query)
        db.disconnect()
        return results
    
    @staticmethod
    def get_approval_rate():
        """
        Calculate overall approval rate
        
        Returns:
            dict: Approval statistics
        """
        db.connect()
        query = """
            SELECT 
                COUNT(*) as total_processed,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected
            FROM reservations
            WHERE status IN ('approved', 'rejected')
        """
        result = db.fetch_one(query)
        db.disconnect()
        
        if result and result['total_processed'] > 0:
            approval_rate = (result['approved'] / result['total_processed']) * 100
            result['approval_rate'] = round(approval_rate, 1)
        else:
            result = {"total_processed": 0, "approved": 0, "rejected": 0, "approval_rate": 0}
        
        return result
    
    @staticmethod
    def get_peak_hours():
        """
        Identify peak reservation hours
        
        Returns:
            list: Hours with highest reservation counts
        """
        db.connect()
        query = """
            SELECT 
                HOUR(start_time) as hour,
                COUNT(*) as count
            FROM reservations
            WHERE status = 'approved'
            GROUP BY HOUR(start_time)
            ORDER BY count DESC
            LIMIT 3
        """
        results = db.fetch_all(query)
        db.disconnect()
        return 
    @staticmethod
    def get_weekly_comparison():
        """
        Compare this week's reservations to last week
        
        Returns:
            dict: Current week count, last week count, percentage change
        """
        db.connect()
        query = """
            SELECT 
                SUM(CASE WHEN reservation_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) as this_week,
                SUM(CASE WHEN reservation_date >= DATE_SUB(CURDATE(), INTERVAL 14 DAY) 
                    AND reservation_date < DATE_SUB(CURDATE(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) as last_week
            FROM reservations
        """
        result = db.fetch_one(query)
        db.disconnect()
        
        if result:
            this_week = result['this_week'] or 0
            last_week = result['last_week'] or 0
            
            if last_week == 0:
                change = 100.0 if this_week > 0 else 0.0
            else:
                change = round(((this_week - last_week) / last_week) * 100, 1)
            
            return {
                'this_week': this_week,
                'last_week': last_week,
                'change': change
            }
        return {'this_week': 0, 'last_week': 0, 'change': 0.0}
    
    @staticmethod
    def get_busiest_day():
        """
        Find the busiest day of the week for reservations
        
        Returns:
            dict: Day name and reservation count
        """
        db.connect()
        query = """
            SELECT 
                DAYNAME(reservation_date) as day_name,
                DAYOFWEEK(reservation_date) as day_num,
                COUNT(*) as count
            FROM reservations
            WHERE status = 'approved'
            GROUP BY DAYNAME(reservation_date), DAYOFWEEK(reservation_date)
            ORDER BY count DESC
            LIMIT 1
        """
        result = db.fetch_one(query)
        db.disconnect()
        return result or {'day_name': 'N/A', 'count': 0}
    
    @staticmethod
    def get_average_daily_reservations():
        """
        Calculate average reservations per day (last 30 days)
        
        Returns:
            float: Average daily reservations
        """
        db.connect()
        query = """
            SELECT 
                COUNT(*) as total,
                DATEDIFF(MAX(reservation_date), MIN(reservation_date)) + 1 as days
            FROM reservations
            WHERE reservation_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        """
        result = db.fetch_one(query)
        db.disconnect()
        
        if result and result['days'] and result['days'] > 0:
            return round(result['total'] / result['days'], 1)
        return 0.0
    
    @staticmethod
    def get_most_active_faculty():
        """
        Get the most active faculty member this month
        
        Returns:
            dict: Faculty name and reservation count
        """
        db.connect()
        query = """
            SELECT 
                u.full_name,
                COUNT(r.id) as reservation_count
            FROM users u
            JOIN reservations r ON u.id = r.user_id
            WHERE u.role = 'faculty'
            AND r.created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY u.id, u.full_name
            ORDER BY reservation_count DESC
            LIMIT 1
        """
        result = db.fetch_one(query)
        db.disconnect()
        return result or {'full_name': 'N/A', 'reservation_count': 0}
    
    @staticmethod
    def get_room_recommendation():
        """
        Recommend underutilized rooms based on capacity vs bookings
        
        Returns:
            dict: Room recommendation with reason
        """
        db.connect()
        query = """
            SELECT 
                c.room_name,
                c.building,
                c.capacity,
                COUNT(r.id) as bookings,
                ROUND(COUNT(r.id) / c.capacity * 100, 1) as utilization_score
            FROM classrooms c
            LEFT JOIN reservations r ON c.id = r.classroom_id AND r.status = 'approved'
            GROUP BY c.id, c.room_name, c.building, c.capacity
            ORDER BY utilization_score ASC
            LIMIT 1
        """
        result = db.fetch_one(query)
        db.disconnect()
        
        if result:
            return {
                'room_name': result['room_name'],
                'building': result['building'],
                'bookings': result['bookings'] or 0,
                'capacity': result['capacity'],
                'message': f"Consider promoting {result['room_name']} - only {result['bookings'] or 0} bookings"
            }
        return {'room_name': 'N/A', 'message': 'No data available'}
    
    @staticmethod
    def get_pending_bottleneck():
        """
        Identify if there's a bottleneck in pending approvals
        
        Returns:
            dict: Pending count and average wait time insight
        """
        db.connect()
        query = """
            SELECT 
                COUNT(*) as pending_count,
                AVG(DATEDIFF(CURDATE(), DATE(created_at))) as avg_wait_days
            FROM reservations
            WHERE status = 'pending'
        """
        result = db.fetch_one(query)
        db.disconnect()
        
        if result:
            pending = result['pending_count'] or 0
            avg_wait = round(result['avg_wait_days'] or 0, 1)
            
            if pending > 5:
                status = 'warning'
                message = f"{pending} reservations waiting (avg {avg_wait} days)"
            elif pending > 0:
                status = 'normal'
                message = f"{pending} pending approval"
            else:
                status = 'good'
                message = "No pending reservations"
            
            return {
                'pending_count': pending,
                'avg_wait_days': avg_wait,
                'status': status,
                'message': message
            }
        return {'pending_count': 0, 'status': 'good', 'message': 'No pending reservations'}