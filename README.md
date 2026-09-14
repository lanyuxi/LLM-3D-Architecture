# 大模型 3D 技术架构图

把 14 款旗舰大模型的**官方技术架构**，做成可以旋转、缩放、点开看内部的 **3D 教学图**。

左侧固定放 **2017 年原始 Transformer 基线**做对照，右侧是目标模型的完整前向路径——每一层是什么、为什么这么设计、跟 2017 版比改了什么，点一下就能看到中英文对照的解释，还配一段**不用术语的大白话讲解**。

整个系统是**一个 HTML 文件，零依赖、零构建、零联网**。

<p align="center">
  <a href="index.html"><b>▶ 直接打开 index.html</b></a>
</p>

---

## 目录

- [这是什么](#这是什么)
- [在线预览](#在线预览)
- [14 款模型](#14-款模型)
- [怎么用](#怎么用)
- [仓库结构](#仓库结构)
- [重新构建单文件](#重新构建单文件)
- [新增一款模型](#新增一款模型)
- [事实准确性怎么保证](#事实准确性怎么保证)
- [技术实现](#技术实现)
- [已知边界](#已知边界)

---

## 这是什么

一张**给产品经理和初学者看的**架构图。它解决的问题是：大模型的架构资料散落在 model card PDF、官方文档、博客和论文里，术语密度高、彼此引用，很难建立整体印象。

这里把每一款模型压缩成**一屏可读完的 3D 结构**：

| 层次 | 内容 |
|---|---|
| **3D 主视图** | 右侧一列是目标模型的前向路径（输入 → 主干 → 输出），左侧一列是 2017 版原始 Transformer 的对应结构，一一对齐 |
| **分组括号** | 按内容把节点分组（如 `MULTIMODAL + SPARSE MoE`、`⚠ UNDISCLOSED · CONTEXT`），一眼看出结构分段 |
| **点开看内部** | 放大到 150% 以上并点选任一色块，外壳会「X 光化」，露出它内部的子结构薄板 |
| **详情面板** | 每个节点有：它在做什么 / 内部原理（逐条，带官方原文引用）/ 关键数据 / **与 2017 版的对照结论** |
| **大白话讲解** | 面板里单独一段，刻意不用术语、用生活类比讲同一件事 |
| **底部指标行** | 参数量、层数、专家数、上下文、输出上限、价格等硬指标 |

**一个贯穿全站的原则**：官方没公开的东西，绝不编造。

- 用灰色 `⚠ UNDISCLOSED` 色块显式标出「官方未公开」的环节，而不是随便填一个看起来合理的数字；
- 专家数量未公开的模型，**不画专家池阵列**（画一排方块等于把估算值冒充官方数据）；
- 官方自己数字打架的地方（比如同一张评测表在 PDF 版和网页版 model card 上不一样），两个数一起列，并注明出处；
- 功能状态按**时间线**写清「什么时候不支持、什么时候起支持」，而不是含糊地并列两种说法。

---

## 在线预览

| 入口 | 链接 |
|---|---|
| **GitHub Pages** | `https://lanyuxi.github.io/LLM-3D-Architecture/` |
| WorkBuddy 资料库 | https://www.workbuddy.cn/space/d/qqvCuTmCeOST1hfWiRFYdB |

> GitHub Pages 需要在仓库 **Settings → Pages** 里把 Source 设为 `main` 分支的根目录，一次设置即可。

---

## 14 款模型

| # | 模型 | 厂商 | 架构主线 |
|---|---|---|---|
| 01 | **Gemini 3.5 Flash** | Google DeepMind | 稀疏 MoE（据家族派生链）· 原生多模态 · 规模参数未公开 |
| 02 | Claude Fable 5.1 | Anthropic | 架构未披露 · 一套权重两种防护配置 |
| 03 | GPT-6 Astra | OpenAI | 架构未披露 · 循环层存在争议 |
| 04 | Doubao-Seed-2.1-pro | 字节跳动 / 火山引擎 | 架构未公开 · 附官方研究推断的底座 |
| 05 | 混元 Hy3 | 腾讯 | 稠密-MoE 混合 + MTP + 快慢思考 |
| 06 | 文心 5.1（ERNIE 5.1） | 百度 | 弹性超网络抽取 + 模态无关 MoE |
| 07 | Llama 4 Maverick | Meta | Early Fusion + iRoPE + 交错 MoE |
| 08 | MiMo-V2.5-Pro | 小米 | 混合注意力 6:1 + 稀疏 MoE |
| 09 | Grok 4.6 | xAI | 架构未公开 |
| 10 | MiniMax-M3 | 稀宇科技 | MSA 稀疏注意力 + 原生多模态 |
| 11 | Qwen3.8-Max | 阿里 | 混合注意力 + 细粒度 MoE |
| 12 | Kimi K3 | 月之暗面 | KDA + AttnRes + LatentMoE |
| 13 | GLM-5.3 | 智谱 | MoE + MLA / DSA + IndexShare |
| 14 | DeepSeek-V4.1-Flash | 深度求索 | CED 非对称编解码器 |

其中 **4 款**（Grok 4.6、Doubao-Seed-2.1-pro、GPT-6 Astra、Claude Fable 5.1）厂商基本没公开架构，页面按「**官方公开信息版**」处理：只画官方确实说过的东西，缺的地方留灰块。

---

## 怎么用

**看**：直接用浏览器打开 `index.html`，不需要服务器、不需要联网。

| 操作 | 效果 |
|---|---|
| 拖动 | 旋转视角 |
| 滚轮 / 双指 | 缩放（50% – 600%） |
| `空格` + 拖动、或 `Shift` + 拖动 | 平移 |
| 双击 | 复位视角 |
| `空格`（单击） | 播放 / 暂停自动演示 |
| 左侧栏 | 切换模型（含折叠按钮，状态会记住） |
| 点色块 / 点右侧标签 | 打开详情面板 |
| **放大到 150% 以上再点色块** | 外壳 X 光化，露出内部结构 |

> 左下角有一排视角预设按钮（等距 / 低角 / 俯视），首次打开想快速看清结构时很好用。

---

## 仓库结构

```
.
├── index.html                      ← ★ 单文件系统：外壳 + 14 套图全部内嵌（约 1.3 MB）
├── README.md
├── .nojekyll                       ← 让 GitHub Pages 不做 Jekyll 处理
├── src/                            ← 14 套图的源文件，每份都能独立打开
│   ├── shell.html                  ← 未融合的导航外壳（重跑融合时需要它）
│   ├── gemini-35-flash-3d-architecture.html
│   ├── claude-fable-51-3d-architecture.html
│   ├── gpt-6-astra-3d-architecture.html
│   ├── doubao-seed-21-pro-3d-architecture.html
│   ├── hunyuan-hy3-3d-architecture.html
│   ├── ernie-51-3d-architecture.html
│   ├── llama-4-maverick-3d-architecture.html
│   ├── mimo-v25-pro-3d-architecture.html
│   ├── grok-46-3d-architecture.html
│   ├── minimax-m3-3d-architecture.html
│   ├── qwen-38-max-3d-architecture.html
│   ├── kimi-k3-3d-architecture.html
│   ├── glm-53-3d-architecture.html
│   └── deepseek-v41-flash-3d-architecture.html
├── tools/
│   └── merge_single_file.py        ← 融合脚本：把外壳 + N 套图打包成单文件
└── docs/
    └── audit/                      ← 14 份事实审核报告（逐条对照官方原文）
        ├── Gemini-3.5-Flash_架构图审核报告.md
        ├── Claude-Fable-5.1_架构图审核报告.md
        └── …
```

**`index.html` 和 `src/` 的关系**：`src/` 是源部件，`index.html` 是**用 `tools/merge_single_file.py` 把 14 份源部件打包进来的产物**。改内容要改 `src/`，然后重新打包。

---

## 重新构建单文件

需要 Python 3（只用标准库）。

```bash
python3 tools/merge_single_file.py \
  --shell src/shell.html \
  --out   index.html \
  --dir   src \
  --pairs '{
    "gemini":"gemini-35-flash-3d-architecture.html",
    "fable":"claude-fable-51-3d-architecture.html",
    "gpt6":"gpt-6-astra-3d-architecture.html",
    "doubao":"doubao-seed-21-pro-3d-architecture.html",
    "hy3":"hunyuan-hy3-3d-architecture.html",
    "ernie":"ernie-51-3d-architecture.html",
    "llama":"llama-4-maverick-3d-architecture.html",
    "mimo":"mimo-v25-pro-3d-architecture.html",
    "grok":"grok-46-3d-architecture.html",
    "mm":"minimax-m3-3d-architecture.html",
    "qwen":"qwen-38-max-3d-architecture.html",
    "kimi":"kimi-k3-3d-architecture.html",
    "glm":"glm-53-3d-architecture.html",
    "ds":"deepseek-v41-flash-3d-architecture.html"
  }'
```

脚本会：读 14 份源文件 → 以明文块内嵌进外壳 → 把 `iframe src` 改成 `srcdoc` → 写出 `index.html`，最后**自己做一次往返校验**（抽出内嵌块、还原、与原文件逐字比对），不一致就报错退出。

### 为什么是「明文内嵌 + srcdoc」

14 套图各自都带着自己的 `<style>` 和顶层 `const`，直接拼进同一个 document 会立刻撞选择器、撞重复声明。走 `iframe` 的 `srcdoc`：

- `srcdoc` 生成的是**独立 document** → CSS / JS 作用域天然隔离；
- **14 套已验证过的图一行都不用改**，风险最低；
- 用的是明文内嵌而不是 base64，所以内嵌内容**仍然可 grep、可 diff**。

---

## 新增一款模型

1. 复制 `src/` 里任意一套图当模板，替换数据层（节点数组、大白话文案、图例、指标行、分组标签、页面标题）；
2. 在 `src/shell.html` 的 `MODELS` 数组里加一项，并加上对应的 `<iframe id="pane-xxx">` 元素；
3. 在融合命令的 `--pairs` 里加一项；
4. 重跑 `tools/merge_single_file.py`。

⚠️ 第 2 步漏掉 `<iframe>` 会让切换逻辑取到 `null` 抛错、页面卡在加载态；第 3 步漏掉则新图永远不出现在单文件里。**静态检查都发现不了，必须实际渲染验证。**

---

## 事实准确性怎么保证

这类图最大的风险不是画得不好看，而是**把第三方说法当成官方口径**。所以每一套图都走同一套流程：

1. **先盘清官方到底公开了什么** —— model card PDF、官方文档站、发布博客、评测页，逐个取一手材料；
2. **独立审核** —— 由另一个不共享开发上下文的审核者，自行联网重取官方材料，按四档来源分级（① 官方一手 / ② 官方人员公开表态 / ③ 二手转述 / ④ 无出处）逐条核查；
3. **修正回灌** —— 审核报告里每一条问题都对应一次明确的原文改正，报告存在 `docs/audit/`。

审出来的典型问题类型（都真实发生过）：

- **归属挂错**：内容对、出处错。例如把「稀疏 MoE」说成是某一代模型自己 model card 的表述，实际那句话写在**前代产品的** model card 上（Gemini 走的是 `3.5 Flash → 3 Flash → 3 Pro` 的派生链）；
- **把无出处数字盖上官方章**：某模型「每层 64 专家 / top-k 8」在网上流传很广，实际无官方出处，且那两个数恰好是**上一代**的公开配置；
- **方向写反**：官方把某项风险评级**上调**了，被写成「维持不变」；
- **伪造英文引文**：中文整理稿里「还原」出的英文原句，在官方全文里逐字搜不到；
- **把文档滞后误判成平台差异**：某项能力官方博客已宣布支持，但旧文档页还写着「不支持」，被写成「两个平台口径不同」，实际是**文档没跟上发布**。

对应的硬规矩：**引号里的英文原句必须能在官方全文里逐字 grep 到本身**；「官方措辞」与「本图解读」必须分栏写。

---

## 技术实现

- **纯 CSS 3D transform**（`preserve-3d` + 六面体贴图）+ **自建投影数学**，投影函数与 CSS transform 逐项对齐，不用 Three.js、不用 canvas、不用 WebGL；
- **零依赖**：没有任何外部 CSS / JS / 字体 / 图片请求，断网可用，随便丢进任何静态托管；
- **光学变焦**：缩放时把 `perspective` 与场景同比放大，得到的是纯光学变焦（构图不变、只是变大），而不是把相机怼到模型脸上；
- **自适应视距**：运行时测量内容包围盒，自动求解等比缩放，保证整图不被裁切；
- **2D 标注层**：标签、分组括号、引线画在 SVG / DOM 层（不是 3D 平面里），所以始终正对镜头、永远可读；
- **性能**：SVG 元素池化（每帧只改属性，不重建 DOM）、布局属性缓存、`visibilitychange` 时暂停渲染循环；
- **数据层 / 引擎层分离**：14 套图共用同一套渲染引擎，只是数据层不同——这也是单文件能打包得动的前提。

---

## 已知边界

- **不是官方发布物**：这是第三方整理的教学图，请以各厂商官方文档为准。图中每一处关键断言都标了出处，便于你回查。
- **「官方未公开」的判定有时效性**：厂商可能后续补公开（例如某项能力从「文档写不支持」变成「官方博客宣布支持」）。发现过期请提 issue。
- **左侧 2017 基线是结构对照，不是逐层映射**：它展示的是「2017 版这一环是怎么做的」，与右侧并不总是一一对应（比如现代模型没有编码器—解码器结构）。
- **体量**：单文件约 1.3 MB。首次打开会略等，之后切换模型是本地渲染，不需要网络。
- **移动端**：交互以拖动 + 双指缩放为主，小屏幕上标签会比较密，建议用平板或桌面浏览。

---

## 许可与致谢

本仓库内容为教学整理，架构信息与英文引文的版权归各厂商所有，引用处均已标注来源。

如需转载或用于商业用途，请先开 issue 沟通。
