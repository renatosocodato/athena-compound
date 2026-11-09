import pandas as pd

from athena_compound.cli import main


def test_csv_keeps_distinct_compound_and_target_ids(tmp_path):
    source = tmp_path/'input.csv'
    source.write_text('compound,target,seed,affinity_kcal_mol\n'
                      '001,003,1,-9\n001,003,2,-7\n01,003,3,-3\n'
                      '01,003,4,-5\n001,03,1,-11\n')
    out = tmp_path/'result'
    assert main(['run', '--input', str(source), '--output', str(out)]) == 0
    ranks = pd.read_csv(out/'rankings.csv', dtype={'compound': str, 'target': str})
    assert ranks.set_index(['compound','target'])['median'].to_dict() == {
        ('001', '003'): -8, ('01', '003'): -4, ('001', '03'): -11,
    }
