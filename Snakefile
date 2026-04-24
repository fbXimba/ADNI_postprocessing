import os
import pandas as pd
from snakemake.io import expand
import glob

#snakemake --use-conda --cores 1 --rerun-incomplete --latency-wait 900 --keep-going -p 

configfile: "config.yaml"

# Project root
PROJECT_ROOT = os.getcwd()

# File paths
data_dir = config["dirs"]["data_dir"] # path to the directory containing the input data
output_dir = config["dirs"]["output_dir"] # path to the directory where the processing steps and dataset will be stored
processed_dir = config["dirs"]["processed_dir"] # path to the directory where the processeing steps will be stored
dataset_dir = config["dirs"]["dataset_dir"] # path to the directory containing the dataset

# Create the output directories if they don't exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(processed_dir, exist_ok=True)
os.makedirs(dataset_dir, exist_ok=True)

# Read all files in the data directory and create a list of input files
input_files = glob.glob(os.path.join(data_dir, "*.nii.gz"))
SUBJECTS = [os.path.basename(f).split(".")[0] for f in input_files] # extract subject names from file names

# Define the path to the post-processed data
POSTPROCESSED_DATASET = expand(os.path.join(dataset_dir, "{subject}_processed.nii.gz"), subject=SUBJECTS)

rule all:
    input:
        POSTPROCESSED_DATASET

rule scale_GL:
    input:
        gen_file = os.path.join(data_dir, "{subject}.nii.gz")
    output:
        scaled = os.path.join(processed_dir, "{subject}", "{subject}_scaled.nii.gz")
    params:
        p = processed_dir
    log:
        "logs/{subject}.scale.log"
    shell:
        r"""
        set -euo pipefail
        export PYTHONPATH="${{PYTHONPATH:-}}:{PROJECT_ROOT}"
        mkdir -p logs {params.p}/{wildcards.subject}
        conda run -n env-prep python scripts/scale_gl.py \
            --input {input.gen_file} \
            --output {output.scaled} \
            >> {log} 2>&1
        """

rule resample:
    input:
        scaled = os.path.join(processed_dir, "{subject}", "{subject}_scaled.nii.gz")
    output:
        resampled = os.path.join(processed_dir, "{subject}", "{subject}_resampled.nii.gz")
    params:
        p = processed_dir,
        new_size = config["resample"]["new_size"],
        interpolator = config["resample"]["interpolator"]
    log:
        "logs/{subject}.resample.log"
    shell:
        r"""
        set -euo pipefail
        export PYTHONPATH="${{PYTHONPATH:-}}:{PROJECT_ROOT}"
        mkdir -p logs {params.p}/{wildcards.subject}
        conda run -n env-prep python scripts/resample.py \
            --input {input.scaled} \
            --output {output.resampled} \
            --new_size {params.new_size[0]} {params.new_size[1]} {params.new_size[2]} \
            --interpolator {params.interpolator} \
            >> {log} 2>&1
        """

rule copy_to_dataset:
    input:
        resampled = os.path.join(processed_dir, "{subject}", "{subject}_resampled.nii.gz")
    output:
        dataset = os.path.join(dataset_dir, "{subject}_processed.nii.gz")
    params:
        dataset_dir = dataset_dir
    shell:
        r"""
        set -euo pipefail
        mkdir -p {params.dataset_dir}
        cp {input.resampled} {output.dataset}
        """