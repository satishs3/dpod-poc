from fastapi import FastAPI, status, HTTPException, Response
from pydantic import BaseModel
from typing import Optional


app = FastAPI()

class Image(BaseModel):
    image_url: str
    sign_key: str
    requestor: str = None
    team: Optional[str] = None

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/sign/image/", status_code=status.HTTP_201_CREATED)
def sign_image(payload: Image):
    print(payload)
    #return Response(status_code=status.HTTP_201_CREATED)
    return {"message": "Image signed successfully",
            "image name": f"signed image {payload.image_url}"}

@app.get("/image/{image_id}")
def read_image(image_id: int, q: Optional[str] = None):
    if image_id == 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return {"image_id": image_id, "q": q}
