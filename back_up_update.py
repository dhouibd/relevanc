import pandas as pd
import os
import git
import psycopg2
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from distutils.dir_util import copy_tree
import shutil

# default_args = {
#     'owner': 'hadrien',
#     'depends_on_past': False,
#     'start_date': datetime(2018, 12, 12),
#     'email': ['hadrien.negros@relevanc.com'],
#     'email_on_failure': True,
#     'email_on_retry': True,
#     'retries': 1,
#     'retry_delay': timedelta(minutes=5)
# }

#dag = DAG('Back_up_databases', default_args=default_args, schedule_interval="0 6 * * 1")

def replace(file_name,name):
    f = open(file_name, 'r')
    filedata = f.read()
    f.close()

    newdata = filedata.replace('CREATE TABLE "'+name+'"','CREATE TABLE IF NOT EXISTS public.'+name)

    f = open(file_name, 'w')
    f.write(newdata)
    f.close()
    return

# Mapr Target Path
#env_name = Variable.get("env_name")
# env_name = "dev"
# if env_name == "prod":
#     TARGET_PATH = "/mapr/relevanc.{0}/data/global/enhanced/backup-database".format(env_name)
# else:
#     TARGET_PATH = "/mapr/relevanc.{0}/data{0}/global/enhanced/backup-database".format(env_name)

TARGET_PATH = "/Users/donia/Documents/relevanc/"

os.chdir(TARGET_PATH)

# def backup(**context):
# loader la liste des databases
with open('db.json') as json_data:
    data_dict = json.load(json_data)

with open('config.json') as json_config:
    configs = json.load(json_config)

# pull la version sur git en local
repo = git.Repo(os.getcwd())
index = git.Repo.init(os.getcwd()).index
origin = repo.remotes.origin
origin.fetch()
origin.pull()

#message du commit
message = "back-up-" + datetime.now().strftime("%d-%m-%Y")

repo_date = datetime.now() - relativedelta(days = 7)
repo_date = repo_date.strftime("-%d-%m-%Y")

# copie du repo dans backup-database-%(d-7)-%m-%Y
# fromDirectory =  os.getcwd()
# toDirectory = os.getcwd() + repo_date + '/'
# os.mkdir(toDirectory)
# copy_tree(fromDirectory, toDirectory)

# supression du .git du dossier
# shutil.rmtree(os.getcwd() + repo_date + '/.git')

# Faire le tour des databases pour changer les csv
for database in data_dict:
    name_db = database.get('name')
    config = database.get('config_name')
    for config in configs:
        name = config.get('name')
        configuration = config.get('config')
        if config == name:
            break

    # if not os.path.exists(repertoire):
    conn = psycopg2.connect("host='{}' port={} dbname='{}' user={} password={}".format(configuration['host'], configuration['port'], configuration['dbname'], configuration['username'], configuration['pwd']))
    # sql = "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name='" + name + "';"

    sql = "select * from " + name_db + ";"
    data = pd.read_sql_query(sql, conn)

    if name_db not in os.listdir():
        # creation du fichier create-.sql
        os.makedirs(name_db)
        file_name = name_db + '/create_'+ name_db + '.sql'
        f = open(file_name, 'a+')
        f.write("BEGIN;")
        f.write("\n")
        f.write(pd.io.sql.get_schema(data, name_db, con=config))
        f.write(";\n")
        f.write("COMMIT;")
        f.close()

        # add IF NOT EXISTS dans le create.sql
        replace(file_name,name_db)

    # ecriture du csv
    file_name = name_db + '/' + name_db + ".csv"
    data.to_csv(file_name, index=False, sep=',')

# add commit et push les modifications
repo.git.add([TARGET_PATH])
index.commit(message)
origin.push()

# back_up_db = PythonOperator(
#             task_id='back_up_db',
#             provide_context=True,
#             python_callable=backup,
#             trigger_rule="all_success",
#             dag=dag
# )
