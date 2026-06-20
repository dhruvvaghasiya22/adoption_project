from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from models import db, Pet, User, AdoptionApplication
from utils import role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'adopter':
        return redirect(url_for('adoptions.my_applications'))
        
    elif current_user.role == 'shelter':
        # Fetch shelter's own pets
        pets = Pet.query.filter_by(shelter_id=current_user.id).order_by(Pet.created_at.desc()).all()
        # Fetch applications for the shelter's pets
        applications = AdoptionApplication.query.join(Pet).filter(
            Pet.shelter_id == current_user.id
        ).order_by(AdoptionApplication.applied_at.desc()).all()
        
        # Calculate stats for dashboard
        total_pets = len(pets)
        adopted_pets = sum(1 for p in pets if p.is_adopted)
        pending_apps = sum(1 for a in applications if a.status == 'pending')
        
        return render_template('admin/dashboard.html', 
                               role='shelter', 
                               pets=pets, 
                               applications=applications,
                               total_pets=total_pets,
                               adopted_pets=adopted_pets,
                               pending_apps=pending_apps)
                               
    elif current_user.role == 'admin':
        # General stats
        total_users = User.query.count()
        total_pets = Pet.query.count()
        total_applications = AdoptionApplication.query.count()
        adopted_pets = Pet.query.filter_by(is_adopted=True).count()
        
        # Latest database records
        latest_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        latest_pets = Pet.query.order_by(Pet.created_at.desc()).limit(5).all()
        latest_applications = AdoptionApplication.query.order_by(AdoptionApplication.applied_at.desc()).limit(5).all()
        
        return render_template('admin/dashboard.html',
                               role='admin',
                               total_users=total_users,
                               total_pets=total_pets,
                               total_applications=total_applications,
                               adopted_pets=adopted_pets,
                               latest_users=latest_users,
                               latest_pets=latest_pets,
                               latest_applications=latest_applications)
    else:
        abort(403)


@admin_bp.route('/admin/manage-pets')
@login_required
@role_required('admin')
def manage_pets():
    pets = Pet.query.order_by(Pet.created_at.desc()).all()
    return render_template('admin/manage_pets.html', pets=pets)


@admin_bp.route('/admin/applications')
@login_required
@role_required('admin')
def manage_applications():
    applications = AdoptionApplication.query.order_by(AdoptionApplication.applied_at.desc()).all()
    return render_template('admin/manage_applications.html', applications=applications)


@admin_bp.route('/application/<int:application_id>/approve', methods=['POST'])
@login_required
@role_required('shelter', 'admin')
def approve_application(application_id):
    application = AdoptionApplication.query.get_or_404(application_id)
    pet = Pet.query.get_or_404(application.pet_id)
    
    if current_user.role != 'admin' and pet.shelter_id != current_user.id:
        abort(403)
        
    if pet.is_adopted:
        flash('This pet has already been adopted!', 'danger')
        return redirect(request.referrer or url_for('admin.dashboard'))
        
    application.status = 'approved'
    pet.is_adopted = True
    
    # Auto-reject other pending applications
    other_apps = AdoptionApplication.query.filter(
        AdoptionApplication.pet_id == pet.id,
        AdoptionApplication.id != application.id,
        AdoptionApplication.status == 'pending'
    ).all()
    for app in other_apps:
        app.status = 'rejected'
        
    db.session.commit()
    flash(f'Application approved! {pet.name} has been marked as adopted.', 'success')
    return redirect(request.referrer or url_for('admin.dashboard'))


@admin_bp.route('/application/<int:application_id>/reject', methods=['POST'])
@login_required
@role_required('shelter', 'admin')
def reject_application(application_id):
    application = AdoptionApplication.query.get_or_404(application_id)
    pet = Pet.query.get_or_404(application.pet_id)
    
    if current_user.role != 'admin' and pet.shelter_id != current_user.id:
        abort(403)
        
    application.status = 'rejected'
    db.session.commit()
    
    flash(f'Application for {pet.name} was rejected.', 'warning')
    return redirect(request.referrer or url_for('admin.dashboard'))


@admin_bp.route('/admin/manage-users')
@login_required
@role_required('admin')
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/manage_users.html', users=users)


@admin_bp.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.name = request.form.get('name', '').strip()
        user.email = request.form.get('email', '').strip()
        user.phone = request.form.get('phone', '').strip()
        user.city = request.form.get('city', '').strip()
        user.role = request.form.get('role', 'adopter')
        
        if not user.name or not user.email:
            flash('Name and Email are required!', 'danger')
            return render_template('admin/edit_user.html', user=user)
            
        db.session.commit()
        flash(f'User {user.name} has been updated successfully!', 'success')
        return redirect(url_for('admin.manage_users'))
        
    return render_template('admin/edit_user.html', user=user)


@admin_bp.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own admin account!', 'danger')
        return redirect(url_for('admin.manage_users'))
        
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.name} has been deleted successfully.', 'success')
    return redirect(url_for('admin.manage_users'))

