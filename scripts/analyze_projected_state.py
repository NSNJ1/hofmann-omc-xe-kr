#!/usr/bin/env python3
"""Analyze Co d-projected DOS and the local spin-density tensor from VASP outputs."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np


def read_poscar(path: Path) -> tuple[np.ndarray, list[str], list[int], np.ndarray]:
    lines = path.read_text(errors="ignore").splitlines()
    if len(lines) < 8:
        raise ValueError(f"POSCAR too short: {path}")
    scale = float(lines[1].split()[0])
    lattice = (
        np.asarray(
            [[float(value) for value in lines[index].split()[:3]] for index in range(2, 5)],
            dtype=float,
        )
        * scale
    )
    symbols = lines[5].split()
    counts = [int(value) for value in lines[6].split()]
    if len(symbols) != len(counts):
        raise ValueError(f"VASP5 species/count mismatch in {path}")
    cursor = 7
    if lines[cursor].strip().lower().startswith("s"):
        cursor += 1
    coordinate_mode = lines[cursor].strip().lower()
    cursor += 1
    natoms = sum(counts)
    coordinates = np.asarray(
        [[float(value) for value in lines[cursor + index].split()[:3]] for index in range(natoms)],
        dtype=float,
    )
    if coordinate_mode.startswith(("c", "k")):
        fractional = coordinates @ np.linalg.inv(lattice)
    else:
        fractional = coordinates
    expanded_symbols: list[str] = []
    for symbol, count in zip(symbols, counts, strict=True):
        expanded_symbols.extend([symbol] * count)
    return lattice, expanded_symbols, counts, fractional


def material_index(symbols: list[str], symbol: str) -> int:
    indices = [index for index, value in enumerate(symbols) if value == symbol]
    if len(indices) != 1:
        raise ValueError(f"expected exactly one {symbol} atom, found {len(indices)}")
    return indices[0]


def parse_doscar(path: Path, atom_index: int) -> dict[str, object]:
    lines = path.read_text(errors="ignore").splitlines()
    natoms = int(lines[0].split()[0])
    header = lines[5].split()
    efermi = float(header[3])
    nedos = int(header[2])
    total_start = 6
    if len(lines) < total_start + nedos:
        raise ValueError(f"DOSCAR is shorter than its declared DOS grid: {path}")
    partial_start = total_start + nedos
    block_size = nedos + 1
    atom_start = partial_start + atom_index * block_size
    if atom_start + nedos >= len(lines):
        raise ValueError(f"DOSCAR does not contain partial block for 0-based atom {atom_index}")
    partial = np.asarray(
        [
            [float(value) for value in lines[index].split()]
            for index in range(atom_start + 1, atom_start + 1 + nedos)
        ],
        dtype=float,
    )
    if partial.shape[1] != 19:
        raise ValueError(f"expected 19 columns in Co partial DOS, found {partial.shape[1]}")
    energies = partial[:, 0]
    occupied = energies <= efermi
    if not occupied.any():
        raise ValueError("Fermi energy lies below the DOS grid")

    def integrate(values: np.ndarray) -> float:
        last = int(np.flatnonzero(occupied)[-1])
        upper = min(last + 1, len(energies) - 1)
        if energies[upper] > efermi:
            interpolated = np.interp(
                efermi,
                energies[last : upper + 1],
                values[last : upper + 1],
            )
            values = values[: upper + 1].copy()
            energies_local = energies[: upper + 1].copy()
            energies_local[-1] = efermi
            values[-1] = interpolated
            return float(np.trapezoid(values, energies_local))
        return float(np.trapezoid(values[: upper + 1], energies[: upper + 1]))

    orbital_names = ("s", "py", "pz", "px", "dxy", "dyz", "dz2", "dxz", "x2-y2")
    orbital_up: dict[str, float] = {}
    orbital_down: dict[str, float] = {}
    for orbital_index, name in enumerate(orbital_names):
        # For spin-polarized DOSCAR the orbital channels are interleaved.
        orbital_up[name] = integrate(partial[:, 1 + 2 * orbital_index])
        orbital_down[name] = integrate(partial[:, 2 + 2 * orbital_index])

    d_orbitals = orbital_names[4:]
    d_up = float(sum(orbital_up[name] for name in d_orbitals))
    d_down = float(sum(orbital_down[name] for name in d_orbitals))
    d_total = d_up + d_down
    sp_up = float(sum(orbital_up[name] for name in orbital_names[:4]))
    sp_down = float(sum(orbital_down[name] for name in orbital_names[:4]))
    orbital_summary = {
        name: {
            "up": orbital_up[name],
            "down": orbital_down[name],
            "total": orbital_up[name] + orbital_down[name],
            "normalized_spin_polarization": (
                (orbital_up[name] - orbital_down[name]) / (orbital_up[name] + orbital_down[name])
                if orbital_up[name] + orbital_down[name] > 0
                else float("nan")
            ),
            "fraction_of_d_projection": (
                (orbital_up[name] + orbital_down[name]) / d_total
                if name in d_orbitals and d_total > 0
                else None
            ),
        }
        for name in orbital_names
    }

    return {
        "natoms_declared": natoms,
        "efermi_eV": efermi,
        "nedos": nedos,
        "energy_min_eV": float(energies[0]),
        "energy_max_eV": float(energies[-1]),
        "orbital_up": orbital_up,
        "orbital_down": orbital_down,
        "d_up": d_up,
        "d_down": d_down,
        "d_trace": d_total,
        "d_spin_moment": d_up - d_down,
        "normalized_d_spin_polarization": (
            (d_up - d_down) / d_total if d_total > 0 else float("nan")
        ),
        "sp_up": sp_up,
        "sp_down": sp_down,
        "sp_spin_moment": sp_up - sp_down,
        "d_orbital_anisotropy_up": float(
            max(orbital_up[name] for name in d_orbitals)
            - min(orbital_up[name] for name in d_orbitals)
        ),
        "d_orbital_anisotropy_down": float(
            max(orbital_down[name] for name in d_orbitals)
            - min(orbital_down[name] for name in d_orbitals)
        ),
        "orbital_summary": orbital_summary,
    }


def read_chgcar_grids(path: Path) -> tuple[tuple[int, int, int], np.ndarray]:
    with path.open("r", errors="ignore") as stream:
        lines = stream.readlines()

    first_grid_index = None
    for index, line in enumerate(lines):
        values = line.split()
        if len(values) == 3 and all(value.isdigit() for value in values):
            candidate = tuple(int(value) for value in values)
            if min(candidate) > 1:
                first_grid_index = index
                grid = candidate
                break
    if first_grid_index is None:
        raise ValueError(f"could not find CHGCAR grid dimensions in {path}")

    ngrid = math.prod(grid)
    values: list[float] = []
    cursor = first_grid_index + 1
    while len(values) < ngrid:
        values.extend(float(value) for value in lines[cursor].split())
        cursor += 1
    if len(values) != ngrid:
        raise ValueError(f"first CHGCAR grid overread in {path}")

    second_grid_index = None
    for index in range(cursor, len(lines)):
        candidate_values = lines[index].split()
        if len(candidate_values) != 3:
            continue
        if not all(value.isdigit() for value in candidate_values):
            continue
        candidate = tuple(int(value) for value in candidate_values)
        if candidate != grid:
            continue
        second_grid_index = index
        break
    if second_grid_index is None:
        raise ValueError(f"could not find magnetization grid in {path}")

    magnetization: list[float] = []
    cursor = second_grid_index + 1
    while len(magnetization) < ngrid:
        magnetization.extend(float(value) for value in lines[cursor].split())
        cursor += 1
    if len(magnetization) != ngrid:
        raise ValueError(f"magnetization grid overread in {path}")
    array = np.asarray(magnetization, dtype=float).reshape(grid[2], grid[1], grid[0])
    return grid, array


def local_spin_analysis(
    lattice: np.ndarray,
    fractional: np.ndarray,
    grid: tuple[int, int, int],
    magnetization: np.ndarray,
    atom_index: int,
) -> dict[str, object]:
    nx, ny, nz = grid
    center = fractional[atom_index]
    ix = np.arange(nx, dtype=float) / nx
    iy = np.arange(ny, dtype=float) / ny
    iz = np.arange(nz, dtype=float) / nz
    zz, yy, xx = np.meshgrid(iz, iy, ix, indexing="ij")
    delta = np.stack((xx - center[0], yy - center[1], zz - center[2]), axis=-1)
    delta = (delta + 0.5) % 1.0 - 0.5
    cartesian = delta @ lattice
    radius = np.linalg.norm(cartesian, axis=-1)
    cell_volume = abs(float(np.linalg.det(lattice)))
    ngrid = math.prod(grid)
    voxel_volume = cell_volume / ngrid

    max_radius = min(2.5, 0.45 * float(np.linalg.norm(lattice, axis=1).min()))
    mask = radius <= max_radius
    radii = radius[mask]
    # VASP CHGCAR density values are already integrated on the NGXF*NGYF*NGZF
    # grid, so the sum divided by the number of grid points gives the cell
    # integral. Multiplying again by the physical voxel volume overcounts by
    # the cell volume.
    weights = magnetization[mask] / ngrid
    vectors = cartesian[mask]

    bin_width = 0.1
    bin_count = int(math.ceil(max_radius / bin_width))
    radial_rows: list[dict[str, float]] = []
    cumulative_by_radius: list[dict[str, float]] = []
    cumulative = 0.0
    for bin_index in range(bin_count):
        lower = bin_index * bin_width
        upper = min((bin_index + 1) * bin_width, max_radius)
        selected = (radii >= lower) & (radii < upper)
        spin = float(weights[selected].sum())
        cumulative += spin
        radial_rows.append(
            {
                "r_min_angstrom": lower,
                "r_max_angstrom": upper,
                "integrated_magnetization": spin,
                "cumulative_magnetization": cumulative,
            }
        )
        cumulative_by_radius.append(
            {
                "radius_angstrom": upper,
                "integrated_magnetization": cumulative,
            }
        )

    cutoffs: list[dict[str, object]] = []
    for cutoff in (1.2, 1.4, 1.6, 2.0):
        if cutoff > max_radius:
            continue
        selected = radii <= cutoff
        selected_vectors = vectors[selected]
        selected_weights = weights[selected]
        signed_integral = float(selected_weights.sum())
        absolute_integral = float(np.abs(selected_weights).sum())
        r2 = np.einsum("ij,ij->i", selected_vectors, selected_vectors)
        second = (
            selected_weights[:, None, None]
            * selected_vectors[:, :, None]
            * selected_vectors[:, None, :]
        ).sum(axis=0)
        second = second / signed_integral if abs(signed_integral) > 0 else np.full((3, 3), np.nan)

        signed_quadrupole_weights = selected_weights
        signed_quadrupole = (
            signed_quadrupole_weights[:, None, None]
            * (
                3.0 * selected_vectors[:, :, None] * selected_vectors[:, None, :]
                - r2[:, None, None] * np.eye(3)
            )
        ).sum(axis=0)
        signed_quadrupole = (
            signed_quadrupole / signed_integral
            if abs(signed_integral) > 0
            else np.full((3, 3), np.nan)
        )
        absolute_quadrupole = (
            np.abs(selected_weights)[:, None, None]
            * (
                3.0 * selected_vectors[:, :, None] * selected_vectors[:, None, :]
                - r2[:, None, None] * np.eye(3)
            )
        ).sum(axis=0)
        absolute_quadrupole = (
            absolute_quadrupole / absolute_integral
            if absolute_integral > 0
            else np.full((3, 3), np.nan)
        )
        signed_eigenvalues, signed_eigenvectors = np.linalg.eigh(signed_quadrupole)
        absolute_eigenvalues, absolute_eigenvectors = np.linalg.eigh(absolute_quadrupole)
        cutoffs.append(
            {
                "radius_angstrom": cutoff,
                "signed_integral_magnetization": signed_integral,
                "absolute_integral_magnetization": absolute_integral,
                "second_moment_matrix_angstrom2": second.tolist(),
                "signed_quadrupole_eigenvalues": signed_eigenvalues.tolist(),
                "signed_quadrupole_eigenvectors": signed_eigenvectors.tolist(),
                "absolute_quadrupole_eigenvalues": absolute_eigenvalues.tolist(),
                "absolute_quadrupole_eigenvectors": absolute_eigenvectors.tolist(),
            }
        )

    return {
        "atom_index_1based": atom_index + 1,
        "center_fractional": center.tolist(),
        "cell_volume_angstrom3": cell_volume,
        "voxel_volume_angstrom3": voxel_volume,
        "max_radius_angstrom": max_radius,
        "radial_profile": radial_rows,
        "cutoff_analysis": cutoffs,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--element", default="Co")
    parser.add_argument(
        "--atom-index",
        type=int,
        help="1-based atom index; required when the element occurs more than once",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    case_dir = args.case_dir.expanduser().resolve()
    lattice, symbols, counts, fractional = read_poscar(case_dir / "POSCAR")
    if args.atom_index is None:
        atom_index = material_index(symbols, args.element)
    else:
        atom_index = args.atom_index - 1
        if atom_index < 0 or atom_index >= len(symbols):
            parser.error("--atom-index is outside the POSCAR atom range")
        if symbols[atom_index] != args.element:
            parser.error(
                f"--atom-index {args.atom_index} is {symbols[atom_index]}, not {args.element}"
            )
    dos = parse_doscar(case_dir / "DOSCAR", atom_index)
    grid, magnetization = read_chgcar_grids(case_dir / "CHGCAR")
    spin = local_spin_analysis(
        lattice,
        fractional,
        grid,
        magnetization,
        atom_index,
    )
    payload = {
        "case_dir": str(case_dir),
        "element": args.element,
        "atom_index_0based": atom_index,
        "species_counts": {symbol: symbols.count(symbol) for symbol in sorted(set(symbols))},
        "poscar_counts": counts,
        "dos": dos,
        "chgcar": {
            "grid": list(grid),
            "magnetization_grid_diagnostics": {
                "raw_sum": float(magnetization.sum()),
                "integral": float(magnetization.sum() / math.prod(grid)),
                "absolute_integral": float(np.abs(magnetization).sum() / math.prod(grid)),
                "minimum": float(magnetization.min()),
                "maximum": float(magnetization.max()),
            },
            "local_spin_analysis": spin,
        },
    }
    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
