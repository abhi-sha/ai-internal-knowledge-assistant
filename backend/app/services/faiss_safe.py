import concurrent.futures
from typing import List,Tuple


FAISS_TIMEOUT_SECONDS=4

def faiss_search_with_timeout(
        vector_store,
        query_vector,
        top_k:int
)->List[Tuple[dict,float]]:
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:

        future=executor.submit(
            vector_store.search,
            query_vector,
            top_k
        )

        try:
            return future.result(timeout=FAISS_TIMEOUT_SECONDS)
        except concurrent.futures.TimeoutError:
            return []
