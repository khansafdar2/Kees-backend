import pymysql
from ecomm_app.settings.staging import *
from ecomm_app.settings.production import *

pymysql.install_as_MySQLdb()
