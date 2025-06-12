import pytest
import os

def run_tests():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    pytest.main([test_dir, '-s', '--tb=auto'])

if __name__ == '__main__':
    run_tests()