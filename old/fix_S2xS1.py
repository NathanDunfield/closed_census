import snappy
import pandas as pd

def remove_S2xS1():
    """
    Initially, I tested if the fundamental group was cyclic, rather
    than *finite* cyclic, hence idenifying some S^2 x S^1 fillings as
    having finite fundamental group.  This function fixes this by
    removing the (exactly) 200 instances of this phenomina.
    """

    def fix_finite(row):
        M = snappy.Triangulation(row['name'])
        corrected = list()
        for slope in row['finite']:
            M.dehn_fill(slope)
            if M.homology().betti_number() == 0:
                corrected.append(slope)
        return corrected

    df = pd.read_csv('../cusped_fillings.csv.bz2')
    df.finite = df.finite.apply(eval)
    init_count = sum(df.finite.apply(len))
    print('Initially %d "finite" Dehn fillings' % init_count)
    df.finite = df.apply(fix_finite, axis=1)
    final_count = sum(df.finite.apply(len))
    print('Now %d finite Dehn fillings, a difference of %d' %
          (final_count, init_count - final_count))
    df.finite = df.finite.apply(repr)
    df.to_csv('corrected_cusped_fillings.csv', index=False)


remove_S2xS1()
