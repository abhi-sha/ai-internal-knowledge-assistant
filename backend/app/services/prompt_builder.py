from typing import List
from app.schemas.retrieval import RetrievedChunk


def build_prompt(
        query:str,
        chunks:List[RetrievedChunk]
)->str:
    context="\n\n".join(
        f"[Doc {c.document_id} | {c.chunk_index}]\n{c.content}"
        for c in chunks
    )


    prompt=f"""
You are an internal enterprise knowledge assistant.
Answer ONLY using the provided context.
If the answer is not in the context, say: "I don't know."

Context:
{context}

Question:
{query}

Answer:
""".strip()
    
    return prompt