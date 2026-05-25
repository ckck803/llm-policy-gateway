# LLM Policy Gateway

Django + Vue 3 Composition API MVP for hybrid LLM routing policy experiments.

The first provider is local Ollama. OpenAI and Gemini are available through provider adapters and can be enabled by adding API keys and activating their catalog models.

## Features

- Policy-based `/api/chat/` endpoint
- Ollama, OpenAI, and Gemini provider adapters
- Prompt analyzer for sensitive data, code prompts, long context, and reasoning signals
- Model catalog and routing policy seed data
- Routing logs and dashboard metrics
- Vue 3 admin dashboard with Playground, Models, Policies, and Routing Logs

## Run Backend

```bash
cd /Users/dongwoo-yang/develop/llm-policy-gateway
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
.venv/bin/python backend/manage.py migrate
.venv/bin/python backend/manage.py seed_demo
.venv/bin/python backend/manage.py runserver 127.0.0.1:8000
```

## Authentication

The API uses DRF token authentication. Create an initial admin user for local development:

```bash
.venv/bin/python backend/manage.py shell -c "from django.contrib.auth.models import User; u,_=User.objects.get_or_create(username='admin', defaults={'is_staff': True, 'is_superuser': True, 'is_active': True}); u.is_staff=True; u.is_superuser=True; u.is_active=True; u.set_password('admin1234'); u.save()"
```

Sign in from the web app with `admin / admin1234`, then use the Users screen to create operators and assign allowed screens. Backend APIs also enforce those screen permissions; hiding tabs in the UI is not the only protection.

New and changed passwords are stored with Django's `BCryptSHA256PasswordHasher`. PBKDF2 remains configured as a fallback so older local users can still sign in.

## Run Frontend

```bash
cd /Users/dongwoo-yang/develop/llm-policy-gateway/frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Ollama

Start Ollama locally before using the Playground:

```bash
ollama serve
ollama pull llama3.1:8b
```

The seeded demo also includes `codellama:latest` and `qwen3:8b`; pull whichever models you want to use.

## OpenAI and Gemini

OpenAI and Gemini credentials can be managed from the Credentials screen. Base URLs and access tokens are stored encrypted with Fernet symmetric encryption.

For production-like use, set a stable encryption key before creating credentials:

```bash
.venv/bin/python - <<'PY'
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
PY
export CREDENTIAL_ENCRYPTION_KEY="generated-key"
```

Environment variables are still supported as a fallback if no active credential exists in the database:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export GEMINI_API_KEY="your-gemini-api-key"
.venv/bin/python backend/manage.py runserver 127.0.0.1:8000
```

Seeded OpenAI/Gemini catalog rows are inactive by default. Enable them from the Models screen after the corresponding credential is configured.

The adapters use:

- OpenAI Responses API: `POST https://api.openai.com/v1/responses`
- Gemini generateContent API: `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
