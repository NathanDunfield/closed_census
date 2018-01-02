""" 
In order to completely determine which QHSpheres are L-spaces, it is
necessary to add in two cusped manifolds that have 11 tetrahedra
ideal triangulations.
"""

import snappy
import pandas as pd
import dehn, hyperbolic, finite

o11_A_isosig = 'lLLLLQMMcbeffihiihjkkxxhxscksbtxr_aBBb'
o11_B_isosig = 'lLLLwMPQccddeghikkjjkhswtrlugscfn_BbBa'

A = snappy.Manifold(o11_A_isosig)
A.set_name('o11_A')
B = snappy.Manifold(o11_B_isosig)
B.set_name('o11_B')

columns = ['name', 'isosig', 'finite', 'fillings', 'betti']

C = snappy.Manifold('m004')


def classify_fillings(M, closed):
    ans = dict()
    slopes = dehn.hyperbolic_dehn_fillings(M)
    for slope in slopes:
        C = M.copy()
        C.dehn_fill(slope)
        vol = C.volume()
        matches = closed[abs(closed.volume - vol) < 1e-6]
        for i, row in matches.iterrows():
            X = snappy.Manifold(row['name'])
            try:
                if X.is_isometric_to(C):
                    ans[tuple(slope)] = str(row['name'])
            except RuntimeError:
                pass
    return ans

def manifold_info(manifold, closed_table):
    ans = dict()
    ans['name'] = manifold.name()
    ans['isosig'] = manifold.triangulation_isosig()
    ans['finite'] = finite.finite_fillings(manifold)
    ans['fillings'] = classify_fillings(manifold, closed_table)
    for slope in ans['finite']:
        ans['fillings'][slope] = 'finite'
    ans['betti'] = manifold.homology().betti_number()
    return ans


def save_extras(extras=None, closed_table=None):
    if extras is None:
        extras = []
        for i, row in pd.read_csv('extra_cusped_raw_2.csv').iterrows():
            M = snappy.Manifold(row['name'])
            M.set_peripheral_curves('shortest')
            M.set_name('X_%d' % i)
            extras.append(M)
    if closed_table is None:
        closed_table = pd.read_csv('closed.csv.bz2')
    extra = [manifold_info(M, closed_table) for M in extras]
    data = pd.DataFrame(data=extra, columns=columns)
    data.to_csv('extra_cusped_2.csv', index=False)


closed_table = pd.read_csv('closed.csv.bz2')

def process_manifold_info(task):
    manifold = snappy.Manifold(task['isosig'])
    finite_fill = finite.finite_fillings(manifold)
    all_fill = classify_fillings(manifold, closed_table)
    for slope in finite_fill:
        all_fill[slope] = 'finite'
    task['finite'] = repr(finite_fill)
    task['fillings'] = repr(all_fill)
    task['betti'] = manifold.homology().betti_number()
    task['done'] = True

    
import taskdb2.worker
taskdb2.worker.run_function('extra_cusped', 'task_info', process_manifold_info)
