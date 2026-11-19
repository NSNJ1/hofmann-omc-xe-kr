# ZJU74 v18 Origin-ready data

This folder contains corrected, plotting-oriented tables. It does not modify the
original source data or figures.

## Important correction

The original panel 4a figure is not merely a different sign style. Its plotted
input and its stated net value are inconsistent.

The manuscript and surviving source table give:

- Sx: frozen methyl term +56.8 meV, framework relaxation -27.7 meV, net +29.1 meV.
- beta: frozen methyl term +38.5 meV, framework relaxation -9.4 meV, net +29.1 meV.

The old `fig5_graft.csv` stores -14.30 and -32.57 in the column named
`S_graft_meV`. Those two numbers are S values from the source notes, not the
frozen methyl terms. The old plotting script then draws them as negative bars,
which cannot produce the displayed net +29.1 meV. Do not reuse that panel.

Use `fig4a_methyl_waterfall.csv`, which has explicit start and end coordinates
for a waterfall plot.

## Files

| File | Use |
|---|---|
| `fig3_environment_long.csv` | Corrected Figure 3 environment labels; `F` is relabeled `F4`. |
| `fig4a_methyl_waterfall.csv` | Correct Figure 4a waterfall data. |
| `fig4b_volume_shape_long.csv` | Figure 4b Ni-shape volume series and separate Pd-cell anchor. |
| `fig4c_guest_sphere.csv` | Figure 4c data separated by comparison type. |
| `figS1_resolution_tests.csv` | Data for the missing Supporting Figure S1. |
| `figure_action_plan.csv` | Required action and software choice for every figure. |

## Provenance

Main sources:

- `ZJU74_项目/03_数据与图表/ZJU74_fig_data_20261018/fig3_net_binding.csv`
- `ZJU74_项目/03_数据与图表/ZJU74_repro_package_20261018/data/graft_pairs.csv`
- `ZJU74_项目/03_数据与图表/ZJU74_fig_data_20261018/fig5_t2b.csv`
- `ZJU74_项目/03_数据与图表/ZJU74_fig_data_20261018/fig5_drho.csv`
- `ZJU74_项目/01_当前主稿/ZJU74_支持信息_SI_v3_20261020.docx`, Tables S1 and S2

The Figure 4a correction follows the manuscript's Table 3 and the arithmetic
identity `graft + relaxation = net`.
