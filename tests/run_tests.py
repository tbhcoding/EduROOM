"""
Test Runner for EduROOM
========================
Run all unit tests with coverage reporting

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --verbose    # Run with verbose output
    python run_tests.py --coverage   # Run with coverage report (requires coverage package)
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_tests(verbosity=2):
    """Discover and run all tests"""
    # Get the tests directory
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Discover all tests
    loader = unittest.TestLoader()
    suite = loader.discover(tests_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED!")
    else:
        print("\n✗ SOME TESTS FAILED")
        if result.failures:
            print("\nFailed tests:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        if result.errors:
            print("\nError tests:")
            for test, traceback in result.errors:
                print(f"  - {test}")
    
    print("=" * 70)
    
    return result.wasSuccessful()


def run_with_coverage():
    """Run tests with coverage reporting"""
    try:
        import coverage
    except ImportError:
        print("Coverage package not installed. Run: pip install coverage")
        print("Running tests without coverage...\n")
        return run_tests()
    
    # Start coverage
    cov = coverage.Coverage(
        source=['utils', 'data'],
        omit=['*/tests/*', '*/__pycache__/*']
    )
    cov.start()
    
    # Run tests
    success = run_tests()
    
    # Stop coverage and report
    cov.stop()
    cov.save()
    
    print("\n" + "=" * 70)
    print("COVERAGE REPORT")
    print("=" * 70)
    cov.report()
    
    # Generate HTML report
    html_dir = os.path.join(os.path.dirname(__file__), 'coverage_html')
    cov.html_report(directory=html_dir)
    print(f"\nHTML report generated: {html_dir}/index.html")
    
    return success


if __name__ == "__main__":
    if '--coverage' in sys.argv:
        success = run_with_coverage()
    elif '--verbose' in sys.argv:
        success = run_tests(verbosity=2)
    else:
        success = run_tests(verbosity=1)
    
    sys.exit(0 if success else 1)
