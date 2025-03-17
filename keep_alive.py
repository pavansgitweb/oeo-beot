from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def main():
  return "Oreo Tree is online! \n credits :- Pavan the great , Gyan the top g"

def run():
  app.run(host="0.0.0.0", port=8080)

def keep_alive():
  server = Thread(target=run)
  server.start()
