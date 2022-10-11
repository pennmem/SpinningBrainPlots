# Overview
As it currently stands, the brain plotting cannot be run on rhino due to display issues.
To get around this, we can get all of our data ready, pack it up into a nice format, and then scp it to your local computer for generation.
Thus, you must install the special envirnment on your local computer. Then you can use the provided ipynb to generate the data on rhino.

# Install Environment
[This is done on the local computer]

Create the conda environment
```bash
conda env create -f brainPlot.yml
```

If anything fails and you need to run it again to update it, use the following command
```bash
conda env update -n brainPlot -f nora.yml
```

If gnu readlines fails, you can just remove the whole line from the yml file and run the update command\
If an existing installation of vtk is already installed by your system, you can
  1. remove it from you system and run the update command
  1. remove it from the yml file (if the version is 8.2.0) and run the update command

# Generate the data
[This is done on rhino]

Run the *GenerateBrainData.ipynb* file in jupyterLab (or other) to generate the brain_plot_data.npz 

# Build the diagram
[This is done on the local computer]

```bash
conda activate brainPlot
python3 genBrainPlot.py
```
