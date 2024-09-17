# patch_madmom.py
import fileinput

files_to_patch = [
    "/usr/local/lib/python3.9/site-packages/madmom/io/__init__.py",
    "/usr/local/lib/python3.9/site-packages/madmom/evaluation/chords.py",
    # Add other files that need patching if necessary
]

for file in files_to_patch:
    with fileinput.FileInput(file, inplace=True) as file:
        for line in file:
            line = line.replace("np.float", "float")
            line = line.replace("np.int", "int")
            print(line, end='')