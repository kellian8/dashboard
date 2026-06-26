"""Runtime configuration, persisted as ``config.json`` at the project root."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict

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
            cfg = cls()
            cfg.save()
            return cfg
        raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        merged = {**_DEFAULTS, **raw}
        return cls(
            endpoint_url=merged["endpoint_url"],
            poll_interval_seconds=int(merged["poll_interval_seconds"]),
            position=merged["position"],
        )

    def save(self) -> None:
        CONFIG_PATH.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
