import os

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient


class ProductNotFoundError(Exception):
    pass


class InvalidProductIdError(Exception):
    pass


def _get_collection():
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    mongodb_db = os.getenv('MONGODB_DB', 'productdb')
    mongodb_collection = os.getenv('MONGODB_COLLECTION', 'products')

    client = MongoClient(mongodb_uri)
    return client[mongodb_db][mongodb_collection]


def _to_product(document):
    return {
        'id': str(document['_id']),
        'name': document['name'],
        'description': document.get('description'),
        'price': document['price'],
        'stock': document.get('stock', 0)
    }


def _to_object_id(product_id):
    try:
        return ObjectId(product_id)
    except (InvalidId, TypeError):
        raise InvalidProductIdError()


def list_products():
    collection = _get_collection()
    documents = collection.find().sort('_id', -1)
    return [_to_product(document) for document in documents]


def get_product(product_id):
    collection = _get_collection()
    object_id = _to_object_id(product_id)
    document = collection.find_one({'_id': object_id})
    if document is None:
        raise ProductNotFoundError()
    return _to_product(document)


def create_product(product_input):
    collection = _get_collection()
    document = {
        'name': product_input.name,
        'description': product_input.description,
        'price': product_input.price,
        'stock': product_input.stock if product_input.stock is not None else 0
    }
    inserted = collection.insert_one(document)
    created = collection.find_one({'_id': inserted.inserted_id})
    return _to_product(created)


def update_product(product_id, product_input):
    collection = _get_collection()
    object_id = _to_object_id(product_id)
    updated_document = {
        'name': product_input.name,
        'description': product_input.description,
        'price': product_input.price,
        'stock': product_input.stock if product_input.stock is not None else 0
    }
    result = collection.update_one({'_id': object_id}, {'$set': updated_document})
    if result.matched_count == 0:
        raise ProductNotFoundError()

    document = collection.find_one({'_id': object_id})
    return _to_product(document)


def delete_product(product_id):
    collection = _get_collection()
    object_id = _to_object_id(product_id)
    result = collection.delete_one({'_id': object_id})
    if result.deleted_count == 0:
        raise ProductNotFoundError()
