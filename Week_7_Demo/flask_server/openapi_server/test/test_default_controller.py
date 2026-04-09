import unittest
from unittest.mock import patch

from flask import json

from openapi_server.models.product import Product  # noqa: E501
from openapi_server.models.product_input import ProductInput  # noqa: E501
from openapi_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_app_handlers_products_create_product(self):
        """Test case for app_handlers_products_create_product

        Create product
        """
        expected = {
            "id": "507f1f77bcf86cd799439011",
            "name": "name",
            "description": "description",
            "price": 0.08008281904610115,
            "stock": 0
        }
        product_input = {"price":0.08008281904610115,"name":"name","description":"description","stock":0}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        with patch('openapi_server.controllers.default_controller.product_service.create_product', return_value=expected):
            response = self.client.open(
                '/api/products',
                method='POST',
                headers=headers,
                data=json.dumps(product_input),
                content_type='application/json')

        self.assertStatus(response, 201)
        body = json.loads(response.data.decode('utf-8'))
        self.assertEqual(body['id'], expected['id'])

    def test_app_handlers_products_delete_product(self):
        """Test case for app_handlers_products_delete_product

        Delete product by id
        """
        headers = { 
        }
        with patch('openapi_server.controllers.default_controller.product_service.delete_product', return_value=None):
            response = self.client.open(
                '/api/products/{product_id}'.format(product_id='507f1f77bcf86cd799439011'),
                method='DELETE',
                headers=headers)

        self.assertStatus(response, 204)

    def test_app_handlers_products_get_product(self):
        """Test case for app_handlers_products_get_product

        Get product by id
        """
        expected = {
            "id": "507f1f77bcf86cd799439011",
            "name": "name",
            "description": "description",
            "price": 10.5,
            "stock": 5
        }
        headers = { 
            'Accept': 'application/json',
        }
        with patch('openapi_server.controllers.default_controller.product_service.get_product', return_value=expected):
            response = self.client.open(
                '/api/products/{product_id}'.format(product_id='507f1f77bcf86cd799439011'),
                method='GET',
                headers=headers)

        self.assertStatus(response, 200)
        body = json.loads(response.data.decode('utf-8'))
        self.assertEqual(body['id'], expected['id'])

    def test_app_handlers_products_list_products(self):
        """Test case for app_handlers_products_list_products

        List products
        """
        expected = [{
            "id": "507f1f77bcf86cd799439011",
            "name": "name",
            "description": "description",
            "price": 10.5,
            "stock": 5
        }]
        headers = { 
            'Accept': 'application/json',
        }
        with patch('openapi_server.controllers.default_controller.product_service.list_products', return_value=expected):
            response = self.client.open(
                '/api/products',
                method='GET',
                headers=headers)

        self.assertStatus(response, 200)
        body = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(body), 1)

    def test_app_handlers_products_update_product(self):
        """Test case for app_handlers_products_update_product

        Update product by id
        """
        expected = {
            "id": "507f1f77bcf86cd799439011",
            "name": "name",
            "description": "description",
            "price": 15.0,
            "stock": 10
        }
        product_input = {"price":0.08008281904610115,"name":"name","description":"description","stock":0}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        with patch('openapi_server.controllers.default_controller.product_service.update_product', return_value=expected):
            response = self.client.open(
                '/api/products/{product_id}'.format(product_id='507f1f77bcf86cd799439011'),
                method='PUT',
                headers=headers,
                data=json.dumps(product_input),
                content_type='application/json')

        self.assertStatus(response, 200)
        body = json.loads(response.data.decode('utf-8'))
        self.assertEqual(body['price'], expected['price'])


if __name__ == '__main__':
    unittest.main()
