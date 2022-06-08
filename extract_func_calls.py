import re
import ast

#TODO make comments nicer
#TODO still need to take into account variables (create a symbol table?)
#TODO torch regex isn't working in the first function
#TODO get parameters 
#TODO find more examples of tf/pt code --> save results in CSV file
#TODO specify PyTorch or Tensorflow by import statement

'''Takes a Python file and a two-letter code ('tf' (for Tensorflow) or 'pt' (For PyTorch)). 
Searches for a list of all of the (either Tensorflow or PyTorch) function calls found in the code
using a regular expression, and returns a list of them.'''
def regex_extractor(python_file: str, api_name: str) -> list: #api_name is either 'tf' (for Tensorflow) or 'pt' (For PyTorch)
    list_of_funcs = []

    file = open(python_file, "r")
    file_lines = file.readlines()
    regex = ""

    #Determine whether to seach for Tensorflow or PyTorch functions
    if api_name == "tf":
        regex = "(tf\.+.*|tensorflow\.+^org)" 
    elif api_name == "pt":
        regex = "torch\.+.*" #I'm still trying to figure out why the ^org isn't working with this...
    else:
        raise ValueError("Invalid entry to function regex_extractor(). Must be either 'tf' (Tensorflow) or 'pt' (PyTorch)") 

    #Compile a list of all relevant function calls
    for line in file_lines:
        line_list = re.findall(regex, line)
        if line_list != []: 
            print(line_list[0])
            list_of_funcs.append(line_list[0])
    
    return list_of_funcs

'''Takes a Python file and a two-letter code ('tf' (for Tensorflow) or 'pt' (For PyTorch)). 
Searches for a list of all of the (either Tensorflow or PyTorch) function calls found in the code
by examining the code's AST, and returns a list of them.'''
def AST_extractor(python_file: str) -> list: 
    list_of_funcs = []
    retrieved_ast = open(python_file, "r")
    python_tree = ast.parse(retrieved_ast.read(), mode='exec')
    valid_funcs = collect_valid_funcs(python_tree)

    #find all function nodes in the tree, format them to be readable, and add them to a list be returned by the function
    for node in ast.walk(python_tree): #inspired by: https://greentreesnakes.readthedocs.io/en/latest/manipulating.html?highlight=visit#working-on-the-tree 
        if isinstance(node, ast.Call): #this is erroring in torch
            ast_func_string = ast.dump(node.func, annotate_fields=False, include_attributes=False) #get string representation of AST function)
            ast_func_string = ast_func_string.split("Name")[1] #clean up the string representation - remove references to types of AST nodes and AST formatting
            ast_func_list = ast_func_string.split(",")
            formatted_func_list = [] #use to hold futher formatted elements of ast_func_list 
            func_as_string = "" #this will be used in the final concatenation phase
            
            #clean up the formatting of each element in ast_func_list which may have AST formatting
            for i in range (len(ast_func_list)):
                element = ast_func_list[i]
                #get rid of quotes, parens, and extra spaces from previous formatting
                element = element.replace("\'", "") 
                element = element.replace(")", "") 
                element = element.replace("(", "") 
                element = element.replace(" ", "") 
                element = element.replace("\"", "") 
                if i == 0 and element not in valid_funcs:
                    break
                formatted_func_list.append(element)

            #params stuff here: 
            ast_args = "" 
            args_list = node.args
            for i in range (len(args_list)):
                arg_string = ast.dump(args_list[i], annotate_fields=False, include_attributes=False)
                #print(arg_string)
                if i == len(args_list) - 2:
                    ast_args = ast_args + arg_string
                else:
                    ast_args = ast_args + arg_string + ","


            #keyword stuff here:
            #TODO write this code

            #dots used to load functions and empty function parameters are represented using 'Load()'
            #Replace 'Load' with '.' or '()', depending on the context specified above, and add the element
            #If element is not 'Load()', simply add it
            #I still need to address the case for nonempty function parameters
            for i in range (len(formatted_func_list)):
                if formatted_func_list[i] == "Load":
                    if i == len(formatted_func_list) - 1: 
                        func_as_string = func_as_string + "()" #add params here later
                    else:
                        func_as_string = func_as_string + "."
                else:
                    func_as_string = func_as_string + formatted_func_list[i]      
            
            list_of_funcs.append(func_as_string) #TODO fix so that len() function doesn't show up

    return list_of_funcs

def collect_valid_funcs(python_tree: ast) ->list :
    #TODO comment this function
    valid_funcs = []
    #trying to get rid of python functions...
    for node in ast.walk(python_tree): #inspired by: https://greentreesnakes.readthedocs.io/en/latest/manipulating.html?highlight=visit#working-on-the-tree 
        if isinstance(node, ast.Import):
            for name in node.names:
                alias_name = ast.dump(name, annotate_fields=False, include_attributes=False).split(",")[1]
                valid_funcs.append(alias_name)
        elif isinstance(node, ast.alias):
            alias_name = ast.dump(node, annotate_fields=False, include_attributes=False).split(",")[1]
            valid_funcs.append(alias_name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                target_string = ast.dump(target, annotate_fields=False, include_attributes=False)
                formatted_target = target_string.split("Name")[1].split(",")[0]
                valid_funcs.append(formatted_target)
        #find examples of these instances below so you know how to format them correctly
        # elif isinstance(node, ast.AnnAssign):
        #     print("AnnAssign:")
        #     print(ast.dump(node, annotate_fields=False, include_attributes=False))
        # if isinstance(node, ast.AugAssign):
        #     print(ast.dump(item, annotate_fields=False, include_attributes=False))

    formatted_funcs = []

    for element in valid_funcs:
        new_element = element.replace("\'", "") 
        new_element = new_element.replace(")", "") 
        new_element = new_element.replace("(", "") 
        new_element = new_element.replace(" ", "") 
        new_element = new_element.replace("\"", "") 
        formatted_funcs.append(new_element)
  
    return formatted_funcs

  

#=====================================================Debugging=====================================================#

# for item in regex_extractor("test_tf.py", "tf"):
#     print(item)

# for item in regex_extractor("test_pt.py", "pt"):
#     print(item)

for item in AST_extractor("test_tf.py"):
    print(item)

# for item in AST_extractor("test_pt.py"):
#     print(item)
