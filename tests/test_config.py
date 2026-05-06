from __future__ import annotations

from deepintshield import ShieldConfig
from deepintshield.config import DEFAULT_BASE_URL


def test_defaults():
    cfg = ShieldConfig()
    assert cfg.virtual_key == ""
    assert cfg.base_url == DEFAULT_BASE_URL
    assert cfg.timeout == 30.0
    assert cfg.persist is True


def test_explicit_base_url_overrides_default():
    cfg = ShieldConfig(base_url="https://gateway.example.com")
    assert cfg.base_url == "https://gateway.example.com"


def test_base_url_trims_trailing_slash():
    cfg = ShieldConfig(base_url="https://gateway.example.com/")
    assert cfg.base_url == "https://gateway.example.com"


def test_blank_base_url_falls_back_to_default():
    cfg = ShieldConfig(base_url="   ")
    assert cfg.base_url == DEFAULT_BASE_URL


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


def test_from_env_reads_base_url(monkeypatch):
    monkeypatch.setenv("DEEPINTSHIELD_BASE_URL", "https://staging.deepintshield.com/")
    cfg = ShieldConfig.from_env()
    assert cfg.base_url == "https://staging.deepintshield.com"
