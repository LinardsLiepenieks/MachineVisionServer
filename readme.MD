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

Install the spacy model - run the post install script

FOR WINDOWS

```
post_install.bat
```

FOR macOS/Linux

```
./post_install.sh
```

## First-time Setup with Django

(use python3 on mac os)

1. Configure your database in `myproject/settings.py` (SQLite is default)

2. Migrate the database:

   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

3. Create a superuser (admin account):

   ```
   python manage.py createsuperuser
   ```

4. Run the development server:

   ```
   python manage.py runserver
   ```

   Your Django site should now be accessible at `http://127.0.0.1:8000/`

   To connect to the server via app run

   ```
   python manage.py runserver 0.0.0.0:8000
   ```

   To connect to the server via mobile device use your computers ip address as the endpoint.
   YOU NEED TO BE CONNECTED ON THE SAME NETWORK.

## Deactivating the Virtual Environment

When you're done working in the virtual environment:

```
deactivate
```

Remember to activate your virtual environment every time you work on your project!
