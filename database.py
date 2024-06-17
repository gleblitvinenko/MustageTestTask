import datetime

import aiosqlite


class Database:

    def __init__(self, db_path):
        self.db_path = db_path

    async def __connect(self):
        self.conn: aiosqlite.Connection = await aiosqlite.connect(self.db_path)

    async def create_tables(self) -> None:

        await self.__connect()

        await self.conn.execute("""
        CREATE TABLE IF NOT EXISTS requests(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requests_datetime DATETIME NOT NULL,
            vacancies_count INTEGER NOT NULL
        )
        """)

    async def insert_vacancies_count(self, vacancies_count: int) -> None:
        await self.__connect()

        await self.conn.execute(f"""
        INSERT INTO requests (vacancies_count, requests_datetime) VALUES (?, ?)
        """, (vacancies_count, datetime.datetime.now()))

        await self.conn.commit()

    async def get_today_requests(self) -> list:
        await self.__connect()

        cursor = await self.conn.execute(f"""
        SELECT strftime('%Y.%m.%d %H:%M', requests_datetime) as formatted_datetime, vacancies_count
        FROM requests
        WHERE DATE(requests_datetime) = ?
        """, (str(datetime.date.today()),))

        rows = await cursor.fetchall()

        return list(rows)


def get_db() -> Database:
    return Database("db.db")

