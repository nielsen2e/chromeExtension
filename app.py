from flask import Flask
from flask_cors import CORS  # Import the CORS function
from resources.blp import blp

app = Flask(__name__)

# Use CORS with your app instance
CORS(app)

# Register the blueprint
app.register_blueprint(blp)

if __name__ == "__main__":
    app.run()
