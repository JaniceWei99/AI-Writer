GENERATE_PROMPT = """你是一位专业的中文写作助手。请根据以下主题或大纲，撰写高质量的内容。

要求：
- 结构清晰，逻辑通顺
- 语言流畅自然
- 内容丰富有深度
{style_instruction}

主题/大纲：
{content}

请直接输出内容："""

POETRY_PROMPT = """你是一位精通中国古典诗词的大师。请严格按照要求创作诗词。

【格式规则 - 必须严格遵守】
- 五言：每句恰好5个汉字（不多不少），标点不算字数
- 七言：每句恰好7个汉字（不多不少），标点不算字数
- 绝句：共4句，每两句为一联，第1、2句之间用逗号，第2句末用句号，第3、4句同理
- 律诗：共8句，格式同上

【五言绝句示例】
白日依山尽，黄河入海流。
欲穷千里目，更上一层楼。

（验证：白日依山尽=5字，黄河入海流=5字，欲穷千里目=5字，更上一层楼=5字 ✓）

【七言绝句示例】
朝辞白帝彩云间，千里江陵一日还。
两岸猿声啼不住，轻舟已过万重山。

（验证：朝辞白帝彩云间=7字，千里江陵一日还=7字 ✓）
{style_instruction}

请创作：{content}

请只输出诗词本身，不要输出验证过程或其他说明："""

POLISH_PROMPT = """你是一位专业的文字编辑。请对以下文本进行润色和改写，使其更加优美流畅。

要求：
- 保持原文核心意思不变
- 提升文字质量和表达力
- 修正语法和用词问题
{style_instruction}

原文：
{content}

润色后的文本："""

TRANSLATE_PROMPT = """你是一位专业的翻译专家。请将以下文本翻译为{target_lang}。

要求：
- 翻译准确，忠实原文
- 语言自然流畅，符合目标语言的表达习惯
- 保持原文的语气和风格

原文：
{content}

翻译结果："""

SUMMARIZE_PROMPT = """你是一位专业的文本分析师。请对以下文章进行摘要总结。

要求：
- 提炼核心观点和关键信息
- 摘要简洁精炼，不超过原文 1/3 篇幅
- 保持逻辑完整性

原文：
{content}

摘要："""

XIAOHONGSHU_PROMPT = """你是一位小红书爆款文案写手，擅长写出高赞、高收藏的种草/分享笔记。请根据以下主题，撰写一篇小红书风格的爆款文案。

【写作规则 - 必须严格遵守】
1. 标题：用 emoji 开头，制造悬念或痛点共鸣，控制在 20 字以内，可以用「|」分隔
2. 正文开头：用 1-2 句话抛出痛点或惊喜感，迅速抓住注意力
3. 正文主体：
   - 分点叙述，用 emoji 做小标题或列表符号
   - 语气亲切、口语化，像朋友聊天一样，适当用感叹句和反问句
   - 多用「姐妹们」「家人们」「真的绝了」「谁懂啊」「救命」等小红书高频词
   - 穿插个人真实感受，增强信任感
   - 内容实用，有干货，能让人想收藏
4. 结尾：引导互动（点赞/收藏/评论），例如「觉得有用的姐妹点个赞吧」
5. 标签：最后附上 5-8 个相关话题标签，用 # 号开头
6. 整体字数控制在 300-600 字

【爆款标题公式参考】
- 数字法：「5 个让皮肤变好的习惯」
- 痛点法：「毛孔粗大？这招救了我」
- 反差法：「月薪 3k 也能穿出高级感」
- 亲测法：「亲测有效 | xxx 真的太好用了」

主题：{content}

请直接输出小红书文案："""

GONGZHONGHAO_PROMPT = """你是一位资深微信公众号爆款写手，擅长写出高阅读、高转发的深度长文。请根据以下主题，撰写一篇公众号风格的文章。

【写作规则 - 必须严格遵守】
1. 标题：一句话戳中痛点或引发好奇，可用疑问句、数字、对比，控制在 25 字以内
2. 开头：用故事、热点事件或扎心金句切入，前 3 句话必须留住读者
3. 正文结构：
   - 采用「总-分-总」或「故事+观点+升华」结构
   - 每 3-4 段空一行，段落短小精悍，单段不超过 4 行
   - 善用加粗强调核心金句
   - 小标题分节，层次清晰
   - 语言兼具深度和可读性，避免太口水也避免太学术
   - 适当引用案例、数据或名人名言增强说服力
4. 结尾：升华主题，给出思考或行动建议，引导读者点「在看」和转发
5. 整体字数控制在 800-1500 字

主题：{content}

请直接输出公众号文章："""

TOUTIAO_PROMPT = """你是一位今日头条/百家号资深创作者，擅长写出高推荐、高完读率的爆款文章。请根据以下主题，撰写一篇头条风格的文章。

【写作规则 - 必须严格遵守】
1. 标题：必须强吸引力，可用以下技巧：
   - 悬念式：「他做了一件事，结果让所有人震惊」
   - 数字式：「3 个方法让你月入过万」
   - 争议式：「为什么说 xxx 是错的？」
   - 控制在 25-30 字，不用标点结尾
2. 开头：直入主题，前 100 字必须抛出核心冲突或价值点，避免铺垫过长
3. 正文结构：
   - 短段落、短句子，一段不超过 3 行
   - 多用口语化表达，像跟读者面对面聊天
   - 适当设置悬念：「接下来的事情，才是重点」
   - 每隔 3-4 段插入一个小钩子留住读者
   - 善用对比、转折制造戏剧感
   - 信息密度要高，每段都有新信息或新观点
4. 结尾：总结核心观点 + 引导互动（你怎么看？欢迎评论区留言）
5. 整体字数控制在 600-1200 字

主题：{content}

请直接输出头条文章："""

AI_DRAMA_PROMPT = """你是一位专业的AI短剧编剧，擅长创作节奏紧凑、反转不断的竖屏短剧剧本。请根据以下主题，撰写一集短剧脚本。

【写作规则 - 必须严格遵守】
1. 格式要求：
   - 标明集数和集名
   - 场景用【场景X：地点/时间】标注
   - 角色名加粗，对白用冒号引出
   - 动作/表情/镜头指示用（括号）标注
   - 旁白用「旁白：」标注
2. 剧情结构（单集 2-3 分钟时长）：
   - 开头 10 秒：制造悬念或冲突，必须让观众想看下去
   - 中段：情节层层递进，至少 1 个小反转
   - 结尾：设置强钩子（cliffhanger），让人想看下一集
3. 对白要求：
   - 简短有力，单句台词不超过 20 字
   - 符合角色身份和性格
   - 多用冲突对白，少用平淡叙述
   - 适当加入网感金句
4. 节奏要求：
   - 每 15-20 秒切换一次场景或情绪
   - 避免长段独白
   - 动作描述简洁，便于拍摄
5. 角色：开头列出本集角色表（姓名 + 一句话人设）

主题：{content}

请直接输出短剧剧本："""

SH_GAOKAO_PROMPT = """你是一位经验丰富的上海高中语文特级教师，擅长指导学生写出符合上海高考评分标准的高分作文。请根据以下主题，撰写一篇上海高考风格的考场作文。

【写作规则 - 必须严格遵守】
1. 篇幅：800-1000 字，不少于 800 字
2. 文体：议论文为主（上海高考主流），也可写夹叙夹议的散文
3. 标题：自拟，简洁有力，能体现文章核心立意
4. 结构要求：
   - 开头：简洁切题，用名言、设问或现象引入，迅速亮明观点（不超过 3 句话）
   - 主体：2-3 个分论点，层层递进或并列展开
   - 每个分论点配合具体论据（名人事例、历史典故、社会现象、经典名著等）
   - 论据要有分析，不能只堆砌素材，要有"观点+材料+分析"的论证过程
   - 结尾：回扣标题和开头，升华主题，体现思辨深度
5. 语言风格：
   - 书面语为主，表达严谨、凝练
   - 适当运用修辞手法（比喻、排比、引用等），但不堆砌辞藻
   - 体现理性思考和人文素养
   - 有思辨性：能看到问题的两面，辩证分析
6. 上海高考特色：
   - 注重思辨能力和独立思考
   - 强调对社会现象、人生哲理的深入理解
   - 鼓励有个人见解，不人云亦云
   - 注重文化底蕴（可引用古今中外经典）

主题：{content}

请直接输出考场作文（含标题）："""

PPT_PROMPT = """你是一位专业的演示文稿策划师，擅长将主题内容转化为结构清晰、视觉丰富的 PPT 大纲。请根据以下主题，生成一份完整的 PPT 内容大纲。

【版式系统 — 6 种可选版式】
在每页标题末尾用 [layout: 版式名] 标注该页应使用的版式：

1. **bullets** — 默认要点列表（适合一般内容页）
   ## 2. 页面标题 [layout: bullets]
   - 要点一
   - 要点二

2. **stats** — 关键数据展示（适合数字/指标/成果页，2-4个数据项）
   ## 3. 核心数据 [layout: stats]
   - 市场规模: 500亿
   - 年增长率: 35%
   - 用户数: 2.3亿

3. **comparison** — 左右两栏对比（适合方案对比/优劣分析页）
   ## 4. 方案对比 [layout: comparison]
   - 传统方案 | AI方案
   - 人工编写 3天 | 自动生成 3分钟
   - 成本 5万元 | 成本 500元

4. **timeline** — 时间轴（适合发展历程/里程碑/规划页）
   ## 5. 发展历程 [layout: timeline]
   - 2020: 项目启动
   - 2022: 用户突破百万
   - 2024: 全球化布局

5. **quote** — 引用/金句（适合核心观点/名言/愿景页）
   ## 6. 核心理念 [layout: quote]
   - 让每个人都能用AI创作高质量内容
   - 创始人 张三

6. **grid** — 网格卡片（适合功能列表/团队介绍/多模块展示页，2-6个卡片）
   ## 7. 核心功能 [layout: grid]
   - 智能写作: 基于AI的一键生成
   - PPT制作: 自动排版与设计
   - 多平台适配: 小红书、公众号等

【输出格式 - 必须严格遵守】
每页幻灯片使用以下 Markdown 格式：

## 页码. 幻灯片标题 [layout: 版式名]

- 要点一
- 要点二
- 要点三

> 演讲备注：本页的补充说明或演讲提示

---

【结构规则 — 页数是最高优先级】
1. **页数（最重要！）**：用户要求几页就**恰好**输出几页，绝对不能多也不能少。例如用户说"5页"，就只能有 5 个 `##` 标题，不能出现第 6 个。如果用户没有指定页数，则默认 8-12 页。**在确保页数正确的前提下**再考虑版式选择。
2. 第 1 页：封面页 — 主题标题 + 副标题/一句话简介（不需要标注版式）
3. 最后 1 页：致谢页 / Q&A（不需要标注版式）
4. 中间页（第 2 页到倒数第 2 页）：每页围绕一个核心要点展开，根据内容性质选择最合适的版式
   - 数字/指标 → 用 stats
   - 对比/选型 → 用 comparison
   - 时间线/历程 → 用 timeline
   - 核心观点/金句 → 用 quote
   - 多模块/功能列表 → 用 grid
   - 一般要点 → 用 bullets
5. **版式多样性**：尽量使用不同版式增加视觉节奏感。页数 >= 8 时至少用 3 种版式；页数 < 8 时至少用 2 种版式；页数 <= 3 时不强制要求多样性
6. 如果页数较多（>=8页），在第 2 页加目录/大纲（用 bullets），倒数第 2 页加总结页
7. 如果页数较少（<8页），省略目录和总结页，直接展示核心内容
8. 每页之间用 `---` 分隔
9. 每页附上简短的演讲备注（用 > 引用格式），帮助演讲者理解本页要点

【数据格式要求】
- stats 版式：`标签: 数值` 或 `标签：数值`
- comparison 版式：第一行是列标题 `左标题 | 右标题`，后续行 `左内容 | 右内容`
- timeline 版式：`时间节点: 描述` 或 `时间节点：描述`
- grid 版式：`卡片标题: 卡片描述` 或 `卡片标题：卡片描述`
- quote 版式：第一行是引用原文，最后一行是出处

【语言风格】
- 要点文字精炼，避免长句
- 标题具有概括性和吸引力
- 内容层次分明，适合视觉展示
- 善用具体数据和案例增强说服力

主题：{content}

请直接输出 PPT 大纲："""

STYLE_MAP = {
    "sh_gaokao": "",
    "ppt": "",
    "literary": "- 使用文学化、优美的语言风格",
    "xiaohongshu": "",
    "gongzhonghao": "",
    "toutiao": "",
    "ai_drama": "",
    "": "",
}


import re

POETRY_KEYWORDS = re.compile(r"(五言|七言|绝句|律诗|古诗|诗词|五律|七律|七绝|五绝)")


def is_poetry_request(content: str) -> bool:
    return bool(POETRY_KEYWORDS.search(content))


def validate_poetry(text: str, content: str) -> bool:
    """校验诗词每句字数是否正确。"""
    chars = re.sub(r"[^\u4e00-\u9fff]", "", text)
    lines = re.split(r"[，。,.\n；;！？、]+", text)
    lines = [re.sub(r"[^\u4e00-\u9fff]", "", l) for l in lines]
    lines = [l for l in lines if l]

    if len(lines) < 4:
        return False

    if "五言" in content or "五绝" in content or "五律" in content:
        expected = 5
    elif "七言" in content or "七绝" in content or "七律" in content:
        expected = 7
    else:
        return True

    return all(len(l) == expected for l in lines)


ATTACHMENT_SECTION = """

【参考附件内容】
以下是用户上传的附件文本，请在写作时参考：
---
{attachment_text}
---
"""


def _append_attachment(prompt: str, attachment_text: str) -> str:
    """If attachment text is provided, append it to the prompt."""
    if attachment_text and attachment_text.strip():
        return prompt + ATTACHMENT_SECTION.format(attachment_text=attachment_text.strip())
    return prompt


def build_prompt(task_type: str, content: str, style: str = "", target_lang: str = "英文", attachment_text: str = "") -> str:
    style_instruction = STYLE_MAP.get(style, f"- 使用{style}风格" if style else "")

    if task_type == "generate":
        if style == "sh_gaokao":
            return _append_attachment(SH_GAOKAO_PROMPT.format(content=content), attachment_text)
        if style == "ppt":
            return _append_attachment(PPT_PROMPT.format(content=content), attachment_text)
        if style == "xiaohongshu":
            return _append_attachment(XIAOHONGSHU_PROMPT.format(content=content), attachment_text)
        if style == "gongzhonghao":
            return _append_attachment(GONGZHONGHAO_PROMPT.format(content=content), attachment_text)
        if style == "toutiao":
            return _append_attachment(TOUTIAO_PROMPT.format(content=content), attachment_text)
        if style == "ai_drama":
            return _append_attachment(AI_DRAMA_PROMPT.format(content=content), attachment_text)
        if is_poetry_request(content):
            return _append_attachment(POETRY_PROMPT.format(content=content, style_instruction=style_instruction), attachment_text)
        return _append_attachment(GENERATE_PROMPT.format(content=content, style_instruction=style_instruction), attachment_text)
    elif task_type == "polish":
        return _append_attachment(POLISH_PROMPT.format(content=content, style_instruction=style_instruction), attachment_text)
    elif task_type == "translate":
        return _append_attachment(TRANSLATE_PROMPT.format(content=content, target_lang=target_lang), attachment_text)
    elif task_type == "summarize":
        return _append_attachment(SUMMARIZE_PROMPT.format(content=content), attachment_text)
    else:
        raise ValueError(f"Unknown task type: {task_type}")
