# SwitchBot CO2 Monitor

SwitchBot の CO2 センサーからデータを取得し、ThingSpeak に送信する Python スクリプト。

## 必要条件

- Python 3.7 以上
- SwitchBot アカウントと API 認証情報
- ThingSpeak アカウントと Write API Key
- SwitchBot CO2 センサー

## セットアップ

1. リポジトリをクローン

```bash
git clone https://github.com/yourusername/switchbot-co2-monitor.git
cd switchbot-co2-monitor
```

2. 必要なパッケージをインストール

```bash
pip install -r requirements.txt
```

3. 設定ファイルを作成

```bash
cp config.yml.example config.yml
```

4. config.yml を編集し、以下の認証情報を設定
   - ThingSpeak Write API Key
   - SwitchBot Token
   - SwitchBot Secret
   - SwitchBot Device ID

## 使用方法

```bash
python main.py
```

スクリプトは設定された間隔（デフォルト 15 分）でセンサーからデータを取得し、ThingSpeak に送信します。

## ツール

### デバイス一覧の取得

SwitchBot デバイスの一覧と ID を取得するには：

python tools/list_devices.py

## ThingSpeak フィールドの設定

- Field 1: Temperature（温度）
- Field 2: Humidity（湿度）
- Field 3: CO2（CO2 濃度）

## ライセンス

MIT
