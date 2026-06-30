import pytest
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.testclient import TestClient


class _NoopAsgiApp:
    async def __call__(self, scope, receive, send):
        await send({
            "type": "http.response.start",
            "status": 406,
            "headers": [(b"content-type", b"text/plain")],
        })
        await send({"type": "http.response.body", "body": b"not acceptable"})


@pytest.mark.parametrize("path", ["/mcp", "/mcp/"])
def test_mcp_http_route_accepts_both_slash_forms_without_redirect(path):
    app = Starlette(
        routes=[
            Route("/mcp", _NoopAsgiApp(), methods=["GET", "POST", "DELETE"]),
            Route("/mcp/", _NoopAsgiApp(), methods=["GET", "POST", "DELETE"]),
        ]
    )

    response = TestClient(app, follow_redirects=False).get(path)

    assert response.status_code == 406
    assert "location" not in response.headers
