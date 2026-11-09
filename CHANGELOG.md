# 0.1.0rc4

- Preserve literal compound and target identifiers and create Vina destinations exclusively after successful docking. Exclude the historical screening/MD workflow.

# 0.1.0rc3

- Reject malformed/empty schemas and convert numeric input before aggregation.
- Stage CLI analysis output so invalid inputs leave no analysis directory.
- Refine optional dependencies to this package and separate heavy engines.
- 25 source-level tests passed on Python 3.14; final installed-distribution checks are recorded separately.
- Add dock CLI and validate seeds, scoring protocol labels and pose-file completion. Executable stub tests verify process/file behavior without claiming a physical Vina calculation.

# 0.1.0rc1

Initial private review candidate with installable API, explicit inputs and synthetic examples.

## 0.1.0rc3

Added configurable CPU count/exhaustiveness, defaulting to one CPU. Added real Vina/direct-CLI equivalence integration scripts with a pinned official public fixture. No engine binary or input structure is redistributed.
