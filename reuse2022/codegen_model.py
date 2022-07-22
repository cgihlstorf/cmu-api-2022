import os
import glob
import torch
import math
from jaxformer.hf.sample import truncate as do_truncate
from jaxformer.hf.sample import set_env, set_seed, print_time, create_model, create_custom_gpt2_tokenizer, create_tokenizer, sample
from jaxformer.hf.score import score #main?

def trim_code_window(file_path:str, file_as_string:str, input_ids_len:int, tokenizer, max_length:int):
  #only use this for present files!
  present_file = open(file_path, 'r')
  present_file_string = present_file.read()
  present_file.close()

  while(input_ids_len >= 2048):
    if len(file_as_string) >= 5000:
      new_len = len(file_as_string) // 2
      file_as_string = file_as_string[new_len:]
    else:
      file_as_string = file_as_string[10:] #decrease size by 10 characters...okay?
    input_ids = tokenizer(file_as_string, truncation=True, padding=True, max_length=max_length, return_tensors='pt',).input_ids
    input_ids_len = input_ids.shape[1]

  #write the present file
  #you don't technically need to do this - you just need to return the context. But I guess writing it would be best
  output_file = open(file_path, 'w')
  output_file.write(file_as_string) #does this overwrite???
  #assert len(output_file.read()) == len(file_as_string) 
  output_file.close()

  #now let's modify the untouched file in the docstring_absent folder to keep the context length (= length minus docstring) equal
  absent_file_path = file_path.replace("docstring_present", "docstring_absent") #get name of the file without the docstring
  #print("absent_file_path is: ", absent_file_path)
  absent_file_read = open(absent_file_path, 'r')
  absent_file_string = absent_file_read.read()
  absent_file_read.close()

  docstring_length = len(present_file_string) - len(absent_file_string) #the only differene between these should be the docstirng length
  #the line below says: the length of the current file (which doesn't end in a docstring) plus the length of the docstring
  #should equal the length of the file that has the docstring by default. Given this length, subtract from this the length
  #of the new file with a docstring that was trimmed down. This will give you the line number from the original non-trimmed
  #file that this new docstring_present file starts at. Start the docstring_absent file at the same place, so that it won't 
  #include any additional context, or the docstring from the docstring_present file
  starting_place = len(absent_file_string) + docstring_length - len(file_as_string)
  #print("Starting place is ", starting_place, ". Length of original file is ", len(present_file_string))
  try:
    assert len(present_file_string) == len(absent_file_string) + docstring_length #before trimming
    #print("Trim assertion 1 passed")
    absent_file_string = absent_file_string[starting_place:] #trim this string from the same place the docstring_present string was trimmed
    assert len(file_as_string) == len(absent_file_string) + docstring_length #after trimming
  except:
    print("Error: ", file_path)
  #print("Trim assertion 2 passed")
  # print("trimmed with docstring: ", len(file_as_string))
  # print("trimmed without docstring: ", len(absent_file_string))
  absent_file_write = open(absent_file_path, 'w') 
  absent_file_write.write(absent_file_string) #overwrite the docstring_absent file with its trimmed version

  return file_as_string
  
def generate_output(): 

 #Loading model and tokenizer, code as per the tutorial:
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
 
 # (2) preamble 
 
 set_env()
 
 pad = 50256
 device = torch.device('cuda:0')
 ckpt = f'./checkpoints/{chosen_model}'
 
 if device.type == "cpu":
   print()
   print("force full precision for cpu!!")
   print()
   fp16 = False
 
 # (3) load
 
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
  code_ds_present = glob.glob('../with_docstring/docstring_present/*.txt')
  output_file_present = open('../results_codegen_ALL_with_context/docstring_present_scores.txt', 'w')
  output_file_absent = open('../results_codegen_ALL_with_context/docstring_absent_scores.txt', 'w')
 
  for file in code_ds_present[0:20000]:
    opened_file = open(file, 'r')
    context = opened_file.read() 
    opened_file.close()
    input_ids = tokenizer(
        context,
        truncation=True,
        padding=True,
        max_length=max_length,
        return_tensors='pt',
    ).input_ids
    input_ids_len = input_ids.shape[1]

    if input_ids_len >= 2048: #>=?
      opened_file_two = open(file, 'r')
      file_as_string = opened_file_two.read()
      context = trim_code_window(file, file_as_string, input_ids_len, tokenizer, max_length) #writes to files and returns the newly trimmed file context as a string

    score_present = score(device=device, model=model, tokenizer=tokenizer, context=context, pad_token_id=pad)
    entropy_present = math.log2(score_present[1]) 
    file_as_list = file.split("/")
    file_name_short = file_as_list[len(file_as_list) - 1]
    output_file_present.write(file_name_short + "->" + str(entropy_present)) #hopefully each output will get its own line
    output_file_present.write('\n')
    
  print("Done writing present files")

  code_ds_absent = glob.glob('../with_docstring/docstring_absent/*.txt')
  
  for file in code_ds_absent[0:20000]:
    opened_file = open(file, 'r')
    context = opened_file.read() 
    #print("getting score for absent file...")
    try:
      score_absent = score(device=device, model=model, tokenizer=tokenizer, context=context, pad_token_id=pad)
      entropy_absent = math.log2(score_absent[1]) 
      file_as_list = file.split("/")
      file_name_short = file_as_list[len(file_as_list) - 1]
      output_file_absent.write(file_name_short + "->" + str(entropy_absent)) #hopefully each output will get its own line
      output_file_absent.write('\n')
    except:
      output_file_absent.write("SKIP")
      output_file_absent.write('\n')
    
  
  print("Done writing absent files")
 
  output_file_present.close()
  output_file_absent.close()

  
 
if __name__ == "__main__":
 generate_output()

