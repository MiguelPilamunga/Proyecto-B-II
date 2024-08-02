from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
import logging

app = Flask(__name__)

# Configurar el registro de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def procesar_query(query):
    # Obtener el tipo de transacción (INSERT, UPDATE, etc.)
    tipo_transaccion = query.split(' ')[0].upper()

    # Obtener el nombre de la tabla
    nombre_tabla = query.split(' ')[2]

    return tipo_transaccion, nombre_tabla


def verificar_integridad_referencial(engine, nombre_tabla, query):
    # Obtener el tipo de transacción (INSERT, UPDATE, etc.)
    tipo_transaccion = query.split(' ')[0].upper()

    if tipo_transaccion == 'INSERT':
        # Obtener los valores insertados en el query
        valores = query.split('VALUES')[1].strip().strip('()').split(',')
        id_producto = int(valores[0].strip().strip("'"))
        id_categoria = int(valores[2].strip().strip("'")) if valores[2].strip().strip("'") != 'NULL' else None

        # Verificar si el id de producto ya existe en la tabla producto
        query_producto = text(f"SELECT COUNT(*) FROM producto WHERE id = {id_producto}")
        with engine.connect() as connection:
            result_producto = connection.execute(query_producto).fetchone()
            count_producto = result_producto[0]

        # Verificar si el id de categoría existe en la tabla categoria
        query_categoria = text(
            f"SELECT COUNT(*) FROM categoria WHERE id = {id_categoria}") if id_categoria is not None else text(
            "SELECT 1")
        with engine.connect() as connection:
            result_categoria = connection.execute(query_categoria).fetchone()
            count_categoria = result_categoria[0]

        return count_producto == 0, count_categoria > 0

    elif tipo_transaccion == 'UPDATE':
        # Obtener los valores actualizados en el query
        set_clause = query.split('SET')[1].split('WHERE')[0].strip()
        id_categoria = int(set_clause.split('=')[1].strip())

        # Obtener el id del producto actualizado
        where_clause = query.split('WHERE')[1].strip()
        id_producto = int(where_clause.split('=')[1].strip())

        # Verificar si el id de producto existe en la tabla producto
        query_producto = text(f"SELECT COUNT(*) FROM producto WHERE id = {id_producto}")
        with engine.connect() as connection:
            result_producto = connection.execute(query_producto).fetchone()
            count_producto = result_producto[0]

        # Verificar si el id de categoría existe en la tabla categoria
        query_categoria = text(f"SELECT COUNT(*) FROM categoria WHERE id = {id_categoria}")
        with engine.connect() as connection:
            result_categoria = connection.execute(query_categoria).fetchone()
            count_categoria = result_categoria[0]

        return count_producto > 0, count_categoria > 0

    else:
        # Para otros tipos de transacciones, puedes agregar la lógica de verificación correspondiente
        return True, True


@app.route('/auditoria/auditar', methods=['POST'])
def auditar():
    server = request.form.get('server')
    database = request.form.get('database')
    username = request.form.get('username')
    password = request.form.get('password')
    query = request.form.get('query')

    connection_string = f"mssql+pymssql://{username}:{password}@{server}/{database}"
    engine = create_engine(connection_string)

    tipo_transaccion, nombre_tabla = procesar_query(query)

    logging.info(f"Auditoría iniciada para la tabla '{nombre_tabla}' con el tipo de transacción '{tipo_transaccion}'")

    check_unique, check_fk = verificar_integridad_referencial(engine, nombre_tabla, query)

    if check_unique and check_fk:
        try:
            with engine.begin() as connection:
                connection.execute(text(query))
            logging.info(f"La transacción '{tipo_transaccion}' se realizó con éxito en la tabla '{nombre_tabla}'")
            return jsonify({'message': 'Transacción realizada con éxito'})
        except Exception as e:
            logging.error(
                f"Error al realizar la transacción '{tipo_transaccion}' en la tabla '{nombre_tabla}': {str(e)}")
            return jsonify({'error': f"Error al realizar la transacción: {str(e)}"}), 500
    else:
        errors = []
        if not check_unique:
            error_unique = f"El valor de 'id' ya existe en la tabla '{nombre_tabla}'"
            logging.warning(error_unique)
            errors.append(error_unique)
        if not check_fk:
            error_fk = f"El valor de 'id_categoria' no existe en la tabla 'categoria'"
            logging.warning(error_fk)
            errors.append(error_fk)
        return jsonify({'errors': errors}), 400


if __name__ == '__main__':
    app.run()