from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, Visita, Propiedad, Usuario, Rol
from app.modulos.auth.routes import roles_permitidos
from datetime import datetime

bp = Blueprint('visitas', __name__)


@bp.route('/')
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def list_visitas():
    estado_filtro = request.args.get('estado', type=str)
    propiedad_filtro = request.args.get('propiedad_id', type=int)

    query = Visita.query

    if estado_filtro:
        query = query.filter(Visita.estado_visita == estado_filtro)
    if propiedad_filtro:
        query = query.filter(Visita.propiedad_id == propiedad_filtro)

    visitas = query.order_by(Visita.fecha_hora.desc()).all()
    propiedades = Propiedad.query.order_by(Propiedad.titulo).all()

    # Contadores
    total = Visita.query.count()
    programadas = Visita.query.filter_by(estado_visita='Programada').count()
    realizadas = Visita.query.filter_by(estado_visita='Realizada').count()
    canceladas = Visita.query.filter_by(estado_visita='Cancelada').count()

    return render_template('visitas/index.html',
                           visitas=visitas,
                           propiedades=propiedades,
                           total=total,
                           programadas=programadas,
                           realizadas=realizadas,
                           canceladas=canceladas,
                           estado_filtro=estado_filtro,
                           propiedad_filtro=propiedad_filtro)


@bp.route('/crear', methods=['GET', 'POST'])
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def create_visita():
    propiedades = Propiedad.query.order_by(Propiedad.titulo).all()

    # Obtener clientes (usuarios con rol Cliente)
    rol_cliente = Rol.query.filter_by(nombre_rol='Cliente').first()
    clientes = Usuario.query.filter_by(rol_id=rol_cliente.id).all() if rol_cliente else []

    if request.method == 'POST':
        fecha_str = request.form.get('fecha_hora')
        propiedad_id = request.form.get('propiedad_id', type=int)
        cliente_id = request.form.get('cliente_id', type=int)
        observaciones = request.form.get('observaciones', '').strip()

        if not fecha_str or not propiedad_id or not cliente_id:
            flash('Todos los campos obligatorios deben completarse.', 'danger')
            return redirect(url_for('visitas.create_visita'))

        try:
            fecha_hora = datetime.strptime(fecha_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Formato de fecha inválido.', 'danger')
            return redirect(url_for('visitas.create_visita'))

        nueva_visita = Visita(
            fecha_hora=fecha_hora,
            propiedad_id=propiedad_id,
            cliente_id=cliente_id,
            estado_visita='Programada',
            observaciones=observaciones if observaciones else None
        )

        db.session.add(nueva_visita)
        db.session.commit()
        flash('Visita programada exitosamente.', 'success')
        return redirect(url_for('visitas.list_visitas'))

    return render_template('visitas/crear.html',
                           propiedades=propiedades,
                           clientes=clientes)


@bp.route('/estado/<int:id>/<string:nuevo_estado>', methods=['POST'])
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def cambiar_estado(id, nuevo_estado):
    visita = Visita.query.get_or_404(id)

    if nuevo_estado not in ['Programada', 'Realizada', 'Cancelada']:
        flash('Estado de visita no válido.', 'danger')
        return redirect(url_for('visitas.list_visitas'))

    visita.estado_visita = nuevo_estado
    db.session.commit()
    flash(f'Visita marcada como "{nuevo_estado}".', 'success')
    return redirect(url_for('visitas.list_visitas'))


@bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def delete_visita(id):
    visita = Visita.query.get_or_404(id)
    db.session.delete(visita)
    db.session.commit()
    flash('Visita eliminada exitosamente.', 'success')
    return redirect(url_for('visitas.list_visitas'))

@bp.route('/solicitar/<int:propiedad_id>', methods=['POST'])
@login_required
@roles_permitidos(['Cliente'])
def solicitar_visita(propiedad_id):
    propiedad = Propiedad.query.get_or_404(propiedad_id)
    
    fecha_str = request.form.get('fecha_hora')
    observaciones = request.form.get('observaciones', '').strip()
    
    if not fecha_str:
        flash('Debes seleccionar una fecha y hora.', 'danger')
        return redirect(url_for('propiedades.detail_propiedad', id=propiedad_id))
        
    try:
        fecha_hora = datetime.strptime(fecha_str, '%Y-%m-%dT%H:%M')
    except ValueError:
        flash('Formato de fecha inválido.', 'danger')
        return redirect(url_for('propiedades.detail_propiedad', id=propiedad_id))
        
    nueva_visita = Visita(
        fecha_hora=fecha_hora,
        propiedad_id=propiedad.id,
        cliente_id=current_user.id,
        estado_visita='Programada',
        observaciones=observaciones if observaciones else 'Solicitada vía web por el cliente.'
    )
    
    db.session.add(nueva_visita)
    db.session.commit()
    
    flash('¡Tu solicitud de visita ha sido enviada exitosamente al agente encargado!', 'success')
    return redirect(url_for('propiedades.detail_propiedad', id=propiedad_id))
