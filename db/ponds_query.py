import os

import requests

RETOOL_URL_FOR_SQL = os.getenv("RETOOL_URL_FOR_SQL")


def get_ponds():
    query = """SELECT * FROM fb4s_pond.pond_values
            ORDER BY id ASC """
    response = requests.post(RETOOL_URL_FOR_SQL, json={"query": query})
    return response.json()
