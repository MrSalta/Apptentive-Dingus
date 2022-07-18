
#!/opt/homebrew/bin/python3
from multiprocessing import parent_process
import os
import pandas as pd
import glob
from pathlib import Path
import sys

# Setting working directory
script_dir = Path(__file__).resolve().parent
source_path = (script_dir / '../Put Reports Here').resolve()
key_path = (script_dir / '../').resolve()

# Setting output

dict_key_file = (key_path/'Key.csv')


# Breakpoint
try:
    dict_from_csv = pd.read_csv(
        dict_key_file, header=None, index_col=0).squeeze("columns")
    print('Key file successfully loaded.')
except FileNotFoundError:
    print(
        'Key file was not found. Please make sure Key.csv is located in the \"Python Dingus\" folder.')
    print(dict_key_file)
    sys.exit(1)
except:
    print('Something went wrong when trying to load Key.csv.')

dict_from_csv = {k.replace(u'\xa0', ' '): v.replace(u'\xa0', ' ')
                 for k, v in dict_from_csv.items()}
print("Dictionary loaded successfully from Key file.")

apptentive_exports = source_path.glob(
    '*.csv')
print("Loading files...")
data = []
print("Files Loaded!")
for csv in apptentive_exports:
    frame = pd.read_csv(csv)
    frame['appname'] = os.path.basename(csv).split("(")[0]
    data.append(frame)

df = pd.concat(data)

group = df.columns.str.split('.').str[0]
df = df.fillna('').astype(str).groupby(group, axis=1).apply(
    lambda d: d.apply(','.join, axis=1))

df = df.replace(dict_from_csv)
df = df.replace("\<null\>\|", "", regex=True)
df['6'] = df['6'].replace(r'\.(?!\s|$)', '', regex=True)
df['6'] = df['6'].replace(r'\,(?!\w)|(?<!\w)\,', '', regex=True)
df['6'] = df['6'].str.split(',')
df = df.explode('6')
df.to_csv("../Final File Here/GenieNewOutput.csv")
print("Load and combine completed. The new file is in the \"Final File Here\" folder")
