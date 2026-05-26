# **ADNI_postprocessing**

This repository contains scripts for postprocessing synthetic MRI data to a state similar to the output of Freesurfer's *autorecon1*.

Purpose of this work is to provide a reproducible pipeline for postprocessing of T1 head volumes :man:.

## Processing steps
- **Rescaling intensity** to the wanted GL values range (0 - mean maximum of the training dataset per group)
- **Resampling** to the wanted shape (256x256x256)
- **Save** the final product in the designed directory


## Repo structure
- `scripts/` preprocessing scripts
    - `scale_GL.py` intensity rescaling (original values' range in the file)
    - `resmple.py` spatial resampling with chosen interpolator

- `config.yaml` configuration file with directories and parameters

- `Snakefile` snakemake file

## Data :file_folder:
Data not included. Structure expected: a folder with the images to precess inside. See configuration file.

## FYI
The intermediate images of the processed are made as to be temporary, they are deleted once the final product is obtained. See `Snakefile`

## Note
This postprocessing routine was used to provide a coherent dataset to test synthetic images generation. :brain:

## Usage exaples 

### Configuration

Modify `config.yaml` with your info and check the ranges inside `scale_gl.py`.

### snakemake :snake:

**dry run** with print command 

```bash
snakemake -n -p
```

**run all rules** :running_woman:
```bash
snakemake --use-conda --cores 50 --rerun-incomplete --latency-wait 900 --keep-going -p 
```

## Requirements

TODO :see_no_evil: :hear_no_evil: :speak_no_evil: