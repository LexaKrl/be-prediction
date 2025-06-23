import psycopg2
import pandas as pd
from config import Config


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )

    def get_user_finances(self, user_id: int):
        """Получить финансовые данные пользователя"""
        query = """
        SELECT 
            date, 
            amount,
            type,
            category
        FROM finance 
        WHERE owner_id = %s
        ORDER BY date DESC
        LIMIT 100
        """
        return pd.read_sql(query, self.conn, params=(user_id,))

    def save_prediction(self, owner_id: int, prediction: float):
        """Сохранить прогноз в таблицу owner"""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                UPDATE owner
                SET 
                    prediction = %s,
                    prediction_calculated_at = NOW()
                WHERE owner_id = %s
            """, (float(prediction), owner_id))
        self.conn.commit()

    def close(self):
        self.conn.close()