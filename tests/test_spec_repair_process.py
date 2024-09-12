from io import BytesIO
import pytest
from httpx import AsyncClient
from infra_ai_service.core.app import get_app
from infra_ai_service.config.config import settings


app = get_app()


@pytest.mark.asyncio
async def test_spec_repair_process():

    base_url = f"http://localhost:{settings.PORT}/"
    async with AsyncClient(app=app, base_url=base_url) as ac:
        err_spec_file = BytesIO(b"err spec file")
        err_log_file = BytesIO(b"err log file content")
        file = {
            "err_spec_file": ("to_repair.spec", err_spec_file),
            "err_log_file": ("error.log", err_log_file),
        }
        resp = await ac.post("/api/v1/spec-repair/", files=file)
        assert resp.status_code == 200
