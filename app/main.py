"""Main FastAPI Application entry point for Software Blueprint AI."""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.schemas import GenerateRequest, GenerateResponse, CompleteBlueprint
from app.graph import run_blueprint_generation
from app.config import get_settings
from app.api.routes import router as api_router
from app.rag.retriever import load_and_ingest_knowledge_base
from app.services.project_service import save_complete_blueprint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("software-blueprint-ai")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    settings = get_settings()
    logger.info("Initializing Software Blueprint AI (Modules 1-6)...")
    logger.info("Target Ollama URL: %s | Model: %s", settings.ollama_base_url, settings.generation_model)
    
    # Pre-index academic knowledge base
    try:
        total_chunks = load_and_ingest_knowledge_base()
        logger.info("Indexed %d knowledge base chunks for RAG.", total_chunks)
    except Exception as e:
        logger.warning("Knowledge base initialization warning: %s", e)

    yield
    logger.info("Shutting down Software Blueprint AI.")


app = FastAPI(
    title="AI-Driven Software Engineering Blueprint Generator",
    description=(
        "Full-Lifecycle Research Prototype converting natural-language ideas into structured, "
        "evidence-grounded, validated, and traceable software engineering blueprints with change impact analysis."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# Allow CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API Routes
app.include_router(api_router, prefix="/api/v1")
app.include_router(api_router)  # Also mount at root level for /projects, /metrics, etc.

# Mount static assets
if os.path.exists(STATIC_DIR):
    assets_dir = os.path.join(STATIC_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get(
    "/",
    tags=["Frontend"],
    summary="Interactive Web UI Dashboard",
    include_in_schema=False
)
async def serve_frontend():
    """Serve the interactive web frontend dashboard."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend index.html not found in app/static/."}


@app.get("/vite.svg", include_in_schema=False)
async def serve_favicon():
    """Serve the application icon."""
    svg_path = os.path.join(STATIC_DIR, "vite.svg")
    if os.path.exists(svg_path):
        return FileResponse(svg_path, media_type="image/svg+xml")
    return {"status": "not found"}


@app.get(
    "/health",
    tags=["System"],
    summary="Service Health Check",
    response_description="Returns system operational status."
)
async def health_check():
    """Verify service availability and dependency status."""
    settings = get_settings()
    return {
        "status": "ok",
        "model": settings.generation_model,
        "embedding_model": settings.embedding_model,
        "version": "2.0.0"
    }


@app.post(
    "/generate",
    response_model=GenerateResponse,
    status_code=status.HTTP_200_OK,
    tags=["Blueprint Generation"],
    summary="Generate Software Blueprint (Legacy & Standalone)",
    response_description="Structured SRS, Project Plan, and Architecture."
)
def generate_blueprint(request: GenerateRequest):
    """Convert a natural-language project idea into a complete Software Blueprint."""
    idea = request.project_idea.strip()
    if not idea or len(idea) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The project idea must be a non-empty string of at least 5 characters."
        )

    logger.info("Processing blueprint generation request for idea: %s", idea[:60])

    try:
        result_state = run_blueprint_generation(idea)
        
        errors = result_state.get("errors", [])
        if errors and not result_state.get("requirements"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Requirement analysis failed: {'; '.join(errors)}"
            )

        requirements = result_state.get("requirements")
        project_plan = result_state.get("project_plan")
        architecture = result_state.get("architecture")
        rag = result_state.get("rag_recommendations")
        val = result_state.get("validation_report")

        if not requirements or not project_plan:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Incomplete blueprint generation."
            )

        # Save to projects store
        bp = CompleteBlueprint(
            project_id="proj-default",
            project_name=request.project_name or requirements.project_name,
            version=1,
            requirements=requirements,
            project_plan=project_plan,
            architecture=architecture,
            rag_recommendations=rag or [],
            validation_report=val,
            version_history=[]
        )
        save_complete_blueprint(bp)

        return GenerateResponse(
            requirements=requirements,
            project_plan=project_plan,
            architecture=architecture,
            rag_recommendations=rag,
            validation_report=val,
            version=1
        )

    except HTTPException:
        raise
    except ConnectionError as ce:
        logger.error("Ollama connection error: %s", ce)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to connect to local Ollama instance. Ensure Ollama is running at http://localhost:11434."
        )
    except Exception as e:
        logger.error("Unexpected error during blueprint generation: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blueprint generation failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
