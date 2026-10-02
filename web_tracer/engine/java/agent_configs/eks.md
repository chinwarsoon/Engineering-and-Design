# Agent attach — EKS / Kubernetes (Phase 3, T30)

Inject the OTel Java agent as a sidecar-mountable JAR and export OTLP to the Web Tracer service
reachable inside the cluster. Approval from the ops team may be required for the `-javaagent`
flag (workplan §10.3 potential issue).

```yaml
# deployment.yaml — add the agent as an init container copy + env vars
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-tracer-target
spec:
  template:
    spec:
      initContainers:
        - name: otel-agent
          image: otel/opentelemetry-javaagent:latest
          command: ["cp", "/javaagent.jar", "/otel/opentelemetry-javaagent.jar"]
          volumeMounts:
            - { name: otel, mountPath: /otel }
      containers:
        - name: app
          image: your-registry/your-app:latest
          env:
            - { name: JAVA_TOOL_OPTIONS, value: "-javaagent:/otel/opentelemetry-javaagent.jar" }
            - { name: OTEL_SERVICE_NAME, value: "web-tracer-target" }
            - { name: OTEL_EXPORTER_OTLP_ENDPOINT, value: "http://web-tracer.web-tracer.svc:8100" }
            - { name: OTEL_EXPORTER_OTLP_PROTOCOL, value: "http/json" }
            - { name: OTEL_INSTRUMENTATION_SPRING_WEBMVC_ENABLED, value: "true" }
          volumeMounts:
            - { name: otel, mountPath: /otel }
      volumes:
        - name: otel
          emptyDir: {}
```

Notes:
- `OTEL_EXPORTER_OTLP_ENDPOINT` uses the in-cluster Web Tracer service DNS (`web-tracer.web-tracer.svc:8100`).
- `http/json` avoids the optional protobuf dependency (T29). Switch to `http/protobuf` only after
  installing `protobuf` in the runtime image.
- The agent exports to `http://<svc>:8100/v1/traces`; spans are written to
  `output/runs/<run_id>/java_trace.json` on the Web Tracer pod.
- If the business backend runs a separate CORS preflight, add `java_resources/CorsConfig.java` so
  `traceparent` is allowed (T33) and the correlation link is not downgraded.
