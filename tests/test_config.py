from __future__ import annotations

from deepintshield import ShieldConfig
from deepintshield.config import DEFAULT_BASE_URL


def test_defaults():
    cfg = ShieldConfig()
    assert cfg.virtual_key == ""
    assert cfg.base_url == DEFAULT_BASE_URL
    assert cfg.timeout == 30.0
    assert cfg.persist is True


def test_from_env_trims_virtual_key(monkeypatch):
    monkeypatch.setenv("DEEPINTSHIELD_VIRTUAL_KEY", "  sk-bf-xyz  ")
    cfg = ShieldConfig.from_env()
    assert cfg.virtual_key == "sk-bf-xyz"
    assert cfg.base_url == DEFAULT_BASE_URL


def test_from_env_persist_toggle(monkeypatch):
    monkeypatch.setenv("DEEPINTSHIELD_PERSIST", "false")
    cfg = ShieldConfig.from_env()
    assert cfg.persist is False


def test_from_env_timeout_coercion(monkeypatch):
    monkeypatch.setenv("DEEPINTSHIELD_TIMEOUT", "12")
    cfg = ShieldConfig.from_env()
    assert cfg.timeout == 12.0
