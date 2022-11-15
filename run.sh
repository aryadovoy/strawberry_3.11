#!/bin/env bash

# Retrieve secrets from AWS & export to environment
python3 retrieve-secrets.py .aws-secrets.env 2>&1
export $(grep -v '^#' .aws-secrets.env | xargs) 2>&1

# Migrate
alembic upgrade head

# Run server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
