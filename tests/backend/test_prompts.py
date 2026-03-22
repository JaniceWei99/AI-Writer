"""Tests for prompts/writing.py — build_prompt, is_poetry_request, validate_poetry."""

import pytest
from prompts.writing import (
    build_prompt,
    is_poetry_request,
    validate_poetry,
    GENERATE_PROMPT,
    POETRY_PROMPT,
    POLISH_PROMPT,
    TRANSLATE_PROMPT,
    SUMMARIZE_PROMPT,
    XIAOHONGSHU_PROMPT,
    GONGZHONGHAO_PROMPT,
    TOUTIAO_PROMPT,
    AI_DRAMA_PROMPT,
    PPT_PROMPT,
    ATTACHMENT_SECTION,
)


# ── is_poetry_request ──────────────────────────────────────────────


class TestIsPoetryRequest:
    @pytest.mark.parametrize("text", [
        "写一首五言绝句",
        "来一首七言律诗",
        "请作一首古诗",
        "帮我写首五律",
        "写一首七绝关于春天",
        "创作一首五绝",
        "写诗词",
    ])
    def test_positive(self, text: str):
        assert is_poetry_request(text) is True

    @pytest.mark.parametrize("text", [
        "写一篇关于AI的文章",
        "帮我润色这段话",
        "翻译成英文",
        "",
    ])
    def test_negative(self, text: str):
        assert is_poetry_request(text) is False


# ── validate_poetry ─────────────────────────────────────────────────


class TestValidatePoetry:
    def test_valid_five_char_quatrain(self):
        poem = "白日依山尽，黄河入海流。欲穷千里目，更上一层楼。"
        assert validate_poetry(poem, "五言绝句") is True

    def test_valid_seven_char_quatrain(self):
        poem = "朝辞白帝彩云间，千里江陵一日还。两岸猿声啼不住，轻舟已过万重山。"
        assert validate_poetry(poem, "七言绝句") is True

    def test_invalid_five_char_wrong_count(self):
        poem = "白日依山尽了，黄河入海流。欲穷千里目，更上一层楼。"
        assert validate_poetry(poem, "五言绝句") is False

    def test_too_few_lines(self):
        poem = "白日依山尽，黄河入海流。"
        assert validate_poetry(poem, "五言绝句") is False

    def test_generic_poetry_skips_char_check(self):
        poem = "春风又绿江南岸，明月何时照我还。落花流水春去也，天上人间别有天。"
        assert validate_poetry(poem, "古诗") is True

    def test_valid_five_char_lushi(self):
        poem = (
            "国破山河在，城春草木深。感时花溅泪，恨别鸟惊心。"
            "烽火连三月，家书抵万金。白头搔更短，浑欲不胜簪。"
        )
        assert validate_poetry(poem, "五律") is True


# ── build_prompt ─────────────────────────────────────────────────────


class TestBuildPrompt:
    def test_generate_default(self):
        result = build_prompt("generate", "AI的未来")
        assert "AI的未来" in result
        assert "撰写高质量的内容" in result

    def test_generate_sh_gaokao_style(self):
        result = build_prompt("generate", "主题", style="sh_gaokao")
        assert "上海高考" in result

    def test_generate_poetry(self):
        result = build_prompt("generate", "写一首五言绝句关于春天")
        assert "五言" in result
        assert "精通中国古典诗词" in result

    def test_generate_xiaohongshu(self):
        result = build_prompt("generate", "护肤推荐", style="xiaohongshu")
        assert "小红书" in result
        assert "护肤推荐" in result

    def test_generate_gongzhonghao(self):
        result = build_prompt("generate", "职场成长", style="gongzhonghao")
        assert "公众号" in result

    def test_generate_toutiao(self):
        result = build_prompt("generate", "科技新闻", style="toutiao")
        assert "头条" in result

    def test_generate_ai_drama(self):
        result = build_prompt("generate", "霸总爱情", style="ai_drama")
        assert "短剧" in result

    def test_generate_ppt(self):
        result = build_prompt("generate", "人工智能发展趋势", style="ppt")
        assert "演示文稿" in result
        assert "人工智能发展趋势" in result

    def test_polish(self):
        result = build_prompt("polish", "这个文章需要改进")
        assert "润色" in result
        assert "这个文章需要改进" in result

    def test_polish_with_style(self):
        result = build_prompt("polish", "text", style="literary")
        assert "文学" in result

    def test_translate(self):
        result = build_prompt("translate", "你好世界", target_lang="英文")
        assert "英文" in result
        assert "你好世界" in result

    def test_translate_custom_lang(self):
        result = build_prompt("translate", "hello", target_lang="日文")
        assert "日文" in result

    def test_summarize(self):
        result = build_prompt("summarize", "一篇很长的文章内容...")
        assert "摘要" in result

    def test_unknown_task_raises(self):
        with pytest.raises(ValueError, match="Unknown task type"):
            build_prompt("unknown", "content")

    def test_attachment_text_appended(self):
        result = build_prompt("generate", "主题", attachment_text="附件参考内容ABC")
        assert "附件参考内容ABC" in result
        assert "参考附件内容" in result

    def test_no_attachment_when_empty(self):
        result = build_prompt("generate", "主题", attachment_text="")
        assert "参考附件内容" not in result

    def test_attachment_works_for_all_tasks(self):
        for task in ("generate", "polish", "translate", "summarize"):
            result = build_prompt(task, "内容", attachment_text="ref")
            assert "ref" in result

    def test_custom_style_fallback(self):
        result = build_prompt("generate", "主题", style="幽默")
        assert "幽默" in result
