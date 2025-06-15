
# Find your conda installation
ls ~/miniconda3/bin/conda

# If found, run initialization
~/miniconda3/bin/conda init

# Restart terminal or reload
source ~/.bashrc

conda create -n face_recognition_env python=3.9
conda activate face_recognition_env
conda install -c conda-forge opencv face_recognition requests
