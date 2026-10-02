# Agent attach — Docker (Phase 3, T30)

Run the target app in a container and export OTLP to the Web Tracer service on the host (or a
shared docker network). Use `host.docker.internal` to reach `:8100` on the host.

```dockerfile
# Dockerfile snippet — mount the agent, point OTel at the host service
ENTRYPOINT ["java", \
  "-javaagent:/otel/opentelemetry-javaagent.jar", \
  "-Dotel.service.name=web-tracer-target", \
  "-Dotel.exporter.otlp.endpoint=http://host.docker.internal:8100", \
  "-Dotel.exporter.otlp.protocol=http/json", \
  "-Dotel.instrumentation.spring-webmvc.enabled=true", \
  "-jar", "/app/your-app.jar"]
```

```bash
# Build + run (publish nothing extra; OTLP goes out to the host service)
docker build -t web-tracer-target .
docker run --rm --name target \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://host.docker.internal:8100 \
  -v $PWD/opentelemetry-javaagent.jar:/otel/opentelemetry-javaagent.jar \
  web-tracer-target
```

Alternative — shared network:
```bash
docker network create wt
docker run --rm --network wt --name web-tracer -p 8100:8100 web-tracer:latest
docker run --rm --network wt --name target \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://web-tracer:8100 \
  web-tracer-target
```

Channel: `http/json` (no protobuf dependency needed). The agent POSTs to `http://<host>:8100/v1/traces`.
