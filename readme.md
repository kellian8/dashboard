# Dashboard

A simple, aesthetic desktop dashboard widget with cross-platform support.

## Overview

Desktop dashboard built with PyQt6 and QML, providing a native-feeling UI panel for at-a-glance system information and widgets.

## Requirements

- Python 3.x
- PyQt6

## Setup

```bash
pip install PyQt6
```

## Running

```bash
python -m dashboard
```

## Project Structure

```
dashboard/
├── __main__.py       # Entry point
├── dash/
│   └── gui/
│       ├── mainWindow.py   # Main window controller
│       ├── bridge.py       # Python/QML bridge
│       └── qml/            # UI definitions
├── setup.py
└── Makefile
```

## Development

_Notes and conventions to be added as the project grows._
