from fastapi import APIRouter,Depends,UploadFile,File,HTTPException,status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentOut
from app.auth.security import get_current_user,require_role
from uuid import UUID
router=APIRouter(prefix="/documents",tags=["documents"])

@router.post("",response_model=DocumentOut)
def upload_document(
    file:UploadFile=File(...),
    user:User=Depends(require_role("admin","user")),
    db:Session=Depends(get_db)
):
    doc=Document(filename=file.filename,
                 content_type=file.content_type,
                 uploaded_by=user.id)
    
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return doc

@router.get("",response_model=DocumentOut)
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
    db.refresh()
    