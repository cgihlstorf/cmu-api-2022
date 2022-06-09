import re
import ast

#TODO the regular expressions produce some outputs but do not cover all cases
#TODO find more examples of tf/pt code --> save results in CSV file

'''Takes a Python file and a two-letter code ('tf' (for Tensorflow) or 'pt' (For PyTorch)). 
Searches for a list of all of the (either Tensorflow or PyTorch) function calls found in the code
using a regular expression, and returns a list of them.'''
#This doesn't handle cases with 'model.add()', etc, yet
def regex_extractor(python_file: str, api_name: str) -> list: #api_name is either 'tf' (for Tensorflow) or 'pt' (For PyTorch)
    list_of_funcs = []

    file = open(python_file, "r")
    file_lines = file.readlines()
    regex = ""

    #Determine whether to seach for Tensorflow or PyTorch functions
    if api_name == "tf":
        regex = ".*\((tf\.+.*|tensorflow\.+^org)"  #this works on Rubular but doesn't work here...
    elif api_name == "pt":
        regex = "torch\.+[^org].*" #This works on some, but not on all, cases
    else:
        raise ValueError("Invalid entry to function regex_extractor(). Must be either 'tf' (Tensorflow) or 'pt' (PyTorch)") 

    #Compile a list of all relevant function calls
    for line in file_lines:
        line_list = re.findall(regex, line)
        if line_list != []: 
            list_of_funcs.append(line_list[0])
    
    return list_of_funcs


#=====================================================Debugging=====================================================#

for item in regex_extractor("test_tf.py", "tf"):
    print(item)

# for item in regex_extractor("test_pt.py", "pt"):
#     print(item)
