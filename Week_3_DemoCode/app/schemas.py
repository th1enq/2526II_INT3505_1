import marshmallow as ma


# ---------------------------------------------------------------------------
# User schemas
# ---------------------------------------------------------------------------

class UserSchema(ma.Schema):
    id     = ma.fields.Int(dump_only=True, metadata={"example": 1})
    name   = ma.fields.Str(required=True, metadata={"example": "Alice"})
    email  = ma.fields.Email(required=True, metadata={"example": "alice@example.com"})
    status = ma.fields.Str(
        load_default="active",
        validate=ma.validate.OneOf(["active", "inactive"]),
        metadata={"example": "active"},
    )


class UserQuerySchema(ma.Schema):
    status = ma.fields.Str(
        load_default=None,
        validate=ma.validate.OneOf(["active", "inactive"]),
    )
    sort  = ma.fields.Str(
        load_default=None,
        validate=ma.validate.OneOf(["id", "name", "email"]),
    )
    page  = ma.fields.Int(load_default=1,  validate=ma.validate.Range(min=1))
    limit = ma.fields.Int(load_default=10, validate=ma.validate.Range(min=1, max=100))


class PaginatedUsersSchema(ma.Schema):
    data  = ma.fields.List(ma.fields.Nested(UserSchema))
    page  = ma.fields.Int()
    limit = ma.fields.Int()
    total = ma.fields.Int()


# ---------------------------------------------------------------------------
# Order schemas
# ---------------------------------------------------------------------------

class OrderSchema(ma.Schema):
    id      = ma.fields.Int(dump_only=True, metadata={"example": 1})
    user_id = ma.fields.Int(required=True,  metadata={"example": 1})
    product = ma.fields.Str(required=True,  metadata={"example": "Laptop"})
    amount  = ma.fields.Float(required=True, metadata={"example": 1200.00})
    status  = ma.fields.Str(
        load_default="pending",
        validate=ma.validate.OneOf(["pending", "completed", "cancelled"]),
        metadata={"example": "pending"},
    )


class OrderQuerySchema(ma.Schema):
    status  = ma.fields.Str(
        load_default=None,
        validate=ma.validate.OneOf(["pending", "completed", "cancelled"]),
    )
    user_id = ma.fields.Int(load_default=None)
    sort    = ma.fields.Str(
        load_default=None,
        validate=ma.validate.OneOf(["id", "amount", "product"]),
    )
    page  = ma.fields.Int(load_default=1,  validate=ma.validate.Range(min=1))
    limit = ma.fields.Int(load_default=10, validate=ma.validate.Range(min=1, max=100))


class PaginatedOrdersSchema(ma.Schema):
    data  = ma.fields.List(ma.fields.Nested(OrderSchema))
    page  = ma.fields.Int()
    limit = ma.fields.Int()
    total = ma.fields.Int()
