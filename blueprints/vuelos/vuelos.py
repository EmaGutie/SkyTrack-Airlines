from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Vuelo, Avion, Tripulante, VueloTripulacion
from datetime import datetime

# Definición del Blueprint
bp = Blueprint('vuelos', __name__)

# ----------------- 1. LISTAR / FILTRAR VUELOS -----------------

@bp.route('/', methods=['GET'])
@login_required 
def listado_vuelos_frontend():
    query = Vuelo.query.filter_by(baja_logica=False)
    
    origen = request.args.get('origen')
    destino = request.args.get('destino')
    estado = request.args.get('estado')
    estados_posibles = ['Programado', 'Demorado', 'Embarcando', 'Cancelado', 'Aterrizado']
    
    if origen:
        query = query.filter(Vuelo.origen.ilike(f'%{origen}%'))
    if destino:
        query = query.filter(Vuelo.destino.ilike(f'%{destino}%'))
    if estado:
        query = query.filter(Vuelo.estado == estado)

    vuelos = query.all()
    
    # CORRECCIÓN: Ruta al template global centralizado
    return render_template('vuelos/vuelos_listado.html', 
                           vuelos=vuelos, 
                           estados_vuelo=estados_posibles,
                           filtro_origen=origen,
                           filtro_destino=destino,
                           filtro_estado=estado)

@bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear_vuelo():
    if request.method == 'POST':
        origen = request.form.get('origen')
        destino = request.form.get('destino')
        fecha_hora_str = request.form.get('fecha_hora')
        id_avion = request.form.get('id_avion')

        avion_seleccionado = Avion.query.get(id_avion)
        
        if not avion_seleccionado:
            flash('Error: Debe seleccionar un avión válido.', 'danger')
            return redirect(url_for('vuelos.crear_vuelo'))

        nuevo_vuelo = Vuelo(
            origen=origen,
            destino=destino,
            fecha_hora=datetime.strptime(fecha_hora_str, '%Y-%m-%dT%H:%M'),
            id_avion=id_avion,
            capacidad_total=avion_seleccionado.capacidad,
            estado='Programado' 
        )

        try:
            db.session.add(nuevo_vuelo)
            db.session.commit()
            flash(f'Vuelo de {origen} a {destino} creado con éxito.', 'success')
            return redirect(url_for('vuelos.listado_vuelos_frontend'))
        except Exception as e:
            db.session.rollback()
            flash('Error al guardar en la base de datos.', 'danger')

    aviones = Avion.query.filter_by(baja_logica=False).all()
    # CORRECCIÓN: Ruta al template global centralizado
    return render_template('vuelos/vuelos_form.html', aviones=aviones)

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required 
def editar_vuelo(id):
    vuelo = Vuelo.query.get_or_404(id)
    estados_vuelo = ['Programado', 'Demorado', 'Embarcando', 'Cancelado', 'Aterrizado']

    if request.method == 'POST':
        id_avion_nuevo = int(request.form['id_avion'])
        id_avion_viejo = vuelo.id_avion
        fecha_hora_str = request.form['fecha_hora']
        
        # 1. Liberación y asignación de avión
        if id_avion_viejo != id_avion_nuevo:
            if id_avion_viejo:
                avion_antiguo = Avion.query.get(id_avion_viejo)
                if avion_antiguo: avion_antiguo.estado = 'disponible' 
        
            avion_nuevo = Avion.query.get(id_avion_nuevo)
            if avion_nuevo: avion_nuevo.estado = 'en vuelo' 

        # 2. Actualizar datos
        vuelo.origen = request.form['origen']
        vuelo.destino = request.form['destino']
        vuelo.fecha_hora = datetime.strptime(fecha_hora_str, '%Y-%m-%dT%H:%M')
        vuelo.id_avion = id_avion_nuevo
        vuelo.estado = request.form['estado']

        try:
            db.session.commit()
            flash('Vuelo actualizado correctamente.', 'success')
            return redirect(url_for('vuelos.listado_vuelos_frontend'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al editar: {e}', 'danger')

    aviones_disponibles = Avion.query.filter((Avion.estado == 'disponible') | (Avion.id == vuelo.id_avion)).all()
    # CORRECCIÓN: Ruta al template global centralizado
    return render_template('vuelos/vuelos_form.html', vuelo=vuelo, aviones=aviones_disponibles, estados_vuelo=estados_vuelo)

@bp.route('/baja/<int:id>', methods=['POST'])
@login_required
def baja_logica_vuelo(id):
    vuelo = Vuelo.query.get_or_404(id)
    avion_asignado = Avion.query.get(vuelo.id_avion)
    
    if avion_asignado:
        avion_asignado.estado = 'disponible'
        
    vuelo.baja_logica = True
    vuelo.estado = 'Cancelado'
    
    db.session.commit()
    flash(f'Vuelo {vuelo.id} dado de baja y avión liberado.', 'success')
    return redirect(url_for('vuelos.listado_vuelos_frontend'))

# ----------------- ASIGNACIÓN DE TRIPULACIÓN -----------------

@bp.route('/ver_asignar_tripulacion/<int:id_vuelo>')
@login_required
def ver_asignar_tripulacion(id_vuelo):
    vuelo = Vuelo.query.get_or_404(id_vuelo)
    todos_tripulantes = Tripulante.query.filter_by(baja_logica=False).all()
    asignados = Tripulante.query.join(VueloTripulacion).filter(VueloTripulacion.id_vuelo == id_vuelo).all()
    
    # CORRECCIÓN: Ruta al template global centralizado
    return render_template('vuelos/asignar_tripulacion.html', 
                           vuelo=vuelo, 
                           tripulantes=todos_tripulantes,
                           asignados=asignados)

@bp.route('/asignar_tripulante/<int:id_vuelo>', methods=['POST'])
@login_required
def asignar_tripulante(id_vuelo):
    vuelo = Vuelo.query.get_or_404(id_vuelo)
    id_trip = request.form.get('id_tripulante')
    
    if not id_trip:
        flash('Seleccione un tripulante.', 'danger')
        return redirect(url_for('vuelos.ver_asignar_tripulacion', id_vuelo=id_vuelo))

    tripulante = Tripulante.query.get(id_trip)
    # Validaciones de cupo (Piloto 1, Copiloto 1, Auxiliares 2)
    asignados = Tripulante.query.join(VueloTripulacion).filter(VueloTripulacion.id_vuelo == id_vuelo).all()
    rol = tripulante.rol.lower()
    
    conteo = sum(1 for t in asignados if t.rol.lower() == rol)
    
    if (rol == 'piloto' and conteo >= 1) or (rol == 'copiloto' and conteo >= 1) or (rol == 'auxiliar' and conteo >= 2):
        flash(f'Cupo lleno para el rol {rol}.', 'danger')
    else:
        nueva = VueloTripulacion(id_vuelo=id_vuelo, id_tripulante=id_trip)
        db.session.add(nueva)
        db.session.commit()
        flash('Tripulante asignado.', 'success')

    return redirect(url_for('vuelos.ver_asignar_tripulacion', id_vuelo=id_vuelo))

@bp.route('/quitar_tripulante/<int:id_vuelo>/<int:id_tripulante>', methods=['POST'])
@login_required
def quitar_tripulante(id_vuelo, id_tripulante):
    asignacion = VueloTripulacion.query.filter_by(id_vuelo=id_vuelo, id_tripulante=id_tripulante).first()
    if asignacion:
        db.session.delete(asignacion)
        db.session.commit()
        flash('Tripulante quitado.', 'info')
    return redirect(url_for('vuelos.ver_asignar_tripulacion', id_vuelo=id_vuelo))

# ----------------- PANEL DE CONTROL -----------------

@bp.route('/panel-estado')
@login_required
def panel_estado():
    vuelos_en_curso = Vuelo.query.filter(Vuelo.baja_logica == False, 
                                        Vuelo.estado.in_(['Programado', 'Embarcando', 'En vuelo'])).all()
    proximo = Vuelo.query.filter_by(baja_logica=False, estado='Programado').order_by(Vuelo.fecha_hora.asc()).first()
    
    # CORRECCIÓN: Ruta al template global centralizado
    return render_template('vuelos/vuelos_panel.html', vuelos=vuelos_en_curso, proximo=proximo)

@bp.route('/actualizar-estado/<int:id>/<nuevo_estado>', methods=['POST'])
@login_required
def actualizar_estado_simulado(id, nuevo_estado):
    vuelo = Vuelo.query.get_or_404(id)
    vuelo.estado = nuevo_estado
    
    # Impacto en el avión
    avion = Avion.query.get(vuelo.id_avion)
    if nuevo_estado == 'Aterrizado' and avion:
        avion.estado = 'disponible'
    elif nuevo_estado == 'En vuelo' and avion:
        avion.estado = 'en vuelo'
        
    db.session.commit()
    flash(f'Vuelo {id} ahora está {nuevo_estado}.', 'success')
    return redirect(url_for('vuelos.panel_estado'))