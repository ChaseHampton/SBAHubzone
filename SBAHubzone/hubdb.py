import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from .models.batch import Batch

load_dotenv()


class HubDB:
    def __init__(self) -> None:
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_DB"),
            cursor_factory=RealDictCursor
        )

    def get_one_search(self):
        stmt = "SELECT search_id, cert_type, body FROM searches WHERE is_searched = false ORDER BY search_id ASC LIMIT 1"
        with self.conn.cursor() as curs:
            curs.execute(stmt)
            yield curs.fetchone()

    def get_all_searches(self):
        stmt = "SELECT search_id, cert_type, body FROM searches WHERE is_searched = false ORDER BY search_id ASC"
        with self.conn.cursor() as curs:
            curs.execute(stmt)
            return curs.fetchall()

    def update_search_is_searched(self, search:dict):
        stmt = "CALL update_search_is_searched(%s)"
        with self.conn.cursor() as curs:
            curs.execute(stmt, (search['search_id'],))

    def reset_search_is_searched(self):
        stmt = "CALL reset_search_is_searched()"
        with self.conn.cursor() as curs:
            curs.execute(stmt)

    def insert_businesses(self, business: list):
        stmt = """INSERT INTO public.businesses (bus_name, url, uei) VALUES(%s, %s, %s);"""
        with self.conn:
            with self.conn.cursor() as curs:
                curs.executemany(stmt, business)

    def reset_businesses(self):
        stmt = "TRUNCATE businesses"
        with self.conn:
            with self.conn.cursor() as curs:
                curs.execute(stmt)

    def get_batch_of_businesses(self, limit=1000, offset=0) -> Batch:
        batch = Batch(limit=limit, offset=offset)
        stmt = """select bus_name, url, uei from businesses b limit %s offset %s"""
        with self.conn.cursor() as curs:
            curs.execute(stmt, (limit, offset))
            batch.recs = curs.fetchall()
        return batch
