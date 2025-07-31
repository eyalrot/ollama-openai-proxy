# Markdown Files Index

## Project Root Files
- `architecture.md` - Points to docs/architecture directory
- `development-flow.md` - Development workflow documentation
- `architecture backup.md` - Backup of architecture doc

## Core Documentation (`/docs`)

### Architecture Documentation (`/docs/architecture/`)
- `index.md` - Main architecture TOC and entry point
- `introduction.md` - Project introduction and change log
- `high-level-architecture.md` - Technical summary and diagrams
- `tech-stack.md` - Technology stack details
- `data-models.md` - Request/response models
- `components.md` - Component descriptions
- `component-diagrams.md` - Visual component diagrams
- `external-apis.md` - OpenAI API integration details
- `core-workflows.md` - Development and runtime workflows
- `rest-api-specification.md` - API endpoint specifications
- `database-schema.md` - Database structure (if applicable)
- `source-tree.md` - Directory structure and Makefile requirements
- `infrastructure-and-deployment.md` - Deployment strategy
- `error-handling-strategy.md` - Error handling patterns
- `coding-standards.md` - Code style and conventions
- `test-strategy-and-standards.md` - Testing philosophy and organization
- `security.md` - Security considerations
- `checklist-results-report.md` - Architecture validation
- `next-steps.md` - Development guidance

### User Stories (`/docs/stories/`)
- `1.1.sdk-type-extraction-setup.md` - Epic 1 Story 1
- `1.2.openai-response-collection.md` - Epic 1 Story 2
- `1.3.type-validation-test-framework.md` - Epic 1 Story 3
- `2.1.fastapi-application-setup.md` - Epic 2 Story 1
- `2.2.testing-infrastructure.md` - Epic 2 Story 2
- `2.3.code-quality-tooling.md` - Epic 2 Story 3
- `2.4.logging-error-handling.md` - Epic 2 Story 4

### Templates (`/docs/templates/`)
- `epic-retrospective-template.md`
- `epic-velocity-tmpl.md`
- `daily-standup-template.md`

### Product Documentation
- `/docs/prd.md` - Product Requirements Document

## BMAD Methodology (`/.bmad-core`)

### Agents (`/.bmad-core/agents/`)
- `bmad-master.md`, `bmad-orchestrator.md`, `pm.md`, `po.md`, `sm.md`
- `architect.md`, `dev.md`, `qa.md`, `analyst.md`, `ux-expert.md`

### Checklists (`/.bmad-core/checklists/`)
- `story-draft-checklist.md`, `story-dod-checklist.md`
- `architect-checklist.md`, `change-checklist.md`
- `pm-checklist.md`, `po-master-checklist.md`

### Tasks (`/.bmad-core/tasks/`)
- Story management: `create-next-story.md`, `validate-next-story.md`, `review-story.md`
- Epic management: `brownfield-create-epic.md`, `brownfield-create-story.md`
- Documentation: `create-doc.md`, `shard-doc.md`, `document-project.md`, `index-docs.md`
- Other: `execute-checklist.md`, `advanced-elicitation.md`, `kb-mode-interaction.md`

### BMAD Guides
- `.bmad-core/user-guide.md` - Main BMAD user guide
- `.bmad-core/working-in-the-brownfield.md` - Brownfield development guide
- `.bmad-core/enhanced-ide-development-workflow.md` - IDE workflow guide

## Reports (`/reports/`)
- QA Reports: `QA_REVIEW_EPIC1.md`, various `qa-report-*.md` and `qa-story-*.md` files
- Story Reports: Various `story-*.md` completion and assessment reports
- Epic Reports: `epic-1-velocity-report.md`, `epic-1-retrospective-report.md`, etc.
- Architecture Reports: `arch_overview.md`, `architecture-checklist-report.md`

## Claude Integration (`/.claude/`)
- `.claude/agents/` - Claude-specific agent definitions
- `.claude/commands/BMad/` - BMAD command definitions (mirrors .bmad-core structure)
- `.claude/.claude/CLAUDE.md` - Claude configuration

## Serena Memories (`/.serena/memories/`)
- `project_overview.md` - Project purpose and goals
- `code_style_conventions.md` - Coding standards
- `suggested_commands.md` - Development commands
- `task_completion_checklist.md` - Task completion steps
- `codebase_structure.md` - Directory organization
- `bmad_methodology.md` - BMAD process overview

## Other Directories
- `.github/chatmodes/` - GitHub chat mode configurations
- `.gemini/bmad-method/GEMINI.md` - Gemini integration
- `.archive-docs-DO NOT-read/` - Archived documentation
- `references/openai-examples/completions/DEPRECATED.md` - Deprecated examples