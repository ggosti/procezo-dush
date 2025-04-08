# procezo-dush

Procezo's aim is to process records that are derived from user sessions obtained from different kinds of experiences, either immersive or real. Here you can find the relational datastructure and Dushbord for Procezo.

## Environment setup

Setting up a virtual environment for development is always a good practice. We will create and activate a conda environment. You can alternatively use venv. In your terminal, execute the following:

```
conda create --name procezo-dush
conda deactivate # Only if necessary. Make sure that you are not already in any other environment before activating.
conda activate procezo-dush
```

You can verify that you are in the virtual environment by executing `which python`, which should print out:
```
/path/to/miniconda3/envs/procezo-dush/bin/python
```
Your requirements.txt should contain the following packages:
```
dash
pandas
scipy
matplotlib
uvicorn[standard]
fastapi[standard]
```
In the virtual environment, install all necessary packages
```
python -m pip install -r requirements.txt
```

## Test Data Structure

This web app is based on a datastrucutre made on classes defined in `models.py`,
and routines that actualy build the data structure `utils.py`.
`models.py` defines classes for projects, groups, and records.
`utils.py` builds the relational datastructure.
To test this datastructure run:

```
python -m doctest models.py
```
and

```
python -m doctest utils.py
```

If necessary in the debbagging phase the database can be loaded with:
```
python utils.py
```
