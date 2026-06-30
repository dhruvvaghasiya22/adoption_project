import os
from flask import Flask
from flask_login import LoginManager
from PIL import Image, ImageDraw, ImageFont

from flask_cors import CORS
from config import Config
from models import db, User, Pet, AdoptionApplication
from werkzeug.security import generate_password_hash

# Import Blueprints
from routes import general_bp
from auth_routes import auth_bp
from pet_routes import pets_bp
from adoption_routes import adoptions_bp
from admin_routes import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for React frontend development server
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})


    # Initialize Database
    db.init_app(app)

    # Initialize Flask-Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    app.register_blueprint(general_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(pets_bp, url_prefix='/')
    app.register_blueprint(adoptions_bp, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/')

    # Setup database, seeding, and default assets
    with app.app_context():
        db.create_all()
        
        # 1. Generate default placeholder pet image if missing
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        default_img_path = os.path.join(upload_folder, 'default_pet.png')
        if not os.path.exists(default_img_path):
            # Create a nice warm peach colored placeholder image
            img = Image.new('RGB', (600, 450), color='#ffefe8')
            draw = ImageDraw.Draw(img)
            # Draw a friendly message/shapes
            draw.rectangle([(20, 20), (580, 430)], outline="#ff7e67", width=3)
            # Since standard fonts might not exist, we just draw a paw outline or a simple box
            draw.ellipse([(260, 160), (340, 240)], fill="#ff7e67")
            draw.ellipse([(220, 130), (270, 180)], fill="#ff7e67")
            draw.ellipse([(330, 130), (380, 180)], fill="#ff7e67")
            draw.ellipse([(190, 180), (240, 230)], fill="#ff7e67")
            draw.ellipse([(360, 180), (410, 230)], fill="#ff7e67")
            img.save(default_img_path)
            print("Generated default_pet.png placeholder image.")

        # 2. Seed Database with default accounts and pets
        if not User.query.first():
            # Seed Users
            admin_user = User(
                name='System Admin',
                email='admin@petadopt.com',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                phone='555-010-0000',
                city='San Francisco'
            )
            shelter_user = User(
                name='Happy Paws Rescue',
                email='shelter@petadopt.com',
                password_hash=generate_password_hash('shelter123'),
                role='shelter',
                phone='555-020-0000',
                city='San Francisco'
            )
            adopter_user = User(
                name='John Adopter',
                email='adopter@petadopt.com',
                password_hash=generate_password_hash('adopter123'),
                role='adopter',
                phone='555-019-2834',
                city='Los Angeles'
            )
            
            db.session.add_all([admin_user, shelter_user, adopter_user])
            db.session.commit()
            print("Default users seeded: admin@petadopt.com, shelter@petadopt.com, adopter@petadopt.com")

            # Seed Pets listed by shelter_user
            pet1 = Pet(
                name='Buddy',
                species='Dog',
                breed='Golden Retriever',
                age=2,
                gender='Male',
                size='Large',
                color='Golden',
                description='Buddy is a friendly, energetic Golden Retriever who loves to play fetch and swim. He is great with kids and other dogs.',
                photo='default_pet.png',
                location='San Francisco',
                vaccinated=True,
                shelter_id=shelter_user.id
            )
            pet2 = Pet(
                name='Whiskers',
                species='Cat',
                breed='Siamese',
                age=1,
                gender='Female',
                size='Small',
                color='Seal Point',
                description='Whiskers is a quiet, cuddly Siamese cat. She loves napping in sunbeams and enjoys gentle chin scratches.',
                photo='default_pet.png',
                location='San Francisco',
                vaccinated=True,
                shelter_id=shelter_user.id
            )
            pet3 = Pet(
                name='Bella',
                species='Rabbit',
                breed='Angora',
                age=3,
                gender='Female',
                size='Medium',
                color='White',
                description='Bella is a soft, sweet Angora rabbit. She requires regular brushing and loves chewing on fresh organic carrots.',
                photo='default_pet.png',
                location='Oakland',
                vaccinated=False,
                shelter_id=shelter_user.id
            )
            
            db.session.add_all([pet1, pet2, pet3])
            db.session.commit()
            print("Default pets seeded: Buddy, Whiskers, Bella")

    return app

app = create_app()

if __name__ == '__main__':
    # Launch developmental server
    app.run(debug=True, host='0.0.0.0', port=5000)
