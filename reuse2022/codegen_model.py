from ast import Assert
import os
import glob
import torch
import math
import ast
from jaxformer.hf.sample import truncate as do_truncate
from jaxformer.hf.sample import set_env, set_seed, print_time, create_model, create_custom_gpt2_tokenizer, create_tokenizer, sample
from jaxformer.hf.score import score 

#TODO: Note; All of the "write" functions are commented out for the moment so I can debug without overwriting the current data.

def remove_all_context_docstrings(context:str):
    '''Removes all docstrings present in a string of source code.'''
    #TODO figure out "" docstrings... can't use ast because it doesn't give docstring quotes do we don't know which quotes to remove...
    #Unless we did something like "while the next thing after/before the docstring is a ", ' or space, or \n...add the string to the docstring."
    left_window = 0
    right_window = left_window + 3
    context_length = len(context)

    start_indices = []
    end_indices = []

    while right_window <= context_length:
      #move a sliding window accross the string to identify docstring quotes. 
      #do this twice to identify the start and end of a docstring
      #keep repeating finding the start and end of docstrings until the entire string has been seen
      #store the indices of the quotes beginning a dodcstirng in one list and correspinding indices ending a docstring in another
      #TODO can't use ast to get docstrings because context could not compile?
        #get the start docstring indices
        while right_window <= context_length and (context[left_window:right_window] != "\'\'\'" and context[left_window:right_window] != "\"\"\""):
            left_window = left_window + 1
            right_window = right_window + 1

        start_indices.append(left_window) #store indices of all beginning quotes of docstrings

        #must increment to avoid beginning at the same docstring quotes we ended on (which would create an infinite loop)
        left_window = left_window + 1
        right_window = right_window + 1

        #get the end docstring indices
        while right_window <= context_length and (context[left_window:right_window] != "\'\'\'" and context[left_window:right_window] != "\"\"\""):
            left_window = left_window + 1
            right_window = right_window + 1

        end_indices.append(right_window)

        #must increment to avoid beginning at the same docstring quotes we ended on (which would create an infinite loop)
        left_window = left_window + 1
        right_window = right_window + 1

    #make sure each start index of a docstring correpsonds to an ending index of the docstring 
    assert len(start_indices) == len(end_indices)

    docstring_list = []

    #use the docstring start and end indices to extract each docstring from the string and put it in a list
    for start, end in zip(start_indices, end_indices):
        docstring_list.append(context[start:end])
    
    #for each docstring in the list of docstrings, replace its occurrance in the code with an empty string (ie, remove it)
    for docstring in docstring_list:
        context = context.replace(docstring, "")

    return context


def remove_docstring(code_string:str, docstring_start, docstring_end) ->str:
  '''Remove docstrings from a given string representation of code. Return a copy of that code
  with its docstring removed.'''

  before_docstring = code_string[0:docstring_start]
  after_docstring = code_string[docstring_end:]
  
  return before_docstring + after_docstring

def trim_code_window(file_as_string:str, input_ids_len:int, tokenizer, max_length:int, docstring_start:int, docstring_end:int, with_docstring:bool):
  '''This docstring will eventually describe what this function does.'''

  the_docstring = file_as_string[docstring_start:docstring_end]
  # print(the_docstring)
  # print("===========================================================================")
  while(input_ids_len >= 2048):
    if len(file_as_string) >= 5000:
      new_len = len(file_as_string) - (len(file_as_string) // 2) #you're basically subracting len - len/2
      file_as_string = file_as_string[new_len:]
    else:
      file_as_string = file_as_string[10:] #decrease size by 10 characters at a time
      new_len = len(file_as_string)
      input_ids = tokenizer(file_as_string, truncation=True, padding=True, max_length=max_length, return_tensors='pt',).input_ids
      input_ids_len = input_ids.shape[1]
    
  if with_docstring:
    docstring_start = file_as_string.index(the_docstring) #this could error if the string isn't found
    docstring_end = docstring_start + len(the_docstring)
   
  assert docstring_start >= 0 and docstring_end >= 0 
  assert input_ids_len < 2048
  #print(len(file_as_string))
  #assert len(file_as_string) <= 2048 #<? <=? #TODO fix this!
  # test_file = open("TESTING2.txt", 'a')
  # test_file.write(file_as_string[docstring_start:docstring_end])
  # test_file.write("\n- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n" )
  # test_file.write(file_as_string + "\n=======================================================================================\n")
  return file_as_string, docstring_start, docstring_end #return shortened context string

def generate_output(remove_context_docstrings:bool, with_docstring:bool): #True if all docstrings in context should be removed
 '''This docstring will describe what this function does.'''
 
 #Loading CodeGen model:
 chosen_model = "codegen-350M-multi" #@param ["codegen-350M-nl", "codegen-350M-multi", "codegen-350M-mono", "codegen-2B-nl", "codegen-2B-multi", "codegen-2B-mono", "codegen-6B-nl", "codegen-6B-multi", "codegen-6B-mono", "codegen-16B-nl", "codegen-16B-multi", "codegen-16B-mono"]
 fp16 = True #@param {type:"boolean"} 
 
 #get model checkpoints
 if not os.path.exists(f'./checkpoints/{chosen_model}'):
   #I made the change to add 'f'
   f'wget -P checkpoints https://storage.googleapis.com/sfr-codegen-research/checkpoints/{chosen_model}.tar.gz && tar -xvf checkpoints/{chosen_model}.tar.gz -C checkpoints/'
  
 #available models
 models_nl = ['codegen-350M-nl', 'codegen-2B-nl', 'codegen-6B-nl', 'codegen-16B-nl']
 models_pl = ['codegen-350M-multi', 'codegen-2B-multi', 'codegen-6B-multi', 'codegen-16B-multi', 'codegen-350M-mono', 'codegen-2B-mono', 'codegen-6B-mono', 'codegen-16B-mono']
 models = models_nl + models_pl

 set_env()
 
 pad = 50256
 device = torch.device('cuda:0')
 ckpt = f'./checkpoints/{chosen_model}'
 
 if device.type == "cpu":
   print()
   print("force full precision for cpu!!")
   print()
   fp16 = False
 
 with print_time('loading parameters'):
   model = create_model(ckpt=ckpt, fp16=fp16).to(device) 

 with print_time('loading tokenizer'):
   if chosen_model in models_pl:
     tokenizer = create_custom_gpt2_tokenizer()
   else:
     tokenizer = create_tokenizer()
   tokenizer.padding_side = 'left'
   tokenizer.pad_token = pad
 
 #@markdown 
 rng_seed = 42 #@param {type:"integer"}
 rng_deterministic = True #@param {type:"boolean"}
 p = 0.95 #@param {type:"number"}
 t = 0.2 #@param {type:"number"}
 max_length = 2048 #number of tokens in input file plus what it generates
 max_length_sample = 1536 #@param {type:"integer"} #max length of output
 batch_size = 1 #@param {type:"integer"}
 
 set_seed(rng_seed, deterministic=rng_deterministic)
 
 with print_time('sampling'):
  input_context_files = glob.glob('../ALL_FILES/50000_output_ALL_with_docstring/*.txt')
  output_file_present = open('../ALL_FILES/Results/50000_all_files_scores_present_with_docstring_context.txt', 'w')
  #output_file_absent will only be used when the with_docstring == True, since code without a docstring can't be split up 
  #into "with docstring" and "docstring extracted"
  output_file_absent = open('../ALL_FILES/Results/50000_all_files_scores_absent_with_docstring_context.txt', 'w')
  #context_lengths = open('all_files_context_lengths_after_trim.txt', 'w') #not in use right now
  num_skipped = 0


  #determine which files to write to and hoe to modify context based on parameters to generate_output(). 
  #Write each file appropriately  
  for file in input_context_files: 
    opened_file = open(file, 'r')
    file_lines = opened_file.readlines()
    opened_file.close()
    index_line = file_lines[0] 
    context = ""

    #shouldn't include any files that should have been filtered out in previous preprocessing steps 
    if index_line[0:4] == "SKIP":
      print("skipped " + file + "...this shouldn't happen here.")

    
    for line in file_lines[1:]: #skip the first line of the file, which is used to list the docstring indices
      context = context + line

    #print(file_lines[0])

    docstring_indices = []
   
    #if the functions have no inherent docstrings
    if with_docstring == False: #no inherent docstrings
      func_name = file[0: len(file) - 7]
      func_name = func_name.split("_FUNC_")[1] #get only the name of the function as it is defined in the file
      func_number = int(file[len(file) - 6])
 
      counter = 0
      func_line_start = 0
      func_line_end = 0

      try:
        context_ast = ast.parse(context)
      except: #skip file if it does not compile
        num_skipped += 1
        #print("Checkpoint 1")
        continue
      
      #locate the function defined as func_name and get its start and end indices
      for node in ast.walk(context_ast):
        if isinstance(node, ast.FunctionDef):
          if node.name == func_name:
            if counter == func_number: 
              #keep track of how many functions of a particular name you pass
              #to ensure that, if there are duplicate function names in different classes, you choose the right one
              func_line_start = node.lineno
              func_line_end = node.end_lineno
              break
            counter = counter + 1 #keep track of how many functions of the same name you've passed to you get to the right one

      context = "" #TODO explain this line

      for line in file_lines[1:func_line_start]: #I don't want this to be inclusive
        #TODO affirm still starting at 1 because docstring indices for code with no docstring will be 0,0
        #Include all text up to the function deifnition so its start index can be measured as its character index, not its line index
        context = context + line
      
      #function's index = however many characters there currently are in the string of code leading up to it
      #plus one more character to get to the start of the function definition
      func_index = len(context) + 1 
      
      #now that we have the character index of the start of the function, 
      #append the rest of the original code (ie the function definition) back to the context
      for line in file_lines[func_line_start :]: 
        context = context + line
      
      #get the length, in characters, of the line of the function definition
      fundef_length = len(file_lines[func_line_start])

      func_index = func_index + fundef_length #get the index of the start of the function's code, after its definition

      #no docstring, so docstring_indices will be func_index + 1
      docstring_indices = [func_index + 1, func_index + 1] 
      #TODO verify why + 1?

      if "def" not in file_lines[func_line_start]:
        #Additional corner case
        #TODO come back and see what's wrong here eventually
        num_skipped = num_skipped + 1 
        #print("Checkpoint 2")
        continue

      
    else: #if with_docstring == True, get the docstring indices
      docstring_indices_str = index_line.strip().split(",") #we want code after the docstring
      docstring_indices.append(int(docstring_indices_str[0])) 
      docstring_indices.append(int(docstring_indices_str[1]))
    
    
    if remove_context_docstrings == True: 
      #remove all context docstrings and readjust remaining docstring indices accordingly
      #otherwise proceed
      docstring = context[docstring_indices[0] + 1 : docstring_indices[1]]
      context_1 = context[0:docstring_indices[0]] #up to the docstring we want to keep
      context_2 = context[docstring_indices[0]:] #rest of code  
      context_1 = remove_all_context_docstrings(context_1)
      
      context = context_1 + context_2 
      # print(context[docstring_indices[0]:docstring_indices[1]])
      # print("======================================================================================================================")
      # print(context)
      # print("===================================================================")
      #get new indices of the function docstring after all context docstrings have been removed
      docstring_len = len(docstring)
      docstring_start = context.index(docstring)
      docstring_end = docstring_start + docstring_len
     
      docstring_indices = [] #reset to add new indices
      docstring_indices.append(docstring_start)
      docstring_indices.append(docstring_end)
      assert docstring_indices[0] >= 0 and docstring_indices[1] >= 0
      
    
    #do the following regardless of whether or not remove_context_docstrings == True

    input_ids = tokenizer(
        context,
        truncation=True,
        padding=True,
        max_length=max_length,
        return_tensors='pt',
    ).input_ids
    
    input_ids_len = input_ids.shape[1]

    if input_ids_len >= 2048: #>=?
      try:
        #context will be either with or without docstrings at this point, depending on the function specifications
        context, docstring_indices[0], docstring_indices[1] = trim_code_window(context, input_ids_len, tokenizer, max_length, docstring_indices[0], docstring_indices[1], with_docstring) 
      except ValueError:
        num_skipped += 1
        print("Skipped trim because docstring was partially erased by trimming.")
        continue
    
    if with_docstring == False: 
      #these files have no inherent docstring, so they will only have 1 score
      #use present_file to write scores
      if context[docstring_indices[1]: ].strip() == "":
        num_skipped += 1
        #print("Checkpoint 4")
        continue
      
      loss_score = score(docstring_indices, device=device, model=model, tokenizer=tokenizer, context=context, pad_token_id=pad,)
      entropy = math.log2(loss_score[1]) 
      file_as_list = file.split("/")
      file_name_short = file_as_list[len(file_as_list) - 1]
      # output_file_present.write(file_name_short + "->" + str(entropy)) 
      # output_file_present.write('\n')
    
    else: #if with_docstring == True, score twice: once with docstring present and once with docstring removed 
      if context[docstring_indices[1]: ].strip() == "":
        print(file)
        print(context[docstring_indices[1] - 5:])
        # print(context[docstring_indices[1]:])
        # print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        # print(context[docstring_indices[0]:docstring_indices[1]])
        # print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        # print(context)
        print("===========================================================")
        #print("found one!")
        #print("Checkpoint 5")
        num_skipped += 1
        continue
     
      #keep the docstring
      loss_score = score(docstring_indices, device=device, model=model, tokenizer=tokenizer, context=context, pad_token_id=pad,)
      entropy = math.log2(loss_score[1]) 
      file_as_list = file.split("/")
      file_name_short = file_as_list[len(file_as_list) - 1]
      # output_file_present.write(file_name_short + "->" + str(entropy)) 
      # output_file_present.write('\n')
    
      #removing the docstring:
      docstring_length = docstring_indices[1] - docstring_indices[0]
      context = remove_docstring(context, docstring_indices[0], docstring_indices[1]) #remove docstring from context
      docstring_indices[1] = docstring_indices[1] - docstring_length #make sure we get the new index of start of code without the docstring
      docstring_indices[0] = docstring_indices[1]

      #context_lengths.write(file + "-->" + str(len(context)) + "\n") #writing the length of the context without the docstring so it doesn't count
     
      #with docstring removed
      loss_score = score(docstring_indices, device=device, model=model, tokenizer=tokenizer, context=context, pad_token_id=pad,)
      entropy = math.log2(loss_score[1]) 
      file_as_list = file.split("/")
      file_name_short = file_as_list[len(file_as_list) - 1]
      # output_file_absent.write(file_name_short + "->" + str(entropy)) 
      # output_file_absent.write('\n')
   
  print("Done writing files")
  # output_file_present.write("DONE WRITING FILES" + "->" + str(num_skipped))
  # output_file_absent.write("DONE WRITING FILES" + "->" + str(num_skipped))
  print(num_skipped)
  output_file_present.close()
  output_file_absent.close()

if __name__ == "__main__":
  remove_context_docstrings = False
  with_docstring = True 
  generate_output(remove_context_docstrings, with_docstring)

 #def generate_output(remove_context_docstrings:bool, with_docstring:bool):

