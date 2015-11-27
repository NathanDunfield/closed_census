import snappy
import pandas as pd
import taskdb2

fill_col = 'inj_02'

census = snappy.OrientableCuspedCensus

def filling_data():
    exdb = taskdb2.ExampleDatabase('cusped_fillings')
    df = exdb.dataframe()
    ans = dict()
    for i, row in df.iterrows():
        ans[row['name']] = eval(row[fill_col])
    return ans

#fillings = filling_data()

def sort_key(name):
    num_tet = {'m':5, 's':6, 'v':7, 't':8, 'o':9}
    return (num_tet[name[0]], name)

def weed(task):
    name = task['name']
    manifold = snappy.Manifold(name)
    slopes = eval(task[fill_col])
    weeded = []
    for s in slopes:
        M = manifold.copy()
        M.dehn_fill(s)
        for i in M.dual_curves():
            X = M.drill(i)
            X = X.filled_triangulation()
            Y = census.identify(X)
            if Y and sort_key(Y.name()) < sort_key(M.name()):
                try:
                    isos = X.is_isometric_to(Y, True)
                except RuntimeError:
                    X.randomize()
                    X = X.high_precision()
                    Y = Y.high_precision()
                    try:
                        isos = X.is_isometric_to(Y, True)
                    except RuntimeError:
                        isos = []
                for iso in isos:
                    C = iso.cusp_maps()[0]
                    t = (C[0,0], C[1,0])
                    weeded.append((M.name() + repr(s), Y.name() + repr(t)))
    task['precursors'] = repr(sorted(set(weeded)))
    task['done'] = True

task = {'name': 'o9_35571', fill_col:'[(-5, 1), (-4, 1), (-3, 1), (-3, 2), (-2, 1), (-2, 3), (-1, 1), (-1, 2), (-1, 3), (-1, 4), (1, 2), (1, 3), (1, 4), (1, 5), (2, 1), (2, 3), (2, 5), (3, 1), (3, 2), (3, 4), (3, 5), (4, 1), (4, 3), (4, 5), (5, 1), (5, 2), (5, 3), (5, 4), (6, 1)]'}
                
            
                
    
    
    
    
