"""
Core simulation engine for KanJian.

Implements 1D heat equation simulation for magma eruption and solidification,
plus interactive visualization capabilities for math/science concepts.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import io
import base64


@dataclass
class SimulationState:
    """Represents the current state of a simulation."""

    temperature: np.ndarray
    solidified: np.ndarray
    time: float
    step: int


@dataclass
class VisualizationConfig:
    """Configuration for visualization output."""

    width: int = 800
    height: int = 600
    dpi: int = 100
    style: str = "dark_background"
    show_grid: bool = True
    color_map: str = "hot"


class MagmaSimulation:
    """
    1D magma eruption and solidification simulation.

    Simulates heat transfer using the heat equation:
        dT/dt = alpha * d²T/dx² - cooling

    Attributes:
        length: Number of spatial points
        dx: Spatial step size
        dt: Time step size
        alpha: Thermal diffusivity
        cooling_rate: Cooling rate constant
        solidification_temp: Temperature at which magma solidifies
    """

    def __init__(
        self,
        length: int = 100,
        dx: float = 1.0,
        dt: float = 0.1,
        alpha: float = 0.1,
        cooling_rate: float = 0.01,
        solidification_temp: float = 800.0,
        initial_temp: float = 1200.0,
        ambient_temp: float = 20.0,
    ):
        self.length = length
        self.dx = dx
        self.dt = dt
        self.alpha = alpha
        self.cooling_rate = cooling_rate
        self.solidification_temp = solidification_temp
        self.initial_temp = initial_temp
        self.ambient_temp = ambient_temp

        self.x = np.linspace(0, length * dx, length)
        self.T = np.ones(length) * initial_temp
        self.solidified = np.zeros(length, dtype=bool)
        self.time = 0.0
        self.step = 0

    def update(self) -> SimulationState:
        """
        Update the simulation state for one time step.

        Returns:
            SimulationState: Current state after update
        """
        d2T_dx2 = np.gradient(np.gradient(self.T, self.dx), self.dx)
        self.T += self.dt * (
            self.alpha * d2T_dx2 - self.cooling_rate * (self.T - self.ambient_temp)
        )

        self.solidified = self.T < self.solidification_temp
        self.T[0] = self.initial_temp
        self.time += self.dt
        self.step += 1

        return SimulationState(
            temperature=self.T.copy(),
            solidified=self.solidified.copy(),
            time=self.time,
            step=self.step,
        )

    def reset(self) -> None:
        """Reset simulation to initial state."""
        self.T = np.ones(self.length) * self.initial_temp
        self.solidified = np.zeros(self.length, dtype=bool)
        self.time = 0.0
        self.step = 0

    def get_state(self) -> SimulationState:
        """Get current simulation state without updating."""
        return SimulationState(
            temperature=self.T.copy(),
            solidified=self.solidified.copy(),
            time=self.time,
            step=self.step,
        )

    def run(self, steps: int) -> List[SimulationState]:
        """
        Run simulation for specified number of steps.

        Args:
            steps: Number of time steps to run

        Returns:
            List of SimulationState at each step
        """
        states = []
        for _ in range(steps):
            state = self.update()
            states.append(state)
        return states


class ConceptVisualizer:
    """
    Visualizer for math and science concepts.

    Supports interactive visualization of:
    - Pythagorean theorem
    - Circle area
    - Linear equations
    - Quadratic equations
    - Trigonometric functions
    """

    def __init__(self, config: Optional[VisualizationConfig] = None):
        self.config = config or VisualizationConfig()

    def visualize_pythagorean(self, a: float, b: float) -> Dict[str, Any]:
        """
        Generate visualization data for Pythagorean theorem.

        Args:
            a: Length of first leg
            b: Length of second leg

        Returns:
            Dict containing visualization data
        """
        c = np.sqrt(a**2 + b**2)
        return {
            "concept": "pythagorean",
            "parameters": {"a": a, "b": b, "c": c},
            "formula": "a² + b² = c²",
            "visualization": {
                "triangle": [[0, 0], [a, 0], [0, b]],
                "squares": {
                    "a": {"pos": [0, -a], "size": a},
                    "b": {"pos": [b, 0], "size": b},
                    "c": {"pos": [0, 0], "size": c, "rotated": True},
                },
            },
        }

    def visualize_circle_area(
        self, radius: float, segments: int = 16
    ) -> Dict[str, Any]:
        """
        Generate visualization data for circle area.

        Args:
            radius: Circle radius
            segments: Number of segments for visualization

        Returns:
            Dict containing visualization data
        """
        area = np.pi * radius**2
        angles = np.linspace(0, 2 * np.pi, segments + 1)
        points = [(radius * np.cos(a), radius * np.sin(a)) for a in angles]

        return {
            "concept": "circle_area",
            "parameters": {"radius": radius, "area": area},
            "formula": "A = πr²",
            "visualization": {
                "circle": {"center": [0, 0], "radius": radius},
                "segments": segments,
                "points": points,
            },
        }

    def visualize_linear_equation(
        self, slope: float, intercept: float, x_range: tuple = (-10, 10)
    ) -> Dict[str, Any]:
        """
        Generate visualization data for linear equation.

        Args:
            slope: Slope (m) of the line
            intercept: Y-intercept (b)
            x_range: Range of x values

        Returns:
            Dict containing visualization data
        """
        x = np.linspace(x_range[0], x_range[1], 100)
        y = slope * x + intercept

        return {
            "concept": "linear_equation",
            "parameters": {"slope": slope, "intercept": intercept},
            "formula": f"y = {slope}x + {intercept}",
            "visualization": {"x": x.tolist(), "y": y.tolist(), "x_range": x_range},
        }

    def visualize_quadratic(
        self, a: float, b: float, c: float, x_range: tuple = (-10, 10)
    ) -> Dict[str, Any]:
        """
        Generate visualization data for quadratic equation.

        Args:
            a: Coefficient of x²
            b: Coefficient of x
            c: Constant term
            x_range: Range of x values

        Returns:
            Dict containing visualization data
        """
        x = np.linspace(x_range[0], x_range[1], 100)
        y = a * x**2 + b * x + c

        discriminant = b**2 - 4 * a * c
        roots = []
        if discriminant >= 0:
            roots = [
                (-b + np.sqrt(discriminant)) / (2 * a),
                (-b - np.sqrt(discriminant)) / (2 * a),
            ]

        return {
            "concept": "quadratic",
            "parameters": {"a": a, "b": b, "c": c},
            "formula": f"y = {a}x² + {b}x + {c}",
            "roots": roots,
            "visualization": {"x": x.tolist(), "y": y.tolist(), "x_range": x_range},
        }

    def visualize_trig(
        self,
        func: str,
        amplitude: float = 1.0,
        frequency: float = 1.0,
        x_range: tuple = (0, 4 * np.pi),
    ) -> Dict[str, Any]:
        """
        Generate visualization data for trigonometric function.

        Args:
            func: Function name ('sin', 'cos', 'tan')
            amplitude: Amplitude of the wave
            frequency: Frequency of the wave
            x_range: Range of x values

        Returns:
            Dict containing visualization data
        """
        x = np.linspace(x_range[0], x_range[1], 200)

        if func.lower() == "sin":
            y = amplitude * np.sin(frequency * x)
        elif func.lower() == "cos":
            y = amplitude * np.cos(frequency * x)
        elif func.lower() == "tan":
            y = amplitude * np.tan(frequency * x)
            y = np.clip(y, -10, 10)
        else:
            raise ValueError(f"Unknown trig function: {func}")

        return {
            "concept": f"trig_{func}",
            "parameters": {
                "function": func,
                "amplitude": amplitude,
                "frequency": frequency,
            },
            "formula": f"y = {amplitude}·{func}({frequency}·x)",
            "visualization": {"x": x.tolist(), "y": y.tolist(), "x_range": x_range},
        }
