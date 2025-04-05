import json
import os
import time
from switchbot_sensor import SwitchBotSensor
import requests
import logging
import traceback

# ログの設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 環境変数の確認
logger.debug(f"SWITCHBOT_TOKEN: {os.environ.get('SWITCHBOT_TOKEN', 'Not set')}")
logger.debug(f"SWITCHBOT_SECRET: {os.environ.get('SWITCHBOT_SECRET', 'Not set')}")
logger.debug(f"SWITCHBOT_DEVICE_ID: {os.environ.get('SWITCHBOT_DEVICE_ID', 'Not set')}")
logger.debug(f"MACKEREL_API_KEY: {os.environ.get('MACKEREL_API_KEY', 'Not set')}")
logger.debug(f"MACKEREL_SERVICE_NAME: {os.environ.get('MACKEREL_SERVICE_NAME', 'Not set')}")

def send_data_to_mackerel(api_key, service_name, data):
    """センサーデータをMackerelに送信する"""
    try:
        url = f"https://api.mackerelio.com/api/v0/services/{service_name}/tsdb"
        logger.debug(f"Mackerel APIエンドポイント: {url}")

        current_time = int(time.time())
        metrics = [
            {
                "name": "switchbot.temperature",
                "time": current_time,
                "value": data['temperature']
            },
            {
                "name": "switchbot.humidity",
                "time": current_time,
                "value": data['humidity']
            },
            {
                "name": "switchbot.co2",
                "time": current_time,
                "value": data['co2']
            }
        ]
        logger.debug(f"送信するメトリクス: {metrics}")

        headers = {
            "X-Api-Key": api_key,
            "Content-Type": "application/json"
        }
        logger.debug(f"リクエストヘッダー: {headers}")

        try:
            response = requests.post(url, headers=headers, json=metrics)
            response.raise_for_status()
            logger.debug(f"Mackerelレスポンス: {response.text}")
            logger.info("Data sent to Mackerel successfully")
            logger.info(f"Temperature: {data['temperature']}°C, "
                       f"Humidity: {data['humidity']}%, "
                       f"CO2: {data['co2']}ppm")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Mackerel APIリクエストエラー: {str(e)}")
            logger.error(f"レスポンス: {e.response.text if e.response else 'No response'}")
            logger.error(traceback.format_exc())
            return False

    except Exception as e:
        logger.error(f"Mackerelへのデータ送信に失敗: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def lambda_handler(event, context):
    """Lambda handler function"""
    try:
        logger.debug("Lambda handler開始")

        # 環境変数から設定を読み込み
        config = {
            'switchbot': {
                'token': os.environ['SWITCHBOT_TOKEN'],
                'secret': os.environ['SWITCHBOT_SECRET'],
                'device_id': os.environ['SWITCHBOT_DEVICE_ID']
            },
            'mackerel': {
                'api_key': os.environ['MACKEREL_API_KEY'],
                'service_name': os.environ['MACKEREL_SERVICE_NAME']
            }
        }
        logger.debug(f"設定: {config}")

        # SwitchBotセンサーの初期化
        logger.debug("SwitchBotセンサーの初期化")
        sensor = SwitchBotSensor(
            token=config['switchbot']['token'],
            secret=config['switchbot']['secret'],
            device_id=config['switchbot']['device_id']
        )

        # センサーデータの取得
        logger.debug("センサーデータの取得開始")
        data = sensor.get_data()
        if not data:
            logger.error("センサーデータの取得に失敗")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': 'Failed to get sensor data'
                })
            }

        logger.debug(f"取得したセンサーデータ: {data}")

        # Mackerelにデータを送信
        logger.debug("Mackerelへのデータ送信開始")
        if send_data_to_mackerel(
            config['mackerel']['api_key'],
            config['mackerel']['service_name'],
            data
        ):
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
                    'message': 'Failed to send data to Mackerel'
                })
            }

    except Exception as e:
        logger.error(f"Lambda handler実行エラー: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error: {str(e)}'
            })
        }

if __name__ == "__main__":
    logger.debug("メイン処理開始")
    result = lambda_handler({}, None)
    logger.debug(f"Lambda実行結果: {result}")
