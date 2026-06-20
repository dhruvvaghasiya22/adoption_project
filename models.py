from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='adopter')  # adopter, shelter, admin
    phone = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    pets = db.relationship('Pet', backref='shelter', lazy=True, cascade="all, delete-orphan")
    applications = db.relationship('AdoptionApplication', backref='applicant', lazy=True, cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        return f'<User {self.email}>'


class Pet(db.Model):
    __tablename__ = 'pets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(50), nullable=False)  # Dog, Cat, Rabbit, Bird, Other
    breed = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=False)  # Male, Female
    size = db.Column(db.String(20), nullable=False)  # Small, Medium, Large
    color = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    photo = db.Column(db.String(255), nullable=True, default='default_pet.png')
    location = db.Column(db.String(100), nullable=False)
    vaccinated = db.Column(db.Boolean, default=False)
    is_adopted = db.Column(db.Boolean, default=False)
    shelter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to applications
    applications = db.relationship('AdoptionApplication', backref='pet', lazy=True, cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super(Pet, self).__init__(**kwargs)

    def __repr__(self):
        return f'<Pet {self.name}>'


class AdoptionApplication(db.Model):
    __tablename__ = 'adoption_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    home_type = db.Column(db.String(50), nullable=False)  # Apartment, House, Farmhouse, Other
    reason = db.Column(db.Text, nullable=False)
    previous_pet_experience = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, approved, rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(AdoptionApplication, self).__init__(**kwargs)

    def __repr__(self):
        return f'<AdoptionApplication User:{self.applicant_id} Pet:{self.pet_id}>'
