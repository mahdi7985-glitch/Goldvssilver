import sqlite3
import json
import os
from datetime import datetime
import jdatetime

# استفاده از مسیر موقت یا دایرکتوری فعلی
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "signals.db")  # مستقیماً در ریشه پروژه

def init_db():
    """ایجاد دیتابیس"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                date_persian TEXT,
                score INTEGER,
                reasons TEXT,
                price REAL,
                stop_loss REAL,
                take_profit REAL,
                is_profitable INTEGER
            )
        """)
        conn.commit()
        conn.close()
        print(f"✅ دیتابیس در مسیر {DB_PATH} ایجاد شد")
    except Exception as e:
        print(f"❌ خطا در ایجاد دیتابیس: {e}")
        raise

def save_signal(score, reasons, data, risk):
    """ذخیره سیگنال در دیتابیس"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        now = datetime.now()
        date_persian = jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M")
        
        cursor.execute("""
            INSERT INTO signals (timestamp, date_persian, score, reasons, price, stop_loss, take_profit, is_profitable)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now.isoformat(),
            date_persian,
            score,
            json.dumps(reasons),
            data['silver_999'],
            risk['stop_loss'],
            risk['take_profit'],
            1 if risk['is_profitable'] else 0
        ))
        
        conn.commit()
        signal_id = cursor.lastrowid
        conn.close()
        return signal_id
    except Exception as e:
        print(f"❌ خطا در ذخیره سیگنال: {e}")
        return None

def get_last_signal():
    """دریافت آخرین سیگنال"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT score, price FROM signals ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {'score': result[0], 'price': result[1]}
        return None
    except Exception as e:
        print(f"❌ خطا در دریافت آخرین سیگنال: {e}")
        return None
