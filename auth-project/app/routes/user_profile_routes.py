from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.db.db_query import query
from app.middleware.auth_deps import authentication
from app.models.user_profile_model import profileModel

router = APIRouter()


@router.post("/profile", status_code=status.HTTP_201_CREATED)
def profile_create(data: profileModel, req: Request, _: dict = Depends(authentication)):
    try:
        user = req.state.user
        if not user.get("user_id") or not user.get("email"):
            raise HTTPException(status_code=400, detail="User not found")

        exists = query(
            "SELECT 1 FROM user_profiles WHERE user_id = %s",
            (user["user_id"],),
            fetchone=True,
        )

        if exists:
            # update profile data
            query(
                "UPDATE user_profiles SET name = %s, gender = %s, phone = %s WHERE user_id = %s",
                (data.name, data.gender, data.phone, user["user_id"]),
            )
            return {"message": "Profile updated successfully"}

            # create new profile

        query(
            "INSERT INTO user_profiles (user_id, name, gender, phone) VALUES (%s, %s, %s, %s)",
            (user["user_id"], data.name, data.gender, data.phone),
        )

        print("user:", user)
        return {"message": "Profile created successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile")
def profile_get(request: Request, _: dict = Depends(authentication)):
    try:

        user = request.state.user

        if not user.get("user_id") or not user.get("email"):
            raise HTTPException(status_code=400, detail="User not found")

        profile = query(
            "SELECT * FROM user_profiles WHERE user_id = %s",
            (user["user_id"],),
            fetchone=True,
            as_dict=True,
        )

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        return {"data": profile}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


