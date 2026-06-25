from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from sqlalchemy import func
from app.models import db, Contrato, Propiedad, Usuario, Rol
from app.modulos.auth.routes import roles_permitidos

bp = Blueprint('contratos', __name__)


@bp.route('/')
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def list_contratos():
    tipo_filtro = request.args.get('tipo', type=str)

    query = Contrato.query

    if tipo_filtro:
        query = query.filter(Contrato.tipo_contrato == tipo_filtro)

    contratos = query.order_by(Contrato.fecha_firma.desc()).all()

    # Contadores
    total = Contrato.query.count()
    total_compraventa = db.session.query(func.sum(Contrato.monto_final)).filter(
        Contrato.tipo_contrato == 'Compraventa').scalar() or 0
    total_arrendamiento = db.session.query(func.sum(Contrato.monto_final)).filter(
        Contrato.tipo_contrato == 'Arrendamiento').scalar() or 0

    return render_template('contratos/index.html',
                           contratos=contratos,
                           total=total,
                           total_compraventa=float(total_compraventa),
                           total_arrendamiento=float(total_arrendamiento),
                           tipo_filtro=tipo_filtro)


@bp.route('/crear', methods=['GET', 'POST'])
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def create_contrato():
    propiedades = Propiedad.query.order_by(Propiedad.titulo).all()

    rol_cliente = Rol.query.filter_by(nombre_rol='Cliente').first()
    clientes = Usuario.query.filter_by(rol_id=rol_cliente.id).all() if rol_cliente else []

    if request.method == 'POST':
        monto_final = request.form.get('monto_final', type=float)
        tipo_contrato = request.form.get('tipo_contrato')
        propiedad_id = request.form.get('propiedad_id', type=int)
        cliente_id = request.form.get('cliente_id', type=int)
        clausulas = request.form.get('clausulas', '').strip()

        if not monto_final or not tipo_contrato or not propiedad_id or not cliente_id:
            flash('Todos los campos obligatorios deben completarse.', 'danger')
            return redirect(url_for('contratos.create_contrato'))

        nuevo_contrato = Contrato(
            monto_final=monto_final,
            tipo_contrato=tipo_contrato,
            propiedad_id=propiedad_id,
            cliente_id=cliente_id,
            clausulas=clausulas if clausulas else None
        )

        db.session.add(nuevo_contrato)
        db.session.commit()
        flash('Contrato registrado exitosamente.', 'success')
        return redirect(url_for('contratos.list_contratos'))

    return render_template('contratos/crear.html',
                           propiedades=propiedades,
                           clientes=clientes)


@bp.route('/detalle/<int:id>')
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def detail_contrato(id):
    contrato = Contrato.query.get_or_404(id)
    return render_template('contratos/detalle.html', contrato=contrato)


@bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
@roles_permitidos(['Administrador'])
def delete_contrato(id):
    contrato = Contrato.query.get_or_404(id)
    db.session.delete(contrato)
    db.session.commit()
    flash('Contrato eliminado exitosamente.', 'success')
    return redirect(url_for('contratos.list_contratos'))
