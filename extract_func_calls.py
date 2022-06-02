import re
import ast

#TODO make comments nicer
#TODO still need to take into account variables (create a symbol table?)
#TODO torch regex isn't working in the first function

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
        regex = "torch\.+.*" #I'm trying to do "torch\.+^org" but it isn't working...
    else:
        raise ValueError("Invalid entry to function regex_extractor(). Must be either 'tf' (Tensorflow) or 'pt' (PyTorch)") 

    #Compile a list of all relevant function calls
    for line in file_lines:
        line_list = re.findall(regex, line)
        if line_list != []: 
            list_of_funcs.append(line_list[0])
    
    return list_of_funcs
 
#print(regex_extractor("test_tf.py", "tf"))
#print(regex_extractor("test_pt.py", "pt"))

'''Takes a Python file and a two-letter code ('tf' (for Tensorflow) or 'pt' (For PyTorch)). 
Searches for a list of all of the (either Tensorflow or PyTorch) function calls found in the code
by examining the code's AST, and returns a list of them.'''
def AST_extractor(python_file: str, api_name: str) -> list: #as in the above function, api_name is either tf (Tensorflow) or pt (PyTorch)
    
    retrieved_ast = open(python_file, "r")
    python_tree = ast.parse(retrieved_ast.read())
    tree_string = ast.dump(python_tree, annotate_fields=False)
    tree_list = re.split("\([A-Z]", tree_string) #not sure what to do here...
    list_of_funcs = []

    #print(tree_string)
    #need to figure out how to represent and work with the AST

    if (api_name != "tf" and api_name != "pt"):
        raise ValueError("Invalid entry to function AST_extractor(). Must be either 'tf' (Tensorflow) or 'pt' (PyTorch)") 

    for item in tree_list:
        if api_name in item:
            item = item.replace(item[0:3], "", -1)
            item_as_list = item.split(",")
            list_of_funcs.append(item_as_list[0:len(item_as_list) - 3])

    return list_of_funcs[0]
  

print(AST_extractor("test_tf.py", "tf"))
#print(AST_extractor("test_pt.py", "pt"))
    




