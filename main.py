import pandas as pd

df = pd.read_csv('locale_table.tsv', sep='\t')
df['Code'] = df['Code'].str.lower()
locale_table_dict = df.set_index('Code')['Name'].to_dict()

print(locale_table_dict)