import pandas as pd


df = pd.read_csv('cr_r_q_ft.csv', index_col='_id')
sum_df = pd.read_csv('sum_cr_r_q.csv', index_col='_id')
fell_df = pd.read_csv('fellonies.csv', index_col='_id')

print(df.info())
print(sum_df.info())
print(fell_df.info())
