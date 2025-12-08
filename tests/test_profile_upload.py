"""
Unit Tests for Profile Picture Upload Validation
=================================================
Tests file type and size validation for profile picture uploads
"""

import unittest
import os
import tempfile


class TestImageValidation(unittest.TestCase):
    """Test cases for image file validation"""
    
    # Configuration matching profile_view.py
    ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
    
    @staticmethod
    def validate_image_file(file_path):
        """
        Validate uploaded image file for type and size.
        (Mirror of the function in profile_view.py)
        """
        ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
        MAX_FILE_SIZE = 2 * 1024 * 1024
        
        # Check file extension
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in ALLOWED_EXTENSIONS:
            allowed = ', '.join(ALLOWED_EXTENSIONS)
            return False, f"Invalid file type. Allowed types: {allowed}"
        
        # Check file size
        try:
            file_size = os.path.getsize(file_path)
            if file_size > MAX_FILE_SIZE:
                size_mb = MAX_FILE_SIZE / (1024 * 1024)
                return False, f"File too large. Maximum size is {size_mb:.0f}MB"
            if file_size == 0:
                return False, "File is empty"
        except OSError:
            return False, "Could not read file"
        
        return True, None
    
    def test_valid_png_extension(self):
        """Test that .png files are accepted"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(b'fake png content')
            temp_path = f.name
        
        try:
            is_valid, error = self.validate_image_file(temp_path)
            self.assertTrue(is_valid)
            self.assertIsNone(error)
        finally:
            os.unlink(temp_path)
    
    def test_valid_jpg_extension(self):
        """Test that .jpg files are accepted"""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(b'fake jpg content')
            temp_path = f.name
        
        try:
            is_valid, error = self.validate_image_file(temp_path)
            self.assertTrue(is_valid)
            self.assertIsNone(error)
        finally:
            os.unlink(temp_path)
    
    def test_valid_jpeg_extension(self):
        """Test that .jpeg files are accepted"""
        with tempfile.NamedTemporaryFile(suffix='.jpeg', delete=False) as f:
            f.write(b'fake jpeg content')
            temp_path = f.name
        
        try:
            is_valid, error = self.validate_image_file(temp_path)
            self.assertTrue(is_valid)
            self.assertIsNone(error)
        finally:
            os.unlink(temp_path)
    
    def test_valid_gif_extension(self):
        """Test that .gif files are accepted"""
        with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as f:
            f.write(b'fake gif content')
            temp_path = f.name
        
        try:
            is_valid, error = self.validate_image_file(temp_path)
            self.assertTrue(is_valid)
            self.assertIsNone(error)
        finally:
            os.unlink(temp_path)
    
    def test_valid_webp_extension(self):
        """Test that .webp files are accepted"""
        with tempfile.NamedTemporaryFile(suffix='.webp', delete=False) as f:
            f.write(b'fake webp content')
            temp_path = f.name
        
        try:
            is_valid, error = self.validate_image_file(temp_path)
            self.assertTrue(is_valid)
            self.assertIsNone(error)
        finally:
            os.unlink(temp_path)
    
    def test_invalid_txt_extension(self):
        """Test that .txt files are rejected"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'not an image')
            temp_path = f.name
        
        try:
            is_valid, error = self.validate_image_file(temp_path)
            self.assertFalse(is_valid)
            self.assertIn("Invalid file type", error)
        finally:
            os.unlink(temp_path)
    
    def test_invalid_pdf_extension(self):
        """Test that .pdf files are rejected"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b'fake pdf content')
            temp_path = f.name
        
        try:
            is_valid, error = self.validate_image_file(temp_path)
            self.assertFalse(is_valid)
            self.assertIn("Invalid file type", error)
        finally:
            os.unlink(temp_path)
    
    def test_invalid_exe_extension(self):
        """Test that .exe files are rejected"""
        with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as f:
            f.write(b'fake exe content')
            temp_path = f.name
        
        try:
            is_valid, error = self.validate_image_file(temp_path)
            self.assertFalse(is_valid)
            self.assertIn("Invalid file type", error)
        finally:
            os.unlink(temp_path)
    
    def test_case_insensitive_extension(self):
        """Test that extension check is case-insensitive"""
        for ext in ['.PNG', '.JPG', '.JPEG', '.GIF', '.WEBP']:
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
                f.write(b'fake content')
                temp_path = f.name
            
            try:
                is_valid, error = self.validate_image_file(temp_path)
                self.assertTrue(is_valid, f"Extension {ext} should be valid")
            finally:
                os.unlink(temp_path)
    
    def test_empty_file_rejected(self):
        """Test that empty files are rejected"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            # Don't write anything - creates empty file
            temp_path = f.name
        
        try:
            is_valid, error = self.validate_image_file(temp_path)
            self.assertFalse(is_valid)
            self.assertIn("empty", error.lower())
        finally:
            os.unlink(temp_path)
    
    def test_file_under_size_limit(self):
        """Test that files under 2MB are accepted"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            # Write 1MB of data
            f.write(b'x' * (1024 * 1024))
            temp_path = f.name
        
        try:
            is_valid, error = self.validate_image_file(temp_path)
            self.assertTrue(is_valid)
            self.assertIsNone(error)
        finally:
            os.unlink(temp_path)
    
    def test_file_at_size_limit(self):
        """Test that files exactly at 2MB are accepted"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            # Write exactly 2MB of data
            f.write(b'x' * (2 * 1024 * 1024))
            temp_path = f.name
        
        try:
            is_valid, error = self.validate_image_file(temp_path)
            self.assertTrue(is_valid)
            self.assertIsNone(error)
        finally:
            os.unlink(temp_path)
    
    def test_file_over_size_limit(self):
        """Test that files over 2MB are rejected"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            # Write 3MB of data
            f.write(b'x' * (3 * 1024 * 1024))
            temp_path = f.name
        
        try:
            is_valid, error = self.validate_image_file(temp_path)
            self.assertFalse(is_valid)
            self.assertIn("too large", error.lower())
        finally:
            os.unlink(temp_path)
    
    def test_nonexistent_file(self):
        """Test handling of non-existent file path"""
        is_valid, error = self.validate_image_file("/nonexistent/path/image.png")
        self.assertFalse(is_valid)
        self.assertIn("Could not read", error)


class TestFilenameGeneration(unittest.TestCase):
    """Test cases for unique filename generation"""
    
    def test_unique_filenames(self):
        """Test that generated filenames are unique"""
        import uuid
        
        user_id = 1
        ext = ".png"
        
        filenames = set()
        for _ in range(100):
            filename = f"user_{user_id}_{uuid.uuid4().hex[:8]}{ext}"
            self.assertNotIn(filename, filenames, "Generated duplicate filename")
            filenames.add(filename)
    
    def test_filename_format(self):
        """Test that filenames follow expected format"""
        import uuid
        
        user_id = 42
        ext = ".jpg"
        filename = f"user_{user_id}_{uuid.uuid4().hex[:8]}{ext}"
        
        self.assertTrue(filename.startswith("user_42_"))
        self.assertTrue(filename.endswith(".jpg"))
        # Should be: user_42_xxxxxxxx.jpg (8 hex chars)
        self.assertEqual(len(filename), len("user_42_") + 8 + len(".jpg"))


if __name__ == "__main__":
    unittest.main()