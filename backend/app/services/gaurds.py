from fastapi import HTTPException,status


MAX_QUERY_LENGTH=500
MAX_FILE_SIZE_MB=10
ALLOWED_CONTENT_TYPES={
    "text/plain"
}
MAX_CONTEXT_CHUNKS = 5


def validate_query(query:str):

    if not query or  not query.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Query can not be empty")
    

    if len(query)>MAX_QUERY_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Query too long (max {MAX_QUERY_LENGTH}chars)"
        )

def validate_file_size(file):
    file.file.seek(0,2)
    size=file.file.tell()
    file.file.seek(0)


    if size>MAX_FILE_SIZE_MB*1024*1024:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"File too large (max({MAX_FILE_SIZE_MB})MB)"
        )


def validate_content_type(content_type:str):

    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type"
        )
    
def validate_context_size(chunks):
    if len(chunks) > MAX_CONTEXT_CHUNKS:
        return chunks[:MAX_CONTEXT_CHUNKS]
    return chunks