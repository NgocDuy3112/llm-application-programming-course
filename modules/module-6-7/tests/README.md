# Tests for Module 6-7 Exercises

This directory contains test suites for validating the Module 6-7 chatbot programming exercises.

## Test Files

- `test_exercises.py` - Pytest-based tests (requires pytest installation)
- `test_demos_exercises.py` - Tests for exercises/demos/ placeholders (requires pytest)
- `run_tests.py` - Standalone test runner (works without pytest)
- `conftest.py` - Pytest configuration for path setup

## Running Tests

### Option 1: Standalone Test Runner (Recommended)
```bash
source .venv/bin/activate
python tests/run_tests.py
```

### Option 2: Using Pytest (if available)
```bash
source .venv/bin/activate
pip install pytest
pytest tests/ -v
```

## Test Coverage

The tests validate:

1. **Import Tests** - All modules can be imported without errors
2. **Component Tests** - Core classes and functions work as expected
3. **Memory Tests** - WindowMemory sliding window behavior
4. **Placeholder Tests** - Ensure no __BLANKn__ placeholders remain in final code

## Expected Results

All tests should pass (12/12) when the exercises are completed correctly.

## Troubleshooting

- If import tests fail, ensure the exercises/ directory structure is complete
- If placeholder tests fail, check that all __BLANKn__ placeholders have been replaced
- If memory tests fail, verify the WindowMemory implementation in orchestrator/memory.py