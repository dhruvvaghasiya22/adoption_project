from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, Pet
from forms import PetForm
from utils import role_required, save_photo

pets_bp = Blueprint('pets', __name__)

@pets_bp.route('/pets')
def pet_list():
    query = Pet.query.filter_by(is_adopted=False)
    
    # Get parameters
    search = request.args.get('search', '').strip()
    species = request.args.get('species', '').strip()
    breed = request.args.get('breed', '').strip()
    gender = request.args.get('gender', '').strip()
    size = request.args.get('size', '').strip()
    location = request.args.get('location', '').strip()
    age_group = request.args.get('age_group', '').strip()
    vaccinated = request.args.get('vaccinated', '').strip()
    
    if search:
        query = query.filter(db.or_(Pet.name.ilike(f'%{search}%'), Pet.breed.ilike(f'%{search}%')))
    if species:
        query = query.filter_by(species=species)
    if breed:
        query = query.filter_by(breed=breed)
    if gender:
        query = query.filter_by(gender=gender)
    if size:
        query = query.filter_by(size=size)
    if location:
        query = query.filter_by(location=location)
    if vaccinated == 'yes':
        query = query.filter_by(vaccinated=True)
    elif vaccinated == 'no':
        query = query.filter_by(vaccinated=False)
        
    if age_group:
        if age_group == 'baby':
            query = query.filter(Pet.age < 1)
        elif age_group == 'young':
            query = query.filter(Pet.age >= 1, Pet.age <= 3)
        elif age_group == 'adult':
            query = query.filter(Pet.age > 3, Pet.age <= 8)
        elif age_group == 'senior':
            query = query.filter(Pet.age > 8)
            
    pets = query.order_by(Pet.created_at.desc()).all()
    
    # Get dynamic filter choices
    all_breeds = db.session.query(Pet.breed).filter(Pet.is_adopted == False, Pet.breed != None).distinct().all()
    all_breeds = sorted([b[0] for b in all_breeds if b[0]])
    
    all_locations = db.session.query(Pet.location).filter(Pet.is_adopted == False, Pet.location != None).distinct().all()
    all_locations = sorted([l[0] for l in all_locations if l[0]])
    
    return render_template('pets/pet_list.html', 
                           pets=pets, 
                           all_breeds=all_breeds, 
                           all_locations=all_locations,
                           search=search,
                           species_filter=species,
                           breed_filter=breed,
                           gender_filter=gender,
                           size_filter=size,
                           location_filter=location,
                           age_group_filter=age_group,
                           vaccinated_filter=vaccinated)


@pets_bp.route('/pets/<int:pet_id>')
def pet_detail(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    return render_template('pets/pet_detail.html', pet=pet)


@pets_bp.route('/pets/add', methods=['GET', 'POST'])
@login_required
@role_required('shelter', 'admin')
def add_pet():
    form = PetForm()
    if form.validate_on_submit():
        photo_filename = 'default_pet.png'
        if form.photo.data:
            photo_filename = save_photo(form.photo.data)
            
        new_pet = Pet(
            name=form.name.data.strip(),
            species=form.species.data,
            breed=form.breed.data.strip() if form.breed.data else None,
            age=form.age.data,
            gender=form.gender.data,
            size=form.size.data,
            color=form.color.data.strip() if form.color.data else None,
            description=form.description.data.strip() if form.description.data else None,
            photo=photo_filename,
            location=form.location.data.strip(),
            vaccinated=form.vaccinated.data,
            shelter_id=current_user.id
        )
        
        db.session.add(new_pet)
        db.session.commit()
        
        flash(f'Pet "{new_pet.name}" has been listed successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
        
    return render_template('pets/add_pet.html', form=form)


@pets_bp.route('/pets/edit/<int:pet_id>', methods=['GET', 'POST'])
@login_required
@role_required('shelter', 'admin')
def edit_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if current_user.role != 'admin' and pet.shelter_id != current_user.id:
        abort(403)
        
    form = PetForm(obj=pet)
    if form.validate_on_submit():
        if form.photo.data:
            pet.photo = save_photo(form.photo.data)
            
        pet.name = form.name.data.strip()
        pet.species = form.species.data
        pet.breed = form.breed.data.strip() if form.breed.data else None
        pet.age = form.age.data
        pet.gender = form.gender.data
        pet.size = form.size.data
        pet.color = form.color.data.strip() if form.color.data else None
        pet.description = form.description.data.strip() if form.description.data else None
        pet.location = form.location.data.strip()
        pet.vaccinated = form.vaccinated.data
        
        db.session.commit()
        flash(f'Pet details for "{pet.name}" updated successfully.', 'success')
        return redirect(url_for('admin.dashboard'))
        
    return render_template('pets/edit_pet.html', form=form, pet=pet)


@pets_bp.route('/pets/delete/<int:pet_id>', methods=['POST'])
@login_required
@role_required('shelter', 'admin')
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if current_user.role != 'admin' and pet.shelter_id != current_user.id:
        abort(403)
        
    pet_name = pet.name
    db.session.delete(pet)
    db.session.commit()
    
    flash(f'Pet "{pet_name}" deleted successfully.', 'success')
    return redirect(url_for('admin.dashboard'))
