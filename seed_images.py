import sqlite3
import os
from app import create_app
from app.models import db, Propiedad, TipoPropiedad, EstadoPropiedad, Propietario, Usuario

def migrate_and_seed():
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'inmobiliaria.db')
    
    # 1. Alter table
    try:
        print("Modificando tabla propiedades para agregar imagen_url...")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("ALTER TABLE propiedades ADD COLUMN imagen_url VARCHAR(255)")
        conn.commit()
        conn.close()
        print("Columna imagen_url agregada exitosamente.")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print("La columna imagen_url ya existe.")
        else:
            print("Error al alterar tabla:", e)
            
    # 2. Add 5 properties
    app = create_app()
    with app.app_context():
        # Get defaults
        tipo_casa = TipoPropiedad.query.filter_by(nombre_tipo='Casa').first()
        tipo_depto = TipoPropiedad.query.filter_by(nombre_tipo='Departamento').first()
        estado_disp = EstadoPropiedad.query.filter_by(nombre_estado='Disponible').first()
        propietario = Propietario.query.first()
        agente = Usuario.query.filter_by(username='wilson').first() or Usuario.query.first()
        
        if not (tipo_casa and tipo_depto and estado_disp and propietario and agente):
            print("Faltan datos base en la BD, no se pueden agregar propiedades.")
            return
            
        print("Añadiendo 5 propiedades nuevas con imágenes...")
        nuevas = [
            Propiedad(
                titulo='Hermosa Casa Minimalista',
                precio=150000.0,
                direccion='Av. Banzer Km 7, Santa Cruz',
                accion='Venta',
                tipo_id=tipo_casa.id,
                propietario_id=propietario.id,
                agente_id=agente.id,
                estado_id=estado_disp.id,
                descripcion='Casa moderna con 3 habitaciones, piscina y garaje doble.',
                imagen_url='https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&auto=format&fit=crop&q=60'
            ),
            Propiedad(
                titulo='Departamento de Lujo Centro',
                precio=850.0,
                direccion='Equipetrol Norte, Santa Cruz',
                accion='Alquiler',
                tipo_id=tipo_depto.id,
                propietario_id=propietario.id,
                agente_id=agente.id,
                estado_id=estado_disp.id,
                descripcion='Espectacular vista de la ciudad, amoblado, 2 dormitorios.',
                imagen_url='https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&auto=format&fit=crop&q=60'
            ),
            Propiedad(
                titulo='Casa Familiar Amplia',
                precio=125000.0,
                direccion='Urubó, Santa Cruz',
                accion='Venta',
                tipo_id=tipo_casa.id,
                propietario_id=propietario.id,
                agente_id=agente.id,
                estado_id=estado_disp.id,
                descripcion='Excelente oportunidad en zona exclusiva, patio grande ideal para niños.',
                imagen_url='https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&auto=format&fit=crop&q=60'
            ),
            Propiedad(
                titulo='Departamento Monoambiente',
                precio=350.0,
                direccion='Zona Sur, La Paz',
                accion='Alquiler',
                tipo_id=tipo_depto.id,
                propietario_id=propietario.id,
                agente_id=agente.id,
                estado_id=estado_disp.id,
                descripcion='Ideal para estudiantes o personas solas. Seguridad 24 hrs.',
                imagen_url='https://images.unsplash.com/photo-1536376072261-38c75010e6c9?w=800&auto=format&fit=crop&q=60'
            ),
            Propiedad(
                titulo='Casa Estilo Colonial',
                precio=180000.0,
                direccion='Sopocachi, La Paz',
                accion='Venta',
                tipo_id=tipo_casa.id,
                propietario_id=propietario.id,
                agente_id=agente.id,
                estado_id=estado_disp.id,
                descripcion='Casa con diseño clásico, amplios salones y detalles en madera.',
                imagen_url='https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83?w=800&auto=format&fit=crop&q=60'
            )
        ]
        
        db.session.add_all(nuevas)
        db.session.commit()
        print("Propiedades añadidas exitosamente.")

if __name__ == '__main__':
    migrate_and_seed()
