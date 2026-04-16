import unittest

from flask import json

from openapi_server.models.create_a_new_product_request import CreateANewProductRequest  # noqa: E501
from openapi_server.models.product import Product  # noqa: E501
from openapi_server.test import BaseTestCase


class TestProductsController(BaseTestCase):
    """ProductsController integration test stubs"""

    def test_create_a_new_product(self):
        """Test case for create_a_new_product

        Create a new product
        """
        create_a_new_product_request = openapi_server.CreateANewProductRequest()
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/products',
            method='POST',
            headers=headers,
            data=json.dumps(create_a_new_product_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_a_product(self):
        """Test case for delete_a_product

        Delete a product
        """
        headers = { 
        }
        response = self.client.open(
            '/api/products/{product_id}'.format(product_id=1),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_a_product_by_id(self):
        """Test case for get_a_product_by_id

        Get a product by ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/products/{product_id}'.format(product_id=1),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_all_products(self):
        """Test case for get_all_products

        Get all products
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/products',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_a_product(self):
        """Test case for update_a_product

        Update a product
        """
        create_a_new_product_request = openapi_server.CreateANewProductRequest()
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/products/{product_id}'.format(product_id=1),
            method='PUT',
            headers=headers,
            data=json.dumps(create_a_new_product_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
