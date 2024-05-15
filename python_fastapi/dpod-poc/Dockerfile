# 
FROM python:3.9

# 
WORKDIR /dpod

# 
COPY ./requirements.txt /dpod/requirements.txt

COPY ./startup-uvicorn.sh /dpod/startup-uvicorn.sh

# 
RUN pip install --no-cache-dir --upgrade -r /dpod/requirements.txt

# 
COPY ./app /dpod/app

# 
ENTRYPOINT ["/bin/sh", "./startup-uvicorn.sh"]
