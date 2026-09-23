# RelayForge

[![Tests](https://github.com/jecas/relayforge/actions/workflows/tests.yml/badge.svg)](https://github.com/jecas/relayforge/actions/workflows/tests.yml)

RelayForge is a resilient asynchronous API integration service built with Python, FastAPI, HTTPX, PostgreSQL, and Docker.

It demonstrates production-oriented patterns for integrating external providers with different authentication and request flows while exposing a consistent API to clients.

The project focuses on problems commonly found in backend integration services: asynchronous HTTP communication, multi-step authentication, provider abstraction, retries, timeouts, external error normalization, correlation IDs, structured logging, persistence, and end-to-end testing.

## Key Features

- Asynchronous FastAPI application
- Async external API communication with HTTPX
- Provider abstraction with multiple provider implementations
- Multi-step authorization flow
- API-key-based provider integration
- Configurable request timeouts
- Retry strategy for transient provider failures
- Exponential retry delay
- `Retry-After` support for rate-limited requests
- Normalized provider error responses
- Correlation ID propagation
- Structured application logging
- PostgreSQL audit persistence
- Async SQLAlchemy
- Alembic database migrations
- Mock external provider for integration and E2E testing
- Docker Compose development environment
- Unit and integration tests
- Full-stack end-to-end tests
- GitHub Actions CI
- Docker image validation in CI

## Architecture

RelayForge separates the public API, orchestration logic, provider-specific integrations, and persistence layer.

```text
Client
  │
  ▼
FastAPI
  │
  ▼
VerificationService
  │
  ▼
ProviderFactory
  │
  ├──────────────────────┐
  │                      │
  ▼                      ▼
AlphaProvider        BetaProvider
  │                      │
  ▼                      ▼
External Alpha API   External Beta API
  │                      │
  └──────────┬───────────┘
             │
             ▼
      Normalized Result
             │
             ▼
        PostgreSQL
      Verification Audit
```

The API does not depend on provider-specific response formats. Each provider implementation is responsible for communicating with its external API and converting the provider response into RelayForge's normalized verification model.

## Provider Integrations

RelayForge currently demonstrates two different integration styles.

### Alpha Provider

Alpha represents a provider with a multi-step authentication flow.

```text
POST /api/v1/verifications
        │
        ▼
VerificationService
        │
        ▼
AlphaProvider
        │
        ├── POST /oauth/authorize
        │          │
        │          ▼
        │     auth_req_id
        │
        ├── POST /oauth/token
        │          │
        │          ▼
        │     access_token
        │
        └── POST /verify
                   │
                   ▼
             provider result
                   │
                   ▼
          normalized response
```

The complete provider flow is treated as a single logical operation by the retry layer. A retryable failure causes the flow to be executed again from the appropriate service boundary rather than exposing provider-specific behavior to API clients.

### Beta Provider

Beta demonstrates a simpler API-key-based integration.

```text
VerificationService
        │
        ▼
BetaProvider
        │
        ▼
POST /beta/verify
        │
        ▼
Provider Response
        │
        ▼
Normalized Result
```

Despite having different external protocols, Alpha and Beta implement the same provider abstraction and return the same internal verification model.

## Resilience

External APIs can fail for many reasons, including temporary outages, rate limits, and network timeouts.

RelayForge maps these failures into application-level exceptions and retries only failures considered transient.

Retryable failures include:

- provider timeouts
- rate limiting
- temporary provider unavailability

Non-retryable failures, such as authentication errors and invalid requests, fail immediately.

The retry mechanism supports configurable maximum attempts and exponential delay between attempts.

When a provider returns a `Retry-After` value for a rate-limited request, RelayForge uses that value when determining how long to wait before retrying.

## Error Normalization

Provider-specific HTTP errors are translated into a consistent RelayForge error model.

This keeps external implementation details behind the provider boundary and gives API clients predictable error responses regardless of which provider was selected.

Example normalized error response:

```json
{
  "correlation_id": "request-123",
  "error": {
    "code": "provider_unavailable",
    "message": "Provider is temporarily unavailable."
  }
}
```

## Correlation IDs

RelayForge uses `X-Correlation-ID` to trace requests across the API and external provider calls.

When a client supplies a correlation ID, RelayForge preserves it.

```text
Client
  │
  │ X-Correlation-ID
  ▼
RelayForge API
  │
  ├── Logs
  │
  ├── Provider requests
  │
  ├── API response
  │
  └── Verification audit
```

If the header is missing, RelayForge generates a correlation ID automatically.

The correlation ID is also returned to the client in the response headers and response payload.

## Observability

Application logs are emitted as structured JSON and include request context such as the correlation ID.

This makes logs easier to ingest and query in centralized logging systems while preserving request traceability across integration flows.

## Persistence

Successful verification requests are persisted in PostgreSQL as audit records.

The audit contains operational metadata such as:

- correlation ID
- selected provider
- verification status
- normalized risk level
- creation timestamp

Sensitive request data such as the phone number is intentionally not stored in the audit record.

Database access uses async SQLAlchemy and schema changes are managed with Alembic migrations.

## Mock Provider

The repository contains a mock external provider used for local development and end-to-end testing.

It implements the external endpoints required by both provider integrations and can simulate scenarios such as:

- successful verification
- provider unavailability
- rate limiting
- request timeout

This allows the complete integration flow to be tested without depending on real third-party services.

## Running with Docker Compose

### Requirements

- Docker
- Docker Compose

Start the complete stack:

```bash
docker compose up --build
```

The stack includes:

```text
RelayForge API      http://localhost:8000
Mock Provider       http://localhost:9000
PostgreSQL
```

The API health endpoint is available at:

```text
GET http://localhost:8000/health
```

Interactive FastAPI documentation is available at:

```text
http://localhost:8000/docs
```

Database migrations are automatically applied when the API container starts.

To stop the stack:

```bash
docker compose down
```

To also remove the PostgreSQL volume:

```bash
docker compose down -v
```

## API Usage

### Alpha Provider

```bash
curl -X POST http://localhost:8000/api/v1/verifications \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: example-alpha-001" \
  -d '{
    "phone_number": "+381641234567",
    "provider": "alpha"
  }'
```

### Beta Provider

```bash
curl -X POST http://localhost:8000/api/v1/verifications \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: example-beta-001" \
  -d '{
    "phone_number": "+381641234567",
    "provider": "beta"
  }'
```

Both integrations return the same normalized response structure:

```json
{
  "correlation_id": "example-alpha-001",
  "result": {
    "verified": true,
    "risk_level": "low",
    "provider": "alpha"
  }
}
```

## Testing

RelayForge uses several testing layers.

### Unit Tests

Unit tests cover isolated application behavior including:

- Alpha provider flow
- Beta provider flow
- provider error mapping
- retry behavior
- timeout handling
- protocol validation
- verification service orchestration

### Integration Tests

Integration tests cover API-level behavior including:

- verification endpoint
- correlation ID preservation
- correlation ID generation
- normalized provider failures

### End-to-End Tests

The E2E suite starts the complete Docker Compose stack:

```text
E2E Test
   │
   ▼
RelayForge API
   │
   ├──────────────► Mock Provider
   │
   ▼
PostgreSQL
```

The tests exercise real HTTP communication between containers and verify persisted audit records in PostgreSQL.

Run the standard test suite with:

```bash
pytest -v
```

Run linting with:

```bash
ruff check .
```

## Continuous Integration

GitHub Actions validates the project on every push and pull request.

The CI pipeline:

1. installs the project and development dependencies
2. runs Ruff
3. validates Alembic migrations with upgrade → downgrade → upgrade
4. runs the pytest suite
5. builds the RelayForge Docker image
6. builds the mock-provider Docker image
7. starts the complete Docker Compose stack
8. waits for the API health check
9. runs the E2E suite
10. verifies persisted PostgreSQL audit records

This validates both isolated application behavior and the complete runtime integration flow.

## Technology Stack

- Python 3.12
- FastAPI
- HTTPX
- Pydantic
- PostgreSQL
- SQLAlchemy 2
- asyncpg
- Alembic
- Docker
- Docker Compose
- Pytest
- Ruff
- GitHub Actions

## Project Structure

```text
relayforge/
├── alembic/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── providers/
│   │   ├── alpha/
│   │   └── beta/
│   ├── repositories/
│   ├── schemas/
│   └── services/
├── mock_provider/
├── scripts/
├── tests/
│   ├── integration/
│   └── unit/
├── .github/
│   └── workflows/
├── compose.yml
├── Dockerfile
├── alembic.ini
└── pyproject.toml
```

## Design Goals

RelayForge is intentionally focused on integration-service concerns rather than CRUD functionality.

The project demonstrates how a Python backend can isolate provider-specific behavior, remain resilient to transient external failures, provide consistent responses to clients, preserve request traceability, and validate the complete integration flow through automated tests.

The external providers used by this project are fictional and implemented specifically for demonstration and testing purposes.
