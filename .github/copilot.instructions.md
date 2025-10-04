# AI Agent Development Instructions

## Project Overview

This project uses Python with `uv` for package management, `agent-framework` for building AI agents, and OpenAI models for AI capabilities.

## Development Environment

### Package Management

- Use `uv` for all Python package management operations
- Run `uv sync` to install dependencies from `pyproject.toml`
- Run `uv add <package>` to add new dependencies
- Run `uv remove <package>` to remove dependencies
- Use `uv run <command>` to execute commands in the virtual environment
- Never use `pip` directly; always use `uv` equivalents

### Python Version

- Specify Python version in `pyproject.toml` under `[project]` section
- Use `uv python install <version>` to install specific Python versions
- Use `uv python pin <version>` to pin the project to a specific Python version
