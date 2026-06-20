from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange

class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=100)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('Register As', choices=[
        ('adopter', 'Adopter (Looking to adopt)'),
        ('shelter', 'Shelter/Rescue Organization')
    ], validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    city = StringField('City', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class PetForm(FlaskForm):
    name = StringField('Pet Name', validators=[DataRequired(), Length(max=100)])
    species = SelectField('Species', choices=[
        ('Dog', 'Dog'),
        ('Cat', 'Cat'),
        ('Rabbit', 'Rabbit'),
        ('Bird', 'Bird'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    breed = StringField('Breed', validators=[Optional(), Length(max=100)])
    age = IntegerField('Age (in years/months)', validators=[Optional(), NumberRange(min=0, max=100)])
    gender = SelectField('Gender', choices=[
        ('Male', 'Male'),
        ('Female', 'Female')
    ], validators=[DataRequired()])
    size = SelectField('Size', choices=[
        ('Small', 'Small'),
        ('Medium', 'Medium'),
        ('Large', 'Large')
    ], validators=[DataRequired()])
    color = StringField('Color', validators=[Optional(), Length(max=50)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=2000)])
    photo = FileField('Pet Photo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only (jpg, jpeg, png, webp)!')
    ])
    location = StringField('Location/City', validators=[DataRequired(), Length(max=100)])
    vaccinated = BooleanField('Fully Vaccinated')
    submit = SubmitField('Submit')


class AdoptionForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    address = StringField('Home Address', validators=[DataRequired(), Length(max=255)])
    home_type = SelectField('Home Type', choices=[
        ('Apartment', 'Apartment'),
        ('House', 'House'),
        ('Farmhouse', 'Farmhouse'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    reason = TextAreaField('Why do you want to adopt this pet?', validators=[
        DataRequired(),
        Length(min=10, max=2000, message='Please write at least 10 characters.')
    ])
    previous_pet_experience = TextAreaField('Describe your previous pet experience (if any)', validators=[
        Optional(),
        Length(max=2000)
    ])
    submit = SubmitField('Submit Application')
