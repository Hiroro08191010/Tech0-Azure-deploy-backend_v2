from sqlalchemy import create_engine
import os
from pathlib import Path

from dotenv import load_dotenv

# .env は「実行ディレクトリ」ではなく「このファイルから見たプロジェクト直下」を読む
# connect_MySQL.py = <root>/db_control/connect_MySQL.py なので parents[1] が <root>
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# DB_PORT が None / "None" のとき落ちないように保険
host_part = f"{DB_HOST}:{DB_PORT}" if DB_PORT and DB_PORT != "None" else DB_HOST

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{host_part}/{DB_NAME}"

# pem の場所：
# 1) Azure/AppService の環境変数 SSL_CA_PATH があればそれを使う
# 2) なければプロジェクト直下の DigiCertGlobalRootG2.crt.pem を使う（あなたの構成に一致）
env_ca = os.getenv("SSL_CA_PATH")
default_ca = PROJECT_ROOT / "DigiCertGlobalRootG2.crt.pem"
cert_path = Path(env_ca).expanduser() if env_ca else default_ca

# ファイル存在チェック（Azureで原因特定しやすくする）
if not cert_path.exists():
    raise FileNotFoundError(
        f"SSL CA pem not found.\n"
        f"  tried: {cert_path}\n"
        f"  PROJECT_ROOT: {PROJECT_ROOT}\n"
        f"  set env SSL_CA_PATH to override."
    )

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "ssl": {
            "ca": str(cert_path),
            "check_hostname": False,  # Azure MySQL だと必要になることあり
        }
    },
)


"""
コードの古いバージョン（参考用）：
from sqlalchemy import create_engine

import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# データベース接続情報
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# MySQLのURL構築
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

SSL_CA_PATH = os.getenv('SSL_CA_PATH')
# エンジンの作成
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "ssl_ca": SSL_CA_PATH
    }
)

# SSL証明書ファイルのパスを絶対パスに変換
# connect_MySQL.pyの場所から見た相対パス
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)  # db_controlの親ディレクトリ（backend）
cert_path = os.path.join(backend_dir, "DigiCertGlobalRootG2.crt.pem")

# エンジンの作成
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "ssl": {
            "ca": cert_path,
            "check_hostname": False
        }
    }
)
"""