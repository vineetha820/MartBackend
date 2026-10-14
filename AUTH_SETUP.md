# Mart accounts

All login accounts use the custom `users.User` model in `users_user`.
The sole product administrator is `vineetha@gmail.com`, user ID 1.
`PRODUCT_ADMIN_USER_ID` in settings identifies that account. It must also
be active and staff. Other staff, superusers, customers and legacy sellers
cannot create, edit or delete products through the API or Django admin.

Public registration at `POST /users/register/` creates customers only:

```json
{"email": "customer@example.com", "password": "your-strong-password"}
```

An optional `account_type` must be `customer`. Seller/admin registration is
rejected. Staff and superuser flags cannot be granted through this endpoint.
The former seller tables are retained for compatibility but are not used to
grant permissions, and seller registration is disabled.

Login with email and password at `/users/login/`. The response includes JWT
tokens and `user.can_manage_products`; use this flag to show product-management
controls in the frontend. The backend enforces the same permission on every
write. Send `Authorization: Bearer <access-token>` with authenticated requests.
The designated admin can also use `/admin/` with the same credentials.

The product API is `/products/products/` and `/products/products/<id>/`.
Anyone can browse products. The backend assigns `created_by` to the designated
admin on creation and preserves it when editing.

Customers place orders with `POST /orders/` and see their own orders with
`GET /orders/`. Example:

```json
{
  "recipient_name": "Customer Name",
  "phone": "1234567890",
  "shipping_address": "Delivery address",
  "items": [{"product": 1, "quantity": 2}]
}
```

Prices and totals come from stored products. Payment collection is not
implemented by these endpoints.

## Product catalogue and local data

`/products/` and `/products/<id>/` are also available; the older
`/products/products/` routes remain supported. Product lists are paginated
(two per page). Use `search`, `name__icontains`, `price__lt`, `price__gt`,
or `price__range` to filter the catalogue. Products expose `in_stock`.

After pulling, install `requirements.txt` and run `manage.py migrate`.
SQLite databases and Python bytecode are local files and are not tracked.
The database snapshots from the merge are retained locally as
`db.merge-local.sqlite3` and `db.merge-remote.sqlite3`; their records were
not combined. The active database retains the local authentication setup.
