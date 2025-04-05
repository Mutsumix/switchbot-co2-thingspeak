import yaml
import json
import os
import boto3
import requests
from typing import Dict, Any

class SwitchBotSensor:
    """SwitchBotセンサーとの通信を管理するクラス"""

    def __init__(self, token, secret, device_id):
        """
        SwitchBotSensorクラスの初期化

        Args:
            token (str): SwitchBot APIトークン
            secret (str): SwitchBot APIシークレット
            device_id (str): デバイスID
        """
        self.token = token
        self.secret = secret
        self.device_id = device_id
        self.base_url = "https://api.switch-bot.com/v1.1"

    def _generate_sign(self):
        """認証用署名を生成"""
        import hashlib
        import hmac
        import base64
        import time
        import uuid

        nonce = str(uuid.uuid4())
        t = str(int(round(time.time() * 1000)))
        string_to_sign = f"{self.token}{t}{nonce}"

        string_to_sign = bytes(string_to_sign, 'utf-8')
        secret = bytes(self.secret, 'utf-8')

        sign = base64.b64encode(
            hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest()
        ).decode('utf-8')

        return sign, t, nonce

    def get_data(self):
        """
        センサーからデータを取得する

        Returns:
            dict or None: センサーデータを含む辞書、エラー時はNone
        """
        url = f"{self.base_url}/devices/{self.device_id}/status"
        sign, t, nonce = self._generate_sign()

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "charset": "utf8",
            "t": t,
            "sign": sign,
            "nonce": nonce
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data["statusCode"] != 100:
                print(f"API error: {data['message']}")
                return None

            body = data["body"]
            # APIレスポンスの内容をログ出力
            print(f"Raw API response: {body}")

            return {
                'temperature': body.get('temperature'),
                'humidity': body.get('humidity'),
                'co2': body.get('CO2', body.get('co2', body.get('carbonDioxide')))
            }

        except Exception as e:
            print(f"Failed to get sensor data: {e}")
            return None

def get_parameters():
    """AWS Systems Managerパラメータストアから設定を取得する"""
    try:
        # パラメータストアを使用する場合
        ssm = boto3.client('ssm')
        thingspeak_api_key = ssm.get_parameter(Name='/switchbot/thingspeak/api_key', WithDecryption=True)['Parameter']['Value']
        switchbot_token = ssm.get_parameter(Name='/switchbot/token', WithDecryption=True)['Parameter']['Value']
        switchbot_secret = ssm.get_parameter(Name='/switchbot/secret', WithDecryption=True)['Parameter']['Value']
        switchbot_device_id = ssm.get_parameter(Name='/switchbot/device_id', WithDecryption=True)['Parameter']['Value']

        return {
            'thingspeak': {
                'api_key': thingspeak_api_key
            },
            'switchbot': {
                'token': switchbot_token,
                'secret': switchbot_secret,
                'device_id': switchbot_device_id
            }
        }
    except Exception as e:
        print(f"パラメータ取得エラー: {e}")
        # 環境変数をフォールバックとして使用
        return {
            'thingspeak': {
                'api_key': os.environ.get('THINGSPEAK_API_KEY')
            },
            'switchbot': {
                'token': os.environ.get('SWITCHBOT_TOKEN'),
                'secret': os.environ.get('SWITCHBOT_SECRET'),
                'device_id': os.environ.get('SWITCHBOT_DEVICE_ID')
            }
        }

def send_data_to_thingspeak(api_key: str, data: Dict[str, Any]) -> bool:
    """センサーデータをThingSpeakに送信する

    Args:
        api_key (str): ThingSpeakのAPIキー
        data (dict): センサーから取得したデータ

    Returns:
        bool: 送信成功時はTrue、失敗時はFalse
    """
    url = f"https://api.thingspeak.com/update"
    payload = {
        "api_key": api_key,
        "field1": data['temperature'],
        "field2": data['humidity'],
        "field3": data['co2']
    }

    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()
        print(f"Data sent to ThingSpeak successfully")
        print(f"Temperature: {data['temperature']}°C, Humidity: {data['humidity']}%, CO2: {data['co2']}ppm")
        return True
    except Exception as e:
        print(f"Failed to send data to ThingSpeak: {e}")
        return False

def lambda_handler(event, context):
    """AWS Lambda用ハンドラー関数"""
    # 設定を取得
    config = get_parameters()

    # センサーオブジェクトを初期化
    sensor = SwitchBotSensor(
        token=config['switchbot']['token'],
        secret=config['switchbot']['secret'],
        device_id=config['switchbot']['device_id']
    )

    try:
        # センサーデータを取得
        data = sensor.get_data()

        if data:
            # ThingSpeakにデータを送信
            success = send_data_to_thingspeak(
                config['thingspeak']['api_key'],
                data
            )

            return {
                'statusCode': 200 if success else 500,
                'body': json.dumps({
                    'success': success,
                    'data': data
                })
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'success': False,
                    'error': 'Failed to get sensor data'
                })
            }
    except Exception as e:
        print(f"実行エラー: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }
