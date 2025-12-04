"""
Unit Tests for Analytics Calculations
======================================
Tests analytics computation logic (without database dependency)
"""

import unittest


class TestApprovalRateCalculation(unittest.TestCase):
    """Test cases for approval rate calculation logic"""
    
    @staticmethod
    def calculate_approval_rate(approved, rejected):
        """Calculate approval rate percentage"""
        total = approved + rejected
        if total == 0:
            return 0.0
        return round((approved / total) * 100, 1)
    
    def test_all_approved(self):
        """Test when all reservations are approved"""
        rate = self.calculate_approval_rate(10, 0)
        self.assertEqual(rate, 100.0)
    
    def test_all_rejected(self):
        """Test when all reservations are rejected"""
        rate = self.calculate_approval_rate(0, 10)
        self.assertEqual(rate, 0.0)
    
    def test_mixed_results(self):
        """Test mixed approval/rejection"""
        rate = self.calculate_approval_rate(7, 3)
        self.assertEqual(rate, 70.0)
        
        rate = self.calculate_approval_rate(1, 1)
        self.assertEqual(rate, 50.0)
    
    def test_no_processed(self):
        """Test when no reservations have been processed"""
        rate = self.calculate_approval_rate(0, 0)
        self.assertEqual(rate, 0.0)
    
    def test_decimal_precision(self):
        """Test decimal precision in calculation"""
        rate = self.calculate_approval_rate(1, 2)
        self.assertEqual(rate, 33.3)
        
        rate = self.calculate_approval_rate(2, 1)
        self.assertEqual(rate, 66.7)


class TestUtilizationCalculation(unittest.TestCase):
    """Test cases for classroom utilization calculation"""
    
    @staticmethod
    def calculate_utilization(approved_reservations, total_reservations):
        """Calculate utilization rate"""
        if total_reservations == 0:
            return 0.0
        return round((approved_reservations / total_reservations) * 100, 1)
    
    def test_full_utilization(self):
        """Test 100% utilization"""
        rate = self.calculate_utilization(10, 10)
        self.assertEqual(rate, 100.0)
    
    def test_zero_utilization(self):
        """Test 0% utilization"""
        rate = self.calculate_utilization(0, 10)
        self.assertEqual(rate, 0.0)
    
    def test_no_reservations(self):
        """Test when no reservations exist"""
        rate = self.calculate_utilization(0, 0)
        self.assertEqual(rate, 0.0)
    
    def test_partial_utilization(self):
        """Test partial utilization"""
        rate = self.calculate_utilization(3, 10)
        self.assertEqual(rate, 30.0)


class TestPercentageCalculation(unittest.TestCase):
    """Test cases for status distribution percentage"""
    
    @staticmethod
    def calculate_percentage(count, total):
        """Calculate percentage of total"""
        if total == 0:
            return 0.0
        return round((count / total) * 100, 1)
    
    def test_full_percentage(self):
        """Test 100% of total"""
        pct = self.calculate_percentage(50, 50)
        self.assertEqual(pct, 100.0)
    
    def test_zero_percentage(self):
        """Test 0% of total"""
        pct = self.calculate_percentage(0, 50)
        self.assertEqual(pct, 0.0)
    
    def test_division_by_zero(self):
        """Test handling of zero total"""
        pct = self.calculate_percentage(10, 0)
        self.assertEqual(pct, 0.0)
    
    def test_quarter_percentage(self):
        """Test 25% calculation"""
        pct = self.calculate_percentage(25, 100)
        self.assertEqual(pct, 25.0)


class TestBarWidthCalculation(unittest.TestCase):
    """Test cases for visualization bar width calculation"""
    
    @staticmethod
    def calculate_bar_width(count, max_count, max_width=200):
        """Calculate proportional bar width for visualization"""
        if max_count == 0:
            return 0
        return int((count / max_count) * max_width)
    
    def test_max_bar_width(self):
        """Test maximum bar width"""
        width = self.calculate_bar_width(100, 100, 200)
        self.assertEqual(width, 200)
    
    def test_zero_bar_width(self):
        """Test zero bar width"""
        width = self.calculate_bar_width(0, 100, 200)
        self.assertEqual(width, 0)
    
    def test_half_bar_width(self):
        """Test 50% bar width"""
        width = self.calculate_bar_width(50, 100, 200)
        self.assertEqual(width, 100)
    
    def test_zero_max_count(self):
        """Test handling of zero max count"""
        width = self.calculate_bar_width(10, 0, 200)
        self.assertEqual(width, 0)
    
    def test_custom_max_width(self):
        """Test custom max width parameter"""
        width = self.calculate_bar_width(50, 100, 150)
        self.assertEqual(width, 75)


class TestTrendAnalysis(unittest.TestCase):
    """Test cases for trend analysis calculations"""
    
    @staticmethod
    def calculate_trend_percentage(current, previous):
        """Calculate percentage change between periods"""
        if previous == 0:
            if current == 0:
                return 0.0
            return 100.0  # Infinite increase shown as 100%
        return round(((current - previous) / previous) * 100, 1)
    
    def test_positive_trend(self):
        """Test upward trend calculation"""
        trend = self.calculate_trend_percentage(15, 10)
        self.assertEqual(trend, 50.0)
    
    def test_negative_trend(self):
        """Test downward trend calculation"""
        trend = self.calculate_trend_percentage(5, 10)
        self.assertEqual(trend, -50.0)
    
    def test_no_change(self):
        """Test no change in trend"""
        trend = self.calculate_trend_percentage(10, 10)
        self.assertEqual(trend, 0.0)
    
    def test_from_zero(self):
        """Test trend from zero baseline"""
        trend = self.calculate_trend_percentage(10, 0)
        self.assertEqual(trend, 100.0)
    
    def test_to_zero(self):
        """Test trend to zero"""
        trend = self.calculate_trend_percentage(0, 10)
        self.assertEqual(trend, -100.0)
    
    def test_both_zero(self):
        """Test when both values are zero"""
        trend = self.calculate_trend_percentage(0, 0)
        self.assertEqual(trend, 0.0)


class TestPeakHourIdentification(unittest.TestCase):
    """Test cases for identifying peak hours"""
    
    @staticmethod
    def identify_peak_hours(hourly_data, top_n=3):
        """Identify top N peak hours from hourly data"""
        if not hourly_data:
            return []
        sorted_data = sorted(hourly_data, key=lambda x: x['count'], reverse=True)
        return sorted_data[:top_n]
    
    def test_identify_top_peaks(self):
        """Test identification of top 3 peak hours"""
        data = [
            {'hour': 9, 'count': 15},
            {'hour': 10, 'count': 25},
            {'hour': 14, 'count': 20},
            {'hour': 11, 'count': 10},
        ]
        peaks = self.identify_peak_hours(data, 3)
        self.assertEqual(len(peaks), 3)
        self.assertEqual(peaks[0]['hour'], 10)
        self.assertEqual(peaks[1]['hour'], 14)
        self.assertEqual(peaks[2]['hour'], 9)
    
    def test_empty_data(self):
        """Test with empty data"""
        peaks = self.identify_peak_hours([], 3)
        self.assertEqual(peaks, [])
    
    def test_fewer_than_requested(self):
        """Test when fewer hours than requested"""
        data = [
            {'hour': 9, 'count': 15},
            {'hour': 10, 'count': 25},
        ]
        peaks = self.identify_peak_hours(data, 5)
        self.assertEqual(len(peaks), 2)


if __name__ == "__main__":
    unittest.main()