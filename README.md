# SwitchBot CO2 Monitor (Lambda 版)

SwitchBot の CO2 センサーからデータを取得し、ThingSpeak に送信する AWS Lambda 関数。

## 前提条件

- AWS アカウント
- SwitchBot アカウントと API 認証情報
- ThingSpeak アカウントと Write API Key
- Python 3.9 以上

## プロジェクト構成

```
.
├── lambda_function.py     # Lambda用のメイン関数
├── switchbot_sensor.py    # SwitchBotセンサークラス
├── requirements.txt       # 依存パッケージ一覧
├── config.yml.example     # 設定ファイルのテンプレート
└── tools/                # ユーティリティツール
    └── list_devices.py   # デバイスID取得ツール
```

## セットアップ手順

1. リポジトリのクローン

```bash
git clone https://github.com/yourusername/switchbot-co2-monitor.git
cd switchbot-co2-monitor
```

2. 必要なパッケージのインストール

```bash
pip install -r requirements.txt
```

3. デバイス ID の取得

```bash
# 設定ファイルの準備
cp config.yml.example config.yml

# config.ymlを編集し、SwitchBotのtokenとsecretを設定
# device_idは空のままでOK

# デバイス一覧の取得
python tools/list_devices.py

# 出力された一覧からCO2センサーのdevice_idをconfig.ymlに設定
```

4. デプロイパッケージの作成

```bash
# 一時的なビルドディレクトリの作成
mkdir build
cd build

# 必要なファイルのコピー
cp ../lambda_function.py .
cp ../switchbot_sensor.py .
cp ../requirements.txt .

# 依存パッケージのインストール
pip install --target . -r requirements.txt

# ZIPファイルの作成
zip -r ../deployment.zip .

# 一時ディレクトリの削除
cd ..
rm -rf build
```

5. AWS 環境のセットアップ

   1. IAM ロールの作成

      - ロール名：`switchbot-co2-monitor-role`
      - ユースケース：`Lambda`
      - ポリシー：`AWSLambdaBasicExecutionRole`

   2. Lambda 関数の作成

      - 関数名：`switchbot-co2-monitor`
      - ランタイム：`Python 3.9`
      - 作成した IAM ロールを選択

   3. 環境変数の設定

      - Lambda 関数の「設定」タブから「環境変数」を選択
      - config.yml の内容を基に以下の環境変数を設定：
        - `SWITCHBOT_TOKEN`：SwitchBot の API トークン
        - `SWITCHBOT_SECRET`：SwitchBot の API シークレット
        - `SWITCHBOT_DEVICE_ID`：CO2 センサーのデバイス ID
        - `THINGSPEAK_API_KEY`：ThingSpeak の Write API Key

   4. デプロイパッケージのアップロード

      - 作成した`deployment.zip`をアップロード

   5. 基本設定の調整

      - メモリ：128 MB
      - タイムアウト：30 秒

   6. EventBridge ルールの作成
      - ルール名：`switchbot-co2-monitor-schedule`
      - スケジュール：`rate(1 hour)`
      - ターゲット：作成した Lambda 関数

6. 動作確認
   - Lambda 関数のテスト実行
   - CloudWatch ログの確認
   - ThingSpeak でのデータ受信確認

## ThingSpeak フィールドの設定

- Field 1: Temperature（温度）
- Field 2: Humidity（湿度）
- Field 3: CO2（CO2 濃度）

## トラブルシューティング

- CloudWatch ログでエラーを確認
- 環境変数が正しく設定されているか確認
- API 認証情報が有効か確認
- デプロイパッケージの作成に失敗する場合：
  - Python 環境が 3.9 以上であることを確認
  - 必要なパッケージがインストールできているか確認
  - 一時ディレクトリのパーミッションを確認

## ライセンス

MIT
