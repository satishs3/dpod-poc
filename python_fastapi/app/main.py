import docker
import subprocess
from fastapi import FastAPI, status
from pydantic import BaseModel
from typing import Optional
from logger import logger
from middleware import log_requests
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()
app.add_middleware(BaseHTTPMiddleware, dispatch=log_requests)

logger.debug("Starting the application")

class ImageRegistry(BaseModel):
    registry_url: str
    userid: str
    password: str

sign_key = {
    "slotName": "pkcs11:token=openssl_sign_DPOD",
    "slotId": "slot-id=3",
    "id": "id=%70%83%8e%fd%71%63%43%24%6b%cc%36%eb%82%b9%0e%bc%c2%cb%80%8f",
    "object": "object=Cloud-Insights-Docker?module-path=/root/HSM_DPOD/libs/64/libCryptoki2.so",
    "pinValue": "&pin-value=NewCOPass"
}
class Image(BaseModel):
    image_url: str
    sign_key: dict
    requestor: str = None
    team: Optional[str] = None

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/registry/login")
def login_to_registry(registry: ImageRegistry):
    # Login to the registry

    client = docker.from_env()
    try:
        client.login(username=registry.userid, password=registry.password, registry=registry.registry_url)
    except docker.errors.APIError as e:
        return {"message": "Failed to login to registry", "error": str(e)}

    # Call the function
    login_to_registry(registry)
    return {"message": "Login to registry successful"}

@app.post("/sign/image/", status_code=status.HTTP_201_CREATED)
def sign_image(payload: Image):
    print(payload)
    signing_key = sign_key["slotName"] + ';' + sign_key["slotId"] + ';' + sign_key["id"] + ';' + sign_key["object"] + sign_key["pinValue"]
    cosign_command = "cosign sign -key " + signing_key + " " + payload.image_url
    # execute the cosign_command
    try:
        subprocess.run(cosign_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        return {"message": "Failed to sign image", "error": str(e)}
    return {"message": "Image signed successfully",
            "image name": f"signed image {payload.image_url}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0,0,0,0", port=8000)

