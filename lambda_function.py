import json
import os
from switchbot_sensor import SwitchBotSensor
import requests
from logging import getLogger, basicConfig, INFO

# ログの設定
logger = getLogger(__name__)
basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_data_to_thingspeak(api_key, data):
    """センサーデータをThingSpeakに送信する"""
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
        logger.info("Data sent to ThingSpeak successfully")
        logger.info(f"Temperature: {data['temperature']}°C, "
                   f"Humidity: {data['humidity']}%, "
                   f"CO2: {data['co2']}ppm")
        return True
    except Exception as e:
        logger.error(f"Failed to send data to ThingSpeak: {e}")
        return False

def lambda_handler(event, context):
    """Lambda handler function"""
    try:
        # 環境変数から設定を読み込み
        config = {
            'switchbot': {
                'token': os.environ['SWITCHBOT_TOKEN'],
                'secret': os.environ['SWITCHBOT_SECRET'],
                'device_id': os.environ['SWITCHBOT_DEVICE_ID']
            },
            'thingspeak': {
                'api_key': os.environ['THINGSPEAK_API_KEY']
            }
        }

        # SwitchBotセンサーの初期化
        sensor = SwitchBotSensor(
            token=config['switchbot']['token'],
            secret=config['switchbot']['secret'],
            device_id=config['switchbot']['device_id']
        )

        # センサーデータの取得
        data = sensor.get_data()
        if not data:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': 'Failed to get sensor data'
                })
            }

        # ThingSpeakにデータを送信
        if send_data_to_thingspeak(config['thingspeak']['api_key'], data):
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Success',
                    'data': data
                })
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': 'Failed to send data to ThingSpeak'
                })
            }

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error: {str(e)}'
            })
        }
