# Co3-squarate Xe/Kr adsorption pilot result

Date: 2026-10-26

## Decision

**STOP_BELOW_RESOLUTION.**

All four gas cases completed and passed the state-identity checks, but the two
occupation states changed the Xe-minus-Kr adsorption preference by only
**1.55896 meV**. This is below the pre-registered 6 meV upper numerical
resolution edge. No independent seed, 4x4x4/650 eV calculation, or geometry
extension was launched.

The valid conclusion is:

> The reproducible new and 701 Co3-squarate occupation states have nearly the
> same local Xe/Kr preference. This pilot does not support a state-dependent
> selectivity result that can be extrapolated beyond the Hofmann family.

Co3-squarate therefore remains a second-framework state/preservation audit in
SI, not a second adsorption-selection case.

## State-preservation result

All six Co atoms in every 1x1x2 gas case retained the intended state:

| Case | Joint down-matrix distance to intended state | To other state | Max eigenvalue delta | Result |
|---|---:|---:|---:|---|
| new-state/Xe | 0.012639 | 1.825081 | 0.000232 | PASS |
| new-state/Kr | 0.005503 | 1.823040 | 0.000140 | PASS |
| state701/Xe | 0.015266 | 1.823063 | 0.000210 | PASS |
| state701/Kr | 0.008489 | 1.822485 | 0.000084 | PASS |

All four cases:

- applied all six target matrices in stage 1;
- released with `OCCEXT=0`;
- reached EDIFF without NELM;
- retained 18.000 uB total magnetization;
- reached the gas-only EDIFFG criterion of 0.02 eV/A;
- passed independent force checks.

The two bare states remained distinct in the supercell: joint down-matrix
distance 1.821604 and maximum eigenvalue delta 0.003605.

## Adsorption result

Electronic adsorption energies at the common pore site, without ZPE:

| State | E_ads(Xe), eV | E_ads(Kr), eV | Xe minus Kr, meV |
|---|---:|---:|---:|
| new-state | -0.405201 | -0.326484 | -78.7173 |
| state701 | -0.406997 | -0.326721 | -80.2763 |

Thus:

`Delta_state = (-78.7173) - (-80.2763) = +1.55896 meV`.

Both states still favor Xe over Kr by about 79-80 meV at this site, consistent
with a Xe-preferring pore. The electronic-state change, however, shifts that
preference by only 1.56 meV. That is far smaller than either the 6 meV upper
envelope or the 12 meV threshold for a clear signal.

## Scope

This is a fixed-cell, fixed-framework, one-guest, 0 K electronic pilot. It does
not provide temperature-dependent uptake, IAST selectivity, full framework
relaxation, or a material ranking. Those omissions do not affect the stop
decision: a framework relaxation cannot reasonably turn a 1.56 meV state
contrast into the required >6 meV robust contrast without changing the
definition of the comparison.

## Artifacts

- `PHASE0_ANALYSIS.json`
- `PHASE0_REPORT.md`
- `GAS_ANALYSIS.json`
- `GAS_REPORT.md`
- `pilot_results_no_restart.tar.gz`

SHA256:

- GAS_ANALYSIS.json:
  `AAA357AAD2AC693C17ED3106865F628B97F66C98663C3E4387ACDB9B6A47F071`
- pilot_results_no_restart.tar.gz:
  `A77C773B1C8999FD9533FE111A5F26F530EAB41C4F71AD6A663EA0448A6B47C7`

No VASP process remains running.
