# Copilot Instructions for AI Coding Agents

This codebase is a multi-service AI chat demo for KubeCon NA 2025, built to showcase RAG pipelines and agent orchestration using KAITO, FastAPI, Next.js, Redis, and OpenTelemetry. Follow these guidelines to be immediately productive:

## Project Overview

This is a monorepo containing:

- **Backend AI Agent** (`src/agent/`) - Python-based AI agent using agent-framework and OpenAI
- **Frontend Chat UI** (`src/web/`) - Next.js-based chat interface for user interactions

### Repository Structure

```
src/
  agent/
    agent/        # Backend AI agent development
  web/       # Next.js web chat UI
```

## Architecture Overview

- **Services:**
  - `src/web/` (Next.js): Chat UI, API proxy
  - `src/agent/` (FastAPI): AI agent logic, OpenAI API integration, session management, CORS
  - **Redis**: Session and conversation history (managed by agent service)
  - **OpenTelemetry**: Distributed tracing
- **Data Flow:**
  - Frontend → Agent Service (simplified, no middleware)
  - Redis and OpenTelemetry are dependencies of the agent service
- **See:** `ARCHITECTURE.md` for diagrams and rationale

## Developer Workflows

- **Start all services:**
  - Infra: `docker compose up -d` in `src/agent/`
  - Agent: `uv sync && uv run python main.py` in `src/agent/`
  - Frontend: `bun install && bun run dev` in `src/web/`
- **Stop all:** `docker compose down` in `src/agent/`
- **Testing:**
  - Agent: `curl -X POST http://localhost:8001/chat -H "Content-Type: application/json" -d '{"message": "Hello!"}'`
  - Health: `curl http://localhost:8001/health`
  - Full stack: Use browser at `http://localhost:3000`

---

## Backend: AI Agent Development (`src/agent/`)

### Technologies

- Python 3.12+
- `uv` for package management
- `agent-framework` for building AI agents
- OpenAI models for AI capabilities
- FastAPI for REST API
- Redis for session management
- OpenTelemetry for distributed tracing

### Development Environment

#### Package Management

- Use `uv` for all Python package management operations
- Run `uv sync` to install dependencies from `pyproject.toml`
- Run `uv add <package>` to add new dependencies
- Run `uv remove <package>` to remove dependencies
- Use `uv run <command>` to execute commands in the virtual environment
- Never use `pip` directly; always use `uv` equivalents

#### Python Version

- Requires Python 3.12 or higher
- Specify Python version in `pyproject.toml` under `[project]` section
- Use `uv python install <version>` to install specific Python versions
- Use `uv python pin <version>` to pin the project to a specific Python version

#### Working Directory

- All agent commands should be run from `src/agent/` directory
- Example: `cd src/agent && uv sync`

### Project Conventions

- **Python:**
  - Use `uv` for dependency management
  - Type hints and PEP8 style
  - Async/await for agent operations
  - Environment variables for secrets (never hardcode)
  - See `AGENTS.md` for agent-framework and OpenAI API best practices
  - Use `ruff` for Python linting (in dev dependencies)

---

## Frontend: Next.js Chat UI (`src/web/`)

### Technologies

- Next.js 15.5.4 with Turbopack
- React 19
- TypeScript
- Tailwind CSS v4
- Bun as package manager

### Development Environment

#### Package Management

- Use `bun` for all package management operations
- Run `bun install` to install dependencies
- Run `bun add <package>` to add new dependencies
- Run `bun remove <package>` to remove dependencies
- Never use `npm` or `yarn`; always use `bun`

#### Available Scripts

- `bun dev` - Start development server with Turbopack
- `bun build` - Build for production with Turbopack
- `bun start` - Start production server
- `bun lint` - Run ESLint

#### Working Directory

- All web commands should be run from `src/web/` directory
- Example: `cd src/web && bun dev`

#### Styling

- Use Tailwind CSS v4 for styling
- Configuration in `postcss.config.mjs`

#### TypeScript

- Strict TypeScript configuration
- Type definitions in `next-env.d.ts`
- Custom types should be added to appropriate `.d.ts` files

### Project Conventions

- **Frontend:**
  - TypeScript, modular React components, Tailwind CSS
  - Chat logic in `hooks/useChat.ts`, UI in `components/chat/`
  - API proxy in `app/api/chat/route.ts`
  - Use ESLint with Next.js config
  - Follow Next.js 15 App Router conventions
  - Ensure TypeScript types are properly defined

---

## Configuration

- `.env.example` files in each service; copy and edit as needed
- Key env vars: `OPENAI_API_KEY`, `AGENT_SERVICE_URL`, Redis config
- Consider using environment variables for configuration
- Never hardcode secrets

## Observability

- OpenTelemetry tracing is enabled by default
- See `otel-config.yaml` in agent service

---

## General Guidelines

### When Working on Backend (AI Agent)

1. Change directory to `src/agent/`
2. Use `uv` for all Python operations
3. Follow agent-framework patterns and conventions
4. Test agent functionality thoroughly

### When Working on Frontend (Chat UI)

1. Change directory to `src/web/`
2. Use `bun` for all package operations
3. Follow Next.js 15 App Router conventions
4. Ensure TypeScript types are properly defined
5. Use Tailwind CSS for styling

### Cross-Cutting Concerns

- Ensure web can communicate with agent agent APIs
- Maintain consistent error handling between web and agent
- Document any API contracts between the two services
- Write clean, maintainable code with proper documentation
- Follow established patterns in existing codebase

### Code Quality

- Backend: Use `ruff` for Python linting (in dev dependencies)
- Frontend: Use ESLint with Next.js config
- Write clean, maintainable code with proper documentation
- Follow established patterns in existing codebase

---

## Integration Points

- **Agent Service:** Integrates with OpenAI API (or Ollama via `OPENAI_BASE_URL`)
- **Redis:** Used for session and chat history (see compose.yaml)
- **Frontend:** Communicates directly with agent service via Next.js API routes

## Troubleshooting

- **Redis issues:** Check Docker status, use `redis-cli ping`
- **Agent errors:** Ensure API key is set, check logs in `main.log`
- **Frontend issues:** Verify agent health with `curl http://localhost:8001/health`, check `AGENT_SERVICE_URL`
- **Port conflicts:** Use `lsof -ti:<port> | xargs kill -9`

## References

- `README.md`, `ARCHITECTURE.md`, `AGENTS.md` for deeper context
- Official docs: agent-framework (pypi.org), OpenAI API (platform.openai.com)

---

**Always verify library versions and API changes before coding. When in doubt, consult documentation and note any assumptions.**
