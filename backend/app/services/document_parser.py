from pathlib import Path

def parse_document(file_path:str)->str:

    path=Path(file_path)

    if not path.exists():
        raise FileNotFoundError("Document file not found")
    
    if path.suffix.lower()==".txt":
        return _parse_txt(path)
    

    raise ValueError(f"Unsupported file type:{path.suffix}")

def _parse_txt(path:Path)->str:
    with path.open("r",encoding="utf-8") as f:
        return f.read()