import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

load_dotenv()

from src import create_app

app = create_app('development')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    print(f"Frontend corriendo en http://localhost:{port}")
    app.run(debug=True, port=port)
