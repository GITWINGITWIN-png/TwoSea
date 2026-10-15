from __future__ import annotations
import numpy as np

from .multirate import decimal_year_to_month

PSMSL_EXCLUDE: dict[str, dict[str, str]] = {
    "ko_taphao_noi": {
        "1985-10": "PSMSL 7469 mm ขณะที่เดือนข้างเคียง 7131/7186 (กระโดด ~+300 แล้วกลับ) · "
                   "UHSLC รายชั่วโมงผ่านโซ่ Q7 และ UHSLC รายวันต่อเนื่องเรียบและตรงกันเอง "
                   "(2319.7/2387.6/2372.0 เทียบ 2319.8/2387.8/2372.2) ⇒ ต่างจาก PSMSL −254 mm",
        "1987-06": "PSMSL 7498 mm ขณะที่เดือนข้างเคียง 7150/7248 · UHSLC สองผลิตภัณฑ์ต่อเนื่อง "
                   "(2337.5/2411.0/2433.3 เทียบ 2337.6/2410.9/2433.4) ⇒ ต่างจาก PSMSL −260 mm",
    },
}


def apply_exclusions(station: str, t: np.ndarray, v: np.ndarray
                     ) -> tuple[np.ndarray, list[str]]:
    rules = PSMSL_EXCLUDE.get(station, {})
    out = np.asarray(v, float).copy()
    if not rules:
        return out, []
    months = decimal_year_to_month(t)
    done = []
    for month in rules:
        hit = np.flatnonzero(months == np.datetime64(month))
        if len(hit) != 1 or not np.isfinite(out[hit[0]]):
            raise ValueError(f"{station} {month}: ไม่พบค่าที่จะตัดในไฟล์ — "
                             "แหล่งข้อมูลอาจแก้ไปแล้ว ต้องทบทวนรายการใน wtc/qc.py")
        out[hit[0]] = np.nan
        done.append(month)
    return out, done
