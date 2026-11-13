import logging
from pathlib import Path
from uuid import uuid4, UUID

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from policy_assistant.domain.entities.document import Document

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/upload")
def upload_document(
    request: Request,
    file: UploadFile = File(...),
):
    try:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="A filename is required.",
            )

        # Normalize Windows and Unix path separators.
        original_file_name = Path(
            file.filename.replace("\\", "/")
        ).name

        # Remove non-printable characters.
        clean_file_name = "".join(
            character
            for character in original_file_name
            if character.isprintable()
        ).strip()

        if not clean_file_name:
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF filename.",
            )

        if Path(clean_file_name).suffix.lower() != ".pdf":
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported.",
            )

        # Read at most 10 MB + 1 byte.
        file_content = file.file.read(MAX_FILE_SIZE + 1)

        if not file_content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="PDF file exceeds the 10 MB limit.",
            )

        clean_file_name = (
            f"{Path(clean_file_name).stem[:250]}.pdf"
        )

        dependencies = request.app.state.dependencies

        document_id = uuid4()
        stored_file_path = (
            dependencies["upload_dir"] / f"{document_id}.pdf"
        )

        try:
            stored_file_path.write_bytes(file_content)

            document = Document(
                id=document_id,
                file_name=clean_file_name,
            )

            dependencies["ingest_use_case"].execute(
                document=document,
                file_path=str(stored_file_path),
            )

            dependencies["vector_store"].save(
                str(dependencies["index_path"])
            )

            logger.info(
                "Document uploaded and indexed successfully. Document ID: %s",
                document.id,
            )

            return {
                "message": "PDF uploaded and indexed successfully.",
                "document_id": str(document.id),
                "file_name": document.file_name,
                "version": document.version,
                "status": document.status,
                "uploaded_at": document.uploaded_at.isoformat(),
            }

        except ValueError as exc:
            logger.warning("Document ingestion rejected: %s", exc)
            stored_file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            ) from exc

        except Exception as exc:
            logger.exception("Unexpected document ingestion failure.")
            stored_file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=500,
                detail="Document ingestion failed.",
            ) from exc

    finally:
        file.file.close()


@router.get("")
def list_documents(request: Request):
    dependencies = request.app.state.dependencies

    documents = dependencies["document_repository"].get_all()

    return {
        "total": len(documents),
        "documents": [
            {
                "document_id": str(document.id),
                "file_name": document.file_name,
                "version": document.version,
                "status": document.status,
                "uploaded_at": document.uploaded_at.isoformat(),
            }
            for document in documents
        ],
    }


@router.delete("/{document_id}")
def delete_document(
    document_id: UUID,
    request: Request,
):
    dependencies = request.app.state.dependencies

    try:
        deleted = dependencies["delete_use_case"].execute(
            document_id=document_id
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

        # Persist the updated FAISS index immediately.
        dependencies["vector_store"].save(
            str(dependencies["index_path"])
        )

        # Remove the locally stored PDF.
        stored_file_path = (
            dependencies["upload_dir"] / f"{document_id}.pdf"
        )
        stored_file_path.unlink(missing_ok=True)

        return {
            "message": "Document deleted successfully.",
            "document_id": str(document_id),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Document deletion failed.",
        ) from exc
