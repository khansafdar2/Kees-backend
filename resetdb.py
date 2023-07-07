
import pymysql, shutil, os, glob, subprocess, requests, time, json
# from ecomm_app import settings

# host = settings.DATABASES['default']['HOST']
# user = settings.DATABASES['default']['USER']
# password = settings.DATABASES['default']['PASSWORD']
# database = settings.DATABASES['default']['NAME']

# connection = pymysql.connect(host=host, user=user, password=password)

try:
    # # Database create and drop
    # dbCursor = connection.cursor()
    #
    # try:
    #     print("Database Exist")
    #     dropdb = "DROP DATABASE " + database
    #     dbCursor.execute(dropdb)
    #     print("Database Dropped")
    #
    #     createdb = "CREATE DATABASE " + database
    #     dbCursor.execute(createdb)
    #     print("Database Created")
    #
    # except:
    #     print("Database not exist")
    #     createdb = f'''CREATE DATABASE IF NOT EXISTS {database}'''
    #     dbCursor.execute(createdb)
    #     print("Database Created")
    #
    # connection.close()

    # Remove Migrations Files
    filepath = ['authentication', 'cms', 'crm', 'discount', 'notification', 'order', 'products', 'setting', 'shipping', 'paymentgateway', 'dashboard', 'storefront', 'vendor', 'social_feed']
    print("Remove Migration Files")
    for app in filepath:
        files = glob.glob(f'{app}\migrations\*')
        for f in files:
            if f == f"{app}\migrations\__init__.py":
                continue
            else:
                if os.path.isdir(f):
                    shutil.rmtree(f)
                elif os.path.isfile(f):
                    os.remove(f)
                else:
                    print("Not a directory or file")
    #
    # # Run Migrations
    # print("Run Migrations")
    # subprocess.Popen(["python", "manage.py", "makemigrations"], stdout=subprocess.PIPE).communicate()
    # #
    # print("Migrate")
    # subprocess.Popen(["python", "manage.py", "migrate"], stdout=subprocess.PIPE).communicate()
    #
    # time.sleep(8)
    #
    # print("Create SuperUser")
    # os.system("python manage.py createsuperuser --username=admin --email=sameed.awais@alchemative.com --noinput")
    #
    # print("Run Server")
    # subprocess.Popen(["python", "manage.py", "runserver"])
    # time.sleep(8)
    #
    # print("get token")
    # token_response = requests.request("GET", f"{settings.HOST_URL}/products/password_change")
    # get_token = json.loads(token_response.text)
    #
    # print("Insert Dummy Data")
    # payload = {}
    # headers = {'Authorization': get_token['token']}
    # requests.request("POST", f"{settings.HOST_URL}/products/insert_dummy_data", headers=headers, data=payload)

    print("Successfully Complete")

except Exception as e:
    print("Exeception occured:{}".format(e))
    # connection.close()
