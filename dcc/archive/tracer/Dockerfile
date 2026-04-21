FROM python:3.11-slim
WORKDIR /tracer
COPY . .
RUN pip install --no-cache-dir fastapi uvicorn networkx
EXPOSE 8000 5000
ENV TRACER_TARGET=/target
ENTRYPOINT ["python", "launch.py", "/target", "--no-browser"]
