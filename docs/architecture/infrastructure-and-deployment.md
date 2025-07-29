# Infrastructure and Deployment

## Development Environment

- **Primary Environment:** VSCode DevContainer (pre-configured with Python 3.12)
- **Working Directory:** `/workspace` (all files mounted here for easy navigation)
- **DevContainer Status:** Already set up and ready to use - no build tasks required
- **Benefits:**
  - No need for virtual environment (venv) management
  - Consistent environment between development and production
  - Claude Code can navigate easily without venv activation issues
  - All dependencies pre-installed in container
  - Python 3.12 runtime pre-configured
- **DevContainer Configuration:** `.devcontainer/devcontainer.json`

## Infrastructure as Code

- **Tool:** Docker 24.0
- **Location:** `docker/` (production), `.devcontainer/` (development)
- **Approach:** 
  - Development: VSCode DevContainer for isolated development
  - CI/CD: Docker containers in GitHub Actions
  - Production: Docker container deployment

## Deployment Strategy

- **Strategy:** Container-based deployment using Docker
- **CI/CD Platform:** GitHub Actions (running in Docker containers)
- **Pipeline Configuration:** `.github/workflows/`

## Environments

- **Development:** VSCode DevContainer - Isolated container environment at `/workspace`
- **CI/CD:** Docker containers in GitHub Actions - Ensures consistency
- **Staging:** Not required for Phase 1 POC
- **Production:** On-premises Docker host - Single container deployment

## Environment Promotion Flow

```text
Development (Local) -> Production (On-premises)
                      
Simple flow for POC:
1. Test locally with docker-compose
2. Build production image
3. Deploy to on-premises Docker host
```

## Rollback Strategy

- **Primary Method:** Docker image rollback (keep previous image version)
- **Trigger Conditions:** Failed health checks, critical errors in logs
- **Recovery Time Objective:** < 5 minutes (time to pull and start previous image)
