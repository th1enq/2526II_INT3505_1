import "@typespec/http";

using TypeSpec.Http;

@service(#{
  title: "Product Management API"
})

namespace ProductAPI;

model ProductInput {
  @doc("Product name")
  name: string;

  @doc("Product price")
  price: float32;

  @doc("Product description")
  description?: string;
}

model Product {
  @doc("Product ID")
  id: int32;

  @doc("Product name")
  name: string;

  @doc("Product price")
  price: float32;

  @doc("Product description")
  description?: string;
}

@route("/api/products")
@tag("products")
interface Products {
  @get
  @summary("Get all products")
  listProducts(): Product[];

  @post
  @summary("Create a new product")
  createProduct(@body payload: ProductInput): {
    @statusCode _: 201;
    @body body: Product;
  };

  @route("/{product_id}")
  @get
  @summary("Get a product by ID")
  getProduct(@path product_id: int32): Product;

  @route("/{product_id}")
  @put
  @summary("Update a product")
  updateProduct(@path product_id: int32, @body payload: ProductInput): Product;

  @route("/{product_id}")
  @delete
  @summary("Delete a product")
  deleteProduct(@path product_id: int32): void;
}
