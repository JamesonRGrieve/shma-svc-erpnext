"""Version comparison helpers for ERPNext service validation."""

from __future__ import annotations

from packaging import version


def _split_major_minor(value: str) -> tuple[int, int]:
    major_str, minor_str, *_ = (value or "0").split(".") + ["0", "0"]
    try:
        major = int(major_str)
        minor = int(minor_str)
    except ValueError as exc:  # pragma: no cover
        raise ValueError(f"Invalid major.minor version: {value!r}") from exc
    return major, minor


def version_floor(value: str) -> str:
    """Return the lowest version accepted for the given major.minor string."""
    major, minor = _split_major_minor(value)
    return str(version.Version(f"{major}.{minor}.0"))


def version_ceiling(value: str) -> str:
    """Return the exclusive upper bound for a major.minor requirement."""
    major, minor = _split_major_minor(value)
    next_minor = minor + 1
    return str(version.Version(f"{major}.{next_minor}.0"))


def version_in_range(current: str, floor: str, ceiling: str) -> bool:
    """Check whether *current* is within the [floor, ceiling) range."""
    current_version = version.parse(str(current))
    floor_version = version.parse(str(floor))
    ceiling_version = version.parse(str(ceiling))
    return floor_version <= current_version < ceiling_version


def filters() -> dict[str, object]:
    """Expose filters to Ansible."""
    return {
        "version_floor": version_floor,
        "version_ceiling": version_ceiling,
        "version_in_range": version_in_range,
    }
