# Java runtime resources (Phase 3 — T33)

These templates let a target Java/Spring application emit **method-level** spans and keep the
W3C `traceparent` header across the CORS preflight, so the browser click and the backend write
land in the **same tree**.

## What each file does

| File | Purpose |
|------|---------|
| `TracedAspect.java` | One Spring AOP `@Around` advice wrapping every Controller/Service/Repository. No business-code edits; produces **nested** spans. Carries `code.namespace` / `code.function`. |
| `pom-snippet.xml` | AOP + AspectJ weaver + OTel API dependencies to add to the target `pom.xml`. |
| `CorsConfig.java` | Permits `traceparent` / `tracestate` on the CORS preflight so the trace link survives. |

## CORS detection (backend side)

The Web Tracer backend already sets `allow_headers = "*"`, so for **our own** target the CORS
downgrade never triggers. The browser-side `probe_cors` (`engine/browser/traceparent.py`) reports
`allowed=True` in that case. For a *separate* business backend, drop in `CorsConfig.java` (or set
`Access-Control-Allow-Headers: traceparent` on its preflight) so `probe_cors` returns `allowed=True`
instead of forcing the URL + time-window fallback.

## Usage

1. Copy `TracedAspect.java` into the target project (`com.webtracer.instrument`).
2. Merge `pom-snippet.xml` into `pom.xml`.
3. Start the app with the OTel agent pointing at this service's OTLP endpoint (see
   `../agent_configs/*.md`).
4. The agent exports to `POST /v1/traces` on the Web Tracer service; spans land in
   `output/runs/<run_id>/java_trace.json`.
