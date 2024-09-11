# Setting Up a Virtual Environment with venv and Django

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

## First-time Setup with Django

1. Install Django (if not in requirements.txt):

   ```
   pip install django
   ```

2. Create a new Django project:

   ```
   django-admin startproject myproject
   ```

3. Navigate to the project directory:

   ```
   cd myproject
   ```

4. Create a new app (optional):

   ```
   python manage.py startapp myapp
   ```

5. Configure your database in `myproject/settings.py` (SQLite is default)

6. Migrate the database:

   ```
   python manage.py migrate
   ```

7. Create a superuser (admin account):

   ```
   python manage.py createsuperuser
   ```

8. Run the development server:

   ```
   python manage.py runserver
   ```

   Your Django site should now be accessible at `http://127.0.0.1:8000/`

## Deactivating the Virtual Environment

When you're done working in the virtual environment:

```
deactivate
```

Remember to activate your virtual environment every time you work on your project!
