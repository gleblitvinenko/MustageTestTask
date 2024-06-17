import asyncio
import uuid

import openpyxl

from database import get_db

db = get_db()


async def add_change_filed(requests_list: list[tuple]) -> list[list]:
    temp_list = list(requests_list[0]) + [0]
    requests_list_with_change = [temp_list]

    for request in requests_list[1:]:
        temp_list = list(request) + [request[1] - temp_list[1]]
        requests_list_with_change.append(temp_list)

    return requests_list_with_change


async def write_data_to_excel(requests_list: list[tuple]) -> str:
    requests_list = await add_change_filed(requests_list)
    wb = openpyxl.Workbook()
    ws = wb.active
    header = ["datetime", "vacancy_count", "change"]
    ws.append(header)
    for request in requests_list:
        ws.append(request)

    unique_id = str(uuid.uuid4())
    file_name = f"vacancies_{unique_id}.xlsx"
    wb.save(file_name)

    return file_name
