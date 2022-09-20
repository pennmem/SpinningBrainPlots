# Install Environment
Create the conda environment
```bash
conda env create -f brainPlot.yml
```
\
If anything fails and you need to run it again to update it, use the following command
```bash
conda env update -n brainPlot -f nora.yml
```
\
If gnu readlines fails, you can just remove the whole line from the yml file and run the update command\
If an existing installation of vtk is already installed by your system, you can\
  1. remove it from you system and run the update command
  1. remove it from the yml file (if the version is 8.2.0) and run the update command

# Generate the data
Run the GenerateBrainData.ipynb file in jupyterLab (or other) to generate the brain_plot_data.npz 

# Build the diagram
```bash
conda activate brainPlot
python3 genBrainPlot.py
```
