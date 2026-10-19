from sfagent.config import AppConfig, load_config, mask_key, save_config


def test_defaults_when_missing(tmp_path):
    cfg = load_config(tmp_path / "nope.json")
    assert cfg.provider == "deepseek"
    assert cfg.max_cost_usd == 1.0
    assert cfg.thinking is False


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / "cfg" / "config.json"
    save_config(AppConfig(api_key="sk-test-123456789", max_steps=7), path)
    cfg = load_config(path)
    assert cfg.api_key == "sk-test-123456789"
    assert cfg.max_steps == 7


def test_unknown_keys_and_corrupt_file_are_tolerated(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"max_steps": 3, "legacy_field": 1}', encoding="utf-8")
    assert load_config(path).max_steps == 3
    path.write_text("{not json", encoding="utf-8")
    assert load_config(path) == AppConfig()


def test_key_from_env(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-from-env-0000")
    assert AppConfig().resolved_api_key() == "sk-from-env-0000"
    assert AppConfig(api_key="sk-gui").resolved_api_key() == "sk-gui"


def test_mask_key_never_leaks():
    assert mask_key("") == "(not set)"
    assert mask_key("fake-abcdefghijklmnop") == "****mnop"
    assert mask_key("short") == "****"


def test_old_saved_defaults_are_migrated(tmp_path):
    import json

    path = tmp_path / "config.json"
    path.write_text(json.dumps({"max_requests": 40, "max_total_tokens": 2_000_000, "max_steps": 9}))
    cfg = load_config(path)
    assert cfg.max_requests == 80 and cfg.max_total_tokens == 6_000_000 and cfg.max_steps == 9
    path.write_text(json.dumps({"max_requests": 25}))      # a user's own choice is kept
    assert load_config(path).max_requests == 25
    assert AppConfig().max_requests == 80
