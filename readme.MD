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

# Installing Redis Server (Version 5 or higher)

Redis is an open-source, in-memory data structure store used as a database, cache, message broker, and queue. This guide will help you install Redis server version 5 or higher on various operating systems.

## Prerequisites

- Administrative access to your system
- Internet connection

## Windows

Redis doesn't officially support Windows. However, you can use Windows Subsystem for Linux (WSL) or a third-party build.

1. Install WSL by following Microsoft's official guide.
2. Once WSL is installed, follow the Linux instructions below.

Alternatively, you can use the unofficial Windows port from [tporadowski/redis](https://github.com/tporadowski/redis/releases).

## macOS

Use Homebrew to install Redis:

```bash
brew install redis
```

To start Redis:

```bash
brew services start redis
```

## Linux (Ubuntu/Debian)

1. Update your package list:

   ```bash
   sudo apt update
   ```

2. Install Redis:

   ```bash
   sudo apt install redis-server
   ```

3. Verify the installation:
   ```bash
   redis-server --version
   ```

## Verifying Redis Version

After installation, verify that you have Redis 5 or higher:

```bash
redis-cli --version
```

## Starting Redis Server

On most systems, Redis will start automatically after installation. If it doesn't:

```bash
sudo systemctl start redis-server
```

## Testing Redis

To test if Redis is working correctly:

1. Start the Redis CLI:

   ```bash
   redis-cli
   ```

2. Type `ping` and press Enter. If Redis is running, it should respond with `PONG`.

3. Exit the Redis CLI by typing `exit` and pressing Enter.

Remember to secure your Redis installation in production environments by setting a password and configuring appropriate network settings.

## Deactivating the Virtual Environment

When you're done working in the virtual environment:

```
deactivate
```

Remember to activate your virtual environment every time you work on your project!
