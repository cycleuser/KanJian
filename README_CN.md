# KanJian - 交互式视觉解释

[![PyPI version](https://badge.fury.io/py/kanjian.svg)](https://pypi.org/project/kanjian/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**KanJian**（看见）是一个让 LLM 能够通过交互式可视化向用户绘制和解释数学和科学概念的工具。

灵感来自 ChatGPT 的动态可视化解释功能，KanJian 使学习者能够通过调整变量并实时查看变化来与数学公式和科学概念互动。

## 功能特性

- **交互式模拟**：运行各种数学/科学概念的模拟
- **多种界面**：CLI、GUI（tkinter）和 Web（FastAPI）界面
- **6 个核心概念**：
  - 岩浆喷发和凝固（热方程）
  - 勾股定理（a² + b² = c²）
  - 圆面积（A = πr²）
  - 线性方程（y = mx + b）
  - 二次方程（y = ax² + bx + c）
  - 三角函数（sin, cos, tan）
- **OpenAI Function Calling**：内置 LLM Agent 集成工具
- **导出可视化**：将可视化保存为 PNG 图像
- **Python API**：使用 ToolResult 模式的清晰一致的 API

## 系统要求

- Python 3.10 或更高版本
- numpy >= 1.24.0
- matplotlib >= 3.7.0

可选：
- tkinter（用于 GUI）
- fastapi, uvicorn, pydantic（用于 Web 界面）

## 安装

### 从 PyPI 安装

```bash
pip install kanjian
```

### 从源码安装

```bash
git clone https://github.com/cycleuser/KanJian.git
cd KanJian
pip install -e .
```

### 带可选依赖安装

```bash
# GUI 界面
pip install kanjian[gui]

# Web 界面
pip install kanjian[web]

# 开发
pip install kanjian[dev]

# 所有依赖
pip install kanjian[all]
```

## 快速开始

### CLI 界面

```bash
# 运行岩浆模拟
kanjian simulate --concept magma --steps 100

# 可视化勾股定理
kanjian visualize --concept pythagorean --param a=3 --param b=4

# 保存可视化到文件
kanjian visualize --concept linear --param slope=2 --param intercept=1 -o output.png

# 获取 JSON 输出
kanjian simulate --concept quadratic --param a=1 --param b=0 --param c=-4 --json

# 显示版本
kanjian --version
```

### Python API

```python
from kanjian import kanjian_simulate, kanjian_visualize

# 运行模拟
result = kanjian_simulate(concept="pythagorean", params={"a": 3, "b": 4})
print(result.success)  # True
print(result.data)     # 可视化数据

# 生成可视化
result = kanjian_visualize(concept="circle", params={"radius": 5})
print(result.data["image_base64"])  # Base64 编码的 PNG

# 保存到文件
result = kanjian_visualize(
    concept="linear",
    params={"slope": 2, "intercept": 1},
    output_path="line.png"
)
print(result.data["file"])  # line.png
```

### GUI 界面

```bash
kanjian-gui
```

或：

```python
from kanjian.gui import main
main()
```

### Web 界面

```bash
kanjian-web
```

然后在浏览器中打开 http://localhost:8000/web

API 文档位于 http://localhost:8000/docs

## 使用方法

### CLI 选项

| 选项 | 描述 |
|------|------|
| `-V, --version` | 显示版本号 |
| `-v, --verbose` | 详细输出 |
| `-q, --quiet` | 抑制非必要输出 |
| `--json` | 以 JSON 格式输出结果 |
| `-o, --output` | 可视化输出路径 |

### 支持的概念

| 概念 | 参数 | 描述 |
|------|------|------|
| `magma` | length, dx, dt, alpha, cooling_rate | 一维热方程模拟 |
| `pythagorean` | a, b | 勾股定理可视化 |
| `circle` | radius, segments | 圆面积演示 |
| `linear` | slope, intercept | 线性方程图像 |
| `quadratic` | a, b, c | 二次方程抛物线 |
| `trig` | func, amplitude, frequency | 三角函数波形 |

## Python API

### ToolResult 模式

所有 API 函数都返回 `ToolResult` 以保持一致的错误处理：

```python
from kanjian import ToolResult, kanjian_simulate

result = kanjian_simulate(concept="magma", steps=50)

if result.success:
    print(f"数据：{result.data}")
    print(f"元数据：{result.metadata}")
else:
    print(f"错误：{result.error}")

# 转换为 dict 以进行 JSON 序列化
print(result.to_dict())
```

### API 函数

#### `kanjian_simulate(concept, steps=100, params=None) -> ToolResult`

运行数学/科学概念的模拟。

**参数：**
- `concept` (str): 要模拟的概念
- `steps` (int): 模拟步数
- `params` (dict): 概念特定参数

**返回值：** 包含模拟数据的 `ToolResult`

#### `kanjian_visualize(concept, params=None, output_path=None) -> ToolResult`

为概念生成可视化。

**参数：**
- `concept` (str): 要可视化的概念
- `params` (dict): 概念特定参数
- `output_path` (str, 可选): 保存 PNG 的路径

**返回值：** 包含可视化数据（base64 图像或文件路径）的 `ToolResult`

## Agent 集成（OpenAI Function Calling）

KanJian 为 LLM Agent 提供 OpenAI 兼容的工具：

```python
from kanjian.tools import TOOLS, dispatch

# 在 OpenAI API 调用中包含 TOOLS
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=TOOLS,
)

# 分发工具调用
for tool_call in response.choices[0].message.tool_calls:
    result = dispatch(
        tool_call.function.name,
        tool_call.function.arguments,
    )
    print(result)  # {'success': True, 'data': ..., 'error': None, ...}
```

### 可用工具

| 工具 | 描述 |
|------|------|
| `kanjian_simulate` | 运行概念模拟 |
| `kanjian_visualize` | 生成可视化 |

## 项目结构

```
KanJian/
├── src/kanjian/
│   ├── __init__.py      # 包初始化、版本、导出
│   ├── __main__.py      # python -m kanjian 入口
│   ├── core.py          # 核心模拟引擎
│   ├── api.py           # 带 ToolResult 的统一 Python API
│   ├── cli.py           # 命令行界面
│   ├── gui.py           # tkinter GUI
│   ├── web.py           # FastAPI Web 界面
│   └── tools.py         # OpenAI Function-Calling 工具
├── tests/
│   └── test_unified_api.py
├── pyproject.toml
├── requirements.txt
├── README.md
└── README_CN.md
```

## 开发

### 运行测试

```bash
pytest tests/ -v
pytest tests/test_unified_api.py -v
pytest --cov=kanjian tests/
```

### Linting 和格式化

```bash
ruff format .
ruff check .
ruff check --fix .
mypy src/kanjian/
```

### 构建 PyPI 包

```bash
pip install build
python -m build
```

### 上传到 PyPI

```bash
pip install twine
twine upload dist/*
```

或使用提供的脚本：

```bash
# Linux/Mac
./upload_pypi.sh

# Windows
upload_pypi.bat
```

## 许可证

MIT 许可证 - 详见 LICENSE 文件。

## 致谢

- 灵感来自 ChatGPT 的动态可视化解释功能
- 使用 numpy 和 matplotlib 构建
- 遵循 Python 多项目统一开发标准
