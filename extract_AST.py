import re
import ast

#TODO make comments nicer
#TODO format parameters and keywords correctly

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


'''Need documentation for this'''
def create_func_string(node: ast, valid_funcs: list) -> str:
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

    #dots used to load functions and empty function parameters are represented using 'Load()'
    #Replace 'Load' with '.' or '()', depending on the context specified above, and add the element
    #If element is not 'Load()', simply add it
    #I still need to address the case for nonempty function parameters
    for i in range (len(formatted_func_list)):
        #why is this outputting empty strings...
        if formatted_func_list[i] == "Load":
            if i == len(formatted_func_list) - 1: 
                func_as_string = func_as_string + "(" 
            else:
                func_as_string = func_as_string + "."
        else:
            func_as_string = func_as_string + formatted_func_list[i]      

    if func_as_string != "":
        param_string = get_param_string(node.args, valid_funcs)
        keywords_string = get_keywords_string(node)
        if param_string != "" and keywords_string != "":
            func_as_string = func_as_string + param_string + ", " + keywords_string + ")" 
        elif param_string != "" and keywords_string == "":
            func_as_string = func_as_string + param_string + ")" #is including param_string redundant
        elif param_string == "" and keywords_string != "":
            func_as_string = func_as_string + param_string + ")" 


    return func_as_string

'''Needs documentation'''
def get_param_string(args: list, valid_funcs: list) ->str: #right now this only takes into account function parameter
    for node in args:
        if isinstance(node, ast.Call):
            return create_func_string(node, valid_funcs)
        elif isinstance(node, ast.Constant):
            return str(node.value)
    return ""

'''Needs documentation'''
def get_keywords_string(node: ast) ->str:
    # #get function keywords:
    # ast_keywords = "" 
    # keywords_list = node.keywords
    # for i in range (len(keywords_list)):
    #     print("Keyword:")
    #     print(keywords_list[i].value) #seems to be constant; tuple...
    #     keyword_string = keywords_list[i].arg + "=" #+ keywords_list[i].value.value #why 2 values? Explain this
    #     if i == len(keywords_list) - 2: #decide whether or not to add a comma for more terms
    #         ast_keywords = ast_keywords + keyword_string
    #     else:
    #         ast_keywords = ast_keywords + keyword_string + ","
    return_string = ""
    for keyword in node.keywords:
        return_string = return_string + keyword.arg + "=" + str(keyword.value) #getting there...still need to account for tuples
    return return_string

'''Takes a Python AST and returns a list of all API references in imports 
and all variable names for API functions from Assign expressions. This will be used
in AST_extractor() to make sure that only functions that are part of imported APIs are 
counted in its output'''
def collect_valid_funcs(python_tree: ast) ->list :
    valid_funcs = []
    #trying to get rid of python functions...
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

'''Need to comment this'''
def alias_to_string(alias : ast.alias):
    alias_name = ast.dump(alias, annotate_fields=False, include_attributes=False).split("alias")[1]
    if len(alias_name.split(",")) > 1:
        alias_name = alias_name.split(",")[1]
    return alias_name

#=====================================================Debugging=====================================================#

for item in AST_extractor("test_tf.py"):
    print(item)

for item in AST_extractor("test_pt.py"):
    print(item)

