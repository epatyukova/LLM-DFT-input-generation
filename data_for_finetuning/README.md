This folder contains Quantum Espresso input files extracted from aiida archives from this repository https://archive.materialscloud.org/record/2023.81 described in the paper https://arxiv.org/abs/2305.17274 

Unaries contain input files with unaries (Li, B, C, etc with different structures (not necessarily observed in the real world)) (2840 files)

Oxides contain input files of oxides M_xO_y with different stoichiometries (x,y) (also not necessarily observed or corresponding to known oxidation states) (4621 files)

There is also a python notebook used to extract data from aiida archive  

Instruction-dataset-generation notebook allows formatting the data in the 'input'-'output' format to finetune the TinyLlama model (the fine-tuning script using the whole set of weights fine-tuning, without any peft techniques is availible in their repo https://github.com/jzhang38/TinyLlama/blob/main/sft/finetune.py)
