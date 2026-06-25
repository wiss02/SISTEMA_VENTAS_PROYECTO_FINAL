from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models import db, Propiedad, TipoPropiedad, EstadoPropiedad, Propietario, Usuario, Rol
from app.modulos.auth.routes import roles_permitidos

bp = Blueprint('propiedades', __name__)

@bp.route('/')
def list_propiedades():
    tipo_id = request.args.get('tipo_id', type=int)
    estado_id = request.args.get('estado_id', type=int)
    precio_max = request.args.get('precio_max', type=float)
    accion = request.args.get('accion', type=str)
    busqueda = request.args.get('busqueda', type=str)

    query = Propiedad.query

    if tipo_id:
        query = query.filter(Propiedad.tipo_id == tipo_id)
    if estado_id:
        query = query.filter(Propiedad.estado_id == estado_id)
    if precio_max:
        query = query.filter(Propiedad.precio <= precio_max)
    if accion:
        query = query.filter(Propiedad.accion == accion)
    if busqueda:
        query = query.filter((Propiedad.titulo.like(f"%{busqueda}%")) | (Propiedad.direccion.like(f"%{busqueda}%")))

    propiedades = query.order_by(Propiedad.fecha_registro.desc()).all()
    tipos = TipoPropiedad.query.all()
    estados = EstadoPropiedad.query.all()

    return render_template('propiedades/index.html', 
                           propiedades=propiedades, 
                           tipos=tipos, 
                           estados=estados,
                           tipo_id=tipo_id,
                           estado_id=estado_id,
                           precio_max=precio_max,
                           accion=accion,
                           busqueda=busqueda)

@bp.route('/detalle/<int:id>')
def detail_propiedad(id):
    propiedad = Propiedad.query.get_or_404(id)
    return render_template('propiedades/detalle.html', propiedad=propiedad)

@bp.route('/crear', methods=['GET', 'POST'])
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def create_propiedad():
    tipos = TipoPropiedad.query.all()
    estados = EstadoPropiedad.query.all()
    propietarios = Propietario.query.all()
    
    agente_rol = Rol.query.filter_by(nombre_rol='Agente').first()
    admin_rol = Rol.query.filter_by(nombre_rol='Administrador').first()
    agentes = Usuario.query.filter(Usuario.rol_id.in_([
        agente_rol.id if agente_rol else 0, 
        admin_rol.id if admin_rol else 0
    ])).all()

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        precio = request.form.get('precio', type=float)
        direccion = request.form.get('direccion')
        accion = request.form.get('accion')
        tipo_id = request.form.get('tipo_id', type=int)
        propietario_id = request.form.get('propietario_id', type=int)
        agente_id = request.form.get('agente_id', type=int)
        estado_id = request.form.get('estado_id', type=int)

        if not titulo or not precio or not direccion or not accion or not tipo_id or not propietario_id or not agente_id or not estado_id:
            flash('Todos los campos obligatorios deben completarse.', 'danger')
            return redirect(url_for('propiedades.create_propiedad'))

        nueva_propiedad = Propiedad(
            titulo=titulo,
            descripcion=descripcion,
            precio=precio,
            direccion=direccion,
            accion=accion,
            tipo_id=tipo_id,
            propietario_id=propietario_id,
            agente_id=agente_id,
            estado_id=estado_id
        )

        db.session.add(nueva_propiedad)
        db.session.commit()
        flash('¡Propiedad creada exitosamente!', 'success')
        return redirect(url_for('propiedades.list_propiedades'))

    return render_template('propiedades/crear.html', tipos=tipos, estados=estados, propietarios=propietarios, agentes=agentes)

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def edit_propiedad(id):
    propiedad = Propiedad.query.get_or_404(id)
    tipos = TipoPropiedad.query.all()
    estados = EstadoPropiedad.query.all()
    propietarios = Propietario.query.all()
    
    agente_rol = Rol.query.filter_by(nombre_rol='Agente').first()
    admin_rol = Rol.query.filter_by(nombre_rol='Administrador').first()
    agentes = Usuario.query.filter(Usuario.rol_id.in_([
        agente_rol.id if agente_rol else 0, 
        admin_rol.id if admin_rol else 0
    ])).all()

    if request.method == 'POST':
        propiedad.titulo = request.form.get('titulo')
        propiedad.descripcion = request.form.get('descripcion')
        propiedad.precio = request.form.get('precio', type=float)
        propiedad.direccion = request.form.get('direccion')
        propiedad.accion = request.form.get('accion')
        propiedad.tipo_id = request.form.get('tipo_id', type=int)
        propiedad.propietario_id = request.form.get('propietario_id', type=int)
        propiedad.agente_id = request.form.get('agente_id', type=int)
        propiedad.estado_id = request.form.get('estado_id', type=int)

        if not propiedad.titulo or not propiedad.precio or not propiedad.direccion or not propiedad.accion or not propiedad.tipo_id or not propiedad.propietario_id or not propiedad.agente_id or not propiedad.estado_id:
            flash('Todos los campos obligatorios deben completarse.', 'danger')
            return redirect(url_for('propiedades.edit_propiedad', id=id))

        db.session.commit()
        flash('¡Propiedad actualizada exitosamente!', 'success')
        return redirect(url_for('propiedades.list_propiedades'))

    return render_template('propiedades/editar.html', propiedad=propiedad, tipos=tipos, estados=estados, propietarios=propietarios, agentes=agentes)

@bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def delete_propiedad(id):
    propiedad = Propiedad.query.get_or_404(id)
    db.session.delete(propiedad)
    db.session.commit()
    flash('Propiedad eliminada exitosamente.', 'success')
    return redirect(url_for('propiedades.list_propiedades'))
