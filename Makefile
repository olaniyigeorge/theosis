.PHONY: dev

## Start the full local development environment.
## This starts Postgres, Redis, the FastAPI backend, and the Next.js frontend.
dev:
	@./scripts/dev.sh
