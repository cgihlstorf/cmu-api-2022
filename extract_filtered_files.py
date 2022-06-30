import ast
import os
import shutil

#recursively go through and find all of the Python files
    #Written
#for each file, see if it imports anything that you need (how to filter out other APIs in the mix?)
    #Written  
#if a file meets the criteria, copy the file into a folder of filtered files 
    #Written
#for each file in this folder of filtered files, find all of the user-defined functions and separate them into folders based on whether or not they have a docstring
#decide what steps to take to measure predictability 

def has_valid_imports(python_file, valid_imports:list ) -> bool:
    #should you filter such that the files have to include only imports from a certain list and no more?
    retrieved_ast = open(python_file, "r")
    python_tree = ast.parse(retrieved_ast.read(), mode='exec')

    #if any import of any file is not in the list of valid imports, skip the file
    for node in ast.walk(python_tree):
        #want to make everything lowercase?
        if isinstance(node, ast.Import):
            for node_name in node.names:
                if node_name.name not in valid_imports: #node_name is of tyoe alias
                    return False
            return True
        elif isinstance(node, ast.ImportFrom):
            if node.module.name not in valid_imports:
                return False
                #I'm not dong anything with the names list because this would exclude keras, etc 
            return True    
        elif isinstance(node, ast.alias):
            if node.name.name not in valid_imports:
                return False
            return True

    return False
        
def find_files(directory, import_names:list, dst): 
    #TODO what type is directory?
    directories_list = []
    files_list = [] 

    #if there is a better way to do this, I'd love to know...   
    for current_dir, subdir, files in os.walk(directory, topdown=True):
        directories_list.append(subdir)
        files_list.append(files)

    #don't attempt to edit directories if there are none
    if directories_list != []:
        directories = directories_list[0]
        for dir in directories:
            find_files(dir, import_names, dst)

    #don't attempt to get files if there are none
    if files_list != []:
        files = files_list[0]
        for file in files:
            start_index = len(file) - 3
            end_index = len(file)
            #only copy files ending in '.py' with the specified imports
            if file[start_index:end_index] == ".py" and has_valid_imports(file, import_names) == True:  
                shutil.copy(file, dst)

valid_imports = ['tensorflow', 'numpy', 'nltk', 're', 'sys', 'os', 'ast', 'turtle']

find_files(os.getcwd(), valid_imports, 'test')
