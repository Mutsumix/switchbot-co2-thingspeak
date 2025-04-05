# SwitchBot CO2 Monitor (Lambda 版)

SwitchBot の CO2 センサーからデータを取得し、ThingSpeak に送信する AWS Lambda 関数。

## 前提条件

- AWS アカウント
- SwitchBot アカウントと API 認証情報
- ThingSpeak アカウントと Write API Key
- Python 3.9 以上（デプロイパッケージ作成用）

## セットアップ手順

1. リポジトリのクローン

```bash
git clone https://github.com/yourusername/switchbot-co2-monitor.git
cd switchbot-co2-monitor
```

2. 環境変数の準備

- `env.example`を参考に、必要な認証情報を控えておく
  - SwitchBot Token
  - SwitchBot Secret
  - SwitchBot Device ID
  - ThingSpeak API Key

3. デプロイパッケージの作成

```bash
# デプロイパッケージ用ディレクトリの作成
mkdir switchbot-lambda
cd switchbot-lambda

# 必要なファイルのコピー
cp ../lambda_function.py .
cp ../switchbot_sensor.py .
cp ../requirements.txt .

# 依存パッケージのインストール
pip install --target . -r requirements.txt

# ZIPファイルの作成
zip -r ../switchbot-lambda.zip .
```

4. AWS 環境のセットアップ

   1. IAM ロールの作成

      - ロール名：`switchbot-co2-monitor-role`
      - ユースケース：`Lambda`
      - ポリシー：`AWSLambdaBasicExecutionRole`

   2. Lambda 関数の作成

      - 関数名：`switchbot-co2-monitor`
      - ランタイム：`Python 3.9`
      - 作成した IAM ロールを選択

   3. 環境変数の設定

      - `SWITCHBOT_TOKEN`
      - `SWITCHBOT_SECRET`
      - `SWITCHBOT_DEVICE_ID`
      - `THINGSPEAK_API_KEY`

   4. デプロイパッケージのアップロード

      - 作成した`switchbot-lambda.zip`をアップロード

   5. 基本設定の調整

      - メモリ：128 MB
      - タイムアウト：30 秒

   6. EventBridge ルールの作成
      - ルール名：`switchbot-co2-monitor-schedule`
      - スケジュール：`rate(1 hour)`
      - ターゲット：作成した Lambda 関数

5. 動作確認
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

## ライセンス

MIT
