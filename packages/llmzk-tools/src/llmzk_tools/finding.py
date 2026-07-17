"""Shared finding dataclass and accumulator helper.

Used by doctor and review modules. Benchmark and update have different
finding/change shapes and keep their own dataclasses.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    level: str
    message: str


def add(findings: list[Finding], level: str, message: str) -> None:
    findings.append(Finding(level=level, message=message))
