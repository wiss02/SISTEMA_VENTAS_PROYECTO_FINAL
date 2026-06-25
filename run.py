from app import create_app
from app.models import db, Rol, Usuario, TipoPropiedad, EstadoPropiedad, Propietario, Propiedad, Visita, Contrato
from datetime import datetime

app = create_app()

def seed_database():
    with app.app_context():
        db.create_all()
        
        # Verificar si ya existen roles en la BD
        if Rol.query.first():
            return
            
        print("Iniciando sembrado de datos de prueba (Nuevo Esquema)...")
        
        # 1. Crear Roles (nombre_rol)
        rol_admin = Rol(nombre_rol='Administrador', descripcion='Acceso total al sistema y configuraciones.')
        rol_agente = Rol(nombre_rol='Agente', descripcion='Gestión de catálogo, visitas, contratos y clientes.')
        rol_cliente = Rol(nombre_rol='Cliente', descripcion='Visualización de catálogo y solicitud de visitas.')
        rol_propietario = Rol(nombre_rol='Propietario', descripcion='Dueño de uno o más inmuebles en la plataforma.')
        db.session.add_all([rol_admin, rol_agente, rol_cliente, rol_propietario])
        db.session.commit()
        
        # 2. Crear Usuarios (Cifrado seguro con Werkzeug)
        user_admin = Usuario(
            username='admin', 
            nombre_completo='Administrador del Sistema',
            correo='admin@tem742.com', 
            rol_id=rol_admin.id
        )
        user_admin.set_password('admin123')
        
        user_agente = Usuario(
            username='agente', 
            nombre_completo='Carlos Agente Inmobiliario',
            correo='agente@tem742.com', 
            rol_id=rol_agente.id
        )
        user_agente.set_password('agente123')
        
        user_cliente = Usuario(
            username='cliente', 
            nombre_completo='Ana Cliente Interesada',
            correo='cliente@tem742.com', 
            rol_id=rol_cliente.id
        )
        user_cliente.set_password('cliente123')
        
        db.session.add_all([user_admin, user_agente, user_cliente])
        db.session.commit()
        
        # 3. Crear Tipos de Propiedad (nombre_tipo)
        tipo_casa = TipoPropiedad(nombre_tipo='Casa')
        tipo_depto = TipoPropiedad(nombre_tipo='Departamento')
        tipo_local = TipoPropiedad(nombre_tipo='Local Comercial')
        tipo_terreno = TipoPropiedad(nombre_tipo='Terreno')
        db.session.add_all([tipo_casa, tipo_depto, tipo_local, tipo_terreno])
        db.session.commit()
        
        # 4. Crear Estados de Propiedad (nombre_estado)
        est_disp = EstadoPropiedad(nombre_estado='Disponible')
        est_res = EstadoPropiedad(nombre_estado='Reservada')
        est_alq = EstadoPropiedad(nombre_estado='Alquilada')
        est_vend = EstadoPropiedad(nombre_estado='Vendida')
        db.session.add_all([est_disp, est_res, est_alq, est_vend])
        db.session.commit()
        
        # 5. Crear Propietarios (con ci_nit)
        prop1 = Propietario(nombre='Carlos Mendoza', telefono='+591 71234567', correo='carlos@propietario.com', ci_nit='1234567 LP')
        prop2 = Propietario(nombre='Maria Delgado', telefono='+591 72345678', correo='maria@propietario.com', ci_nit='2345678 CB')
        prop3 = Propietario(nombre='Roberto Gomez', telefono='+591 73456789', correo='roberto@propietario.com', ci_nit='3456789 SC')
        db.session.add_all([prop1, prop2, prop3])
        db.session.commit()
        
        # 6. Crear Propiedades (con accion, tipo_id, estado_id)
        p1 = Propiedad(
            titulo='Moderna Casa en Condominio Cerrado',
            descripcion='Hermosa casa de dos plantas con 4 habitaciones, 3 baños, amplio jardín privado, parrillero y garaje para 2 vehículos.',
            precio=185000.00,
            direccion='Av. Busch, Condominio Sevilla, Casa N° 15',
            accion='Venta',
            tipo_id=tipo_casa.id,
            propietario_id=prop1.id,
            agente_id=user_agente.id,
            estado_id=est_disp.id
        )
        p2 = Propiedad(
            titulo='Departamento Céntrico 2 Dormitorios',
            descripcion='Excelente departamento amoblado en piso 8. Cuenta con balcón panorámico, cocina americana de concepto abierto y hermosas áreas sociales en la terraza común.',
            precio=600.00,
            direccion='Calle 21 de Calacoto, Edificio Tower, N° 456',
            accion='Alquiler',
            tipo_id=tipo_depto.id,
            propietario_id=prop2.id,
            agente_id=user_agente.id,
            estado_id=est_alq.id
        )
        p3 = Propiedad(
            titulo='Local Comercial sobre Avenida Principal',
            descripcion='Amplio local de 120 mt2 con excelente iluminación, baños independientes e instalaciones para gas industrial. Ideal para restaurante, tienda o sucursal bancaria.',
            precio=1200.00,
            direccion='Av. Hernando Siles, N° 1205',
            accion='Alquiler',
            tipo_id=tipo_local.id,
            propietario_id=prop3.id,
            agente_id=user_admin.id,
            estado_id=est_disp.id
        )
        p4 = Propiedad(
            titulo='Terreno Amplio en Zona Residencial',
            descripcion='Lote de terreno de 500 mt2 con topografía plana, totalmente saneado e inscrito en derechos reales. Cuenta con acceso a todos los servicios básicos.',
            precio=95000.00,
            direccion='Zona Achumani, Calle 15, Lote N° 4',
            accion='Venta',
            tipo_id=tipo_terreno.id,
            propietario_id=prop1.id,
            agente_id=user_agente.id,
            estado_id=est_vend.id
        )
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()
        
        # 7. Crear Visitas
        v1 = Visita(
            fecha_hora=datetime(2026, 6, 25, 10, 30),
            estado_visita='Programada',
            observaciones='Cliente interesado en verificar la iluminación natural y el estado de la grifería.',
            propiedad_id=p1.id,
            cliente_id=user_cliente.id
        )
        db.session.add(v1)
        db.session.commit()
        
        # 8. Crear Contratos (Compraventa o Arrendamiento)
        c1 = Contrato(
            monto_final=600.00,
            clausulas='Contrato de arrendamiento por 1 año forzoso con garantía de 1 mes.',
            tipo_contrato='Arrendamiento',
            propiedad_id=p2.id,
            cliente_id=user_cliente.id
        )
        c2 = Contrato(
            monto_final=95000.00,
            clausulas='Contrato de compraventa al contado mediante transferencia bancaria.',
            tipo_contrato='Compraventa',
            propiedad_id=p4.id,
            cliente_id=user_cliente.id
        )
        db.session.add_all([c1, c2])
        db.session.commit()
        
        print("¡Datos de prueba sembrados exitosamente!")

if __name__ == '__main__':
    seed_database()
    app.run(debug=True, port=5000)
