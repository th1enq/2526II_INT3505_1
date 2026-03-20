"""
Simple API with Flask-RESTX - Auto-generates OpenAPI spec + Swagger UI
"""

from flask import Flask
from flask_restx import Api, Resource, fields, Namespace
from flask_cors import CORS


def create_app():
    """Application factory for generating OpenAPI spec."""
    app = Flask(__name__)
    app.config["RESTX_MASK_SWAGGER"] = False
    
    CORS(app)
    
    # Initialize Flask-RESTX API with auto-generated OpenAPI spec
    api = Api(
        app,
        version="1.0.0",
        title="Product Management API",
        description="A simple API for managing products",
        doc="/swagger"  # Swagger UI at /swagger
    )
    
    # Define namespace (like blueprint)
    products_ns = Namespace("products", description="Product operations")
    
    # Sample data
    products_db = [
        {"id": 1, "name": "Product A", "price": 99.99, "description": "First product"},
        {"id": 2, "name": "Product B", "price": 199.99, "description": "Second product"},
    ]
    
    # Define models for documentation
    product_model = api.model('Product', {
        'id': fields.Integer(required=True, description='Product ID'),
        'name': fields.String(required=True, description='Product name'),
        'price': fields.Float(required=True, description='Product price'),
        'description': fields.String(description='Product description')
    })
    
    product_input = api.model('ProductInput', {
        'name': fields.String(required=True, description='Product name'),
        'price': fields.Float(required=True, description='Product price'),
        'description': fields.String(description='Product description')
    })
    
    # Endpoints
    @products_ns.route('/')
    class ProductList(Resource):
        """Product list operations"""
        
        @products_ns.doc('list_products')
        @products_ns.marshal_list_with(product_model)
        def get(self):
            """Get all products"""
            return products_db, 200
        
        @products_ns.doc('create_product')
        @products_ns.expect(product_input)
        @products_ns.marshal_with(product_model, code=201)
        def post(self):
            """Create a new product"""
            data = api.payload
            new_product = {
                "id": max([p["id"] for p in products_db]) + 1,
                "name": data["name"],
                "price": data["price"],
                "description": data.get("description", "")
            }
            products_db.append(new_product)
            return new_product, 201
    
    @products_ns.route('/<int:product_id>')
    class ProductDetail(Resource):
        """Product detail operations"""
        
        @products_ns.doc('get_product')
        @products_ns.marshal_with(product_model)
        def get(self, product_id):
            """Get a product by ID"""
            product = next((p for p in products_db if p["id"] == product_id), None)
            if not product:
                api.abort(404, f"Product {product_id} not found")
            return product, 200
        
        @products_ns.doc('update_product')
        @products_ns.expect(product_input)
        @products_ns.marshal_with(product_model)
        def put(self, product_id):
            """Update a product"""
            product = next((p for p in products_db if p["id"] == product_id), None)
            if not product:
                api.abort(404, f"Product {product_id} not found")
            
            data = api.payload
            product.update(data)
            return product, 200
        
        @products_ns.doc('delete_product')
        def delete(self, product_id):
            """Delete a product"""
            global products_db
            products_db = [p for p in products_db if p["id"] != product_id]
            return "", 204
    
    api.add_namespace(products_ns, path="/api/products")
    
    @app.route("/")
    def health():
        """Health check"""
        return {"status": "API is running! Visit /swagger for docs"}, 200
    
    return app


if __name__ == "__main__":
    app = create_app()
    print("✓ Flask-RESTX auto-generating OpenAPI spec + Swagger UI!")
    print("   - Swagger UI:    http://localhost:5000/swagger")
    print("   - OpenAPI JSON:  http://localhost:5000/swagger.json")
    
    app.run(debug=True, port=5000)