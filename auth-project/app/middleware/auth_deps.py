from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.utils.jwt import verify_token

security = HTTPBearer()


def authentication(
    credentials: HTTPAuthorizationCredentials = Depends(security), req: Request = None
):
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expaired token"
        )
    req.state.user = payload
    return payload
