# Ask Aman — Progress

## Current project architecture

- `aman-portfolio/` is a JavaScript-only Vite 8 single-page React 19 application. `src/main.jsx` mounts `App.jsx` inside `StrictMode`.
- There is no router or multi-page route structure. `App.jsx` composes the one-page portfolio in this order: Hero, About (which includes Beyond Code), Education, Skills, Projects, Experience, Contact, then Footer and Back to Top.
- Page content is held in plain JavaScript modules under `src/data/` (`profile`, `projects`, `experience`, `education`, and `skills`).
- UI is organized into `components/common`, `components/layout`, and `components/sections`; static assets live in `src/assets` and `public`.
- `api/index.py` is a module-scope, Vercel-compatible FastAPI entry point. It provides the non-Gemini `GET /api/health` endpoint and the grounded `POST /api/ask` endpoint.

## Relevant dependencies

- Frontend runtime: `react`, `react-dom`, `tailwindcss`, `@tailwindcss/vite`.
- Development: `vite`, `@vitejs/plugin-react`, `oxlint`.
- Backend requirements: `fastapi`, `google-genai`, `numpy`, and `python-dotenv` only. No LangChain, LangGraph, FAISS, ChromaDB, Pinecone, Supabase, SentenceTransformers, or database dependency is present.

## Build commands

- `npm run dev` — Vite development server.
- `npm run build` — Vite production build.
- `npm run lint` — Oxlint.
- `python -m pip install -r requirements.txt` — install the lightweight backend dependencies locally.
- `python scripts/validate_rag_data.py` — validate the JSON knowledge base.
- There is no `test` script or test framework configured.

## Important existing conventions

- JavaScript and JSX use ES modules with `.jsx` React components and `.js` data modules.
- Tailwind CSS v4 is enabled through the Vite plugin; `src/index.css` defines the `portfolio-*` theme colors, root design tokens, shared component classes, and responsive CSS.
- The visual system is dark (`#080B14`) with blue, violet, and cyan accents, Sora display headings, Inter body text, rounded cards, and responsive Tailwind breakpoints plus custom media queries.
- Existing animations use CSS keyframes/transitions and `RevealOnScroll` with `IntersectionObserver`; they respect `prefers-reduced-motion`. No animation library is used.
- Icons are inline SVG paths. Reusable controls include `PrimaryButton`, `SecondaryButton`, `Tag`, `Container`, `SectionHeading`, and `RevealOnScroll`.
- Interactive overlays (`MobileMenu`, `ProjectModal`) manage Escape, focus, scroll locking, and return focus. Preserve those accessibility conventions for a future chat overlay.
- `.gitignore` excludes `node_modules`, `dist`, `.env`, `.env.*`, and `*.local`, while explicitly retaining `.env.example`. The Gemini key is read only by Python from an unprefixed `GEMINI_API_KEY`; React does not read it and no `VITE_` key is used.

## Files created

- `api/.gitkeep`
- `rag_data/.gitkeep`
- `scripts/.gitkeep`
- `src/components/AskAman/.gitkeep`
- `ASK_AMAN_PROGRESS.md`
- `rag_data/about.json` (6 records)
- `rag_data/education.json` (3 records)
- `rag_data/skills.json` (6 records)
- `rag_data/projects.json` (12 records)
- `rag_data/experience.json` (3 records)
- `rag_data/contact.json` (3 records)
- `rag_data/faq.json` (8 records)
- `scripts/validate_rag_data.py`
- `api/__init__.py`
- `api/config.py`
- `api/models.py`
- `api/data_loader.py`
- `api/errors.py`
- `api/index.py`
- `api/intent_router.py`
- `requirements.txt`
- `.env.example`
- `tests/test_intent_router.py`
- `scripts/build_index.py`
- `rag_data/vectors.json` (generated locally; 41 vectors)
- `api/retriever.py`
- `tests/test_retriever.py`
- `api/prompt.py`
- `api/gemini_service.py`
- `api/rag_service.py`
- `tests/test_api_ask.py`

The knowledge base contains 41 focused retrieval records across seven JSON files. It uses only currently displayed portfolio facts and omits all `REPLACE_WITH...` and case-study placeholder content. No embeddings, RAG runtime, or chat-interface code has been added.

## Knowledge-base validation

- Run `python scripts/validate_rag_data.py` from `aman-portfolio/`.
- The validator checks JSON parsing, required fields, unique IDs, valid categories, non-empty content, keywords, and that each record category matches its file.
- Validation result: passed — 41 records across 7 files.

## Content requiring manual confirmation

- The original poetry excerpt for the Beyond Code section is still a placeholder and was excluded.
- The resume URL is still a placeholder and was excluded.
- GitHub and live-demo URLs for HireSense AI, Kaushik Footprints, and the Land Bidding Platform are placeholders and were excluded.
- Project case-study details, architecture/workflow details, and screenshots are placeholders or absent and were excluded.
- The Poetic Pebbles "AI Search and Assistant (under development)" status is currently displayed and included; confirm it remains current before a production knowledge-base refresh.

## Potential integration concerns

- No `vercel.json` is present. The current app is a static Vite site; a future FastAPI endpoint must be shaped for Vercel's Python serverless-function model and Hobby limits.
- The later frontend should use a same-origin `/api/...` route or a public `VITE_` setting only for a non-secret base URL. Backend-only configuration must remain server-side; no environment-variable convention currently exists.
- `requirements.txt` contains the only required Python packages. The data loader uses paths derived from its own module location, so it can find `rag_data/` when initialized by a Vercel Python Function.
- Keep the existing section order unchanged. A floating or independently mounted Ask Aman control is the least disruptive likely integration point; it must preserve mobile layout, keyboard/focus behavior, and reduced-motion behavior.
- Portfolio source data is a useful future knowledge base, but it includes visible placeholders and encoded punctuation that should be handled deliberately during retrieval preparation.
- Existing deployment metadata still contains canonical-domain and social-image placeholders.
- The FastAPI entry point is initialized at module scope for Vercel Python Functions. It currently exposes only `GET /api/health`; it does not create a Gemini client, generate embeddings, or make any external request.
- `.env` and `.env.*` are ignored while `.env.example` remains tracked. Gemini configuration is read only in Python from unprefixed `GEMINI_*` variables and must never be copied into React or a `VITE_` variable.

## Baseline build result

- `npm run build`: passed. Vite transformed 54 modules and produced the production bundle successfully.
- `npm run lint`: passed with no output.
- Test baseline: no test script or test framework is configured, so no automated tests were available to run.
- The first sandboxed build attempt could not load Tailwind's native oxide binary and raised `spawn EPERM`; the same unmodified build passed when run with the permitted native runtime access.

## Backend foundation validation

- Installed `requirements.txt` locally and confirmed imports for FastAPI, Google GenAI, NumPy, and python-dotenv. No Gemini client was created and no external AI service was called.
- `python -m compileall -q api` passed.
- The knowledge-loader check passed: it loaded 41 records with the expected per-category counts and raised `KnowledgeLoadError` with an understandable message for a missing knowledge directory.
- An in-process FastAPI `GET /api/health` check passed: status was `ok`, knowledge reported 41 records, and every configuration value in the response was a boolean. The check emitted an upstream Starlette TestClient deprecation warning only.
- Git-ignore verification confirmed `.env`, `.env.local`, and `.env.production` are ignored while `.env.example` is not ignored.

## Intent-routing foundation

- `api/intent_router.py` implements deterministic hybrid routing with normalized token matching, phrase matching, and named-entity matching. It does not import or call Gemini or another LLM.
- Routing signals are kept in the configurable `DEFAULT_INTENT_SIGNALS` mapping and can be replaced per intent with `IntentSignals` overrides.
- Project names are derived from project overview records and company names are derived from experience role records. Every meaningful category is scored; `related_intents` preserves multi-topic questions for future retrieval rather than restricting it to the primary category.
- Broad questions, greetings, and low-signal questions return `general`. The name "Aman" alone is not an about signal.
- Test command: `python -m unittest discover -s tests -v`.
- Test result: passed — 7 tests. Coverage includes all requested questions, single-intent routing, project-plus-skills and GlobalLogic-plus-skills multi-intent routing, greeting and low-signal general fallbacks, broad-question fallback, and configurable keyword extensions.

## Embedding-index foundation

- `scripts/build_index.py` loads and validates all 41 knowledge records, builds retrieval-document text from titles, content, and keywords, preserves source metadata and SHA-256 fingerprints, and writes a completed compact JSON index atomically.
- The configured embedding model is `gemini-embedding-001`. Document vectors use `RETRIEVAL_DOCUMENT`; the index records `RETRIEVAL_QUERY` for future query vectors and validates the provider-returned, consistent vector dimension.
- The builder safely reuses unchanged validated vectors, retries temporary failures with 1, 2, and 4-second exponential backoff, caps the compact index at 3 MiB, and never prints an API key.
- Commands: `python scripts/build_index.py` generates the index; `python scripts/build_index.py --validate` validates an existing index without contacting Gemini.
- Current result: the locally configured server-side credentials generated and validated `rag_data/vectors.json` successfully. No credential value is recorded here.
- Generated index: model `gemini-embedding-001`; 41 embedded knowledge records; vector dimension 3072. Validation confirmed every current knowledge record has one compatible embedding.

## Hybrid-retrieval foundation

- `api/retriever.py` loads the knowledge base and persisted vector index once at module initialization. It validates that every vector ID, metadata field, content fingerprint, model, task type, and vector dimension match the current knowledge records; missing or stale indexes produce a clear `RetrievalInitializationError`.
- Each retrieval call generates exactly one compatible query embedding, calculates cosine similarity against the private in-memory document matrix, applies configurable primary/related intent boosts (0.06/0.03 scaled by router confidence), and applies a semantic relevance threshold of 0.28.
- Intent-aware and global semantic candidates are merged and deduplicated by record ID. Global candidates remain eligible even when their category differs from the router result. The default result limit is three records.
- Public `RetrievedRecord` results contain only record ID, title, category, source section, content, semantic score, applied intent boost, and final score; raw vectors are never returned.
- `tests/test_retriever.py` uses a complete mocked index and query-embedding callbacks, so no test consumes Gemini quota. It covers named projects, high-confidence boosts, multi-intent experience-and-skills questions, general search, global fallback, deduplication, missing information, and stale-index errors.
- Test result: `python -m unittest discover -s tests -v` passed — 15 tests total (7 router and 8 retriever). Knowledge validation and Python compilation also passed.
- Runtime verification passed: after index validation, a fresh import loaded the 41 knowledge records and persisted vector index once at module initialization with no initialization error. This verification did not generate a query embedding or call Gemini.

## Public Ask Aman endpoint

- `api/prompt.py` creates a context-only system prompt that requires third-person, concise answers, rejects invented portfolio details and prompt-injection instructions, keeps prompts and internals private, and recommends Contact when relevant.
- `api/gemini_service.py` uses the current Google GenAI client with a 12-second request timeout, one generation candidate, and a 250-token output cap. It does not log questions, histories, contact data, or secrets, and maps quota, timeout, and temporary-provider failures to safe service errors.
- `api/rag_service.py` routes, retrieves at most three records, stops before generation when context is unavailable, sends only retrieved context plus up to two recent transient exchanges, and returns source titles/sections, suggestions, and the selected intent.
- `POST /api/ask` accepts a question of at most 300 characters and no more than two exchanges. It returns the documented answer/sources/suggestions/intent shape, sets `Cache-Control: no-store`, uses short-window hashed-client rate limiting, and maps invalid input, missing index, provider quota, timeout, temporary failure, retrieval failure, and unavailable information to friendly structured errors.
- CORS is same-origin in production. In local development, only `http://localhost:5173` and `http://127.0.0.1:5173` are allowed.
- `tests/test_api_ask.py` uses a mocked RAG service and verifies the success contract, input validation, error mappings, rate limiting, history bound, cache control, and that `GET /api/health` never reaches RAG or Gemini.
- Test result: `python -m unittest discover -s tests -v` passed — 20 tests total. The suite includes 8 mocked retriever tests and therefore does not consume embedding quota. `GET /api/health` remains Gemini-free.

## Current retrieval verification

- `python scripts/build_index.py --validate` passed: 41 records, dimension 3072.
- A fresh Python process imported `api.retriever`; its module-level default retriever loaded all 41 knowledge records and the persisted index once, with no initialization error.
- `python -m unittest discover -s tests -v` passed: 20 tests total, including the 8 mocked retriever tests for ranking, boosts, deduplication, global fallback, multi-intent retrieval, missing information, and stale-index handling.
- `python scripts/validate_rag_data.py` passed, and `git diff --check` found no whitespace errors. No query embedding or live answer-generation request was made during this verification.

## Current endpoint verification

- The local endpoint tests passed for successful structured responses, input validation, cache-control, history bounds, rate limiting, all requested friendly error mappings, and the guarantee that `GET /api/health` never accesses RAG or Gemini.
- Endpoint tests replace the RAG service with a local fake, so no live generation request, visitor-message persistence, or Gemini quota consumption occurred during validation.

## Comprehensive offline test suite

- Added `tests/test_backend_safety.py`. Its Gemini embedding and generation clients are local fakes, so automated tests make no external calls and use no Gemini quota.
- The suite covers knowledge loading and duplicate/missing IDs; single and multi-intent routing; cosine ranking, boosting, global fallback, deduplication, and the three-record cap; empty and overlong questions; unavailable information; prompt-injection protections; API-key secrecy; quota, timeout, temporary-provider, and malformed-response handling; health behaviour; source metadata; history limits; cache control; rate limiting; and absence of raw vectors in public responses.
- Added `scripts/smoke_ask_aman.py`, an opt-in manual request utility. It sends no request unless explicitly run with `python scripts/smoke_ask_aman.py --live`.
- Final validation: `python -m unittest discover -s tests -v` passed (30 tests); `python scripts/validate_rag_data.py` passed (41 records); `python scripts/build_index.py --validate` passed (41 vectors, dimension 3072); `npm run lint` and `npm run build` passed. No frontend test script is configured.

## Ask Aman visual interface

- Added `src/components/AskAman/AskAman.jsx`, `ChatButton.jsx`, `ChatWindow.jsx`, `ChatHeader.jsx`, `ChatMessage.jsx`, `SuggestedQuestions.jsx`, and `TypingIndicator.jsx`; the widget is mounted at the application level after the existing Footer and Back to Top control, without changing portfolio section order.
- The interface matches the portfolio's dark blue/violet/cyan visual system, Sora/Inter typography, rounded glass-like surfaces, existing focus treatment, and restrained transform/opacity motion. It provides a floating trigger, desktop panel, mobile dynamic-viewport bottom sheet, suggested questions, source badges, typing indicator, character counter, loading/error/quota/unavailable states, and reduced-motion fallbacks.
- The visual widget is connected through a same-origin `POST /api/ask` client module. Browser code calls only this backend endpoint, never Gemini directly, and includes no API key or other secret.
- Accessibility includes labelled controls, visible focus states, Escape handling, focus placement/return, a dialog focus loop, touch-sized controls, and an ARIA live conversation region.
- Final frontend validation: `npm run lint` and `npm run build` passed. The production build transformed 61 modules successfully.

## Ask Aman frontend API integration

- Added `src/components/AskAman/askAmanApi.js` and `useAskAman.js`. The hook sends only a bounded question and the two most recent transient exchanges to `/api/ask`; it uses `AbortController` for timeout/unmount cancellation, allows one active request, prevents duplicate sends, and applies a 900 ms client-side cooldown.
- Mock replies and local-preview labels were removed. The exact requested welcome message and six initial suggested questions are now used; backend suggestions replace the initial list when returned.
- Safe client-side error states cover offline, timeout, quota/rate-limit, unavailable information, validation, and other server failures. Backend error messages are not displayed. Failed questions retry without adding a second visitor message.
- Visitor messages, sources, and suggestions are rendered as React text rather than HTML. Conversation state stays only in memory, with only two successful exchanges retained for API history; no local storage or secret frontend configuration is used.
- Validation after integration: `npm run lint` passed; `python -m unittest discover -s tests -v` passed (30 tests); `npm run build` passed (63 modules transformed). No frontend test runner is configured.

## Retrieval threshold correction

- Corrected an over-strict semantic-threshold edge case for explicit, high-confidence category requests such as `Tell me about Aman`. If normal semantic retrieval yields no record, the retriever now uses the directly matched intent category only when confidence is at least 0.8 and the router matched a concrete phrase/entity.
- Broad, low-confidence, and unknown questions still require semantic evidence and continue to return the unavailable-information response rather than unrelated portfolio content.
- Added a mocked retriever test for this fallback. Current validation passed: 31 Python tests, knowledge validation (41 records), and vector-index validation (41 vectors at dimension 3072).

## Local full-stack development

- Added the `npm run dev:api` command, which runs the Vercel-compatible FastAPI app locally through `python -m uvicorn api.index:app --host 127.0.0.1 --port 8000`.
- Added a Vite development proxy for `/api` to `http://127.0.0.1:8000`. Run `npm run dev:api` in one terminal and `npm run dev` in another; the React widget can then call `/api/ask` without exposing a cross-origin URL or a secret.
- Corrected the frontend error mapper so a plain Vite 404 (which occurs when only the frontend is running) is shown as a server/setup problem, not as unavailable portfolio information.

## End-to-end local diagnosis and correction

- Root cause of the visible generic unavailable message: the React Vite server was running without a FastAPI process on port 8000. The browser therefore could not reach `/api/ask`. The Vite proxy and `dev:api` command now provide the required two-process local setup.
- `GET /api/health` now safely reports API status, knowledge readiness/count, index readiness/indexed-record count/vector dimension, API-key presence as a boolean, and the generation/embedding model names. It never returns a key or calls Gemini.
- Direct local health result: status `ok`; 41 knowledge records; valid index with 41 vectors at dimension 3072; API key configured `true`; generation model `gemini-3.1-flash-lite`; embedding model `gemini-embedding-001`.
- Direct `POST /api/ask` result for `Tell me about Aman`: HTTP 200 with a grounded About answer, intent `about`, and three About source records. Routing, query embedding, retrieval, and generation all completed successfully.
- Vite-proxy `POST /api/ask` result for the same request: HTTP 200 with a grounded answer, intent `about`, and source metadata. The proxy preserved `/api/health` and `/api/ask` paths exactly.
- A single early proxy run returned `gemini_timeout` because the former 12-second provider timeout was too narrow; provider timeout is now 20 seconds and the frontend abort limit is aligned at 25 seconds. The final proxy run succeeded.
- Added safe health/index metadata, local-only frontend diagnostics (status and backend code only), response parsing for structured errors plus `detail`/`message`/non-JSON bodies, and regression coverage for local `.env.local` path loading, same-origin API path, Vite proxy, source badges, and safe text rendering.
- Final validation: 35 Python tests passed; knowledge validator passed; vector-index validator passed; frontend lint passed; production build passed (63 modules). Real credentials were never printed or stored in frontend code.

## Verified project-link handling

- Extended the knowledge schema with optional validated `links` metadata. `project-poetic-pebbles-overview` now contains the verified `poetic-pebbles-play-store` link: `https://play.google.com/store/apps/details?id=com.tech.poeticpebbles`, labelled `Download on Google Play` and typed `play_store`.
- Added `api/link_validation.py` and schema/data-loader/validator checks for stable unique link IDs, non-empty labels, HTTPS URL structure, supported types (`play_store`, `github`, `linkedin`), and approved external domains (`play.google.com`, `github.com`, `linkedin.com`). JavaScript, data, HTTP, malformed, and unapproved-domain URLs are rejected.
- Link-oriented project questions set the router action `external_link`. The RAG service resolves a named project link directly from validated record metadata, returns no Gemini-generated URL, and skips embedding retrieval and generation. Unknown project links return the configured unavailable-link sentence without inventing a URL.
- The API response now includes relevant validated `links`. The React client revalidates returned URLs against the same HTTPS host/type allowlist, and `ChatMessage` renders a responsive Play Store action button with an inline icon, new-tab safety attributes, accessible label, and the visible text `Download on Google Play ↗`. Source badges remain below the response.
- Regenerated and validated `rag_data/vectors.json` after the project record change: 41 synchronized vectors at dimension 3072 using `gemini-embedding-001`.
- Added `tests/test_project_links.py` plus router/frontend regression coverage. Final validation: 41 Python tests passed; knowledge and index validation passed; lint and production build passed (63 modules).

## Next implementation step

Optionally run `python scripts/smoke_ask_aman.py --live` against a locally served endpoint to verify one real grounded answer with the server-side key, then deploy the static site and Vercel Python Function together.
