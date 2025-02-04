import requests
import hashlib
import hmac
import base64
import time
import uuid
from typing import Optional, Dict
from logging import getLogger

logger = getLogger(__name__)

class SwitchBotSensor:
    """SwitchBotセンサーとの通信を管理するクラス"""

    def __init__(self, token: str, secret: str, device_id: str):
        """
        SwitchBotSensorクラスの初期化

        Args:
            token (str): SwitchBot APIトークン
            secret (str): SwitchBot APIシークレット
            device_id (str): デバイスID
        """
        self.token = token  # Bearerプレフィックスは後で付ける
        self.secret = secret
        self.device_id = device_id
        self.base_url = "https://api.switch-bot.com/v1.1"

    def _generate_sign(self) -> tuple[str, str, str]:
        """認証用署名を生成"""
        nonce = str(uuid.uuid4())
        t = str(int(round(time.time() * 1000)))
        string_to_sign = f"{self.token}{t}{nonce}"

        string_to_sign = bytes(string_to_sign, 'utf-8')
        secret = bytes(self.secret, 'utf-8')

        sign = base64.b64encode(
            hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest()
        ).decode('utf-8')

        return sign, t, nonce

    def get_data(self) -> Optional[Dict]:
        """
        センサーからデータを取得する

        Returns:
            Optional[Dict]: センサーデータを含む辞書、エラー時はNone
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
                logger.error(f"API error: {data['message']}")
                return None

            body = data["body"]
            # APIレスポンスの内容をログ出力
            logger.info(f"Raw API response: {body}")

            return {
                'temperature': body.get('temperature'),
                'humidity': body.get('humidity'),
                'co2': body.get('CO2', body.get('co2', body.get('carbonDioxide')))  # 大文字のCO2キーを最優先で確認
            }

        except Exception as e:
            logger.error(f"Failed to get sensor data: {e}")
            return None

    def cleanup(self) -> None:
        """クリーンアップ処理（この場合は不要だが、インターフェースの一貫性のため実装）"""
        pass
