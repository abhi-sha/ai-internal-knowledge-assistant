from sentence_transformers import SentenceTransformer
from typing import List

model=SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(texts:List[str])->List[list[float]]:


    embeddings=model.encode(        
        # size if 384 
        # if let's say text had 2 chunks then output
        #  would be of size (2,384)
        texts,
        convert_to_numpy=True
    )


    return embeddings.tolist()
