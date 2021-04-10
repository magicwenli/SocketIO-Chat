import os

from dotenv import load_dotenv

from app import create_app
from app.extends import socketio

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = create_app()

if __name__ == '__main__':
    socketio.run(app)
