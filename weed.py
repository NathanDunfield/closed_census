import snappy
import taskdb2
import pandas as pd
import networkx as nx

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

def normalize_slope((a,b)):
    if a*b == 0:
        a, b = abs(a), abs(b)
    elif b < 0:
        a, b = -a, -b
    return (a,b)

def weed(task):
    """
    WARNING: For future use, need to include relations caused by
    symmetries of a fixed 1-cusp manifold.
    """
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
                    t = normalize_slope((C[0,0], C[1,0]))
                    weeded.append((M.name() + repr(s), Y.name() + repr(t)))
    task['precursors'] = repr(sorted(set(weeded)))
    task['done'] = True


def sort_into_classes(df):
    """
    Check the precursors field for missing fillings, then pick the
    minimal element in each equivalence class.
    """
    closed, images = set(), set()
    for i, row in df.iterrows():
        closed.update(row['name'] + repr(slope) for slope in row[fill_col])
        images.update(x[1] for x in row['precursors'])


    G = nx.Graph()
    G.add_nodes_from(closed)
    for i, row in df.iterrows():
        G.add_edges_from(row['precursors'])

    classes = [sorted(H, key=sort_key) for H in nx.connected_components(G)]
    classes.sort(key=lambda x:sort_key(x[0]))

    ans = pd.DataFrame({'name':[c[0] for c in classes], 'descriptions':classes})
    ans = ans[['name', 'descriptions']]
    ans.to_csv('closed.csv', index=False)
    return ans

task = {'name': 'o9_35571', fill_col:'[(-5, 1), (-4, 1), (-3, 1), (-3, 2), (-2, 1), (-2, 3), (-1, 1), (-1, 2), (-1, 3), (-1, 4), (1, 2), (1, 3), (1, 4), (1, 5), (2, 1), (2, 3), (2, 5), (3, 1), (3, 2), (3, 4), (3, 5), (4, 1), (4, 3), (4, 5), (5, 1), (5, 2), (5, 3), (5, 4), (6, 1)]'}
                
            
                
def refine_classes(df):
    """
    Look at the classes where the (volume, group) hashes colide.
    """
    grouped = df.groupby(['volume', 'group_hash'])
    nontrivial = [tuple(df.name.ix[g]) for g in grouped.groups.values() if len(g) > 1]
    assert {len(g) for g in nontrivial} == {2}
    merge = []
    bad = []
    for a, b in nontrivial:
        A = snappy.Manifold(a)
        B = snappy.Manifold(b)
        if A.name() == B.name():
            for X in [A, B]:
                X.set_peripheral_curves('fillings')
                X.dehn_fill((0,0))
            isoms = A.is_isometric_to(B, True)
            if any(i.extends_to_link() for i in isoms):
                merge.append((a, b))
            else:
                bad.append((a,b))
        else:
            try:
                if A.is_isometric_to(B):
                    merge.append((a,b))
            except RuntimeError:
                bad.append((a,b))
                

    return merge, bad
    
    
