from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MultipleLocator

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "data" / "source_tables"
OUTPUT = REPO / "figures" / "rebuilt"

COLORS = {
    "reference": "#626262",
    "reference_light": "#A6A6A6",
    "nikr": "#0F4D92",
    "pdkr": "#C27B3A",
    "xe": "#0F4D92",
    "kr": "#D17A36",
    "pd": "#0F4D92",
    "pt": "#B64342",
    "ni": "#42949E",
}


plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "font.size": 7,
        "axes.linewidth": 0.8,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "legend.frameon": False,
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
    }
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def style_axis(ax, *, grid_axis: str = "y") -> None:
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.grid(axis=grid_axis, color="#DDE2E8", linewidth=0.6, zorder=0)
    ax.tick_params(labelsize=7, pad=2)
    ax.set_axisbelow(True)


def panel_label(ax, label: str) -> None:
    ax.text(
        -0.16,
        1.05,
        label,
        transform=ax.transAxes,
        fontsize=8,
        fontweight="bold",
        ha="left",
        va="bottom",
    )


def save_figure(fig, stem: str) -> None:
    fig.savefig(OUTPUT / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(OUTPUT / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(OUTPUT / f"{stem}.png", dpi=600, bbox_inches="tight")
    fig.savefig(OUTPUT / f"{stem}.tiff", dpi=600, bbox_inches="tight")
    plt.close(fig)


def figure_3_reference_effects() -> None:
    source = read_csv(SOURCE / "hofmann_figure_20261025" / "fig2_target_family_source.csv")
    rows_a = [row for row in source if row["panel"] == "a"]
    rows_d = [row for row in source if row["panel"] == "c"]

    fig = plt.figure(figsize=(7.2, 4.9))
    gs = fig.add_gridspec(2, 2, wspace=0.44, hspace=0.48)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    # a: paired complex and bare shifts.
    order = [("Pd", "Xe"), ("Pd", "Kr"), ("Pt", "Xe"), ("Pt", "Kr"), ("Ni", "Xe"), ("Ni", "Kr")]
    labels = [f"{metal}–{gas}" for metal, gas in order]
    y = np.arange(len(order))[::-1]
    lookup = {(row["metal"], row["gas"], row["metric"]): float(row["value_meV"]) for row in rows_a}
    for yi, (metal, gas) in zip(y, order, strict=True):
        complex_shift = lookup[(metal, gas, "complex_shift")]
        bare_shift = lookup[(metal, gas, "bare_shift")]
        ax_a.plot([complex_shift, bare_shift], [yi, yi], color="#C9CED3", lw=1.3, zorder=1)
        ax_a.scatter(
            complex_shift,
            yi,
            s=28,
            color=COLORS["nikr"],
            edgecolor="white",
            linewidth=0.6,
            zorder=2,
        )
        ax_a.scatter(
            bare_shift,
            yi,
            s=28,
            facecolor="white",
            edgecolor=COLORS["reference"],
            linewidth=1.2,
            zorder=2,
        )
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(labels)
    ax_a.set_xlabel("Energy shift from reference (meV)")
    ax_a.set_xlim(-55, -34)
    ax_a.axvline(0, color="#8B949E", lw=0.6, ls="--", visible=False)
    style_axis(ax_a, grid_axis="x")
    first_complex = lookup[("Pd", "Xe", "complex_shift")]
    first_bare = lookup[("Pd", "Xe", "bare_shift")]
    ax_a.annotate(
        "guest-loaded",
        (first_complex, y[0]),
        xytext=(-3, 8),
        textcoords="offset points",
        ha="right",
        va="bottom",
        fontsize=6.2,
        color=COLORS["nikr"],
    )
    ax_a.annotate(
        "guest-free",
        (first_bare, y[0]),
        xytext=(-3, 8),
        textcoords="offset points",
        ha="right",
        va="bottom",
        fontsize=6.2,
        color=COLORS["reference"],
    )
    panel_label(ax_a, "a")

    # b: net adsorption-energy response after consistent reference assignment.
    net = [lookup[(metal, gas, "family_matched_eads_shift")] for metal, gas in order]
    colors = [COLORS["xe"] if gas == "Xe" else COLORS["kr"] for _, gas in order]
    ax_b.axvline(0, color="#7C8792", lw=0.8, ls="--")
    for yi, value, color in zip(y, net, colors, strict=True):
        ax_b.plot([0, value], [yi, yi], color=color, lw=1.1, alpha=0.75)
        ax_b.scatter(value, yi, s=30, color=color, edgecolor="white", linewidth=0.6, zorder=3)
        ax_b.text(
            value + (0.55 if value >= 0 else -0.55),
            yi,
            f"{value:+.1f}",
            va="center",
            ha="left" if value >= 0 else "right",
            fontsize=6.2,
        )
    ax_b.set_yticks(y)
    ax_b.set_yticklabels(labels)
    ax_b.set_xlabel("Reference-consistent ΔEads (meV)")
    ax_b.set_xlim(-2, 17)
    style_axis(ax_b, grid_axis="x")
    panel_label(ax_b, "b")

    # c: selectivity under three electronic references.
    sel = read_csv(SOURCE / "v20_workdata" / "fig2b_selectivity.csv")
    y_sel = {"Pd": 2, "Pt": 1, "Ni": 0}
    for row in sel:
        metal = row["Metal"]
        values = [
            float(row["Historical control"]),
            float(row["Mx target family"]),
            float(row["Same-protocol control"]),
        ]
        ax_c.plot(
            values[:2],
            [y_sel[metal], y_sel[metal]],
            color="#C9CED3",
            lw=1.2,
            zorder=1,
        )
        ax_c.scatter(values[0], y_sel[metal], s=32, color=COLORS["reference"], zorder=3)
        ax_c.scatter(values[1], y_sel[metal], s=36, color=COLORS["nikr"], zorder=3)
        ax_c.scatter(
            values[2],
            y_sel[metal],
            s=32,
            facecolor="white",
            edgecolor=COLORS["pdkr"],
            linewidth=1.2,
            zorder=3,
        )
        ax_c.text(
            values[1] + 0.8,
            y_sel[metal] + 0.08,
            f"{values[1]:.1f}",
            fontsize=6.2,
            color=COLORS["nikr"],
        )
    ax_c.set_yticks([0, 1, 2])
    ax_c.set_yticklabels(["Ni", "Pt", "Pd"])
    ax_c.set_xlabel("S = Eads(Xe) − Eads(Kr) (meV)")
    ax_c.set_xlim(-80, -47)
    style_axis(ax_c, grid_axis="x")
    ax_c.legend(
        handles=[
            Line2D(
                [],
                [],
                marker="o",
                ls="",
                color=COLORS["reference"],
                markersize=4,
                label="Reference",
            ),
            Line2D(
                [], [], marker="o", ls="", color=COLORS["nikr"], markersize=4, label="Ni–Kr target"
            ),
            Line2D(
                [],
                [],
                marker="o",
                ls="",
                markerfacecolor="white",
                markeredgecolor=COLORS["pdkr"],
                markeredgewidth=1,
                markersize=4,
                label="Pd–Kr target",
            ),
        ],
        loc="lower left",
        bbox_to_anchor=(0.0, 1.01, 1.0, 0.18),
        mode="expand",
        ncol=3,
        fontsize=6.0,
        borderaxespad=0,
    )
    panel_label(ax_c, "c")

    # d: numerical sensitivity of the target-set energies.
    d_order = [("Pd", "Xe"), ("Pd", "Kr"), ("Pt", "Xe"), ("Pt", "Kr"), ("Ni", "Xe"), ("Ni", "Kr")]
    d_lookup = {(row["metal"], row["gas"]): float(row["value_meV"]) for row in rows_d}
    y_d = np.arange(len(d_order))[::-1]
    for yi, (metal, gas) in zip(y_d, d_order, strict=True):
        value = d_lookup[(metal, gas)]
        color = COLORS["xe"] if gas == "Xe" else COLORS["kr"]
        edge = COLORS["pt"] if metal == "Pd" and gas == "Kr" else color
        ax_d.plot([0, value], [yi, yi], color=color, lw=1.1, alpha=0.75)
        ax_d.scatter(value, yi, s=30, color=color, edgecolor=edge, linewidth=1.0, zorder=3)
        ax_d.text(value + 0.0008, yi, f"{value:+.4f}", va="center", fontsize=5.8)
    ax_d.axvline(0, color="#7C8792", lw=0.8, ls="--")
    ax_d.set_yticks(y_d)
    ax_d.set_yticklabels([f"{m}–{g}" for m, g in d_order])
    ax_d.set_xlabel("ΔEads(650 − 600 eV) (meV)")
    ax_d.set_xlim(-0.003, 0.015)
    ax_d.xaxis.set_major_locator(MultipleLocator(0.003))
    ax_d.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.3f}"))
    style_axis(ax_d, grid_axis="x")
    panel_label(ax_d, "d")

    save_figure(fig, "Figure3_reference_effects")


def figure_4_chemical_controls() -> None:
    base = SOURCE / "v20_workdata"
    xe = read_csv(base / "fig3_xe.csv")
    kr = read_csv(base / "fig3_kr.csv")
    response = read_csv(base / "fig3_selectivity_change_vs_H.csv")

    fig = plt.figure(figsize=(7.2, 4.9))
    gs = fig.add_gridspec(2, 2, wspace=0.42, hspace=0.48)
    fig.subplots_adjust(top=0.84)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    environments = ["H", "CH3", "F4"]
    metals = ["Pd", "Pt", "Ni"]
    metal_colors = [COLORS["pd"], COLORS["pt"], COLORS["ni"]]
    x = np.arange(len(environments))
    width = 0.22

    for ax, data, title in [
        (ax_a, xe, "Xe binding"),
        (ax_b, kr, "Kr binding"),
    ]:
        for metal, color in zip(metals, metal_colors, strict=True):
            values = [-float(row[metal]) for row in data if row["Environment"] in environments]
            ax.plot(x, values, color=color, marker="o", ms=4.2, lw=1.4, zorder=3)
        ax.set_xticks(x)
        ax.set_xticklabels(["H", r"CH$_3$", r"F$_4$"])
        ax.set_title(title, loc="left", fontsize=8.2, fontweight="bold", pad=8)
        ax.set_ylabel(r"$-$E$_{\mathrm{ads}}$ (meV)")
        ax.set_ylim(235, 345)
        style_axis(ax)

    fig.legend(
        handles=[
            Patch(facecolor=COLORS["pd"], label="Pd"),
            Patch(facecolor=COLORS["pt"], label="Pt"),
            Patch(facecolor=COLORS["ni"], label="Ni"),
        ],
        loc="upper center",
        bbox_to_anchor=(0.52, 0.985),
        ncol=3,
        fontsize=6.5,
        handlelength=1.2,
        columnspacing=1.8,
    )
    panel_label(ax_a, "a")
    panel_label(ax_b, "b")

    selectivity = read_csv(base / "fig3_selectivity_from_energies.csv")
    matrix = np.array(
        [
            [-float(row[metal]) for metal in metals]
            for row in selectivity
            if row["Environment"] in environments
        ]
    )
    ax_c.imshow(matrix, cmap="Blues", vmin=0, vmax=75, aspect="auto")
    ax_c.set_xticks(range(3))
    ax_c.set_xticklabels(environments)
    ax_c.set_yticks(range(3))
    ax_c.set_yticklabels(metals)
    ax_c.set_xlabel("Environment")
    ax_c.set_ylabel("Metal")
    ax_c.set_title("Xe preference (meV)", loc="left", fontsize=8, fontweight="bold")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            value = matrix[i, j]
            color = "white" if value > 40 else "#172033"
            ax_c.text(j, i, f"{value:.1f}", ha="center", va="center", fontsize=7, color=color)
    ax_c.tick_params(length=0)
    for spine in ax_c.spines.values():
        spine.set_visible(False)
    panel_label(ax_c, "c")

    rows_by_env = {row["Environment"]: [float(row[m]) for m in metals] for row in response}
    x2 = np.arange(2)
    for idx, _metal in enumerate(metals):
        vals = [rows_by_env[env][idx] for env in ["CH3", "F4"]]
        bars = ax_d.bar(
            x2 + (idx - 1) * width,
            vals,
            width=width,
            color=metal_colors[idx],
            edgecolor="none",
            alpha=0.92,
        )
        for bar, value in zip(bars, vals, strict=True):
            ax_d.text(
                bar.get_x() + bar.get_width() / 2,
                value + 0.5,
                f"{value:.1f}",
                ha="center",
                va="bottom",
                fontsize=5.8,
            )
    ax_d.set_xticks(x2)
    ax_d.set_xticklabels([r"CH$_3$", r"F$_4$"])
    ax_d.set_ylabel(r"$\Delta S$ vs H (meV)")
    ax_d.set_xlabel("Environment")
    ax_d.set_ylim(0, 53)
    ax_d.set_title("Change relative to H", loc="left", fontsize=8.2, fontweight="bold", pad=8)
    style_axis(ax_d)
    panel_label(ax_d, "d")

    save_figure(fig, "Figure4_chemical_controls")


def figure_5_decomposition() -> None:
    base = SOURCE / "v20_origin"
    waterfall = read_csv(base / "fig4a_methyl_waterfall.csv")
    volume_ni = read_csv(SOURCE / "v20_workdata" / "fig4b_ni_volume.csv")
    volume_pd = read_csv(SOURCE / "v20_workdata" / "fig4b_pd_cell_anchor.csv")
    charge = read_csv(base / "fig4c_guest_sphere.csv")

    fig = plt.figure(figsize=(7.2, 4.9))
    gs = fig.add_gridspec(2, 2, wspace=0.42, hspace=0.48)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    group_names = {"Sx": "Pd–Kr target", "beta": "Reference"}
    group_x = {"Sx": 0, "beta": 1}
    term_x = {"frozen methyl host": -0.22, "framework relaxation": 0.0, "net DeltaS_CH3": 0.22}
    term_labels = ["contact", "relaxation", "net"]
    term_colors = [COLORS["pdkr"], COLORS["reference_light"], COLORS["nikr"]]
    for row in waterfall:
        group = row["pair"]
        term = row["term"]
        if term == "net DeltaS_CH3":
            value = float(row["net_meV"])
            xpos = group_x[group] + term_x[term]
            ax_a.bar(xpos, value, width=0.18, color=term_colors[2], edgecolor="none")
            ax_a.text(xpos, value + 1.0, f"{value:.1f}", ha="center", fontsize=6)
        elif term == "framework relaxation":
            value = float(row["delta_meV"])
            xpos = group_x[group] + term_x[term]
            ax_a.bar(xpos, value, width=0.18, color=term_colors[1], edgecolor="none")
            ax_a.text(xpos, value - 2.1, f"{value:.1f}", ha="center", va="top", fontsize=6)
        else:
            value = float(row["delta_meV"])
            xpos = group_x[group] + term_x[term]
            ax_a.bar(xpos, value, width=0.18, color=term_colors[0], edgecolor="none")
            ax_a.text(xpos, value + 1.0, f"{value:.1f}", ha="center", fontsize=6)
    ax_a.axhline(0, color="#66707A", lw=0.8)
    ax_a.set_xticks([-0.22, 0, 0.22, 0.78, 1, 1.22])
    ax_a.set_xticklabels(term_labels * 2, rotation=20, ha="right")
    ax_a.text(0, 67, group_names["Sx"], ha="center", fontsize=7, fontweight="bold")
    ax_a.text(1, 67, group_names["beta"], ha="center", fontsize=7, fontweight="bold")
    ax_a.set_ylabel(r"Contribution to $\Delta S$(CH$_3$) (meV)")
    ax_a.set_ylim(-35, 72)
    style_axis(ax_a)
    panel_label(ax_a, "a")

    ni_x = [float(row["V_over_V0"]) for row in volume_ni]
    ni_xe = [-float(row["Xe_Eads_meV"]) for row in volume_ni]
    ni_kr = [-float(row["Kr_Eads_meV"]) for row in volume_ni]
    pd_x = [float(row["V_over_V0"]) for row in volume_pd]
    pd_xe = [-float(row["Xe_Eads_meV"]) for row in volume_pd]
    pd_kr = [-float(row["Kr_Eads_meV"]) for row in volume_pd]
    ax_b.plot(ni_x, ni_xe, color=COLORS["xe"], marker="o", lw=1.3, ms=3.5, label="Ni–Xe")
    ax_b.plot(ni_x, ni_kr, color=COLORS["kr"], marker="o", lw=1.3, ms=3.5, label="Ni–Kr")
    ax_b.scatter(
        pd_x,
        pd_xe,
        marker="D",
        s=34,
        facecolor="white",
        edgecolor=COLORS["xe"],
        linewidth=1.1,
        label="Pd-cell Xe",
    )
    ax_b.scatter(
        pd_x,
        pd_kr,
        marker="D",
        s=34,
        facecolor="white",
        edgecolor=COLORS["kr"],
        linewidth=1.1,
        label="Pd-cell Kr",
    )
    ax_b.set_xlabel(r"$V/V_0$")
    ax_b.set_ylabel(r"Binding strength, $-$E$_{\mathrm{ads}}$ (meV)")
    ax_b.set_ylim(235, 342)
    style_axis(ax_b)
    ax_b.text(0.975, ni_xe[1] + 2.2, "Ni–Xe", color=COLORS["xe"], fontsize=6.2, fontweight="bold")
    ax_b.text(0.975, ni_kr[1] - 5.0, "Ni–Kr", color=COLORS["kr"], fontsize=6.2, fontweight="bold")
    ax_b.text(1.053, pd_xe[0] + 5.0, "Pd-cell Xe", color=COLORS["xe"], fontsize=6.0)
    ax_b.text(1.053, pd_kr[0] + 6.0, "Pd-cell Kr", color=COLORS["kr"], fontsize=6.0)
    ax_b.set_xlim(0.963, 1.085)
    panel_label(ax_b, "b")

    refs = [row for row in charge if row["comparison_group"] == "reference magnitude"]
    small = [row for row in charge if row["comparison_group"] == "small perturbation"]
    ax_c.bar(
        [row["quantity"] for row in refs],
        [float(row["value_e"]) for row in refs],
        color=[COLORS["xe"], COLORS["kr"]],
        edgecolor="none",
        width=0.55,
    )
    for idx, row in enumerate(refs):
        ax_c.text(
            idx,
            float(row["value_e"]) + 0.03,
            f"{float(row['value_e']):.3f}",
            ha="center",
            fontsize=6.5,
        )
    ax_c.set_ylabel(r"Integrated $|\Delta\rho|$ (e)")
    ax_c.set_ylim(0, 1.2)
    ax_c.tick_params(axis="x", rotation=15)
    style_axis(ax_c)
    ax_c.set_title("Reference magnitude", loc="left", fontsize=8, fontweight="bold")
    panel_label(ax_c, "c")

    small_labels = ["CH3 effect", "Metal variation"]
    small_values = [float(row["value_e"]) for row in small]
    ax_d.bar(
        small_labels,
        small_values,
        color=[COLORS["pdkr"], COLORS["ni"]],
        edgecolor="none",
        width=0.55,
    )
    for idx, value in enumerate(small_values):
        ax_d.text(idx, value + 0.0015, f"{value:.3f}", ha="center", fontsize=6.5)
    ax_d.set_ylabel(r"Change in sphere charge (e)")
    ax_d.set_ylim(0, 0.05)
    ax_d.tick_params(axis="x", rotation=15)
    style_axis(ax_d)
    ax_d.set_title("Small perturbations", loc="left", fontsize=8, fontweight="bold")
    panel_label(ax_d, "d")

    save_figure(fig, "Figure5_methyl_and_cell_response")


def figure_s1_resolution() -> None:
    base = SOURCE / "v20_workdata"
    cutoff = read_csv(base / "figS1_cutoff.csv")
    kmesh = read_csv(base / "figS1_kmesh.csv")

    fig = plt.figure(figsize=(7.2, 4.8))
    gs = fig.add_gridspec(2, 2, wspace=0.42, hspace=0.48)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    cut_x = [int(row["Setting"]) for row in cutoff]
    cut_e = [float(row["Eads_meV"]) for row in cutoff]
    cut_d = [float(row["Delta_vs_production_meV"]) for row in cutoff]
    ax_a.plot(cut_x, cut_e, color=COLORS["nikr"], marker="o", lw=1.2, ms=3.5)
    ax_a.scatter(
        [600],
        [cut_e[2]],
        marker="D",
        s=30,
        facecolor="white",
        edgecolor=COLORS["reference"],
        linewidth=1.0,
        zorder=3,
    )
    ax_a.set_xticks(cut_x)
    ax_a.set_xlabel("Cutoff energy (eV)")
    ax_a.set_ylabel(r"E$_{\mathrm{ads}}$ (meV)")
    style_axis(ax_a)
    panel_label(ax_a, "a")

    ax_b.axhspan(-2, 2, color="#E7EBEF", zorder=0)
    ax_b.axhline(0, color="#6C7682", lw=0.7, ls="--")
    ax_b.plot(cut_x, cut_d, color=COLORS["nikr"], marker="o", lw=1.2, ms=3.5)
    ax_b.scatter(
        [600],
        [cut_d[2]],
        marker="D",
        s=30,
        facecolor="white",
        edgecolor=COLORS["reference"],
        linewidth=1.0,
        zorder=3,
    )
    for xval, yval in zip(cut_x, cut_d, strict=True):
        if xval != 600:
            ax_b.text(xval, yval + 0.09, f"{yval:+.1f}", ha="center", fontsize=5.8)
    ax_b.set_xticks(cut_x)
    ax_b.set_xlabel("Cutoff energy (eV)")
    ax_b.set_ylabel(r"$\Delta$E$_{\mathrm{ads}}$ (meV)")
    ax_b.set_ylim(-2.3, 2.3)
    style_axis(ax_b, grid_axis="x")
    panel_label(ax_b, "b")

    k_labels = [row["Setting"] for row in kmesh]
    k_x = np.arange(len(k_labels))
    k_d = [float(row["Delta_vs_production_meV"]) for row in kmesh]
    for idx, row in enumerate(kmesh):
        selected_y = 0 if row["Family"] == "beta" else 1
        selected_color = COLORS["reference"] if selected_y == 0 else COLORS["pdkr"]
        ax_c.scatter(
            k_x[idx],
            selected_y,
            s=55,
            color=selected_color,
            edgecolor="white",
            linewidth=0.8,
            zorder=3,
        )
        ax_c.scatter(
            k_x[idx],
            1 - selected_y,
            s=55,
            facecolor="white",
            edgecolor="#D5DADF",
            linewidth=1.0,
            zorder=2,
        )
        ax_d.scatter(
            k_x[idx],
            k_d[idx],
            s=34,
            color=selected_color,
            edgecolor="white",
            linewidth=0.6,
            zorder=3,
        )
        ax_d.text(
            k_x[idx],
            k_d[idx] + 0.65,
            f"{k_d[idx]:+.1f}",
            ha="center",
            fontsize=5.8,
            color=selected_color,
        )
    ax_c.axhline(0, color="#A7AFB7", lw=0.7)
    ax_c.axhline(1, color="#A7AFB7", lw=0.7)
    ax_c.set_ylim(-0.45, 1.45)
    ax_c.set_yticks([0, 1])
    ax_c.set_yticklabels(["Reference", "Alternate"])
    ax_c.set_xticks(k_x)
    ax_c.set_xticklabels(k_labels, rotation=20, ha="right")
    ax_c.set_ylabel("Selected solution")
    ax_c.tick_params(axis="both", length=0)
    ax_c.grid(False)
    for spine in ax_c.spines.values():
        spine.set_visible(False)
    ax_d.axhspan(-2, 2, color="#E7EBEF", zorder=0)
    ax_d.axhline(0, color="#6C7682", lw=0.7, ls="--")
    ax_d.set_xticks(k_x)
    ax_d.set_xticklabels(k_labels, rotation=20, ha="right")
    ax_d.set_ylabel(r"$\Delta$E$_{\mathrm{ads}}$ (meV)")
    ax_d.set_ylim(-3, 15)
    style_axis(ax_d, grid_axis="x")
    panel_label(ax_c, "c")
    panel_label(ax_d, "d")

    save_figure(fig, "FigureS1_resolution_and_solution_identity")


def figure_s2_second_framework() -> None:
    base = SOURCE / "v20_workdata"
    pair = read_csv(base / "figS2a.csv")
    margins = read_csv(base / "figS2b.csv")

    fig = plt.figure(figsize=(7.2, 4.9))
    gs = fig.add_gridspec(2, 2, wspace=0.44, hspace=0.54)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    protocols = [row["Protocol"] for row in pair]
    values = [float(row["new_minus_701_meV"]) for row in pair]
    x_positions = np.arange(len(protocols))[::-1]
    short_protocols = [
        "Fixed 3×3×3, 600 eV",
        "Fixed 4×4×4, 600 eV",
        "Fixed 3×3×3, 650 eV",
        "H-only, 3×3×3, 600 eV",
        "Full-ion, 3×3×3, 600 eV",
        "Full-ion, 4×4×4, 650 eV",
    ]
    ax_a.barh(
        x_positions,
        values,
        color=[COLORS["nikr"]] * 4 + [COLORS["pdkr"]] * 2,
        height=0.62,
    )
    for y, value in zip(x_positions, values, strict=True):
        ax_a.text(value + 0.16, y, f"{value:.2f}", va="center", fontsize=5.8)
    ax_a.set_yticks(x_positions)
    ax_a.set_yticklabels(short_protocols, fontsize=5.8)
    ax_a.set_xlabel("Solution I − II (meV)")
    ax_a.set_xlim(0, 14)
    style_axis(ax_a, grid_axis="x")
    panel_label(ax_a, "a")

    labels = [row["Comparison"] for row in margins]
    vals = [float(row["max_eigenvalue_delta"]) for row in margins]
    colors = [COLORS["reference_light"], COLORS["reference_light"], COLORS["nikr"], COLORS["nikr"]]
    markers = ["o", "s", "o", "s"]
    ypos = np.arange(len(labels))[::-1]
    for y, value, color, marker in zip(ypos, vals, colors, markers, strict=True):
        ax_b.plot([0, value], [y, y], color=color, lw=1.3, marker=marker, ms=4)
        ax_b.text(value + 0.00018, y, f"{value:.4f}", va="center", fontsize=5.8)
    ax_b.set_yticks(ypos)
    ax_b.set_yticklabels(
        [
            "Low-energy\ncontrol",
            "Acceptance-like",
            "Solution I\n4×4×4/650 eV",
            "Solution II\n4×4×4/650 eV",
        ],
        fontsize=6,
    )
    ax_b.set_xlabel(r"Max eigenvalue change $\Delta\lambda_{\max}$")
    ax_b.set_xlim(0, 0.0065)
    style_axis(ax_b, grid_axis="x")
    panel_label(ax_b, "b")

    co_values = {"Solution I": (-0.405201, -0.326484), "Solution II": (-0.406997, -0.326721)}
    xx = np.arange(2)
    labels = list(co_values)
    width = 0.32
    ax_c.bar(
        xx - width / 2,
        [co_values[key][0] for key in labels],
        width=width,
        color=COLORS["xe"],
        edgecolor="none",
    )
    ax_c.bar(
        xx + width / 2,
        [co_values[key][1] for key in labels],
        width=width,
        color=COLORS["kr"],
        edgecolor="none",
    )
    for idx, key in enumerate(labels):
        ax_c.text(
            idx - width / 2,
            co_values[key][0] - 0.007,
            f"{co_values[key][0]:.3f}",
            ha="center",
            va="top",
            fontsize=5.8,
        )
        ax_c.text(
            idx + width / 2,
            co_values[key][1] - 0.007,
            f"{co_values[key][1]:.3f}",
            ha="center",
            va="top",
            fontsize=5.8,
        )
    ax_c.axhline(0, color="#6C7682", lw=0.7)
    ax_c.set_xticks(xx)
    ax_c.set_xticklabels(labels)
    ax_c.set_ylabel(r"E$_{\mathrm{ads}}$ (eV)")
    ax_c.set_ylim(-0.45, 0)
    style_axis(ax_c)
    panel_label(ax_c, "c")

    deltas = [-78.71732, -80.27628]
    bars = ax_d.bar(
        labels, deltas, color=[COLORS["nikr"], COLORS["pdkr"]], edgecolor="none", width=0.52
    )
    for bar, value in zip(bars, deltas, strict=True):
        ax_d.text(
            bar.get_x() + bar.get_width() / 2,
            value - 0.9,
            f"{value:.2f}",
            ha="center",
            va="top",
            fontsize=6,
        )
    ax_d.axhline(0, color="#6C7682", lw=0.7)
    ax_d.set_ylabel(r"E$_{\mathrm{ads}}$(Xe − Kr) (meV)")
    ax_d.set_ylim(-86, 0)
    style_axis(ax_d)
    panel_label(ax_d, "d")

    save_figure(fig, "FigureS2_second_framework_boundary")


def main() -> None:
    figure_3_reference_effects()
    figure_4_chemical_controls()
    figure_5_decomposition()
    figure_s1_resolution()
    figure_s2_second_framework()


if __name__ == "__main__":
    main()
