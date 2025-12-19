from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Avion

# ... Definición del Blueprint ...

bp = Blueprint('aviones', __name__, template_folder='templates')

@bp.route('/')
@login_required
def listado_aviones():
    
    aviones = Avion.query.filter_by(baja_logica=False).all()
    return render_template('aviones_listado.html', aviones=aviones)

@bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear_avion():
    if request.method == 'POST':
        
        modelo = request.form.get('modelo')
        capacidad = request.form.get('capacidad')

        nuevo_avion = Avion(
            modelo=modelo,
            capacidad=int(capacidad),
            estado='disponible', # Valor por defecto 
            baja_logica=False    # Valor por defecto 
        )

        try:
            db.session.add(nuevo_avion)
            db.session.commit()
            flash('Avión registrado con éxito.', 'success')
            return redirect(url_for('aviones.listado_aviones'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar: {e}', 'danger')
            return render_template('aviones_form.html')

    return render_template('aviones_form.html')


@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_avion(id):
    avion = Avion.query.get_or_404(id)
    estados_avion = ['disponible', 'mantenimiento', 'en_vuelo'] # Lista de estados posibles

    if request.method == 'POST':
        avion.modelo = request.form.get('modelo')
        try:
            avion.capacidad = int(request.form.get('capacidad'))
        except (ValueError, TypeError):
            pass 
            
        avion.estado = request.form.get('estado')
        
        db.session.commit()
        
        flash(f'Avión "{avion.modelo}" actualizado con éxito.', 'success')
        return redirect(url_for('aviones.listado_aviones')) 
    return render_template('aviones_form.html', avion=avion, estados_avion=estados_avion)


# --- FUNCIÓN PARA ELIMINAR (BAJA LÓGICA) ---
@bp.route('/baja/<int:id>', methods=['POST'])
@login_required
def baja_logica_avion(id):
    avion = Avion.query.get_or_404(id) # Busca el avión o tira error 404
    
    avion.baja_logica = True 
    
    try:
        db.session.commit()
        flash(f'Avión {avion.modelo} dado de baja correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar la baja: {e}', 'danger')
        
    return redirect(url_for('aviones.listado_aviones'))