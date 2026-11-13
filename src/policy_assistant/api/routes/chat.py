import logging

from fastapi import APIRouter, HTTPException, Request

from policy_assistant.api.schemas.chat import ChatQueryRequest


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/chat",
    tags=["Chat"],
)


@router.post("/query")
def query_policy(request: Request, body: ChatQueryRequest):
    dependencies = request.app.state.dependencies

    try:
        result = dependencies["query_use_case"].execute(
            question=body.question
        )

        logger.info(
            "Policy query processed successfully. Sources: %d",
            len(result.sources),
        )

        return {
            "answer": result.answer,
            "sources": [
                {
                    "document_id": str(source.document_id),
                    "file_name": source.file_name,
                    "version": source.document_version,
                    "page_number": source.page_number,
                }
                for source in result.sources
            ],
        }

    except ValueError as exc:
        logger.warning("Policy query rejected: %s", exc)

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected policy query failure.")

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing your question.",
        ) from exc