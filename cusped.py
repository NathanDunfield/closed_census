import snappy
import taskdb2

def get_dataframe():
    exdb = taskdb2.ExampleDatabase('cusped_fillings')
    df = exdb.dataframe()
    for col in ['inj_02', 'precursors']:
        df[col] = df[col].apply(eval)
    return df

if __name__ == '__main__':
    df = get_dataframe()
