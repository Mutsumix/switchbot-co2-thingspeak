import yaml
import time
import schedule
import requests
from switchbot_sensor import SwitchBotSensor
from logging import getLogger, basicConfig, INFO

# ログの設定
logger = getLogger(__name__)
basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    """設定ファイル（config.yml）を読み込む"""
    with open('config.yml', 'r') as file:
        return yaml.safe_load(file)

def send_data_to_thingspeak(api_key, data):
    """センサーデータをThingSpeakに送信する

    Args:
        api_key (str): ThingSpeakのAPIキー
        data (dict): センサーから取得したデータ
    """
    url = f"https://api.thingspeak.com/update?api_key={api_key}"
    payload = {
        "field1": data['temperature'],
        "field2": data['humidity'],
        "field3": data['co2']
    }

    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()
        logger.info("Data sent to ThingSpeak successfully")
        logger.info(f"Temperature: {data['temperature']}°C, Humidity: {data['humidity']}%, CO2: {data['co2']}ppm")
    except Exception as e:
        logger.error(f"Failed to send data to ThingSpeak: {e}")

def monitor_and_send():
    """センサーデータを取得し、ThingSpeakに送信する"""
    config = load_config()
    sensor = SwitchBotSensor(
        token=config['sensor']['switchbot']['token'],
        secret=config['sensor']['switchbot']['secret'],
        device_id=config['sensor']['switchbot']['device_id']
    )

    try:
        data = sensor.get_data()
        if data:
            send_data_to_thingspeak(
                config['thingspeak']['api_key'],
                data
            )
        else:
            logger.error("Failed to get sensor data")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        sensor.cleanup()

def main():
    """メイン関数: スケジューラーを設定し、定期的にデータを送信する"""
    config = load_config()

    # 起動直後に1回実行
    logger.info("Initial data collection started...")
    monitor_and_send()

    # その後、定期実行をスケジュール
    schedule.every(config['sensor']['scheduler']['interval_minutes']).minutes.do(monitor_and_send)

    logger.info("Scheduled monitoring started. Press Ctrl+C to exit.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user.")

if __name__ == "__main__":
    main()



