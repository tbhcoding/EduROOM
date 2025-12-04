"""
Unit Tests for Data Validation
===============================
Tests input validation functions used across the application
"""

import unittest
from datetime import datetime, timedelta


class TestDateValidation(unittest.TestCase):
    """Test cases for date validation (mirrors reservation_view logic)"""
    
    @staticmethod
    def validate_date(date_str):
        """Validate date format YYYY-MM-DD"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def test_valid_date_format(self):
        """Test valid YYYY-MM-DD format"""
        self.assertTrue(self.validate_date("2025-12-15"))
        self.assertTrue(self.validate_date("2025-01-01"))
        self.assertTrue(self.validate_date("2025-06-30"))
    
    def test_invalid_date_format(self):
        """Test invalid date formats"""
        self.assertFalse(self.validate_date("12-15-2025"))  # MM-DD-YYYY
        self.assertFalse(self.validate_date("15/12/2025"))  # DD/MM/YYYY
        self.assertFalse(self.validate_date("2025/12/15"))  # Wrong separator
        self.assertFalse(self.validate_date("Dec 15, 2025"))  # Text format
    
    def test_invalid_date_values(self):
        """Test invalid date values"""
        self.assertFalse(self.validate_date("2025-13-01"))  # Invalid month
        self.assertFalse(self.validate_date("2025-00-15"))  # Zero month
        self.assertFalse(self.validate_date("2025-02-30"))  # Feb 30 doesn't exist
        self.assertFalse(self.validate_date("2025-04-31"))  # April has 30 days
    
    def test_empty_and_null(self):
        """Test empty and null inputs"""
        self.assertFalse(self.validate_date(""))
        self.assertFalse(self.validate_date("   "))
    
    def test_leap_year(self):
        """Test leap year date validation"""
        self.assertTrue(self.validate_date("2024-02-29"))   # 2024 is leap year
        self.assertFalse(self.validate_date("2025-02-29"))  # 2025 is not


class TestTimeValidation(unittest.TestCase):
    """Test cases for time validation"""
    
    @staticmethod
    def validate_time(time_str):
        """Validate time format HH:MM (24-hour)"""
        try:
            datetime.strptime(time_str, '%H:%M')
            return True
        except ValueError:
            return False
    
    def test_valid_time_format(self):
        """Test valid HH:MM format"""
        self.assertTrue(self.validate_time("09:00"))
        self.assertTrue(self.validate_time("14:30"))
        self.assertTrue(self.validate_time("00:00"))
        self.assertTrue(self.validate_time("23:59"))
    
    def test_invalid_time_format(self):
        """Test invalid time formats"""
        self.assertFalse(self.validate_time("09.00"))    # Wrong separator
        self.assertFalse(self.validate_time("09:00 AM")) # 12-hour format
        self.assertFalse(self.validate_time("nine:00"))  # Text instead of number
        self.assertFalse(self.validate_time(""))         # Empty string
    
    def test_invalid_time_values(self):
        """Test invalid time values"""
        self.assertFalse(self.validate_time("24:00"))  # Hour out of range
        self.assertFalse(self.validate_time("12:60"))  # Minute out of range
        self.assertFalse(self.validate_time("25:30"))  # Invalid hour
        self.assertFalse(self.validate_time("-1:30"))  # Negative hour


class TestTimeRangeValidation(unittest.TestCase):
    """Test cases for time range validation"""
    
    @staticmethod
    def validate_time_range(start_time, end_time):
        """Validate that end time is after start time"""
        try:
            start = datetime.strptime(start_time, '%H:%M')
            end = datetime.strptime(end_time, '%H:%M')
            return end > start
        except ValueError:
            return False
    
    def test_valid_time_range(self):
        """Test valid time ranges (end after start)"""
        self.assertTrue(self.validate_time_range("09:00", "11:00"))
        self.assertTrue(self.validate_time_range("08:00", "17:00"))
        self.assertTrue(self.validate_time_range("14:00", "14:30"))
    
    def test_invalid_time_range(self):
        """Test invalid time ranges (end before or equal to start)"""
        self.assertFalse(self.validate_time_range("11:00", "09:00"))  # End before start
        self.assertFalse(self.validate_time_range("09:00", "09:00"))  # Same time
        self.assertFalse(self.validate_time_range("17:00", "08:00"))  # Reversed


class TestEmailValidation(unittest.TestCase):
    """Test cases for email validation"""
    
    @staticmethod
    def validate_cspc_email(email):
        """Validate CSPC email format"""
        if not email or not isinstance(email, str):
            return False
        email = email.strip().lower()
        return email.endswith("@cspc.edu.ph") or email.endswith("@my.cspc.edu.ph")
    
    def test_valid_cspc_emails(self):
        """Test valid CSPC email formats"""
        self.assertTrue(self.validate_cspc_email("admin@cspc.edu.ph"))
        self.assertTrue(self.validate_cspc_email("student@my.cspc.edu.ph"))
        self.assertTrue(self.validate_cspc_email("faculty@my.cspc.edu.ph"))
    
    def test_invalid_emails(self):
        """Test invalid email formats"""
        self.assertFalse(self.validate_cspc_email("user@gmail.com"))
        self.assertFalse(self.validate_cspc_email("user@yahoo.com"))
        self.assertFalse(self.validate_cspc_email("user@cspc.edu"))  # Missing .ph
        self.assertFalse(self.validate_cspc_email(""))
        self.assertFalse(self.validate_cspc_email(None))
    
    def test_case_insensitivity(self):
        """Test that email validation is case-insensitive"""
        self.assertTrue(self.validate_cspc_email("USER@CSPC.EDU.PH"))
        self.assertTrue(self.validate_cspc_email("User@My.CSPC.Edu.Ph"))


class TestIDNumberValidation(unittest.TestCase):
    """Test cases for ID number validation"""
    
    @staticmethod
    def validate_id_number(id_number):
        """Validate ID number format (8 digits)"""
        if not id_number or not isinstance(id_number, str):
            return False
        id_number = id_number.strip()
        return id_number.isdigit() and len(id_number) == 8
    
    def test_valid_id_numbers(self):
        """Test valid ID number formats"""
        self.assertTrue(self.validate_id_number("00000000"))
        self.assertTrue(self.validate_id_number("12345678"))
        self.assertTrue(self.validate_id_number("25123456"))
    
    def test_invalid_id_numbers(self):
        """Test invalid ID number formats"""
        self.assertFalse(self.validate_id_number("1234567"))    # Too short
        self.assertFalse(self.validate_id_number("123456789"))  # Too long
        self.assertFalse(self.validate_id_number("1234567a"))   # Contains letter
        self.assertFalse(self.validate_id_number("1234-5678"))  # Contains dash
        self.assertFalse(self.validate_id_number(""))
        self.assertFalse(self.validate_id_number(None))


if __name__ == "__main__":
    unittest.main()