from dotenv import load_dotenv
import os

load_dotenv()

db_user = os.environ['DB_USER']
db_pwd = os.environ['DB_PASSWORD']
db_host = os.environ['DB_HOST']
db_name = os.environ['DB_NAME']
db_port = os.environ['DB_PORT']

# Assuming you are using PostgreSQL
DATABASE_CONNECTION = f'postgresql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}'
