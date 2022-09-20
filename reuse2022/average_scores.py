import glob
import matplotlib.pyplot as plt
import ast
import math
import seaborn as sns
import pandas as pd
import numpy as np


def is_same_file(pres_line, abs_line):
    pres = pres_line.split("->")[0]
    abs = abs_line.split("->")[0]
    if abs != pres:
        print(pres)
        print(abs)
    return abs == pres


def average_scores(present_scores:str, 
                   absent_scores:str, 
                   file_path_start:str,
                   score_diff_file:str):
    
    #score = entropy
    present_file = open(present_scores, 'r')
    present_lines = present_file.readlines()
    absent_file = open(absent_scores, 'r')
    absent_lines = absent_file.readlines()
    score_differences = open(score_diff_file, 'w')
    
    print(len(present_lines))
    print(len(absent_lines))
    assert len(present_lines) == len(absent_lines)
    
    scores_sum_pres = 0
    scores_sum_abs = 0
    number_of_scores = 0
    pres_greater = 0
    abs_greater = 0
    pres_abs_equal = 0


    for pres_line, abs_line in zip(present_lines, absent_lines):
        #I eventually need to find the cause of the assertion error in codegen_model.py
        # if pres_line.strip() == "SKIP" or abs_line.strip() == "SKIP":
        #     continue
        if "DONE WRITING FILES" in pres_line.strip():
            assert "DONE WRITING FILES" in abs_line.strip()
            break

        number_of_scores = number_of_scores + 1
        assert is_same_file(pres_line, abs_line)
        
        score_pres = float(pres_line.split("->")[1])
        score_abs = float(abs_line.split("->")[1])

        if score_pres > score_abs:
            pres_greater += 1
        elif score_pres < score_abs:
            abs_greater += 1
        else:
            pres_abs_equal += 1

        current_file = file_path_start + pres_line.split("->")[0]

        score_diff = score_pres - score_abs #pres-abs is default! (positive = higher entropy with docstring, negative = lower entropy with docstring)
        score_differences.write(current_file + "->" + str(score_diff) + "\n")

        scores_sum_pres = scores_sum_pres + score_pres
        scores_sum_abs = scores_sum_abs + score_abs

    # print(pres_greater)
    # print(abs_greater)
    # print(pres_abs_equal)
    return_string = "Higher entropy with docstring: " + str(pres_greater)
    return_string = "\n Higher entropy without docstring: " + str(abs_greater)
    return_string = "\n Equal entropy: " + str(pres_abs_equal)
    return_string = "\nDocstring present: " + str('%.2f' %(scores_sum_pres/number_of_scores)) + '\n' + "Docstring absent: " + str('%.2f' %(scores_sum_abs/number_of_scores)) + '\n' + "Total functions scored: " + str(number_of_scores)
    return_string = return_string + "\n" + "Code with a docstring had higher entropy(less predictable) " + str((pres_greater/number_of_scores)*100) + " percent of the time."
    return_string = return_string + "\n" + "Code without a docstring had higher entropy(less predictable) " + str((abs_greater/number_of_scores)*100) + " percent of the time."
    return_string = return_string + "\n" + "Same entropy " + str((pres_abs_equal/number_of_scores)*100) + " percent of the time."

    return return_string


def average_score_difference(present_scores:str, absent_scores:str):

    present_file = open(present_scores, 'r')
    present_lines = present_file.readlines()
    absent_file = open(absent_scores, 'r')
    absent_lines = absent_file.readlines()

    number_of_scores = 0
    total_score_diffs = 0
    
    max_diff = 0
    min_diff = float('inf')
    file = ""

    for pres_line, abs_line in zip(present_lines, absent_lines):

        if pres_line.strip() == "DONE WRITING FILES":
            assert abs_line.strip() == "DONE WRITING FILES"
            break

        if pres_line.strip() == "SKIP" or abs_line.strip() == "SKIP":
            continue

        number_of_scores = number_of_scores + 1
        assert is_same_file(pres_line, abs_line)
        
        score_pres = float(pres_line.split("->")[1])
        score_abs = float(abs_line.split("->")[1])

        score_diff = abs(score_pres - score_abs)

        if score_diff < min_diff:
            min_diff = score_diff

        if score_diff > max_diff:
            max_diff = score_diff
            file = pres_line.split("->")[0]


        total_score_diffs = total_score_diffs + score_diff

    return_string = "Average score difference: " + str(total_score_diffs/number_of_scores) + "\n"
    return_string = return_string + "Highest score_difference: " + str(max_diff) + " in " + str(file) + "\n"
    return_string = return_string + "Lowest score_difference: " + str(min_diff) + "\n"
    return return_string

def are_there_duplicates(directory_of_files):
    dir_files = glob.glob(directory_of_files + '/*.txt')
    dir_len = len(dir_files)
    dir_set = set()
    for file in dir_files:
        dir_set.add(file)
    print(dir_len)
    print(len(dir_set))
    return not(dir_len == len(dir_set)) #returns True if there are duplicates (ie, if the lengths are not the same)


def average_single_file_scores(score_file):
    opened_file = open(score_file, 'r')
    file_lines = opened_file.readlines()
    number_of_scores = 0
    scores_sum = 0
    
    for line in file_lines:
        #I eventually need to find the cause of the assertion error in codegen_model.py
        if line.strip() == "SKIP":
            continue
        number_of_scores = number_of_scores + 1
        score = float(line.split("->")[1])
        scores_sum = scores_sum + score

    return "Average entropy is " + str(scores_sum / number_of_scores) + "\n" + str(number_of_scores) + " files scored."

def get_code_examples(score_diff_file, score_comp_large_ent_code_file, score_comp_medium_ent_code_file, score_comp_small_ent_code_file, score_comp_same_ent_code_file):
    
    score_differences_file = open(score_diff_file)
    score_differences = score_differences_file.readlines()

    high_ent_diff_w_ds_higher = 0
    high_ent_diff_w_ds_lower = 0
    medium_ent_diff_w_ds_higher = 0
    medium_ent_diff_w_ds_lower = 0
    low_ent_diff_w_ds_higher = 0
    low_ent_diff_w_ds_lower = 0
    same_ent_diff = 0 #ds higher or lower makes no sense here
    
    score_comp_large_ent_code = open(score_comp_large_ent_code_file, 'w')
    score_comp_medium_ent_code = open(score_comp_medium_ent_code_file, 'w')
    score_comp_small_ent_code = open(score_comp_small_ent_code_file, 'w')
    score_comp_same_ent_code = open(score_comp_same_ent_code_file, 'w')

    for line in score_differences:

        line_as_list = line.split("->")

        file = line_as_list[0]
        opened_file = open(file, 'r')
        file_contents = opened_file.read()

        score_diff = float(line_as_list[1]) #get the entropy score

        string = ""

        if score_diff < 0: #lower entropy with docstring
            string = "lower entropy with docstring"
            if score_diff <= -1: #high ent difference
                output_file = score_comp_large_ent_code 
                high_ent_diff_w_ds_lower += 1
            elif score_diff >= -0.1: #low ent difference
                output_file = score_comp_small_ent_code
                low_ent_diff_w_ds_lower += 1
            else: #in the middle
                output_file = score_comp_medium_ent_code
                medium_ent_diff_w_ds_lower += 1
        elif score_diff > 0: #higher entropy with docstring (remember, doing docstring_present - docstring_absent)
            string = "higher entropy with docstring"
            if score_diff >= 1: #high ent difference
                output_file = score_comp_large_ent_code
                high_ent_diff_w_ds_higher += 1
            elif score_diff <= 0.1: #low ent difference
                output_file = score_comp_small_ent_code
                low_ent_diff_w_ds_higher += 1
            else: #in the middle (med_ent_diff)
                output_file = score_comp_medium_ent_code
                medium_ent_diff_w_ds_higher += 1
        else: #if = 0
            string = "same entropy"
            output_file = score_comp_same_ent_code
            same_ent_diff += 1

        assert output_file #that it exists 
        assert string != ""

        output_file.write(file_contents)
        output_file.write("\n- - - - - - - - - - - - - - - - - - -  -" + string + "- - - - - - - - - - - - - - - - - - - - \n\n")
    
    total_files = high_ent_diff_w_ds_higher + high_ent_diff_w_ds_lower + medium_ent_diff_w_ds_higher + medium_ent_diff_w_ds_lower + low_ent_diff_w_ds_higher + low_ent_diff_w_ds_lower + same_ent_diff

    print("wrote " + str(total_files) + " total files")

    return_string = "Higher entropy difference, higher entropy with docstring: " + str(high_ent_diff_w_ds_higher) + " files, or " + str('%.2f' %((high_ent_diff_w_ds_higher/total_files) * 100)) + " percent."
    return_string = return_string + "\n" + "Higher entropy difference, lower entropy with docstring: " + str(high_ent_diff_w_ds_lower) + " files, or " + str('%.2f' %((high_ent_diff_w_ds_lower/total_files) * 100)) + " percent."
    return_string = return_string + "\n" + "Medium entropy difference, higher entropy with docstring: " + str(medium_ent_diff_w_ds_higher) + " files, or " + str('%.2f' %((medium_ent_diff_w_ds_higher/total_files) * 100)) + " percent."
    return_string = return_string + "\n" + "Medium entropy difference, lower entropy with docstring: " + str(medium_ent_diff_w_ds_lower) + " files, or " + str('%.2f' %((medium_ent_diff_w_ds_lower/total_files) * 100)) + " percent."
    return_string = return_string + "\n" + "Low entropy difference, higher entropy with docstring: " + str(low_ent_diff_w_ds_higher) + " files, or " + str('%.2f' %((low_ent_diff_w_ds_higher/total_files) * 100)) + " percent."
    return_string = return_string + "\n" + "Low entropy difference, lower entropy with docstring: " + str(low_ent_diff_w_ds_lower) + " files, or " + str('%.2f' %((low_ent_diff_w_ds_lower/total_files) * 100)) + " percent."
    return_string = return_string + "\n" + "Same entropy difference: " + str(same_ent_diff) + " files, or " + str('%.2f'%((same_ent_diff/total_files) * 100)) + " percent."


    return return_string

def get_body_length(code:str, func_name:str, func_number:int, lines_list:list):
        #print("ENTER FUNCTION")
        func_line_start = 0
        func_line_end = 0
        code_ast = ast.parse(code)
        counter = 0
        node_name = "NOTHING"
        for node in ast.walk(code_ast):
            if isinstance(node, ast.FunctionDef):
                if node.name == func_name:
                    node_name = node.name
                    #print(counter)
                    if counter == func_number: 
                        #keep track of how many functions of a particular name you pass
                        #to ensure that, if there are duplicate function names in different classes, you choose the right one
                        func_line_start = node.lineno
                        func_line_end = node.end_lineno
                        break
                    counter = counter + 1             
        func_body = ""
        for line in lines_list[func_line_start:func_line_end]:
            func_body = func_body + line
        
        # print(func_body)
        # print("- - - - - - - - - - - - - - - - CODE:- - - - - - - - - - - - - - - - - - - - - - - ")
        # print(code)
        # print("===============================================================================")
        if func_line_start == func_line_end:
            # print(func_name, "MARKER", func_number)
            # #print(code)
            # print(lines_list[func_line_start])
            # print(lines_list[func_line_end])
            # print(code)
            # print("====================================")
            return None
        return len(func_body)

def get_length_score_scatterplot_data(present_scores, absent_scores):

    pres_scores_opened = open(present_scores, 'r')
    abs_scores_opened = open(absent_scores, 'r')
    pres_score_lines = pres_scores_opened.readlines()
    abs_score_lines = abs_scores_opened.readlines()

    assert len(pres_score_lines) == len(abs_score_lines)
    num_skipped = 0
    num_files = len(pres_score_lines)

    lengths = []
    scores_pres = []
    scores_abs = []

    lengths_high_diff = []
    score_diffs_high = []
    scores_pres_high = []
    scores_abs_high = []
    lengths_medium_diff = []
    score_diffs_medium = []
    scores_pres_medium = []
    scores_abs_medium = []
    lengths_low_diff = []
    score_diffs_low = []
    scores_pres_low = []
    scores_abs_low = []
    lengths_same_diff = []
    scores_same_diff = []

    lengths_high_diff_higher_ent_with_ds = []
    lengths_high_diff_lower_ent_with_ds = []
    lengths_medium_diff_higher_ent_with_ds = []
    lengths_medium_diff_lower_ent_with_ds = []
    lengths_low_diff_higher_ent_with_ds = []
    lengths_low_diff_lower_ent_with_ds = []
    lengths_same_diff_thus_same_ent = []


    for pres_line, abs_line in zip(pres_score_lines, abs_score_lines):
       
        # if pres_line.strip() == "SKIP" or abs_line.strip() == "SKIP":
        #     num_skipped += 1
        #     continue

        if "DONE WRITING FILES" in pres_line.strip():
            assert "DONE WRITING FILES" in abs_line.strip()
            break

        path_pres = '../ALL_FILES/50000_output_ALL_with_docstring/'
        path_abs = '../ALL_FILES/50000_output_ALL_no_docstring/'
        pres_file = path_pres + pres_line.split("->")[0]
        #abs_file = path_abs + abs_line.split("->")[0]
        pres_score = float(pres_line.split("->")[1])
        abs_score = float(abs_line.split("->")[1])
        score_diff_raw = pres_score - abs_score #with_docstring - no_docstring
        score_diff_abs = abs(score_diff_raw)
        
        func_name = pres_file[0: len(pres_file) - 7]
        func_name = func_name.split("_FUNC_")[1] #get only the name of the function as it is defined in the file
        func_number = int(pres_file[len(pres_file) - 6])

        pres_file_opened_1 = open(pres_file, 'r')
        pres_file_contents = pres_file_opened_1.read()
        pres_file_opened_1.close()
        pres_file_opened_2 = open(pres_file, 'r')
        pres_file_lines = pres_file_opened_2.readlines()

        try:
            func_body_length = get_body_length(pres_file_contents, func_name, func_number, pres_file_lines)
            if func_body_length == None:
                num_skipped += 1 #TODO something's not right here...
                continue
        except SyntaxError:
            num_skipped += 1
            continue

        
        # lengths.append(func_body_length)
        # scores_pres.append(pres_score)
        # scores_abs.append(abs_score)
        
        if score_diff_abs == 0: #no entropy diff
            #I don't think this is really necessary but manybe it's good to have just in case?
            #print("I must exist!!!")
            lengths_same_diff.append(func_body_length)
            scores_same_diff.append(score_diff_raw)
            lengths_same_diff_thus_same_ent.append(func_body_length)
        
        elif score_diff_abs >= 1: #high entropy diff
            lengths_high_diff.append(func_body_length)
            score_diffs_high.append(score_diff_raw)
            scores_pres_high.append(pres_score)
            scores_abs_high.append(abs_score)
            if pres_score > abs_score:
                lengths_high_diff_higher_ent_with_ds.append(func_body_length)
            elif pres_score < abs_score:
                lengths_high_diff_lower_ent_with_ds.append(func_body_length)
           

        elif score_diff_abs < 1 and score_diff_abs > 0.1: #medium entropy diff
            lengths_medium_diff.append(func_body_length)
            score_diffs_medium.append(score_diff_raw)
            scores_pres_medium.append(pres_score)
            scores_abs_medium.append(abs_score)
            if pres_score > abs_score:
                lengths_medium_diff_higher_ent_with_ds.append(func_body_length)
            elif pres_score < abs_score:
                lengths_medium_diff_lower_ent_with_ds.append(func_body_length)
           

        elif score_diff_abs <= 0.1: #low entropy diff
            lengths_low_diff.append(func_body_length)
            score_diffs_low.append(score_diff_raw)
            scores_pres_low.append(pres_score)
            scores_abs_low.append(abs_score)
            if pres_score > abs_score:
                lengths_low_diff_higher_ent_with_ds.append(func_body_length)
            elif pres_score < abs_score:
                lengths_low_diff_lower_ent_with_ds.append(func_body_length)
           
        else:
            raise ValueError("None of the if-else options were met - fix so that all scores are included.")

    
    def avg(vals:list):
        total_vals = len(vals)
        vals_sum = 0
        for val in vals:
            vals_sum = vals_sum + val
        return vals_sum / total_vals

    def log_lengths(nums):
        return_list = []
        for num in nums:
            return_list.append(math.log10(num))
        return return_list
    

    df = pd.DataFrame()
    index = ["High\nEntropy\nDifference", "Medium\nEntropy\nDifference", "Low\nEntropy\nDifference"]
    cols = ["Higher\nEntropy\nwith\nDocstring", "Lower\nEntropy\nWith\nDocstring"]
    #data = {'Name':['Tom', 'nick', 'krish', 'jack'], 'Age':[20, 21, 19, 18]}
    print(len((lengths_high_diff_higher_ent_with_ds)))
    print(len((lengths_high_diff_lower_ent_with_ds)))
    print(len(lengths_medium_diff_higher_ent_with_ds))
    print(len(lengths_medium_diff_lower_ent_with_ds))
    print(len(lengths_low_diff_higher_ent_with_ds))
    print(len(lengths_low_diff_lower_ent_with_ds))
    print(len(lengths_same_diff_thus_same_ent))
    high_diff = [len((lengths_high_diff_higher_ent_with_ds)), len((lengths_high_diff_lower_ent_with_ds))]
    med_diff = [len((lengths_medium_diff_higher_ent_with_ds)), len((lengths_medium_diff_lower_ent_with_ds))]
    low_diff = [len((lengths_low_diff_higher_ent_with_ds)), len((lengths_low_diff_lower_ent_with_ds))]
    #no_diff = [0, 0, len(lengths_same_diff_thus_same_ent)]
    heatmap_data = [high_diff, med_diff, low_diff]
    
    # for pres_score, abs_score, length in zip(scores_pres_high[0:10], scores_abs_high[0:10], lengths_high_diff[0:10]): #[high] entropy diff
    #     score_diff_raw = pres_score - abs_score
    #     score_diff_abs = abs(score_diff_raw)
    #     score_diff_data.append(round(score_diff_abs, 1))
    #     length_data.append(length)    
        
    #heatmap_data = pd.DataFrame(heatmap_data)
    #print(heatmap_data)
    # heatmap_df = pd.DataFrame(heatmap_data, index=index, columns=cols)
    # heatmap = sns.heatmap(heatmap_df, annot=True, linecolor= "white", square=False)
    # plt.title("Entropy Differences vs Number of Examples")
    # plt.savefig("heatmap_50000_diffs_vs_num_examples_no_docstring_context.jpg")

    



    print(len((lengths_high_diff_higher_ent_with_ds)))
    print(len((lengths_high_diff_lower_ent_with_ds)))
    print(len(lengths_medium_diff_higher_ent_with_ds))
    print(len(lengths_medium_diff_lower_ent_with_ds))
    print(len(lengths_low_diff_higher_ent_with_ds))
    print(len(lengths_low_diff_lower_ent_with_ds))
    print(len(lengths_same_diff_thus_same_ent))

    lower_ent_with_docstring = len((lengths_high_diff_lower_ent_with_ds)) + len((lengths_medium_diff_lower_ent_with_ds)) + len((lengths_low_diff_lower_ent_with_ds))
    higher_ent_with_docstring = len((lengths_high_diff_higher_ent_with_ds)) + len((lengths_medium_diff_higher_ent_with_ds)) + len((lengths_low_diff_higher_ent_with_ds))
    same_ent_with_and_without_docstring = len(lengths_same_diff_thus_same_ent)
    assert len(lengths_same_diff_thus_same_ent) == len(lengths_same_diff)
    
    x_axis_bar_graph_vals = ["H/H", "H/L", "M/H", "M/L", "L/H", "L/L", "None"]
    
    y_axis_bar_graph_vals_avg_length = [avg(lengths_high_diff_higher_ent_with_ds), avg(lengths_high_diff_lower_ent_with_ds), 
    avg(lengths_medium_diff_higher_ent_with_ds), avg(lengths_medium_diff_lower_ent_with_ds), 
    avg(lengths_low_diff_higher_ent_with_ds), avg(lengths_low_diff_lower_ent_with_ds), avg(lengths_same_diff_thus_same_ent)]

    y_axis_bar_graph_vals_num_lengths = [len(lengths_high_diff_higher_ent_with_ds), len(lengths_high_diff_lower_ent_with_ds), 
    len(lengths_medium_diff_higher_ent_with_ds), len(lengths_medium_diff_lower_ent_with_ds), 
    len(lengths_low_diff_higher_ent_with_ds), len(lengths_low_diff_lower_ent_with_ds), len(lengths_same_diff_thus_same_ent)]

    colors = ["blue", "blue", "purple", "purple", "teal", "teal", "green"]

    file_path_name = '50000_ent_diff_vs_avg_len_bar_graph_no_docstring_context'
    print(y_axis_bar_graph_vals_avg_length)
    plt.bar(x_axis_bar_graph_vals, y_axis_bar_graph_vals_avg_length, color=colors)
    # plt.legend("High entropy difference/Higher entropy with docstring", "High entropy difference/Lower entropy with docstring", 
    # "Medium entropy difference/Higher entropy with docstring", "Medium entropy difference/Lower entropy with docstring",
    # "Low entropy difference/Higher entropy with docstring", "Low entropy difference/Lower entropy with docstring")
    #plt.xlabel("Entropy Difference")
    plt.ylabel("Average Code Body Length")
    plt.title("Entropy Difference vs Average Code Body Length")
    plt.savefig(file_path_name + '.jpg')
    plt.savefig('SVG' + file_path_name + '.svg')
    
    # plt.scatter(log_lengths(lengths_high_diff), scores_pres_high, 10, marker = ".")
    # plt.scatter(log_lengths(lengths_medium_diff), scores_pres_medium, 10, marker = "s")
    # plt.scatter(log_lengths(lengths_low_diff), scores_pres_low, 10, marker = "^")
    # #plt.scatter(log_lengths(lengths_same_diff), scores_same_diff, 10, marker = "x")
    # plt.legend(["High Entropy Difference", "Medium Entropy Difference", "Low Entropy Difference"])
    # plt.title("Code Length vs Entropy, Docstring Present")
    # plt.xlabel("Entropy")
    # plt.ylabel("Length of Code Body") #(entropy_with_docstring - entropy_without_docstring)
    # file_path_name = '50000_lengths_vs_entropy_ds_present_no_docstring_context'
    # plt.savefig(file_path_name + '.jpg')
    # plt.savefig('SVG' + file_path_name + '.svg')

    print(num_skipped, "files skipped out of", num_files, "files, or", str('%.2f' %((num_skipped/num_files) * 100)), "percent")
    print("That leaves", num_files - num_skipped, "total files left in the data")


def plot_all_scores(present_scores_file, initially_absent_scores_file):
    scores_pres = []
    lengths_pres = []

    scores_abs = []
    lengths_abs = []

    present_scores_opened = open(present_scores_file, 'r')
    present_scores = present_scores_opened.readlines()
    initially_absent_scores_opened = open(initially_absent_scores_file, 'r')
    initially_absent_scores = initially_absent_scores_opened.readlines()


    for pres_line in present_scores:  
        pres_line = '../ALL_FILES/80%_full_output_ALL_with_docstring/' + pres_line
        if pres_line.strip() == "../ALL_FILES/80%_full_output_ALL_with_docstring/DONE WRITING FILES":
            break
        path_pres = pres_line.split("->")[0] 
        #print(pres_line)
        score_pres = float(pres_line.split("->")[1])
        pres_file_opened_1 = open(path_pres, 'r')
        pres_file_lines = pres_file_opened_1.readlines()
        pres_file_opened_2 = open(path_pres, 'r')
        pres_file_code = pres_file_opened_2.read()
        func_name_pres = path_pres[0: len(path_pres) - 7]
        func_name_pres = func_name_pres.split("_FUNC_")[1] #get only the name of the function as it is defined in the file
        func_number_pres = int(path_pres[len(path_pres) - 6])

        try:
            pres_length = get_body_length(pres_file_code, func_name_pres, func_number_pres, pres_file_lines)
            if pres_length == None:
                #num_skipped += 1 #TODO something's not right here...
                continue
        except SyntaxError:
            #num_skipped += 1
            continue

        scores_pres.append(score_pres)
        lengths_pres.append(pres_length)
       
    
    for initially_abs_line in initially_absent_scores:
        initially_abs_line = '../ALL_FILES/80%_full_output_ALL_no_docstring/' + initially_abs_line
        path_initial_abs = initially_abs_line.split("->")[0]
        score_initially_abs = float(initially_abs_line.split("->")[1])
        abs_init_opened_1 = open(path_initial_abs, 'r')
        abs_init_lines = abs_init_opened_1.readlines()
        abs_init_opened_2 = open(path_pres, 'r')
        abs_init_code = abs_init_opened_2.read()
        func_name_abs_init = path_pres[0: len(path_pres) - 7]
        func_name_abs_init = func_name_pres.split("_FUNC_")[1] #get only the name of the function as it is defined in the file
        func_number_abs_init = int(path_pres[len(path_pres) - 6])

        
        try:
            abs_init_length = get_body_length(abs_init_code, func_name_abs_init, func_number_abs_init, abs_init_lines)
            if abs_init_length == None:
                #num_skipped += 1 #TODO something's not right here...
                continue
        except SyntaxError:
            #num_skipped += 1
            continue

        
        scores_abs.append(score_initially_abs)
        lengths_abs.append(abs_init_length)


    plt.scatter(scores_pres, lengths_pres, 5)
    plt.scatter(scores_abs, lengths_abs, 5)
    plt.legend(["Functions With Docstrings", "Functions Without Docstrings"])
    plt.title("Scores vs Lengths - All Files")
    plt.xlabel("Scores")
    plt.ylabel("Code Lengths")
    plt.savefig("ALL_FILES_PLOT.jpg")
    print("Done plotting!")
        


present_scores = "../ALL_FILES/Results/50000_all_files_scores_present_no_docstring_context.txt"
absent_scores = "../ALL_FILES/Results/50000_all_files_scores_absent_no_docstring_context.txt"
file_path_start = '../ALL_FILES/50000_output_ALL_with_docstring/'
score_diff_file = '../ALL_FILES/50000_raw_ent_diff_scores_no_docstring_context.txt'
# initially_absent_scores = '../ALL_FILES/Results/80%_all_files_scores_no_docstring.txt'

#print(average_scores(present_scores, absent_scores, file_path_start, score_diff_file))

#print(average_score_difference(present_scores, absent_scores))

#plot_all_scores(present_scores, initially_absent_scores)

score_comp_large_ent_code_file = '50000_scores_comp/50000_all_scores_comparisons_large_entropy_difference_no_docstring_context.txt'
score_comp_medium_ent_code_file = '50000_scores_comp/50000_all_scores_comparisons_medium_entropy_difference_no_docstring_context.txt'
score_comp_small_ent_code_file = '50000_scores_comp/50000_all_scores_comparisons_small_entropy_difference_no_docstring_context.txt'
score_comp_same_ent_code_file = '50000_scores_comp/50000_all_scores_comparisons_same_entropy_difference_no_docstring_context.txt'
#print(get_code_examples(score_diff_file, score_comp_large_ent_code_file, score_comp_medium_ent_code_file, score_comp_small_ent_code_file, score_comp_same_ent_code_file))



scores_no_docstring = '../ALL_FILES/Results/80%_all_files_scores_no_docstring_no_docstring_context.txt'
#print(average_single_file_scores(scores_no_docstring))


get_length_score_scatterplot_data(present_scores, absent_scores)

