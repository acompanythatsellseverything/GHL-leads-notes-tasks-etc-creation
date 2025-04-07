import requests

RETOOL_URL_FOR_SQL = "https://api.retool.com/v1/workflows/d378f48d-2398-4488-9f3a-498b6fc2b576/startTrigger?workflowApiKey=retool_wk_05c76ca96e98468f9657b32fbe3f737c"


def get_ponds():
    query = """SELECT * FROM fb4s_pond.pond_values
            ORDER BY id ASC """
    response = requests.post(RETOOL_URL_FOR_SQL, json={"query": query})
    return response.json()
