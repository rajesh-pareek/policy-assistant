
from contextlib import asynccontextmanager

from fastapi import FastAPI

from policy_assistant.api.dependencies import create_dependencies
from policy_assistant.api.routes.documents import router as documents_router
from policy_assistant.api.routes.chat import router as chat_router
from policy_assistant.core.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    dependencies = create_dependencies()
    app.state.dependencies = dependencies

    yield

    dependencies["vector_store"].save(
        str(dependencies["index_path"])
    )

configure_logging()
app = FastAPI(
    title="Pratham AI Policy Assistant",
    description="AI-powered employee policy assistant using RAG.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(documents_router)
app.include_router(chat_router)



@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "Pratham AI Policy Assistant",
    }
