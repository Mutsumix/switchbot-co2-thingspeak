# SwitchBot CO2 センサー データ収集サーバーレス実装

このプロジェクトは、SwitchBot CO2 センサーからデータを取得し、ThingSpeak に送信する仕組みを AWS Lambda を使ったサーバーレス環境に移行するためのものです。

## 構成

- **lambda_function.py**: Lambda 関数のメインコード
- **cloudformation.yml**: AWS リソースをプロビジョニングするための CloudFormation テンプレート

## セットアップ手順

### 前提条件

- AWS アカウント
- AWS CLI（インストール済み、設定済み）
- SwitchBot API の認証情報（Token, Secret, Device ID）
- ThingSpeak Write API Key

### デプロイ手順

1. AWS CLI が設定されていることを確認します

```bash
aws configure list
```

2. Lambda 関数のデプロイパッケージを作成します

```bash
# プロジェクトディレクトリに移動
cd /path/to/switchbot-co2-thingspeak

# デプロイ用のディレクトリを作成
mkdir -p deployment

# 必要なライブラリをインストール
pip install -t deployment/ requests

# Lambda関数コードをコピー
cp lambda_function.py deployment/

# デプロイパッケージを作成
cd deployment
zip -r ../deployment.zip .
cd ..
```

3. CloudFormation スタックをデプロイします

```bash
aws cloudformation create-stack \
  --stack-name switchbot-co2-thingspeak \
  --template-body file://cloudformation.yml \
  --capabilities CAPABILITY_IAM \
  --parameters \
  ParameterKey=ThingSpeakApiKey,ParameterValue=YOUR_THINGSPEAK_API_KEY \
  ParameterKey=SwitchBotToken,ParameterValue=YOUR_SWITCHBOT_TOKEN \
  ParameterKey=SwitchBotSecret,ParameterValue=YOUR_SWITCHBOT_SECRET \
  ParameterKey=SwitchBotDeviceId,ParameterValue=YOUR_SWITCHBOT_DEVICE_ID \
  ParameterKey=ScheduleExpression,ParameterValue="rate(1 hour)"
```

`YOUR_THINGSPEAK_API_KEY`, `YOUR_SWITCHBOT_TOKEN`, `YOUR_SWITCHBOT_SECRET`, `YOUR_SWITCHBOT_DEVICE_ID`を実際の値に置き換えてください。また、`ScheduleExpression`は必要に応じて調整できます。

4. Lambda 関数コードをアップロードします（CloudFormation スタック作成後）

```bash
# CloudFormationスタックのステータスを確認
aws cloudformation describe-stacks --stack-name switchbot-co2-thingspeak --query "Stacks[0].StackStatus"

# ステータスが"CREATE_COMPLETE"になったら、Lambda関数コードをアップロード
aws lambda update-function-code \
  --function-name switchbot-co2-thingspeak \
  --zip-file fileb://deployment.zip
```

## スケジュールの変更方法

CloudWatch Events のルールを更新して、データ収集の頻度を変更できます。

例えば、30 分ごとに実行するには：

```bash
aws events put-rule \
  --name SwitchBotCO2DataCollectionSchedule \
  --schedule-expression "rate(30 minutes)"
```

または、特定の時間に実行する cron 式を使用することもできます：

```bash
# 毎時0分に実行
aws events put-rule \
  --name SwitchBotCO2DataCollectionSchedule \
  --schedule-expression "cron(0 * * * ? *)"
```

## 手動実行

Lambda 関数を手動で実行してテストするには：

```bash
aws lambda invoke \
  --function-name switchbot-co2-thingspeak \
  --payload '{}' \
  response.json

cat response.json
```

## モニタリングとログ確認

CloudWatch Logs で関数の実行ログを確認できます：

```bash
# 最新のログストリームを取得
LOG_STREAM=$(aws logs describe-log-streams \
  --log-group-name "/aws/lambda/switchbot-co2-thingspeak" \
  --order-by LastEventTime \
  --descending \
  --limit 1 \
  --query "logStreams[0].logStreamName" \
  --output text)

# ログイベントを表示
aws logs get-log-events \
  --log-group-name "/aws/lambda/switchbot-co2-thingspeak" \
  --log-stream-name "$LOG_STREAM"
```

## クリーンアップ

不要になった場合は、リソースを削除します：

```bash
aws cloudformation delete-stack --stack-name switchbot-co2-thingspeak
```

## メモ

- Lambda 関数のタイムアウトは 30 秒に設定されています。これは API の応答時間によっては調整が必要かもしれません。
- コードは Python 3.9 で実行されますが、必要に応じてランタイムを変更できます。
- ラズパイでのスケジュール実行（cron 等）よりも、EventBridge を使ったスケジュール実行の方が管理が容易です。
