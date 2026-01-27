import faiss
import os
import pickle
from typing import List
import numpy as np
from app.core.config import VECTOR_DIMENSION,VECTOR_STORE_PATH,METADATA_PATH


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

    
    def add_vectors(self,vectors:List[List[float]],metadatas:List[dict]):
        vectors_np = np.array(vectors).astype("float32")
        self.index.add(vectors_np)
        self.metadata.extend(metadatas)
        self._persist()

    def search(self,query_vector:List[float],top_k=5):
        
        distances,indices=self.index.search([query_vector],top_k)

        results=[]

        for idx in indices[0]:
            if idx==-1:
                continue
            results.append(self.metadata[idx])
        
        return results
    
    def _persist(self):
        faiss.write_index(self.index,VECTOR_STORE_PATH)

        with open(METADATA_PATH,"wb") as f:
            pickle.dump(self.metadata,f)
