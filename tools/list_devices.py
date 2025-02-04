import requests
import time
import hashlib
import hmac
import base64
import uuid
import json
import yaml

def load_config():
    """設定ファイル（config.yml）を読み込む"""
    with open('config.yml', 'r') as file:
        return yaml.safe_load(file)

def generate_sign(token: str, secret: str):
    nonce = str(uuid.uuid4())
    t = str(int(round(time.time() * 1000)))
    string_to_sign = f"{token}{t}{nonce}"

    string_to_sign = bytes(string_to_sign, 'utf-8')
    secret = bytes(secret, 'utf-8')

    sign = base64.b64encode(
        hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest()
    ).decode('utf-8')

    return sign, t, nonce

def get_device_list():
    config = load_config()
    token = config['sensor']['switchbot']['token']
    secret = config['sensor']['switchbot']['secret']

    sign, t, nonce = generate_sign(token, secret)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "charset": "utf8",
        "t": t,
        "sign": sign,
        "nonce": nonce
    }

    response = requests.get(
        "https://api.switch-bot.com/v1.1/devices",
        headers=headers
    )

    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    get_device_list()
