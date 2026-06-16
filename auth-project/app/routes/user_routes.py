from fastapi import APIRouter

router = APIRouter()


@router.get("/users/{id}")
def get_users(id: int):
    return {"user_id": id}


@router.get("/items")
def get_items(page: int, limit: int):
    return {"page": page, "limit": limit}


@router.post("/user/{id}")
def update_user(id: int, data: dict, active: bool = True):
    return {"id": id, "data": data, "active": active, "message": "updated successfully"}
