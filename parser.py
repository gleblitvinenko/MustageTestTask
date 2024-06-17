import aiohttp
import asyncio
import json
import time

import database

db = database.get_db()

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'uk',
    'apollographql-client-name': 'web-alliance-desktop',
    'apollographql-client-version': '9a41718',
    'cid': '1631184089.1718612403',
    'content-type': 'application/json',
    'origin': 'https://robota.ua',
    'priority': 'u=1, i',
    'referer': 'https://robota.ua/',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
}

params = {
    'q': 'getPublishedVacanciesList',
}

json_data = {
    'operationName': 'getPublishedVacanciesList',
    'variables': {
        'pagination': {
            'count': 0,
            'page': 0,
        },
        'filter': {
            'keywords': 'junior',
            'clusterKeywords': [],
            'salary': 0,
            'districtIds': [],
            'scheduleIds': [],
            'rubrics': [],
            'metroBranches': [],
            'showAgencies': True,
            'showOnlyNoCvApplyVacancies': False,
            'showOnlySpecialNeeds': False,
            'showOnlyWithoutExperience': False,
            'showOnlyNotViewed': False,
            'showWithoutSalary': True,
            'showMilitary': True,
        },
        'sort': 'BY_VIEWED',
        'isBrowser': True,
    },
    'query': 'query getPublishedVacanciesList($filter: PublishedVacanciesFilterInput!, $pagination: PublishedVacanciesPaginationInput!, $sort: PublishedVacanciesSortType!, $isBrowser: Boolean!) {\n  publishedVacancies(filter: $filter, pagination: $pagination, sort: $sort) {\n    totalCount\n    items {\n      ...PublishedVacanciesItem\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment PublishedVacanciesItem on Vacancy {\n  id\n  schedules {\n    id\n    __typename\n  }\n  title\n  description\n  sortDateText\n  hot\n  designBannerUrl\n  isPublicationInAllCities\n  badges {\n    name\n    __typename\n  }\n  salary {\n    amount\n    comment\n    amountFrom\n    amountTo\n    __typename\n  }\n  company {\n    id\n    logoUrl\n    name\n    honors {\n      badge {\n        iconUrl\n        tooltipDescription\n        locations\n        isFavorite\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  city {\n    id\n    name\n    __typename\n  }\n  showProfile\n  seekerFavorite @include(if: $isBrowser) {\n    isFavorite\n    __typename\n  }\n  seekerDisliked @include(if: $isBrowser) {\n    isDisliked\n    __typename\n  }\n  formApplyCustomUrl\n  anonymous\n  isActive\n  publicationType\n  __typename\n}\n',
}


async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.post('https://dracula.robota.ua/', params=params, headers=headers, json=json_data) as response:
            response.raise_for_status()  # Бросить исключение для ошибок HTTP
            return await response.json()


async def get_vacancies_count() -> int:
    try:
        data = await fetch_data()
        vacancies_count = data["data"]["publishedVacancies"]["totalCount"]
        return vacancies_count
    except aiohttp.ClientResponseError as e:
        print(f"HTTP error occurred: {e}")
    except aiohttp.ClientError as e:
        print(f"Client error occurred: {e}")
    except asyncio.TimeoutError:
        print("Request timed out")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")


async def write_request_to_db() -> None:
    vacancies_count = await get_vacancies_count()
    await db.insert_vacancies_count(vacancies_count)


async def periodic_task(interval):
    while True:
        start_time = asyncio.get_event_loop().time()
        await write_request_to_db()
        elapsed_time = asyncio.get_event_loop().time() - start_time
        sleep_time = max(0, interval - elapsed_time)
        await asyncio.sleep(sleep_time)
