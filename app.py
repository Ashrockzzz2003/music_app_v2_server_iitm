from flask import Flask
from controller.auth_controller import auth
from controller.user_controller import user
from controller.admin_controller import admin
from controller.public_controller import public

from db.init_db import reinitializeDatabase
from middleware.keyGen import generateKey

from flask_cors import CORS

app = Flask(__name__)
CORS(app)


app.secret_key = "OkvzD0IvqdPOa47J0q3z5VaGy2cCDoP6V5GEfO0kGeq3vFfk1cb7vs8QMJiwF0nGIcXWCKoqD6wE6h1mUQZdQu7hR3FLjDwyRCCOY6bfuLBpr+WgQIDAQABAoGAENt4zTvrXc7Sig4N3tUsJ"
app.config["UPLOAD_FOLDER"] = "static"


app.register_blueprint(auth, url_prefix="/api/auth")
app.register_blueprint(user, url_prefix="/api/user")
app.register_blueprint(admin, url_prefix="/api/admin")
app.register_blueprint(public, url_prefix="/api/public")

if __name__ == "__main__":
    # Clear Data and Reinitialize Database
    # reinitializeDatabase()
    # Generate RSA Keys
    # generateKey()
    app.run(debug=True, port=5000)
