#!/bin/bash

# Start the python server
uvicorn --host 0.0.0.0 --port 80 app.main:app
