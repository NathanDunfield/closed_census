"""
Proving that a given closed manifold is hyperbolic.
"""
import hashlib
import snappy
import taskdb2
import pandas as pd
import sage.all

def all_positive(manifold):
    return manifold.solution_type() == 'all tetrahedra positively oriented'

def find_positive_triangulation(manifold, tries=100):
    M = manifold.copy()
    for i in range(tries):
        if all_positive(M):
            return M
        M.randomize()
    for d in M.dual_curves():
        X = M.drill(d)
        X = X.filled_triangulation()
        X.dehn_fill((1,0))
        for i in range(tries):
            if all_positive(X):
                return X
            X.randomize()

def verify_hyperbolic_basic(manifold):
    M = find_positive_triangulation(manifold)
    if M is not None:
        prec = 53
        while prec < 1000:
            try:
                if M.verify_hyperbolicity(bits_prec=prec)[0]:
                    return True
            except RuntimeError:
                print('Treating exception in verify code as a failure')
            prec = 2*prec                
    return False

def is_hyperbolic(manifold):
    if verify_hyperbolic_basic(manifold):
        return True
    else:
        for d in range(1, 7):
            for C in manifold.covers(d):
                if verify_hyperbolic_basic(C):
                    return True

def basic_test():
    df = pd.read_csv('closed.csv.bz2')
    for i, row in df.iterrows():
        M = snappy.Manifold(row['name'])
        if is_hyperbolic(M) != True:
            print M

def basic_test_2():
    df = pd.read_csv('closed.csv.bz2')
    for i, row in df.iterrows():
        M = snappy.ManifoldHP(row['name'])
        M.dirichlet_domain()
        print M
                
def create_db():
    df = pd.read_csv('closed.csv.bz2')
    cols = [('verified', 'tinyint'), ('volume', 'double'), ('inj', 'double'),
            ('chern_simons', 'double'), ('group_hash', 'text')]
    exdb = taskdb2.ExampleDatabase('closed_02', df['name'], cols)
    return exdb

def basic_invariants(task):
    name = task['name']
    base, fill = name.split('(')
    M = snappy.ManifoldHP(base)
    M.chern_simons()
    M.dehn_fill(eval('(' + fill))
    task['volume'] = float(M.volume())
    task['chern_simons'] = float(M.chern_simons())
    if is_hyperbolic(M.low_precision()):
        task['verified'] = True
        task['done'] = True

def subgroup_hash(G, H, lite):
    C = G.Core(H)
    ans = [G.Index(H), G.Index(C), H.AQInvariants()]
    if not lite:
        ans.append(C.AQInvariants())
    return [x.sage() for x in ans]

def hash_magma_group(G, index, lite=False):
    sgs = G.LowIndexSubgroups("<1,%d>" % index)
    return sorted([subgroup_hash(G, H, lite) for H in sgs])

def basic_magma_hash(M, index=6):
    G = sage.all.magma(M.fundamental_group())
    raw_hash = hash_magma_group(G, index+1)
    return (index, hashlib.md5(repr(raw_hash)).hexdigest())

def basic_magma_hash_lite(M, index=6):
    G = sage.all.magma(M.fundamental_group())
    raw_hash = hash_magma_group(G, index+1, lite=True)
    return (index, 'lite', hashlib.md5(repr(raw_hash)).hexdigest())

def add_magma_hash(task):
    name = task['name']
    M = snappy.Manifold(name)
    task['group_hash'] = repr(basic_magma_hash(M))
    task['done'] = True

def add_magma_hash_10(task):
    name = task['name']
    M = snappy.Manifold(name)
    task['group_hash_10'] = repr(basic_magma_hash_lite(M, index=10))
    task['done'] = True

def add_magma_hash_simple_quo(task):
    M = snappy.Manifold(task['name'])
    G = sage.all.magma(M.fundamental_group())
    raw_hash = []
    for homs in G.SimpleQuotients(10000, Limit=10**10):
        for h in homs:
            H = G.sub(h)
            raw_hash.append(subgroup_hash(G, H, True))
    raw_hash = sorted(raw_hash)
    task['group_hash_simple'] = hashlib.md5(repr(raw_hash)).hexdigest()
    task['done'] = True

def add_injectivity_radius(task):
    M = snappy.ManifoldHP(task['name'])
    radius = 0.34
    spec = []
    try:
        while len(spec) == 0:
            radius = 1.5*radius
            spec = M.length_spectrum(radius)
        task['inj'] = float(spec[0].length.real())
        task['done'] = True
    except RuntimeError:
        return
