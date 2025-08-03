#!/bin/bash

# SwitchBot CO2 Monitor Lambda デプロイパッケージ作成スクリプト

echo "[INFO] Lambda デプロイパッケージの作成を開始します..."

# 作業ディレクトリの確認
if [ ! -f "lambda_function.py" ]; then
    echo "[ERROR] lambda_function.py が見つかりません。switchbot-co2-thingspeakディレクトリで実行してください。"
    exit 1
fi

# 一時的なビルドディレクトリの削除（既存の場合）
if [ -d "build" ]; then
    echo "[INFO] 既存のbuildディレクトリを削除しています..."
    rm -rf build
fi

# 既存のデプロイメントファイルの削除
if [ -f "deployment.zip" ]; then
    echo "[INFO] 既存のdeployment.zipを削除しています..."
    rm -f deployment.zip
fi

echo "[INFO] ビルドディレクトリを作成しています..."
mkdir build
cd build

echo "[INFO] 必要なファイルをコピーしています..."
cp ../lambda_function.py .
cp ../switchbot_sensor.py .
cp ../requirements.txt .

echo "[INFO] 依存パッケージをインストールしています..."
pip install --target . -r requirements.txt

# 不要なファイルの削除（パッケージサイズ削減のため）
echo "[INFO] 不要なファイルを削除しています..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

echo "[INFO] ZIPファイルを作成しています..."
zip -r ../deployment.zip . -q

# パッケージサイズの表示
package_size=$(ls -lh ../deployment.zip | awk '{print $5}')
echo "[SUCCESS] デプロイパッケージが作成されました: deployment.zip (${package_size})"

# 一時ディレクトリの削除
cd ..
rm -rf build

echo ""
echo "[SUCCESS] デプロイパッケージの作成が完了しました！"
echo ""
echo "次のステップ:"
echo "1. AWS Lambda コンソールで新しい関数を作成"
echo "2. deployment.zip をアップロード"
echo "3. 以下の環境変数を設定:"
echo "   - SWITCHBOT_TOKEN: SwitchBot APIトークン"
echo "   - SWITCHBOT_SECRET: SwitchBot APIシークレット"
echo "   - SWITCHBOT_DEVICE_ID: CO2センサーのデバイスID"
echo "   - THINGSPEAK_API_KEY: ThingSpeak Write API Key"
echo "4. 基本設定: メモリ128MB, タイムアウト30秒"
echo "5. EventBridge でスケジュール実行を設定（推奨: 1時間ごと）"