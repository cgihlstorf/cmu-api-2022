import ast
import os
import shutil

#TODO comment this!

def has_defined_funcs(python_file) -> bool:
    '''comment this'''
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
        
    

   
        
'''comment this too'''
def find_files(directory, import_names:set, dst): 
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
    

valid_imports = {'tensorflow', 'numpy', 'torch'}

#check to make sure paths accurately reflect change to reuse2022
# path_to_train_files = '../../../data/vincent/Mining/CodeData/PythonData/Training'
# path_to_test_files = '../../../data/vincent/Mining/CodeData/PythonData/Testing'

source_file = 'all_py_files'
destination_file = 'ml_py_files'

find_files(source_file, valid_imports, destination_file)
