import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from roles.service.filter_plugins import versioning


def test_version_bounds_are_semantic():
    floor = versioning.version_floor("10.11")
    ceiling = versioning.version_ceiling("10.11")
    assert floor == "10.11.0"
    assert ceiling == "10.12.0"
    assert versioning.version_in_range("10.11.5", floor, ceiling)
    assert not versioning.version_in_range("10.12.0", floor, ceiling)
