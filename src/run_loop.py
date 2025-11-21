import time
from src.rules import failed_login_burst, off_hours_activity

if __name__ == "__main__":
    while True:
        failed_login_burst()
        off_hours_activity()
        time.sleep(60)
