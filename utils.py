import os
import uuid
from functools import wraps
from flask import abort, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename
from PIL import Image

def role_required(*roles):
    """Decorator to restrict access to specific user roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def save_photo(file_field_data):
    """Saves and resizes a pet photo using Pillow, returning the filename."""
    if not file_field_data:
        return 'default_pet.png'
    
    filename = secure_filename(file_field_data.filename)
    if not filename:
        return 'default_pet.png'
        
    # Generate unique filename using uuid
    ext = os.path.splitext(filename)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    
    # Ensure upload directory exists
    upload_dir = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
        
    filepath = os.path.join(upload_dir, unique_filename)
    
    try:
        # Open image using Pillow
        image = Image.open(file_field_data)
        
        # Convert RGBA to RGB if saving as JPEG
        if image.mode in ('RGBA', 'LA') and ext in ('.jpg', '.jpeg'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3]) # 3 is the alpha channel
            image = background
            
        # Resize/Thumbnail
        image.thumbnail((800, 800))
        image.save(filepath)
        return unique_filename
    except Exception as e:
        print(f"Error saving image: {e}")
        return 'default_pet.png'
