import marshmallow as ma


class BookSchema(ma.Schema):
    id = ma.fields.Int(dump_only=True, metadata={"example": 1})
    title = ma.fields.Str(required=True, metadata={"example": "Clean Architecture"})
    author = ma.fields.Str(required=True, metadata={"example": "Robert C. Martin"})
    isbn = ma.fields.Str(required=True, metadata={"example": "9780134494166"})
    published_year = ma.fields.Int(required=True, metadata={"example": 2017})
    genre = ma.fields.Str(required=True, metadata={"example": "Software Engineering"})
    price = ma.fields.Float(required=True, metadata={"example": 45.5})
    stock = ma.fields.Int(required=True, validate=ma.validate.Range(min=0), metadata={"example": 20})
    in_stock = ma.fields.Bool(dump_only=True, metadata={"example": True})


class BookQuerySchema(ma.Schema):
    author = ma.fields.Str(load_default=None)
    genre = ma.fields.Str(load_default=None)
    in_stock = ma.fields.Bool(load_default=None)
    min_price = ma.fields.Float(load_default=None, validate=ma.validate.Range(min=0))
    max_price = ma.fields.Float(load_default=None, validate=ma.validate.Range(min=0))
    sort = ma.fields.Str(
        load_default=None,
        validate=ma.validate.OneOf(["id", "title", "author", "price", "published_year"]),
    )
    page = ma.fields.Int(load_default=1, validate=ma.validate.Range(min=1))
    limit = ma.fields.Int(load_default=10, validate=ma.validate.Range(min=1, max=100))


class PaginatedBooksSchema(ma.Schema):
    data = ma.fields.List(ma.fields.Nested(BookSchema))
    page = ma.fields.Int()
    limit = ma.fields.Int()
    total = ma.fields.Int()
