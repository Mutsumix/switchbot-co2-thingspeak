#!/usr/bin/env python3
"""
SwitchBot CO2 Monitor Lambda デプロイパッケージ作成スクリプト
Windows/macOS/Linux対応版
"""

import os
import shutil
import zipfile
import subprocess
import sys
from pathlib import Path

def run_command(command, shell=False):
    """コマンドを実行し、結果を返す"""
    try:
        result = subprocess.run(command, shell=shell, check=True, 
                              capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def main():
    print("[INFO] Lambda デプロイパッケージの作成を開始します...")
    
    # 作業ディレクトリの確認
    if not Path("lambda_function.py").exists():
        print("[ERROR] lambda_function.py が見つかりません。")
        print("   switchbot-co2-thingspeakディレクトリで実行してください。")
        sys.exit(1)
    
    # 必要なファイルの確認
    required_files = ["lambda_function.py", "switchbot_sensor.py", "requirements.txt"]
    for file in required_files:
        if not Path(file).exists():
            print(f"[ERROR] {file} が見つかりません。")
            sys.exit(1)
    
    # 一時的なビルドディレクトリの削除（既存の場合）
    build_dir = Path("build")
    if build_dir.exists():
        print("[INFO] 既存のbuildディレクトリを削除しています...")
        shutil.rmtree(build_dir)
    
    # 既存のデプロイメントファイルの削除
    deployment_zip = Path("deployment.zip")
    if deployment_zip.exists():
        print("[INFO] 既存のdeployment.zipを削除しています...")
        deployment_zip.unlink()
    
    print("[INFO] ビルドディレクトリを作成しています...")
    build_dir.mkdir()
    
    print("[INFO] 必要なファイルをコピーしています...")
    for file in required_files:
        shutil.copy2(file, build_dir / file)
    
    print("[INFO] 依存パッケージをインストールしています...")
    # pip install コマンドを実行
    pip_cmd = [sys.executable, "-m", "pip", "install", "--target", str(build_dir), 
               "-r", str(build_dir / "requirements.txt")]
    
    success, output = run_command(pip_cmd)
    if not success:
        print(f"[ERROR] パッケージのインストールに失敗しました:\n{output}")
        sys.exit(1)
    
    print("[INFO] 不要なファイルを削除しています...")
    # 不要なファイル・ディレクトリの削除
    patterns_to_remove = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.dist-info",
        "**/*.egg-info",
        "**/tests",
        "**/test_*"
    ]
    
    for pattern in patterns_to_remove:
        for path in build_dir.glob(pattern):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                path.unlink(missing_ok=True)
    
    print("[INFO] ZIPファイルを作成しています...")
    with zipfile.ZipFile(deployment_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in build_dir.rglob('*'):
            if file_path.is_file():
                # build/ プレフィックスを除去してZIPに追加
                arc_name = file_path.relative_to(build_dir)
                zipf.write(file_path, arc_name)
    
    # パッケージサイズの表示
    package_size = deployment_zip.stat().st_size
    package_size_mb = package_size / (1024 * 1024)
    print(f"[SUCCESS] デプロイパッケージが作成されました: deployment.zip ({package_size_mb:.2f} MB)")
    
    # 一時ディレクトリの削除
    print("[INFO] 一時ディレクトリを削除しています...")
    shutil.rmtree(build_dir)
    
    print("")
    print("[SUCCESS] デプロイパッケージの作成が完了しました！")
    print("")
    print("次のステップ:")
    print("1. AWS Lambda コンソールで新しい関数を作成")
    print("   - 関数名: switchbot-co2-monitor")
    print("   - ランタイム: Python 3.9")
    print("   - IAM ロール: AWSLambdaBasicExecutionRole を持つロール")
    print("")
    print("2. deployment.zip をアップロード")
    print("")
    print("3. 以下の環境変数を設定:")
    print("   - SWITCHBOT_TOKEN: SwitchBot APIトークン")
    print("   - SWITCHBOT_SECRET: SwitchBot APIシークレット")
    print("   - SWITCHBOT_DEVICE_ID: CO2センサーのデバイスID")
    print("   - THINGSPEAK_API_KEY: ThingSpeak Write API Key")
    print("")
    print("4. 基本設定の調整:")
    print("   - メモリ: 128 MB")
    print("   - タイムアウト: 30秒")
    print("")
    print("5. EventBridge でスケジュール実行を設定（推奨: rate(1 hour)）")
    print("")
    print("[TIPS]")
    print("   - デバイスIDの取得: python tools/list_devices.py")
    print("   - テスト実行でCloudWatchログを確認してください")

if __name__ == "__main__":
    main()