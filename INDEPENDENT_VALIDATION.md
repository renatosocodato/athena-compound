# Independent implementation and scientific checks

The rc3 reference runs and the rc4 macOS replay passed on the pinned official 1IEP fixture: v1.2.7 on macOS ARM64 (rc3 and rc4), and v1.2.5 plus v1.2.7 on Ubuntu ARM64 (rc3). In each run, the adapter and direct invocation produced byte-identical PDBQT files with CPU 1, exhaustiveness 1 and seed 2026.

Outputs differed across the tested platform/binary combinations: the macOS v1.2.7 best score was -6.845 kcal/mol and the Linux best score was -10.94 kcal/mol. Fixed seed therefore does not establish cross-platform pose/score identity. These low-exhaustiveness integration runs do not validate redocking accuracy, binding affinity, efficacy or MD. See integration/ for input acquisition, hashes and the executable comparison.

These are internal computational checks against independent implementations, public inputs and real engines. No external peer review is claimed. Full execution details are in VALIDATION.md.

## Revision after independent candidate review

Preserve literal compound and target identifiers and create Vina destinations exclusively after successful docking. Exclude the historical screening/MD workflow. Hosted execution records for the exact distributions are tracked separately.
