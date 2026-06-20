from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import db, Pet, AdoptionApplication
from forms import AdoptionForm
from utils import role_required

adoptions_bp = Blueprint('adoptions', __name__)

@adoptions_bp.route('/adopt/<int:pet_id>', methods=['GET', 'POST'])
@login_required
@role_required('adopter')
def apply(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    
    # Check if pet is already adopted
    if pet.is_adopted:
        flash('This pet has already been adopted!', 'warning')
        return redirect(url_for('pets.pet_detail', pet_id=pet.id))
        
    # Check if applicant has already applied for this pet
    existing_app = AdoptionApplication.query.filter_by(
        pet_id=pet.id,
        applicant_id=current_user.id
    ).first()
    
    if existing_app:
        flash(f'You have already submitted an application for {pet.name} (Status: {existing_app.status.capitalize()}).', 'info')
        return redirect(url_for('adoptions.my_applications'))
        
    form = AdoptionForm()
    if form.validate_on_submit():
        new_app = AdoptionApplication(
            pet_id=pet.id,
            applicant_id=current_user.id,
            full_name=form.full_name.data.strip(),
            phone=form.phone.data.strip(),
            address=form.address.data.strip(),
            home_type=form.home_type.data,
            reason=form.reason.data.strip(),
            previous_pet_experience=form.previous_pet_experience.data.strip() if form.previous_pet_experience.data else None,
            status='pending'
        )
        
        db.session.add(new_app)
        db.session.commit()
        
        flash(f'Your adoption application for {pet.name} has been submitted successfully!', 'success')
        return redirect(url_for('adoptions.my_applications'))
        
    # Prefill the applicant's name and phone number if available in their profile
    if request.method == 'GET':
        form.full_name.data = current_user.name
        form.phone.data = current_user.phone
        
    return render_template('adoptions/apply.html', form=form, pet=pet)


@adoptions_bp.route('/my-applications')
@login_required
@role_required('adopter')
def my_applications():
    applications = AdoptionApplication.query.filter_by(
        applicant_id=current_user.id
    ).order_by(AdoptionApplication.applied_at.desc()).all()
    
    return render_template('adoptions/my_applications.html', applications=applications)
