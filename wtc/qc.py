"""ค่าที่ตัดทิ้งเพราะพิสูจน์แล้วว่าผิด — **ทุกรายการต้องมีหลักฐานกำกับ**

ไฟล์นี้เป็นที่เดียวในโปรเจกต์ที่อนุญาตให้ทำให้ค่าในข้อมูลดิบหายไป
ทั้ง scripts/build_series.py และ notebooks/01_data.ipynb เรียกรายการเดียวกันนี้
⇒ ถ้าจะเพิ่มหรือถอนรายการ ให้แก้ที่นี่ที่เดียว แล้วรันทั้งสายใหม่

หลักที่ใช้ตัดสิน: ค่าหนึ่งจะถูกตัดได้ก็ต่อเมื่อ **แหล่งอิสระอย่างน้อยสองแหล่งเห็นตรงกัน**
ว่าค่านั้นผิด ไม่ใช่แค่ "ดูแปลก" — ค่าที่ดูแปลกแต่ไม่มีหลักฐานต้องเก็บไว้ เพราะสัญญาณ
ภูมิอากาศที่รุนแรงจริงก็ดูแปลกได้เหมือนกัน

ค่าที่ตัดจะกลายเป็น NaN แล้ว preprocess.fill_gaps จัดการตามกฎเดิม
(ช่องว่าง 1 เดือน ⇒ interp เชิงเส้น) และ **ติด mask ว่าเป็นของเติม** เหมือนช่องว่างอื่น

ตัดสินใจเมื่อ 2026-09-30 (หลัง Q7) — ดู notebooks/03_multirate.ipynb §7
"""
from __future__ import annotations
import numpy as np

from .multirate import decimal_year_to_month

# สถานี -> {เดือน: หลักฐาน}
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
    """คืน (ค่าที่ตัดแล้ว, รายการเดือนที่ถูกตัดจริง)

    ตรวจด้วยว่าทุกเดือนในรายการมีอยู่ในไฟล์และยังไม่เป็น NaN — ถ้าแหล่งข้อมูลอัปเดตแล้ว
    แก้ค่านั้นไปเองหรือเดือนนั้นหายไป เราต้องรู้ ไม่ใช่ตัดอากาศเงียบ ๆ
    """
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
