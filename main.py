from database import Database
from ml_model import FinancePredictor
from rabbit_consumer import RabbitMQConsumer
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_user(user_id: int):
    logging.info(f"Обработка пользователя: {user_id}")

    db = Database()
    predictor = FinancePredictor()

    try:
        df = db.get_user_finances(user_id)

        if df.empty:
            logging.warning(f"Нет данных для пользователя {user_id}")
            prediction = 0.0
        else:
            prediction = predictor.predict_future(df)
            logging.info(f"Прогноз для {user_id}: {prediction:.2f}")

        db.save_prediction(user_id, prediction)

    except Exception as e:
        logging.error(f"Ошибка обработки пользователя {user_id}: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    consumer = RabbitMQConsumer(process_user)
    try:
        consumer.start_consuming()
    except KeyboardInterrupt:
        logging.info("Остановка сервиса")
    finally:
        consumer.close()