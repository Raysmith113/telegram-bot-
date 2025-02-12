import requests
from requests.structures import CaseInsensitiveDict
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID

RPC_ENDPOINT = "https://api.mainnet-beta.solana.com"
SOLANA_EXPLORER_ENDPOINT = "https://explorer-api.mainnet-beta.solana.com/"


def is_token_account(address):
    client = Client(RPC_ENDPOINT)

    response = client.get_account_info(Pubkey.from_string(address))

    account_info = response.value

    if account_info is None:
        return False

    if account_info.owner == TOKEN_PROGRAM_ID:
        return True
    else:
        return False


def get_symbol(address):
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    headers["content-type"] = "application/json"

    print(address)

    payload = {
        "id": address,
        "jsonrpc": "2.0",
        "method": "getAsset",
        "params": {
            "id": address,
        },
    }

    resp = requests.post(RPC_ENDPOINT, headers=headers, json=payload)

    print(resp.status_code)

    if resp.status_code != 200 or 'error' in resp.json():
        return None

    print(resp.text)

    data = resp.json()

    print(data['result']['content']['metadata']['symbol'])

    return data['result']['content']['metadata']['symbol']
