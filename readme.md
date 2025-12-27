# docx_ai_reconstruct 📄➡️🤖➡️📝

> **排版已死，AI 重生。**
> 基于“解耦与重构”范式的 AI 文档自动化重建工具链。

## 📖 背景与哲学

我们正处于一个 AI 能力爆发但工具链尚未跟上的尴尬期。直接让 LLM 修改 `.docx` 二进制文件往往会导致格式崩坏。

**docx_ai_reconstruct** 提出了一种全新的**“双流架构”**工作流范式：

1.  **基建流 (Infrastructure Layer)**：由代码负责。处理文件的物理属性（如解包、排序、像素尺寸、Hash），确保零幻觉。
2.  **认知流 (Cognitive Layer)**：由 AI 负责。处理视觉内容的语义理解（如编写图注、无障碍文本、判断布局逻辑）。

最终，通过**“逻辑缝合”**，将物理骨架与语义灵魂重新结合，实现 100% 可控的文档重建。

## ✨ 核心功能

本项目目前实现了该流水线的 **第一阶段：自动化预处理与视觉资产提取**。

* **🕵️‍♂️ 深度解包**：自动解压 `.docx` 容器，无损提取所有媒体资源（Images）。
* **🔢 自然排序**：实现了符合人类直觉的文件名排序算法（`image2.png` 排在 `image10.png` 之前），确保上下文顺序正确。
* **👁️ 视觉参考生成**：自动生成《视觉参考 PDF》。每一页包含一张大图及其文件名 ID。
    * *作用*：直接投喂给 GPT-4o/Claude，让 AI 能够建立 `文件名 <-> 图片内容` 的语义索引。
* **📦 智能分块**：针对超多图文档，自动将 PDF 切分为多个部分（默认 100 页/卷），防止超出 AI 上下文限制。

## 🛠️ 安装与依赖

本项目基于 Python 开发，核心依赖为 `Pillow` (PIL)。

1. 克隆仓库：
```bash
git clone [https://github.com/yourusername/docx_ai_reconstruct.git](https://github.com/yourusername/docx_ai_reconstruct.git)
cd docx_ai_reconstruct

```

2. 安装依赖：

```bash
pip install pillow

```

## 🚀 快速开始

### 1. 准备文档

将你需要处理的 Word 文档（例如 `report.docx`）准备好。

### 2. 运行提取脚本

打开 `deconstruct.py`，在底部修改输入文件路径（`input_docx`）：

```python
if __name__ == "__main__":
    input_docx = "你的文档路径.docx"  # <--- 修改这里
    output_folder = "./pipeline_output"
    # ...

```

运行脚本：

```bash
python deconstruct.py

```

### 3. 查看输出

脚本将在 `pipeline_output` 目录下生成如下结构：

```text
pipeline_output/
└── 你的文档名/
    ├── media_source/       # [基建素材] 提取出的所有原始图片文件
    └── visual_refs/        # [认知素材] 视觉参考 PDF (例如: Report_VisualRef_Part1.pdf)

```

## 🤖 AI 工作流指南 (The Workflow)

要实现高质量的文档重建，请遵循以下 **“双流”** 步骤：

### Step 1: 视觉认知注入 (Vision)

将生成的 `VisualRef.pdf` 上传给多模态 AI (GPT-4o/Claude)，并发送以下 **Prompt**：

> “这是一个文档的图片资源表（PDF）。请阅读每一页，提取图片 ID，并根据图片内容生成语义数据。请输出一个 JSON 列表，格式如下：
> `[ { "id": "image1.png", "ai_analysis": { "caption": "图注内容...", "alt_text": "无障碍描述...", "layout_suggestion": "full_width/sidebar" } }, ... ]`
> 注意：不要编造图片的尺寸或物理属性，这些由代码处理。”

### Step 2: 逻辑缝合与重构 (Coding)

将文档的纯文本内容（你需要另外提取文本）和 **Step 1 得到的 JSON** 投喂给 AI (如 Claude 3.5 Sonnet)，并发送 Prompt：

> “现在我们进行文档重构。
> 1. 我有一组图片文件（在 media_source 文件夹中）。
> 2. 我有这份 JSON 数据（包含了图片的语义理解）。
> 3. 请写一个 Python 脚本（使用 python-docx）：
> * 读取 JSON 中的语义信息生成图注。
> * **(关键)** 在插入图片时，使用 PIL 读取本地图片文件的实际尺寸（width/height），不要依赖幻觉。
> * 将图片与文本重新缝合。”
> 
> 
> 
> 

## 📅 Roadmap

* [x] **v0.1**: `.docx` 媒体提取与《视觉参考 PDF》生成。
* [ ] **v0.2**: 自动生成包含物理属性（宽高、Hash、主色调）的 `base_info.json`，彻底移除 AI 对物理世界的猜测。
* [ ] **v0.3**: 文本层提取与“锚点植入”。
* [ ] **v0.4**: CLI 命令行工具支持。

## 📄 License

MIT License