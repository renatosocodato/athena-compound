import numpy as np
from pathlib import Path
import pandas as pd
import pytest
from unittest.mock import patch
from athena_compound.core import rank_compounds,run_vina

def fixture():
    return pd.DataFrame({'compound':['a']*3+['b']*3,'target':['r']*6,'seed':[1,2,3]*2,'affinity_kcal_mol':[-6,-8,-7,-4,-6,-5]})

def test_median_and_spread_not_best_pose_cherry_picking():
    r=rank_compounds(fixture());assert r.compound.tolist()==['a','b']
    assert r['median'].tolist()==[-7,-5];assert r['count'].tolist()==[3,3]

def test_duplicate_seed_rejected():
    x=fixture()
    with pytest.raises(ValueError):rank_compounds(pd.concat([x,x.iloc[:1]]))

def test_nonfinite_rejected():
    x=fixture().astype({'affinity_kcal_mol':float});x.loc[0,'affinity_kcal_mol']=np.inf
    with pytest.raises(ValueError):rank_compounds(x)

def test_vina_command_no_shell_and_explicit_seed_box(tmp_path):
    receptor=tmp_path/'r.pdbqt';ligand=tmp_path/'l.pdbqt'
    receptor.write_text('fixture');ligand.write_text('fixture')
    with patch('athena_compound.core.shutil.which',return_value='/mock/vina'),patch('athena_compound.core.subprocess.run') as run:
        run.side_effect=lambda args,**kw: Path(args[args.index('--out')+1]).write_text('REMARK synthetic pose')
        run_vina(receptor,ligand,tmp_path/'out.pdbqt',[1,2,3],[10,11,12],seed=44)
        args=run.call_args.args[0];assert args[args.index('--seed')+1]=='44'
        assert float(args[args.index('--size_z')+1])==12
        assert 'shell' not in run.call_args.kwargs


def test_competing_docking_cannot_replace_destination(tmp_path):
    receptor=tmp_path/'receptor.pdbqt';receptor.write_text('fixture')
    output=tmp_path/'output.pdbqt'

    def finish_after_competitor(args, **kwargs):
        Path(args[args.index('--out')+1]).write_text('later pose')
        output.write_text('first successful pose')

    with patch('athena_compound.core.shutil.which',return_value='/mock/vina'),patch('athena_compound.core.subprocess.run',side_effect=finish_after_competitor):
        with pytest.raises(FileExistsError):
            run_vina(receptor,receptor,output,[0,0,0],[1,1,1])
    assert output.read_text() == 'first successful pose'

def test_vina_bad_box_and_overwrite_rejected(tmp_path):
    with pytest.raises(ValueError):run_vina('x','y','z',[0,0,0],[1,-1,1])
    r=tmp_path/'r';r.write_text('fixture')
    with pytest.raises(FileExistsError):run_vina(r,r,r,[0,0,0],[1,1,1])


def test_numeric_strings_are_converted_before_aggregation():
    x=fixture().astype(str)
    ranks=rank_compounds(x)
    assert ranks['median'].tolist()==[-7.,-5.]

@pytest.mark.parametrize('seed',[0,-1,1.5,float('nan'),True])
def test_invalid_seed_identifiers_rejected(seed):
    x=fixture().astype({'seed':object});x.loc[0,'seed']=seed
    with pytest.raises(ValueError):rank_compounds(x)

def test_duplicates_after_seed_numeric_conversion_rejected():
    x=fixture().astype({'seed':object});x.loc[1,'seed']='1'
    with pytest.raises(ValueError):rank_compounds(x)

def test_mixed_engines_rejected_within_target():
    x=fixture();x['engine']=['vina']*3+['other']*3
    with pytest.raises(ValueError,match='Mixed engine'):rank_compounds(x)

@pytest.mark.parametrize('invalid',['empty','missing','empty_id'])
def test_invalid_schema_rejected(invalid):
    x=fixture()
    if invalid=='empty':x=x.iloc[:0]
    if invalid=='missing':x=x.drop(columns=['target'])
    if invalid=='empty_id':x.loc[0,'compound']='  '
    with pytest.raises(ValueError):rank_compounds(x)

@pytest.mark.parametrize('seed,timeout',[(0,1),(True,1),(1,0),(1,float('inf'))])
def test_invalid_vina_runtime_options_rejected(seed,timeout):
    with pytest.raises(ValueError):run_vina('r','l','o',[0,0,0],[1,1,1],seed=seed,timeout=timeout)

def test_successful_process_without_pose_is_not_success(tmp_path):
    r=tmp_path/'r';r.write_text('fixture')
    with patch('athena_compound.core.shutil.which',return_value='/mock/vina'),patch('athena_compound.core.subprocess.run'):
        with pytest.raises(RuntimeError,match='pose file'):run_vina(r,r,tmp_path/'pose',[0,0,0],[1,1,1])


@pytest.mark.parametrize('keyword,value', [('cpu',0),('cpu',True),('exhaustiveness',0),('exhaustiveness',1.5)])
def test_invalid_compute_settings_rejected(keyword,value):
    with pytest.raises(ValueError):
        run_vina('unused','unused','unused',[0,0,0],[1,1,1],**{keyword:value})
