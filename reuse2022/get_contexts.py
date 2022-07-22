#imports
import ast
import os
import re
import random
import glob

#TODO COMMENT THIS CODE!!!
#TODO what about for docstrings that are outside the function declaration?
#TODO remove '#' comments 
#TODO update comments
#TODO these functions as currently written assume that all docstrings will be written within the function definition
#TODO include types in functions

#corner cases:
    #function body is too long
    #pass
    ########################
    #remove inline comments? What if a function contains mostly comments? How does the AST work for that again? => YOU DECIDE, okay to just do docstring
    #def within def? => depends on AST traversal(you're good) => might affect entropy (won't isolate entropy of inner function) => YOU DECIDE (ignore, compute multiple times)
    #what if all a function does is return None? => this seems okay
    #lines of code commented out in a function? => you could try AST parse on comments, or just to ' #' and add special cases or exclude
    #Entropy stage --> sort by docstring length?

class Function:
    '''Stores information about a function defined in a Python file. Includes
    the function name, function body, function docstring, and the function's start and end lines.'''
    def __init__(self, func_name:str, func_body:str, docstring:str, func_start:int, func_end:int):
        self.func_name = func_name
        self.func_body = func_body
        self.docstring = docstring
        self.func_start = func_start #not sure I need this?
        self.func_end = func_end
    
    def is_acceptable_func_length(self):
        '''Returns True if the body of the function defined on func_line_number is less than 2048 characters,
        and False if the file is empty or more than 2048 characters.'''
        if self.func_body == "":
            #print("got an empty file")
            return False
        elif len(self.func_body) <= 2048:
            return True
        else:
            return False

    def has_docstring(self):
        '''Returns True if a function has a docstring, and 
        False if it does not have d docstring.'''
        if self.docstring == "None":
            return False
        return True

    def remove_docstring(self, code_string) ->str:
        '''Remove docstrings from a given string representation of code. Return a copy of that code
        with its docstring removed. Must specify which portion of the code should have docstrings 
        removed (ie, entire file or only one function definition).'''
        return re.sub("[\"\'][\"\'][\"\'](\n|.)*[\"\'][\"\'][\"\']", "", code_string, re.MULTILINE) 

    def is_corner_case(self): #use a switch statement?
        '''Checks to see if the function is one we want to skip.'''
        #see if the function is an appropriate length
        if not self.is_acceptable_func_length(): #need self as param?
            return True
        #check to see if the function body is simply "pass"
        elif self.remove_docstring(self.func_body).strip() == "pass":
            return True
        return False

def create_function_list(python_file:str) ->list : #create a class instead?
    '''Creates and returns a list of Function objects created from each
    function in a Python file.'''
    ast_file = open(python_file, 'r') 
    code_as_string = ast_file.read()
    ast_file.close()

    python_tree = ast.parse(code_as_string, mode='exec')
    file_funcs = []

    #for each function definition in the file, map the function name to body, docstring, start line, and end line
    for node in ast.walk(python_tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            func_body = ast.get_source_segment(code_as_string, node)
            print(func_body)
            docstring = str(ast.get_docstring(node)) 
            func_start = node.lineno
            func_end = node.end_lineno
            function = Function(func_name, func_body, docstring, func_start, func_end)
            file_funcs.append(function)
    
    return file_funcs

def already_exists(directory:str, file:str):
    dir_files = glob.glob(directory + "*.txt")
    if file in dir_files:
        return True
    return False

def write_functions(python_file:str, dest_folder_no_ds:str, dest_folder_ds:str):
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

    for func in file_funcs:
        #try:
            unique_counter = 0
            context = ""
            func_name = func.func_name #just name/end?
            end_of_func = func.func_end
            
            #skip functions whose bodies have more than 2048 characters
            if func.is_corner_case():
                print("skipped", func.func_name, "in", python_file)
                continue
 
            #create a string consisting of the body of func plus any preceding context
            for line in file_lines[0: end_of_func]: 
                context = context + line 

            opened_file_two = open(python_file)#debugging
            file_string = opened_file_two.read()#debugging
            file_string.strip()#debugging
            opened_file_two.close()#debugging
            context.strip()#debugging
            
            if func.has_docstring():
                print("had a docstring")
                destination_file = dest_folder_ds + file_name + '_FUNC_' + func_name + '_' + str(unique_counter) + '_.txt'
                if already_exists(dest_folder_ds, destination_file):
                    unique_counter = unique_counter + 1
                    destination_file = dest_folder_ds + file_name + '_FUNC_' + func_name + '_' + str(unique_counter) + '_.txt'
            else:
                # print("no docstring")
                # destination_file = dest_folder_no_ds + file_name + '_FUNC_' + func_name + '_' + str(unique_counter) + '_.txt'
                # if already_exists(dest_folder_ds, destination_file):
                #     unique_counter = unique_counter + 1
                #     destination_file = dest_folder_no_ds + file_name + '_FUNC_' + func_name + '_' + str(unique_counter) + '_.txt'
                continue #debugging
            
            output_file = open(destination_file, 'w') 
            output_file.write("ORIGINAL FILE: " + python_file + "\n" + file_string + "\n")#debugging
            output_file.write("=====================================================================================================================")#debugging
            output_file.write("\nFUNCTION WITH CONTEXT:\n" + context)#debugging
            output_file.close()#debugging
            # output_file.write(context) 
            output_file.close()

        # except: 
        #     print("Corner case: ", python_file)
        #     break

def write_function_files(directory, dest_folder_no_ds, dest_folder_ds):
    '''For all Python files in a given directory, write all the functions of each file to 
    files in the approproate folders.'''

    file_list = []#debugging

    #for each file in the directory, create files for each of its methods' bodies and docstrings
    for current_dir, subdir, files in os.walk(directory, topdown=True):
        #debugging for now, but below is what we want usually
        for file in files:
            # if file[len(file) - 3:len(file)] != ".py": #only include Python files
            #     continue
            file_list.append(file)#debugging
           
    file = random.choice(file_list)#debugging
    #file = "tensor2tensor__insights__graph.py"#debugging
    file_path = current_dir + "/" + file#debugging
    write_functions(file_path, dest_folder_no_ds, dest_folder_ds)#debugging
    print("done")#debugging
            
directory = 'ALL_FILES/all_py_files'
dest_folder_no_ds = 'ALL_FILES/TestExamples/no_docstring/'
dest_folder_ds = 'ALL_FILES/TestExamples/with_docstring/'

write_function_files(directory, dest_folder_no_ds, dest_folder_ds)

#=================================================Testing and Debugging============================================================#
#write_functions('get_docstring_text_processing.py')
# the_dict = create_func_info_dict('get_docstring_text_processing.py')
# print(the_dict)
#get_line_number('create_function_docstring_files', 'get_docstring_text_processing.py')