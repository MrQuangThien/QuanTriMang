from fastapi import Header, HTTPException
import os

def require_api_key(x_api_key: str | None = Header(default=None)):
    expected = os.getenv("API_KEY")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="API key không hợp lệ")
    return True
