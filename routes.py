from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import Pet

general_bp = Blueprint('general', __name__)

@general_bp.route('/')
def home():
    # Fetch 3 featured pets that are not yet adopted, ordered by newest first
    featured_pets = Pet.query.filter_by(is_adopted=False).order_by(Pet.created_at.desc()).limit(3).all()
    return render_template('home.html', featured_pets=featured_pets)

@general_bp.route('/about')
def about():
    return render_template('about.html')

@general_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Simulated contact form submission
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        flash(f'Thank you, {name}! Your message has been received. We will contact you at {email} soon.', 'success')
        return redirect(url_for('general.contact'))
    return render_template('contact.html')
