from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Import routes after app creation to avoid circular imports
# In a larger app, we would use Blueprints.
from routes import *

if __name__ == '__main__':
    app.run(debug=True, port=5000)
