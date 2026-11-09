"""An executable stub verifies subprocess/file behavior, not docking physics."""
import subprocess
import pytest
from athena_compound.core import run_vina


def test_executable_backend_with_space_in_paths_and_cli(tmp_path):
    binary=tmp_path/'fake vina'
    binary.write_text("#!/usr/bin/env python3\nimport sys\nfrom pathlib import Path\nPath(sys.argv[sys.argv.index('--out')+1]).write_text('REMARK synthetic interface fixture')\n")
    binary.chmod(0o755)
    receptor=tmp_path/'receptor ; unused.pdbqt';receptor.write_text('fixture')
    ligand=tmp_path/'ligand.pdbqt';ligand.write_text('fixture')
    output=tmp_path/'pose.pdbqt'
    result=run_vina(receptor,ligand,output,[0,0,0],[1,1,1],executable=str(binary))
    assert result.returncode==0 and output.read_text().startswith('REMARK')


def test_subprocess_failure_is_propagated(tmp_path):
    binary=tmp_path/'fake-vina'
    binary.write_text('#!/usr/bin/env python3\nraise SystemExit(3)\n');binary.chmod(0o755)
    receptor=tmp_path/'r';receptor.write_text('fixture')
    with pytest.raises(subprocess.CalledProcessError):
        run_vina(receptor,receptor,tmp_path/'pose',[0,0,0],[1,1,1],executable=str(binary))
    assert not (tmp_path/'pose').exists()
