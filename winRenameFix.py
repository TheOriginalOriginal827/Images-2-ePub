# This is a simple program to fix Windows renaming 
# to comply with the required format for Imgs to ePub.
#
# Windows will mass-rename with the wrong format, 
# which is (1).png, (2).jpeg, (3).jfif, etc..
# this program will simply remove the parenthesis
# from files near the .py so it works with Imgs to ePub.

import os

exts = ['.png', '.jpg', '.jpeg', '.jpe', '.jif', '.jfif', '.jfi', '.gif', '.webp']

dir = os.path.dirname(os.path.realpath(__file__))

print(dir)

imgs = [f for f in os.listdir(dir) if f.endswith(tuple(exts))]

for file in imgs:
    img = file
    img = img.replace(" ", "")
    for char in "()":
        img = img.replace(char, "")
    os.rename(os.path.join(dir,file), os.path.join(dir, img))
    
print("Files renamed.")