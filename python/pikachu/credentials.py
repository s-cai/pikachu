import gdax
import json

def auth_client_from_json(filename):
    with open(filename, 'r') as json_data_file:
        creds = json.load(json_data_file)
    return gdax.AuthenticatedClient(**creds)
