from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import papermill as pm
import json, os, uuid

app = FastAPI()

BASE = os.path.dirname(os.path.abspath(__file__))
NOTEBOOK = os.path.join(BASE, "Redes_N8N.ipynb")

class Params(BaseModel):
    tickers: list[str]          # llega del formulario, vía n8n
    ub: float = 0.01            # opcional; usa el default si n8n no lo manda
    us: float = -0.01

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ejecutar")
def ejecutar(params: Params):
    run_id = str(uuid.uuid4())[:8]
    out_dir = os.path.join(BASE, "runs", run_id)
    os.makedirs(out_dir, exist_ok=True)
    out_nb = os.path.join(out_dir, "ejecutado.ipynb")

    try:
        pm.execute_notebook(
            NOTEBOOK, out_nb, cwd=out_dir,
            parameters={
                "TICKERS": params.tickers,
                "ub": params.ub,
                "us": params.us,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando el notebook: {e}")

    resultados_path = os.path.join(out_dir, "resultados.json")
    if not os.path.exists(resultados_path):
        raise HTTPException(status_code=500, detail="El notebook no generó resultados.json")

    with open(resultados_path, encoding="utf-8") as f:
        resultados = json.load(f)

    return {"run_id": run_id, "status": "ok", "resultados": resultados}