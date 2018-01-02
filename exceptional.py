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
            M = manifold.copy()
            M.dehn_fill(s, 0)
            if dehn.appears_hyperbolic(M):
                assert dehn.approx_systole(M) < 0.2
            else:
                ans.append(s)
    task['other_exceptional'] = repr(ans)
    task['done'] = True

task0 = {'name':'o9_39593', 'fillings':'dict()'}

taskdb2.worker.run_function('cusped_fillings', 'task_other', remaining_exceptional)
