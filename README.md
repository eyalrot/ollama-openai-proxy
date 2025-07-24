# Python FastAPI Development Template

A modern Python development environment with FastAPI, Docker, and VS Code DevContainer support.

## Features

- **Python 3.12** with FastAPI framework
- **VS Code DevContainer** for consistent development environment
- **Docker & Docker Compose** support (including Docker-in-Docker)
- **Development Tools**: black, mypy, flake8, pytest, pre-commit
- **Linux Utilities**: curl, wget, ping, netcat, and more
- **C/C++ Development**: gcc, g++, cmake, gdb, valgrind
- **Claude Code Integration**: Works both inside and outside the container

## Quick Start

### Using VS Code DevContainer (Recommended)

1. Open the project in VS Code
2. When prompted, click "Reopen in Container"
3. VS Code will build and start the development container
4. The application will be available at `http://localhost:11433`

### Using Docker Compose

```bash
# Build and start the application
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop the application
docker-compose down
```

### Local Development

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 11433 --reload

# Or use Make
make run
```

## Project Structure

```
.
├── app/                    # Application code
│   ├── __init__.py
│   └── main.py            # FastAPI application
├── tests/                 # Test files
│   ├── __init__.py
│   └── test_main.py       # Example tests
├── .devcontainer/         # VS Code DevContainer configuration
│   ├── devcontainer.json  # Container settings
│   ├── Dockerfile         # Container image definition
│   └── docker-compose.yml # DevContainer compose file
├── docker-compose.yml     # Production Docker Compose
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── pyproject.toml        # Python tool configurations
├── Makefile              # Common commands
└── README.md             # This file
```

## Available Commands

```bash
make help          # Show all available commands
make install       # Install production dependencies
make install-dev   # Install development dependencies
make run          # Run the application
make test         # Run tests with coverage
make lint         # Run linting
make format       # Format code
make type-check   # Run type checking
make clean        # Remove cache files
```

## API Endpoints

- `GET /` - Health check endpoint
- `GET /health` - Detailed health status
- `POST /items` - Create a new item
- `GET /items/{item_id}` - Get a specific item
- `GET /items` - List all items
- `DELETE /items/{item_id}` - Delete an item

## Development Workflow

1. **Code Formatting**: The project uses Black for code formatting and isort for import sorting
2. **Type Checking**: MyPy is configured for strict type checking
3. **Linting**: Flake8 and Pylint ensure code quality
4. **Testing**: Pytest with coverage reporting
5. **Pre-commit Hooks**: Automatically run formatting and linting before commits

## Claude Code Integration

The DevContainer is configured to work with Claude Code both inside and outside the container:

- Claude configuration is mounted at `/home/vscode/.claude`
- File permissions are properly set for seamless integration
- The container includes all necessary tools for Claude Code to function properly

## Adding New Dependencies

1. Add production dependencies to `requirements.txt`
2. Add development dependencies to `requirements-dev.txt`
3. Rebuild the container if using DevContainer:
   - Command Palette → "Dev Containers: Rebuild Container"

## Environment Variables

You can set environment variables in:
- `.env` file (create one based on `.env.example` if provided)
- `docker-compose.yml` under the `environment` section
- `.devcontainer/devcontainer.json` under `containerEnv`

## Troubleshooting

### Port 11433 is already in use
```bash
# Find the process using the port
sudo lsof -i :11433

# Or change the port in docker-compose.yml and app/main.py
```

### Permission issues with Docker socket
Make sure your user is in the docker group:
```bash
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

### DevContainer fails to build
1. Check Docker is running: `docker ps`
2. Clear Docker cache: `docker system prune -a`
3. Rebuild without cache: In VS Code, use "Dev Containers: Rebuild Container Without Cache"

## License

This is a template project. Feel free to use it as a starting point for your own projects.