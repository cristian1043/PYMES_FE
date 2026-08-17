from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.services.productos_service import ProductosService
from src.utils.decorators import requiere_rol

productos_bp = Blueprint('productos', __name__, url_prefix='/productos')

@productos_bp.route('/', methods=['GET'])
@requiere_rol(1, 2, 3)
def ver_productos():
    """Muestra el catálogo / tabla de productos con soporte para paginación."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    res_paginado = ProductosService.obtener_todos(page=page, per_page=per_page)
    
    items = res_paginado.get("items", []) if isinstance(res_paginado, dict) else res_paginado
    return render_template('productos/ver_productos.html', productos=items, paginacion=res_paginado)

@productos_bp.route('/nuevo', methods=['GET', 'POST'])
@requiere_rol(1, 3) # Admin y Almacenista pueden crear/modificar productos e inventario
def nuevo_producto():
    """Formulario y registro de un nuevo producto (Admin y Almacenista)."""
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

@productos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@requiere_rol(1, 3) # Admin y Almacenista pueden editar productos
def editar_producto(id):
    """Formulario y procesamiento para actualizar un producto existente."""
    producto = ProductosService.obtener_por_id(id)
    if not producto:
        flash("El producto especificado no existe", "warning")
        return redirect(url_for('productos.ver_productos'))

    if request.method == 'POST':
        data = {
            'nombre': request.form.get('nombre'),
            'descripcion': request.form.get('descripcion'),
            'precio': float(request.form.get('precio', 0)),
            'stock': int(request.form.get('stock', 0)),
            'id_categoria': int(request.form.get('id_categoria')) if request.form.get('id_categoria') else None
        }
        res, err = ProductosService.actualizar(id, data)
        if err:
            flash(f"Error al actualizar el producto: {err}", "danger")
        else:
            flash("Producto actualizado exitosamente", "success")
            return redirect(url_for('productos.ver_productos'))

    categorias = ProductosService.obtener_categorias()
    return render_template('productos/editar_producto.html', producto=producto, categorias=categorias)
