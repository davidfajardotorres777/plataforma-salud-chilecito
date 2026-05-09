# plataforma-salud-chilecito
"Plataforma integral de gestión de turnos y datos clínicos para el departamento de Chilecito". Puedes complementar la frase agregando que está respaldada por una arquitectura de base de datos políglota
Data Access Objects for health care

Before you begin, you’ll need:
IDE or Text editor
Python 3.12
pip install --upgrade pip
Create database schema
dbscripts
Create the virtual environment
python -m venv ./venv
Activate the virtual environment
source ./venv/bin/activate
Install jupyter
pip install notebook==7.5.5
Install pandas
pip install pandas==3.0.2
Install Libs
pip install sqlalchemy==2.0.49
For Oracle Databases
pip install oracledb==3.4.2
For install Oracle Database with docker
sudo apt install docker.io

sudo docker run -d --name oracle-xe -p 1521:1521 -p 8080:8080 -e ORACLE_PASSWORD=admin gvenzl/oracle-xe

sudo docker start oracle-xe

sudo docker ps

For PostgreSQL
Install PostgreSQL Libs
sudo apt-get install libpq-dev python-dev
sudo apt-get update
pip install psycopg2
