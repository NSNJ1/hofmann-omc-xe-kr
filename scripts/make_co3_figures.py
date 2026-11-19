from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
MATRIX_SOURCE = REPO / "data" / "source_tables" / "co3"
DOS_SOURCE = MATRIX_SOURCE / "co3_spin_resolved_dos_long.csv"
OUTPUTS = REPO / "figures" / "rebuilt" / "co3"
QA = OUTPUTS / "qa"
for directory in (OUTPUTS, QA):
    directory.mkdir(parents=True, exist_ok=True)


INK = "#111111"
GRAY = "#6F6F6F"
LIGHT_GRAY = "#D9D9D9"
PALE_GRAY = "#EFEFEF"
BLUE = "#0066CC"
LIGHT_BLUE = "#C9E0F7"
RED = "#D7191C"
LIGHT_RED = "#F6D3D3"
TEAL = "#008C95"
WHITE = "#FFFFFF"

ORBITALS = ("dxy", "dyz", "dz2", "dxz", "dx2-y2")
ORBITAL_DISPLAY = {
    "dxy": r"$\mathrm{d}_{\mathrm{xy}}$",
    "dyz": r"$\mathrm{d}_{\mathrm{yz}}$",
    "dz2": r"$\mathrm{d}_{\mathrm{z}^{2}}$",
    "dxz": r"$\mathrm{d}_{\mathrm{xz}}$",
    "dx2-y2": r"$\mathrm{d}_{\mathrm{x}^{2}-\mathrm{y}^{2}}$",
}
ORBITAL_CAPTION = {
    "dxy": "four lobes in xy",
    "dyz": "four lobes in yz",
    "dz2": "two lobes + ring",
    "dxz": "four lobes in xz",
    "dx2-y2": "lobes along x/y",
}


plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.size": 7.1,
        "axes.titlesize": 8.2,
        "axes.titleweight": "bold",
        "axes.labelsize": 7.2,
        "xtick.labelsize": 6.3,
        "ytick.labelsize": 6.3,
        "legend.fontsize": 6.1,
        "axes.linewidth": 0.9,
        "legend.frameon": False,
        "mathtext.fontset": "dejavusans",
        "mathtext.default": "regular",
        "figure.facecolor": WHITE,
        "axes.facecolor": WHITE,
        "savefig.facecolor": WHITE,
    }
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def style_box_axis(ax: plt.Axes) -> None:
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.9)
        spine.set_color(INK)
    ax.tick_params(colors=INK, direction="out", length=2.7, width=0.8, pad=2.2)
    ax.grid(False)


def panel_letter(ax: plt.Axes, letter: str, *, x: float = -0.13, y: float = 1.02) -> None:
    ax.text(
        x,
        y,
        letter,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=9.2,
        fontweight="bold",
        color=INK,
        clip_on=False,
    )


def panel_title(ax: plt.Axes, title: str) -> None:
    ax.set_title(title, pad=4.0, fontsize=8.1, fontweight="bold", color=INK)


def save_publication(fig: plt.Figure, stem: str) -> dict[str, object]:
    base = OUTPUTS / stem
    fig.savefig(base.with_suffix(".svg"), facecolor=WHITE, transparent=False)
    fig.savefig(base.with_suffix(".pdf"), facecolor=WHITE, transparent=False)
    fig.savefig(base.with_suffix(".png"), dpi=300, facecolor=WHITE)
    fig.savefig(
        base.with_suffix(".tiff"),
        dpi=600,
        facecolor=WHITE,
        pil_kwargs={"compression": "tiff_lzw"},
    )
    plt.close(fig)
    return {
        "stem": stem,
        "svg": str(base.with_suffix(".svg")),
        "pdf": str(base.with_suffix(".pdf")),
        "png": str(base.with_suffix(".png")),
        "tiff": str(base.with_suffix(".tiff")),
    }


def orbital_value(name: str, x: np.ndarray, y: np.ndarray, z: np.ndarray) -> np.ndarray:
    if name == "dxy":
        return 2.0 * x * y
    if name == "dyz":
        return 2.0 * y * z
    if name == "dz2":
        return (3.0 * z * z - 1.0) / 2.0
    if name == "dxz":
        return 2.0 * x * z
    if name == "dx2-y2":
        return x * x - y * y
    raise ValueError(name)


def draw_orbital(ax: plt.Axes, name: str) -> None:
    theta = np.linspace(0.0, np.pi, 55)
    phi = np.linspace(0.0, 2.0 * np.pi, 80)
    theta, phi = np.meshgrid(theta, phi)
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    value = orbital_value(name, x, y, z)
    scale = float(np.max(np.abs(value)))
    radius = 0.22 + 0.78 * np.abs(value) / scale
    norm = mpl.colors.TwoSlopeNorm(vmin=-scale, vcenter=0.0, vmax=scale)
    facecolors = mpl.colormaps["coolwarm"](norm(value))
    ax.plot_surface(
        radius * x,
        radius * y,
        radius * z,
        facecolors=facecolors,
        linewidth=0,
        antialiased=True,
        shade=False,
    )
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)
    ax.view_init(elev=18, azim=35)
    ax.set_axis_off()
    ax.set_title(ORBITAL_DISPLAY[name], fontsize=8.3, pad=-1)
    ax.text2D(
        0.5,
        0.01,
        ORBITAL_CAPTION[name],
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=5.7,
        color=GRAY,
    )


def matrix_from_rows(
    rows: list[dict[str, str]],
    state: str,
    atom: str,
    spin: str,
) -> np.ndarray:
    matrix = np.zeros((5, 5), dtype=float)
    lookup = {name: index for index, name in enumerate(ORBITALS)}
    for row in rows:
        if row["state"] == state and row["atom"] == atom and row["spin"] == spin:
            matrix[lookup[row["row_orbital"]], lookup[row["column_orbital"]]] = float(row["value"])
    return matrix


def draw_matrix_cells(ax: plt.Axes, matrix: np.ndarray, *, title: str, vmax: float) -> None:
    image = ax.imshow(
        matrix,
        cmap="RdBu_r",
        vmin=-vmax,
        vmax=vmax,
        interpolation="nearest",
        aspect="equal",
    )
    ax.set_xticks(range(5))
    ax.set_yticks(range(5))
    ax.set_xticklabels([ORBITAL_DISPLAY[item] for item in ORBITALS], rotation=35, ha="right")
    ax.set_yticklabels([ORBITAL_DISPLAY[item] for item in ORBITALS])
    ax.tick_params(length=0, pad=2)
    for row in range(5):
        for column in range(5):
            value = matrix[row, column]
            color = WHITE if abs(value) > 0.46 * vmax else INK
            ax.text(
                column,
                row,
                f"{value:.2f}",
                ha="center",
                va="center",
                fontsize=5.05,
                color=color,
            )
    ax.set_title(title, pad=4.0, fontsize=8.0, fontweight="bold")
    style_box_axis(ax)
    return image


def draw_matrix_anatomy(ax: plt.Axes) -> None:
    # Keep the custom orbital labels inside the axes so the row-axis title
    # cannot collide with the tick labels at the left edge.
    ax.set_xlim(-1.00, 5.65)
    ax.set_ylim(-1.45, 5)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for row in range(5):
        for column in range(5):
            face = LIGHT_BLUE if row == column else LIGHT_RED
            ax.add_patch(
                Rectangle(
                    (column, 4 - row),
                    1,
                    1,
                    facecolor=face,
                    edgecolor=WHITE,
                    linewidth=1.2,
                )
            )
            label = rf"$n_{{{row + 1}{column + 1}}}$"
            ax.text(column + 0.5, 4.5 - row, label, ha="center", va="center", fontsize=5.8)
    for column, name in enumerate(ORBITALS):
        ax.text(
            column + 0.5,
            -0.10,
            ORBITAL_DISPLAY[name],
            ha="center",
            va="top",
            fontsize=5.9,
            rotation=28,
        )
    for row, name in enumerate(ORBITALS):
        ax.text(
            -0.08,
            4.5 - row,
            ORBITAL_DISPLAY[name],
            ha="right",
            va="center",
            fontsize=5.9,
        )
    ax.text(2.5, -1.18, r"column orbital $m'$", ha="center", va="top", fontsize=6.3)
    ax.text(-0.82, 2.5, r"row orbital $m$", ha="center", va="center", rotation=90, fontsize=6.3)
    ax.text(
        5.08,
        4.5,
        "5 diagonal entries\norbital populations",
        ha="left",
        va="center",
        fontsize=6.0,
        color=BLUE,
    )
    ax.text(
        5.08,
        2.5,
        "20 off-diagonal entries\nmixing and phase",
        ha="left",
        va="center",
        fontsize=6.0,
        color=RED,
    )
    panel_title(ax, "Anatomy of one spin matrix")
    panel_letter(ax, "f", x=-0.05, y=1.08)
    style_box_axis(ax)


def draw_spin_pair(ax: plt.Axes) -> None:
    ax.set_xlim(0, 2.3)
    ax.set_ylim(0, 2.2)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    panels = (
        (0.08, 0.65, BLUE, LIGHT_BLUE, r"$\uparrow$ spin-up"),
        (1.25, 0.65, RED, LIGHT_RED, r"$\downarrow$ spin-down"),
    )
    for origin_x, origin_y, edge, fill, label in panels:
        ax.text(
            origin_x + 0.42,
            origin_y + 0.92,
            label,
            ha="center",
            va="bottom",
            fontsize=6.8,
            fontweight="bold",
            color=edge,
        )
        for row in range(5):
            for column in range(5):
                color = fill if row == column else WHITE
                ax.add_patch(
                    Rectangle(
                        (origin_x + column * 0.17, origin_y + (4 - row) * 0.17),
                        0.17,
                        0.17,
                        facecolor=color,
                        edgecolor=edge if row == column else LIGHT_GRAY,
                        linewidth=0.55,
                    )
                )
    ax.text(
        1.15,
        0.25,
        "full electronic state = two 5×5 matrices",
        ha="center",
        va="center",
        fontsize=6.8,
        fontweight="bold",
    )
    panel_title(ax, "One state needs both spin channels")
    panel_letter(ax, "g", x=-0.05, y=1.08)
    style_box_axis(ax)


def mechanism_1() -> dict[str, object]:
    fig = plt.figure(figsize=(7.2, 6.65))
    grid = fig.add_gridspec(
        3,
        5,
        height_ratios=(1.0, 1.12, 0.68),
        left=0.035,
        right=0.975,
        bottom=0.045,
        top=0.90,
        wspace=0.10,
        hspace=0.30,
    )
    for index, name in enumerate(ORBITALS):
        ax = fig.add_subplot(grid[0, index], projection="3d")
        draw_orbital(ax, name)
        ax.text2D(
            -0.02,
            0.97,
            chr(ord("a") + index),
            transform=ax.transAxes,
            fontsize=9.2,
            fontweight="bold",
        )

    ax_matrix = fig.add_subplot(grid[1, :3])
    draw_matrix_anatomy(ax_matrix)
    ax_spin = fig.add_subplot(grid[1, 3:])
    draw_spin_pair(ax_spin)

    ax_note = fig.add_subplot(grid[2, :])
    ax_note.axis("off")
    ax_note.text(
        0.0,
        0.86,
        "diagonal",
        fontsize=7.3,
        fontweight="bold",
        color=BLUE,
        va="top",
    )
    ax_note.text(
        0.0,
        0.46,
        "Orbital population.\nUseful as a label, not enough\nfor state identity.",
        fontsize=5.9,
        va="top",
    )
    ax_note.text(
        0.35,
        0.86,
        "off-diagonal",
        fontsize=7.3,
        fontweight="bold",
        color=RED,
        va="top",
    )
    ax_note.text(
        0.35,
        0.46,
        "Orbital mixing and phase.\nSimilar diagonal counts can\nhide different matrices.",
        fontsize=5.9,
        va="top",
    )
    ax_note.text(
        0.69,
        0.86,
        "both spins",
        fontsize=7.3,
        fontweight="bold",
        color=INK,
        va="top",
    )
    ax_note.text(
        0.69,
        0.46,
        "One physical Co state needs\nspin-up and spin-down\nmatrices together.",
        fontsize=5.9,
        va="top",
    )
    fig.suptitle(
        "A spin-resolved Co 3d state needs two 5×5 matrices",
        x=0.035,
        y=0.965,
        ha="left",
        fontsize=10.5,
        fontweight="bold",
    )
    fig.text(
        0.035,
        0.925,
        "Orbital lobes are normalized angular-function schematics, not VASP isosurfaces from this run.",
        fontsize=6.1,
        color=GRAY,
    )
    return save_publication(fig, "Mechanism_1_orbital_matrix_anatomy")


def mechanism_2() -> dict[str, object]:
    matrix_rows = read_csv(MATRIX_SOURCE / "co3_high_setting_matrices.csv")
    summary = read_csv(MATRIX_SOURCE / "co3_matrix_distance_summary.csv")
    new_up = matrix_from_rows(matrix_rows, "new", "Co3", "up")
    new_down = matrix_from_rows(matrix_rows, "new", "Co3", "down")
    old_up = matrix_from_rows(matrix_rows, "701", "Co3", "up")
    old_down = matrix_from_rows(matrix_rows, "701", "Co3", "down")
    diff_down = new_down - old_down
    vmax = max(
        float(np.max(np.abs(new_up))),
        float(np.max(np.abs(new_down))),
        float(np.max(np.abs(old_up))),
        float(np.max(np.abs(old_down))),
    )

    fig = plt.figure(figsize=(7.2, 5.5))
    grid = fig.add_gridspec(
        2,
        3,
        left=0.08,
        right=0.98,
        bottom=0.11,
        top=0.85,
        wspace=0.44,
        hspace=0.54,
    )
    ax_new_up = fig.add_subplot(grid[0, 0])
    ax_new_down = fig.add_subplot(grid[0, 1])
    ax_diff = fig.add_subplot(grid[0, 2])
    ax_old_up = fig.add_subplot(grid[1, 0])
    ax_old_down = fig.add_subplot(grid[1, 1])
    ax_metric = fig.add_subplot(grid[1, 2])
    draw_matrix_cells(ax_new_up, new_up, title="Solution I: spin-up", vmax=vmax)
    draw_matrix_cells(ax_new_down, new_down, title="Solution I: spin-down", vmax=vmax)
    draw_matrix_cells(
        ax_diff,
        diff_down,
        title="Co3 spin-down difference",
        vmax=float(np.max(np.abs(diff_down))),
    )
    draw_matrix_cells(ax_old_up, old_up, title="Solution II: spin-up", vmax=vmax)
    draw_matrix_cells(ax_old_down, old_down, title="Solution II: spin-down", vmax=vmax)
    panel_letter(ax_new_up, "a", x=-0.26, y=1.08)
    panel_letter(ax_new_down, "b", x=-0.26, y=1.08)
    panel_letter(ax_diff, "c", x=-0.26, y=1.08)
    panel_letter(ax_old_up, "d", x=-0.26, y=1.08)
    panel_letter(ax_old_down, "e", x=-0.26, y=1.08)
    panel_letter(ax_metric, "f", x=-0.26, y=1.08)

    up = {
        row["quantity"].split()[0]: float(row["value"])
        for row in summary
        if "spin-up Frobenius" in row["quantity"]
    }
    down = {
        row["quantity"].split()[0]: float(row["value"])
        for row in summary
        if "spin-down Frobenius" in row["quantity"]
    }
    co_labels = ["Co1", "Co2", "Co3"]
    x = np.arange(3)
    for index, label in enumerate(co_labels):
        up_value = up[label]
        down_value = down[label]
        ax_metric.plot([index, index], [up_value, down_value], color=LIGHT_GRAY, lw=1.4, zorder=1)
        ax_metric.scatter(
            index - 0.07, up_value, s=34, color=BLUE, edgecolors=WHITE, linewidths=0.5, zorder=3
        )
        ax_metric.scatter(
            index + 0.07, down_value, s=34, color=RED, edgecolors=WHITE, linewidths=0.5, zorder=3
        )
        ax_metric.text(
            index - 0.10,
            up_value * 1.20,
            f"{up_value:.3f}",
            ha="right",
            va="bottom",
            fontsize=5.0,
            color=BLUE,
        )
        ax_metric.text(
            index + 0.10,
            down_value * 1.20,
            f"{down_value:.3f}",
            ha="left",
            va="bottom",
            fontsize=5.0,
            color=RED,
        )
    ax_metric.set_yscale("log")
    ax_metric.set_ylim(5e-4, 3.0)
    # Leave enough right-hand data space for the Co3 spin-down annotation.
    ax_metric.set_xlim(-0.55, 2.72)
    ax_metric.set_xticks(x)
    ax_metric.set_xticklabels(co_labels)
    ax_metric.set_ylabel("Frobenius distance")
    ax_metric.set_title("Spin-channel matrix separation", pad=4, fontsize=8.0, fontweight="bold")
    ax_metric.legend(
        handles=[
            Line2D([], [], marker="o", ls="none", color=BLUE, ms=4.2, label="spin-up"),
            Line2D([], [], marker="o", ls="none", color=RED, ms=4.2, label="spin-down"),
        ],
        loc="upper left",
        handletextpad=0.3,
        labelspacing=0.25,
    )
    fig.suptitle(
        "Energy proximity does not establish occupation-matrix identity",
        x=0.045,
        y=0.975,
        ha="left",
        fontsize=10.5,
        fontweight="bold",
    )
    fig.text(
        0.045,
        0.925,
        "Real matrices parsed from the 4x4x4 / 650 eV stage-2 release; red/blue indicate positive/negative elements. "
        r"$\Delta E_{\mathrm{Solution\ I-Solution\ II}}=6.177$ meV.",
        fontsize=5.9,
        color=GRAY,
    )
    return save_publication(fig, "Mechanism_2_spin_resolved_state_identity")


def mechanism_3_dos() -> dict[str, object]:
    rows = read_csv(DOS_SOURCE)
    series: dict[tuple[str, str], tuple[np.ndarray, np.ndarray]] = {}
    for row in rows:
        key = (row["state"], row["spin"])
        x = float(row["Energy_minus_Efermi_eV"])
        y = float(row["DOS"])
        if key not in series:
            series[key] = ([], [])
        series[key][0].append(x)
        series[key][1].append(y)
    parsed = {key: (np.asarray(values[0]), np.asarray(values[1])) for key, values in series.items()}

    fig = plt.figure(figsize=(7.0, 3.7))
    grid = fig.add_gridspec(
        1,
        2,
        left=0.11,
        right=0.96,
        bottom=0.19,
        top=0.82,
        wspace=0.28,
    )
    axes = [fig.add_subplot(grid[0, index]) for index in range(2)]
    ymax = 0.0
    for state in ("new", "701"):
        up_x, up_y = parsed[(state, "up")]
        down_x, down_y = parsed[(state, "down")]
        mask_up = (up_x >= -2.0) & (up_x <= 2.0)
        mask_down = (down_x >= -2.0) & (down_x <= 2.0)
        ymax = max(ymax, float(np.max(up_y[mask_up])), float(np.max(down_y[mask_down])))
    ymax *= 1.12
    for ax, state, title, letter in (
        (axes[0], "new", "Solution I: spin-resolved total DOS", "a"),
        (axes[1], "701", "Solution II: spin-resolved total DOS", "b"),
    ):
        up_x, up_y = parsed[(state, "up")]
        down_x, down_y = parsed[(state, "down")]
        mask_up = (up_x >= -2.0) & (up_x <= 2.0)
        mask_down = (down_x >= -2.0) & (down_x <= 2.0)
        ax.plot(up_x[mask_up], up_y[mask_up], color=BLUE, lw=1.25, zorder=3)
        ax.plot(down_x[mask_down], -down_y[mask_down], color=RED, lw=1.25, zorder=3)
        ax.fill_between(up_x[mask_up], 0, up_y[mask_up], color=BLUE, alpha=0.18, linewidth=0)
        ax.fill_between(
            down_x[mask_down], 0, -down_y[mask_down], color=RED, alpha=0.18, linewidth=0
        )
        ax.axhline(0, color=INK, lw=0.8)
        ax.axvline(0, color=GRAY, lw=0.8, ls=(0, (2.2, 1.8)))
        ax.set_xlim(-2.0, 2.0)
        ax.set_ylim(-ymax, ymax)
        ax.set_xlabel(r"$E-E_F$ (eV)")
        ax.set_ylabel("Density of states\n(spin-up / spin-down)")
        panel_title(ax, title)
        panel_letter(ax, letter)
        style_box_axis(ax)
    axes[0].legend(
        handles=[
            Line2D([], [], color=BLUE, lw=1.4, label="spin-up"),
            Line2D([], [], color=RED, lw=1.4, label="spin-down"),
        ],
        loc="upper left",
        handletextpad=0.35,
        labelspacing=0.25,
    )
    fig.suptitle(
        "Spin-resolved total DOS for the two released Co3-squarate solutions",
        x=0.045,
        y=0.955,
        ha="left",
        fontsize=10.4,
        fontweight="bold",
    )
    fig.text(
        0.045,
        0.875,
        "Spin-down is mirrored below zero. Only total DOS is available; no site/orbital projection was invented.",
        fontsize=6.0,
        color=GRAY,
    )
    return save_publication(fig, "Mechanism_3_spin_resolved_dos")


def qa(items: list[dict[str, object]]) -> dict[str, object]:
    report: dict[str, object] = {"files": [], "checks": []}
    for item in items:
        for extension in ("svg", "pdf", "png", "tiff"):
            path = Path(str(item[extension]))
            report["checks"].append(
                {
                    "file": str(path),
                    "check": f"{extension}_nonempty",
                    "pass": path.stat().st_size > 1000,
                }
            )
        report["files"].append(
            {
                "stem": item["stem"],
                "sha256": {
                    extension: sha256(Path(str(item[extension])))
                    for extension in ("svg", "pdf", "png", "tiff")
                },
            }
        )
    return report


def main() -> None:
    items = [mechanism_2(), mechanism_3_dos()]
    report = qa(items)
    provenance = {
        "backend": "Python/matplotlib",
        "matrix_source": (MATRIX_SOURCE / "co3_high_setting_matrices.csv")
        .relative_to(REPO)
        .as_posix(),
        "matrix_summary_source": (MATRIX_SOURCE / "co3_matrix_distance_summary.csv")
        .relative_to(REPO)
        .as_posix(),
        "dos_source": DOS_SOURCE.relative_to(REPO).as_posix(),
        "outputs": items,
        "qa": report,
    }
    (QA / "qa_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (QA / "provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {"outputs": items, "all_checks_pass": all(item["pass"] for item in report["checks"])},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
