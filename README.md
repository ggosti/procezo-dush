# procezo-dush

Procezo's aim is to process records that are derived from user sessions obtained from different kinds of experiences, either immersive or real. Here you can find the relational datastructure and Dushbord for Procezo.

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
