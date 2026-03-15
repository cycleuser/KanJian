"""
Unified Python API for KanJian.

All public functions return ToolResult for consistent error handling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List
from pathlib import Path
import numpy as np
import io
import base64

from kanjian.core import MagmaSimulation, ConceptVisualizer, VisualizationConfig


@dataclass
class ToolResult:
    """Standard result wrapper for all API functions."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
        }


def kanjian_simulate(
    *,
    concept: str = "magma",
    steps: int = 100,
    params: Optional[Dict[str, Any]] = None,
) -> ToolResult:
    """
    Run a simulation for a math/science concept.

    Args:
        concept: Concept to simulate ('magma', 'pythagorean', 'circle', 'linear', 'quadratic', 'trig')
        steps: Number of simulation steps
        params: Concept-specific parameters

    Returns:
        ToolResult with simulation data
    """
    try:
        params = params or {}

        if concept == "magma":
            sim = MagmaSimulation(
                length=params.get("length", 100),
                dx=params.get("dx", 1.0),
                dt=params.get("dt", 0.1),
                alpha=params.get("alpha", 0.1),
                cooling_rate=params.get("cooling_rate", 0.01),
            )
            states = sim.run(steps)
            data = {
                "concept": "magma",
                "steps": len(states),
                "final_temperature": states[-1].temperature.tolist() if states else [],
                "final_solidified": states[-1].solidified.tolist() if states else [],
                "time": states[-1].time if states else 0,
            }

        elif concept == "pythagorean":
            visualizer = ConceptVisualizer()
            data = visualizer.visualize_pythagorean(
                a=params.get("a", 3), b=params.get("b", 4)
            )

        elif concept == "circle":
            visualizer = ConceptVisualizer()
            data = visualizer.visualize_circle_area(
                radius=params.get("radius", 5), segments=params.get("segments", 16)
            )

        elif concept == "linear":
            visualizer = ConceptVisualizer()
            data = visualizer.visualize_linear_equation(
                slope=params.get("slope", 1.0),
                intercept=params.get("intercept", 0.0),
                x_range=params.get("x_range", (-10, 10)),
            )

        elif concept == "quadratic":
            visualizer = ConceptVisualizer()
            data = visualizer.visualize_quadratic(
                a=params.get("a", 1.0),
                b=params.get("b", 0.0),
                c=params.get("c", 0.0),
                x_range=params.get("x_range", (-10, 10)),
            )

        elif concept == "trig":
            visualizer = ConceptVisualizer()
            data = visualizer.visualize_trig(
                func=params.get("func", "sin"),
                amplitude=params.get("amplitude", 1.0),
                frequency=params.get("frequency", 1.0),
                x_range=params.get("x_range", (0, 4 * np.pi)),
            )

        else:
            return ToolResult(
                success=False,
                error=f"Unknown concept: {concept}. Supported: magma, pythagorean, circle, linear, quadratic, trig",
            )

        from kanjian import __version__

        return ToolResult(
            success=True,
            data=data,
            metadata={"version": __version__, "concept": concept, "steps": steps},
        )

    except Exception as e:
        return ToolResult(
            success=False, error=str(e), metadata={"concept": concept, "steps": steps}
        )


def kanjian_visualize(
    *,
    concept: str,
    params: Optional[Dict[str, Any]] = None,
    output_path: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
) -> ToolResult:
    """
    Generate visualization for a concept and optionally save to file.

    Args:
        concept: Concept to visualize
        params: Concept-specific parameters
        output_path: Optional path to save visualization (PNG)
        config: Visualization configuration

    Returns:
        ToolResult with visualization data or file path
    """
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from kanjian.core import ConceptVisualizer

        config_dict = config or {}
        vis_config = VisualizationConfig(
            width=config_dict.get("width", 800),
            height=config_dict.get("height", 600),
            dpi=config_dict.get("dpi", 100),
            style=config_dict.get("style", "dark_background"),
        )

        visualizer = ConceptVisualizer(vis_config)

        if concept == "magma":
            sim = MagmaSimulation()
            sim.run(params.get("steps", 50) if params else 50)

            plt.style.use(vis_config.style)
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

            im = ax1.imshow(
                sim.T.reshape(1, -1), cmap=vis_config.color_map, aspect="auto"
            )
            ax1.set_title("Temperature Distribution")
            ax1.set_xlabel("Distance")
            plt.colorbar(im, ax=ax1, label="Temperature (°C)")

            ax2.fill_between(
                sim.x, sim.T, where=sim.solidified, alpha=0.5, label="Solidified"
            )
            ax2.plot(sim.x, sim.T, "r-", label="Temperature")
            ax2.axhline(
                y=sim.solidification_temp,
                color="k",
                linestyle="--",
                label="Solidification Temp",
            )
            ax2.set_xlabel("Distance")
            ax2.set_ylabel("Temperature (°C)")
            ax2.legend()

            plt.tight_layout()

            if output_path:
                plt.savefig(output_path, dpi=vis_config.dpi, bbox_inches="tight")
                plt.close()
                data = {"file": output_path}
            else:
                buf = io.BytesIO()
                plt.savefig(buf, format="png", dpi=vis_config.dpi, bbox_inches="tight")
                plt.close()
                buf.seek(0)
                img_base64 = base64.b64encode(buf.read()).decode("utf-8")
                data = {"image_base64": img_base64}

        else:
            sim_result = kanjian_simulate(concept=concept, params=params, steps=1)
            if not sim_result.success:
                return sim_result

            vis_data = sim_result.data
            plt.style.use(vis_config.style)
            fig, ax = plt.subplots(figsize=(10, 6))

            if concept == "linear" or concept == "quadratic" or concept == "trig":
                x = vis_data["visualization"]["x"]
                y = vis_data["visualization"]["y"]
                ax.plot(x, y, "b-", linewidth=2)
                ax.set_title(vis_data["formula"])
                ax.set_xlabel("x")
                ax.set_ylabel("y")
                ax.grid(vis_config.show_grid)

            elif concept == "pythagorean":
                triangle = vis_data["visualization"]["triangle"]
                triangle_coords = triangle + [triangle[0]]
                tri_x, tri_y = zip(*triangle_coords)
                ax.plot(tri_x, tri_y, "b-", linewidth=2)
                ax.set_title(
                    f"{vis_data['formula']} → c = {vis_data['parameters']['c']:.2f}"
                )
                ax.set_aspect("equal")
                ax.grid(vis_config.show_grid)

            elif concept == "circle":
                circle_data = vis_data["visualization"]["circle"]
                from matplotlib.patches import Circle

                circle = Circle(
                    circle_data["center"],
                    circle_data["radius"],
                    fill=False,
                    linewidth=2,
                )
                ax.add_patch(circle)
                ax.set_title(
                    f"{vis_data['formula']} = {vis_data['parameters']['area']:.2f}"
                )
                ax.set_aspect("equal")
                ax.grid(vis_config.show_grid)

            plt.tight_layout()

            if output_path:
                plt.savefig(output_path, dpi=vis_config.dpi, bbox_inches="tight")
                plt.close()
                data = {"file": output_path}
            else:
                buf = io.BytesIO()
                plt.savefig(buf, format="png", dpi=vis_config.dpi, bbox_inches="tight")
                plt.close()
                buf.seek(0)
                img_base64 = base64.b64encode(buf.read()).decode("utf-8")
                data = {"image_base64": img_base64, "concept_data": vis_data}

        from kanjian import __version__

        return ToolResult(
            success=True,
            data=data,
            metadata={
                "version": __version__,
                "concept": concept,
                "output": output_path,
            },
        )

    except Exception as e:
        return ToolResult(
            success=False,
            error=str(e),
            metadata={"concept": concept, "output": output_path},
        )
