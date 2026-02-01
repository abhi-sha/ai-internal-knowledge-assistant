# from celery import Celery
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.document import Document
from app.services.document_parser import parse_document
from app.services.text_chunker import chunk_text
from app.services.embedding_service import generate_embeddings
from app.services.vector_store import FaissVectorStore
from app.core.logger import get_logger
from app.models.document_chunk import DocumentChunk
from app.core.celery_app import celery_app
from uuid import UUID

@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=5,
    retry_kwargs={"max_retries": 3},
)
def ingest_document_task(self,document_id:str):

    db:Session=SessionLocal()
    logger=get_logger()
    document = None 

    try:
        # document=db.query(Document).filter(Document.id==document_id).first()
        document_uuid=UUID(document_id)
        document = db.get(Document,document_uuid)
        if not document:
            logger.error("Document not found",extra={"document_id": document_id})
            return

        # 1. mark processing
        document.status="processing"
        db.commit()

        # 2.Extract text from doc 
        extracted_text=parse_document(document.file_path)

        if not extracted_text.strip():
            raise ValueError("Parsed document is empty")
        
        # 3. Chunk text
        chunks=chunk_text(extracted_text)

        embeddings= generate_embeddings(chunks)

        if len(chunks)!=len(embeddings):
            raise ValueError("Embedding generation failed")
        
        for idx,chunk in enumerate(chunks):
            db.add(
                DocumentChunk(
                    document_id=document.id,
                    content=chunk,
                    chunk_index=idx
                )
            )
        db.commit()
        # sleep(2)    #heavy task here

        # Store embeddings in FAISS
        vector_store=FaissVectorStore()
        metadata=[]
        for i in range(len(chunks)):
            metadata.append({"document_id": str(document.id),"chunk_index": i})

        vector_store.add_vectors(embeddings,metadata)
        
        # Mark Completed
        document.status="completed"
        db.commit()
    except Exception as e:
        logger.exception("Document ingestion failed")
        if document:
            # print("Background processing error:", e)
            logger.exception("Background processing error")
            document.status="failed"
            document.error_message=str(e)
            db.commit()
    finally:
        db.close()