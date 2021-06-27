# Welcome to flask-todo!


## How To Run This Application

flask-todo is a minimalistic application developed for beginners to teach them the basics of creating a web application with flask. Below you can see how to start the application using a local SQLite database.

*Note: requires python 3*

1. Create a Python virtual environment and activate it:

    *For Unix and Mac computers:*

    ```
    $ python3 -m venv env
    $ source env/bin/activate
    (venv) $ _
    ```

    *For Windows computers:*

    ```
    $ python -m venv env
    $ env\scripts\activate
    (env) $ _
    ```

2. Import the Python dependencies into the virtual environment:

    ```
    (venv) $ pip install -r requirements.txt
    ```

3. Set flask environment variable:

    *For Unix and Mac computers:*

    ```
    (env) $ export FLASK_APP=app.py

    ```

    *For Windows computers:*

    ```
    (env) $ set FLASK_APP=app.py

    ```

4. Create a local database:

    ```
    (env) $ flask shell
    >>> from app import db
    >>> db.create_all()

    ```
    *alternatively, to use already existing migrations, run*

    ```
    (env) $ flask db upgrade
    ```

4. Start the development web server:

    ```
    (env) $ flask run
    ```

5. Access the application on your web browser at `http://localhost:5000`. Register a new account, log in, create
a new todo list and add items to it.
