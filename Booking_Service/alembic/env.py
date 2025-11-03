from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os, sys, json
from dotenv import load_dotenv
import boto3

# ---- Load environment variables from .env ----
load_dotenv()

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---- Function: Fetch DB password from AWS Secrets Manager ----
def get_db_password(secret_name, region_name):
    try:
        client = boto3.client("secretsmanager", region_name=region_name)
        response = client.get_secret_value(SecretId=secret_name)
        secret_string = response["SecretString"]

        try:
            # Try to parse as JSON first
            secret_json = json.loads(secret_string)
            return secret_json.get("password", secret_string)
        except json.JSONDecodeError:
            return secret_string
    except Exception as e:
        print("❌ ERROR: Could not fetch DB password from AWS Secrets Manager.")
        print("   Make sure your AWS CLI is configured and IAM user has permissions.")
        print(f"   Details: {e}")
        sys.exit(1)

# ---- Build database URL ----
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME")
AWS_REGION = os.getenv("AWS_REGION")
DB_SECRET_NAME = os.getenv("DB_SECRET_NAME")

DB_PASSWORD = get_db_password(DB_SECRET_NAME, AWS_REGION)
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
config.set_main_option("sqlalchemy.url", DB_URL)

# Replace this with your Base.metadata if using models
target_metadata = None

# ---- Offline migrations ----
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# ---- Online migrations ----
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
