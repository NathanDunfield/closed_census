""" 
This code is to double-check the list of exceptional Dehn fillings.
Specifically, it verifies that all proposed non-exceptional fillings
are hyperbolic.

This file was originally in the repository "closed_census".
"""

import snappy
from sage.all import RealIntervalField, FreeModule, gcd, ZZ

# Enumerating primitive lattice points.  Copied from "dehn.py" to make
# this file self-contained.

ZZ2 = FreeModule(ZZ, 2)

def dehn_filling_filter(a, b):
    return gcd(a,b) == 1 and not (a == 0 and b < 0) and not (a < 0 and b == 0)

def half_square(n, primitive=False):
    """
    All lattice points on the square of 'radius' n
    where y >= 0.   
    """
    top = [ (k, n) for k in range(-n, n)]
    right = [ (n, k) for k in range(0, n + 1)]
    left = [(-n, k) for k in range(0, n)]
    return [ ZZ2(p) for p in left+top+right if not primitive or dehn_filling_filter(*p) ]

def half_filled_square(n, primitive=False):
    ans = []
    for i in range(1, n + 1):
        ans += half_square(i, primitive)
    return ans

# Code to prove a manifold is hyperbolic.  Copied from "hyperbolic.py"
# to make this file self-contained.

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

                
def cusp_translations(manifold):
    trans = manifold.cusp_translations(verified=True, bits_prec=212)
    return trans[0]

def slopes_to_length_six(manifold):
    """ 
    For a 1-cusped manifold, returns a list of slopes such that
    any slope *not* on this list provably has length at least 6.

    >>> M = snappy.Manifold('m004')
    >>> len(slopes_to_length_six(M))
    10
    
    """
    M = manifold
    six = RealIntervalField()(6)
    assert M.num_cusps() == 1
    v, w = cusp_translations(M)
    assert w.imag() == 0  # Make sure w is real
    x = w.abs()
    y = v.imag().abs()
    # Any slope (a, b) will have length at least a x + b y
    n = max(six/x, six/y).upper().ceil()
    def norm((a, b)):
        return (a*v + b*w).abs()
    slopes = half_filled_square(n, primitive=True)
    slopes_by_length = sorted((norm(s), s) for s in slopes)
    return [tuple(s) for (r, s) in slopes_by_length if not(r > six)]


def check_manifold(manifold, excluded_slopes):
    """ 

    When this function returns True, it means that it proved that
    *every* slope not in excluded_slopes is hyperbolic.  It does not
    check in any way that the excluded_slopes are nonhyperbolic.

    >>> M = snappy.Manifold('o9_44223')
    >>> check_manifold(M, [])
    False
    >>> check_manifold(M, [(1, 0)])
    True
    >>> check_manifold(M, [(1, 0), (0, 1), (1,1)])
    True
    
    >>> M = snappy.Manifold('t05185')
    >>> check_manifold(M, [(-1, 1), (0, 1), (1, 0), (1, 1)])
    True
    """
    M = manifold
    slopes = []
    for s in slopes_to_length_six(M):
        if s not in excluded_slopes:
            N = M.copy()
            N.dehn_fill(s)
            if not is_hyperbolic(N):
                return False
    return True

# Code past this point was used for the actual computations which
# involved storing the contents of "cusped_with_exceptional.csv.bz2"
# in a local MySQL database for easy access.  If you want to check the
# main theorem yourself, you should write the analogous code to the
# first function below to process that CSV file.

def test_check_manifold(todo=10):
    import taskdb2
    db = taskdb2.ExampleDatabase('check_exceptional')
    for i, row in db.dataframe().sample(todo).iterrows():
        M = snappy.Manifold(row['name'])
        slopes = eval(row.exceptional_slopes)
        print(M, slopes, check_manifold(M, slopes))
    

def add_slope_length(task):
    name, slope = task['name'].split('(')
    M = snappy.Manifold(name)
    a, b = eval('(' + slope)
    v, w = cusp_translations(M)
    r = (a*v + b*w).abs().lower()
    task['slope_length'] = float(r)
    task['done'] = True

def check_manifold_saving_details(task):
    M = snappy.Manifold(task['name'])
    excluded = eval(task['exceptional_slopes'])
    hyp_slopes = []
    failure = False
    for s in slopes_to_length_six(M):
        if s not in excluded:
            N = M.copy()
            N.dehn_fill(s)
            if is_hyperbolic(N):
                hyp_slopes.append(s)
            else:
                failure = True
                
    task['hyperbolic_slopes'] = repr(hyp_slopes)
    task['passed'] = 0 if failure else 1
    task['done'] = not failure


def add_basic_info(task):
    M = snappy.Manifold(task['name'])
    while not M.solution_type().startswith('all tet'):
        M.randomize()
    task['volume'] = float(M.volume(verified=True, bits_prec=1000))
    assert M.num_cusps() == 1
    v, w = cusp_translations(M)
    assert w.imag() == 0  # Make sure w is real
    cusp_area = w.real() * v.imag()
    task['cusp_area'] = float(cusp_area)
    task['cusp_vol'] = float(cusp_area/2)
    task['merid_len'] = float(v.abs())
    if v.real().abs() < 1e-60:
        v = v - v.real()
    task['cusp_trans'] = repr((complex(v), float(w)))
    task['tets'] = M.num_tetrahedra()
    task['done'] = True


def collate_basic_stats(dataframe):
    import pandas as pd
    pd.set_option('display.precision', 1)
    df = dataframe
    dg = df.groupby('tets')
    cols = ['volume', 'cusp_vol', 'merid_len']
    dg = dg[cols]
    descr_cols = [('volume', 'count')]
    descr_cols += [(col, desc) for col in cols for desc in 
                   ['min', 'mean', 'max', 'std']]
    return dg.describe()[descr_cols]
    
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
