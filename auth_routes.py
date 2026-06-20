from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from forms import RegisterForm, LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('general.home'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if email is already in use
        email_lower = form.email.data.lower().strip()
        existing_user = User.query.filter_by(email=email_lower).first()
        if existing_user:
            flash('An account with this email already exists.', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Create user object
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            name=form.name.data.strip(),
            email=email_lower,
            password_hash=hashed_password,
            role=form.role.data,
            phone=form.phone.data.strip() if form.phone.data else None,
            city=form.city.data.strip() if form.city.data else None
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('general.home'))
        
    form = LoginForm()
    if form.validate_on_submit():
        email_lower = form.email.data.lower().strip()
        user = User.query.filter_by(email=email_lower).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Welcome back, {user.name}!', 'success')
            
            # Redirect to next parameter if present
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            # Default redirects based on role
            if user.role in ['shelter', 'admin']:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('general.home'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('general.home'))
