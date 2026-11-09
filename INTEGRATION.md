# Real Vina integration reference

The source release provides two scripts. `integration/fetch_vina_fixture.py` downloads the official Vina v1.2.7 executable for macOS/Linux and prepared 1IEP receptor/ligand inputs pinned to upstream commit `8eb40404f4f45608acb3b01427587ac049f27c1f`. Fixture hashes are verified. The binary and inputs remain outside the software distribution. Retain the upstream Apache-2.0 licence fetched with them.

```sh
python -m pip install .
python integration/fetch_vina_fixture.py --output new_vina_inputs
python integration/check_vina.py --binary new_vina_inputs/vina_1.2.7_linux_x86_64 --receptor new_vina_inputs/1iep_receptor.pdbqt --ligand new_vina_inputs/1iep_ligand.pdbqt --output new_vina_check
```

Choose the binary name matching the platform, or supply another separately installed Vina executable to `check_vina.py`. Windows is not covered by these scripts. The fetcher records provenance; releases without an independent upstream digest must not be described as signature-verified. Network access occurs only in the fetch script, never automatically in the core API.

The comparison uses seed 2026, one CPU and exhaustiveness 1, with the documented 1IEP box. These intentionally modest settings test adapter/direct-CLI equivalence, not pose recovery quality. Both calls must generate identical PDBQT bytes and finite pose scores. Local macOS ARM execution with the official Vina 1.2.7 executable passed that criterion, producing one pose with score -6.845 kcal/mol. This value is a software execution observation, not evidence of binding accuracy or efficacy; no criterion was changed to match it.

`run_vina` and the `dock` CLI now expose `cpu`/`--cpu` (default 1) and `exhaustiveness`/`--exhaustiveness` (default 8). The integration script overrides exhaustiveness to 1 explicitly. Real MD, MM/PBSA, redocking-quality validation and compound-prioritization performance remain separate tasks.

Sources: [official tutorial](https://autodock-vina.readthedocs.io/en/latest/docking_basic.html), [official release](https://github.com/forlilab/AutoDock-Vina/releases/tag/v1.2.7).
