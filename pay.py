import requests
from hashlib import sha384
import time
import json
import hmac

class Wrapper:
    def __init__(self,
        public_key: str = None,
        private_key: str = None):
        self.public_key = public_key
        self.private_key = private_key
        self.DEFAULT_HEADERS = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    def _request(self, uri: str, path: str, body: dict):
        round(time.time() * 1000)
        nonce = round(time.time() * 1000)
        str_nonce = str(nonce)
        print(str_nonce, nonce)
        body = json.dumps(body)
        headers = self.DEFAULT_HEADERS.copy()
        headers["kun-nonce"] = str_nonce
        headers["kun-apikey"] = self.public_key
        headers["kun-signature"] = self._sign(
            path, str_nonce, body
        )
        response = requests.put(uri, data=body, headers=headers)
        json_response = response.json()
        return json_response

    def load(self, code):
        body = {"code": code}
        return self._request("https://api.kuna.io:443/v3/auth/kuna_codes/redeem", "/v3/auth/kuna_codes/redeem", body)
    def _sign(self, path: str, nonce: str, body: str) -> str:
        payload = "{}{}{}".format(path, nonce, body)
        print(nonce)
        payload_bin = payload.encode("ascii")
        private_key_bin = self.private_key.encode("ascii")
        sign = hmac.new(private_key_bin, payload_bin, sha384)
        return sign.hexdigest()

