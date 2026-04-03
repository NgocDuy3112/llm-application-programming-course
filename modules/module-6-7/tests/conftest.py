"""
Pytest configuration for Module 6-7 tests.
"""

import sys
from pathlib import Path

# Add exercises and exercises/demos to Python path for imports
exercises_path = Path(__file__).parent.parent / "exercises"
demos_exercises_path = exercises_path / "demos"

if str(exercises_path) not in sys.path:
    sys.path.insert(0, str(exercises_path))
if str(demos_exercises_path) not in sys.path:
    sys.path.insert(0, str(demos_exercises_path))