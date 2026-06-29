#!/usr/bin/env bash
poetry install --with shared,shared-dev,services,services-dev --without gui
