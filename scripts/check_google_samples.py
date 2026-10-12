"""Run the OKF tools against every bundle of Google's official samples repo.

python scripts/check_google_samples.py <path to open-knowledge-format clone>
"""

import sys
from pathlib import Path

from astromesh_okf import Bundle


def check(d: Path) -> bool:
    try:
        b = Bundle(d)
        res = b.find(include_deprecated=True, limit=100)
        assert res["skipped_invalid"] == 0, f"{res['skipped_invalid']} invalid concepts"
        b.index("/")
        for r in res["results"]:
            b.read(r["id"])
        print(f"{d.name}: {len(res['results'])} concepts OK")
        return True
    except Exception as e:  # noqa: BLE001
        print(f"{d.name}: FAIL {e!r}")
        return False


def main(repo: str) -> int:
    dirs = sorted(p for p in (Path(repo) / "bundles").iterdir() if p.is_dir())
    oks = list(map(check, dirs))  # no short-circuit: report every bundle
    return 0 if all(oks) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
