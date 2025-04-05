# AWS CLI 設定手順

## 1. AWS CLI のインストール

### macOS の場合

**Homebrew を使用する場合：**

```bash
brew install awscli
```

**公式インストーラーを使用する場合：**

1. [AWS CLI 公式ダウンロードページ](https://aws.amazon.com/cli/)から macOS 用インストーラーをダウンロード
2. ダウンロードした PKG ファイルを実行
3. インストールウィザードの指示に従う

### インストール確認

インストール後、以下のコマンドを実行して正常にインストールされたか確認します：

```bash
aws --version
```

## 2. IAM ユーザーとアクセスキーの作成

1. [AWS Management Console](https://console.aws.amazon.com/)にサインイン
2. 右上のアカウント名をクリックし、「セキュリティ認証情報」を選択
3. 左側のメニューから「IAM ユーザー」を選択
4. 「ユーザーを作成」をクリック
5. ユーザー名（例：cli-user）を入力
6. アクセスの種類で「プログラムによるアクセス」を選択
7. 「次へ：アクセス権限」をクリック
8. 「既存のポリシーを直接アタッチ」を選択
9. 以下のポリシーを検索して選択（最小限必要なポリシー）
   - AmazonS3FullAccess
   - AmazonLambdaFullAccess
   - AmazonCloudWatchFullAccess
   - IAMFullAccess
   - AmazonSSMFullAccess
   - AWSCloudFormationFullAccess
10. 「次へ：タグ」→「次へ：確認」→「ユーザーの作成」をクリック
11. **重要：** アクセスキー ID とシークレットアクセスキーを表示するページが表示されます。このページを閉じると二度とシークレットアクセスキーを表示できないため、必ずこの情報をダウンロードするか、安全な場所にコピーしてください。

## 3. AWS CLI の設定

ターミナルで以下のコマンドを実行します：

```bash
aws configure
```

プロンプトに従って、以下の情報を入力します：

```
AWS Access Key ID [None]: 【発行されたアクセスキーID】
AWS Secret Access Key [None]: 【発行されたシークレットアクセスキー】
Default region name [None]: ap-northeast-1  # 東京リージョンの場合
Default output format [None]: json
```

これで AWS CLI の基本設定は完了です。

## 4. 設定の確認

以下のコマンドを実行して、設定が正しく行われているか確認します：

```bash
aws sts get-caller-identity
```

正常に設定されていれば、以下のような出力が表示されます：

```json
{
  "UserId": "AIDAXXXXXXXXXXXXXXXX",
  "Account": "123456789012",
  "Arn": "arn:aws:iam::123456789012:user/cli-user"
}
```

## 5. Lambda 用のデプロイパッケージの作成

AWS CLI の設定が完了したら、Lambda のデプロイパッケージを作成します：

```bash
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

## 6. CloudFormation スタックのデプロイ

config.yml 内の設定を参考に、パラメータを指定して CloudFormation スタックをデプロイします：

```bash
aws cloudformation create-stack \
  --stack-name switchbot-co2-thingspeak \
  --template-body file://cloudformation.yml \
  --capabilities CAPABILITY_IAM \
  --parameters \
  ParameterKey=ThingSpeakApiKey,ParameterValue="7N9FY1RVMJ4H2PLC" \
  ParameterKey=SwitchBotToken,ParameterValue="bb9d962f34b369f27393847fb2d19fe97f4dbb30b29698546155c8cfbe1dc54924db0f64eff0d4567509252dd2f32b77" \
  ParameterKey=SwitchBotSecret,ParameterValue="50a958c83b3b283851272f124194e9d8" \
  ParameterKey=SwitchBotDeviceId,ParameterValue="B0E9FE533857" \
  ParameterKey=ScheduleExpression,ParameterValue="rate(1 hour)"
```

これにより、AWS 環境にすべてのリソースが自動的に作成されます。
