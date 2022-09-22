import glob
import ast
import matplotlib.pyplot as plt

def organize_files(high_entropy_diff_file:str, medium_entropy_diff_file:str, low_entropy_diff_file:str, same_entropy_diff_file:str):

    '''Takes in text files listing names of files of code contexts based on their differences in
    entropy and whether or their code had a higher entropy with or without a docstring. 
    Organizes these files into a larger group of files sorted by both entropy difference
    and whether or not the presence of a docstring resulted in a higher entropy.'''
    
    high_ED_file = open(high_entropy_diff_file, 'r')
    medium_ED_file = open(medium_entropy_diff_file, 'r')
    low_ED_file = open(low_entropy_diff_file, 'r')
    same_ED_file = open(same_entropy_diff_file, 'r')

    high_ent_diff = high_ED_file.readlines()
    medium_ent_diff = medium_ED_file.readlines()
    low_ent_diff = low_ED_file.readlines()
    same_ent_diff = same_ED_file.readlines()

    #print("high_ent_diff has length", len(high_ent_diff))

    #want the following arrays of files: --> ED = entropy difference; ES = entropy score
    high_ED_high_ES = []
    high_ED_low_ES = []
    high_ED_same_ES = []
    medium_ED_high_ES = []
    medium_ED_low_ES = []
    medium_ED_same_ES = []
    low_ED_high_ES = []
    low_ED_low_ES = []
    low_ED_same_ES = []
    same_ED_high_ES = []
    same_ED_low_ES = []
    same_ED_same_ES = []

    for line in high_ent_diff: #high ED
        #print("going through high_end_diff...")
        split_line = line.split(",")
        file_name = split_line[0]
        description = split_line[1].strip()
        #print(description)
        if description == "higher entropy with docstring":
            high_ED_high_ES.append(file_name)
        elif description == "lower entropy with docstring":
            high_ED_low_ES.append(file_name)
        elif description == "same entropy":
            print("yes")
            high_ED_same_ES.append(file_name)
        else:
            continue

    for line in medium_ent_diff: #medium ED
        split_line = line.split(",")
        file_name = split_line[0]
        description = split_line[1].strip()
        #print(description)
        if description == "higher entropy with docstring":
            medium_ED_high_ES.append(file_name)
        elif description == "lower entropy with docstring":
            medium_ED_low_ES.append(file_name)
        elif description == "same entropy":
            print("yes")
            medium_ED_same_ES.append(file_name)
        else:
            continue

    for line in low_ent_diff: #low ED
        split_line = line.split(",")
        file_name = split_line[0]
        description = split_line[1].strip()
        #print(description)
        if description == "higher entropy with docstring":
            low_ED_high_ES.append(file_name)
        elif description == "lower entropy with docstring":
            low_ED_low_ES.append(file_name)
        elif description == "same entropy":
            print("yes")
            low_ED_same_ES.append(file_name)
        else:
            continue

    for line in same_ent_diff: #same ED
        split_line = line.split(",")
        file_name = split_line[0]
        description = split_line[1].strip()
        #print(description)
        if description == "higher entropy with docstring":
            same_ED_high_ES.append(file_name)
        elif description == "lower entropy with docstring":
            same_ED_low_ES.append(file_name)
        elif description == "same entropy":
            print("yes")
            same_ED_same_ES.append(file_name)
        else:
            continue

    print(len(same_ED_high_ES))
    print(len(same_ED_low_ES))
    print(len(same_ED_same_ES))
    total_files = len(high_ED_high_ES) + len(high_ED_low_ES) + len(high_ED_same_ES)
    total_files = total_files + len(medium_ED_high_ES) + len(medium_ED_low_ES) + len(medium_ED_same_ES)
    total_files = total_files + len(low_ED_high_ES) + len(low_ED_low_ES) + len(low_ED_same_ES)
    total_files = total_files + len(same_ED_high_ES) + len(same_ED_low_ES) + len(same_ED_same_ES)
    #print(total_files)
   

    return high_ED_high_ES, high_ED_low_ES, high_ED_same_ES, medium_ED_high_ES, medium_ED_low_ES, medium_ED_same_ES, low_ED_high_ES, low_ED_low_ES, low_ED_same_ES, same_ED_high_ES, same_ED_low_ES, same_ED_same_ES
        

def get_average_body_lengths(high_entropy_diff_file:str, medium_entropy_diff_file:str, low_entropy_diff_file:str, same_entropy_diff_file:str):

    '''Takes in text files listing paths to files of Python code. Each path is followed by
     1) the entropy difference of the function in the file with and without a docstring and 2) 
     if that entropy was higher with or without a docstring. 
     
     Returns, for each text file parameter, average the lengths of the code bodies 
     from the Python files listed within each input text file.'''

    print("got to get_average_body_lengths...")

    def get_lengths(input_files:list):
        '''Given a text file listing the paths to files with a Python function and
        its preceding context, find the lengths of the body of each Python function.'''
        #print("got to get_lengths")

        output_body_lengths = []
        output_docstring_lengths = []
        #print(input_files)

        for file in input_files:

            #print("first for loop of get_lengths")

            func_name = file[0: len(file) - 7]
            func_name = func_name.split("_FUNC_")[1]
            func_number = int(file[len(file) - 6]) 
            opened_file = open(file, 'r') #file is the full path we need
            code_as_string = opened_file.read()
            try:
                python_tree = ast.parse(code_as_string, mode='exec')
            except:
                continue
            
            counter = 0
            func_body_length = 0
            func_docstring_length = 0

            for node in ast.walk(python_tree): #topdown??? I hope it's True by default
                #print("got into the second for loop...")
                if isinstance(node, ast.FunctionDef):
                    #print("got to a fundef")
                    if node.name == func_name:
                        #print("got correct name...")
                        if counter == func_number:
                            #print("counter == func_number!!!")
                            func_body = ast.get_source_segment(code_as_string, node)
                            func_docstring = ast.get_docstring(node)
                            start_place = 0
                            for char in func_body:
                                if char == ":": #assuming this will stop at the end of the def line
                                    break
                                else:
                                    start_place = start_place + 1
                            func_body = func_body[start_place :]
                            func_body_length = len(func_body)
                            if func_docstring != None:
                                func_docstring_length = len(func_docstring)
                            # else:
                            #     print(func_body)
                            #print(func_body_length)
                        counter = counter + 1 #get to the correct function if there are multiple of the same name in different classes
            # if func_body_length == 0:
            #     print("got a 0-length function body")
            output_body_lengths.append(func_body_length)
            output_docstring_lengths.append(func_docstring_length)
        #print(len(output_lengths))
        return output_body_lengths, output_docstring_lengths #list of lengths

    def average_length(lengths:list):
        '''Given a list of lengths, return the average of those lengths.'''
        #print("getting average for a list...")
       
        lengths_sum = 0
        total_lengths = len(lengths)
        max_length = 0
        
        if total_lengths == 0: #I think it's possible to have no files in one of these categories...?
            return 0

        for length in lengths:
            if length > max_length:
                max_length = length
            lengths_sum = lengths_sum + length
        
        print("Max length:", max_length)
        return lengths_sum / total_lengths

    #================================================Start of Function=================================================+#

    high_ED_high_ES, high_ED_low_ES, high_ED_same_ES, medium_ED_high_ES, medium_ED_low_ES, medium_ED_same_ES, low_ED_high_ES, low_ED_low_ES, low_ED_same_ES, same_ED_high_ES, same_ED_low_ES, same_ED_same_ES = organize_files(high_entropy_diff_file, medium_entropy_diff_file, low_entropy_diff_file, same_entropy_diff_file)

    high_ED_high_ES_code_body_lengths, high_ED_high_ES_code_docstring_lengths = get_lengths(high_ED_high_ES)
    high_ED_low_ES_code_body_lengths, high_ED_low_ES_code_docstring_lengths = get_lengths(high_ED_low_ES)
    high_ED_same_ES_code_body_lengths, high_ED_same_ES_code_docstring_lengths = get_lengths(high_ED_same_ES)
    medium_ED_high_ES_code_body_lengths, medium_ED_high_ES_code_docstring_lengths = get_lengths(medium_ED_high_ES)
    medium_ED_low_ES_code_body_lengths, medium_ED_low_ES_code_docstring_lengths = get_lengths(medium_ED_low_ES)
    medium_ED_same_ES_code_body_lengths, medium_ED_same_ES_code_docstring_lengths = get_lengths(medium_ED_same_ES)
    low_ED_high_ES_code_body_lengths, low_ED_high_ES_code_docstring_lengths = get_lengths(low_ED_high_ES)
    low_ED_low_ES_code_body_lengths, low_ED_low_ES_code_docstring_lengths = get_lengths(low_ED_low_ES)
    low_ED_same_ES_code_body_lengths, low_ED_same_ES_code_docstring_lengths = get_lengths(low_ED_same_ES)
    same_ED_high_ES_code_body_lengths, same_ED_high_ES_code_docstring_lengths = get_lengths(same_ED_high_ES)
    same_ED_low_ES_code_body_lengths,  same_ED_low_ES_code_docstring_lengths = get_lengths(same_ED_low_ES)
    same_ED_same_ES_code_body_lengths, same_ED_same_ES_code_docstring_lengths = get_lengths(same_ED_same_ES)

    #print("got here after calls to get_lengths")

    return_string_high_ED = "Average code body length of code with the higher entropy: " + str(average_length(high_ED_high_ES_code_body_lengths)) + "\n"
    return_string_high_ED = return_string_high_ED + "Average code body length of code with the lower entropy: " + str(average_length(high_ED_low_ES_code_body_lengths)) + "\n"
    return_string_high_ED = return_string_high_ED + "Average code body length of code with equal entropy: " + str(average_length(high_ED_same_ES_code_body_lengths)) + "\n"
    return_string_high_ED = return_string_high_ED + "Average docstring length of code with the higher entropy: " + str(average_length(high_ED_high_ES_code_docstring_lengths)) + "\n"
    return_string_high_ED = return_string_high_ED + "Average docstring length of code with the lower entropy: " + str(average_length(high_ED_low_ES_code_docstring_lengths)) + "\n"
    return_string_high_ED = return_string_high_ED + "Average docstring length of code with equal entropy: " + str(average_length(high_ED_same_ES_code_docstring_lengths)) + "\n"
    return_string_high_ED = return_string_high_ED + "\n========================================================================"

    return_string_medium_ED = "Average code body length of code with the higher entropy: " + str(average_length(medium_ED_high_ES_code_body_lengths)) + "\n"
    return_string_medium_ED = return_string_medium_ED  + "Average code body length of code with the lower entropy: " + str(average_length(medium_ED_low_ES_code_body_lengths)) + "\n"
    return_string_medium_ED = return_string_medium_ED  + "Average code body length of code with equal entropy: " + str(average_length(medium_ED_same_ES_code_body_lengths)) + "\n"
    return_string_medium_ED = return_string_medium_ED + "Average code body length of docstring with the higher entropy: " + str(average_length(medium_ED_high_ES_code_docstring_lengths)) + "\n"
    return_string_medium_ED = return_string_medium_ED  + "Average docstring length of code with the lower entropy: " + str(average_length(medium_ED_low_ES_code_docstring_lengths)) + "\n"
    return_string_medium_ED = return_string_medium_ED  + "Average docstring length of code with equal entropy: " + str(average_length(medium_ED_same_ES_code_docstring_lengths)) + "\n"
    return_string_medium_ED = return_string_medium_ED + "\n========================================================================"

    return_string_low_ED = "Average code body length of code with the higher entropy: " + str(average_length(low_ED_high_ES_code_body_lengths)) + "\n"
    return_string_low_ED = return_string_low_ED  + "Average code body length of code with the lower entropy: " + str(average_length(low_ED_low_ES_code_body_lengths)) + "\n"
    return_string_low_ED = return_string_low_ED  + "Average code body length of code with equal entropy: " + str(average_length(low_ED_same_ES_code_body_lengths)) + "\n"
    return_string_low_ED = return_string_low_ED + "Average code body length of docstring with the higher entropy: " + str(average_length(low_ED_high_ES_code_docstring_lengths)) + "\n"
    return_string_low_ED = return_string_low_ED  + "Average docstring length of code with the lower entropy: " + str(average_length(low_ED_low_ES_code_docstring_lengths)) + "\n"
    return_string_low_ED = return_string_low_ED  + "Average docstring length of code with equal entropy: " + str(average_length(low_ED_same_ES_code_docstring_lengths)) + "\n"
    return_string_low_ED = return_string_low_ED + "\n========================================================================"

    return_string_no_ED = "Average code body length of code with the higher entropy: " + str(average_length(same_ED_high_ES_code_body_lengths)) + "\n"
    return_string_no_ED =  return_string_no_ED + "Average code body length of code with the lower entropy: " + str(average_length(same_ED_low_ES_code_body_lengths)) + "\n"
    return_string_no_ED =  return_string_no_ED + "Average code body length of code with equal entropy: " + str(average_length(same_ED_same_ES_code_body_lengths)) + "\n"
    return_string_no_ED =  return_string_no_ED + "Average docstring length of code with the higher entropy: " + str(average_length(same_ED_high_ES_code_docstring_lengths)) + "\n"
    return_string_no_ED =  return_string_no_ED + "Average docstring length of code with the lower entropy: " + str(average_length(same_ED_low_ES_code_docstring_lengths)) + "\n"
    return_string_no_ED =  return_string_no_ED + "Average docstring length of code with equal entropy: " + str(average_length(same_ED_same_ES_code_docstring_lengths)) + "\n"
    return_string_no_ED = return_string_no_ED + "\n========================================================================"

    return_string = "Among code with HIGH differences in entropy with/without a docstring: " + "\n" + return_string_high_ED
    return_string = "\n" + return_string + "\nAmong code with MEDIUM differences in entropy with/without a docstring: " + "\n" + return_string_medium_ED
    return_string = "\n" + return_string + "\nAmong code with LOW differences in entropy with/without a docstring: " + "\n" + return_string_low_ED
    return_string = "\n" + return_string + "\nAmong code with NO difference in entropy with/without a docstring: " + "\n" + return_string_no_ED

    return return_string



high_entropy_diff_file = "80%_all_scores_high_entropy_difference.txt"
low_entropy_diff_file = "80%_all_scores_low_entropy_difference.txt"
medium_entropy_diff_file = "80%_all_scores_medium_entropy_difference.txt"
same_entropy_diff_file = "80%_all_scores_no_entropy_difference.txt"
#directory = "../ALL_FILES/80%_full_output_ALL_with_docstring/" #don't need this, files are already in this format
print(get_average_body_lengths(high_entropy_diff_file, medium_entropy_diff_file, low_entropy_diff_file, same_entropy_diff_file))


        



# file = "demo_03_PP_Ch_03_Function_Design__PP_Ch_3B_LM_FUNC_get_weekday_5_.txt"
# func_name = file[0: len(file) - 7]
# func_number = file[len(file) - 6]
# print(func_number)
# print(func_name)
# func_name = func_name.split("_FUNC_")[1]
# print(func_name)
# func_def_start = "def " + func_name + "("
# print(func_def_start)


# organize_files("../ALL_FILES/80%_full_output_ALL_with_docstring", "", "", "", "", "", "")
