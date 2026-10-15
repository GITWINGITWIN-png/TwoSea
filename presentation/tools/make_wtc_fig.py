"""ระนาบ WTC สไตล์ D สำหรับหน้า SQ06_S030 — วาดใหม่จากข้อมูลจริงของโครงงาน DSP (อ่านอย่างเดียว)

    PYTHONDONTWRITEBYTECODE=1 ../.venv/bin/python tools/make_wtc_fig.py

ทำไมไม่ใช้รูป fig03 ของรายงาน: viridis สีเข้มกลืนลูกศรเฟส (ผู้ใช้ 10-14) และมี 6 แผงเล็กจนอ่านไม่ออกบนจอ
ที่นี่: 2 แผงใหญ่ (อันดามัน × Niño3.4 · อ่าวไทย × Niño3.4) · พื้นขาว→น้ำเงิน · เส้นเกินเกณฑ์ 95% สีหมึก ·
ลูกศรดำเฉพาะในบริเวณที่เกินเกณฑ์ · นอกกรวยอิทธิพลจางลง
ข้อความอธิบาย (ชื่อแผง คำอธิบายสัญลักษณ์) อยู่ใน HTML ของหน้า — ในรูปมีแค่แกน
ผล: deck/public/plots/wtc_<ทะเล>.png (ไม่อยู่ใน git — สร้างใหม่ด้วยคำสั่งข้างบน)
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
import tomllib  # noqa: E402
DSP = (ROOT / Path(tomllib.loads((ROOT / "studio.toml").read_text())["sources"]["dsp_project"]).expanduser()).resolve()
OUT = ROOT / "deck" / "public" / "plots"

# สีของ theme D (deck/style.css)
INK, INK2, INK3 = "#12303D", "#3B5866", "#6B8794"
# R² 0 → 1: ขาว → ฟ้า → น้ำเงินอันดามัน → น้ำเงินเข้ม (ลูกศรดำยังเห็นชัดบนช่วงกลาง)
CMAP = LinearSegmentedColormap.from_list("d_blue", ["#FFFFFF", "#CFE3F3", "#7FB0DD", "#2F74C0", "#1B4B80"])

FONT = Path.home() / ".local/share/fonts/two-seas/Anuphan[wght].ttf"
if FONT.exists():
    font_manager.fontManager.addfont(str(FONT))
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=str(FONT)).get_name()


def panel(t, per, R2, phase, sig, coi, path):
    # 1700×330 px ที่ 100 dpi = ขนาดจริงบนจอ 1920×1080 (ตัวอักษร 17 pt ≈ 24 px)
    fig, ax = plt.subplots(figsize=(17, 3.3), dpi=100)
    fig.subplots_adjust(left=0.055, right=0.995, top=0.97, bottom=0.25)
    ax.contourf(t, per, R2, levels=np.linspace(0, 1, 11), cmap=CMAP)
    ax.contour(t, per, sig.astype(float), levels=[0.5], colors=INK, linewidths=2.4)

    # ลูกศรเฉพาะจุดที่เกินเกณฑ์และอยู่ในกรวย — ทุก 6 สเกล · ทุก 18 เดือน (ถี่กว่านี้ทับกันเป็นก้อน)
    T, P = np.meshgrid(t[::18], per[::6])
    ph, ok = phase[::6, ::18], sig[::6, ::18] & (P <= np.interp(T, t, coi))
    ax.quiver(T[ok], P[ok], np.cos(ph[ok]), np.sin(ph[ok]), scale=48, width=0.0024,
              headwidth=4, headlength=4.5, color="#0B1A22", zorder=5)

    # นอกกรวยอิทธิพล: ทาขาวโปร่งทับ + เส้นประขอบกรวย
    ax.fill_between(t, coi, per.max(), color="white", alpha=0.72, zorder=3)
    ax.plot(t, coi, "--", color=INK2, lw=1.6, zorder=4)

    ax.set_yscale("log", base=2)
    ax.set_ylim(per.max(), per.min())  # คาบสั้นอยู่บน
    ax.set_yticks([0.5, 1, 2, 4, 8, 16, 32])
    ax.set_yticklabels(["0.5", "1", "2", "4", "8", "16", "32"])
    ax.set_xlim(t.min(), t.max())
    ax.set_xticks(range(1960, 2030, 10))
    ax.tick_params(colors=INK2, labelsize=17, length=5)
    for s in ax.spines.values():
        s.set_color("#C9D6DC")
    ax.set_ylabel("คาบ (ปี)", color=INK2, fontsize=17)
    ax.set_xlabel("ปี", color=INK2, fontsize=16, labelpad=4)   # ผู้ใช้ 10-15: ทุกกราฟต้องมีชื่อแกน x และ y
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def main():
    r = np.load(DSP / "data" / "processed" / "wtc_q1.npz", allow_pickle=True)
    stations, indices = [str(s) for s in r["stations"]], [str(s) for s in r["indices"]]
    t, per, coi = r["t"], r["periods"], r["coi"]
    keep = per <= 40  # ตัดคาบยาวเกินข้อมูลออก (ส่วนนั้นอยู่นอกกรวยทั้งหมด)
    xi = indices.index("nino34")
    OUT.mkdir(parents=True, exist_ok=True)
    for name, st in (("andaman", "ko_taphao_noi"), ("gulf", "ko_lak")):
        si = stations.index(st)
        sig = r["sig"][si, xi] & r["valid"][si, xi]
        panel(t, per[keep], r["R2"][si, xi][keep].astype(float), r["phase"][si, xi][keep].astype(float),
              sig[keep], coi, OUT / f"wtc_{name}.png")
        print(f"{OUT / f'wtc_{name}.png'}")


if __name__ == "__main__":
    main()
