"""Replicate-aware docking ranking and an explicit external Vina interface."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import numpy as np
import pandas as pd


def _positive_integer(value, label):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or not 0 < value <= 2147483647:
        raise ValueError(f'{label} must be a positive signed 32-bit integer')
    return int(value)


def rank_compounds(frame):
    """Rank median docking energies across unique seeds, within each target.

    Optional engine/protocol columns must identify one common scoring protocol
    per target. Without these columns the caller must establish comparability.
    Energies must have numeric units kcal/mol; lower is ranked first. Different
    replicate counts are reported, not treated as equal evidence precision.
    """
    cols = ['compound', 'target', 'seed', 'affinity_kcal_mol']
    if not isinstance(frame, pd.DataFrame) or frame.empty or not frame.columns.is_unique or not set(cols).issubset(frame.columns):
        raise ValueError('Nonempty table with unique compound, target, seed and affinity columns required')
    if frame[cols].isna().any().any():
        raise ValueError('Complete compound/target/seed observations required')
    working = frame.copy()
    for column in ['compound', 'target']:
        working[column] = working[column].astype(str).str.strip()
        if working[column].eq('').any():
            raise ValueError('Nonempty compound and target identifiers required')
    try:
        seeds = pd.to_numeric(working.seed, errors='raise').to_numpy(dtype=float)
        affinity = pd.to_numeric(working.affinity_kcal_mol, errors='raise').to_numpy(dtype=float)
    except (ValueError, TypeError) as error:
        raise ValueError('Numeric affinity and integer seeds required') from error
    if not np.isfinite(seeds).all() or (seeds <= 0).any() or (seeds > 2147483647).any() or not np.equal(seeds, np.floor(seeds)).all():
        raise ValueError('Seeds must be positive signed 32-bit integers')
    if working.seed.map(lambda x: isinstance(x, (bool, np.bool_))).any():
        raise ValueError('Boolean seeds are not seed identifiers')
    working['seed'] = seeds.astype(np.int64)
    working['affinity_kcal_mol'] = affinity
    if working.duplicated(cols[:3]).any():
        raise ValueError('Unique compound/target/seed observations required')
    if not np.isfinite(affinity).all():
        raise ValueError('Affinity must be finite')
    for column in ['engine', 'protocol']:
        if column in working:
            if working[column].isna().any() or working[column].astype(str).str.strip().eq('').any():
                raise ValueError(f'Complete {column} labels required when supplied')
            if (working.groupby('target')[column].nunique() > 1).any():
                raise ValueError(f'Mixed {column} within a target cannot be ranked together')
    result = working.groupby(['compound', 'target']).affinity_kcal_mol.agg(['median', 'min', 'max', 'count']).reset_index()
    return result.sort_values(['target', 'median', 'compound']).reset_index(drop=True)


def run_vina(receptor, ligand, output, center, size, seed=2026, executable='vina', timeout=600, cpu=1, exhaustiveness=8):
    """Run separately installed Vina; success requires a nonempty output file.

    The subprocess receives an argument list and writes a staged pose. The
    destination is created exclusively after a successful run, so a competing
    invocation cannot replace it. Vina is installed separately.
    """
    seed = _positive_integer(seed, 'Seed')
    cpu = _positive_integer(cpu, 'CPU count')
    exhaustiveness = _positive_integer(exhaustiveness, 'Exhaustiveness')
    try:
        center = np.asarray(center, dtype=float)
        size = np.asarray(size, dtype=float)
    except (TypeError, ValueError) as error:
        raise ValueError('Numeric box coordinates required') from error
    if center.shape != (3,) or size.shape != (3,) or not np.isfinite([center, size]).all() or (size <= 0).any():
        raise ValueError('Three finite center coordinates and positive box sizes required')
    if isinstance(timeout, bool) or not isinstance(timeout, (float, int)) or not np.isfinite(timeout) or timeout <= 0:
        raise ValueError('Positive finite timeout required')
    receptor, ligand = (Path(p).expanduser().resolve() for p in (receptor, ligand))
    output = Path(output).expanduser()
    output = output.parent.resolve() / output.name
    if not receptor.is_file() or not ligand.is_file():
        raise FileNotFoundError('Receptor and ligand PDBQT files required')
    if output.exists() or output.is_symlink():
        raise FileExistsError('Refusing to overwrite output')
    if not output.parent.is_dir():
        raise FileNotFoundError('Output parent directory must exist')
    binary = shutil.which(executable)
    if binary is None:
        raise RuntimeError('Install AutoDock Vina separately')
    with tempfile.TemporaryDirectory(prefix='.athena-vina-', dir=output.parent) as directory:
        staged = Path(directory) / 'pose.pdbqt'
        args = [binary, '--receptor', str(receptor), '--ligand', str(ligand), '--out', str(staged), '--seed', str(seed), '--cpu', str(cpu), '--exhaustiveness', str(exhaustiveness)]
        for axis, c, s in zip('xyz', center, size):
            args += ['--center_' + axis, str(c), '--size_' + axis, str(s)]
        result = subprocess.run(args, check=True, capture_output=True, text=True, timeout=timeout)
        if not staged.is_file() or staged.is_symlink() or staged.stat().st_size == 0:
            raise RuntimeError('Vina returned successfully but did not produce a nonempty pose file')
        os.link(staged, output)
    return result
