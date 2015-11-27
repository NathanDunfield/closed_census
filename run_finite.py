#! /bin/env sage-python
#
#SBATCH --partition m
#SBATCH --tasks=1
#SBATCH --mem-per-cpu=4096
#SBATCH --nice=10000
#SBATCH --time=7-00:00
#SBATCH --output=slurm_out/%j
#SBATCH --error=slurm_error/%j
#SBATCH --nodelist=keeling-e01

import taskdb2, snappy, finite

def find_finite_fillings(task):
    M = snappy.ManifoldHP(task['name'])
    slopes = finite.finite_fillings(M)
    task['finite'] = repr(sorted(slopes))
    task['done'] = True

exdb = taskdb2.ExampleDatabase('cusped_fillings')
exdb.run_function('task_finite', find_finite_fillings, num_tasks=1)
