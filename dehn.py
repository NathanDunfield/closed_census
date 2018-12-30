"""
Dehn fillings of 1-cusped hyperbolic 3-manifolds.
"""

from sage.all import (gcd, vector, matrix, sqrt,
                      ComplexField, RealField, FreeModule,
                      ZZ) 
import snappy
import hyperbolic

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

class NormalizedCuspLattice:
    """
    The Euclidean cusp lattice of a 1-cusped hyperbolic 3-manifold,
    where the horotorus has been scaled to have area 1.

    >>> M = snappy.Manifold('m003')
    >>> L = NormalizedCuspLattice(M)
    >>> len(L.primitive_elements())
    60
    """
    def __init__(self, manifold):
        assert manifold.num_cusps() == 1
        if isinstance(manifold, snappy.Manifold):
            CC = ComplexField(53)
        elif isinstance(manifold, snappy.ManifoldHP):
            CC = ComplexField(212)
        m, l = 1, manifold.cusp_info(0).shape
        m, l = vector(CC(m)), vector(CC(l))
        root_area = sqrt(abs(matrix([m,l]).det()))
        self.m, self.l = m, l = m/root_area, l/root_area
        self.gram = matrix( [[m*m, m*l], [m*l, l*l]] )
        self.CC = CC

    def norm(self, v):
        return sqrt(v * self.gram * v)

    def primitive_elements(self, max_length=7.6):
        """
        Default max_length ensures that for any longer slope the filling
        is hyperbolic with core geodesic *shorter* than 0.17.  See
        Remark 5.8 on page 410 of Hodgson-Kerckhoff for details.
        """
        # To find all slopes up to the specified length, we need to
        # know how much shorter a vector can be in the cusp lattice as
        # compared to the norm of the corresponding vector in Z^2.  As
        # the gram matrix G can be orthogonally diagonalized, this is
        # precisely determined by the square root of the smallest
        # eigenvalue of G.

        CC = self.CC
        RR = RealField(CC.prec())
        eigenvals = self.gram.charpoly().roots(CC, False)
        L = RR(max_length)/sqrt(min(abs(x) for x in eigenvals))
        ans = []
        for n in range(1, L + 1):
            for p in half_square(n, primitive=True):
                if self.norm(p) <= max_length:
                    ans.append(p)
        ans.sort(key=self.norm)
        return ans

    def __repr__(self):
        return "<CuspLattice %s %s>" % (self.m, self.l)

def test_cusp_lattice_primitive_elements(num_tests=10):
    """
    Check that "primitive_elements" is really getting everything up to
    the specified cutoff.

    >>> test_cusp_lattice_primitive_elements()
    """
    C = snappy.OrientableCuspedCensus(cusps=1)
    for i in range(num_tests):
        M = C.random()
        L = NormalizedCuspLattice(M)
        prim_elts1 = L.primitive_elements(5)
        prim_elts2 = [e for e in L.primitive_elements(10) if L.norm(e) <= 5]
        assert prim_elts1 == prim_elts2

def appears_hyperbolic(M):
    """
    This example returns the complete structure even though we asked
    for something on the Dehn filling.

    >>> M = snappy.Manifold('m305(1, 0)')
    >>> appears_hyperbolic(M)
    False
    """
    acceptable = ['all tetrahedra positively oriented',
                  'contains negatively oriented tetrahedra']
    if M.solution_type() in acceptable and M.volume() > 0:
        for cusp in M.cusp_info():
            if not cusp.is_complete:
                if cusp.core_length.real() < 1e-10:
                    return False
        return True
    else:
        return False
        
def approx_systole(M):
    """
    >>> M = snappy.ManifoldHP('s918(-5, 1)') 
    >>> N = snappy.ManifoldHP('o9_33519(-2, 1)') 
    >>> M.is_isometric_to(N)
    True
    >>> float(approx_systole(M)) == float(approx_systole(N))
    True
    >>> float(approx_systole(M))
    0.36951117321124866
    """
    c = M.cusp_info(0).core_length
    d = M.dual_curves()[0]
    return min(c.real(), d['filled_length'].real())

def hyperbolic_dehn_fillings(manifold, min_core_geod=0.2):
    """
    >>> M = snappy.ManifoldHP('s000')
    >>> len(hyperbolic_dehn_fillings(M))
    16
    """
    assert min_core_geod > 0.17
    L = NormalizedCuspLattice(manifold)
    ans = []
    for s in L.primitive_elements():
        M = manifold.copy()
        M.dehn_fill(s, 0)
        if appears_hyperbolic(M):
            c = M.cusp_info(0).core_length
            if c.real() >= min_core_geod:
                d = M.dual_curves()[0]
                if d['filled_length'].real() >= min_core_geod:
                    ans.append(s)
    return ans

def initial_list_of_closed():
    import csv
    file = open('/pkgs/tmp/closed.csv', 'w')
    writer = csv.writer(file)
    writer.writerow(['name','slopes'])
    for M in snappy.OrientableCuspedCensus(cusps=1):
        slopes = hyperbolic_dehn_fillings(M)
        writer.writerow([M.name(), repr(slopes)])
        file.flush()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    M = snappy.Manifold('m003')
    L = NormalizedCuspLattice(M)
