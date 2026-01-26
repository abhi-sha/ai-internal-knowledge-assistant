from fastapi import APIRouter,Depends,UploadFile,File,HTTPException,status,BackgroundTasks
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

router=APIRouter(prefix="/documents",tags=["documents"])


def process_document_background(document_id:UUID):
    db:Session=SessionLocal()

    try:
        document=db.query(Document).filter(Document.id==document_id).first()

        if not document:
            return
        
        document.status="processing"
        db.commit()

        sleep(2)    #heavy task here

        document.status="completed"
        db.commit()
    except Exception as e:
        document.status="failed"
        document.error_message=str(e)
        db.commit()
    finally:
        db.close()

@router.post("",response_model=DocumentOut)
def upload_document(
    background_tasks:BackgroundTasks,
    file:UploadFile=File(...),
    user:User=Depends(require_role("admin","user")),
    db:Session=Depends(get_db)
):  
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

    background_tasks.add_task(process_document_background,doc.id)
    return doc

@router.get("",response_model=list[DocumentOut])
def list_documents(
    user:User=Depends(get_current_user),
    db:Session=Depends(get_db),
):
    return db.query(Document).all()


@router.delete("/{document_id}",status_code=204)
def delete_document(
    document_id:UUID,
    user:User=Depends(require_role("admin")),
    db:Session=Depends(get_db),
):
    doc=db.query(Document).filter(Document.id==document_id).first()

    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Document not found")
    
    db.delete(doc)
    db.commit()

    return {"status":"File deleted"}
    