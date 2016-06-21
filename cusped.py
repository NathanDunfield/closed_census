import snappy
import taskdb2
import collections

def get_dataframe():
    exdb = taskdb2.ExampleDatabase('cusped_fillings')
    df = exdb.dataframe()
    for col in ['inj_02', 'precursors', 'fillings']:
        df[col] = df[col].apply(eval)
    return df

def set_fillings():
    cusped_db = taskdb2.ExampleDatabase('cusped_fillings')
    closed_db = taskdb2.ExampleDatabase('closed_02')
    cusped = cusped_db.dataframe()
    closed = closed_db.dataframe()
    cusped_dict = collections.defaultdict(dict)

    # Set the finite fillings
    for i, row in cusped.iterrows():
        for slope in eval(row['finite']):
            cusped_dict[row['name']][slope] = 'finite'

    # Now for the hyperbolic ones
    for i, row in closed.iterrows():
        for description in eval(row['descriptions']):
            name, slope = description.split('(')
            slope = eval('(' + slope)
            cusped_dict[name][slope] = row['name']

    cusped['fillings'] = cusped.name.apply(lambda n:repr(cusped_dict[n]))
    cusped_db.update_column(cusped, 'fillings')

#if __name__ == '__main__':
#    df = get_dataframe()
