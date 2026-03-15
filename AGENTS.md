# AGENTS.md - Agent Guidelines for KanJian

AI coding agent guidelines for the KanJian repository - a tool for interactive visual explanations of math and science concepts.

## Project Overview

KanJian (看见 - "to see" in Chinese) enables LLMs to draw and explain math/science concepts through interactive visualizations. Supports CLI, GUI, and web interfaces with OpenAI Function-Calling integration.

## Build, Lint, and Test Commands

### Running the Application
```bash
# CLI interface
kanjian simulate --concept magma --steps 100
kanjian visualize --concept pythagorean --param a=3 --param b=4

# GUI interface
kanjian-gui

# Web interface
kanjian-web  # Opens at http://localhost:8000/web

# Python module
python -m kanjian --help
```

### Installing Dependencies
```bash
pip install -e .
pip install -e ".[gui]"
pip install -e ".[web]"
pip install -e ".[all]"
```

### Linting and Formatting
```bash
ruff format .
ruff check .
ruff check --fix .
mypy src/kanjian/
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run a single test file
pytest tests/test_unified_api.py -v

# Run a single test function
pytest tests/test_unified_api.py::TestToolResult::test_success_result -v

# Run tests with coverage
pytest --cov=kanjian tests/ -v
```

### Building and Publishing
```bash
python -m build
./upload_pypi.sh    # Linux/Mac
upload_pypi.bat     # Windows
twine upload dist/*
```

## Code Style Guidelines

### Imports
- Order: standard library, third-party, local modules (blank lines between)
- Use absolute imports for local modules
- Use delayed imports in api.py/tools.py to avoid circular dependencies

### Naming Conventions
- **Classes**: PascalCase (e.g., `MagmaSimulation`, `ToolResult`)
- **Functions/Methods**: snake_case (e.g., `kanjian_simulate`, `visualize_pythagorean`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_STEPS`)
- **Variables**: snake_case (e.g., `temperature`, `cooling_rate`)
- **API functions**: `kanjian_verb_noun` format

### Type Hints
- Required for all function parameters and return values
- Use `Optional[T]` for optional parameters
- Use `Dict[str, Any]` for flexible dictionaries

### Documentation
- Google-style docstrings with Args, Returns, Raises sections
- Triple double quotes (`"""`) for docstrings
- Document units in comments (e.g., `# Temperature in Celsius`)

### Code Formatting
- Maximum line length: 100 characters
- 4 spaces for indentation (no tabs)
- Two blank lines between top-level definitions
- Use f-strings for string formatting

### Error Handling
- All API functions return `ToolResult` for consistent error handling
- Catch exceptions and return `ToolResult(success=False, error=str(e))`
- Include `version` in metadata for all results

### ToolResult Pattern
```python
@dataclass
class ToolResult:
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {"success": self.success, "data": self.data, 
                "error": self.error, "metadata": self.metadata}
```

### Testing
- Test file naming: `test_<module_name>.py`
- Test function naming: `test_<functionality>`
- 6 test classes required: TestToolResult, TestKanJianAPI, TestToolsSchema, 
  TestToolsDispatch, TestCLIFlags, TestPackageExports

## Project Structure
```
KanJian/
├── src/kanjian/
│   ├── __init__.py      # Package initialization, version, exports
│   ├── __main__.py      # python -m kanjian entry point
│   ├── core.py          # Core simulation engine
│   ├── api.py           # Unified Python API with ToolResult
│   ├── cli.py           # CLI interface with unified flags
│   ├── gui.py           # tkinter GUI
│   ├── web.py           # FastAPI web interface
│   └── tools.py         # OpenAI Function-Calling tools
├── tests/test_unified_api.py
├── scripts/generate_help_screenshots.py
├── images/
├── pyproject.toml
├── requirements.txt
├── README.md / README_CN.md
├── upload_pypi.sh / upload_pypi.bat
└── AGENTS.md
```

## CLI Unified Flags

| Flag | Description | Notes |
|------|-------------|-------|
| `-V, --version` | Show version | Use `action="version"` |
| `-v, --verbose` | Verbose output | Sets logging to DEBUG |
| `-q, --quiet` | Suppress output | Sets logging to WARNING |
| `--json` | JSON output | Use `dest="json_output"` |
| `-o, --output` | Output path | For file output |

Exit codes: 0=Success, 1=Runtime error, 2=Invalid arguments

## OpenAI Function-Calling Tools

### tools.py Structure
- `TOOLS: list[dict]` - OpenAI tool definitions
- `dispatch(name, arguments) -> dict` - Tool call dispatcher

### Tool Naming
- Format: `kanjian_verb_noun` (e.g., `kanjian_simulate`, `kanjian_visualize`)

### dispatch Function Pattern
```python
def dispatch(name: str, arguments: Dict[str, Any] | str) -> Dict[str, Any]:
    if isinstance(arguments, str):
        arguments = json.loads(arguments)
    if name == "kanjian_simulate":
        from kanjian.api import kanjian_simulate
        return kanjian_simulate(**arguments).to_dict()
    raise ValueError(f"Unknown tool: {name}")
```

## Supported Concepts

| Concept | Parameters | Description |
|---------|-----------|-------------|
| `magma` | length, dx, dt, alpha, cooling_rate | 1D heat equation |
| `pythagorean` | a, b | a² + b² = c² |
| `circle` | radius, segments | A = πr² |
| `linear` | slope, intercept | y = mx + b |
| `quadratic` | a, b, c | y = ax² + bx + c |
| `trig` | func, amplitude, frequency | sin/cos/tan |

## Development Workflow

1. Make changes to relevant modules
2. Run linting: `ruff format . && ruff check . --fix`
3. Run tests: `pytest tests/test_unified_api.py -v`
4. Verify CLI: `kanjian --help && kanjian -V`
5. Test API: `python -c "from kanjian import kanjian_simulate; print(kanjian_simulate(concept='magma'))"`
6. Update documentation if adding features

## Dependencies

- numpy >= 1.24.0: Numerical computing
- matplotlib >= 3.7.0: Visualization
- fastapi, uvicorn, pydantic: Web interface (optional)
- tkinter: GUI (optional)
- pytest, ruff, mypy: Development (optional)

## Repository

- GitHub: https://github.com/cycleuser/KanJian
- PyPI: https://pypi.org/project/kanjian/
