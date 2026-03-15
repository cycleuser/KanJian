# KanJian - Interactive Visual Explanations

[![PyPI version](https://badge.fury.io/py/kanjian.svg)](https://pypi.org/project/kanjian/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**KanJian** (看见 - "to see" in Chinese) is a tool that lets LLMs draw and explain math and science concepts to users through interactive visualizations.

Inspired by ChatGPT's dynamic visual explanations feature, KanJian enables learners to interact with mathematical formulas and scientific concepts by adjusting variables and seeing real-time changes.

## Features

- **Interactive Simulations**: Run simulations for various math/science concepts
- **Multiple Interfaces**: CLI, GUI (tkinter), and Web (FastAPI) interfaces
- **6 Core Concepts**:
  - Magma eruption and solidification (heat equation)
  - Pythagorean theorem (a² + b² = c²)
  - Circle area (A = πr²)
  - Linear equations (y = mx + b)
  - Quadratic equations (y = ax² + bx + c)
  - Trigonometric functions (sin, cos, tan)
- **OpenAI Function Calling**: Built-in tools for LLM agent integration
- **Export Visualizations**: Save visualizations as PNG images
- **Python API**: Clean, consistent API with ToolResult pattern

## Requirements

- Python 3.10 or higher
- numpy >= 1.24.0
- matplotlib >= 3.7.0

Optional:
- tkinter (for GUI)
- fastapi, uvicorn, pydantic (for web interface)

## Installation

### From PyPI

```bash
pip install kanjian
```

### From Source

```bash
git clone https://github.com/cycleuser/KanJian.git
cd KanJian
pip install -e .
```

### With Optional Dependencies

```bash
# GUI interface
pip install kanjian[gui]

# Web interface
pip install kanjian[web]

# Development
pip install kanjian[dev]

# All dependencies
pip install kanjian[all]
```

## Quick Start

### CLI Interface

```bash
# Run a magma simulation
kanjian simulate --concept magma --steps 100

# Visualize Pythagorean theorem
kanjian visualize --concept pythagorean --param a=3 --param b=4

# Save visualization to file
kanjian visualize --concept linear --param slope=2 --param intercept=1 -o output.png

# Get JSON output
kanjian simulate --concept quadratic --param a=1 --param b=0 --param c=-4 --json

# Show version
kanjian --version
```

### Python API

```python
from kanjian import kanjian_simulate, kanjian_visualize

# Run a simulation
result = kanjian_simulate(concept="pythagorean", params={"a": 3, "b": 4})
print(result.success)  # True
print(result.data)     # Visualization data

# Generate visualization
result = kanjian_visualize(concept="circle", params={"radius": 5})
print(result.data["image_base64"])  # Base64 encoded PNG

# Save to file
result = kanjian_visualize(
    concept="linear",
    params={"slope": 2, "intercept": 1},
    output_path="line.png"
)
print(result.data["file"])  # line.png
```

### GUI Interface

```bash
kanjian-gui
```

Or:

```python
from kanjian.gui import main
main()
```

### Web Interface

```bash
kanjian-web
```

Then open http://localhost:8000/web in your browser.

API docs available at http://localhost:8000/docs

## Usage

### CLI Options

| Option | Description |
|--------|-------------|
| `-V, --version` | Show version number |
| `-v, --verbose` | Verbose output |
| `-q, --quiet` | Suppress non-essential output |
| `--json` | Output results as JSON |
| `-o, --output` | Output path for visualization |

### Supported Concepts

| Concept | Parameters | Description |
|---------|-----------|-------------|
| `magma` | length, dx, dt, alpha, cooling_rate | 1D heat equation simulation |
| `pythagorean` | a, b | Pythagorean theorem visualization |
| `circle` | radius, segments | Circle area demonstration |
| `linear` | slope, intercept | Linear equation graph |
| `quadratic` | a, b, c | Quadratic equation parabola |
| `trig` | func, amplitude, frequency | Trigonometric function wave |

## Python API

### ToolResult Pattern

All API functions return `ToolResult` for consistent error handling:

```python
from kanjian import ToolResult, kanjian_simulate

result = kanjian_simulate(concept="magma", steps=50)

if result.success:
    print(f"Data: {result.data}")
    print(f"Metadata: {result.metadata}")
else:
    print(f"Error: {result.error}")

# Convert to dict for JSON serialization
print(result.to_dict())
```

### API Functions

#### `kanjian_simulate(concept, steps=100, params=None) -> ToolResult`

Run a simulation for a math/science concept.

**Parameters:**
- `concept` (str): Concept to simulate
- `steps` (int): Number of simulation steps
- `params` (dict): Concept-specific parameters

**Returns:** `ToolResult` with simulation data

#### `kanjian_visualize(concept, params=None, output_path=None) -> ToolResult`

Generate visualization for a concept.

**Parameters:**
- `concept` (str): Concept to visualize
- `params` (dict): Concept-specific parameters
- `output_path` (str, optional): Path to save PNG

**Returns:** `ToolResult` with visualization data (base64 image or file path)

## Agent Integration (OpenAI Function Calling)

KanJian exposes OpenAI-compatible tools for LLM agents:

```python
from kanjian.tools import TOOLS, dispatch

# Include TOOLS in your OpenAI API call
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=TOOLS,
)

# Dispatch tool calls
for tool_call in response.choices[0].message.tool_calls:
    result = dispatch(
        tool_call.function.name,
        tool_call.function.arguments,
    )
    print(result)  # {'success': True, 'data': ..., 'error': None, ...}
```

### Available Tools

| Tool | Description |
|------|-------------|
| `kanjian_simulate` | Run simulation for a concept |
| `kanjian_visualize` | Generate visualization |

## CLI Help

```
$ kanjian --help
usage: kanjian [-h] [-V] [-v] [-q] [--json] {simulate,visualize} ...

KanJian - Interactive visual explanations for math and science concepts

positional arguments:
  {simulate,visualize}
                        Available commands
    simulate            Run a simulation for a concept
    visualize           Generate visualization for a concept

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -v, --verbose         Verbose output
  -q, --quiet           Suppress non-essential output
  --json                Output results as JSON
```

## Project Structure

```
KanJian/
├── src/kanjian/
│   ├── __init__.py      # Package initialization, version, exports
│   ├── __main__.py      # python -m kanjian entry point
│   ├── core.py          # Core simulation engine
│   ├── api.py           # Unified Python API with ToolResult
│   ├── cli.py           # Command-line interface
│   ├── gui.py           # tkinter GUI
│   ├── web.py           # FastAPI web interface
│   └── tools.py         # OpenAI Function-Calling tools
├── tests/
│   └── test_unified_api.py
├── pyproject.toml
├── requirements.txt
├── README.md
└── README_CN.md
```

## Development

### Running Tests

```bash
pytest tests/ -v
pytest tests/test_unified_api.py -v
pytest --cov=kanjian tests/
```

### Linting and Formatting

```bash
ruff format .
ruff check .
ruff check --fix .
mypy src/kanjian/
```

### Building for PyPI

```bash
pip install build
python -m build
```

### Uploading to PyPI

```bash
pip install twine
twine upload dist/*
```

Or use the provided scripts:

```bash
# Linux/Mac
./upload_pypi.sh

# Windows
upload_pypi.bat
```

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Inspired by ChatGPT's dynamic visual explanations feature
- Built with numpy and matplotlib
- Following Python multi-project unified development standards
