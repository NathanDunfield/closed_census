#! /bin/env sage-python
#
#SBATCH --partition m
#SBATCH --tasks=1
#SBATCH --mem-per-cpu=4096
#SBATCH --nice=10000
#SBATCH --time=7-00:00
#SBATCH --output=slurm_out/%j
#SBATCH --error=slurm_error/%j

import taskdb2
import snappy
import dehn

def remaining_exceptional(task):
    manifold = snappy.ManifoldHP(task['name'])
    known = eval(task['fillings'])
    L = dehn.NormalizedCuspLattice(manifold)
    ans = []
    for s in L.primitive_elements():
        if tuple(s) not in known:
            print(s) 
            M = manifold.copy()
            M.dehn_fill(s, 0)
            if dehn.appears_hyperbolic(M):
                if dehn.approx_systole(M) >= 0.2:
                    assert len(M.length_spectrum(0.2)) != 0
            else:
                ans.append(s)
    task['new_exceptional'] = repr(ans)
    task['done'] = True

task0 = {'name':'o9_39593', 'fillings':'dict()'}
task1 = {'name':'o9_00523', 'fillings':'dict()'}

#taskdb2.worker.run_function('cusped_fillings', 'task_other', remaining_exceptional)

import pandas as pd

#data = pd.read_csv('cusped_fillings.csv.bz2')

def make_exceptional_database(data):
    names, kinds = [], []
    for i, cusped in data.iterrows():
        name = cusped['name']
        for slope in eval(cusped['finite']):
            names.append(name + repr(slope))
            kinds.append('finite')
        for slope in eval(cusped['other_exceptional']):
            names.append(name + repr(slope))
            kinds.append('')
    return pd.DataFrame({'name':names, 'kind':kinds}, columns=['name', 'kind'])
