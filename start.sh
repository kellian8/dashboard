#!/usr/bin/env bash
poetry run python dash-services/main.py &
sleep 2
poetry run python dash-gui/main.py
