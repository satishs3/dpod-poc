# 
FROM python:3.9

# 
WORKDIR /dpod

# 
COPY ./requirements.txt /dpod/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /dpod/requirements.txt

# 
COPY ./app /dpod/app

# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
