import httpx
import pytest

from backend.core.config import Settings
from backend.main import create_app


@pytest.mark.anyio
async def test_health_returns_ok() -> None:
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_jwks_url_defaults_to_project_url() -> None:
    settings = Settings(_env_file=None, supabase_url="https://example.supabase.co/")

    assert settings.jwks_url == "https://example.supabase.co/auth/v1/.well-known/jwks.json"