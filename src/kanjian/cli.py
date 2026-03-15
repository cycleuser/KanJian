"""
Command-line interface for KanJian.

Implements unified CLI flags: -V/--version, -v/--verbose, -q/--quiet, --json, -o/--output
"""

from __future__ import annotations

import argparse
import sys
import json
import logging
from pathlib import Path

from kanjian import __version__
from kanjian.api import kanjian_simulate, kanjian_visualize


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Configure logging based on verbosity flags."""
    if quiet:
        logging.getLogger().setLevel(logging.WARNING)
    elif verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser with unified flags."""
    parser = argparse.ArgumentParser(
        prog="kanjian",
        description="KanJian - Interactive visual explanations for math and science concepts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  kanjian simulate --concept magma --steps 100
  kanjian visualize --concept pythagorean --param a=3 --param b=4
  kanjian visualize --concept linear --param slope=2 --param intercept=1 -o output.png
  kanjian --version
  kanjian --help
        """,
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"kanjian {__version__}",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress non-essential output",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    simulate_parser = subparsers.add_parser(
        "simulate",
        help="Run a simulation for a concept",
    )
    simulate_parser.add_argument(
        "--concept",
        type=str,
        default="magma",
        choices=["magma", "pythagorean", "circle", "linear", "quadratic", "trig"],
        help="Concept to simulate (default: magma)",
    )
    simulate_parser.add_argument(
        "--steps",
        type=int,
        default=100,
        help="Number of simulation steps (default: 100)",
    )
    simulate_parser.add_argument(
        "--param",
        action="append",
        dest="params",
        metavar="KEY=VALUE",
        help="Concept parameter (can be used multiple times)",
    )
    simulate_parser.set_defaults(func=run_simulate)

    visualize_parser = subparsers.add_parser(
        "visualize",
        help="Generate visualization for a concept",
    )
    visualize_parser.add_argument(
        "--concept",
        type=str,
        required=True,
        choices=["magma", "pythagorean", "circle", "linear", "quadratic", "trig"],
        help="Concept to visualize",
    )
    visualize_parser.add_argument(
        "--param",
        action="append",
        dest="params",
        metavar="KEY=VALUE",
        help="Concept parameter (can be used multiple times)",
    )
    visualize_parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output path for visualization (PNG)",
    )
    visualize_parser.set_defaults(func=run_visualize)

    return parser


def parse_params(param_list: list[str] | None) -> dict:
    """Parse parameter list into dictionary."""
    params = {}
    if param_list:
        for param in param_list:
            if "=" in param:
                key, value = param.split("=", 1)
                try:
                    params[key] = float(value) if "." in value else int(value)
                except ValueError:
                    params[key] = value
    return params


def run_simulate(args: argparse.Namespace) -> int:
    """Execute simulate command."""
    params = parse_params(args.params)
    result = kanjian_simulate(
        concept=args.concept,
        steps=args.steps,
        params=params,
    )

    if args.json_output:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.success:
            print(f"✓ Simulation completed: {result.data.get('concept', 'unknown')}")
            print(f"  Steps: {result.data.get('steps', 0)}")
            if result.data.get("time"):
                print(f"  Final time: {result.data['time']:.2f}")
        else:
            print(f"✗ Simulation failed: {result.error}", file=sys.stderr)
            return 1

    return 0


def run_visualize(args: argparse.Namespace) -> int:
    """Execute visualize command."""
    params = parse_params(args.params)
    result = kanjian_visualize(
        concept=args.concept,
        params=params,
        output_path=args.output,
    )

    if args.json_output:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.success:
            if args.output:
                print(f"✓ Visualization saved to: {args.output}")
            else:
                print(f"✓ Visualization generated: {args.concept}")
                if result.data.get("concept_data"):
                    cd = result.data["concept_data"]
                    print(f"  Formula: {cd.get('formula', 'N/A')}")
        else:
            print(f"✗ Visualization failed: {result.error}", file=sys.stderr)
            return 1

    return 0


def main(argv: list[str] | None = None) -> int:
    """Main entry point for CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    setup_logging(verbose=args.verbose, quiet=args.quiet)

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
