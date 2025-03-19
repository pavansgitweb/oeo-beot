from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time

class RestartBot(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("main.py"):  
            print("Detected changes in main.py. Restarting bot...")
            bot_process.terminate()
            time.sleep(1)
            start_bot()

def start_bot():
    global bot_process
    bot_process = subprocess.Popen(["python", "main.py"])

start_bot()
event_handler = RestartBot()
observer = Observer()
observer.schedule(event_handler, path=".", recursive=False)
observer.start()

try:
    while True:
        time.sleep(5)
except KeyboardInterrupt:
    observer.stop()

observer.join()
