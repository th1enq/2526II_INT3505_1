import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.product import Product  # noqa: E501
from openapi_server.models.product_input import ProductInput  # noqa: E501
from openapi_server.services import product_service


def app_handlers_products_create_product(body):  # noqa: E501
    """Create product

     # noqa: E501

    :param product_input: 
    :type product_input: dict | bytes

    :rtype: Union[Product, Tuple[Product, int], Tuple[Product, int, Dict[str, str]]
    """
    try:
        product_input = _parse_product_input(body)
        created = product_service.create_product(product_input)
        return Product.from_dict(created), 201
    except ValueError as exc:
        return {'message': str(exc)}, 400


def app_handlers_products_delete_product(product_id):  # noqa: E501
    """Delete product by id

     # noqa: E501

    :param product_id: MongoDB ObjectId string
    :type product_id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    try:
        product_service.delete_product(product_id)
        return None, 204
    except (product_service.ProductNotFoundError, product_service.InvalidProductIdError):
        return {'message': 'Product not found'}, 404


def app_handlers_products_get_product(product_id):  # noqa: E501
    """Get product by id

     # noqa: E501

    :param product_id: MongoDB ObjectId string
    :type product_id: str

    :rtype: Union[Product, Tuple[Product, int], Tuple[Product, int, Dict[str, str]]
    """
    try:
        product = product_service.get_product(product_id)
        return Product.from_dict(product)
    except (product_service.ProductNotFoundError, product_service.InvalidProductIdError):
        return {'message': 'Product not found'}, 404


def app_handlers_products_list_products():  # noqa: E501
    """List products

     # noqa: E501


    :rtype: Union[List[Product], Tuple[List[Product], int], Tuple[List[Product], int, Dict[str, str]]
    """
    products = product_service.list_products()
    return [Product.from_dict(product) for product in products]


def app_handlers_products_update_product(product_id, body):  # noqa: E501
    """Update product by id

     # noqa: E501

    :param product_id: MongoDB ObjectId string
    :type product_id: str
    :param product_input: 
    :type product_input: dict | bytes

    :rtype: Union[Product, Tuple[Product, int], Tuple[Product, int, Dict[str, str]]
    """
    try:
        product_input = _parse_product_input(body)
        updated = product_service.update_product(product_id, product_input)
        return Product.from_dict(updated)
    except ValueError as exc:
        return {'message': str(exc)}, 400
    except (product_service.ProductNotFoundError, product_service.InvalidProductIdError):
        return {'message': 'Product not found'}, 404


def _parse_product_input(body):
    if isinstance(body, ProductInput):
        return body

    if connexion.request.is_json:
        payload = connexion.request.get_json()
        return ProductInput.from_dict(payload)

    if isinstance(body, dict):
        return ProductInput.from_dict(body)

    raise ValueError('Invalid payload')
