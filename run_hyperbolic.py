#! /bin/env sage-python
#
#SBATCH --partition m
#SBATCH --tasks=1
#SBATCH --mem-per-cpu=4096
#SBATCH --nice=10000
#SBATCH --time=7-00:00
#SBATCH --output=slurm_out/%j
#SBATCH --error=slurm_error/%j

import taskdb2, hyperbolic
exdb = taskdb2.ExampleDatabase('closed_02')
exdb.run_function('task_inj', hyperbolic.add_injectivity_radius)
