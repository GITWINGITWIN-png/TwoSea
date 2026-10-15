#!/usr/bin/env python3
from __future__ import annotations
import sys, time
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

NB_DIR = Path(__file__).resolve().parent.parent / "notebooks"


def run_one(path: Path) -> bool:
    nb = nbformat.read(path, as_version=4)
    t0 = time.perf_counter()
    try:
        NotebookClient(nb, timeout=1800, kernel_name="python3",
                       resources={"metadata": {"path": str(NB_DIR)}}).execute()
    except CellExecutionError as exc:
        nbformat.write(nb, path)
        print(f"  ❌ {path.name}  พังที่เซลล์:\n{str(exc)[:1500]}")
        return False
    nbformat.write(nb, path)
    print(f"  ✅ {path.name}  {len(nb.cells)} เซลล์ · {time.perf_counter() - t0:.0f} วินาที")
    return True


def main() -> int:
    prefix = sys.argv[1] if len(sys.argv) > 1 else ""
    books = sorted(p for p in NB_DIR.glob(f"{prefix}*.ipynb"))
    if not books:
        print(f"ไม่พบโน้ตบุ๊กที่ขึ้นต้นด้วย {prefix!r}")
        return 1
    ok = all([run_one(p) for p in books])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
