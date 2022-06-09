import re
import ast

#TODO Figure out how to format keyword values

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
            func_string = create_func_string(node, valid_funcs) 
            if func_string == "": #An empty string is returned if the function does not belong to an imported API
                continue
            else:
                list_of_funcs.append(func_string)         
    return list_of_funcs


'''Takes in an AST function node and a list of valid function names to include in its output;
returns a string representation of the function name, without parameters or keywords.'''
def create_func_string(node: ast, valid_funcs: list) -> str:
    ast_func_string = ast.dump(node.func, annotate_fields=False, include_attributes=False) #get string representation of AST function
    ast_func_string = ast_func_string.split("Name")[1] #remove references to types of AST nodes and other AST formatting
    ast_func_list = ast_func_string.split(",")
    formatted_func_list = [] #used to hold each newly formatted element of ast_func_list 
    func_as_string = "" #our string to return
            
    #get rid of quotes, parens, and extra spaces that the previous clearnup didn't catch
    for i in range (len(ast_func_list)):
        element = ast_func_list[i]
        element = element.replace("\'", "") 
        element = element.replace(")", "") 
        element = element.replace("(", "") 
        element = element.replace(" ", "") 
        element = element.replace("\"", "") 
        if i == 0 and element not in valid_funcs: #don't include the function name if it isn't part of an imported API
            break
        formatted_func_list.append(element)

    #Both dots used to load functions and empty function parameters are represented using 'Load()'
    #Replace 'Load' with '.' or '()', depending on which of the above it represents, and add the element
    for i in range (len(formatted_func_list)):
        if formatted_func_list[i] == "Load":
            if i == len(formatted_func_list) - 1: 
                func_as_string = func_as_string + "(" 
            else:
                func_as_string = func_as_string + "."
        else: #If element is not 'Load()', append it to the output string as-is
            func_as_string = func_as_string + formatted_func_list[i]      

    #for all functions from imported APIs, append string versions of all applicable parameters and keywords
    if func_as_string != "": #ignore non-APi functions, which would still be represented as empty strings at this point
        param_string = get_param_string(node.args, valid_funcs)
        keywords_string = get_keywords_string(node)
        if param_string != "" and keywords_string != "":
            func_as_string = func_as_string + ")" #empty paremeters and keywords
        elif param_string != "" and keywords_string == "":
            func_as_string = func_as_string + param_string + ")" 
        elif param_string == "" and keywords_string != "":
            #I still need to figure out how to format keyword values
            func_as_string = func_as_string + keywords_string + ")" 

    return func_as_string

'''Returns a string representation of a function's parameters. Right now it only returns 
representatons for function parameters or constant parameters.'''
def get_param_string(args: list, valid_funcs: list) ->str: 
    for node in args:
        if isinstance(node, ast.Call):
            return create_func_string(node, valid_funcs)
        elif isinstance(node, ast.Constant):
            return str(node.value)
    return ""

'''Returns a string representation of any keywords parameters of a function and 
an empty string if there are no keyword parameters.'''
#Function is not quite done yet...I still need to account for more types of parateters (ex: tuples) if needed
def get_keywords_string(node: ast) ->str:
    return_string = ""
    for keyword in node.keywords:
        return_string = return_string + keyword.arg + "=" + str(keyword.value) 
    return return_string

'''Takes a Python AST and returns a list of all API references in imports 
and all variable names for API functions from Assign expressions. This will be used
in AST_extractor() to make sure that only functions that are part of imported APIs are 
counted in its output'''
def collect_valid_funcs(python_tree: ast) ->list :
    valid_funcs = []
    #if a node is an import statement or assignment, store its name in a list for future reference
    for node in ast.walk(python_tree): #inspired by: https://greentreesnakes.readthedocs.io/en/latest/manipulating.html?highlight=visit#working-on-the-tree 
        if isinstance(node, ast.Import):
            for name in node.names:
                alias_name = alias_to_string(name)
                valid_funcs.append(alias_name)
        elif isinstance(node, ast.alias):
            alias_name = alias_to_string(name)
            valid_funcs.append(alias_name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                target_string = ast.dump(target, annotate_fields=False, include_attributes=False)
                formatted_target = target_string.split("Name")[1].split(",")[0]
                valid_funcs.append(formatted_target)

        #find examples of these instances below so you know how to format them correctly:

        # elif isinstance(node, ast.AnnAssign):
        #     print("AnnAssign:")
        #     print(ast.dump(node, annotate_fields=False, include_attributes=False))
        # if isinstance(node, ast.AugAssign):
        #     print(ast.dump(item, annotate_fields=False, include_attributes=False))

    formatted_funcs = []

    #remove any extra punctuation/formatting left around the function name
    for element in valid_funcs:
        new_element = element.replace("\'", "") 
        new_element = new_element.replace(")", "") 
        new_element = new_element.replace("(", "") 
        new_element = new_element.replace(" ", "") 
        new_element = new_element.replace("\"", "") 
        formatted_funcs.append(new_element)
  
    return formatted_funcs

'''Takes in an alias object from an import statement and converts the 
alias to a string'''
def alias_to_string(alias : ast.alias):
    alias_name = ast.dump(alias, annotate_fields=False, include_attributes=False).split("alias")[1]
    #if there are multiple names in the alias object (representing the original name and its alias), return only the alias 
    if len(alias_name.split(",")) > 1:
        alias_name = alias_name.split(",")[1]
    return alias_name

#=====================================================Debugging=====================================================#

for item in AST_extractor("test_tf.py"):
    print(item)

for item in AST_extractor("test_pt.py"):
    print(item)

