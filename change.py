import pandas as pd

pd.options.mode.chained_assignment = None

new = pd.read_csv('new.csv', error_bad_lines=False, sep=';', index_col=0)
book = pd.read_csv('List_ID.csv', error_bad_lines=False, sep=';', index_col=0)


for index in range(1, 700):
    if book['banned'][index] == 'Yes' or book['banned'][index] == 'Confirm the number':
        book['twiter'][index] = new['twiter'][index]
        book['twiter_pass'][index] = new['twiter_pass'][index]
        book['twitwr_backup_login'][index] = new['twitwr_backup_login'][index]
        book['twiter_backup_pass'][index] = new['twiter_backup_pass'][index]
        book['banned'][index] = 'No'
book.to_csv('new_twitter.csv', sep=';')
print(new)