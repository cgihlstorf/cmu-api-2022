import os

def ensure_same_files(pres_dir:str, abs_dir:str):
    pres_dir_files = [] #present
    abs_dir_files = [] #absent

    for current_dir, subdir, files in os.walk(pres_dir, topdown=True):
        for file in files:
            pres_dir_files.append(file)
    
    for current_dir, subdir, files in os.walk(abs_dir, topdown=True):
        for file in files:
            abs_dir_files.append(file)

    if len(pres_dir_files) > len(abs_dir_files):
        for file in pres_dir_files:
            if file not in abs_dir_files:
                os.remove("with_docstring/docstring_present/" + file) #you can just say pres_dir
    elif len(pres_dir_files) < len(abs_dir_files):
        for file in abs_dir_files:
            if file not in pres_dir_files:
                os.remove("with_docstring/docstring_absent/" + file)
    elif len(pres_dir_files) == len(abs_dir_files):
        print("already equal")


pres_dir = "with_docstring/docstring_present"
abs_dir = "with_docstring/docstring_absent"
ensure_same_files(pres_dir, abs_dir)