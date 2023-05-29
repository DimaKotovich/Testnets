import pandas as pd

pd.set_option('display.notebook_repr_html', False)
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', 50)
pd.set_option('display.width', 100)

book = pd.read_csv('list_ID2.csv', error_bad_lines=False, sep=';', index_col=0)
# book = book[300:]
# new = book.loc[(book['banned'] == 'Yes') | (book['banned'] == 'Confirm the number')]
# new.to_csv('banned_twitter.csv', sep=';')
book = book.drop(columns=book.columns[1:4], axis=1)
book.drop(columns=book.columns[5:], axis=1).to_csv('Twitter+DolphinId.csv', sep=';')
