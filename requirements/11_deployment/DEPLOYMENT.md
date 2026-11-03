# Deployment

## Development

Frontend:
Vite

Backend:
Uvicorn/FastAPI

Database:
MySQL 8.x local Docker/container or managed MySQL

## Production

Frontend can be hosted separately from backend.

Backend connects privately to MySQL where possible.

## Environment variables

Frontend:
VITE_API_URL

Backend:
MYSQL_URL
JWT_SECRET
CORS_ORIGINS
GST_PROVIDER_API_KEY
GST_PROVIDER_BASE_URL
APP_ENV

## Production requirements

- HTTPS
- restricted CORS
- secure headers
- rate limiting
- database backups
- monitoring
- structured logging
- health check
- secrets management
- tested restore procedure

## CI/CD

1. install dependencies
2. lint
3. run unit tests
4. run integration tests
5. build frontend
6. run migration checks
7. deploy

Failed tests must block production deployment.

## Database backup

Backups must be automated according to the selected hosting environment.

At least one restoration test must be performed before production launch.
