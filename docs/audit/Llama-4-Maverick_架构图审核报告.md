# Llama 4 Maverick 3D 架构图 · 官方一致性审核报告

**审核对象**：`llama-4-maverick-3d-architecture.html`（云端资料库 v14）、`index.html`（导航入口）
**审核日期**：2026-09-13
**审核方式**：独立子代理审核（不共享开发上下文，自行联网取一手材料）+ 开发方二次复核
**结论**：**发现 10 处问题，其中 5 处实质性错误，已全部修正。** 官方规格（400B / 17B、48 层、128+1 专家、5,120 隐藏维度、GQA 40:8、1M 上下文、202,048 词表）经逐项核对**全部正确**。

> 本轮审核与修正后，开发方又补查了三处一手材料用于交叉验证：transformers / vLLM 的 `Llama4` 源码、Meta 在 HF / ModelScope 的官方模型卡、AMD Primus 的 Megatron 配置 PR。下文 E1 / E2 / E3 的证据链因此从「推断」升级为「源码 + 官方口径」双证。

---

## 一、实质性错误（5 处，已修正）

### E1 「48 层 = 32 稠密 + 16 MoE」是算错的（散布 9 处）

| 项 | 内容 |
|---|---|
| 图中原写 | 「中间维度 16,384 · 占 48 层里的**三分之二**」「每 3 层一个循环：**2 层稠密 + 1 层 MoE**」「约占 48 层中的 **32 层**」「只在中途插入专家层」「**2 稠密 + 1 MoE** 交错」 |
| 我的错因 | 我把 `interleave_moe_layer_step = 2` 读成了「**每两层稠密才插一层 MoE**」。这是对配置项**语义**的误读，不是笔误 |
| 正确含义 | 该配置的含义是「**层索引满足条件的层是 MoE**」，不是「稠密层的间隔」。vLLM 源码写得很直白：<br>`is_moe_layer = interleave_moe_layer_step > 0 and (layer_idx + 1) % interleave_moe_layer_step == 0`<br>→ step = 2 时，第 1、3、5…47 层是 MoE，**48 层里 24 层稠密、24 层 MoE**，即 **1:1 逐层交替** |
| 官方口径 | Meta 在 HF 的发布博客原文：*"Llama Scout is a full MoE consisting of 16 experts. Llama Maverick uses 128 experts, but MoE and dense layers alternate. Therefore, experts are applied in **half of the layers**."* —— 官方明确说「一半」，与 24 + 24 完全吻合 |
| 独立验算 | 用参数量自行核算，把两种读法都代进去：<br>· 每层注意力 ≈ 40 头 × 128 维 → QKV+O ≈ 105M；稠密 MLP ≈ 3 × 5,120 × 16,384 ≈ 252M；每层 MoE ≈ 128 路由 + 1 共享 ≈ 16.2B<br>· **24 层 MoE**：24 × 16.2B + 24 × 252M + 48 × 105M + 词表/输出头 ≈ **400.7B** ✓<br>· **16 层 MoE**：16 × 16.2B + 32 × 252M + 48 × 105M + 词表/输出头 ≈ **273B** ✗（与 400B 差 130B，不可能） |
| 修正 | 9 处全部改为「逐层交替 / 24 稠密 + 24 MoE / 一半」，并同步修正指标行、大白话、2017 对照节点 |

### E2 Maverick 的训练数据是 ~22 万亿 token，不是 40 万亿

| 项 | 内容 |
|---|---|
| 图中原写 | 「官方训练数据口径为「**最多 40 万亿 token**」（transformers 官方文档）」 |
| 官方口径 | Meta 官方模型卡（HF / ModelScope 双源逐字一致）：*"Llama 4 Scout was pretrained on **~40 trillion tokens** and Llama 4 Maverick was pretrained on **~22 trillion tokens** of multimodal data"*。模型卡规格表亦列：Scout Token count ~40T、Maverick **~22T** |
| 我为什么会错 | 40T 是 **Scout 的数字**，也是**整个 Llama 4 家族的混合量口径**（Meta 博客称整体训练混合「超过 30 万亿 token」）。我把家族 / 同门数字挂到了 Maverick 头上 |
| 修正 | 改为准确的三层口径：「官方模型卡给出 Maverick 约 22 万亿 token（同表 Scout 为约 40 万亿——这两个数字容易张冠李戴）；官方博客另称整个 Llama 4 的训练数据混合量超过 30 万亿 token」 |

### E3 Scout 的 step = 1 意味着「48 层全是 MoE」，我写反了

| 项 | 内容 |
|---|---|
| 图中原写 | 「Scout 的 step 为 1，即稠密与 MoE **逐层交替**」 |
| 正确含义 | step = 1 时 `(layer_idx + 1) % 1 == 0` **恒成立** → Scout 的 48 层**全部是 MoE 层**，没有稠密 MLP 层。与我 E1 的错误同源：把「交错间隔」当成了配置项含义 |
| 官方口径 | Meta 博客：*"Llama Scout is a **full MoE** consisting of 16 experts"* —— 全 MoE，与源码推断一致 |
| 修正 | 2 处（节点 07 / 09 的 how 与 inner）改为「48 层全部是 MoE 层」 |

### E4 专家池点亮 8 个方块，文字却写「唯一被选中」（自相矛盾）

| 项 | 内容 |
|---|---|
| 图中原写 | 图例与读图说明都写「亮色 = 当前 token 选中的**那 1 个**路由专家（128 选 1）」，但专家池渲染参数是 `const lit = [0,1,4,5,7,8,10,11];`——**点亮了 8 个** |
| 性质 | 这是图**自己和自己**打架：文字说 1 个，画面给 8 个。`num_experts_per_tok` 官方默认为 **1**（top-1 路由），所以是画面错了 |
| 修正 | `const lit = [5];` —— 只点亮 1 个 |

### E5 官方原话是「比稠密模型更高」，我弱引成「相当」

| 项 | 内容 |
|---|---|
| 图中原写 | 「官方称这种交错结构在固定算力下能达到**与稠密模型相当**的质量」 |
| 官方口径 | *"Under fixed FLOPs assumptions, it achieves **comparable quality to dense models**"* —— 这一句本身译作「相当/可比」并不算错，但官方在另一处更强调 *"higher quality than dense models at a fixed training FLOP budget"*。两者表述并存，我单取较弱的一侧 |
| 修正 | 按更完整的一方改写：「在固定训练算力预算下，这种交错结构能带来**比稠密模型更高**的质量」 |

---

## 二、其余 5 处修正

| # | 项 | 修正 |
|---|---|---|
| 6 | 节点 04 称「官方 config … **且明确不使用** QK-Norm」——把 Maverick 的配置当成了 Llama 4 的共性 | QK-Norm 只在 **Scout** 上启用（Meta 博客：*"**Llama Scout** … uses an additional RMS normalization … of the Query and Key states in RoPE layers"*；AMD Primus 的 Maverick 配置实测为 `use_qk_norm: false`）→ 改为「Maverick 不使用 QK-Norm；同系列的 Scout 则相反，它的这一项为 true」 |
| 7 | 节点 08 把「共享 8,192 + 路由 8,192 = 稠密 16,384」写成官方等式 | 官方从未以此表述设计意图 → 补上「这是本图归纳出的数值关系，官方并未以此表述设计意图」 |
| 8 | 节点 11 把「官方在 1M 长度上验证过检索」当成 Maverick 的事实 | 官方博客的长文检索（Needle-in-a-haystack）叙述**主要针对 Scout 的 10M**；Maverick 的 1M 检索能力仅见于二手转述 → 降级为明确说明，并把该槽位换成官方确有的「预训练 256K / 后训练扩展到 1M」 |
| 9 | 节点 05 的 iRoPE 只说「部分层无位置编码」，没有量化 | 补上官方口径：**每 4 层 1 层 NoPE，48 层中 12 层为 NoPE**（`no_rope_layer_interval = 4`） |
| 10 | 节点 06 的 `chunk 8192` 没说适用范围 | 补上：**分块注意力只用在带位置编码的 RoPE 层**；NoPE 层为全因果注意力、可看完整上下文（Meta 博客：*"RoPE layers can only keep track of context in 8K blocks, while NoPE layers have access to the full context"*） |

---

## 三、重点问题逐条核查结果

| 我的疑问 | 核查结论 |
|---|---|
| **48 层到底怎么分？** | ❌ 原来错。**24 稠密 + 24 MoE（1:1 逐层交替）**，源码 + 官方博客 + 参数量验算三证一致 |
| **`interleave_moe_layer_step = 2` 是什么意思？** | ✅ 正确含义是「层索引条件的间隔」；step = 2 → 奇数索引层为 MoE。原先把「2」读成「每 2 层稠密插 1 层 MoE」，错 |
| **Scout 是「逐层交替」吗？** | ❌ 反了。Scout step = 1 → **48 层全是 MoE**，官方称 full MoE |
| **Maverick 预训练 token 数？** | ❌ 原来错（写 40T）。**官方模型卡：~22T**（Scout ~40T、家族混合 >30T） |
| **400B / 17B 成立吗？** | ✅ 官方模型卡与开发者文档双确认；17B 激活亦与「48 层 × 每层 356.7M」的验算吻合 |
| **128 路由 + 1 共享，每 token 激活 1 个？** | ✅ 成立。`num_experts_per_tok` 官方默认 1（top-1）；专家池点亮数已从 8 改为 1 |
| **QK-Norm 是 Llama 4 共性吗？** | ❌ 不是共性。Scout 用、**Maverick 不用**（`use_qk_norm: false`） |
| **iRoPE 的 NoPE 比例？** | ✅ 每 4 层 1 层，48 层中 12 层 |
| **chunk 8192 是全局的吗？** | ✅ 算术对，但**只用于 RoPE 层**；NoPE 层为全因果 |
| **「1M 上验证过检索」可以写吗？** | ⚠️ 不宜。官方 NIAH 叙述主要针对 Scout 10M，Maverick 的 1M 检索属二手转述 |
| **发布日期 / 许可？** | ✅ **2025-04-05 发布**、**Llama 4 Community License**（自定义商用许可，非 MIT / Apache） |
| **视觉编码器？** | ✅ MetaCLIP 改进版，34 层 ViT，与文本 token 拼接做 Early Fusion，无跨注意力 |
| **后训练三阶段？** | ✅ 轻量 SFT → 在线 RL → 轻量 DPO；配合 Behemoth 的协同蒸馏 |
| **词表 202,048 / 隐藏 5,120 / GQA 40:8 / head dim 128？** | ✅ 全部与官方 config 一致 |

---

## 四、确认无误的项

**总体规格**：400B 总参 / 17B 激活、48 层、128+1 专家 / MoE 层、1+1 专家 / token、1M 上下文（Instruct 版）、隐藏维度 5,120、词表 202,048 —— 逐项与 Meta 官方模型卡、开发者文档、config.json 核对无误。

**机制与描述**：Early Fusion 原生多模态（文本 + 图像进同一 token 序列）、iRoPE 交错位置设计、温度缩放只在 NoPE 层、分块注意力只在 RoPE 层、GQA 40 查询 / 8 KV 头、稠密中间维度 16,384、专家中间维度 8,192、top-1 路由、协同蒸馏（Behemoth 为教师）、Behemoth 未发布（图中已正确标为「从 Behemoth 协同蒸馏」而非并列发布）—— 全部核对无误。

**同门未串写**：所有涉及 Scout 的对照处已逐条复核，V2.5 式的「张冠李戴」在本轮 E2 / E3 中被清理干净（Scout：109B / 16 专家 / 40T / 10M 上下文 / step=1 全 MoE）。

**左列 2017 对照**：Attention Is All You Need 的 9 个节点（Embedding + 位置编码、Masked MHA、Add & Norm、Cross-Attention、FFN、Softmax 输出等）与原文一致。

---

## 五、审核局限

1. **HF 直连被网络策略阻断**：模型卡全文经 HF 镜像（huggingface.tw）、ModelScope 官方 API、DeepLearning.AI 摘要三路交叉比对，逐字一致；`interleave_moe_layer_step` 的语义另经 vLLM 官方源码与 AMD Primus 的 Megatron 配置 PR 双证。
2. **「官方是否公开过 Maverick 的 1M 检索能力」**：仅见二手转述，图中已降级说明、不下结论。
3. **「共享 + 路由 = 稠密」的数值巧合**：8,192 + 8,192 = 16,384 在数值上成立，但官方未把它表述为设计意图，图中已明确标注为「本图归纳」。
4. **Behemoth 的最终形态**：官方仅给出「近 2T 总参 / 288B 激活 / 16 专家」，且发布时仍在训练，未发布权重；图中只把它作为蒸馏教师出现。

---

## 六、验证记录

| 验证项 | 结果 |
|---|---|
| 语法检查 | 通过（提取主 `<script>` 块，`node --check`） |
| 节点数 | 24（15 主体 + 9 对照）；含专家池共 36 |
| 演示步数 | 15（HUD `01 / 15`），无 `undefined` 断点 |
| 旧表述扫描 | 9 项全部清除（32 层是稠密 / 16 层是 MoE / 2 稠密 + 1 MoE / 三分之二 / 最多 40 万亿 / 与稠密模型相当 / 约占 48 层中的 32 层 / 官方在 1M 长度上验证过检索 / 每 3 层一个循环） |
| 新增正确内容扫描 | 11 项全部命中 |
| 专家池点亮数 | `const lit = [5]`（1 个）✓ |
| 静态 HTML 区扫描 | 无架构类残留（仅 CSS 像素值） |
| 渲染验证 | 无头 Chrome 渲染正常：右列「★ 稠密与 MoE 逐层交替」、指标行「48 LAYERS / 24 稠密 + 24 MoE」、专家池仅 1 个亮块 |
| 双向自查 | 工作副本 vs 基线副本 60 行变更，全部来自本轮 30 处修正；`index.html` 零改动 |
| 云端版本 | v14（本套共提交 2 次：新增页面 v13 → 审核修正 v14） |
| 修正前备份 | `/tmp/llama-before-auditfix.html` |
