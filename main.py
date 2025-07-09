from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="FastAPI 기본 애플리케이션",
    description="FastAPI로 만든 기본 API 서버",
    version="1.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic 모델 정의
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True

# 메모리 기반 데이터 저장소 (실제 프로젝트에서는 데이터베이스를 사용하세요)
items_db = []
item_id_counter = 1

# 루트 엔드포인트
@app.get("/")
async def root():
    return {"message": "FastAPI 기본 애플리케이션에 오신 것을 환영합니다!"}

# 헬스체크 엔드포인트
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "서버가 정상적으로 작동 중입니다"}

# 모든 아이템 조회
@app.get("/items", response_model=List[Item])
async def get_items():
    return items_db

# 특정 아이템 조회
@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다")

# 새 아이템 생성
@app.post("/items", response_model=Item)
async def create_item(item: ItemCreate):
    global item_id_counter
    new_item = Item(
        id=item_id_counter,
        name=item.name,
        description=item.description,
        price=item.price,
        is_available=item.is_available
    )
    items_db.append(new_item)
    item_id_counter += 1
    return new_item

# 아이템 업데이트
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemCreate):
    for i, existing_item in enumerate(items_db):
        if existing_item.id == item_id:
            updated_item = Item(
                id=item_id,
                name=item.name,
                description=item.description,
                price=item.price,
                is_available=item.is_available
            )
            items_db[i] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다")

# 아이템 삭제
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    for i, item in enumerate(items_db):
        if item.id == item_id:
            deleted_item = items_db.pop(i)
            return {"message": f"아이템 '{deleted_item.name}'이 삭제되었습니다"}
    raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다")

# 사용자 정보 엔드포인트
@app.get("/users/me")
async def read_user_me():
    return {"username": "현재 사용자", "email": "user@example.com"}

# 경로 매개변수 예제
@app.get("/users/{user_id}")
async def read_user(user_id: int):
    return {"user_id": user_id, "username": f"사용자{user_id}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 