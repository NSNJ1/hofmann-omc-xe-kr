# Scripts

| Script | Purpose |
|---|---|
| `verify_key_numbers.py` | Recompute the reported energy and selectivity checks |
| `make_v20_data_figures.py` | Rebuild the main quantitative figure set from source CSV files |
| `make_co3_figures.py` | Rebuild the Co3 state-matrix and DOS figures |
| `extract_occupation_matrix.py` | Parse the final spin-up/down 5 x 5 matrix from an `OUTCAR` |
| `compare_occupation_matrices.py` | Compare complete matrices, spectra, and Frobenius distances |
| `analyze_co3_adsorption_pilot.py` | Re-evaluate the common-site Co3 Xe/Kr pilot |
| `analyze_projected_state.py` | Recompute projected DOS and local spin-density tensor diagnostics when `DOSCAR` and `CHGCAR` are available |
| `sanitize_paths.py` | Replace workstation/cluster prefixes before a release |
| `build_manifest.py` | Write SHA-256 manifests for GitHub and the Zenodo archive |
| `check_release.py` | Validate required files, hashes, secrets, and forbidden content |

Scripts resolve data relative to the repository root. They can be run from
any working directory.
