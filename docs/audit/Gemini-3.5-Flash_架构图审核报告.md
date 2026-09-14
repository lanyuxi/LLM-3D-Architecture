# 「Gemini 3.5 Flash 技术架构 · 3D 教学图」事实审核报告

- 审核对象：`/Users/xixi/WorkBuddy/2026-09-12-16-34-58/outputs/gemini-35-flash-3d-architecture.html`（1413 行）
- 数据层位置：`const RIGHT`（L452–603）、`const LEFT`（L608–657）、`const PLAIN`（L662–689）、`FANS`（L705–706）、`const GROUPS`（L799–810）、`const LEGEND`（L813–820）、`const METRICS`（L824–833）、页头副标题（L196–197）
- 审核人立场：独立核查，不预设开发者判断正确
- 审核日期：2026-09-13

---

## 0. 审核方法与取证说明（先说清可信度边界）

实际使用的取证手段：

1. **直接下载（curl + storage.googleapis.com，网络可达）**：4 份官方 PDF 全部 200 下载成功。
2. **PDF 解析（pypdf + pillow）**：文本用 `re.sub(r'\s+',' ')` 压平后逐词检索；结果为图片的页面用 `page.images` 导出 PNG、2× 放大后以图像方式阅读。
3. **WebFetch**：对 `docs.cloud.google.cn` 成功取到 Cloud 模型页与开发者指南**全文**；对 `ai.google.dev`、`googledevai-dot-devsite-v2-prod-3p.appspot.com`、`deepmind.google` **全部 429/失败**（沙箱代理白名单只放行 `storage.googleapis.com`，直连超时）。
4. **WebSearch（可用）**：用来取回被拦截域的**逐字正文**。搜索引擎返回的是页面原文片段，可直接用于 grep 式核对；但**属于"经搜索索引转存的官方原文"，不是本次会话直接抓取的原始报文**，凡属此类我都在下表标注 `[索引]`。
5. **未做的事**：没有查 arXiv/技术报告以外的镜像站，没有穷尽式回溯每一条第三方说法的原始出处（下文逐条注明"未取到/无法验证"）。

**判定口径**：`正确` = 我取到的官方原文可逐字或语义支持；`需修正` = 大方向对但表述/归属/完整性有实质瑕疵；`错误` = 与官方原文冲突；`无法验证` = 我试过但确实取不到。

---

## 1. 一句话结论

**这张图的骨架是可信的、可以作为教学材料发布，但不建议照现状直接发布**：12 条关键断言里 9 条完全成立、3 条需修正，另有 3 处硬性事实错误（Computer Use 的定性方向错了、SWE-Bench Pro 漏了官方第二个口径、3 Pro model card 页数写错）。修正这 6 处（约 10 分钟工作量）后可放心发布。

---

## 2. 来源分级表（只列我**实际取到内容**的载体）

### ① 官方一手（厂商自己的 model card / 官方文档 / 官方评测）

| # | 载体 | 取法 | 结论 |
|---|---|---|---|
| A1 | Gemini 3.5 Flash Model Card PDF<br>`storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-5-Flash-Model-Card.pdf` | 直接下载，pypdf 文本 + 第 4 页图片导出读图 | **7 页**，`Published: May 2026`。输入/输出/架构/训练数据/软硬件齐备；结果表在 p4 图片 |
| A2 | Gemini 3 Flash Model Card PDF<br>`.../Gemini-3-Flash-Model-Card.pdf` | 直接下载 | **6 页**，`Published: December 2025` |
| A3 | Gemini 3 Pro Model Card PDF<br>`.../Gemini-3-Pro-Model-Card.pdf` | 直接下载 | **10 页**（⚠ 图里写 8 页），`Model Release: November 2025, Last Updated: May 2026`。MoE 原文在此 |
| A4 | 官方评测 PDF<br>`storage.googleapis.com/deepmind-media/gemini/gemini_3-5_flash_model_evaluation.pdf` | 直接下载；第 3 页 `X22.png` 1538×1152 导出并 2× 放大读图 | **3 页**，p3 确为整页图片。方法论句在 p1–p2 |
| A5 | Google Cloud 模型页（中文镜像，官方）<br>`docs.cloud.google.cn/gemini-enterprise-agent-platform/models/gemini/3-5-flash` | WebFetch **直取全文** | 模态 / 1,048,576 / 65,535 / topK 64 / 计算机使用预览版支持 / 缓存 / 批量 / 区域 / 版本日期，全部命中 |
| A6 | Google Cloud 开发者指南页<br>`.../models/guides/gemini-3-5-flash` | WebFetch **直取全文** | 四档思考、400 互斥、思维保留、采样参数弃用、函数调用严格匹配、**输出上限写作 65,536** |
| A7 | Google Cloud 迁移页 `.../models/migrate` | [索引] | 原文句：**「Gemini 3.5 Flash 目前不支援電腦使用。」** |
| A8 | Google AI for Developers《What's new in Gemini 3.5 Flash》<br>`googledevai-dot-devsite-v2-prod-3p.appspot.com/gemini-api/docs/whats-new-gemini-3.5` | [索引]（直取被拦） | 同页同时含 `Computer Use is not supported at this moment.`、迁移清单同义句、以及 `Gemini 3.5 Flash inherits all Gemini 3 family capabilities, including Computer Use.`；FAQ 工具清单含 `…and Computer Use` |
| A9 | 同页**另一路径** `/gemini-api/docs/generate-content/whats-new-gemini-3.5` | [索引] | 同一句话写成 **`inherits all Gemini 3 family capabilities except Computer Use.`** |
| A10 | Google AI for Developers《Gemini 3.x 指南》`/gemini-api/docs/interactions/gemini-3` | [索引] | 四档思考表（含 Dynam 标注）、采样参数原句、思维保留原句、函数调用约束 |
| A11 | Media resolution 文档 `…/gemini-api/docs/generate-content/media-resolution` | [索引] | `UNSPECIFIED / LOW / MEDIUM / HIGH / ULTRA_HIGH` 五值；`ULTRA_HIGH (Per part only)` |
| A12 | Gemini Developer API 定价页 `generativeai-dot-devsite-v2-prod-3p.appspot.com/pricing` | [索引] | 输入 \$1.50 / 输出（含思考 token）\$9.00 / 上下文缓存 \$0.15（存储 \$1.00/1M·小时）；批量 \$0.75/\$4.50 |
| A13 | DeepMind 模型卡网页 `deepmind.google/models/model-cards/gemini-3-5-flash/`、`deepmind.google/technologies/gemini/flash`、`deepmind.google/gemini` | [索引]（直取被拦） | 结果表与 A1 的 PDF **不一致**：SWE-Bench Pro 写 **55.1%**（PDF 写 53.9%），另有 4 处单元格不同 |
| A14 | Vertex AI 模型参考页 `cloud-dot-devsite-v2-prod.appspot.com/vertex-ai/docs/generative-ai/model-reference/overview` | [索引] | `Warning: Sampling parameters (temperature, topP, and topK) are deprecated for all Gemini 3 models.`；`Range for Gemini 3 models versions 3.5 Flash and lower: 0.0 - 2.0 (default: 1.0)` |

### ② 官方人员公开表态（官方博客 / 负责人发声）

| # | 载体 | 取法 | 与图的关系 |
|---|---|---|---|
| B1 | `blog.google/…/gemini-models/introducing-computer-use-gemini-3.5-flash/`（作者 Mateo Quiros，Google DeepMind PM） | [索引] 全文 | **「Computer use is now a built-in tool supported in Gemini 3.5 Flash…」**「developers can start using computer use in 3.5 Flash via the Gemini API and Gemini Enterprise Agent Platform」；第三方报道其发布时间约 **2026-06-25**。**图里完全没引用** |
| B2 | `blog.google/…/gemini-models/gemini-3-5/`《Gemini 3.5: frontier intelligence with action》 | [索引] 全文 | 佐证 76.2% / 1656 Elo / 83.6% / 84.2% 与 5 月 19 日发布 |

### ③ 二手转述（仅用于判断"是否只存在于第三方"，不作为事实依据）

GIGAZINE（HN 参数估算转述）、The Batch/DeepLearning.AI、llm-stats、aiwiki.ai、iotdigitaltwinplm、CSDN、腾讯云开发者社区、cnblogs、awesomeagents 等。

### ④ 无出处

图中所列「128 个专家、每题激活 2 个」——**我在官方与第三方两侧均未找到出处**（见图未误标为官方，见 §4-P9）。

---

## 3. 逐条核查结果表

| # | 图中断言（摘要） | 图中出处标注 | 实际核查结果 | 判定 | 建议改法 |
|---|---|---|---|---|---|
| 1 | 架构范式「稀疏 MoE + transformer-based + 原生多模态」是官方口径，但原文写在 3 Pro 卡上；3.5 Flash 自己的卡上完全没有 MoE 这个词 | 3 Pro Model Card | A3 原文逐字命中；`MoE` 在 A1/A2 中 **0 命中**，在 A3 中 2 命中 | **正确** | 措辞可保留；建议补一句「3.5 Flash 是否为 MoE 属**派生推断**，官方未直接声明」（见 §4-P7） |
| 2 | 派生链三级：3.5 Flash ← 3 Flash ← 3 Pro；3 Pro 卡把 3.5 Flash 列进「Gemini 3 Pro family」名单 | A1/A2/A3 | A1 `based on the Gemini 3 Flash reasoning foundation`、A2 `built off of the Gemini 3 Pro reasoning foundation`、A3 `is not a modification or a fine-tune of a prior model`、家族名单末项 `and Gemini 3.5 Flash` —— 四处全部逐字命中 | **正确** | 无需改 |
| 3 | 参数量 / 激活量 / 专家数 / 路由 top-k / 层数 / 注意力变体 / 位置编码 / 归一化 / TPU 代次 —— 官方全部未公开，三张卡全文零命中 | 三张 model card | 关键词扫描（三卡文本 + 评测 PDF）：`billion` 0、`layer` 0、`attention` 0、`GQA` 0、`multi-query` 0、`RoPE` 0、`rotary` 0、`sliding` 0、`RMSNorm` 0、`QK-norm` 0、`Trillium` 0、`active` 0、`positional` 0、`normalization` 0、`heads` 0、`MLP` 0 —— **结论成立**。⚠ 但 `parameter`(A3:2)、`parameters`(A3:2)、`total`(A3:1)、`expert`(A1:1/A2:1/A3:3)、`experts`(A3:2) **并非零命中**，只是全部出现在 MoE 那句释义与安全评估的 "expert teams" 里，**没有任何数字** | **正确（表述需精确化）** | 「零命中」改为「**无数值**：相关词仅出现在 MoE 释义句与安全评估段，不含任何参数量/专家数/层数」 |
| 4 | 上下文 1,048,576；输出上限官方**三处**写法不一致（64K / 65k / 65,535） | A1 / AI dev docs / A5 | 1,048,576 三处一致 ✅；输出上限实际至少 **5 种**官方写法：`64K token output`(A1)、`64k`(DeepMind 网页)、`65k max output tokens`(A8)、`65,535（默认）`(A5)、**`65,536`(A6)** | **需修正（数量不全）** | 补第 4 处 `65,536`（Cloud 开发者指南）与 `64k`（DeepMind 网页）；把「三处」改为「至少四处/多处」 |
| 5 | 四档 minimal/low/medium/high；默认由 high 改 medium；low 被加强；与 thinking_budget 互斥返回 400 | AI dev docs / Cloud | A10 表逐字命中（含 `high: Supported(Dynamic)`）；A5「现在为 MEDIUM，与预览版中的 HIGH 不同」；A6「同时使用将返回 400 错误」；A8 `low is now significantly improved for code and agentic tasks that require fewer steps` | **正确** | 无需改 |
| 6 | 思维保留默认开启、无需改 API；官方明示会增加 token 与响应时间；历史要么完整要么整体省略 | AI dev docs / Cloud | A6、A10 逐字命中（`No API changes needed`、`may increase token usage and response time`、`either include full context … or omit it entirely`） | **正确** | 建议补一句 GenerateContent API 侧仍需「传入完整未修改的对话历史（含 thought signatures）」 |
| 7 | Computer Use 官方口径不一致：AI dev 正文一处写 not supported，同页迁移说明写 including Computer Use；Cloud 侧标预览版支持 | AI dev docs / Cloud | 三句**都真实存在**（A8/A9/A5）。⚠ 但真实图景是**时间线**：GA 时（5/19）不支持 → **2026-06-25 官方博客 B1 宣布 3.5 Flash 已内建 computer use** → Cloud 页随之标「预览版功能 支持」。且 A9 这条路径写的是 **`except Computer Use`**（图未提） | **需修正（结论方向错）** | 改为「官方文档处于**新旧叠加**状态：GA 期文档写不支持（A8/A7），2026-06-25 官方博客 B1 宣布支持并可通过 Gemini API / Gemini Enterprise Agent Platform 使用（B1 引文），Cloud 模型页已更新为预览版支持；A9 路径仍写 except Computer Use。**不是平台分化，是文档未同步**」 |
| 8 | temperature/top_p/top_k 不再推荐；Cloud 仍列默认值，`topK：64（固定值）`，且此 64 是采样阶段 topK，与 MoE 路由 top-k 无关 | AI dev docs / Cloud | A10 原句逐字命中；A5 参数默认值表逐字命中（温度 1.0 / topP 0.95 / topK 64 固定值）；A14 明示 topK 是「top-k sampling threshold … top k most probable tokens」→ **采样口径，与专家路由无关**，图辨析正确 | **正确** | 无需改 |
| 9 | 训练数据六类来源 + 去重/robots.txt/安全过滤/质量过滤 | 3 Pro Model Card | A3 逐字命中六类来源与四道处理流程；后训练含 `instruction tuning data … reinforcement learning data, and human-preference data`；RL `can leverage multi-step reasoning, problem-solving and theorem-proving data` | **正确** | 无需改 |
| 10 | 官方评测 13 项数字；Gemini 取默认采样档（=medium）、Claude/GPT 取最大思考档 | 官方评测 PDF | **13 项数字全部与 A4 第 3 页表格图片一致**（含 SWE-Bench Pro **53.9%**、MRCR 128k 77.3% / 1M 26.6%、GDPval-AA 1656 Elo）；方法论四句引文逐字命中 | **正确，但漏标第二口径** | 见 §4-P2：**官方模型卡网页 A13 同一张表写 SWE-Bench Pro 55.1%**（另有 4 处单元格不同），图应并列标注 |
| 11 | 刻意不画专家池阵列，理由是专家数未公开 | `FANS = {}`，L701–704 注释 | 官方确无专家数（见 #3），不画 = 不以估算冒充官方，**处理恰当且值得保留**；但 `PLAIN.EXP_ON / EXP_OFF`（L687–688）因 FANS 为空已成死代码，会误导改图者 | **正确（处理恰当）** | 建议删除或注释掉 EXP_ON/EXP_OFF |
| 12 | 并列 8 条第三方说法并明确否定 | 各节点 how / PLAIN | 官方侧**全部零命中**（已逐词扫描，见 #3）；且图**未**把它们当官方。HN 估算「250B–300B 总参 / 10–16B 激活，作者自标 estimate」已由 GIGAZINE 转述**逐字证实**（作者 easygenes，按 TPU **8i** 反推）；第三方确实存在把 MoE/GQA 直接安到 3.5 Flash 头上的文章（如 iotdigitaltwinplm 写 `grouped-query attention`、`sparse MoE layer`，CSDN 写「分层稀疏注意力」） | **正确（个别无法复现）** | `Lithiumflow`／`5:1 局部全局交替`／`128 个专家激活 2 个` 三条**我未取到第三方原文**，但官方零命中成立且图未误标为官方 → 建议图里补出处链接或删去不可复现项 |

---

## 4. 发现的问题清单（按严重度排序）

### P1（严重）Node 11 对 Computer Use 的定性与结论方向错误
- 文件位置：`RIGHT[10]`，L552–560；`PLAIN['11']`，L673
- 图中文字：「结论：官方口径按平台分化——Gemini API 一侧曾明写不支持，Gemini Enterprise Agent Platform 一侧标为预览版可用。」
- 为什么错：
  1. 官方博客 B1（blog.google，Google DeepMind PM 署名，约 2026-06-25）明确宣布 **`Computer use is now a built-in tool supported in Gemini 3.5 Flash`**，「Developers and enterprises can start using computer use in 3.5 Flash **via the Gemini API** and Gemini Enterprise Agent Platform」。也就是说 **Gemini API 一侧现在也支持**，"API 不支持 / Cloud 支持"的平台分化叙述不成立。
  2. 图中引用的 `including Computer Use` 那句（A8），在官方**另一条路径** A9 上写作 **`except Computer Use`**——图只引了前者，导致矛盾被误读为"官方自己打架"而不是"文档版本未同步"。
  3. Cloud 迁移页 A7 至今仍写「Gemini 3.5 Flash 目前不支援電腦使用」，属**过时文档**。
- 正确写法：把它写成**时间线 + 文档滞后**，并补官方博客引用；同时说明 `including / except` 两种官方措辞并存。
- 官方原文：`Computer use is now a built-in tool supported in Gemini 3.5 Flash, delivering our best performance yet for agentic computer use tasks.`（B1）

### P2（严重）Node 15 SWE-Bench Pro 漏掉官方第二口径 55.1%
- 文件位置：`RIGHT[14]`，L593–602；`PLAIN['15']`，L677
- 图中文字：「SWE-Bench Pro 53.9%（single attempt）」
- 核查：我下载的官方 PDF（A1 `X43.png`）与官方评测 PDF（A4 `X22.png`）**两张结果表图片逐像素同源**（`md5(image.tobytes())` 均为 `87fd19a5c9121e0762b016e230a06c4e`），均写 **53.9%**。但官方 DeepMind 网页 A13（`deepmind.google/models/model-cards/gemini-3-5-flash/`）同一张表写 **55.1%**，且另有 4 处单元格不同：3 Flash 49.6%（PDF 48.4%）、CharXiv Sonnet 4.6 72.4%（PDF 70.5%）、ARC-AGI-2 GPT-5.5 84.6%（PDF 85.0%）、GDPval-AA 对手 1676/1769（PDF 1674/1773）。
- 为什么重要：这张图的卖点之一就是"官方口径不一致要如实并列"。这里存在一处**官方内部的 53.9% vs 55.1% 分歧**，图却只给一个数，并且由此会让人误以为"网上的 55.1% 是错的"（实际它是官方网页版数字）。
- 正确写法：并排列出 `53.9%（官方 model card PDF / 官方评测 PDF）` 与 `55.1%（官方 DeepMind 网页版 model card）`。
- 备注：第三方（llm-stats、The Batch 转述、cnblogs）写的 55.1% 与官方网页一致，**不能一律打成"网传错误"**。

### P3（中）3 Pro model card 页数写成 8 页，实为 10 页
- 文件位置：`RIGHT[4]` how，L495；`PLAIN['05']`，L667
- 图中文字：「Gemini 3 Pro model card（8 页）」「3.5 Flash 七页、3 Flash 六页、3 Pro 八页」
- 核查：`PdfReader('g3p.pdf')` → `len(pages) == 10`（p1 封面 / p2–p3 架构与训练 / … / p10）。3.5 Flash = 7 页 ✅、3 Flash = 6 页 ✅。
- 正确写法：改为「10 页」。这处错误会削弱"我逐页翻过"的可信度，建议顺手修。

### P4（中）Node 02「natively multimodal 同时写进 Description 与 Architecture 两处」不准确
- 文件位置：`RIGHT[1]` how，L466
- 图中文字：「官方把「natively multimodal」同时写进 Description 与 Architecture 两处」
- 核查：A3 的 `Description` 段确为 `a suite of highly-capable, natively multimodal, reasoning models`；但 A3 的 `Architecture` 段写的是 **`with native multimodal support for text, vision, and audio inputs`**（`native multimodal support`），**不是** `natively multimodal`。A1/A2 的 Architecture 段则只写 `based on …`。
- 正确写法：「`natively multimodal` 出现在三张卡的 Description 段；`native multimodal support for …` 出现在 3 Pro 卡的 Architecture 段——两者措辞不同，不应混为一谈。」

### P5（中）输出上限「三处不一致」实为至少五处
- 文件位置：`RIGHT[0]`/`RIGHT[14]`，L458/L596；`METRICS` L826
- 核查：`64K token output`(A1)、`64k`(A13 网页)、`65k max output tokens`(A8)、`65,535（默认）`(A5)、**`65,536`(A6 Cloud 开发者指南)**。
- 正确写法：至少补上 `65,536`。另建议注明 `65,535 = 2^16−1`、`65,536 = 2^16`，是典型的"取整口径不同"。

### P6（轻）「零命中」列表里混进了会命中的词
- 文件位置：`RIGHT[4]` how，L495；`RIGHT[5]` how，L505
- 核查：`parameter`(A3×2) / `parameters`(A3×2) / `total`(A3×1) / `expert`(A1×1,A2×1,A3×3) / `experts`(A3×2) 都有命中，只是无数值。
- 正确写法：把「关键词…零命中」改为「**关键词…均无任何数值命中**（词本身仅出现在 MoE 释义句与安全评估段）」。这属于**表述严谨性**问题，不影响结论。

### P7（轻）Node 03 把"派生推断"写成"官方口径覆盖"，主视觉断言略强
- 文件位置：`RIGHT[2]`，L472–480（`face:'SPARSE MoE'`、`star:1`）；页头 L196「稀疏 MoE」
- 核查：官方对 3.5 Flash 只说 `is based on`(A1)，对 3 Flash 说 `is built off of`(A2)，MoE 只写在 A3。图在正文里已诚实交代了链条（L474/L478），但 **LEGEND/页头/节点名把它直接呈现为 3.5 Flash 的既定架构**。
- 建议：主标题或节点名加「（据派生链推断）」字样，避免零基础读者记住"官方说 3.5 Flash 是 MoE"。

### P8（轻）media_resolution「四档」漏了默认值档
- 文件位置：`RIGHT[1]` inner，L463
- 核查：A11 官方枚举为 **`MEDIA_RESOLUTION_UNSPECIFIED`（默认）/ LOW / MEDIUM / HIGH / ULTRA_HIGH（仅 per part）**，共 5 值。
- 建议：改成「low / medium / high / ultra_high 四档可调，另有默认 UNSPECIFIED」。

### P9（轻）三条第三方说法标注但未给出处
- 文件位置：`RIGHT[5]` how，L506；`RIGHT[4]` how，L497；`PLAIN['06']`，L668
- 涉及：`代号 Lithiumflow`、`5:1 局部与全局注意力层交替（局部窗口 1024）`、`128 个专家、每题激活 2 个`、`1 万亿参数、激活 15–20B`
- 核查：官方零命中**已确认**（`attention`/`sliding`/`Lithium` 全 0）；但**我未能复现**上述第三方原文（HN 估算那条已由 GIGAZINE 证实，属唯一确认的一条）。`1 万亿参数` 我在第三方 ima.qq.com 见到，但其激活量写「1500–2000 亿」，与图中「15–20B」不符。
- 建议：保留"官方零命中"结论；对不能给出链接的第三方说法，或补链接、或删除，避免读者反向质疑。

---

## 5. 过度保守 / 漏标的问题（官方已公开却被图忽略）

| 项 | 官方已公开的事实 | 图里的处理 | 评价 |
|---|---|---|---|
| Computer Use | 官方博客 B1 明确宣布 3.5 Flash 内建 computer use、可经 Gemini API 使用 | 完全未引用 | **漏标**，且直接导致 P1 的定性错误。必须补 |
| SWE-Bench Pro | 官方网页版 model card 写 55.1% | 只写 53.9% | **漏标**，与"如实并列官方分歧"的自我定位冲突 |
| 输出上限 | Cloud 开发者指南 A6 写 65,536 | 只说"三处" | 漏标 |
| 官方定价 | A12 官方定价页给出了 \$1.50 / \$9.00 / 缓存 \$0.15 / 批次 \$0.75·\$4.50 | 图只写价格数字（METRICS L832），未标出处 | 建议补「Gemini Developer API 定价页」出处 |
| Knowledge cutoff | A8 FAQ：`Gemini 3.5 Flash has a knowledge cutoff of January 2025.` | 未提 | 可选补充（教学图漏这个不算错） |
| GA 状态 / 退役日 | A5：正式版，2026-05-19 发布，2027-05-19 或之后停用 | METRICS 已正确采用 ✅ | 做得好 |
| 媒体分辨率默认档 | A11 的 UNSPECIFIED | 未提 | 见 P8 |
| 专家池不绘制 | 官方无专家数 | `FANS = {}` + 注释说明 | **判断恰当**：用"估算值画一排方块"确实等于冒充官方数据。这是本图最值得保留的设计决策，但在被审对象里属"正确做法"，不是问题 |
| 思维保留的"无需改 API" | A10：GenerateContent API 仍需传入完整历史 | 图引了官方原话并补了"完整/省略"约束 | 已到位，仅建议补半句 |

---

## 6. 引文核对（逐句去官方全文 grep）

| 图位置 | 图中英文引文（节选） | 结果 |
|---|---|---|
| L475 | `Gemini 3 Pro is a sparse mixture-of-experts (MoE) … transformer-based models … with native multimodal support for text, vision, and audio inputs.` | **逐字命中**（A3；省略号处为参考文献列表，属合规省略） |
| L476 | `Sparse MoE models activate a subset of model parameters per input token by learning to dynamically route tokens to a subset of parameters (experts); this allows them to decouple total model capacity from computation and serving cost per token.` | **逐字命中**（A3） |
| L485 | `Gemini 3.5 Flash is based on the Gemini 3 Flash reasoning foundation with thinking levels…` / `Gemini 3.5 Flash is based on Gemini 3 Flash.` | **逐字命中**（A1） |
| L486 | `Gemini 3 Flash is built off of the Gemini 3 Pro reasoning foundation…` | **逐字命中**（A2，PDF 原文为 `built oﬀ of`，连字 ﬀ 属排版） |
| L487 | `Gemini 3 Pro is not a modification or a fine-tune of a prior model. … and Gemini 3.5 Flash.` | **逐字命中**（A3；连字 ﬁ） |
| L508 | `Training was done using JAX and ML Pathways.` | **逐字命中**（A3） |
| L507 | `trained using Google's Tensor Processing Units (TPUs)` | **逐字命中**（A3） |
| L525 | `New default effort level: Default thinking effort changed from high to medium.` | **逐字命中**（A8） |
| L525 | `The default thinking level for Gemini 3 models is now MEDIUM, changed from HIGH in the preview version of Gemini 3 Flash.` | **逐字命中**（A6 英文版） |
| L527 | `low is now significantly improved for code and agentic tasks that require fewer steps` | **逐字命中**（A8） |
| L535 | `Thought preservation: The model maintains intermediate reasoning across multi-turn conversations automatically. When present in the conversation history, reasoning context carries forward… No API changes needed.` | **逐字命中**（A10/A8；`No API changes needed` 后官方接冒号展开，省略号合规） |
| L536 | `Thoughts from previous turns are now preserved by default. The service no longer clears thought history from the conversation context before passing it to the model.` | **逐字命中**（A6） |
| L538 | `Thought preservation may increase token usage and response time.` | **逐字命中**（A6） |
| L547 | `mismatched responses cause the model to return empty responses with finish_reason: STOP in most cases.` | **逐字命中**（A10/A6） |
| L555 | `Computer Use is not supported at this moment.` | **逐字命中**（A8，New model 段） |
| L556 | `Gemini 3.5 Flash inherits all Gemini 3 family capabilities, including Computer Use.` | **命中**（A8）；⚠ 但 A9 同一句写作 `except Computer Use`，图未体现 |
| L586 | `temperature, top_p, top_k: we strongly recommend not changing the default values. Gemini 3's reasoning capabilities are optimized for the default settings. Use thinking_level instead of thinking_budget.` | **逐字命中**（A10） |
| L597 | `All Gemini scores are pass @1 except where otherwise noted.` | **逐字命中**（A4） |
| L597 | `All of the results are all run with the Gemini API for the model-id gemini-3.5-flash with default sampling settings unless indicated otherwise below.` | **逐字命中**（A4，原文连字 ﬂ） |
| L598 | `For Claude Opus 4.7, Sonnet 4.6, and GPT-5.5 we default to reporting maximum thinking/reasoning settings available…` | **逐字命中**（A4，后接 `but when reported results are not available…`） |
| L600 | `All the results for non-Gemini models are sourced from providers' self reported numbers unless otherwise mentioned below.` | **逐字命中**（A4） |
| L566 | `Does Gemini 3.5 Flash support the Batch API? Yes.` / `Is Context Caching supported? Yes, Context Caching is supported.` | **逐字命中**（A8 FAQ） |
| L575 | `publicly-available web-documents, text, code, images, audio (including speech and other audio types) and video` / `instruction tuning data, reinforcement learning data, and human-preference data` | **命中**（A3）；注：PDF 抽取文本为 `instruction tuning data reinforcement learning data, and human-preference data`，缺一逗号，疑为抽取产物，**不判错** |
| L577 | `deduplication, honoring robots.txt, safety filtering … quality filtering` | **命中**（A3 原文为 `safety ﬁltering in-line with Google's commitment to advancing AI safely and responsibly, and quality ﬁltering`，省略号合规） |

**结论：22 条英文引文全部可命中官方全文，用词、标点、词形（含连字）与官方一致，仅 1 处（L556）存在"只引了对自己结论有利的那一版措辞"的选择性问题。**

---

## 7. 对「官方口径不一致」与「未公开」两类断言的专门评价

这两类都是强断言，逐一看证据强度。

### 7.1 「未公开」类（Node 05 / 06 / 12 / 13 的 ⚠ 项）
- **证据强度：高**。我独立在三张 model card + 官方评测 PDF 上做了 40+ 关键词扫描，`attention / layer / GQA / MQA / RoPE / RMSNorm / QK-norm / sliding / Trillium / billion / active / positional / normalization / MLP / heads` **全部 0 命中**，且无任何参数量、激活量、专家数、层数的数字。
- **残余风险**：① 措辞"零命中"对 `parameter/total/expert` 不成立（无数值，但有词），建议改为「无数值命中」；② 图未说明自己**没有**检索过官方技术报告/博客这类非 model card 载体——我补做了，Google 侧未见架构披露（The Batch 亦记为 `Undisclosed: Parameter count, training data and methods, architectural details`），故结论不变；③ TPU 代次：A3 只说 `Google's Tensor Processing Units (TPUs)`，无代次，"第六代 Trillium 属第三方"成立。
- **总评**：结论正确，证据可加强（把检索清单写进图注就更有说服力）。

### 7.2 「官方口径不一致」类
- **输出上限（Node 15）**：三处引用**全部真实**，但**不止三处**（至少五处），属"证据方向对、覆盖面不全"。
- **Computer Use（Node 11）**：三处引用**全部真实**，但**定性错**。图上把它讲成"API 侧不支持 / Cloud 侧支持"的平台分裂；实际是"GA 期不支持 → 6-25 官方博客 B1 宣布支持 → Cloud 页已更新 → AI dev 文档与 Cloud 迁移页尚未同步"的时间线，且官方内部还存在 `including / except` 两种措辞（A8/A9）。这是全图**唯一一处把"文档滞后"误判为"平台分化"**的地方，也是唯一会实质误导读者（读者可能因此认为"官方就是不支持 computer use"）的地方。
- **SWE-Bench Pro（Node 15 数字）**：图**未识别**这处官方分歧（PDF/网页两版 53.9% vs 55.1%），属于"该报的不一致没报"。
- **总评**：这类断言的"敢并列"精神是对的，但**证据采集面偏窄**——只查了 model card / Cloud 模型页 / AI dev 文档三处，漏掉了官方博客与 DeepMind 网页，而后者恰好是决定 Computer Use 定性和 SWE-Bench Pro 数字的两处关键载体。

---

## 8. 总体评分 / 可发布性判断

| 维度 | 评分 | 说明 |
|---|---|---|
| 官方原文引用准确性 | **9.5 / 10** | 22 条引文全中，含连字与标点；仅 1 处选择性引用 |
| 事实数字准确性 | **8.5 / 10** | 13 个评测数字全对、1M/65,535/topK 64/价格/退役日全对；SWE-Bench Pro 漏第二口径、页数写错 |
| 「未公开」判断 | **9 / 10** | 结论正确、处理方式（不画专家池）值得肯定；措辞需精确化 |
| 「口径不一致」判断 | **6 / 10** | Computer Use 定性错误是硬伤；另有 2 处该报未报 |
| 来源标注完整性 | **6.5 / 10** | 未引用 blog.google、DeepMind 网页、官方定价页 |
| 教学可读性 / 架构图本身 | 不在本次审核范围 | —— |

**可发布性判断：不建议现状直接发布，修正后可发布。**

必须修（发布前）：
1. **P1** Node 11 + `PLAIN['11']`：改为"GA 期不支持 → 2026-06-25 官方博客宣布支持"的时间线，补 `blog.google` 引文与 `except Computer Use` 版本。
2. **P2** Node 15 + `PLAIN['15']`：SWE-Bench Pro 并列 `53.9%（官方 PDF）` / `55.1%（官方网页）`，并说明其余 4 处单元格差异。
3. **P3** L495 / L667：3 Pro model card 改「10 页」。

建议修（提升可信度）：
4. **P4** L466：Description 与 Architecture 措辞区分开。
5. **P5** 输出上限补 `65,536`。
6. **P6** 「零命中」改「无数值命中」。
7. **P7** 节点名补"据派生链推断"。
8. **P9** 给第三方说法补链接或删去不可复现项。

修完前 3 项后，这张图在同类教学"3D 架构图"里属于**诚实度与引文质量都偏高**的一档——它的主要问题不是编造，而是**采集面不够宽**导致对官方最新状态（computer use）判断落后了一个版本。

---

## 9. 补充核查：左侧 2017 对照基线（`const LEFT`，L608–657）

左侧 9 个节点是对 Vaswani et al., 2017《Attention Is All You Need》的复述，不涉及 Gemini 官方载体，但既然图上把它们当作"事实基线"，我也逐项判了一遍（依据为该论文本身的标准结论）。

| # | 图中断言 | 判定 | 说明 |
|---|---|---|---|
| A1 | 词表 Embedding + 正弦位置编码相加注入输入层；正弦编码不需训练、外推能力有限 | **正确** | 与原文 `Positional Encoding` 一节一致；"外推有限"是通行评价，非原文措辞，属合理补充 |
| A2 | 因果掩码把未来位置置为负无穷；O(L²) 完整点积；每层各存一份 KV、不共享 | **正确** | 论文 `Masked Multi-Head Attention` + `scale by 1/√dk` + 逐层独立投影均成立 |
| A3/A5/A7 | Add & Norm = 残差相加 + LayerNorm | **正确** | 原文为 `LayerNorm(x + Sublayer(x))`。⚠ 可补一句「2017 版是 Post-LN」，与当代 Pre-LN 形成对照，教学价值更高 |
| A4 | 跨注意力 Q 来自解码器、K/V 来自编码器，每层各做一遍 | **正确** | 原文 Encoder-Decoder Attention 的确如此 |
| A6 | 稠密 FFN：Linear→激活→Linear，全部参数激活 | **正确** | 原文 FFN 为 `Linear(d_model, d_ff) → ReLU → Linear(d_ff, d_model)`；`d_ff = 2048`（教学图未给维度，属简化，不算错） |
| A8 | Linear 投影到词表维度，输出 logits | **正确** | 与原文 Output Linear + Softmax 一致 |
| A9 | Softmax 归一化后采样，自回归拼回输入；每步重读增长中的 KV Cache | **正确** | 原文未提 KV Cache（该术语为后出），但作为工程解释成立；建议标注"KV Cache 属后续工程实践，非 2017 论文原文用词" |
| A2/A9 cmp 列 | "→ Gemini 3.5 Flash 用的注意力变体官方未公开"、"反而建议不要手动设置 temperature/top_p/top_k" | **正确** | 与 A10 / A3 零命中结论一致 |

**总评：左侧基线无事实错误**，唯一可优化处是把 KV Cache 标注为"后续实践用词"、并补 Post-LN 说明。

## 10. 补充核查：页头 / METRICS / LEGEND（非节点数据）

| 位置 | 图中文字 | 判定 | 依据 |
|---|---|---|---|
| 页头 L196 | 「Google DeepMind · 稀疏 MoE · 原生多模态」 | **需修正（措辞）** | MoE 属派生推断，见 P7；建议加"据派生链" |
| 页头 L197 | `1M` 上下文 / `65k` 最大输出 | **正确** | A1（1M）/ A8（65k）；输出上限多口径问题见 P5 |
| 页头 L197 | `4` 档思考（默认 medium） | **正确** | A10 四值表 + A6 |
| 页头 L197 | 参数规模 `官方未公开` | **正确** | 见 §3 #3 |
| 页头 L197 | `2026-05-19` GA | **正确** | A5「发布阶段：正式版；发布日期：2026 年 5 月 19 日」 |
| 页头 L197 | Gemini 3 Pro family | **正确** | A3 家族名单含 Gemini 3.5 Flash；⚠ 但 DeepMind 网页版把 3.5 Flash 标为 `Status: Preview`，与 Cloud 的"正式版"冲突，图取后者已属合理选择 |
| METRICS L826 | `65k / MAX OUTPUT / 官方三处写法不一致` | **需修正** | 应为"至少四处"，见 P5 |
| METRICS L831 | `GA / 2026-05-19 RELEASE / 退役 2027-05-19 或更晚` | **正确** | A5「停用日期：2027 年 5 月 19 日或之后」 |
| METRICS L832 | `$1.50 / $9 / PER 1M TOKENS / 缓存输入 $0.15` | **正确** | A12 官方定价页逐字命中 |
| METRICS L829–830 | `⚠ PARAM COUNT 官方未公开`、`⚠ EXPERTS / TOP-K 官方未公开` | **正确** | 零数值命中 |
| LEGEND L817 | 「⚠ Computer Use 口径不一」 | **需修正** | 改为「⚠ Computer Use：文档滞后 / 新旧口径并存」，见 P1 |
| LEGEND L814–815 | 「稀疏 MoE 主干 ★」「家族派生链 ★」 | **正确** | 见 §3 #1 #2 |
| 页脚 L239–240 | MRCR 128k 77.3% / 1M 26.6% 两根条形 | **正确** | A4 表格图片逐字一致 |
| 页脚 L238 文案 | 「MRCR v2 · 长上下文检索 · 官方自测」 | **正确** | A4：`Results for all models are self-computed.` |

---

## 附录 A：官方关键原文摘录（供图作者直接取用改图）

**A1 — Gemini 3.5 Flash Model Card（storage.googleapis.com，7 页，Published: May 2026）**

> `Inputs: Text strings …, images, audio, and video files, with a token context window of up to 1M.`
> `Outputs: Text, with a 64K token output.`
> `Architecture: Gemini 3.5 Flash is based on Gemini 3 Flash. For more information about the model architecture for Gemini 3.5 Flash, see the Gemini 3 Flash model card.`
> `Description: … highly-capable, natively multimodal, reasoning models.`

**A2 — Gemini 3 Flash Model Card（6 页，December 2025）**

> `Gemini 3 Flash is built oﬀ of the Gemini 3 Pro reasoning foundation with thinking levels to control the mix of quality, cost and latency.`
> `Model dependencies: Gemini 3 Flash is based on Gemini 3 Pro.`

**A3 — Gemini 3 Pro Model Card（10 页，Model Release: November 2025, Last Updated: May 2026）**

> `Architecture: Gemini 3 Pro is a sparse mixture-of-experts (MoE) (Clark et al., 2022; …; Shazeer et al., 2017) transformer-based models (Vaswani et al., 2017) with native multimodal support for text, vision, and audio inputs.`
> `Sparse MoE models activate a subset of model parameters per input token by learning to dynamically route tokens to a subset of parameters (experts); this allows them to decouple total model capacity from computation and serving cost per token.`
> `Model dependencies: Gemini 3 Pro is not a modiﬁcation or a ﬁne-tune of a prior model. Each subsequent model in the Gemini 3 Pro family is based on Gemini 3 Pro … The Gemini 3 Pro family includes models such as: Gemini 3 Pro Image, Gemini 3 Flash, Gemini 3.1 Pro, Gemini 3.1 Flash Image, Gemini 3.1 Flash-Lite, Gemini 3.1 Flash Live, and Gemini 3.5 Flash.`
> `Hardware: Gemini 3 Pro was trained using Google's Tensor Processing Units (TPUs).` / `Software: Training was done using JAX and ML Pathways.`
> `Data ﬁltering and preprocessing included techniques such as deduplication, honoring robots.txt, safety ﬁltering in-line with Google's commitment to advancing AI safely and responsibly, and quality ﬁltering to mitigate risks and improve training data reliability.`

**A4 — 官方评测 PDF（3 页，p3 为图片）**

> `Methodology: All Gemini scores are pass @1 except where otherwise noted. "Single attempt" settings allow no majority voting or parallel test-time compute. All of the results are all run with the Gemini API for the model-id gemini-3.5-ﬂash with default sampling settings unless indicated otherwise below.`
> `All the results for non-Gemini models are sourced from providers' self reported numbers unless otherwise mentioned below. For Claude Opus 4.7, Sonnet 4.6, and GPT-5.5 we default to reporting maximum thinking/reasoning settings available, but when reported results are not available we use best available reasoning results.`
> 结果表（p3 图片）关键单元格：`SWE-Bench Pro (Public) … Single attempt — 53.9% / 48.4% / 54.2% / 53.0% / 64.3% / 58.6%`；`MRCR v2 (8-needle) 128k (average) 77.3%`、`1M (pointwise) 26.6%`；`ARC-AGI-2 72.1%`；`GDPval-AA 1656 Elo`

**A5 — Google Cloud 模型页（docs.cloud.google.cn，官方中文镜像）**

> `模态：Text — Input and output；Image — Input only；Audio — Input only；Video — Input only`
> `token 数量上限：上下文窗口 1,048,576；输出词元数上限 65,535（默认）`
> `工具：… 计算机使用（预览版功能）支持`
> `上下文缓存：隐式上下文缓存、显式上下文缓存 — 支持`
> `使用选项：预配吞吐量 支持；批量推理 支持；Pay-as-you-go 支持；固定配额 不支持`
> `参数默认值：温度 0.0-2.0（默认 1.0）；topP 0.0-1.0（默认 0.95）；topK：64（固定值）；candidateCount 1-8（默认 1）`
> `版本：gemini-3.5-flash — 发布阶段：正式版；发布日期：2026 年 5 月 19 日；停用日期：2027 年 5 月 19 日或之后`

**A6 — Google Cloud 开发者指南页**

> `输出 token 长度上限：65,536` ← **P5 的第 4 处口径**
> `Gemini 3 模型的默认思考等级现在为 MEDIUM，与 Gemini 3 Flash 预览版中的 HIGH 不同。`
> `thinking_level 参数和旧版 thinking_budget 参数是互斥的。在请求中同时使用这两个参数将返回 400 错误。`
> `默认情况下，系统现在会保留之前轮次的思考。该服务不再在将对话上下文传递给模型之前清除对话上下文中的思考历史记录。`
> `注意：思维保留可能会增加 token 使用量和响应时间。`

**A8 — Google AI for Developers《What's new in Gemini 3.5 Flash》**

> `Gemini 3.5 Flash supports the 1M token context window, 65k max output tokens, thinking, and the same set of tools and platform features as Gemini 3 Flash. Computer Use is not supported at this moment.`
> `New default effort level: Default thinking effort changed from high to medium.`
> `Improved low thinking: low is now significantly improved for code and agentic tasks that require fewer steps, offering strong quality at lower latency and cost.`
> `Gemini 3.5 Flash inherits all Gemini 3 family capabilities, including Computer Use.` ← 与 A9 冲突
> `What are the context window limits? Gemini 3.5 Flash supports a 1 million token input context window and up to 65k output tokens.`
> `Does Gemini 3.5 Flash support the Batch API? Yes.` / `Is Context Caching supported? Yes, Context Caching is supported.`
> `Which tools are supported? Gemini 3.5 Flash supports Google Search, Grounding with Google Maps, File Search, Code Execution, URL Context, and standard Function Calling, including combined tool use, and Computer Use.`

**A9 — 同一文档的另一路径（generate-content 版）**

> `Gemini 3.5 Flash inherits all Gemini 3 family capabilities except Computer Use.` ← **P1 的关键反证**

**A10 — Google AI for Developers《Gemini 3.x 指南》**

> `temperature, top_p, top_k: we strongly recommend not changing the default values. Gemini 3's reasoning capabilities are optimized for the default settings. Use thinking_level instead of thinking_budget.`
> `minimal … Matches the "no thinking" setting for most queries … / low … Minimizes latency and cost. / medium (default) … Balanced thinking for most tasks. / high … Maximizes reasoning depth.`（表中 Gemini 3.5 Flash 的 high 标 `Supported(Dynamic)`）
> `Thought preservation: The model maintains intermediate reasoning across multi-turn conversations automatically. … No API changes needed: Interactions API: … GenerateContent API: Beginning with Gemini 3.5 Flash, the model uses reasoning context from all previous turns when thought signatures are present in the conversation history.`

**B1 — Google 官方博客（Mateo Quiros, Google DeepMind PM，约 2026-06-25）← 图完全未引用**

> `Computer use is now a built-in tool supported in Gemini 3.5 Flash, delivering our best performance yet for agentic computer use tasks.`
> `Developers and enterprises can start using computer use in 3.5 Flash via the Gemini API and Gemini Enterprise Agent Platform.`

**A13 — deepmind.google 网页版模型卡（55.1% 版本）**

> `SWE-Bench Pro (Public) Diverse agentic coding tasks Single attempt 55.1% 49.6% 54.2% — 64.3% 58.6%`
> `ARC-AGI-2 … 72.1% 33.6% 77.1% 58.3% 75.8% 84.6%`（PDF 版为 `85.0%`）
> `GDPval-AA … 1656 1204 1314 1676 1753 1769`（PDF 版为 `1674 / 1773`）

---

## 附：本次取证的原始产物清单

目录 `/Users/xixi/WorkBuddy/2026-09-12-16-34-58/_audit_gemini/`：

- `g35f.pdf` / `g3f.pdf` / `g3p.pdf` / `eval35f.pdf`（官方原件）
- `*.flat.txt`（压平后的可 grep 文本）
- `eval_p3_0.png`、`eval_p3_2x.png`、`g35f_p4_2x.png`、`raw_eval35f.pdf_2.png`、`raw_g35f.pdf_3.png`（结果表图片，含 md5 同源证据）
