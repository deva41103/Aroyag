from flask import Flask
from routes.landing import landing_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.newborn import newborn_bp
from routes.medical_records import medical_bp
from routes.patient_records import patient_records_bp


app = Flask(__name__)
app.secret_key = "arogyam_secret_key"

# Register blueprints
app.register_blueprint(landing_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(newborn_bp)
app.register_blueprint(medical_bp)
app.register_blueprint(patient_records_bp)

if __name__ == "__main__":
    app.run(debug=True)
