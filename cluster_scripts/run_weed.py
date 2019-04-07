#! /bin/env sage-python
#
#SBATCH --partition m
#SBATCH --tasks=1
#SBATCH --mem-per-cpu=4096
#SBATCH --nice=10000
#SBATCH --time=7-00:00
#SBATCH --output=slurm_out/%j
#SBATCH --error=slurm_error/%j

import taskdb2, weed


def fix_weed(task):
    def fix_one(desc):
        name, slope = desc.split('(')
        slope = '(' + slope
        slope = weed.normalize_slope(eval(slope))
        return name + repr(slope)
    pre = eval(task['precursors'])
    task['precursors'] = repr(sorted({(x, fix_one(y)) for x, y in pre}))
    task['done'] = True
        
        
# 1466710
exdb = taskdb2.ExampleDatabase('cusped_fillings')
exdb.run_function('task_weed', fix_weed, num_tasks=1,
                  columns=['precursors'])
