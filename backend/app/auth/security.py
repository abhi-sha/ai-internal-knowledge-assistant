from passlib.context import CryptContext

pwd_context=CryptContext(schemes=["argon2"])


def hash_password(password:str) -> str:
    print("PASSWORD SENT IS",password)
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str,hashed_password: str)->bool:
    return pwd_context.verify(plain_password,hashed_password)