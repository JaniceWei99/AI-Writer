"""Tests for routers/writing.py — API endpoints with mocked Ollama."""

import io
import json
import pytest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from main import app


@pytest.fixture()
def client():
    return TestClient(app)


# ── Health check ─────────────────────────────────────────────────────


class TestHealthCheck:
    def test_health(self, client: TestClient):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "model" in data


# ── Upload ───────────────────────────────────────────────────────────


class TestUpload:
    def test_upload_txt(self, client: TestClient):
        content = "Hello World"
        resp = client.post(
            "/api/writing/upload",
            files={"file": ("test.txt", io.BytesIO(content.encode()), "text/plain")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["filename"] == "test.txt"
        assert data["text"] == content
        assert data["char_count"] == len(content)

    def test_upload_unsupported_type(self, client: TestClient):
        resp = client.post(
            "/api/writing/upload",
            files={"file": ("img.png", io.BytesIO(b"fake"), "image/png")},
        )
        assert resp.status_code == 400
        assert "不支持" in resp.json()["detail"]

    def test_upload_docx(self, client: TestClient):
        import docx
        doc = docx.Document()
        doc.add_paragraph("docx content")
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        resp = client.post(
            "/api/writing/upload",
            files={"file": ("doc.docx", buf, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        )
        assert resp.status_code == 200
        assert "docx content" in resp.json()["text"]


# ── Process (non-streaming) ─────────────────────────────────────────


class TestProcess:
    @patch("routers.writing.generate", new_callable=AsyncMock)
    def test_process_generate(self, mock_gen, client: TestClient):
        mock_gen.return_value = {"text": "生成的文章内容", "token_count": 10}
        resp = client.post("/api/writing/process", json={
            "task_type": "generate",
            "content": "AI的未来",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"] == "生成的文章内容"
        assert data["token_count"] == 10
        assert data["task_type"] == "generate"

    @patch("routers.writing.generate", new_callable=AsyncMock)
    def test_process_polish(self, mock_gen, client: TestClient):
        mock_gen.return_value = {"text": "润色后", "token_count": 5}
        resp = client.post("/api/writing/process", json={
            "task_type": "polish",
            "content": "原文",
            "style": "literary",
        })
        assert resp.status_code == 200
        assert resp.json()["result"] == "润色后"

    @patch("routers.writing.generate", new_callable=AsyncMock)
    def test_process_translate(self, mock_gen, client: TestClient):
        mock_gen.return_value = {"text": "Hello", "token_count": 1}
        resp = client.post("/api/writing/process", json={
            "task_type": "translate",
            "content": "你好",
            "target_lang": "英文",
        })
        assert resp.status_code == 200
        assert resp.json()["result"] == "Hello"

    @patch("routers.writing.generate", new_callable=AsyncMock)
    def test_process_summarize(self, mock_gen, client: TestClient):
        mock_gen.return_value = {"text": "摘要", "token_count": 2}
        resp = client.post("/api/writing/process", json={
            "task_type": "summarize",
            "content": "一篇很长的文章...",
        })
        assert resp.status_code == 200
        assert resp.json()["result"] == "摘要"

    def test_process_invalid_task_type(self, client: TestClient):
        resp = client.post("/api/writing/process", json={
            "task_type": "invalid",
            "content": "x",
        })
        assert resp.status_code == 422

    @patch("routers.writing.generate", new_callable=AsyncMock)
    def test_process_with_attachment(self, mock_gen, client: TestClient):
        mock_gen.return_value = {"text": "结果", "token_count": 1}
        resp = client.post("/api/writing/process", json={
            "task_type": "generate",
            "content": "写文章",
            "attachment_text": "附件参考内容",
        })
        assert resp.status_code == 200
        prompt_arg = mock_gen.call_args[0][0]
        assert "附件参考内容" in prompt_arg

    @patch("routers.writing.generate", new_callable=AsyncMock)
    def test_process_poetry_with_retry(self, mock_gen, client: TestClient):
        bad_poem = "这首诗字数不对"
        good_poem = "白日依山尽，黄河入海流。欲穷千里目，更上一层楼。"
        mock_gen.side_effect = [
            {"text": bad_poem, "token_count": 5},
            {"text": good_poem, "token_count": 20},
        ]
        resp = client.post("/api/writing/process", json={
            "task_type": "generate",
            "content": "写一首五言绝句",
        })
        assert resp.status_code == 200
        assert resp.json()["result"] == good_poem
        assert mock_gen.call_count == 2


# ── Stream ───────────────────────────────────────────────────────────


class TestStream:
    @patch("routers.writing.generate_stream")
    def test_stream_generate(self, mock_stream, client: TestClient):
        async def fake_stream(prompt):
            for token in ["你", "好", "世", "界"]:
                yield token

        mock_stream.return_value = fake_stream("ignored")

        resp = client.post("/api/writing/stream", json={
            "task_type": "generate",
            "content": "greeting",
        })
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]

        lines = resp.text.strip().split("\n")
        data_lines = [l for l in lines if l.startswith("data: ")]
        payloads = [l.replace("data: ", "") for l in data_lines]
        assert payloads[-1] == "[DONE]"
        tokens = [json.loads(p) for p in payloads[:-1]]
        assert "".join(tokens) == "你好世界"

    @patch("routers.writing.generate", new_callable=AsyncMock)
    def test_stream_poetry_falls_back_to_non_stream(self, mock_gen, client: TestClient):
        poem = "白日依山尽，黄河入海流。欲穷千里目，更上一层楼。"
        mock_gen.return_value = {"text": poem, "token_count": 20}
        resp = client.post("/api/writing/stream", json={
            "task_type": "generate",
            "content": "写一首五言绝句",
        })
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]
        assert "[DONE]" in resp.text


# ── Export PPTX ──────────────────────────────────────────────────────


class TestExportPptx:
    def test_export_pptx_basic(self, client: TestClient):
        md = "## Slide One\n- Bullet A\n---\n## Slide Two\n- Bullet B"
        resp = client.post("/api/writing/export-pptx", json={
            "content": md,
            "title": "Test PPT",
            "template": "business",
        })
        assert resp.status_code == 200
        assert "presentationml.presentation" in resp.headers["content-type"]
        assert len(resp.content) > 0

    def test_export_pptx_default_template(self, client: TestClient):
        resp = client.post("/api/writing/export-pptx", json={
            "content": "## Hello\n- World",
        })
        assert resp.status_code == 200

    def test_export_pptx_all_templates(self, client: TestClient):
        for template in ("business", "minimal", "green", "warm"):
            resp = client.post("/api/writing/export-pptx", json={
                "content": "## Slide\n- Bullet",
                "template": template,
            })
            assert resp.status_code == 200

    def test_export_pptx_empty_content(self, client: TestClient):
        resp = client.post("/api/writing/export-pptx", json={
            "content": "",
            "title": "Empty",
        })
        assert resp.status_code == 200

    def test_export_pptx_filename_header(self, client: TestClient):
        resp = client.post("/api/writing/export-pptx", json={
            "content": "## Slide\n- Bullet",
            "title": "我的演示",
        })
        assert resp.status_code == 200
        assert "Content-Disposition" in resp.headers
