import re
import ast

#TODO make comments nicer
#TODO still need to take into account variables (create a symbol table?)

'''Takes a Python file and a two-letter code ('tf' (for Tensorflow) or 'pt' (For PyTorch)). 
Returns a list of all of the (either Tensorflow or PyTorch) function calls found in the code.'''
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
print(regex_extractor("test_pt.py", "pt"))

def AST_extractor(python_file: str, api_name: str) -> list: #as in the above function, api_name is either tf (Tensorflow) or pt (PyTorch)
    
    retrieved_ast = open(python_file, "r")
    python_tree = ast.parse(retrieved_ast.read())
    tree_string = ast.dump(python_tree, annotate_fields=False)
    tree_list = tree_string.split("Assign") #not sure what to do here...
    list_of_funcs = []

    #print(tree_string)
    for item in tree_list:
        print(item)

    if api_name == "tf":
        #specify for tf 
        x = 1 #placeholder for now
    elif api_name == "pt":
        #specify for pt
        x = 2 #placeholder for now
    else:
        raise ValueError("Invalid entry to function AST_extractor(). Must be either 'tf' (Tensorflow) or 'pt' (PyTorch)") 

    return list_of_funcs
  



#print(AST_extractor("test_tf.py", "tf"))
#print(AST_extractor("test_pt.py", "pt"))
    




