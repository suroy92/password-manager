from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

def create_app():
    app = FastAPI(title="Password Manager API")

    @app.get("/api/health")
    def health():
        return {"ok": True}

    ui_dist = Path(__file__).resolve().parents[2] / "ui" / "dist"
    if ui_dist.exists():
        app.mount("/", StaticFiles(directory=str(ui_dist), html=True), name="ui")
    else:
        @app.get("/")
        def not_built():
            return JSONResponse({"message": "UI not built. Run: cd ui && npm install && npm run build"}, 200)

    return app

app = create_app()

# mount stub routes
from .routes_stub import router as _stub
app.include_router(_stub, prefix='/api')
