"""Runtime configuration, persisted as ``config.yml`` at the project root."""
from __future__ import annotations

import yaml
from pathlib import Path
from dataclasses import dataclass, field, asdict
from loguru import logger

from .paths import CONFIG_PATH

_DEFAULTS = {
    "endpoint_url": "http://localhost:8000/summary",
    "poll_interval_seconds": 60,
    "position": {"x": 20, "y": 20},
}


@dataclass
class Config:
    endpoint_url: str = _DEFAULTS["endpoint_url"]
    poll_interval_seconds: int = _DEFAULTS["poll_interval_seconds"]
    position: dict = field(default_factory=lambda: dict(_DEFAULTS["position"]))

    @classmethod
    def load(cls) -> "Config":
        """Load config, writing a default file on first run."""
        if not CONFIG_PATH.exists():
            logger.warning("Config not found at {} — writing defaults", CONFIG_PATH)
            cfg = cls()
            cfg.save()
            return cfg
        raw = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
        merged = {**_DEFAULTS, **raw}
        cfg = cls(
            endpoint_url=merged["endpoint_url"],
            poll_interval_seconds=int(merged["poll_interval_seconds"]),
            position=merged["position"],
        )
        logger.info(
            "Config loaded | endpoint={} poll_interval={}s position={}",
            cfg.endpoint_url,
            cfg.poll_interval_seconds,
            cfg.position,
        )
        return cfg

    def save(self) -> None:
        CONFIG_PATH.write_text(yaml.dump(asdict(self), default_flow_style=False), encoding="utf-8")
        logger.debug("Config saved to {}", CONFIG_PATH)