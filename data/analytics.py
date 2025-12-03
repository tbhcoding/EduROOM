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
        return results