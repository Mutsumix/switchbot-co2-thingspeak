import requests
import hashlib
import hmac
import base64
import time
import uuid
import json
from typing import Optional, Dict, Any, Tuple
import logging
import traceback

logger = logging.getLogger(__name__)

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
        """署名を生成する"""
        try:
            t = str(int(round(time.time() * 1000)))
            nonce = base64.b64encode(bytes(str(time.time()), 'utf-8')).decode()
            sign_str = f"{self.token}{t}{nonce}"

            logger.debug(f"署名文字列: {sign_str}")

            sign_hmac = hmac.new(bytes(self.secret, 'utf-8'),
                               bytes(sign_str, 'utf-8'),
                               hashlib.sha256)
            sign = base64.b64encode(sign_hmac.digest()).decode('utf-8')

            logger.debug(f"生成された署名: {sign}")
            return sign, t, nonce
        except Exception as e:
            logger.error(f"署名の生成に失敗: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def get_data(self):
        """センサーデータを取得する"""
        try:
            logger.debug("センサーデータの取得を開始")

            # 認証用のヘッダーを生成
            sign, t, nonce = self._generate_sign()
            headers = {
                "Authorization": f"Bearer {self.token}",
                "sign": sign,
                "nonce": nonce,
                "t": t,
                "Content-Type": "application/json"
            }

            logger.debug(f"認証ヘッダー生成完了: {headers}")

            # デバイスのステータスを取得
            url = f"{self.base_url}/devices/{self.device_id}/status"
            logger.debug(f"APIリクエスト送信: {url}")

            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                logger.debug(f"APIレスポンスステータス: {response.status_code}")
                logger.debug(f"APIレスポンスヘッダー: {response.headers}")
                logger.debug(f"APIレスポンス本文: {response.text}")

                data = response.json()
                logger.debug(f"APIレスポンスJSON: {data}")

                if data.get("statusCode") != 100:
                    logger.error(f"APIエラー: {data}")
                    return None

                # 必要なデータを抽出
                result = {
                    "temperature": data["body"]["temperature"],
                    "humidity": data["body"]["humidity"],
                    "co2": data["body"]["CO2"]
                }

                logger.debug(f"取得したセンサーデータ: {result}")
                return result

            except requests.exceptions.RequestException as e:
                logger.error(f"APIリクエストエラー: {str(e)}")
                logger.error(f"レスポンス: {e.response.text if e.response else 'No response'}")
                logger.error(traceback.format_exc())
                return None

        except Exception as e:
            logger.error(f"センサーデータの取得に失敗: {str(e)}")
            logger.error(traceback.format_exc())
            return None

    def cleanup(self):
        """クリーンアップ処理（この場合は不要だが、インターフェースの一貫性のため実装）"""
        pass
