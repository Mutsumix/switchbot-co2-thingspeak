# SwitchBot CO2 Monitor to Mackerel

SwitchBot CO2 モニターのデータを Mackerel に送信する AWS Lambda 関数です。

## 必要条件

- Python 3.9 以上
- AWS アカウント
- SwitchBot CO2 モニター
- SwitchBot API トークンとシークレット
- Mackerel アカウント

## プロジェクト構成

```
.
├── lambda_function.py     # Lambda用のメイン関数
├── switchbot_sensor.py    # SwitchBotセンサークラス
├── requirements.txt       # 依存パッケージ一覧
├── env.example           # 環境変数のテンプレート
└── tools/                # ユーティリティツール
    └── list_devices.py   # デバイスID取得ツール
```

## セットアップ手順

1. SwitchBot API の設定

   - SwitchBot アプリでデベロッパーオプションを開く
   - トークンとシークレットを取得
   - デバイス一覧を取得して CO2 モニターのデバイス ID を確認

     ```bash
     # 設定ファイルの準備
     cp env.example .env
     # .envを編集し、SwitchBotのtokenとsecretを設定

     # デバイス一覧の取得
     python tools/list_devices.py
     ```

2. Mackerel の設定

   - Mackerel にサインアップ
   - API キーを発行（Write 権限が必要）
   - サービスを作成（例：`SwitchBotSensor`）

3. デプロイパッケージの作成

   ```bash
   # 依存パッケージのインストールとZIP作成
   pip install requests==2.26.0 --target ./package
   cd package
   zip -r ../lambda.zip .
   cd ..
   zip -g lambda.zip lambda_function.py switchbot_sensor.py
   ```

4. AWS Lambda の設定

   1. Lambda 関数の作成

      - 関数名：`switchbot-co2-monitor`
      - ランタイム：`Python 3.9`
      - 基本的な Lambda 実行ロールを選択

   2. 環境変数の設定

      ```
      SWITCHBOT_TOKEN=your_token
      SWITCHBOT_SECRET=your_secret
      SWITCHBOT_DEVICE_ID=your_device_id
      MACKEREL_API_KEY=your_api_key
      MACKEREL_SERVICE_NAME=SwitchBotSensor
      ```

   3. 基本設定の調整

      - メモリ：128 MB
      - タイムアウト：30 秒

   4. EventBridge ルールの設定
      - 既存のルールを使用
      - スケジュール：`rate(1 hour)`

## メトリクス

Mackerel には以下のメトリクスが送信されます：

- `switchbot.temperature`: 温度（℃）
- `switchbot.humidity`: 湿度（%）
- `switchbot.co2`: CO2 濃度（ppm）

## ダッシュボードの設定

1. グラフの作成

   - 温度グラフ: `switchbot.temperature`（0-40 の範囲を推奨）
   - 湿度グラフ: `switchbot.humidity`（0-100 の範囲を推奨）
   - CO2 濃度グラフ: `switchbot.co2`（0-2000 の範囲を推奨）

2. アラート設定（推奨値）
   - CO2 濃度: 1000 ppm 以上で Warning、1500 ppm 以上で Critical
   - 温度: 28°C 以上で Warning、32°C 以上で Critical
   - 湿度: 70%以上で Warning、80%以上で Critical

## トラブルシューティング

- CloudWatch ログでエラーを確認
- 環境変数が正しく設定されているか確認
- API 認証情報が有効か確認
- デプロイパッケージの作成に失敗する場合：
  - Python 環境が 3.9 以上であることを確認
  - 必要なパッケージがインストールできているか確認

## ライセンス

MIT
