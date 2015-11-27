import os, sys, re, glob, csv
import pandas as pd
import sage.all
import snappy
import taskdb2

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

def collate_by_manifold():
    df = pd.read_csv('berge_finite_checked.csv.bz2')
    df['base_name'] = df.name.apply(lambda x:x.split('(')[0])
    df['slope'] = df.name.apply(lambda x:eval('(' + x.split('(')[1]))
    gb = df.groupby(['base_name'])
    collated = pd.DataFrame(gb.slope.agg(sorted), columns = ['finite'])
    collated['name'] = collated.index
    collated.to_csv('/tmp/test.csv', index=False, columns=['name', 'finite'])

def check_collated():
    da = pd.read_csv('berge_finite_checked.csv.bz2')
    db = pd.read_csv('berge_finite_checked_collated.csv.bz2')
    db['finite'] = db.finite.apply(eval)
    assert sum(db.finite.apply(len)) == len(da)

def compare_with_new(df):
    #exdb = taskdb2.ExampleDatabase('cusped_fillings')
    #df = exdb.dataframe()
    df = df[df.finite.notnull()]
    df = df[['name', 'finite']]

    db = pd.read_csv('berge_finite_checked_collated.csv.bz2')
    db['finite2'] = db['finite']
    del db['finite']

    da = pd.merge(df, db, on='name')
    return da
