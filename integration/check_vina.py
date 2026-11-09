"""Compare the adapter against a direct call to the real Vina executable.

Requires explicitly supplied public input files; does not download anything.
This verifies software integration, not docking accuracy or drug efficacy.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import numpy as np
from athena_compound.core import run_vina


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary',required=True,type=Path)
    parser.add_argument('--receptor',required=True,type=Path)
    parser.add_argument('--ligand',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.output.exists():parser.error('Output directory must be new')
    args.output.mkdir(parents=True)
    binary=args.binary.resolve();receptor=args.receptor.resolve();ligand=args.ligand.resolve()
    center=[15.190,53.903,16.917];size=[20.,20.,20.];seed=2026
    adapter=args.output/'adapter.pdbqt';direct=args.output/'direct.pdbqt'
    version=subprocess.run([str(binary),'--version'],capture_output=True,text=True,check=True,timeout=30)
    result=run_vina(receptor,ligand,adapter,center,size,seed=seed,
                    executable=str(binary),timeout=600,cpu=1,exhaustiveness=1)
    command=[str(binary),'--receptor',str(receptor),'--ligand',str(ligand),
             '--out',str(direct),'--seed',str(seed),'--cpu','1','--exhaustiveness','1']
    for axis,c,s in zip('xyz',center,size):command += ['--center_'+axis,str(c),'--size_'+axis,str(s)]
    control=subprocess.run(command,capture_output=True,text=True,check=True,timeout=600)
    (args.output/'adapter.log').write_text(result.stdout+result.stderr)
    (args.output/'direct.log').write_text(control.stdout+control.stderr)
    a=adapter.read_text();b=direct.read_text()
    scores=[float(v) for v in re.findall(r'^REMARK VINA RESULT:\s+([-+0-9.eE]+)',a,re.M)]
    if not scores or not np.isfinite(scores).all():raise AssertionError('No finite Vina pose scores')
    if a!=b:raise AssertionError('Adapter and direct call differ for same binary/inputs/seed/CPU')
    summary={'engine_version':version.stdout.strip(),'cpu':1,'exhaustiveness':1,'seed':seed,
             'center_angstrom':center,'box_angstrom':size,'n_poses':len(scores),
             'best_score_kcal_mol':scores[0],'adapter_direct_bytes_equal':True,
             'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [binary,receptor,ligand,adapter,direct]},
             'data_kind':'official_public_1iep_fixture',
             'interpretation':'Same-backend integration equivalence only; no redocking accuracy, binding or therapeutic validation'}
    (args.output/'result.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
