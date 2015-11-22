import os

os.remove("rm -rf db_repository")
os.remove("app.db")

os.system("db_create.py")
os.system("db_migrate.py")
os.system("create_roles.py")
