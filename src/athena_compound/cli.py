DESCRIPTION = 'Compound screening interfaces and ranking'

import argparse
import csv
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import pandas as pd
from . import core

def main(argv=None):
    parser=argparse.ArgumentParser(description=DESCRIPTION)
    sub=parser.add_subparsers(dest='command',required=True)
    ex=sub.add_parser('example',help='Run a synthetic example, without network or private data')
    ex.add_argument('--output',type=Path,required=True)
    run=sub.add_parser('run',help='Analyze explicit input files; see INPUTS.md')
    run.add_argument('--input',type=Path,required=True);run.add_argument('--output',type=Path,required=True)
    dock=sub.add_parser('dock',help='Run separately installed Vina on explicit PDBQT inputs')
    dock.add_argument('--receptor',type=Path,required=True);dock.add_argument('--ligand',type=Path,required=True)
    dock.add_argument('--output',type=Path,required=True)
    dock.add_argument('--center',type=float,nargs=3,required=True);dock.add_argument('--size',type=float,nargs=3,required=True)
    dock.add_argument('--seed',type=int,default=2026);dock.add_argument('--timeout',type=float,default=600)
    dock.add_argument('--executable',default='vina')
    dock.add_argument('--cpu',type=int,default=1)
    dock.add_argument('--exhaustiveness',type=int,default=8)
    args=parser.parse_args(argv)
    if args.command=='dock':
        try:
            core.run_vina(args.receptor,args.ligand,args.output,args.center,args.size,args.seed,args.executable,args.timeout,cpu=args.cpu,exhaustiveness=args.exhaustiveness)
        except (ValueError,OSError,RuntimeError,subprocess.SubprocessError) as error:
            parser.error(str(error))
        return 0
    if args.output.exists():parser.error('Output directory already exists; choose a new directory')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix='.athena-stage-',dir=args.output.parent) as tmp:
            staged=argparse.Namespace(**vars(args));staged.output=Path(tmp)
            result=analyze(staged)
            (staged.output/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
            shutil.copytree(staged.output,args.output)
    except (ValueError,KeyError,OSError,csv.Error) as error:
        parser.error(str(error))
    return 0

def analyze(args):
    if args.command=='example':
        frame=pd.DataFrame({'compound':['probe_a']*3+['probe_b']*3,'target':['target_a']*6,'seed':[1,2,3]*2,'affinity_kcal_mol':[-7,-6,-8,-5,-4,-6]})
    else:
        with args.input.open(encoding='utf-8-sig', newline='') as stream:
            reader=csv.reader(stream, strict=True)
            header=next(reader, [])
            if not header or any(not c.strip() for c in header) or len(set(header)) != len(header):
                raise ValueError('CSV requires nonempty unique column names')
            records=[]
            for row in reader:
                if not row:
                    continue
                if len(row) != len(header):
                    raise ValueError(f'Invalid CSV record at line {reader.line_num}')
                records.append(row)
        frame=pd.DataFrame(records, columns=header)
    ranks=core.rank_compounds(frame);ranks.to_csv(args.output/'rankings.csv',index=False)
    return {'data_kind':'synthetic' if args.command=='example' else 'user_supplied','pairs':len(ranks),'interpretation':'Docking ranking only; no simulated engine run in this example'}
