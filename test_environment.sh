#!/bin/bash

echo "=== DevContainer Environment Test ==="
echo ""

# Test Python
echo "1. Python Test:"
echo -n "   Python version: "
python3 --version
echo -n "   Pip version: "
pip3 --version
echo -n "   Python path: "
which python3
echo ""

# Test Node.js
echo "2. Node.js Test:"
echo -n "   Node version: "
node --version
echo -n "   NPM version: "
npm --version
echo -n "   NPX available: "
which npx > /dev/null && echo "Yes" || echo "No"
echo ""

# Test Docker
echo "3. Docker Test:"
echo -n "   Docker CLI version: "
docker --version
echo -n "   Docker Compose: "
docker compose version
echo ""

# Test GitHub CLI
echo "4. GitHub CLI Test:"
echo -n "   GitHub CLI version: "
gh --version | head -n1
echo ""

# Test development tools
echo "5. Python Development Tools:"
echo -n "   Black: "
black --version 2>&1 | head -n1
echo -n "   MyPy: "
mypy --version
echo -n "   Pytest: "
pytest --version | head -n1
echo ""

# Test networking tools
echo "6. Networking Tools:"
echo -n "   Curl: "
curl --version | head -n1 | cut -d' ' -f1-2
echo -n "   Ping available: "
which ping > /dev/null && echo "Yes" || echo "No"
echo -n "   Netcat available: "
which nc > /dev/null && echo "Yes" || echo "No"
echo ""

# Test C/C++ tools
echo "7. C/C++ Development Tools:"
echo -n "   GCC version: "
gcc --version | head -n1
echo -n "   G++ version: "
g++ --version | head -n1
echo -n "   CMake version: "
cmake --version | head -n1
echo ""

# Test FastAPI application
echo "8. FastAPI Application Test:"
echo -n "   FastAPI importable: "
python3 -c "import fastapi; print('Yes - Version:', fastapi.__version__)" 2>/dev/null || echo "No"
echo -n "   Uvicorn available: "
which uvicorn > /dev/null && echo "Yes" || echo "No"
echo ""

# Test environment variables
echo "9. Environment Variables:"
echo "   PYTHONPATH: $PYTHONPATH"
echo "   PATH includes npm-global: "
echo "$PATH" | grep -q ".npm-global" && echo "   Yes" || echo "   No"
echo ""

# Test BMAD readiness
echo "10. BMAD-METHOD Readiness:"
echo -n "    NPX available for BMAD: "
npx --version > /dev/null 2>&1 && echo "Yes - Ready to run: npx bmad-method install" || echo "No"
echo ""

echo "=== Test Complete ==="