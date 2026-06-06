# CureDesk

Mobile-first telehealth platform — **Expo** (primary) + **Next.js** (web), sharing a **FastAPI** backend with symptom ML, prescription OCR, and Groq-powered chat.

## Monorepo layout

```text
curedesk/
├── apps/
│   ├── mobile/          # Expo (React Native) — primary client
│   └── web/             # Next.js — marketing + desktop flows
├── packages/
│   └── shared/          # API client, types, theme, constants
├── services/
│   └── api/             # FastAPI + Postgres + ML inference
├── ml/                  # Python training scripts (no notebooks)
├── docker-compose.yml
└── turbo.json
```

## Prerequisites

- Node.js 20+
- Python 3.12+
- pnpm 9 (`corepack enable && corepack prepare pnpm@9.15.0 --activate`)
- Docker (for Postgres locally)

## Quick start

### 1. Environment

Copy `.env.example` to `.env` and fill in values (Firebase, Groq, optional Sentry).

### 2. Database

```bash
docker compose up postgres -d
pnpm db:migrate
pnpm db:seed
```

### 3. ML artifacts

**CPU (default when no CUDA):**
```bash
pnpm ml:train:cpu
python ml/eval_symptoms.py
```

**NVIDIA RTX / CUDA GPU (recommended on Windows/Linux with CUDA):**
```bash
pip install -r ml/requirements-gpu.txt
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
pnpm ml:train:gpu
python ml/eval_ocr.py --gpu
```

Auto-detects your RTX GPU when CUDA PyTorch is installed. Symptom training uses **XGBoost on CUDA**; OCR uses **EasyOCR on GPU**.

```bash
pnpm ml:train          # auto: GPU if CUDA available, else CPU
python ml/eval_ocr.py  # same auto-detect for OCR eval
```

### 4. API

```bash
pnpm api:dev
# http://localhost:8000/health
# http://localhost:8000/docs
```

### 5. Frontends

```bash
pnpm install
pnpm dev:web      # http://localhost:3000
pnpm dev:mobile   # Expo dev server
```

For physical devices, set `EXPO_PUBLIC_API_URL` to your machine's LAN IP.

## CLI setup (recommended)

```powershell
# Full setup (Python deps, ML train, DB, pnpm install)
npm run setup

# Or step by step:
npm run setup:ml:data     # Legacy: Kaggle symptom CSV + BD prescription images
npm run setup:ml:data:all # All recommended datasets (symptoms, OCR, drugs, RAG)
npm run setup:db          # Docker Postgres + migrate + seed
npm run setup:ml:gpu      # Train symptom model (or setup:ml / ml:train:cpu)
npm run api:dev           # Start API

# Firebase (interactive — opens browser to login)
npm run setup:firebase -- -ProjectId YOUR_FIREBASE_PROJECT_ID
```

Use `npx pnpm@9.15.0` instead of `pnpm` if pnpm is not on PATH.

## Firebase setup (CLI)

1. Create a project: [Firebase Console](https://console.firebase.google.com) or `npx firebase-tools projects:create curedesk-app`
2. Enable **Google** + **Email/Password** in Authentication (console or after login)
3. Register a web app in console, then pull env into clients:

```powershell
npm run setup:firebase -- -ProjectId YOUR_PROJECT_ID
```

4. Service account for API (Google Cloud CLI):

```powershell
gcloud auth login
gcloud iam service-accounts keys create firebase-sa.json `
  --iam-account=firebase-adminsdk-XXXX@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

Add to `services/api/.env`:

```text
FIREBASE_SERVICE_ACCOUNT_JSON=firebase-sa.json
```

## OpenAPI type generation

With the API running:

```bash
pnpm generate:types
```

Updates `packages/shared/src/types.generated.ts`.

## Environment variables

See [.env.example](.env.example) for the full list. Key vars:

| Variable | Used by |
|----------|---------|
| `DATABASE_URL` | FastAPI |
| `GROQ_API_KEY` | Chat endpoint |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | FastAPI token verification |
| `NEXT_PUBLIC_*` / `EXPO_PUBLIC_*` | Client Firebase + API URL |
| `OCR_USE_GPU` | FastAPI OCR — `auto`, `true`, or `false` |
| `ML_USE_GPU` | Documented preference; use `pnpm ml:train:gpu` for training |

## Smoke test checklist

- [ ] `GET /health` → `{ "status": "ok" }`
- [ ] `GET /ready` → `db: true`, `ml: true` (after train + Postgres)
- [ ] Web: symptom form → predictions → disease detail page
- [ ] Web: prescription upload → OCR text + drug matches
- [ ] Web: chatbot → Groq reply
- [ ] Mobile: same flows via tabs
- [ ] Email + Google login → profile history (when Firebase configured)
- [ ] `pnpm typecheck` and `pytest` pass

## Security note

A legacy Gemini API key was previously committed in deleted source files. **Rotate that key** in Google Cloud Console if the repository was ever public or shared.

## Scripts

| Command | Description |
|---------|-------------|
| `pnpm setup` | Full CLI setup script |
| `pnpm setup:ml:data` | Download legacy Kaggle symptom + prescription datasets |
| `pnpm setup:ml:data:all` | Download all recommended ML datasets (~500 MB) |
| `pnpm setup:ml:data:large` | Include large HF datasets (~3–5 GB) |
| `pnpm setup:db` | Docker Postgres + migrate + seed |
| `pnpm setup:firebase` | Pull Firebase SDK config into client `.env` files |
| `pnpm dev:web` | Next.js dev server |
| `pnpm dev:mobile` | Expo dev server |
| `pnpm api:dev` | FastAPI with hot reload |
| `pnpm ml:train` | Train symptom classifier (auto GPU/CPU) |
| `pnpm ml:train:gpu` | Force XGBoost training on NVIDIA CUDA |
| `pnpm ml:train:cpu` | Force CPU RandomForest training |
| `pnpm db:seed` | Seed Postgres from CSVs |
| `pnpm db:migrate` | Run Alembic migrations |
| `pnpm generate:types` | OpenAPI → TypeScript codegen |
| `pnpm typecheck` | TypeScript check all packages |

## Phase 2 (not in scope)

Async OCR queue, Groq streaming, EAS production builds, PWA — see plan roadmap.
