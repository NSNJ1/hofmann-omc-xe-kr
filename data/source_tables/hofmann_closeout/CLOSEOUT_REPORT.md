# JCTC/npj OMC calculation closeout

Date: 2026-10-23

> **Figure 3a standardization note added 2026-11-01.** The legacy seeds
> `401/402` (Pd-Kr) and `501/502` (Ni-Kr) used `phase0/a` source geometries.
> Although their INCAR, KPOINTS and POTCAR settings match the later runs, the
> Ni POSCAR differs by up to `2.30 x 10^-4 A`. They are excluded from the
> standardized `phase0/y` eight-seed series used in Figure 3a. The historical
> 10-per-target statement below remains a legacy sensitivity record and is not
> the fixed-geometry plotting series.

## Completion

All planned calculations and controls are complete:

- 12/12 standard-geometry directed complexes;
- 6/6 same-template compound controls;
- 9/9 standard bare controls/candidates;
- 12/12 convergence directories;
- 16/16 U-ramp steps;
- 2/2 650 eV re-seeded cutoff gate cases;
- 7/7 additional 650 eV directed complexes;
- 6/6 650 eV bare controls/candidates;
- 4/4 state-matched 650 eV references;
- 16/16 extended-random cases.

The extended-random queue passed all 32 stage-level input/OUTCAR checks.

## Reproducibility

At fixed `phase0/y` geometry and fixed DFT+U settings:

- Pd–Kr Sx followed three distinct SCF paths and all returned Sx.
- Ni–Kr Mx followed three distinct SCF paths and all returned Mx.
- The eight newly added Pd perturbations had a stage-2 range of 0.00335 meV
  (sample SD 0.00115 meV); including the two earlier seeds, all 10/10 returned
  Sx with a 0.00102 meV sample SD.
- The eight newly added Ni perturbations had a stage-2 range of 0.00615 meV
  (sample SD 0.00222 meV); including the two earlier seeds, all 10/10 returned
  Mx with a 0.00371 meV sample SD.
- New random trajectories reached the target full-matrix neighborhood within
  Frobenius distance 0.00084–0.00951.

These are local stability tests. They are not independent random samples of the
whole occupation space and do not prove a global ground state.

## Cutoff and numerical checks

- Direct continuation of a 600 eV wavefunction at 650 eV returned Ni–Kr Mx to
  beta. This was a restart-basis effect.
- Reapplying `OCCEXT=1` at 650 eV and releasing it recovered Ni–Kr Mx exactly
  (full-matrix distance 0.000173) and retained a 41.41635 meV stabilization
  relative to the 650 eV beta control.
- Pd–Kr Sx was retained at 650 eV (distance 0.000539; 48.82418 meV below the
  same-cutoff alpha control).
- The 650 eV directed complex and bare tables reproduce the 600 eV
  state-resolved adsorption energies to approximately 0.01–0.03 meV.
- k=6 and `EDIFF=1e-7` retained the Sx/Mx states in the tested systems.

## High-cutoff state-resolved adsorption energies

Applying matched complex and bare state shifts to the frozen v9 anchors:

| gas | Pd / meV | Ni / meV | Pt / meV |
|---|---:|---:|---:|
| Xe | -314.454 | -308.334 | -289.487 |
| Kr | -252.416 | -239.818 | -238.536 |

Xe/Kr separation:

| metal | S = E_Xe - E_Kr / meV |
|---|---:|
| Pd | -62.038 |
| Ni | -68.516 |
| Pt | -50.951 |

The absolute single-gas ordering remains `Pd > Ni > Pt` for both gases. The
Ni–Pt Kr difference is only about 1.28 meV and is below a defensible
state/parameter-resolution claim. The Mx branch changes the selectivity
ordering to Ni > Pd > Pt, mainly by weakening Pd and Pt Xe adsorption.

## U-ramping

The U-ramp completed from U=0 to 3.5 eV in eight linked steps for each metal,
but its terminal state is neither the directed Sx nor Mx state. It is a
path-dependent branch at higher energy. U-ramping therefore demonstrates path
dependence but does not validate Mx/Sx.

## Claims supported by the data

1. Multiple self-consistent DFT+U occupation-matrix solutions exist at fixed
   geometry and composition.
2. A state identity can shift a complex total energy by roughly 37–49 meV.
3. The Pd Sx and Ni Mx branches are reproducible under multiple SCF paths,
   local perturbations, and the tested cutoff/tolerance changes.
4. The high-cutoff Mx branch changes Xe/Kr selectivity without changing the
   absolute single-gas metal ordering.
5. Using a single SCF output can therefore hide a discrete electronic-state
   choice in an adsorption-energy workflow.

## Claims not supported

1. Mx is not a proven new thermodynamic phase or symmetry-distinct phase.
2. The five historical plus Mx labels are not an exhaustive enumeration.
3. The random perturbations are not a global OMC or original ROLP search.
4. The Ni–Pt 1.28 meV Kr ranking and the Pd/Ni selectivity ranking are below
   a robust DFT meta-comparison threshold.
5. The results do not establish generality across MOF topologies or metal
   chemistries.

## Journal assessment

JCTC is the more defensible target: the strongest result is a method/reporting
issue—SCF state identity in periodic DFT+U adsorption workflows—supported by
controls, cutoff re-seeding, and 20 local random restarts.

npj Computational Materials is not yet supported by this single material
family and would require at least one independent framework/topology plus a
physical classification of the Mx pattern.

The next scientific task is therefore not more 600 eV seeds. It is either:

1. a second MOF framework with the same state-resolved protocol; or
2. a rigorous symmetry/orbital-rotation and spin-density analysis that turns
   Mx from an operational fingerprint into a physical classification.

## Red-team verdict

- Arithmetic: passed. The 16 random cases have consistent denominators, all
  stage-2 calculations converge, and the high-cutoff E_ads values reproduce
  from the recorded state shifts.
- Fatal issue check: no surviving 600→650 eV artifact remains after the
  occupation constraint was reapplied at 650 eV.
- Material issue: all quantitative ranking claims still come from one MOF
  family; transferability is unproven.
- Material issue: Mx has a reproducible fixed-basis signature but no proven
  symmetry-invariant physical identity.
- Material issue: the 1.28 meV Ni–Pt Kr ordering and small selectivity
  differences are below a safe cross-material decision threshold.
- Minor issue: U-ramping samples one continuous path and therefore does not
  measure basin coverage.

These material issues are carried into the journal decision and are not
hidden as caveats in the Results section.

## Provenance

- Standard analysis: `standard_analysis.md` and associated CSV files.
- Extended random data: `extended_random_summary.csv`.
- High-cutoff table: `highcut_Mx_eads_20261022.csv`.
- VM roots:
  - `remote:/jctc_standard_states_20261021`
  - `remote:/jctc_extended_random_standard_20261021`
  - `remote:/jctc_cutoff_full_20261022`
  - `remote:/jctc_cutoff_refs_20261022`
