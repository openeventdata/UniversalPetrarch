#!/bin/bash

# Root folder where TurboParser is installed.
root_folder=$1
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${root_folder}/deps/local/lib"

# Set options.
language=arabic #english_proj
prune=true
posterior_threshold=0.0001
model_type=standard
labeled=true

# Set path folders.
path_bin=${root_folder}
path_models=${root_folder}/models/${language}

# Set file paths.
suffix=parser_standard_clean_coarse
file_model=${path_models}/${language}_${suffix}.model

# Run the parser.
file_test=$2
file_prediction=${file_test}.pred

${path_bin}/TurboParser \
    --test \
    --evaluate \
    --file_model=${file_model} \
    --file_test=${file_test} \
    --file_prediction=${file_prediction}

