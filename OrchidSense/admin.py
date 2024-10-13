from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

# Define a Blueprint for admin-related routes
# The 'admin_bp' blueprint will handle routes prefixed with '/admin'
# and use templates from the 'templates' folder.admin_bp = Blueprint('admin', __name__, template_folder='templates')

@admin_bp.route('/admin')
@login_required
def admin_dashboard():
    """
        Route for the admin dashboard page.
        Accessible only by logged-in users with admin privileges.
        If the user is not an admin, they will receive a 403 Forbidden error.

        :return: Rendered template for the admin dashboard.
        """
    if not current_user.is_admin:
        abort(403)  # If the user is not an admin, abort with a 403 error.
    return render_template('admin_dashboard.html')

@admin_bp.route('/admin/data')
@login_required
def admin_data():
    """
    Route for the admin data page.
    Accessible only by logged-in users with admin privileges.
    If the user is not an admin, they will receive a 403 Forbidden error.

    :return: Rendered template for the admin data page.
    """
    if not current_user.is_admin:
        abort(403) # If the user is not an admin, abort with a 403 error.
    return render_template('admin_data.html') # Render the admin data page template.
