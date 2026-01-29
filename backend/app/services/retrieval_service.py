from typing import List
from sqlalchemy.orm import Session

from app.services.embedding_service import generate_embeddings
from app.services.vector_store import FaissVectorStore
from app.models.document_chunk import DocumentChunk
from app.models.document import Document
from app.models.user import User
from app.schemas.retrieval import RetrievedChunk
from uuid import UUID

def retrieve_chunks(
    *,
    db: Session,
    user: User,
    query: str,
    top_k: int
) -> List[RetrievedChunk]:

    # 1. Embed query
    query_embedding = generate_embeddings(query)

    # 2. FAISS similarity search
    faiss=FaissVectorStore()
    faiss_results = faiss.search(query_embedding, top_k)

    results: List[RetrievedChunk] = []

    for meta, score in faiss_results:
        document_id = UUID(meta["document_id"])
        chunk_index = meta["chunk_index"]

        # 3. Fetch document (ACL check)
        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if not document:
            continue

        # Access control
        if user.role != "admin" and document.uploaded_by != user.id:
            continue

        # 4. Fetch chunk
        chunk = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id == document_id,
                DocumentChunk.chunk_index == chunk_index
            )
            .first()
        )

        if not chunk:
            continue

        results.append(
            RetrievedChunk(
                document_id=document_id,
                chunk_index=chunk_index,
                content=chunk.content,
                score=score
            )
        )

    return results