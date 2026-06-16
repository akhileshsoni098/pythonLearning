from fastapi import APIRouter, HTTPException, status
from app.models.user_auth_model import LoginModel, RegisterModel
from app.db.db_query import query
from app.utils.hash import hash_password, verify_password
from app.utils.jwt import create_access_token

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterModel):
    try:
        check = query(
            "SELECT 1 FROM users WHERE email = %s", (data.email,), fetchone=True
        )

        print("check:", check)

        if check:
            raise HTTPException(status_code=400, detail="Email already exists")

        hashed_password = hash_password(data.password)

        query(
            """
        INSERT INTO users (email, password_hash, role, is_active)
        VALUES (%s, %s, %s, %s)
        """,
            (data.email, hashed_password, data.role, data.is_active),
        )

        return {"message": "User registered successfully"}

    except HTTPException:
        raise

    except Exception as e:
        import traceback
        traceback.print_exc()
        print("REGISTER ERROR:", e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login", status_code=status.HTTP_200_OK)
def login(data: LoginModel):
    try:
        user = query(
            "SELECT * FROM users WHERE email = %s", (data.email,), fetchone=True
        )

        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        user_id, email, password_hash, role, is_active, created_at = user

        if not verify_password(data.password, password_hash):
            raise HTTPException(status_code=400, detail="Invalid password")

        token = create_access_token({"user_id": user_id, "email": email})

        return {
            "message": "Login successful",
            "access_token": token,
            "token_type": "bearer",
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("LOGIN ERROR:", e)
        raise HTTPException(status_code=500, detail="Internal server error")
