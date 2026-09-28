import os
import time
import json
import logging
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://opentelemetry-collector.monitoring.svc.cluster.local:4318")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama.ai.svc.cluster.local:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5-coder:1.5b")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("${{ values.name }}")

resource = Resource.create({"service.name": "${{ values.name }}", "service.version": "1.0.0"})
trace_provider = TracerProvider(resource=resource)
trace_exporter = OTLPSpanExporter(endpoint=f"{OTEL_ENDPOINT}/v1/traces")
trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer("genai.tracer")

app = FastAPI(title="${{ values.name }} API")
FastAPIInstrumentor.instrument_app(app, tracer_provider=trace_provider)

class PromptRequest(BaseModel):
    prompt: str

@app.get("/healthz")
async def health():
    return {"status": "ok", "service": "${{ values.name }}"}

@app.post("/api/v1/generate")
async def generate(req: PromptRequest):
    start_time = time.time()
    with tracer.start_as_current_span(f"chat {MODEL_NAME}") as span:
        span.set_attribute("gen_ai.system", "ollama")
        span.set_attribute("gen_ai.request.model", MODEL_NAME)
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": MODEL_NAME, "prompt": req.prompt, "stream": False}
            )
            data = resp.json()
            return {
                "service": "${{ values.name }}",
                "response": data.get("response", ""),
                "duration_seconds": round(time.time() - start_time, 2)
            }
