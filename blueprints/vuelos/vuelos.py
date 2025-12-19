from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Vuelo, Avion, Tripulante, VueloTripulacion
from datetime import datetime

bp = Blueprint('vuelos', __name__, template_folder='templates')


# ----------------- 1. LISTAR / FILTRAR VUELOS (CASO N° 1) -----------------


@bp.route('/', methods=['GET'])
@login_required 
def listado_vuelos_frontend():
    # Inicializar la consulta base: solo vuelos con baja_logica=False
    query = Vuelo.query.filter_by(baja_logica=False)
    
    # -----------------------------------------------------------
    # 1. Obtener parámetros de búsqueda del formulario (GET)
    # -----------------------------------------------------------
    origen = request.args.get('origen')
    destino = request.args.get('destino')
    estado = request.args.get('estado')
    estados_posibles = ['Programado', 'Demorado', 'Embarcando', 'Cancelado', 'Aterrizado']
    
    # -----------------------------------------------------------
    # 2. Aplicar filtros dinámicamente si los parámetros existen
    # -----------------------------------------------------------
    
    # Filtro por Origen
    if origen:
        # Usamos .ilike() para búsqueda flexible (case-insensitive LIKE)
        query = query.filter(Vuelo.origen.ilike(f'%{origen}%'))

    # Filtro por Destino
    if destino:
        query = query.filter(Vuelo.destino.ilike(f'%{destino}%'))

    # Filtro por Estado
    if estado:
        query = query.filter(Vuelo.estado == estado)

    # -----------------------------------------------------------
    # 3. Ejecutar la consulta final
    # -----------------------------------------------------------
    vuelos = query.all()
    
    return render_template('vuelos_listado.html', 
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
        fecha_hora = request.form.get('fecha_hora')
        id_avion = request.form.get('id_avion')

        # Buscamos el avión para obtener su capacidad automáticamente
        avion_seleccionado = Avion.query.get(id_avion)
        
        if not avion_seleccionado:
            flash('Error: Debe seleccionar un avión válido.', 'danger')
            return redirect(url_for('vuelos.crear_vuelo'))

        # Creamos el vuelo usando la capacidad del avión
        nuevo_vuelo = Vuelo(
            origen=origen,
            destino=destino,
            fecha_hora=fecha_hora,
            id_avion=id_avion,
            capacidad_total=avion_seleccionado.capacidad,
            estado='programado' 
        )

        try:
            db.session.add(nuevo_vuelo)
            db.session.commit()
            flash(f'Vuelo de {origen} a {destino} creado con éxito.', 'success')
            return redirect(url_for('vuelos.listado_vuelos_frontend'))
        except Exception as e:
            db.session.rollback()
            print(f"DEBUG: Error al guardar: {e}")
            flash('Error al guardar en la base de datos.', 'danger')

    aviones = Avion.query.filter_by(baja_logica=False).all()
    return render_template('vuelos_form.html', aviones=aviones)



@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required 
def editar_vuelo(id):
    vuelo = Vuelo.query.get_or_404(id)
    estados_vuelo = ['Programado', 'Demorado', 'Embarcando', 'Cancelado', 'Aterrizado']

    if request.method == 'POST':
        # LÓGICA POST: Actualizar vuelo y gestionar cambio de estado de Avión
        id_avion_nuevo = int(request.form['id_avion'])
        id_avion_viejo = vuelo.id_avion

        # Manejo de fecha_hora:
        fecha_hora_str = request.form['fecha_hora']
        fecha_hora = datetime.datetime.strptime(fecha_hora_str, '%Y-%m-%dT%H:%M')
        
        # 1. Liberación del Avión Anterior (si el avión ha cambiado)
        if id_avion_viejo != id_avion_nuevo:
            # Si había un avión asignado antes, lo ponemos como 'disponible'
            if id_avion_viejo:
                avion_antiguo = Avion.query.get(id_avion_viejo)
                # Solo liberar si estaba 'en vuelo'
                if avion_antiguo and avion_antiguo.estado == 'en vuelo': 
                    # CORRECCIÓN 2: Usamos 'disponible' en minúsculas
                    avion_antiguo.estado = 'disponible' 
                    db.session.add(avion_antiguo)
        
            # 2. Asignar el nuevo avión y ponerlo en 'en vuelo'
            avion_nuevo = Avion.query.get(id_avion_nuevo)
            if avion_nuevo:
                 # CORRECCIÓN 2: Usamos 'en vuelo' en minúsculas
                avion_nuevo.estado = 'en vuelo' 
                db.session.add(avion_nuevo)

        # 3. Actualizar datos del vuelo
        vuelo.origen = request.form['origen']
        vuelo.destino = request.form['destino']
        vuelo.fecha_hora = fecha_hora
        vuelo.id_avion = id_avion_nuevo
        vuelo.estado = request.form['estado']

        try:
            db.session.commit()
            flash('Vuelo actualizado y estado del avión gestionado exitosamente.', 'success')
            return redirect(url_for('vuelos.listado_vuelos_frontend'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al editar el vuelo: {e}', 'danger')
            return redirect(url_for('vuelos.editar_vuelo', id=id))

    # LÓGICA GET: Mostrar formulario. Traer aviones disponibles + el asignado al vuelo
    aviones_disponibles = Avion.query.filter(
        (Avion.estado == 'disponible') | (Avion.id == vuelo.id_avion)
    ).all()
        
    return render_template('vuelos_form.html', 
                           vuelo=vuelo, 
                           aviones=aviones_disponibles, 
                           estados_vuelo=estados_vuelo)


@bp.route('/baja/<int:id>', methods=['POST'])
@login_required
def baja_logica_vuelo(id):
    # 1. Buscar el vuelo
    vuelo = Vuelo.query.get(id)
    
    if not vuelo:
        flash('Vuelo no encontrado.', 'danger')
        return redirect(url_for('vuelos.listado_vuelos_frontend'))
        
    # --- LÓGICA DE LIBERACIÓN DEL AVIÓN AGREGADA ---
    # 2. Buscar el avión asignado a este vuelo
    avion_asignado = Avion.query.get(vuelo.id_avion)
    
    # 3. Liberar el avión si existe y si su estado actual es 'en vuelo'
    if avion_asignado and avion_asignado.estado == 'en vuelo':
        avion_asignado.estado = 'disponible'
        db.session.add(avion_asignado)
        mensaje_avion = f" Avión {avion_asignado.modelo} ha sido liberado."
    else:
        mensaje_avion = ""
    # ----------------------------------------------------
        
    # 4. Realizar la baja lógica del vuelo
    vuelo.baja_logica = True
    vuelo.estado = 'Cancelado'
    
    try:
        db.session.commit()
        flash(f'Vuelo ID {vuelo.id} dado de baja (Eliminación Lógica) con éxito.{mensaje_avion}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al dar de baja el vuelo: {e}', 'danger')
    
    return redirect(url_for('vuelos.listado_vuelos_frontend'))


# ----------------- ASIGNAR/QUITAR TRIPULACIÓN (CASO N° 5) -----------------

@bp.route('/ver_asignar_tripulacion/<int:id_vuelo>')
@login_required
def ver_asignar_tripulacion(id_vuelo):
    vuelo = Vuelo.query.get_or_404(id_vuelo) #
    
    # Traemos tripulantes para el selector (solo activos)
    todos_tripulantes = Tripulante.query.filter_by(baja_logica=False).all()
    
    # Traemos los que YA están en este vuelo para mostrarlos abajo
    asignados = Tripulante.query.join(VueloTripulacion).filter(VueloTripulacion.id_vuelo == id_vuelo).all()
    
    return render_template('asignar_tripulacion.html', 
                           vuelo=vuelo, 
                           tripulantes=todos_tripulantes,
                           asignados=asignados)


@bp.route('/asignar_tripulante/<int:id_vuelo>', methods=['POST'])
@login_required
def asignar_tripulante(id_vuelo):
    vuelo = Vuelo.query.get_or_404(id_vuelo)
    id_tripulante_raw = request.form.get('id_tripulante')
    
    if not id_tripulante_raw:
        flash('Debe seleccionar un tripulante.', 'danger')
        return redirect(url_for('vuelos.ver_asignar_tripulacion', id_vuelo=id_vuelo))

    id_tripulante = int(id_tripulante_raw)
    tripulante = Tripulante.query.get(id_tripulante)

    if not tripulante:
        flash('Tripulante no encontrado.', 'danger')
        return redirect(url_for('vuelos.ver_asignar_tripulacion', id_vuelo=id_vuelo))

    # 1. Verificar si ya está asignado (evitar duplicados exactos)
    existe = VueloTripulacion.query.filter_by(id_vuelo=id_vuelo, id_tripulante=id_tripulante).first()
    if existe:
        flash(f'{tripulante.nombre} ya está en este vuelo.', 'warning')
        return redirect(url_for('vuelos.ver_asignar_tripulacion', id_vuelo=id_vuelo))

    # 2. Contar cuántos hay de cada rol ya asignados a este vuelo
    # Usamos un join para contar por el rol del tripulante
    asignados = Tripulante.query.join(VueloTripulacion).filter(VueloTripulacion.id_vuelo == id_vuelo).all()
    
    conteo_pilotos = sum(1 for t in asignados if t.rol.lower() == 'piloto')
    conteo_copilotos = sum(1 for t in asignados if t.rol.lower() == 'copiloto')
    conteo_auxiliares = sum(1 for t in asignados if t.rol.lower() == 'auxiliar')

    # 3. Validaciones de cupo según el rol del que queremos agregar ahora
    rol_nuevo = tripulante.rol.lower()

    if rol_nuevo == 'piloto' and conteo_pilotos >= 1:
        flash('Error: El vuelo ya tiene un piloto asignado.', 'danger')
    elif rol_nuevo == 'copiloto' and conteo_copilotos >= 1:
        flash('Error: El vuelo ya tiene un copiloto asignado.', 'danger')
    elif rol_nuevo == 'auxiliar' and conteo_auxiliares >= 2:
        flash('Error: El vuelo ya tiene el máximo de 2 auxiliares.', 'danger')
    else:
        # Si pasa todas las validaciones, procedemos a guardar
        nueva_asignacion = VueloTripulacion(id_vuelo=id_vuelo, id_tripulante=id_tripulante)
        db.session.add(nueva_asignacion)
        try:
            db.session.commit()
            flash(f'{tripulante.nombre} ({tripulante.rol}) asignado con éxito.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error en la base de datos: {e}', 'danger')

    return redirect(url_for('vuelos.ver_asignar_tripulacion', id_vuelo=id_vuelo))


@bp.route('/quitar_tripulante/<int:id_vuelo>/<int:id_tripulante>', methods=['POST'])
@login_required
def quitar_tripulante(id_vuelo, id_tripulante):
    # Buscamos la asignación específica en la tabla intermedia
    asignacion = VueloTripulacion.query.filter_by(
        id_vuelo=id_vuelo, 
        id_tripulante=id_tripulante
    ).first()

    if asignacion:
        try:
            db.session.delete(asignacion)
            db.session.commit()
            flash('Tripulante quitado del vuelo correctamente.', 'info')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al quitar tripulante: {e}', 'danger')
    else:
        flash('No se encontró la asignación.', 'warning')

    return redirect(url_for('vuelos.ver_asignar_tripulacion', id_vuelo=id_vuelo))


#Panel de Estado===================================================================================================
@bp.route('/panel-estado')
@login_required
def panel_estado():
    # Solo vuelos que no estén cancelados ni borrados
    vuelos_en_curso = Vuelo.query.filter(
        Vuelo.baja_logica == False, 
        Vuelo.estado.in_(['En curso', 'Programado', 'Embarcando', 'En vuelo'])
    ).all()
    
    # El próximo vuelo a despegar (el más cercano en el tiempo)
    proximo_vuelo = Vuelo.query.filter(
        Vuelo.baja_logica == False, 
        Vuelo.estado == 'Programado'
    ).order_by(Vuelo.fecha_hora.asc()).first()

    return render_template('vuelos_panel.html', 
                           vuelos=vuelos_en_curso, 
                           proximo=proximo_vuelo)

@bp.route('/iniciar_vuelo/<int:id>', methods=['POST'])
@login_required
def iniciar_vuelo(id):
    vuelo = Vuelo.query.get_or_404(id)
    vuelo.estado = 'en vuelo' 
    db.session.commit()
    flash(f'El vuelo {vuelo.id} ha despegado.', 'info')
    return redirect(url_for('vuelos.panel_estado')) 

@bp.route('/arribar_vuelo/<int:id>', methods=['POST'])
@login_required
def arribar_vuelo(id):
    vuelo = Vuelo.query.get_or_404(id)
    vuelo.estado = 'arribado' # Estado final
    db.session.commit()
    flash(f'El vuelo {vuelo.id} ha llegado a destino.', 'success')
    return redirect(url_for('vuelos.panel_estado'))

@bp.route('/actualizar-estado/<int:id>/<nuevo_estado>', methods=['POST'])
@login_required
def actualizar_estado_simulado(id, nuevo_estado):
    vuelo = Vuelo.query.get_or_404(id)
    avion = Avion.query.get(vuelo.id_avion)
    
    vuelo.estado = nuevo_estado
    
    # Lógica de impacto en el avión (Caso N° 4 y 6)
    if nuevo_estado == 'Aterrizado' and avion:
        avion.estado = 'disponible' # Se libera el avión al aterrizar
    elif nuevo_estado == 'En vuelo' and avion:
        avion.estado = 'en vuelo' # Se asegura que figure ocupado
        
    try:
        db.session.commit()
        flash(f'Estado del vuelo {vuelo.id} actualizado a {nuevo_estado}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar estado: {e}', 'danger')
        
    return redirect(url_for('vuelos.panel_estado'))