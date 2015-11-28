"""
Proving that a given closed manifold is hyperbolic.
"""
import snappy
import taskdb2
import pandas as pd

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
        while prec < 500:
            try:
                if M.verify_hyperbolicity()[0]:
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
