#!/usr/bin/env bash
docker compose up -d &
sleep 3
poetry run python dash-gui/main.py
