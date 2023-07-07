# E-commerce Backend Application 
        custom developer ecommerce plateform
        for brands and marketplace

## `Description`
This is end to end solution for ecommerce brand and marketplace

![alt text][logo]

[logo]: https://alche-ecw.s3.amazonaws.com/e-comm+logo.jpeg "E-comm Logo logo"

## Technologies
        Frameworks: Django, Django Rest Framework
        DB: Mysql

## Main Modules
        -Ecomm App
        
## External Services Used
         - SMS Service
         - Email Service

## `Installation Guide for Command Line`
1. Clone repo

2. inside cloned repo create a virtual environment using below command

    ```virtualenv venv --python=python3```
    
    Note: if you did not install python3 on your system please install it first and follow the guide of python3 installation 

3. Now activate virtual environment using below command

    ```source ./venv/bin/activate```

4. Now install dependencies of our system by typing below command

    ```pip install  -r requirement.txt```
    
5. Now go to ./ecomm_app/settings.py file and add below credentials for database in database section.
   
   replace this
   
   ``` 
   'default': {
            'ENGINE': 'django.db.backends.mysql',

            'NAME': os.environ['dbName'],
            "HOST": os.environ['hostName'],
            "USER": os.environ['username'],
            "PASSWORD": os.environ['password'],
            "PORT": os.environ['port']

    }
   ```

    with this
    
    ```
   'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'ecomm_db',
            "HOST": 'localhost',
            "USER": 'root',
            "PASSWORD": 'YOUR_ROOT_PASSWOR_WILL_BE_HERE',
            "PORT": 3306

    }
   ```
   
   **Note:** if you did not install mysql locally then please install it and create a database with name **ecomm_db**
   
6. Now run migrations with below command

    ```python manage.py migrate```

7. Now export data from any staing db and import it in your localhost db

8. Now run the server successfully using below command

    ```pyton manage.py runserver```

## `Installation Guide for Pycharm`
1. Clone the Repo to your directory.
2. Open the code folder in your IDE (eg. PyCharm)
3. Open up the directory in your terminal and install requirements by running
   - **`pip install -r requirements.txt`**
4. Now go to ./ecomm_app/settings.py file and add below credentials for database in database section.
   
   replace this
   
   ``` 
   'default': {
            'ENGINE': 'django.db.backends.mysql',

            'NAME': os.environ['dbName'],
            "HOST": os.environ['hostName'],
            "USER": os.environ['username'],
            "PASSWORD": os.environ['password'],
            "PORT": os.environ['port']

    }
   ```

    with this
    
    ```
   'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'ecomm_db',
            "HOST": 'localhost',
            "USER": 'root',
            "PASSWORD": 'YOUR_ROOT_PASSWOR_WILL_BE_HERE',
            "PORT": 3306

    }
   ```
   
   **Note:** if you did not install mysql locally then please install it and create a database with name **ecomm_db**
5. Run migrations by running commands:
    - **`python manage.py makemigrations`**
    - **`python manage.py migrate`**
6. Start project locally on port 8000 by running **`python manage.py runserver`**.