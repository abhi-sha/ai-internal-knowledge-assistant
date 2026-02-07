import faiss
import os
import pickle
from typing import List
import numpy as np
from app.core.config import VECTOR_DIMENSION,VECTOR_STORE_PATH,METADATA_PATH
from fastapi import Request
from app.core.logger import get_logger

class FaissVectorStore:
    def __init__(self):
        self.index=None
        self.metadata=[]

        self._load_or_create()

    def _load_or_create(self):
        if os.path.exists(VECTOR_STORE_PATH):
            self.index=faiss.read_index(VECTOR_STORE_PATH)

            with open(METADATA_PATH,"rb") as f:
                self.metadata=pickle.load(f)
        else:
            self.index=faiss.IndexFlatIP(VECTOR_DIMENSION)
            self.metadata=[]
    
    def add_vectors(
            self,
            vectors:List[List[float]],
            metadatas:List[dict]
            ):
        

        vectors_np = np.array(vectors, dtype="float32")

        start_id = self.index.ntotal
        self.index.add(vectors_np)

        for i, meta in enumerate(metadatas):
            self.metadata.append({
                "vector_id": start_id + i,
                "document_id": meta["document_id"],
                "chunk_index": meta["chunk_index"],
            })

        self._persist()
        

    def search(self,query_vector:List[float],top_k=5):
        
        query_vector=np.array(query_vector).astype("float32")

        query_vector = query_vector.reshape(1, -1)

        scores, indices = self.index.search(query_vector, top_k)

        results = []

        for rank, idx in enumerate(indices[0]):
            if idx == -1:
                continue
            results.append((self.metadata[idx], scores[0][rank]))
        
        return results
    
    def delete_document(self,document_id:str,request_id:str):

        if self.index.ntotal==0:
            return 
        
        keep_embeddings=[]
        keep_metadata=[]
        
        logger=get_logger(
        request_id=request_id
       
    )
        before=self.index.ntotal
        
        logger.info( "FAISS delete started",
                    extra={
                        "document_id":document_id,
                        "vectors_before":before
                    })

        for i,meta in enumerate(self.metadata):
            if meta["document_id"]!=document_id:
                keep_embeddings.append(self.index.reconstruct(i))
                keep_metadata.append(meta)

        if not keep_embeddings:
            self.index=faiss.IndexFlatIP(VECTOR_DIMENSION)  
            self.metadata=[]
            self._persist()
            return

        new_index=faiss.IndexFlatIP(VECTOR_DIMENSION)
        new_index.add(np.array(keep_embeddings,dtype="float32"))

        for idx,meta in enumerate(keep_metadata):
            meta["vector_id"]=idx

        self.index=new_index
        self.metadata=keep_metadata

      

        self._persist()
        after=self.index.ntotal
        logger.info( "FAISS delete completed",
                    extra={
                        "document_id":document_id,
                        "vectors_after":before-after
                    })


    def health(self)->dict:
         return {
            "faiss_vectors": self.index.ntotal,
            "metadata_entries": len(self.metadata),
            "consistent": self.index.ntotal == len(self.metadata),
        }

    def _persist(self):
        faiss.write_index(self.index,VECTOR_STORE_PATH)

        with open(METADATA_PATH,"wb") as f:
            pickle.dump(self.metadata,f)

