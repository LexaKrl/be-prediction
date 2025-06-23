import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Database
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "finance")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

    # RabbitMQ
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "root")
    RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "root")
    RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "finance.predict")

    # ML model
    MODEL_PATH = os.getenv("MODEL_PATH", "finance_predictor.joblib")