"""
Web interface for KanJian using FastAPI.

Provides REST API and web UI for interactive visualizations.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import io
import base64

from kanjian import __version__
from kanjian.api import kanjian_simulate, kanjian_visualize, ToolResult


app = FastAPI(
    title="KanJian API",
    description="Interactive visual explanations for math and science concepts",
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimulateRequest(BaseModel):
    """Request model for simulation endpoint."""

    concept: str = "magma"
    steps: int = 100
    params: Optional[Dict[str, Any]] = None


class VisualizeRequest(BaseModel):
    """Request model for visualization endpoint."""

    concept: str
    params: Optional[Dict[str, Any]] = None
    output_path: Optional[str] = None


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint with API information."""
    return {
        "name": "KanJian API",
        "version": __version__,
        "description": "Interactive visual explanations for math and science concepts",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "version": __version__}


@app.get("/concepts")
async def list_concepts() -> Dict[str, List[str]]:
    """List available concepts for visualization."""
    return {
        "concepts": ["magma", "pythagorean", "circle", "linear", "quadratic", "trig"]
    }


@app.post("/simulate")
async def simulate(request: SimulateRequest) -> Dict[str, Any]:
    """
    Run a simulation for a concept.

    Args:
        request: Simulation request with concept, steps, and parameters

    Returns:
        Simulation results
    """
    result = kanjian_simulate(
        concept=request.concept,
        steps=request.steps,
        params=request.params,
    )

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return result.to_dict()


@app.post("/visualize")
async def visualize(request: VisualizeRequest) -> Dict[str, Any]:
    """
    Generate visualization for a concept.

    Args:
        request: Visualization request with concept and parameters

    Returns:
        Visualization data (base64 image or file path)
    """
    result = kanjian_visualize(
        concept=request.concept,
        params=request.params,
        output_path=request.output_path,
    )

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return result.to_dict()


@app.get("/simulate/{concept}")
async def simulate_get(
    concept: str,
    steps: int = Query(default=100, ge=1, le=1000),
) -> Dict[str, Any]:
    """GET endpoint for simulation (convenience)."""
    result = kanjian_simulate(concept=concept, steps=steps)

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return result.to_dict()


@app.get("/visualize/{concept}")
async def visualize_get(
    concept: str,
    as_image: bool = Query(default=False, description="Return as PNG image"),
) -> Any:
    """GET endpoint for visualization (convenience)."""
    result = kanjian_visualize(concept=concept, params={})

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    if as_image and result.data.get("image_base64"):
        image_data = base64.b64decode(result.data["image_base64"])
        return HTMLResponse(
            content=image_data,
            media_type="image/png",
        )

    return result.to_dict()


@app.get("/web", response_class=HTMLResponse)
async def web_interface() -> str:
    """Simple web interface for KanJian."""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>KanJian - Interactive Visual Explanations</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #333; }
        .controls { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .visualization { border: 2px solid #ddd; border-radius: 8px; padding: 20px; text-align: center; min-height: 400px; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 5px; }
        button:hover { background: #0056b3; }
        select, input { padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }
        #result { margin-top: 20px; }
    </style>
</head>
<body>
    <h1>🔬 KanJian - Interactive Visual Explanations</h1>
    <p>Explore math and science concepts through interactive visualizations</p>
    
    <div class="controls">
        <h3>Controls</h3>
        <label>Concept: 
            <select id="concept">
                <option value="magma">Magma Eruption</option>
                <option value="pythagorean">Pythagorean Theorem</option>
                <option value="circle">Circle Area</option>
                <option value="linear">Linear Equation</option>
                <option value="quadratic">Quadratic Equation</option>
                <option value="trig">Trigonometric Function</option>
            </select>
        </label>
        <div id="params"></div>
        <br>
        <button onclick="simulate()">Simulate</button>
        <button onclick="visualize()">Visualize</button>
    </div>
    
    <div class="visualization">
        <h3>Visualization</h3>
        <div id="result">Select a concept and click Visualize</div>
    </div>
    
    <script>
        const paramsConfig = {
            magma: [
                {name: 'length', type: 'number', default: 100},
                {name: 'steps', type: 'number', default: 100},
                {name: 'alpha', type: 'number', default: 0.1, step: 0.01}
            ],
            pythagorean: [
                {name: 'a', type: 'number', default: 3},
                {name: 'b', type: 'number', default: 4}
            ],
            circle: [
                {name: 'radius', type: 'number', default: 5},
                {name: 'segments', type: 'number', default: 16}
            ],
            linear: [
                {name: 'slope', type: 'number', default: 1, step: 0.1},
                {name: 'intercept', type: 'number', default: 0}
            ],
            quadratic: [
                {name: 'a', type: 'number', default: 1, step: 0.1},
                {name: 'b', type: 'number', default: 0},
                {name: 'c', type: 'number', default: 0}
            ],
            trig: [
                {name: 'func', type: 'select', options: ['sin', 'cos', 'tan']},
                {name: 'amplitude', type: 'number', default: 1, step: 0.1},
                {name: 'frequency', type: 'number', default: 1, step: 0.1}
            ]
        };
        
        document.getElementById('concept').addEventListener('change', updateParams);
        updateParams();
        
        function updateParams() {
            const concept = document.getElementById('concept').value;
            const paramsDiv = document.getElementById('params');
            const config = paramsConfig[concept] || [];
            
            paramsDiv.innerHTML = config.map(p => {
                if (p.type === 'select') {
                    return `<label>${p.name}: <select id="param_${p.name}">${p.options.map(o => `<option value="${o}">${o}</option>`).join('')}</select></label>`;
                }
                return `<label>${p.name}: <input type="${p.type}" id="param_${p.name}" value="${p.default}" step="${p.step || 1}"></label>`;
            }).join(' ');
        }
        
        function getParams() {
            const concept = document.getElementById('concept').value;
            const config = paramsConfig[concept] || [];
            const params = {};
            config.forEach(p => {
                const value = document.getElementById(`param_${p.name}`).value;
                params[p.name] = p.type === 'number' ? parseFloat(value) : value;
            });
            return params;
        }
        
        async function simulate() {
            const concept = document.getElementById('concept').value;
            const params = getParams();
            
            try {
                const response = await fetch('/simulate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({concept, steps: params.steps || 100, params})
                });
                const result = await response.json();
                document.getElementById('result').innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('result').innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
            }
        }
        
        async function visualize() {
            const concept = document.getElementById('concept').value;
            const params = getParams();
            
            try {
                const response = await fetch('/visualize', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({concept, params})
                });
                const result = await response.json();
                
                if (result.success && result.data.image_base64) {
                    document.getElementById('result').innerHTML = '<img src="data:image/png;base64,' + result.data.image_base64 + '" style="max-width: 100%;">';
                } else if (result.success) {
                    document.getElementById('result').innerHTML = '<pre>' + JSON.stringify(result.data, null, 2) + '</pre>';
                } else {
                    document.getElementById('result').innerHTML = '<p style="color: red;">Error: ' + result.error + '</p>';
                }
            } catch (error) {
                document.getElementById('result').innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
            }
        }
    </script>
</body>
</html>
    """


def main() -> int:
    """Main entry point for web server."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
