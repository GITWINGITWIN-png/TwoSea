"""แผนที่พื้นสไตล์ D จากแนวชายฝั่งจริง (Natural Earth 1:50m ผ่าน cartopy) สำหรับหน้า SQ08_S020 / SQ08_S030

    PYTHONDONTWRITEBYTECODE=1 ../.venv/bin/python tools/make_basemap.py

ทำไม: แผนที่วาดมือเดิมต่างจากของจริงจนมองไม่ออกว่าคือที่ไหน (ผู้ใช้ 10-14)
ภาพเป็นพิกัดแบบ lon/lat ตรง ๆ (PlateCarree) ทั้งรูปไม่มีขอบ → หน้า deck แปลงพิกัดเป็นพิกเซลได้ด้วยสูตรเส้นตรง
    x = (lon − lon0) / (lon1 − lon0) · W      y = (lat1 − lat) / (lat1 − lat0) · H
ลูกศร ป้าย และแอนิเมชันอยู่ใน SVG/HTML ของหน้า (ต้องคลิกทีละขั้น) — รูปมีแค่ทะเล แผ่นดิน และเส้นศูนย์สูตร
ผล: deck/public/plots/map_<ชื่อ>.png (ไม่อยู่ใน git)
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import cartopy.crs as ccrs  # noqa: E402
import cartopy.feature as cfeature  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "deck" / "public" / "plots"

SEA, LAND, COAST, EQUATOR = "#EEF5F9", "#D3DBC8", "#98A68B", "#8FA1AB"

# ทะเลตามความลึก (Natural Earth bathymetry 200 / 1000 / 3000 ม.) — ตื้น = ฟ้าอ่อน · ลึก = น้ำเงินเข้มขึ้น
DEPTH = [("K_200", "#D6E8F3"), ("J_1000", "#BCD6EA"), ("H_3000", "#9DC1E0")]
SHALLOW = "#EAF4FA"   # ไหล่ทวีป (< 200 ม.) — อ่าวไทยทั้งแอ่งอยู่ในชั้นนี้

# ชื่อ: (lon0, lon1, lat0, lat1, กว้าง px, สูง px[, ทะเลตามความลึก]) — สัดส่วนพิกเซลเท่ากับสัดส่วนองศา ไม่ให้แผนที่ยืด
MAPS = {
    "s82": (80, 132, -10, 16, 1600, 800),   # อันดามัน: มหาสมุทรอินเดีย → ทะเลทวีป → ขอบแปซิฟิก
    "s83": (92, 118, -3, 16, 832, 608),     # อ่าวไทย: อันดามัน · ช่องแคบมะละกา · ทะเลจีนใต้ (ลูซอนอยู่นอกขอบขวา)
    "s01": (92, 105, 4, 14, 1040, 800, True),       # SQ01_S010 ใกล้: สองสถานี · ทะเลตามความลึก
    "s01w": (40, 180, -38, 37, 1493, 800, True),    # SQ01_S010 ไกล: มหาสมุทรอินเดีย → แปซิฟิก
}


def render(name, lon0, lon1, lat0, lat1, w, h, depth=False):
    fig = plt.figure(figsize=(w / 100, h / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.PlateCarree())
    ax.set_extent([lon0, lon1, lat0, lat1], crs=ccrs.PlateCarree())
    ax.set_facecolor(SHALLOW if depth else SEA)
    if depth:
        # แต่ละชั้นคือพื้นที่ที่ลึกกว่าค่านั้น — วาดจากตื้นไปลึก ชั้นลึกทับชั้นตื้น
        for key, colour in DEPTH:
            ax.add_feature(cfeature.NaturalEarthFeature("physical", f"bathymetry_{key}", "10m"),
                           facecolor=colour, edgecolor="none")
    ax.add_feature(cfeature.LAND.with_scale("50m"), facecolor=LAND, edgecolor=COAST, linewidth=1.4)
    ax.plot([lon0, lon1], [0, 0], "--", color=EQUATOR, lw=1.6, transform=ccrs.PlateCarree())
    ax.axis("off")
    path = OUT / f"map_{name}.png"
    fig.savefig(path, facecolor=SEA)
    plt.close(fig)
    print(path, f"{w}×{h}", f"lon {lon0}–{lon1}", f"lat {lat0}–{lat1}")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, spec in MAPS.items():
        render(name, *spec)
