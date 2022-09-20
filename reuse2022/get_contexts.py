#imports
import ast
import os
import re
import random
import glob

#TODO COMMENT THIS CODE!!! 
#TODO what about for docstrings that are outside the function declaration?
#TODO include types in functions
#TODO specify the function exceptions you want to except! That way you can ^C haha
#TODO fix pass exceptions!!!


class Function:
    '''Stores information about a function defined in a Python file. Includes
    the function name, function path, function body, function docstring, and 
    the function's start and end lines.'''
    def __init__(self, func_name:str, func_path:str, func_body:str, docstring:str, func_start:int, func_end:int):
        self.name = func_name
        self.path = func_path
        self.body = func_body #includes docstring
        self.docstring = docstring
        self.start = func_start #not sure I need this?
        self.end = func_end
        #self.docstring_indices?
    
    def is_acceptable_func_length(self):
        '''Returns True if the body of the function defined on func_line_number is less than 2048 characters,
        and False if the file is empty or more than 2048 characters.'''
        if self.body.strip() == "":
            #print("got an empty file")
            return False
        elif len(self.body) <= 2048:
            return True
        else:
            return False

    def has_docstring(self):
        '''Returns True if a function has a docstring, and 
        False if it does not have d docstring.'''
        if self.docstring == "None":
            return False
        return True

def get_docstring_indices(context:str, file_path:str, func:Function): #use context which only only goes up to the function def
    '''Comment this!'''
    file = open(file_path, 'r')
    file_lines = file.readlines()
    file.close()
    left_window = 0
    context_length = len(context)
    for line in file_lines[0: func.start - 1]: #stop after to get to the line of the function definition
        left_window = left_window + len(line)
    
    right_window = left_window + 3
    docstring_indices= []

    try:
        #traverse the string with a window to get the start and end character indices of each set of opening and closing docstring quotes
        while right_window <= context_length: #only want to traverse the function body
                if context[left_window:right_window] == "\'\'\'" or context[left_window:right_window] == "\"\"\"":
                    docstring_indices.append(left_window)
                    left_window = left_window + 1 
                    right_window = right_window + 1
                    while right_window <= context_length: #just go through the function body searching for a docstring
                        if context[left_window:right_window] == "\'\'\'" or context[left_window:right_window] == "\"\"\"":
                            docstring_indices.append(right_window)
                        left_window = left_window + 1
                        right_window = right_window + 1
                else:
                    left_window = left_window + 1
                    right_window = right_window + 1

        return str(docstring_indices[0]) + "," + str(docstring_indices[1])

    except:
        #print("Docstring indices corner case:", file_path)
        return "SKIP:" + file_path
    

def has_code_commented(python_file):
    #TODO not used yet...I don't actually think this is a huge issue but I wanted to write the code just in case
    '''Takes in a Python file and returns True of the file contains
    commented-out lines of code, and False otherwise.'''
    ast_file = open(python_file, 'r') 
    codelines = ast_file.readlines()
    ast_file.close()
    for line in codelines:
        if line.strip()[0] == '#': #we've located a comment on its own line (first character is '#')
            line_without_sharp = line[1:] #ignore comment character
            try:
                ast.parse(line_without_sharp)
            except:
                return False #the comment was not code
            return True

def has_nested_function(python_func:ast):
    '''Takes in an ast representation of a Python function
    and returns True if it has another function definition
    within it. Returns False otherwise.'''
    for node in ast.walk(python_func):
        if isinstance(node, ast.FunctionDef):
            return True
    return False


def remove_docstring(context:str, docstring_start, docstring_end) ->str:
    '''Remove docstrings from a given string representation of code. Return a copy of that code
    with its docstring removed.'''
    before_docstring = context[0:docstring_start]
    after_docstring = context[docstring_end + 1:] 
    return before_docstring + after_docstring


def is_corner_case(func:Function, context:str, docstring_start:int, docstring_end:int): #use a switch statement?
        '''Checks to see if the function is one we want to skip, 
        depending on whether it satisfies certain criteria.'''
        #check if the function is an appropriate length
        if not func.is_acceptable_func_length(): #need self as param?
            return True
        #check to see if the function body is simply "pass"
        body_no_ds = remove_docstring(context, docstring_start, docstring_end).strip()
        if body_no_ds[len(body_no_ds) - 4:].strip() == "pass" or body_no_ds[len(body_no_ds) - 4:].strip() == "...":
            #print("skipped pass function")
            return True
        return False


def create_function_list(python_file:str) ->list : 
    '''Creates and returns a list of Function objects created from each
    function in a Python file.'''
    ast_file = open(python_file, 'r') 
    code_as_string = ast_file.read()
    ast_file.close()

    python_tree = ast.parse(code_as_string, mode='exec')
    file_funcs = []

    #for each function definition in the file, map the function name to body, docstring, start line, and end line
    for node in ast.walk(python_tree):
        #TODO get docstring start and end values
            #ideas: use regex to find the docstring given the parsed dosctring plus wherever the quotes are, get start/end lines of that
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            func_path = python_file
            func_body = ast.get_source_segment(code_as_string, node)
            docstring = str(ast.get_docstring(node)) 
            func_start = node.lineno
            func_end = node.end_lineno
            function = Function(func_name, func_path, func_body, docstring, func_start, func_end)
            file_funcs.append(function)
    return file_funcs


def already_exists(directory:str, file:str):
    dir_files = glob.glob(directory + "*.txt")
    if file in dir_files:
        return True
    return False

def write_functions(python_file:str, dest_folder_no_ds:str, dest_folder_ds:str, num_files_skipped:int):
    '''For each function in a file, write, in a new file, as much prior code context as possible
    leading up to the function definition, and stop when the end of the function's body is reached.'''

    #retrieve just the name of the Python file, without any prior path information included
    file_name_list = python_file.split("/")
    file_name = file_name_list[len(file_name_list) - 1]
    file_name = file_name[0: len(file_name) - 3]

    opened_file = open(python_file)
    file_lines = opened_file.readlines()
    opened_file.close() 

    #create a list of the file's functions, each represented as a Function object
    file_funcs = create_function_list(python_file) 
    unique_counter = 0 #will be used for any functions with the same name defined in different classes

    for func in file_funcs: 
        try: #uncommmenting this will make ^C not work :/
            context = ""
            func_name = func.name 
            end_of_func = func.end

            #create a string consisting of the body of func plus any preceding context
            for line in file_lines[0: end_of_func]: 
                context = context + line 
            
            if func.has_docstring():

                docstring_indices = get_docstring_indices(context, python_file, func)
                
                if docstring_indices[0:4] == "SKIP":
                    num_files_skipped = num_files_skipped + 1
                    continue

                indices_list = docstring_indices.split(",")
                docstring_start = int(indices_list[0])
                docstring_end = int(indices_list[1])

                if is_corner_case(func, context, docstring_start, docstring_end):
                    num_files_skipped = num_files_skipped + 1
                    continue


                destination_file = dest_folder_ds + file_name + '_FUNC_' + func_name + '_' + str(unique_counter) + '_.txt'
                
                if already_exists(dest_folder_ds, destination_file): #used for functions with the same name defined in different classes
                    unique_counter = unique_counter + 1
                    destination_file = dest_folder_ds + file_name + '_FUNC_' + func_name + '_' + str(unique_counter) + '_.txt'
                
                output_file = open(destination_file, 'w') 
                output_file.write(docstring_indices + "\n")
                output_file.write(context) 
                output_file.close()
   
            else: #if function in question has no docstring, remove all docstrings from the prior file context

                if is_corner_case(func, context, len(context), len(context)):
                    #print("skipped", func.name, "in", python_file)
                    num_files_skipped = num_files_skipped + 1
                    continue
           
                #TODO: find a way to remove all docstrings in previous context
                destination_file = dest_folder_no_ds + file_name + '_FUNC_' + func_name + '_' + str(unique_counter) + '_.txt'
                
                if already_exists(dest_folder_no_ds, destination_file):
                    unique_counter = unique_counter + 1
                    destination_file = dest_folder_no_ds + file_name + '_FUNC_' + func_name + '_' + str(unique_counter) + '_.txt'
            
                output_file = open(destination_file, 'w') 
                output_file.write(context) 
                output_file.close()

        except: 
            #TODO verify all types of corner cases.
            #skips files that generate an error because their names are too long 
            num_files_skipped = num_files_skipped + 1
            print("Corner case: ", python_file)
            break

    return num_files_skipped

def write_function_files(directory, dest_folder_no_ds, dest_folder_ds):
    '''For all Python files in a given directory, write all the functions of each file to 
    files in the approproate folders.'''
    num_files_skipped = 0
    #for each file in the directory, create files for each of its methods' bodies and docstrings
    for current_dir, subdir, files in os.walk(directory, topdown=True):
        for file in files[0:50000]:
            if file[len(file) - 3:len(file)] != ".py": #only include Python files
                continue
            file_path = current_dir + "/" + file
            num_files_skipped = write_functions(file_path, dest_folder_no_ds, dest_folder_ds, num_files_skipped)
    return num_files_skipped
            
#initialize/open them here?
directory = 'ALL_FILES/all_py_files'
dest_folder_no_ds = 'ALL_FILES/50000_output_ALL_no_docstring/'
dest_folder_ds = 'ALL_FILES/50000_output_ALL_with_docstring/'


print(write_function_files(directory, dest_folder_no_ds, dest_folder_ds))
#print("Number of files skipped:", str(num_files_skipped), "out of", len(glob.glob(directory)), " total files")

#=================================================Testing and Debugging============================================================#
#write_functions('get_docstring_text_processing.py')
# the_dict = create_func_info_dict('get_docstring_text_processing.py')
# print(the_dict)
#get_line_number('create_function_docstring_files', 'get_docstring_text_processing.py')