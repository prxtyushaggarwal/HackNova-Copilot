import sys
from pathlib import Path

# Add project root to sys.path so modules in app/ can be imported on Vercel
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from main import app

# Vercel looks for the ASGI/WSGI entrypoint object named `app`
