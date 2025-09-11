# Wrapper script para BackendBot Service
import sys
import os
import time
import subprocess
from datetime import datetime

def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(r'C:\Users\DELL\Desktop\BackendBot\logs\service.log', 'a') as f:
        f.write(f'{timestamp} - {message}\n')

def main():
    log_message('BackendBot Service starting...')
    os.environ['API_KEY'] = 'tu_clave_aqui'

    while True:
        try:
            log_message('Starting backend process...')
            process = subprocess.Popen([
                r'C:\Users\DELL\AppData\Local\Programs\Python\Python312\python.exe',
                r'C:\Users\DELL\Desktop\BackendBot\main.py'
            ], cwd=r'C:\Users\DELL\Desktop\BackendBot')

            process.wait()
            log_message(f'Backend process exited with code: {process.returncode}')

            if process.returncode != 0:
                log_message('Backend crashed, restarting in 5 seconds...')
                time.sleep(5)
            else:
                log_message('Backend stopped normally')
                break

        except Exception as e:
            log_message(f'Error in service wrapper: {e}')
            time.sleep(5)

if __name__ == '__main__':
    main()
