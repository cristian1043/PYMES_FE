from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.services.productos_service import ProductosService

productos_bp = Blueprint('productos', __name__, url_prefix='/productos')

@productos_bp.route('/', methods=['GET'])
def ver_productos():
    """Muestra el catálogo / tabla de productos."""
    productos = ProductosService.obtener_todos()
    return render_template('productos/ver_productos.html', productos=productos)

@productos_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    """Formulario y registro de un nuevo producto."""
    if request.method == 'POST':
        data = {
            'nombre': request.form.get('nombre'),
            'descripcion': request.form.get('descripcion'),
            'precio': float(request.form.get('precio', 0)),
            'stock': int(request.form.get('stock', 0)),
            'id_categoria': int(request.form.get('id_categoria')) if request.form.get('id_categoria') else None
        }
        res, err = ProductosService.crear(data)
        if err:
            flash(f"Error al crear el producto: {err}", "danger")
        else:
            flash("Producto creado exitosamente", "success")
            return redirect(url_for('productos.ver_productos'))

    categorias = ProductosService.obtener_categorias()
    return render_template('productos/nuevo_producto.html', categorias=categorias)
