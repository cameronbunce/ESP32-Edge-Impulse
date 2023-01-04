import network, hmac, 
import urequests as requests


class EI_Ingest:
    def __init__(self, hmac_key, api_key):
        self.hmac = hmac_key
        self.api = api_key

    