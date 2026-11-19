# Open-science scope for this release

The deposit follows current high-impact computational-paper practice and
exceeds the minimum journal requirement in two ways:

1. the actionable inputs and analysis code are exposed in a Git repository
   rather than described only at a high level;
2. the same repository state is archived with a version-specific DOI.

The v1.1.0 public release does not attempt to mirror every byte of the
calculation workspace. Large restart/volumetric files and licensed software
are omitted, while the numerical tables, selected endpoint outputs, state
matrices, and figure-generation code needed to audit the claims are retained.

The full v1.0.0 workspace remains in the local archive
`E:\git\hofmann-omc-xe-kr-full-v1.0.0` for provenance and deeper follow-up.

This is preferable to publishing:

- a README-only repository whose claims cannot be recomputed;
- a dump of scratch files with no entry point;
- processed figures without their source tables;
- raw licensed inputs such as `POTCAR`.

The manuscript should cite the version DOI, while the GitHub URL can serve as
the maintained development location.
