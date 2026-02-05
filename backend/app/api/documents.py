from fastapi import APIRouter,Depends,UploadFile,File,HTTPException,status,BackgroundTasks,Request
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentOut
from app.auth.security import get_current_user,require_role
from uuid import UUID
from app.core.config import DOCUMENTS_DIR
import uuid

from time import sleep
from app.db.session import SessionLocal
from app.services.document_parser import parse_document
from app.services.text_chunker import chunk_text
from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import generate_embeddings
from app.services.vector_store import FaissVectorStore
from app.tasks.document_ingestion import ingest_document_task
from fastapi import Request
from app.core.logger import get_logger
from app.core.rate_limiter import limiter
from app.services.gaurds import validate_file_size,validate_content_type

router=APIRouter(prefix="/documents",tags=["documents"])


# def process_document_background(document_id:UUID):
#     db:Session=SessionLocal()

#     try:
#         document=db.query(Document).filter(Document.id==document_id).first()

#         if not document:
#             return

#         # 1. mark processing
#         document.status="processing"
#         db.commit()

#         # 2.Extract text from doc 
#         extracted_text=parse_document(document.file_path)

#         if not extracted_text.strip():
#             raise ValueError("Parsed document is empty")
        
#         # 3. Chunk text
#         chunks=chunk_text(extracted_text)

#         embeddings= generate_embeddings(chunks)

#         if len(chunks)!=len(embeddings):
#             raise ValueError("Embedding generation failed")
        
#         for idx,chunk in enumerate(chunks):
#             db.add(
#                 DocumentChunk(
#                     document_id=document.id,
#                     content=chunk,
#                     chunk_index=idx
#                 )
#             )
#         db.commit()
#         # sleep(2)    #heavy task here

#         # Store embeddings in FAISS
#         vector_store=FaissVectorStore()
#         metadata=[]
#         for i in range(len(chunks)):
#             metadata.append({"document_id": str(document.id),"chunk_index": i})

#         vector_store.add_vectors(embeddings,metadata)
        
#         # Mark Completed
#         document.status="completed"
#         db.commit()
#     except Exception as e:
#         print("Background processing error:", e)
#         document.status="failed"
#         document.error_message=str(e)
#         db.commit()
#     finally:
#         db.close()

@router.post("",response_model=DocumentOut)
@limiter.limit("10/minute")
def upload_document(
    request:Request,
    background_tasks:BackgroundTasks,
    file:UploadFile=File(...),
    user:User=Depends(require_role("admin","user")),
    db:Session=Depends(get_db)
):  
    

    validate_file_size(file)
    validate_content_type(file.content_type)

    file_id=uuid.uuid4()
    file_extension=Path(file.filename).suffix
    stored_filename=f"{file_id}{file_extension}"
    file_path=DOCUMENTS_DIR/stored_filename

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file,buffer)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file"
        )
    
    doc=Document(filename=file.filename,
                 content_type=file.content_type,
                 file_path=str(file_path),
                 status="uploded",
                 uploaded_by=user.id)
    
    db.add(doc)
    db.commit()
    db.refresh(doc)

    ingest_document_task.delay(str(doc.id))
    # background_tasks.add_task(process_document_background,doc.id)
    return doc

@router.get("",response_model=list[DocumentOut])
def list_documents(
    user:User=Depends(get_current_user),
    db:Session=Depends(get_db),
):
    return (
        db.query(Document).order_by(Document.created_at.desc())
        .all()
    )

@router.get("/{document_id}",response_model=DocumentOut)
def get_document(
    document_id:UUID,
    user:User=Depends(get_current_user),
    db:Session=Depends(get_db),
):
    doc=db.query(Document).filter(Document.id==document_id).first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return doc
    
@router.delete("/{document_id}",status_code=204)
def delete_document(
    document_id:UUID,
    request:Request,
    user:User=Depends(require_role("admin")),
    db:Session=Depends(get_db),
):
    
    doc=db.query(Document).filter(Document.id==document_id).first()

    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Document not found")
    
    vector_store=FaissVectorStore()
    logger=get_logger(request_id=request.state.request_id)

    try:

        vector_store.delete_document(str(document_id),request_id=request.state.request_id)


        file_path=Path(doc.file_path)
        if file_path.exists():
            file_path.unlink()

        db.delete(doc)
        db.commit()

    except Exception as e:
        db.rollback()
        logger.exception("FAILED TO DELETE DOCUMENT",
                         extra={"document_id":str(document_id)})

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file from disk"
        )
        
   
    return {"status":"File deleted"}
    