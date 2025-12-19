from flask import Flask
from routes.landing import landing_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp

app = Flask(__name__)
app.secret_key = "arogyam_secret_key"

# Register blueprints
app.register_blueprint(landing_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

if __name__ == "__main__":
    app.run(debug=True)
