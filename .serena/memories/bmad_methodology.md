# BMAD Methodology

## Overview
The project follows the BMAD (Business Model Agile Development) methodology, which emphasizes:
- Story-driven development with strict quality checklists
- Role-based agents (PM, PO, Architect, Developer, QA, etc.)
- Structured epic and story creation process
- Comprehensive documentation and reporting

## Key BMAD Components
- **Agents**: Specialized roles defined in `.bmad-core/agents/` and `.claude/agents/`
  - bmad-orchestrator: Overall coordination
  - bmad-scrum-master: Story creation and validation
  - bmad-developer: Implementation following DOD
  - bmad-qa-manager: Quality assurance and testing
- **Checklists**: Quality gates in `.bmad-core/checklists/`
  - Story draft checklist
  - Story DOD (Definition of Done) checklist
  - Architecture checklist
  - Change checklist
- **Tasks**: Predefined workflows in `.bmad-core/tasks/`

## Development Flow
1. Stories are created following BMAD templates
2. Each story goes through draft validation
3. Development follows TDD approach
4. QA validation against DOD checklist
5. Reports generated in `/reports` directory

## Current Epic Structure
- Epic 1: SDK Type Extraction & Response Collection (Phase 1 Focus)
- Epic 2: Testing Infrastructure & Code Quality
- Epic 3: Tags Endpoint Implementation  
- Epic 4: Chat Endpoint Implementation
- Epic 5: Generate Endpoint Implementation
- Epic 6: Embeddings Endpoint Implementation
- Epic 7: Integration Testing & SDK Compatibility
- Epic 8: Documentation & Deployment Preparation
- Epic 9: Code Standards & Final Validation