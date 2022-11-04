import pandas as pd

def extract(sheetname):

    '''
    Opens diagnosis_rates.xlsx from current directory
    returns 8x16 extracted df
    '''
    
    # Open file into df
    path = 'diagnosis_rates.xlsx'
    df = pd.read_excel(path,sheet_name=sheetname)

    # Get headers
    headers = ['diagnosis'] + list(df.iloc[0].values[3:-1]) + [90]
    headers = [int(i) if isinstance(i,float) else i for i in headers]

    # Subset rows to table
    df = df.iloc[3:11]

    # Drop cols
    df.drop(['Unnamed: 0','Unnamed: 2'],axis=1,inplace=True)

    # Rename columns
    df.columns = headers

    # Reindex by diagnosis
    df.index=df['diagnosis'].values
    df.drop(['diagnosis'],axis=1,inplace=True)

    return df