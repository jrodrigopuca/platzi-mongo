from bson.json_util import dumps, ObjectId
from flask import current_app
from pymongo import MongoClient, DESCENDING
from werkzeug.local import LocalProxy


# Este método se encarga de configurar la conexión con la base de datos
def get_db():
    platzi_db = current_app.config['PLATZI_DB_URI']
    client = MongoClient(platzi_db)
    return client.platzi


# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)


def test_connection():
    return dumps(db.collection_names())


def collection_stats(collection_nombre):
    return dumps(db.command('collstats', collection_nombre))

# -----------------Carreras-------------------------


def crear_carrera(json):
    return str(db.carreras.insert_one(json).inserted_id)


def consultar_carrera_por_id(carrera_id):
    return dumps(db.carreras.find_one(
        {'_id': ObjectId(carrera_id)}
    ))


def actualizar_carrera(carrera):
    # Esta funcion solamente actualiza nombre y descripcion de la carrera
    toFilter = {'_id':ObjectId(carrera['_id'])}
    toUpdate = {'$set':{'nombre': carrera['nombre'], 'descripcion': carrera['descripcion']}}
    return str(db.carreras.update_one(toFilter,toUpdate).modified_count)

def borrar_carrera_por_id(carrera_id):
    return str(db.carreras.delete_one({'_id':ObjectId(carrera_id)}))


# Clase de operadores
def consultar_carreras(skip, limit):
    return dumps(db.carreras.find({}).skip(int(skip)).limit(int(limit)))

# relación carrera-curso: agregar
def agregar_curso(json):
    curso = consultar_curso_por_id_proyeccion(json['id_curso'], proyeccion={'nombre': 1})
    toFilter = {'_id': ObjectId(json['id_carrera'])}
    toUpdate = {'$addToSet': {'cursos': curso}}
    return str(db.carreras.update_one(toFilter, toUpdate).modified_count)


def borrar_curso_de_carrera(json):
    toFilter = {'_id': ObjectId(json['id_carrera'])}
    toUpdate = {'$pull': {'cursos': {'_id': ObjectId(json['id_curso'])}}}
    return str(db.carreras.update_one(toFilter, toUpdate).modified_count)

# -----------------Cursos-------------------------


def crear_curso(json):
    return str(db.cursos.insert_one(json).inserted_id)


def consultar_curso_por_id(id_curso):
    return dumps(db.cursos.find_one({'_id':ObjectId(id_curso)}))


def actualizar_curso(curso):
    # Esta funcion solamente actualiza nombre, descripcion y clases del curso
    filterId = {'_id': ObjectId(curso['_id'])}
    toUpdate = {
        'nombre': curso['nombre'],
        'descripcion': curso['descripcion'],
        'clases': curso['clases']
    } 
    return str(db.cursos.update_one(filterId,{'$set':toUpdate}).modified_count)


def borrar_curso_por_id(curso_id):
    return str(db.cursos.delete_one({'_id':ObjectId(curso_id)}).deleted_count)

# relación carrera-curso: consultar
def consultar_curso_por_id_proyeccion(id_curso, proyeccion=None):
    return db.cursos.find_one({'_id':ObjectId(id_curso)}, proyeccion)


def consultar_curso_por_nombre(nombre):
    return dumps(db.cursos.find({'$text': {'$search': nombre}}))

