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
 
# for item in regex_extractor("test_tf.py", "tf"):
#     print(item)

# for item in regex_extractor("test_pt.py", "pt"):
#     print(item)

'''Takes a Python file and a two-letter code ('tf' (for Tensorflow) or 'pt' (For PyTorch)). 
Searches for a list of all of the (either Tensorflow or PyTorch) function calls found in the code
by examining the code's AST, and returns a list of them.'''
def AST_extractor(python_file: str, api_name: str) -> list: #as in the above function, api_name is either tf (Tensorflow) or pt (PyTorch)
    if (api_name != "tf" and api_name != "pt"):
        raise ValueError("Invalid entry to function AST_extractor(). Must be either 'tf' (Tensorflow) or 'pt' (PyTorch)") 

    list_of_funcs = []
    retrieved_ast = open(python_file, "r")
    python_tree = ast.parse(retrieved_ast.read(), mode='exec')

    #find all function nodes in the tree, format them to be readable, and add them to a list be returned by the function
    for node in ast.walk(python_tree): #inspired by: https://greentreesnakes.readthedocs.io/en/latest/manipulating.html?highlight=visit#working-on-the-tree 
        if isinstance(node, ast.Call) and api_name in ast.dump(node.func): #this is erroring in torch
            #get string representation of AST
            ast_string = ast.dump(node.func)

            #clean up the string representation - remove references to types of AST nodes and AST formatting
            ast_string = ast_string.split("id=")[1]
            ast_list = ast_string.split(",")

            ast_string = "" #reset for reuse
            
            element_list = [] #use to hold futher formatted elements of ast_list

            #further clean up the formatting of each element in ast_list which may have AST formatting
            for element in ast_list:
                if "=" in element:
                    element = element.split("=")[1]
                
                element = element.replace("\'", "") #get rid of quotes from previous formatting
                element_list.append(element)

            #dots used to load functions and empty function parameters are represented using 'Load()'
            #Replace 'Load' with '.' or '()', depending on the context specified above, and add the element
            #If element is not 'Load()', simply add it
            #I still need to address the case for nonempty function parameters
            for i in range (len(element_list)):
                if element_list[i] == "Load())": #complensating for an extra paren left in the string representation
                    if i == len(element_list) - 1:
                        ast_string = ast_string + "()"
                    else:
                         ast_string = ast_string + "."
                else:
                    ast_string = ast_string + element_list[i] 
            
            list_of_funcs.append(ast_string)

    return list_of_funcs
  

#print results of functions
for item in AST_extractor("test_tf.py", "tf"):
    print(item)

# for item in AST_extractor("test_pt.py", "pt"):
#     print(item)

