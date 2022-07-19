
#!/opt/homebrew/bin/python3
from os import path as osp
import pandas as pd
from sys import executable as sys
import tkinter as tk
import inspect
from tkinter import filedialog as fd
from tkinter import simpledialog as sd
from tkinter import messagebox as mb

# Function to get the current working directory


def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False):
        path = osp.abspath(sys)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = osp.realpath(path)
    return osp.dirname(path)


# Setting working directory
script_dir = get_script_dir
print(get_script_dir())

# Setting up UI (so to speak)
root = tk.Tk()
w = 800
h = 650

# get screen width and height
ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()

# Calc x and 7 for the tk window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)

root.geometry('%dx%d+%d+%d' % (w, h, x, y))
root.withdraw()
# dict_key_file = (script_dir/'Key.csv')

# Dialog to choose key file
dict_key_file = fd.askopenfilename(
    title='Choose Key File',
    filetypes=(("CSV Files", "*.csv"),))

# Dialog to grab report files
f = fd.askopenfilenames(
    title='Choose Report Files',
    filetypes=(("CSV Files", "*.csv"),))

# Load Key file into dictionary
try:
    dict_from_csv = pd.read_csv(
        dict_key_file,
        header=None,
        index_col=0).squeeze("columns")
    print('Key file successfully loaded.')
  # Handle Key file load error
except FileNotFoundError:
    mb.showerror(title='Key file not found.',
                 message='Key file not found. Please make sure you\'re selecting \"Key.csv\".')
    print(
        'Key file was not found. Make sure you select the proper \"Key.csv\" file.')
    print(dict_key_file)
    sys.exit(1)
except:
    mb.showerror(title='Something went wrong',
                 message='No key file was selected. Canceled by user.')
    print('Something went wrong when trying to load Key.csv.')

# Create dictionary from Key
dict_from_csv = {k.replace(u'\xa0', ' '): v.replace(u'\xa0', ' ')
                 for k, v in dict_from_csv.items()}
print("Dictionary loaded successfully from Key file.")

# Load and read the selected CSVs
data = []
print("Files Loaded!")

# Add the 'appname' column to the dataframe
for csv in f:
    frame = pd.read_csv(csv)
    frame['appname'] = osp.basename(csv).split("(")[0]
    data.append(frame)

# DO: Concat the files
df = pd.concat(data)

# Change the question columns to be just the number, for easier reporting
group = df.columns.str.split('.').str[0]
df = df.fillna('').astype(str).groupby(group, axis=1).apply(
    lambda d: d.apply(','.join, axis=1))

# Read through dictionary and replace resultes
df = df.replace(dict_from_csv)

# Remove the "Null" thingy that shows up on the network column
df = df.replace("\<null\>\|", "", regex=True)

# For multi-select columns, concat into one column, separated by commas
# TODO: There needs to be a way for us to declare which "column" is affected by this
# Ok, going to try by asking if there's a multi-select column first
is_multi = mb.askyesno(
    title='Multi-Select?',
    message='Are there any multi-select questions in this set?',
    parent=root)
if is_multi == True:
    print('Multi-Select column indcated. Asking for number.')
    mc = sd.askstring(
        title='Which question is multi-select?',
        prompt='Which question number is a multi-select field?',
        parent=root)
    print('Column ' + mc + ' selected.')
    print('mc = ' + mc + '.')

    df[mc] = df[mc].replace(r'\.(?!\s|$)', '', regex=True)
    df[mc] = df[mc].replace(r'\,(?!\w)|(?<!\w)\,', '', regex=True)
    df[mc] = df[mc].str.split(',')
    df = df.explode(mc)

# Get file name
file_name = sd.askstring(
    title='File Name',
    prompt='Enter file name',
    parent=root)

# Get save location
save_location = fd.askdirectory(
    parent=root,
    initialdir=osp.join(osp.expanduser('~'), 'Desktop'),
    title='Choose save location')
save_path = (save_location + '/' + file_name + '.csv')

# Actually write the file to the root
df.to_csv(save_path)

print("Load and combine completed. The new file is at " + save_path + ".")
# Close the TK window
mb.showinfo(
    title='Success!',
    message="Load and combine completed. The new file is at " + save_path + ".")
root.destroy()
