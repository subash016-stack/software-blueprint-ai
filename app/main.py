import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.schemas import GenerateRequest, GenerateResponse
from app.graph import run_blueprint_generation
from app.llm import get_settings

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
    logger.info("Initializing Software Blueprint AI API...")
    logger.info("Target Ollama Base URL: %s", settings.ollama_base_url)
    logger.info("Target Ollama Model: %s", settings.ollama_model)
    yield
    logger.info("Shutting down Software Blueprint AI API.")


app = FastAPI(
    title="AI-Driven Software Engineering Blueprint Generator",
    description=(
        "Research prototype that converts natural-language project ideas into structured "
        "Software Requirements Specifications (Module 1) and actionable Project Plans (Module 2)."
    ),
    version="1.0.0",
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

# Mount static assets
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get(
    "/",
    tags=["Frontend"],
    summary="Interactive Web UI",
    include_in_schema=False
)
async def serve_frontend():
    """Serve the interactive web frontend dashboard."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend index.html not found. Please check app/static/ directory."}


@app.get(
    "/health",
    tags=["System"],
    summary="Service Health Check",
    response_description="Returns system operational status."
)
async def health_check():
    """Verify service availability."""
    return {"status": "ok"}



@app.post(
    "/generate",
    response_model=GenerateResponse,
    status_code=status.HTTP_200_OK,
    tags=["Blueprint Generation"],
    summary="Generate Software Blueprint",
    response_description="Structured SRS and Engineering Project Plan."
)
async def generate_blueprint(request: GenerateRequest):
    """Convert a natural-language project idea into a complete Software Blueprint.
    
    Executes:
    1. **Module 1 (Requirement Analysis Agent)**: Stakeholders, Functional Requirements (FR),
       Non-Functional Requirements (NFR), Constraints, Ambiguities, and Assumptions.
    2. **Module 2 (Project Planning Agent)**: Cohesive Modules, Work Breakdown Tasks,
       Dependency Scheduling, Milestones, and an Ordered Roadmap.
    """
    idea = request.project_idea.strip()
    if not idea or len(idea) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The project idea must be a non-empty string of at least 5 characters."
        )

    logger.info("Processing blueprint generation request for idea: %s", idea[:60])

    try:
        result_state = run_blueprint_generation(idea)
        
        # Check for pipeline errors
        errors = result_state.get("errors", [])
        if errors and not result_state.get("requirements"):
            logger.error("Pipeline failure in Requirement Agent: %s", errors)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Requirement analysis failed: {'; '.join(errors)}"
            )

        if errors and not result_state.get("project_plan"):
            logger.error("Pipeline failure in Planning Agent: %s", errors)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Project planning failed: {'; '.join(errors)}"
            )

        requirements = result_state.get("requirements")
        project_plan = result_state.get("project_plan")

        if not requirements or not project_plan:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Incomplete blueprint generation. One or more modules produced empty outputs."
            )

        return GenerateResponse(
            requirements=requirements,
            project_plan=project_plan
        )

    except HTTPException:
        raise
    except ConnectionError as ce:
        logger.error("Ollama connection error: %s", ce)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to connect to local Ollama instance. Ensure Ollama is running at the configured URL."
        )
    except Exception as e:
        logger.error("Unexpected error during blueprint generation: %s", e, exc_info=True)
        # Avoid leaking raw internal stack traces to the API client
        error_msg = str(e)
        if "Failed to connect" in error_msg or "Connection refused" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to reach Ollama LLM service. Please verify that Ollama is active."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blueprint generation failed: {error_msg}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
