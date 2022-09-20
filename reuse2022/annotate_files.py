import random

#TODO close files

def create_ent_diff_lists(scores_pres:str, scores_abs:str):
    '''Creates files listing the names of functions and their 
    entropy score differences. Each file is categorized by entropy score 
    difference. Either high, medium, low, or no difference. '''
    scores_pres_opened = open(scores_pres, 'r')
    scores_abs_opened = open(scores_abs, 'r')
    scores_pres_list = scores_pres_opened.readlines()
    scores_abs_list = scores_abs_opened.readlines()

    high_ent_diff_file = open('high_ent_diff_for_annotations.txt', 'w')
    medium_ent_diff_file = open('medium_ent_diff_for_annotations.txt', 'w')
    low_ent_diff_file = open('low_ent_diff_for_annotations.txt', 'w')
    no_ent_diff_file = open('no_ent_diff_for_annotations.txt', 'w')

    for pres_line, abs_line in zip(scores_pres_list, scores_abs_list):
        pres_list = pres_line.split("->")
        abs_list = abs_line.split("->")
        file = 'ALL_FILES/50000_output_ALL_with_docstring/' + pres_list[0]
        pres_score = float(pres_list[1])
        abs_score = float(abs_list[1])
        score_diff_raw = pres_score - abs_score
        score_diff_abs = abs(score_diff_raw)
        if score_diff_abs == 0:
            #no diff
            no_ent_diff_file.write(file + "->" + str(score_diff_raw) + "\n")
        if score_diff_abs > 1:
            #high diff
            high_ent_diff_file.write(file + "->" + str(score_diff_raw) + "\n")
        elif score_diff_abs >= 0.1 and score_diff_abs <= 1:
            #med diff
            medium_ent_diff_file.write(file + "->" + str(score_diff_raw) + "\n")
        elif score_diff_abs < 0.1:
            #low diff
            low_ent_diff_file.write(file + "->" + str(score_diff_raw) + "\n")
        else:
            raise ValueError("Should have gotten to one of the previous if statements...")


def write_random_files(input_ent_diff_file:str, output_file:str, num_files:int, get_any_files:bool):
    '''Picks 'num_files' random files from inputPent_diff_file and writes their content to 
    a new file, with a note about whether the function with or without a docstring had the higher entropy.'''
    #must run create_ent_diff_lists first
    opened_input_file = open(input_ent_diff_file, 'r')
    input_file_lines = opened_input_file.readlines()
    
    if len(input_file_lines) < num_files:
        num_files = len(input_file_lines)
    
    opened_input_file.close()
    opened_output_file = open(output_file, 'w')
    files_seen = []
    file_counter = 0
    lower_count = 0
    higher_count = 0
    same_count = 0
    
    #print(file_counter, num_files)
    
    while file_counter < num_files:
        line = random.choice(input_file_lines)
        
        if "DONE WRITING FILES" in line:
            file_counter += 1
            continue

        if line in files_seen:
            continue
       
        files_seen.append(line)
        split_line = line.split("->")
        file_name = split_line[0]
        opened_file = open(file_name, 'r')
        file_content = opened_file.read()
        opened_file.close()
        score_diff = float(split_line[1])
        string = ""
        opened_output_file.write(file_content + "\n")
        if score_diff > 0: #higher entropy with docstring
            string = "higher entropy with docstring"
            higher_count += 1
        elif score_diff < 0: #lower entropy with docstring
            string = "lower entropy with docstring"
            if get_any_files == False and lower_count == (num_files / 2):
                continue
            lower_count += 1   
        elif score_diff == 0: #same entropy
            string = "same entropy"
            same_count += 1
        else:
            raise ValueError("Should have gotten to one of the previous if statements.")

        opened_output_file.write("- - - - - - - - - - - - - - - - - - - - - - - - -" + string + "- - - - - - - - - - - - - - - - - - - - - - - - -\n\n")
        file_counter += 1

    print("Done writing random files")


scores_pres = 'ALL_FILES/Results/50000_all_files_scores_present_no_docstring_context.txt'
scores_abs = 'ALL_FILES/Results/50000_all_files_scores_absent_no_docstring_context.txt'
#create_ent_diff_lists(scores_pres, scores_abs)
output_file_high_diff = 'files_to_annotate_high_diff.txt'
output_file_medium_diff = 'files_to_annotate_medium_diff.txt'
output_file_low_diff = 'files_to_annotate_low_diff.txt'
output_file_no_diff = 'files_to_annotate_no_diff.txt'

write_random_files('high_ent_diff_for_annotations.txt', output_file_high_diff, 20, True)
write_random_files('medium_ent_diff_for_annotations.txt', output_file_medium_diff, 20, False)
write_random_files('low_ent_diff_for_annotations.txt', output_file_low_diff, 20, False)
write_random_files('no_ent_diff_for_annotations.txt', output_file_no_diff, 20, True)













