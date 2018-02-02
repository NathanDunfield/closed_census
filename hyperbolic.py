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

    # In the closed case, here is another trick.
    if all(not c for c in M.cusp_info('is_complete')):
        for i in range(tries):
            # Drills out a random edge
            X = M.__class__(M.filled_triangulation())
            if all_positive(X):
                return X
            M.randomize()

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

def add_injectivity_cusped(task):
    # Note version was only used for a few outliers
    M = snappy.ManifoldHP(task['name'])
    curves = M.dual_curves()
    if len(curves) > 0:
        likely_systole = curves[0].complete_length.real()
        if likely_systole < 0.01:
            task['inj'] = float(likely_systole)
            task['done'] = True
            return
        cutoff = 1.1 * likely_systole
    else:
        cutoff = 0.34
    spec = []
    while len(spec) == 0:
        try:
            radius = 1.5*cutoff
            spec = M.length_spectrum(cutoff)
        except RuntimeError:
            try:
                D = M.dirichlet_domain(centroid_at_origin=False)
                spec = D.length_spectrum_dicts(cutoff)
            except RuntimeError:
                return 

    task['inj'] = float(spec[0].length.real())
    task['done'] = True

def add_homology(task):
    """
    Infinite order is recorded as 0.  
    """
    M = snappy.Manifold(task['name'])
    H = M.homology()
    divs = H.elementary_divisors()
    task['H_1'] = repr(divs)
    order = H.order()
    if order=='infinite':
        order = 0
    task['H_1_order'] = order
    task['betti'] = H.betti_number()
    task['done'] = True

def basic_invariants_cusped(task):
    M = snappy.ManifoldHP(task['name'])
    task['volume'] = float(M.volume())
    task['chern_simons'] = float(M.chern_simons())
    task['done'] = True
