# Input contract

Ranking CSV: compound,target,seed,affinity_kcal_mol. Identifiers must be nonempty, and seeds must be positive signed 32-bit integers. Numeric strings are converted before calculations. One row per compound/target/seed is required; aliases such as numeric 1 and string "1" are treated as the same seed. Missing/nonfinite affinity, empty tables and duplicate observations are rejected.

Scores are ranked by median across seeds, with min/max/count reported. Compounds within a target must use the same scoring engine, preparation, box and protocol. Optional engine/protocol columns are checked for consistency within target; when absent, comparability is a caller responsibility. Seed counts can differ; the ranking does not establish equal precision, binding affinity in an experiment, or efficacy.

## Optional Vina execution

```sh
athena-compound dock --receptor receptor.pdbqt --ligand ligand.pdbqt --output pose.pdbqt --center 0 0 0 --size 20 20 20 --seed 2026
```

Install AutoDock Vina separately and retain its own licence. Python `run_vina` accepts the same explicit receptor/ligand, box, seed, installed executable and timeout. It rejects existing outputs, nonpositive seeds, nonfinite boxes and nonpositive timeout, propagates subprocess failures, and requires a nonempty staged pose. The destination is created exclusively using a same-filesystem hard link after success, so concurrent runs cannot overwrite one another. Choose an output filesystem that supports hard links. No physical pose-quality claim follows from this check.

CSV compound and target identifiers are literal (for example, `001` and `01` are distinct). Use distinct compound identifiers for different chemical microstates if their results must be kept separate. Ranking does not infer microstate identity or combine scores across targets or protocols.

`dock` and `run_vina` accept positive signed-32-bit CPU count (default 1) and exhaustiveness (default 8). The explicit real-engine integration reference is documented in INTEGRATION.md.
