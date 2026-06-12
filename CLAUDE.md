# Claude E-commerce POC Project

This file provides context for Claude, the AI assistant, working on this project.

## Project Overview

This project is a Proof of Concept (POC) for an e-commerce backend.

- **Technology Stack:**
  - Python 3.12
  - FastAPI
  - Pydantic v2

- **Database:**
  - Starts with in-memory dummy data.
  - The architecture is designed for easy migration to a real database (e.g., PostgreSQL with SQLAlchemy).

## Architecture

The project follows a clean, layered architecture:

- `app/api`: API endpoints (routes).
- `app/schemas`: Pydantic models for request/response validation.
- `app/services`: Business logic layer.
- `app/repositories`: Data access layer (abstracts the data source).
- `app/models`: Core data models (business entities).
- `app/core`: Configuration, logging, and security.
- `app/dependencies`: FastAPI dependency injection.
- `app/exceptions`: Custom exceptions and handlers.
- `app/utils`: Utility functions.
- `tests/`: Unit and integration tests.

## Development Workflow

1.  **Architectural Design:** Define and agree upon folder structures and architectural patterns before writing implementation code.
2.  **Layered Implementation:** Implement features layer by layer, starting from models and repositories and moving up to services and the API.
3.  **Dependency Injection:** Use FastAPI's dependency injection system to manage dependencies like repositories and services, promoting loose coupling.
4.  **Type Hinting:** Use Python 3.12 type hints throughout the codebase for clarity and robustness.
