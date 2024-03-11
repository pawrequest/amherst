# import pytest
# from fastapi.testclient import TestClient
#
# # from amherst import amherst_app
#
# client = TestClient(amherst_app)
#
#
# def test_index():
#     r = client.get("/")
#     assert r.status_code == 200, r.text
#     assert r.text.startswith("<!doctype html>\n")
#     assert r.headers.get("content-type") == "text/html; charset=utf-8"
#
#
# @pytest.mark.asyncio
# async def test_api_root():
#     r = client.post("/api/hire/view/post", json=)
#     # assert r.status_code == 200
#     print(r.json())
