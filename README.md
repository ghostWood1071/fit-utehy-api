# FastAPI Async Codebase

## Structure

```text
app/
  api/v1/            # router API
  core/
    auth/            # Auth0 integration
    db/              # abstraction database layer
  db/                # session + postgres adapter wiring
  models/            # SQLAlchemy models
  repositories/      # data access
  schemas/           # pydantic schemas
  services/          # business logic
tests/               # unit tests
```

## Local run

```bash
cp .env .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test run

```bash
pytest -q
```

## Docker

```bash
docker build -t fastapi-async-base .
docker run --env-file .env -p 8000:8000 fastapi-async-base
```

## Auth0

Auth0 config:
- `AUTH0_DOMAIN`
- `AUTH0_AUDIENCE`
- `AUTH0_ISSUER`
- `AUTH0_ALGORITHMS`
