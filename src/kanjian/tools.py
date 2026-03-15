"""
OpenAI Function-Calling tools for KanJian.

Provides TOOLS list and dispatch function for LLM agent integration.
"""

from __future__ import annotations

import json
from typing import Any, Dict


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "kanjian_simulate",
            "description": "Run a simulation for a math or science concept (magma eruption, Pythagorean theorem, circle area, linear/quadratic equations, trig functions)",
            "parameters": {
                "type": "object",
                "properties": {
                    "concept": {
                        "type": "string",
                        "description": "Concept to simulate: magma, pythagorean, circle, linear, quadratic, or trig",
                        "enum": ["magma", "pythagorean", "circle", "linear", "quadratic", "trig"],
                    },
                    "steps": {
                        "type": "integer",
                        "description": "Number of simulation steps (default: 100)",
                        "default": 100,
                    },
                    "params": {
                        "type": "object",
                        "description": "Concept-specific parameters (e.g., {a: 3, b: 4} for pythagorean)",
                    },
                },
                "required": ["concept"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "kanjian_visualize",
            "description": "Generate interactive visualization for a math or science concept and optionally save to file",
            "parameters": {
                "type": "object",
                "properties": {
                    "concept": {
                        "type": "string",
                        "description": "Concept to visualize: magma, pythagorean, circle, linear, quadratic, or trig",
                        "enum": ["magma", "pythagorean", "circle", "linear", "quadratic", "trig"],
                    },
                    "params": {
                        "type": "object",
                        "description": "Concept-specific parameters",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Optional file path to save visualization as PNG",
                    },
                },
                "required": ["concept"],
            },
        },
    },
]


def dispatch(name: str, arguments: Dict[str, Any] | str) -> Dict[str, Any]:
    """
    Dispatch tool calls to appropriate KanJian functions.

    Args:
        name: Tool name (kanjian_simulate or kanjian_visualize)
        arguments: Tool arguments as dict or JSON string

    Returns:
        Tool result as dictionary

    Raises:
        ValueError: If unknown tool name
    """
    if isinstance(arguments, str):
        arguments = json.loads(arguments)

    if name == "kanjian_simulate":
        from kanjian.api import kanjian_simulate

        result = kanjian_simulate(
            concept=arguments.get("concept", "magma"),
            steps=arguments.get("steps", 100),
            params=arguments.get("params"),
        )
        return result.to_dict()

    elif name == "kanjian_visualize":
        from kanjian.api import kanjian_visualize

        result = kanjian_visualize(
            concept=arguments.get("concept"),
            params=arguments.get("params"),
            output_path=arguments.get("output_path"),
        )
        return result.to_dict()

    else:
        raise ValueError(f"Unknown tool: {name}. Available: kanjian_simulate, kanjian_visualize")
