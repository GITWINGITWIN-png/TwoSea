# Sea Level × Wavelet Coherence — ทะเลไทยสองฝั่ง

โครงงานวิชา 01204496 · ทำซ้ำ [Song & Chen (2022)](https://doi.org/10.2166/wcc.2022.180) (WTC + MWC) กับระดับน้ำทะเลอ่าวไทยและอันดามัน

📄 **รายงาน: [`reports/final/report.pdf`](reports/final/report.pdf)** (ต้นฉบับ `report.tex` · `report.md`)

## รันเอง

ต้องมี [uv](https://docs.astral.sh/uv/) และ Python ≥ 3.12

```bash
uv sync

# ข้อมูล
uv run python scripts/fetch_data.py
uv run python scripts/check_data.py
uv run python scripts/build_series.py

# วิเคราะห์
uv run python scripts/verify_decimation.py
uv run python scripts/run_wtc.py
uv run python scripts/run_mwc_null.py
uv run python scripts/run_mwc.py
uv run python scripts/null_control.py --nrep 1000
uv run python scripts/sensitivity.py --all

# รูป + รายงาน
uv run python scripts/make_figures.py
uv run --group report python scripts/make_infographics.py
cd reports/final && latexmk -xelatex report.tex
```

ทดสอบ: `uv run --group dev pytest tests` · โน้ตบุ๊ก: `uv run --group dev --group reference python scripts/run_notebooks.py`
