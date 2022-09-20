import ast
import os
import shutil

def has_defined_funcs(python_file) -> bool:
    '''Returns True if the Python file has functions defined within it;
    False otherwise.'''
    try:
        retrieved_ast = open(python_file, 'r', encoding='utf-8')
        python_tree = ast.parse(retrieved_ast.read(), mode='exec')

        for node in ast.walk(python_tree):
            if isinstance(node, ast.FunctionDef):
                return True
        return False

    except:
        #ignore code with errors in it
        return False


def has_valid_imports(python_file, valid_imports:list ) -> bool:
    '''Returns True if a Python file has some or all of the imports
    in a given list of valid imports, but no others. This was created
    to filter out any imports I wasn't familiar with so I could better
    analyze code examples.'''
    #right now this function takes any files with at least one valid function
    file_imports = set()  

    try:
        retrieved_ast = open(python_file, 'r', encoding='utf-8')
        python_tree = ast.parse(retrieved_ast.read(), mode='exec')

        for node in ast.walk(python_tree):
            #want to make everything lowercase?
            if isinstance(node, ast.Import):
                for node_name in node.names:
                    file_imports.add(node_name.name)
            elif isinstance(node, ast.ImportFrom):
                file_imports.add(node.module)                  
            elif isinstance(node, ast.alias):
                file_imports.add(node.name)
    
        #only include a file if every import in it is in out set of valid imports
        for file_import in file_imports:
            if file_import not in valid_imports:
                return False
        return True

    except:
        #ignore code with errors in it
        return False
        
    

def find_files(directory, import_names:set, dst): 
    '''Goes through a directory of Python files and copies those
    that a) have at least one function defined within them and b)
    have all of their imports belonging to the input list of valid imports.'''
    file_lists = [] 
    current_directory = ""

    #if there is a better way to do this, I'd love to know...   
    for current_dir, subdir, files in os.walk(directory, topdown=True):
        for file in files:
            file_path = current_dir + "/" + file
            start_index = len(file) - 3
            end_index = len(file)
            #only copy files ending in '.py' with the specified imports
            if file[start_index:end_index] == ".py" and has_valid_imports(file_path, import_names) and has_defined_funcs(file_path):  
                #print(file_path)
                shutil.copy(file_path, dst)
    

valid_imports = {'tensorflow', 'numpy', 'torch'} #this is a smaller set of imports I used to create a more limited folder of files with.
#The files I used for my research project included more imports, including os, system, ast, and Turtle.

#check to make sure paths accurately reflect change to reuse2022
# path_to_train_files = '../../../data/vincent/Mining/CodeData/PythonData/Training'
# path_to_test_files = '../../../data/vincent/Mining/CodeData/PythonData/Testing'

source_file = 'all_py_files'
destination_file = 'ml_py_files'

find_files(source_file, valid_imports, destination_file)
