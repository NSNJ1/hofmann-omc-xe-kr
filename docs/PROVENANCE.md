# Provenance

## Inputs used for this release

The release was assembled from the current numerical closeout tables and
figure-source exports on 2026-11-20. The principal source groups were:

- the final Hofmann calculation closeout tables;
- the target-family source table and Co3 robustness table;
- long-form plotting exports used to build the current manuscript figures;
- selected complete occupation matrices, parsed state audits, and Co3 DOS;
- reduced differential-charge-density slices;
- archived Hofmann `INCAR`, `KPOINTS`, `POSCAR`, and `CONTCAR` files;
- selected VASP text outputs for the second-framework calculations.

## Path handling

Generated manifests and audit reports may retain a logical calculation or
job identifier. Local desktop paths and cluster home-directory prefixes are
removed before publication. The released repository should contain no
credential, private key, access token, or personal absolute path.

## Exclusion rules

Files were excluded when they were:

- licensed VASP datasets (`POTCAR`) or executables;
- full restart or volumetric files (`WAVECAR`, `CHGCAR`);
- caches, compiled Python, VM images, or downloaded third-party papers;
- unrelated project material, prompts, or pre-submission editorial drafts.

## Integrity

`manifest_sha256.txt` records the SHA-256 digest of every distributed file
except the manifest itself and ignored high-resolution TIFF exports. Run
`python scripts/check_release.py` after checkout to verify the tree and the
forbidden-content rules.
