from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app.models import db, Propietario
from app.modulos.auth.routes import roles_permitidos

bp = Blueprint('propietarios', __name__)


@bp.route('/')
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def list_propietarios():
    busqueda = request.args.get('busqueda', type=str)

    query = Propietario.query

    if busqueda:
        query = query.filter(
            (Propietario.nombre.like(f'%{busqueda}%')) |
            (Propietario.ci_nit.like(f'%{busqueda}%'))
        )

    propietarios = query.order_by(Propietario.nombre).all()

    return render_template('propietarios/index.html',
                           propietarios=propietarios,
                           busqueda=busqueda)


@bp.route('/crear', methods=['GET', 'POST'])
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def create_propietario():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        telefono = request.form.get('telefono', '').strip()
        correo = request.form.get('correo', '').strip()
        ci_nit = request.form.get('ci_nit', '').strip()

        if not nombre or not telefono or not ci_nit:
            flash('Nombre, teléfono y CI/NIT son obligatorios.', 'danger')
            return redirect(url_for('propietarios.create_propietario'))

        # Verificar CI/NIT duplicado
        existente = Propietario.query.filter_by(ci_nit=ci_nit).first()
        if existente:
            flash('Ya existe un propietario con ese CI/NIT.', 'danger')
            return redirect(url_for('propietarios.create_propietario'))

        nuevo = Propietario(
            nombre=nombre,
            telefono=telefono,
            ci_nit=ci_nit,
            correo=correo if correo else None
        )

        db.session.add(nuevo)
        db.session.commit()
        flash('Propietario registrado exitosamente.', 'success')
        return redirect(url_for('propietarios.list_propietarios'))

    return render_template('propietarios/crear.html')


@bp.route('/api/crear_rapido', methods=['POST'])
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def api_create_propietario():
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    telefono = data.get('telefono', '').strip()
    correo = data.get('correo', '').strip()
    ci_nit = data.get('ci_nit', '').strip()

    if not nombre or not telefono or not ci_nit:
        return jsonify({'success': False, 'message': 'Nombre, teléfono y CI/NIT son obligatorios.'}), 400

    existente = Propietario.query.filter_by(ci_nit=ci_nit).first()
    if existente:
        return jsonify({'success': False, 'message': 'Ya existe un propietario con ese CI/NIT.'}), 400

    nuevo = Propietario(
        nombre=nombre,
        telefono=telefono,
        ci_nit=ci_nit,
        correo=correo if correo else None
    )

    db.session.add(nuevo)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'propietario': {
            'id': nuevo.id,
            'nombre': nuevo.nombre,
            'ci_nit': nuevo.ci_nit
        }
    })


@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def edit_propietario(id):
    propietario = Propietario.query.get_or_404(id)

    if request.method == 'POST':
        propietario.nombre = request.form.get('nombre', '').strip()
        propietario.telefono = request.form.get('telefono', '').strip()
        propietario.correo = request.form.get('correo', '').strip() or None
        nuevo_ci = request.form.get('ci_nit', '').strip()

        if not propietario.nombre or not propietario.telefono or not nuevo_ci:
            flash('Nombre, teléfono y CI/NIT son obligatorios.', 'danger')
            return redirect(url_for('propietarios.edit_propietario', id=id))

        # Verificar CI/NIT duplicado (excluyendo el actual)
        existente = Propietario.query.filter(
            Propietario.ci_nit == nuevo_ci,
            Propietario.id != id
        ).first()
        if existente:
            flash('Ya existe otro propietario con ese CI/NIT.', 'danger')
            return redirect(url_for('propietarios.edit_propietario', id=id))

        propietario.ci_nit = nuevo_ci
        db.session.commit()
        flash('Propietario actualizado exitosamente.', 'success')
        return redirect(url_for('propietarios.list_propietarios'))

    return render_template('propietarios/editar.html', propietario=propietario)


@bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
@roles_permitidos(['Administrador'])
def delete_propietario(id):
    propietario = Propietario.query.get_or_404(id)

    # Verificar si tiene propiedades asociadas
    if propietario.propiedades:
        flash('No se puede eliminar: este propietario tiene propiedades asociadas.', 'danger')
        return redirect(url_for('propietarios.list_propietarios'))

    db.session.delete(propietario)
    db.session.commit()
    flash('Propietario eliminado exitosamente.', 'success')
    return redirect(url_for('propietarios.list_propietarios'))
