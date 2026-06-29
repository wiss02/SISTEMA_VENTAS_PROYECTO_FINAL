from app import create_app
from app.models import db, Rol, Usuario, TipoPropiedad, EstadoPropiedad, Propietario, Propiedad, Visita, Contrato
from datetime import datetime, timedelta

app = create_app()

def seed_database():
    with app.app_context():
        db.create_all()
        
        # Verificar si ya existen roles en la BD
        if Rol.query.first():
            return
            
        print("Iniciando sembrado de datos de prueba...")
        
        # 1. Crear Roles
        rol_admin = Rol(nombre_rol='Administrador', descripcion='Acceso total al sistema y configuraciones.')
        rol_agente = Rol(nombre_rol='Agente', descripcion='Gestión de catálogo, visitas, contratos y clientes.')
        rol_cliente = Rol(nombre_rol='Cliente', descripcion='Visualización de catálogo y solicitud de visitas.')
        rol_propietario = Rol(nombre_rol='Propietario', descripcion='Dueño de uno o más inmuebles en la plataforma.')
        db.session.add_all([rol_admin, rol_agente, rol_cliente, rol_propietario])
        db.session.commit()
        
        # 2. Crear Usuarios
        # ADMINISTRADOR PRINCIPAL — Wilson
        user_admin = Usuario(
            username='wilson', 
            nombre_completo='Wilson Rene',
            correo='wilsonrenelp@gmail.com', 
            rol_id=rol_admin.id
        )
        user_admin.set_password('admin123')
        
        # Segundo admin (backup)
        user_admin2 = Usuario(
            username='admin', 
            nombre_completo='Administrador del Sistema',
            correo='admin@tem742.com', 
            rol_id=rol_admin.id
        )
        user_admin2.set_password('admin123')
        
        user_agente1 = Usuario(
            username='carlos.agente', 
            nombre_completo='Carlos Mendoza Ríos',
            correo='carlos.mendoza@tem742.com', 
            rol_id=rol_agente.id
        )
        user_agente1.set_password('agente123')
        
        user_agente2 = Usuario(
            username='lucia.agente', 
            nombre_completo='Lucía Vargas Soliz',
            correo='lucia.vargas@tem742.com', 
            rol_id=rol_agente.id
        )
        user_agente2.set_password('agente123')
        
        user_cliente1 = Usuario(
            username='ana.cliente', 
            nombre_completo='Ana Fernández Quiroga',
            correo='ana.fernandez@correo.com', 
            rol_id=rol_cliente.id
        )
        user_cliente1.set_password('cliente123')
        
        user_cliente2 = Usuario(
            username='marco.cliente', 
            nombre_completo='Marco Gutiérrez Peña',
            correo='marco.gutierrez@correo.com', 
            rol_id=rol_cliente.id
        )
        user_cliente2.set_password('cliente123')
        
        db.session.add_all([user_admin, user_admin2, user_agente1, user_agente2, user_cliente1, user_cliente2])
        db.session.commit()
        
        # 3. Tipos de Propiedad
        tipo_casa = TipoPropiedad(nombre_tipo='Casa')
        tipo_depto = TipoPropiedad(nombre_tipo='Departamento')
        tipo_local = TipoPropiedad(nombre_tipo='Local Comercial')
        tipo_terreno = TipoPropiedad(nombre_tipo='Terreno')
        tipo_oficina = TipoPropiedad(nombre_tipo='Oficina')
        db.session.add_all([tipo_casa, tipo_depto, tipo_local, tipo_terreno, tipo_oficina])
        db.session.commit()
        
        # 4. Estados de Propiedad
        est_disp = EstadoPropiedad(nombre_estado='Disponible')
        est_res = EstadoPropiedad(nombre_estado='Reservada')
        est_alq = EstadoPropiedad(nombre_estado='Alquilada')
        est_vend = EstadoPropiedad(nombre_estado='Vendida')
        db.session.add_all([est_disp, est_res, est_alq, est_vend])
        db.session.commit()
        
        # 5. Propietarios
        prop1 = Propietario(nombre='Carlos Eduardo Mendoza', telefono='+591 71234567', correo='carlos.mendoza@propietario.com', ci_nit='1234567 LP')
        prop2 = Propietario(nombre='María Teresa Delgado', telefono='+591 72345678', correo='maria.delgado@propietario.com', ci_nit='2345678 CB')
        prop3 = Propietario(nombre='Roberto Andrés Gómez', telefono='+591 73456789', correo='roberto.gomez@propietario.com', ci_nit='3456789 SC')
        prop4 = Propietario(nombre='Patricia Soledad Flores', telefono='+591 74567890', correo='patricia.flores@propietario.com', ci_nit='4567890 OR')
        prop5 = Propietario(nombre='Fernando José Quispe', telefono='+591 75678901', ci_nit='5678901 PT')
        db.session.add_all([prop1, prop2, prop3, prop4, prop5])
        db.session.commit()
        
        # 6. Propiedades (7 inmuebles para mejor demostración)
        p1 = Propiedad(
            titulo='Moderna Casa en Condominio Cerrado',
            descripcion='Hermosa casa de dos plantas con 4 habitaciones, 3 baños, amplio jardín privado, parrillero y garaje para 2 vehículos. Acabados de primera calidad con pisos de porcelanato.',
            precio=185000.00,
            direccion='Av. Busch, Condominio Sevilla, Casa N° 15',
            accion='Venta',
            tipo_id=tipo_casa.id,
            propietario_id=prop1.id,
            agente_id=user_agente1.id,
            estado_id=est_disp.id
        )
        p2 = Propiedad(
            titulo='Departamento Céntrico 2 Dormitorios',
            descripcion='Excelente departamento amoblado en piso 8. Balcón panorámico, cocina americana de concepto abierto, áreas sociales en la terraza común. Incluye parqueo subterráneo.',
            precio=600.00,
            direccion='Calle 21 de Calacoto, Edificio Tower, Piso 8',
            accion='Alquiler',
            tipo_id=tipo_depto.id,
            propietario_id=prop2.id,
            agente_id=user_agente1.id,
            estado_id=est_alq.id
        )
        p3 = Propiedad(
            titulo='Local Comercial sobre Avenida Principal',
            descripcion='Amplio local de 120 m² con excelente iluminación natural, baños independientes e instalaciones para gas industrial. Ideal para restaurante o tienda.',
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
            descripcion='Lote de 500 m² con topografía plana, totalmente saneado e inscrito en derechos reales. Acceso a todos los servicios básicos. Excelente para proyecto residencial.',
            precio=95000.00,
            direccion='Zona Achumani, Calle 15, Lote N° 4',
            accion='Venta',
            tipo_id=tipo_terreno.id,
            propietario_id=prop1.id,
            agente_id=user_agente2.id,
            estado_id=est_vend.id
        )
        p5 = Propiedad(
            titulo='Oficina Ejecutiva en Torre Corporativa',
            descripcion='Oficina de 85 m² en piso 12 con vista panorámica a la ciudad. Incluye sala de reuniones, recepción independiente y 2 parqueos. Edificio con seguridad 24/7.',
            precio=950.00,
            direccion='Av. Arce, Torre Empresarial, Piso 12, Of. 1205',
            accion='Alquiler',
            tipo_id=tipo_oficina.id,
            propietario_id=prop4.id,
            agente_id=user_agente1.id,
            estado_id=est_disp.id
        )
        p6 = Propiedad(
            titulo='Casa Familiar con Jardín en Irpavi',
            descripcion='Casa de una planta con 3 dormitorios, 2 baños, living-comedor amplio, cocina equipada y jardín trasero de 80 m². Zona tranquila y segura, cerca de colegios.',
            precio=145000.00,
            direccion='Zona Irpavi, Calle 3, N° 456',
            accion='Venta',
            tipo_id=tipo_casa.id,
            propietario_id=prop5.id,
            agente_id=user_agente2.id,
            estado_id=est_res.id
        )
        p7 = Propiedad(
            titulo='Departamento Estudio Amoblado',
            descripcion='Departamento tipo estudio de 45 m², completamente amoblado y equipado. Ideal para profesionales o estudiantes. Incluye internet y servicios básicos.',
            precio=350.00,
            direccion='Zona Sopocachi, Av. 6 de Agosto, Edificio Plaza',
            accion='Alquiler',
            tipo_id=tipo_depto.id,
            propietario_id=prop2.id,
            agente_id=user_agente1.id,
            estado_id=est_disp.id
        )
        db.session.add_all([p1, p2, p3, p4, p5, p6, p7])
        db.session.commit()
        
        # 7. Visitas
        ahora = datetime.now()
        v1 = Visita(
            fecha_hora=ahora + timedelta(days=2, hours=10),
            estado_visita='Programada',
            observaciones='Cliente interesado en verificar la iluminación natural y el estado de la grifería.',
            propiedad_id=p1.id,
            cliente_id=user_cliente1.id
        )
        v2 = Visita(
            fecha_hora=ahora - timedelta(days=3, hours=2),
            estado_visita='Realizada',
            observaciones='Visita completada. El cliente quedó satisfecho con la ubicación pero pidió negociar el precio.',
            propiedad_id=p3.id,
            cliente_id=user_cliente1.id
        )
        v3 = Visita(
            fecha_hora=ahora + timedelta(days=5, hours=15),
            estado_visita='Programada',
            observaciones='Primera visita del cliente. Interesado en alquiler para oficina personal.',
            propiedad_id=p5.id,
            cliente_id=user_cliente2.id
        )
        v4 = Visita(
            fecha_hora=ahora - timedelta(days=10),
            estado_visita='Cancelada',
            observaciones='El cliente canceló por motivos personales. Reprogramar la siguiente semana.',
            propiedad_id=p6.id,
            cliente_id=user_cliente2.id
        )
        v5 = Visita(
            fecha_hora=ahora - timedelta(days=1, hours=5),
            estado_visita='Realizada',
            observaciones='Visita al departamento estudio. Cliente muy interesado, solicitó contrato de alquiler.',
            propiedad_id=p7.id,
            cliente_id=user_cliente1.id
        )
        db.session.add_all([v1, v2, v3, v4, v5])
        db.session.commit()
        
        # 8. Contratos
        c1 = Contrato(
            monto_final=600.00,
            clausulas='Contrato de arrendamiento por 1 año forzoso con garantía de 1 mes. El inquilino se compromete a mantener el inmueble en buen estado y cubrir los servicios básicos.',
            tipo_contrato='Arrendamiento',
            propiedad_id=p2.id,
            cliente_id=user_cliente1.id
        )
        c2 = Contrato(
            monto_final=95000.00,
            clausulas='Contrato de compraventa al contado mediante transferencia bancaria. El vendedor entrega la propiedad libre de gravámenes y con documentación saneada en Derechos Reales.',
            tipo_contrato='Compraventa',
            propiedad_id=p4.id,
            cliente_id=user_cliente2.id
        )
        c3 = Contrato(
            monto_final=350.00,
            clausulas='Contrato de arrendamiento por 6 meses con opción a renovación. Incluye mobiliario y servicios básicos. Garantía de 1 mes de alquiler.',
            tipo_contrato='Arrendamiento',
            propiedad_id=p7.id,
            cliente_id=user_cliente1.id
        )
        db.session.add_all([c1, c2, c3])
        db.session.commit()
        
        print("=" * 50)
        print("¡Datos de prueba sembrados exitosamente!")
        print("=" * 50)
        print("")
        print("CREDENCIALES DE ACCESO:")
        print("-" * 50)
        print(f"  ADMIN:   wilson / admin123  (wilsonrenelp@gmail.com)")
        print(f"  ADMIN2:  admin / admin123")
        print(f"  AGENTE:  carlos.agente / agente123")
        print(f"  AGENTE:  lucia.agente / agente123")
        print(f"  CLIENTE: ana.cliente / cliente123")
        print(f"  CLIENTE: marco.cliente / cliente123")
        print("-" * 50)

# Ejecutar el sembrado de base de datos siempre (necesario para Gunicorn en Render)
seed_database()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
