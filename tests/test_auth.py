"""
Unit Tests for Authentication Module
=====================================
Tests password hashing and verification functions
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import hash_password, verify_password


class TestPasswordHashing(unittest.TestCase):
    """Test cases for password hashing functionality"""
    
    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string"""
        password = "testpassword123"
        hashed = hash_password(password)
        self.assertIsInstance(hashed, str)
    
    def test_hash_password_not_plaintext(self):
        """Test that hashed password is not the same as plaintext"""
        password = "mySecurePassword"
        hashed = hash_password(password)
        self.assertNotEqual(password, hashed)
    
    def test_hash_password_generates_unique_hashes(self):
        """Test that same password generates different hashes (due to salt)"""
        password = "samePassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        self.assertNotEqual(hash1, hash2)
    
    def test_hash_password_bcrypt_format(self):
        """Test that hash follows bcrypt format (starts with $2b$)"""
        password = "formatTest"
        hashed = hash_password(password)
        self.assertTrue(hashed.startswith("$2b$"))


class TestPasswordVerification(unittest.TestCase):
    """Test cases for password verification functionality"""
    
    def test_verify_correct_password(self):
        """Test that correct password verifies successfully"""
        password = "correctPassword123"
        hashed = hash_password(password)
        self.assertTrue(verify_password(password, hashed))
    
    def test_verify_incorrect_password(self):
        """Test that incorrect password fails verification"""
        password = "correctPassword"
        wrong_password = "wrongPassword"
        hashed = hash_password(password)
        self.assertFalse(verify_password(wrong_password, hashed))
    
    def test_verify_empty_password(self):
        """Test verification with empty password"""
        password = ""
        hashed = hash_password(password)
        self.assertTrue(verify_password("", hashed))
        self.assertFalse(verify_password("notempty", hashed))
    
    def test_verify_special_characters(self):
        """Test password with special characters"""
        password = "P@ssw0rd!#$%^&*()"
        hashed = hash_password(password)
        self.assertTrue(verify_password(password, hashed))
    
    def test_verify_unicode_password(self):
        """Test password with unicode characters"""
        password = "密码テスト123"
        hashed = hash_password(password)
        self.assertTrue(verify_password(password, hashed))
    
    def test_verify_long_password(self):
        """Test verification with long password (bcrypt limit is 72 bytes)"""
        password = "a" * 70  # Within bcrypt's 72 byte limit
        hashed = hash_password(password)
        self.assertTrue(verify_password(password, hashed))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_case_sensitivity(self):
        """Test that passwords are case-sensitive"""
        password = "CaseSensitive"
        hashed = hash_password(password)
        self.assertTrue(verify_password("CaseSensitive", hashed))
        self.assertFalse(verify_password("casesensitive", hashed))
        self.assertFalse(verify_password("CASESENSITIVE", hashed))
    
    def test_whitespace_handling(self):
        """Test that whitespace in passwords is preserved"""
        password = "  spaces  "
        hashed = hash_password(password)
        self.assertTrue(verify_password("  spaces  ", hashed))
        self.assertFalse(verify_password("spaces", hashed))


if __name__ == "__main__":
    unittest.main()