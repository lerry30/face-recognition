# Installation

# ...

# Find your conda installation
ls ~/miniconda3/bin/conda

# If found, run initialization
~/miniconda3/bin/conda init

# Restart terminal or reload
source ~/.bashrc

conda create -n face_recognition_env python=3.9
conda activate face_recognition_env
conda install -c conda-forge opencv face_recognition requests

# -------------------------------------------------------------------------------------

# If you'll try to open the conda project you'll need to initialized it first

~/miniconda3/bin/conda init
source ~/.bashrc

# Once there's something like 'base' infront of the command execution line, it means you're
# in the base virtual environment and you're able to use command 'conda'

# List your conda virtual environment
conda env list

# Enable your virtual environment where all dedicated libraries for your project are installed
conda activate your_venv

