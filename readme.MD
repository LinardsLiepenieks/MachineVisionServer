# Setting Up a Virtual Environment with venv

## Creating a Virtual Environment

### Windows

```
python -m venv myenv
```

### Mac

```
python3 -m venv myenv
```

## Activating the Virtual Environment

### Windows

```
myenv\Scripts\activate
```

### Mac

```
source myenv/bin/activate
```

## Adding venv to .gitignore

Add the following line to your `.gitignore` file:

```
myenv/
```

## Installing Requirements

Once your virtual environment is activated:

```
pip install -r requirements.txt
```

## Deactivating the Virtual Environment

When you're done working in the virtual environment:

```
deactivate
```
