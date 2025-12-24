from flask import Flask
from routes.landing import landing_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.newborn import newborn_bp
from routes.medical_records import medical_bp
from routes.patient_records import patient_records_bp
import os


def create_app():
    app = Flask(__name__)

    # 🔐 Secret key (use env in production)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "arogyam_secret_key")

    # ✅ Register blueprints
    app.register_blueprint(landing_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(newborn_bp)
    app.register_blueprint(medical_bp)
    app.register_blueprint(patient_records_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
