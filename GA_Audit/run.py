#!/usr/bin/env python3
"""
GA Audit - Main runner script
Use with GLM-API virtual environment
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Add GLM-API to path for imports
GLM_API_PATH = Path("/Users/free/WorkSpace/GLM-API")
if str(GLM_API_PATH) not in sys.path:
    sys.path.insert(0, str(GLM_API_PATH))

# Import and run main
from ga_audit.main import main

if __name__ == "__main__":
    main()
