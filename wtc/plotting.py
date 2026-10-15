from __future__ import annotations
import numpy as np


def use_thai_font(size: int = 10) -> str:
    import matplotlib as mpl
    from matplotlib import font_manager as fm

    have = {f.name for f in fm.fontManager.ttflist}
    for name in ("Noto Sans Thai", "Sarabun", "Loma", "Garuda", "TH Sarabun New"):
        if name in have:
            mpl.rcParams["font.family"] = [name, "DejaVu Sans"]
            mpl.rcParams["font.size"] = size
            mpl.rcParams["axes.unicode_minus"] = False
            return name
    return "ไม่พบฟอนต์ไทย — ตัวอักษรไทยในรูปจะเป็นกล่อง"


def period_axis(ax, periods, label: str = "คาบ (ปี)") -> None:
    ax.set_yscale("log", base=2)
    ticks = [v for v in (0.25, 0.5, 1, 2, 4, 8, 16, 32, 64)
             if periods.min() <= v <= periods.max()]
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"{v:g}" for v in ticks])
    ax.minorticks_off()
    ax.set_ylim(periods.max(), periods.min())
    ax.set_ylabel(label)


def plain_log_ticks(ax, axis: str = "both") -> None:
    from matplotlib.ticker import FuncFormatter, NullFormatter
    fmt = FuncFormatter(lambda val, _: f"{val:g}")
    axes = {"x": [ax.xaxis], "y": [ax.yaxis], "both": [ax.xaxis, ax.yaxis]}[axis]
    for a in axes:
        a.set_major_formatter(fmt)
        a.set_minor_formatter(NullFormatter())


def plot_coherence(ax, t, periods, R2, coi, phase=None, *, title="",
                   levels=None, arrow_step=(6, 24), sig_mask=None):
    import matplotlib.pyplot as plt

    levels = np.linspace(0, 1, 11) if levels is None else levels
    cf = ax.contourf(t, periods, R2, levels=levels, cmap="viridis", extend="neither")

    if sig_mask is not None:
        ax.contour(t, periods, sig_mask.astype(float), levels=[0.5],
                   colors="white", linewidths=1.6)

    ax.fill_between(t, coi, periods.max(), color="white", alpha=0.7, zorder=3)
    ax.plot(t, coi, "k--", lw=1.2, zorder=4)

    if phase is not None:
        si, ti = arrow_step
        T, P = np.meshgrid(t[::ti], periods[::si])
        ph = phase[::si, ::ti]
        inside = P <= np.interp(T, t, coi)
        u, v = np.where(inside, np.cos(ph), np.nan), np.where(inside, np.sin(ph), np.nan)
        ax.quiver(T, P, u, v, scale=25, width=0.0018, color="k", zorder=5)

    period_axis(ax, periods)
    ax.set_xlabel("ปี")
    ax.set_title(title)
    return cf


def plot_filter_response(ax, design, tides: dict | None = None, *, fs_out: float = 1.0):
    f, H = design.response()
    db = 20 * np.log10(np.maximum(H, 1e-12))
    ax.plot(f, db, lw=1.1, color="C0", label=f"FIR Kaiser {design.numtaps} taps")
    ax.axvspan(0, design.f_pass, color="C2", alpha=0.12, label=f"passband ≤ {design.f_pass:g} cpd")
    ax.axvspan(design.f_stop, f.max(), color="C3", alpha=0.08,
               label=f"stopband ≥ {design.f_stop:g} cpd")
    ax.hlines(-design.atten_db, design.f_stop, f.max(), colors="C3", ls="--", lw=1.2,
              label=f"สเปก −{design.atten_db:g} dB")
    ax.axvline(fs_out / 2, color="k", ls=":", lw=1, label=f"Nyquist ใหม่ {fs_out / 2:g} cpd")
    if tides:
        for name, fr in tides.items():
            ax.axvline(fr, color="0.5", lw=0.6)
            ax.text(fr, 3, name, rotation=90, fontsize=7, ha="center", va="bottom", color="0.3")
    ax.set_xlim(0, min(2.2, f.max()))
    ax.set_ylim(-130, 12)
    ax.set_xlabel("ความถี่ (รอบ/วัน)")
    ax.set_ylabel("|H(f)| (dB)")
    ax.legend(fontsize=7, loc="lower left")


def plot_series(ax, t, y, mask=None, *, label="", color="C0"):
    ax.plot(t, y, lw=0.7, color=color, label=label)
    if mask is not None and mask.any():
        ax.plot(t[mask], y[mask], ".", ms=2.5, color="crimson",
                label=f"ของเติม {mask.sum()} จุด ({mask.mean():.1%})")
    ax.set_xlabel("ปี")
    if label:
        ax.legend(loc="upper left", fontsize=8)
