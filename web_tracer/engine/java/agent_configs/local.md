# Agent attach — local (Phase 3, T30)

Run the target Spring application on your workstation and point the OTel Java agent at the
Web Tracer service (`:8100`, OTLP path `/v1/traces`).

```bash
# 1. (one-time) copy the aspect + merge pom-snippet.xml (see java_resources/README.md)

# 2. start the target app with the agent
java -javaagent:/path/to/opentelemetry-javaagent.jar \
     -Dotel.service.name=web-tracer-target \
     -Dotel.exporter.otlp.endpoint=http://127.0.0.1:8100 \
     -Dotel.exporter.otlp.protocol=http/json \
     -Dotel.instrumentation.spring-webmvc.enabled=true \
     -jar target/your-app.jar
```

Channel notes:
- `http/json` works with **no extra dependency** (protobuf optional, T29). If you install
  `protobuf` you may use `http/protobuf`.
- The agent POSTs to `http://127.0.0.1:8100/v1/traces`; the Web Tracer `OtlpReceiver` writes
  `output/runs/<run_id>/java_trace.json`.

Verify:
```bash
curl -s localhost:8100/java/receiver/status      # running=true after /java/receiver/start
curl -s localhost:8100/java/instrumentation/strategies
```
