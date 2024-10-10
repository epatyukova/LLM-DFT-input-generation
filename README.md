# LLM-DFT-input-generation
Here we plan use LLMs to generate input files for different DFT packages.

Current state: file Input-generation-vanilla aims to generate input for single point energy calculations with Quantum Espresso. It uses internal knowledge of models. Example of generated files can be found in generated_files/ folder.

In Prompting-with-input-files.ipynb I tried to show the llama-3-8B_instruct the input file, and ask to generate the similar one for specific compound. It works fine.
