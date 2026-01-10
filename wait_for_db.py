
# !/usr/bin/env python
"""
Wait for database to be ready before starting the application.
"""
import os
import sys
import time
import MySQLdb
from decouple import config


def wait_for_db():
    """Wait for MySQL database to be ready."""
    db_host = config('DB_HOST', default='mysql')
    db_port = config('DB_PORT', default='3306', cast=int)
    db_name = config('DB_NAME', default='taskdb')
    db_user = config('DB_USER', default='taskuser')
    db_password = config('DB_PASSWORD', default='taskpass123')

    max_retries = 30
    retry_interval = 2

    print(f"Waiting for MySQL at {db_host}:{db_port}...")

    for attempt in range(max_retries):
        try:
            connection = MySQLdb.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                passwd=db_password,
                db=db_name
            )
            connection.close()
            print("✅ MySQL is ready!")
            return True
        except MySQLdb.Error as e:
            print(f"Attempt {attempt + 1}/{max_retries}: MySQL not ready yet - {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
            else:
                print("❌ Failed to connect to MySQL after maximum retries")
                sys.exit(1)

    return False


if __name__ == '__main__':
    wait_for_db()