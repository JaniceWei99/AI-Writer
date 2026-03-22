"""Tests for models/schemas.py — Pydantic model validation."""

import pytest
from pydantic import ValidationError
from models.schemas import TaskType, WritingRequest, WritingResponse


class TestTaskType:
    def test_enum_values(self):
        assert TaskType.GENERATE == "generate"
        assert TaskType.POLISH == "polish"
        assert TaskType.TRANSLATE == "translate"
        assert TaskType.SUMMARIZE == "summarize"

    def test_enum_count(self):
        assert len(TaskType) == 4


class TestWritingRequest:
    def test_minimal_valid(self):
        req = WritingRequest(task_type="generate", content="主题")
        assert req.task_type == TaskType.GENERATE
        assert req.content == "主题"
        assert req.style == ""
        assert req.target_lang == "英文"
        assert req.attachment_text == ""

    def test_full_fields(self):
        req = WritingRequest(
            task_type="translate",
            content="hello",
            style="literary",
            target_lang="日文",
            attachment_text="附件内容",
        )
        assert req.target_lang == "日文"
        assert req.attachment_text == "附件内容"

    def test_invalid_task_type(self):
        with pytest.raises(ValidationError):
            WritingRequest(task_type="invalid", content="x")

    def test_missing_content(self):
        with pytest.raises(ValidationError):
            WritingRequest(task_type="generate")

    def test_all_task_types(self):
        for t in ("generate", "polish", "translate", "summarize"):
            req = WritingRequest(task_type=t, content="test")
            assert req.task_type.value == t


class TestWritingResponse:
    def test_basic(self):
        resp = WritingResponse(task_type="generate", result="结果文本")
        assert resp.result == "结果文本"
        assert resp.token_count == 0

    def test_with_token_count(self):
        resp = WritingResponse(task_type="polish", result="r", token_count=42)
        assert resp.token_count == 42

    def test_invalid_task_type(self):
        with pytest.raises(ValidationError):
            WritingResponse(task_type="bad", result="r")
