import os, sys, re, glob, csv
import pandas as pd
import sage.all
import snappy

num_tet = {'m':5, 's':6, 'v':7, 't':8, 'o':9}
def sort_key(datum):
    name = datum[0]
    return (num_tet[name[0]], name)


def extract_john_to_csv():
    ans = []
    for filename in glob.glob('data/OCC*'):
        for line in open(filename):
            if len(line) > 1 and line[0] in ['m', 's', 'v', 't', 'o']:
                line = line.strip()
                parts = line.split()
                name = parts[0]
                description = ' '.join(parts[1:])
                ans.append((name, description))

    ans.sort(key=sort_key)

    file = open('berge_finite.csv', 'w')
    out = csv.writer(file)
    out.writerow(['name', 'description'])
    out.writerows(ans)

def order_via_magma(name):
    M = snappy.Manifold(name)
    G = M.fundamental_group()
    if G.num_generators() == 0:
        return 1
    MG = sage.all.magma(G)
    return MG.Order().sage()

def check_with_magma():
    df = pd.read_csv('berge_finite.csv')
    df['order'] = df.name.apply(order_via_magma)
    df.to_csv('berge_finite_checked.csv', index=False)
    return df

