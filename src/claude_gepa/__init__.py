"""Minimal GEPA + Claude Managed Agents prototype."""

from .candidate import DEFAULT_SEED_CANDIDATE, CandidateBundle
from .optimizer import optimize_demo

__all__ = ["CandidateBundle", "DEFAULT_SEED_CANDIDATE", "optimize_demo"]
