from precedentpal.config import Settings


def test_health_is_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["version"] == "dev"  # no GIT_SHA outside a CI-built image


def test_git_sha_comes_from_the_environment(monkeypatch):
    monkeypatch.setenv("GIT_SHA", "3f2c1ab")
    settings = Settings(app_env="ci", database_url="postgresql://localhost/db", _env_file=None)
    assert settings.git_sha == "3f2c1ab"
