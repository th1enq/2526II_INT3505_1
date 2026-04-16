import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.create_a_new_product_request import CreateANewProductRequest  # noqa: E501
from openapi_server.models.product import Product  # noqa: E501
from openapi_server import util


def create_a_new_product(body=None):  # noqa: E501
    """Create a new product

     # noqa: E501

    :param create_a_new_product_request: 
    :type create_a_new_product_request: dict | bytes

    :rtype: Union[Product, Tuple[Product, int], Tuple[Product, int, Dict[str, str]]
    """
    create_a_new_product_request = body
    if connexion.request.is_json:
        create_a_new_product_request = CreateANewProductRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_a_product(product_id):  # noqa: E501
    """Delete a product

     # noqa: E501

    :param product_id: Product ID
    :type product_id: 

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_a_product_by_id(product_id):  # noqa: E501
    """Get a product by ID

     # noqa: E501

    :param product_id: Product ID
    :type product_id: 

    :rtype: Union[Product, Tuple[Product, int], Tuple[Product, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_all_products():  # noqa: E501
    """Get all products

     # noqa: E501


    :rtype: Union[List[object], Tuple[List[object], int], Tuple[List[object], int, Dict[str, str]]
    """
    return 'do some magic!'


def update_a_product(product_id, body=None):  # noqa: E501
    """Update a product

     # noqa: E501

    :param product_id: Product ID
    :type product_id: 
    :param create_a_new_product_request: 
    :type create_a_new_product_request: dict | bytes

    :rtype: Union[Product, Tuple[Product, int], Tuple[Product, int, Dict[str, str]]
    """
    create_a_new_product_request = body
    if connexion.request.is_json:
        create_a_new_product_request = CreateANewProductRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
