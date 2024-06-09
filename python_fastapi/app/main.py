import os
import subprocess
from app.lib.conjurClient import ConjurClient
from app.middleware import log_requests
from fastapi import FastAPI, status
from logger import logger
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()
app.add_middleware(BaseHTTPMiddleware, dispatch=log_requests)

logger.debug("Starting the application")

class toSign(BaseModel):
    image_url: str
    key_label: str

class toVerify(BaseModel):
    image_url: str
    key_label: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/sign/image/", status_code=status.HTTP_201_CREATED)
def sign_image(payload: toSign):
    conjur_client = ConjurClient()
    secret = conjur_client.get_secret(payload.key_label)
    if secret is None:
        return {"message": "secret could not be retrieved conjur"}
    input_cmd_list = []
    script_command = f"python3 /dpod/app/sign_image.py {payload.image_url} {secret}"
    input_cmd_list.append(script_command)
    try:
        process = subprocess.check_output(
                  input_cmd_list,
                  shell=True,
                  timeout=60
            )
    except subprocess.CalledProcessError as e:
        return {"message": "error while handling the request", "error": str(e)}
    return {"message": "image signing response", "output": f"{process.decode('utf-8')}"}

@app.post("/verify/image/", status_code=status.HTTP_201_CREATED)
def verify_image(payload: toVerify):
    filename = f"/dpod/app/{payload.key_label}.pub"
    if os.path.exists(filename) == False:
        conjur_client = ConjurClient()
        secret = conjur_client.get_secret(payload.key_label)
        # write the secret to a file
        if secret is None:
            return {"message": "secret could not be retrieved conjur"}
        secret = str(secret).replace("\\n", "\n").strip()
        with open(filename, "w") as f:
            f.write(secret)
    input_cmd_list = []
    script_command = f"python3 /dpod/app/verify_image.py {payload.image_url} {filename}"
    input_cmd_list.append(script_command)
    try:
        process = subprocess.check_output(
                  input_cmd_list,
                  shell=True,
                  timeout=60
            )
    except subprocess.CalledProcessError as e:
        return {"message": "error while handling the request", "error": str(e)}
    return {"message": "image signature verification response", "output": f"{process.decode('utf-8')}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0,0,0,0", port=8000,reload=True)
