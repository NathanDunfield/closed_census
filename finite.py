"""
Finding Dehn finite fillings independently, as a check on Berge's
list.

For simplicity (and hence robustness), we ignore the cusp neighborhood and search the below fixed list of slopes.  
"""

import snappy
import sage.all

fixed_slopes = [(-1, 1), (0, 1), (1, 0), (1, 1), (-2, 1), (-1, 2), (1, 2), (2, 1),
          (-3, 1), (-3, 2), (-2, 3), (-1, 3), (1, 3), (2, 3), (3, 1), (3, 2)]

def score_presentation(group):
    return group.num_generators(), sum(len(R) for R in group.relators())
    
def good_presentation(manifold, tries=10):
    M = manifold.copy()
    best_G = M.fundamental_group()
    best_score = score_presentation(best_G)
    for i in range(tries):
        if best_score[0] <= 1:
            break
        M.randomize()
        G = M.fundamental_group()
        score = score_presentation(G)
        if score < best_score:
            best_score, best_G = score, G
    return best_G

def order_via_magma(group):
    if group.num_generators() == 0:
        return 1
    G = sage.all.magma(group)
    return G.Order(CosetLimit=250000).sage()

def has_finite_fundamental_group(manifold):
    M = manifold.high_precision()
    G = good_presentation(manifold)
    if G.num_generators() == 0:
        return True
    elif G.num_generators() == 1:
        return len(G.num_relators()) == 1  # Exclude pi_1 = Z
    return order_via_magma(G) not in [0, sage.all.infinity]

def finite_fillings(manifold):
    """
    >>> M = snappy.Manifold('m003')
    >>> finite_fillings(M)
    [(-2, 1), (-1, 1), (0, 1), (1, 0), (1, 1)]
    """
    ans = []
    for slope in fixed_slopes:
        M = manifold.copy()
        M.dehn_fill(slope)
        if has_finite_fundamental_group(M):
            ans.append(slope)
    return sorted(ans)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
        
    
    
    
    
