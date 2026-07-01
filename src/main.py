from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Gauge, Histogram
from src.schemas import ShortenRequest, ShortenResponse
from src.store import LinkStore
import time
 
app = FastAPI(title="MiniLink", version="0.1.0")
store = LinkStore()
BASE_URL = "http://localhost:8000"
 
# Metriques metier MiniLink
links_created_total = Counter(
    "minilink_links_created_total",
    "Nombre total de liens crees",
    ["status"]
)
redirects_total = Counter(
    "minilink_redirects_total",
    "Nombre total de resolutions de code",
    ["status"]
)
store_size = Gauge(
    "minilink_store_size",
    "Nombre de liens actuellement stockes"
)
shorten_duration = Histogram(
    "minilink_shorten_duration_seconds",
    "Duree de creation d'un lien court en secondes",
    buckets=[0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0]
)
 
# Instrumentation automatique HTTP (expose GET /metrics)
Instrumentator().instrument(app).expose(app)
 
 
@app.get("/health")
def health():
    return {"status": "ok"}
 
 
@app.post("/shorten", response_model=ShortenResponse)
def shorten(request: ShortenRequest):
    start = time.time()
    try:
        url = str(request.url)
        code = store.create(url)
        shorten_duration.observe(time.time() - start)
        links_created_total.labels(status="ok").inc()
        store_size.set(store.size())
        return {"code": code,
                "short_url": f"{BASE_URL}/{code}",
                "original_url": url}
    except Exception:
        links_created_total.labels(status="error").inc()
        raise
 
 
@app.get("/resolve/{code}")
def resolve(code: str):
    url = store.resolve(code)
    if url is None:
        redirects_total.labels(status="not_found").inc()
        raise HTTPException(status_code=404, detail="Code inconnu")
    redirects_total.labels(status="ok").inc()
    return {"code": code, "original_url": url}
