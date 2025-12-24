from flask import Blueprint, render_template

# -------------------------------
# Landing / Home Blueprint
# -------------------------------
landing_bp = Blueprint(
    "landing",
    __name__,
    template_folder="templates"
)

@landing_bp.route("/", methods=["GET"])
def landing():
    """
    Public landing page
    - Entry point of the application
    - No authentication required
    """
    return render_template("landing.html")
