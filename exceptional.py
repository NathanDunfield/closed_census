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
import dehn, hyperbolic

def solution_valid(M):
    try: 
        M.tetrahedra_shapes(bits_prec=212)
        return True
    except ValueError:
        return False

def remaining_exceptional(task):
    manifold = snappy.ManifoldHP(task['name'])
    known = eval(task['fillings'])
    for slope in eval(task['other_exceptional']):
        known[slope] = 'other_exceptional'
    L = dehn.NormalizedCuspLattice(manifold)
    ans = []
    for s in L.primitive_elements():
        if tuple(s) not in known:
            proved_hyperbolic = False
            M = manifold.copy()
            M.dehn_fill(s, 0)
            if not (dehn.appears_hyperbolic(M) and
                    solution_valid(M) and
                    hyperbolic.is_hyperbolic(M)):
                ans.append(s)
    task['new_exceptional'] = repr(ans)
    task['done'] = True

task0 = {'name':'o9_39593', 'fillings':'dict()', 'other_exceptional':'dict()'}
task1 = {'name':'o9_00523', 'fillings':'dict()', 'fillings':'dict()'}
task2 = {'fillings': "{(1, 3): 'v2802(1, 3)', (-1, 5): 'v2802(-1, 5)', (2, 1): 's663(-3, 2)', (-2, 5): 'v2802(-2, 5)', (5, 1): 'v2802(5, 1)', (1, 2): 's667(1, 2)', (-2, 1): 'm303(-2, 3)', (-5, 1): 'v2802(-5, 1)', (-4, 3): 'v2802(-4, 3)', (1, 5): 'v2802(1, 5)', (-3, 2): 'v2802(-3, 2)', (4, 1): 'v2802(4, 1)', (3, 2): 'v2802(3, 2)', (-1, 2): 's572(3, 2)', (1, 4): 'v2802(1, 4)', (-3, 1): 'v2739(-2, 3)', (2, 3): 'v2802(2, 3)', (-3, 4): 'v2802(-3, 4)', (1, 0): 'finite', (-5, 3): 'v2802(-5, 3)', (-2, 3): 'v2802(-2, 3)', (5, 2): 'v2802(5, 2)', (3, 1): 'v2802(3, 1)', (-1, 3): 'v2802(-1, 3)', (-4, 1): 'v2802(-4, 1)', (4, 3): 'v2802(4, 3)', (-1, 4): 'v2802(-1, 4)', (-5, 2): 'v2802(-5, 2)', (3, 4): 'v2802(3, 4)'}",
 'finite': '[(1, 0)]',
 'name': 'v2802',
 'other_exceptional': '[(-1, 1), (1, 1)]'}

taskdb2.worker.run_function('cusped_fillings', 'task_stupid', remaining_exceptional)

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
