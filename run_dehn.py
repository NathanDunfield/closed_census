#! /bin/env sage-python
#
#SBATCH --partition m
#SBATCH --tasks=1
#SBATCH --mem-per-cpu=4096
#SBATCH --nice=10000
#SBATCH --time=7-00:00
#SBATCH --output=slurm_out/%j
#SBATCH --error=slurm_error/%j

import taskdb2, snappy, dehn

def create_database():
    names = [M.name() for M in snappy.OrientableCuspedCensus(cusps=1)]
    cols = [('finite', 'text'), ('inj_02', 'text')]
    taskdb2.ExampleDatabase('cusped_fillings', names, cols)
    
def find_fat_fillings(task):
    M = snappy.ManifoldHP(task['name'])
    slopes = dehn.hyperbolic_dehn_fillings(M, 0.2)
    task['inj_02'] = repr(sorted(slopes))
    task['done'] = True

exdb = taskdb2.ExampleDatabase('cusped_fillings')
exdb.run_function('task_inj02', find_fat_fillings, num_tasks=1)
