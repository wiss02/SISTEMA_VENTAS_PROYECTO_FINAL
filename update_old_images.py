from app import create_app
from app.models import db, Propiedad

# Lista de imágenes genéricas bonitas de casas/departamentos
DEFAULT_IMAGES = [
    'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800&auto=format&fit=crop&q=60',
    'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=800&auto=format&fit=crop&q=60'
]

def update_images():
    app = create_app()
    with app.app_context():
        propiedades_sin_imagen = Propiedad.query.filter(
            (Propiedad.imagen_url == None) | (Propiedad.imagen_url == '')
        ).all()
        
        count = 0
        for i, prop in enumerate(propiedades_sin_imagen):
            prop.imagen_url = DEFAULT_IMAGES[i % len(DEFAULT_IMAGES)]
            count += 1
            
        db.session.commit()
        print(f"Se actualizaron {count} propiedades con imágenes predeterminadas.")

if __name__ == '__main__':
    update_images()
