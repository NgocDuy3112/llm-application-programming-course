import importlib.util
import sys
import traceback
import os

# Ensure project root is on sys.path so `src` can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

spec = importlib.util.spec_from_file_location("tests.test_chat_service", "tests/test_chat_service.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
errors = []
for name in dir(m):
    if name.startswith("test_"):
        try:
            getattr(m, name)()
            print(f"PASS {name}")
        except AssertionError as e:
            print(f"FAIL {name}: {e}")
            errors.append((name, e))
        except Exception as e:
            print(f"ERROR {name}: {e}")
            traceback.print_exc()
if errors:
    print('\nSome tests failed')
    sys.exit(1)
else:
    print('\nAll tests passed')
