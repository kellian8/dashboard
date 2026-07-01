#!/usr/bin/env bash
# Write docker compose run command that specified the service
docker compose up -d &
sleep 5
poetry run python dash-gui/main.py
