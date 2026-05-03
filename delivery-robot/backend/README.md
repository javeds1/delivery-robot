# Campus Delivery Robot Backend

Initial backend scaffold for the campus delivery robot project using:

- Django
- Django REST Framework
- Django Channels
- PostgreSQL
- Redis
- JWT authentication

## Project structure

- `config/` Django project settings, ASGI, URLs
- `apps/accounts/` custom user model and profile endpoints
- `apps/vendors/` vendor management
- `apps/menu/` menu item management
- `apps/orders/` order APIs and order lifecycle
- `apps/dispatch/` mock robot dispatch records
- `apps/mock_delivery/` temporary high-fidelity mock delivery API
- `apps/notifications/` WebSocket consumer for live order updates

## Setup for Supabase

1. Create a virtual environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your Supabase database host and password.
4. Start Redis locally:
   `docker compose up -d`
5. Run migrations against Supabase PostgreSQL:
   `python manage.py makemigrations`
   `python manage.py migrate`
6. Create an admin user:
   `python manage.py createsuperuser`
7. Start the server:
   `python manage.py runserver`

## Supabase values to copy

Get these from your Supabase project database settings:

- `POSTGRES_HOST`
- `POSTGRES_PASSWORD`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`

Keep `POSTGRES_SSLMODE=require` for Supabase.

If Supabase gives you a pooler URL like:
`postgresql://postgres.project-ref:[YOUR-PASSWORD]@aws-1-us-west-2.pooler.supabase.com:6543/postgres`

then use:

```env
POSTGRES_DB=postgres
POSTGRES_USER=postgres.project-ref
POSTGRES_PASSWORD=your-supabase-db-password
POSTGRES_HOST=aws-1-us-west-2.pooler.supabase.com
POSTGRES_PORT=6543
POSTGRES_SSLMODE=require
```

## Key API routes

- `GET /api/health/`
- `POST /api/auth/token/`
- `GET /api/accounts/me/`
- `GET|POST /api/vendors/`
- `GET|POST /api/menu/items/`
- `GET|POST /api/orders/`
- `POST /api/orders/<id>/status/`
- `GET /api/dispatch/`
- `GET /api/mock-delivery/robots`
- `GET|POST /api/mock-delivery/orders`
- `GET /api/mock-delivery/orders/<orderId>`
- `POST /api/mock-delivery/orders/<orderId>/cancel`
- `POST /api/mock-delivery/orders/<orderId>/close`
- `POST /api/mock-delivery/orders/<orderId>/open`
- `POST /api/mock-delivery/orders/<orderId>/ready`
- `POST /api/mock-delivery/orders/<orderId>/return-to-pickup`
- `GET /api/mock-delivery/user`

## Temporary mock delivery toggles

Use these env vars for plug-and-play switching:

```env
DISPATCH_PROVIDER=mock
MOCK_DELIVERY_ENABLED=true
MOCK_DELIVERY_STATE_MODE=deterministic
```

- `DISPATCH_PROVIDER`: `mock` routes dispatch flow to temporary provider; `real` keeps a placeholder adapter path ready for real API hookup.
- `MOCK_DELIVERY_ENABLED`: disables/enables order creation endpoints without removing routes.
- `MOCK_DELIVERY_STATE_MODE`: `deterministic` keeps stable order states, `timed` auto-progresses state transitions for async testing.

## Mock Delivery API schemas and examples

Base prefix: `/api/mock-delivery`

### Shared schemas

`CreateInput` (POST `/orders` request)

```json
{
  "id": "ddf6f55b-e8e7-463a-bf71-0fa33711d833",
  "extId": "order-123",
  "robot": "robot-1",
  "clientName": "John Doe",
  "phone": "+15555551234",
  "email": "john@example.com",
  "webhook": "https://example.com/updateOrder",
  "scheduledPickUp": "2026-04-25T16:30:00Z",
  "src": {
    "lat": 30.3414,
    "lon": -97.6768,
    "address": "123 Main St, Austin, TX"
  },
  "dst": {
    "lat": 30.3422,
    "lon": -97.6759,
    "address": "Engineering Building"
  }
}
```

`Orders` (GET `/orders` response)

```json
{
  "orders": [
    {
      "id": "ddf6f55b-e8e7-463a-bf71-0fa33711d833",
      "extId": "order-123",
      "src": {
        "lat": 30.3414,
        "lon": -97.6768,
        "address": "123 Main St, Austin, TX",
        "extId": ""
      },
      "dst": {
        "lat": 30.3422,
        "lon": -97.6759,
        "address": "Engineering Building",
        "extId": ""
      },
      "scheduledPickUp": "2026-04-25T16:30:00Z",
      "request": {
        "src": { "address": "123 Main St, Austin, TX" },
        "dst": { "address": "Engineering Building" },
        "clientName": "John Doe"
      },
      "createdAt": "2026-04-25T16:20:00Z",
      "status": "accepted",
      "ready": true,
      "eta": {
        "pickUp": "2026-04-25T16:30:00Z",
        "dropOff": "2026-04-25T16:42:00Z",
        "return": "2026-04-25T16:50:00Z"
      },
      "robots": [
        {
          "name": "robot-1",
          "position": { "lat": 30.3414, "lon": -97.6768, "yaw": 90.0 },
          "route": [
            { "lat": 30.3414, "lon": -97.6768 },
            { "lat": 30.3422, "lon": -97.6759 }
          ],
          "deliveringOtherOrders": false
        }
      ]
    }
  ]
}
```

`Robots` (GET `/robots` response)

```json
{
  "robots": [
    {
      "name": "robot-1",
      "position": { "lat": 30.3414, "lon": -97.6768, "yaw": 90.0 },
      "route": [
        { "lat": 30.3414, "lon": -97.6768 },
        { "lat": 30.3422, "lon": -97.6759 }
      ],
      "deliveringOtherOrders": false
    }
  ]
}
```

`UIUser` (GET `/user` response)

```json
{
  "firstName": "Jane",
  "lastName": "Vendor",
  "login": "mock_delivery_vendor",
  "email": "vendor@example.com",
  "roles": ["vendor"],
  "partnerId": "mock-partner",
  "features": {
    "adminOperations": true,
    "basicOperations": true,
    "cancelOrder": true,
    "createOrder": true,
    "dropOffOrder": true,
    "loadOrder": true,
    "manageOrder": true,
    "returnToPickUp": true,
    "viewOrder": true,
    "viewRobots": true
  },
  "config": {
    "dispatchRadius": 10.0,
    "countryCode": "US",
    "omitPhone": false,
    "newOrderSound": true,
    "predefinedOrders": []
  }
}
```

`ErrorModel` (example)

```json
{
  "type": "about:blank",
  "title": "Not Found",
  "status": 404,
  "detail": "Order not found."
}
```

### Endpoints with sample requests and responses

#### `GET /api/mock-delivery/orders`

Query params:
- `robot` (optional string)
- `only_active` (optional boolean)

Example request:

```http
GET /api/mock-delivery/orders?robot=robot-1&only_active=true
Authorization: Bearer <token>
```

Example `200` response: see `Orders` schema above.

#### `POST /api/mock-delivery/orders`

Example request body: see `CreateInput` schema above.

Example `201` response: one `OrderState` object (same item shape as `orders[]`).

Example `503` response:

```json
{
  "type": "about:blank",
  "title": "Service Unavailable",
  "status": 503,
  "detail": "Mock delivery endpoints are disabled."
}
```

#### `GET /api/mock-delivery/orders/<orderId>`

Example request:

```http
GET /api/mock-delivery/orders/ddf6f55b-e8e7-463a-bf71-0fa33711d833
Authorization: Bearer <token>
```

Example `200` response: one `OrderState` object.

Example `404` response: see `ErrorModel`.

#### `POST /api/mock-delivery/orders/<orderId>/cancel`

Example request:

```http
POST /api/mock-delivery/orders/ddf6f55b-e8e7-463a-bf71-0fa33711d833/cancel
Authorization: Bearer <token>
```

Example `200` response (excerpt):

```json
{
  "id": "ddf6f55b-e8e7-463a-bf71-0fa33711d833",
  "status": "canceled"
}
```

#### `POST /api/mock-delivery/orders/<orderId>/close`

Example request:

```http
POST /api/mock-delivery/orders/ddf6f55b-e8e7-463a-bf71-0fa33711d833/close
Authorization: Bearer <token>
```

Example `200` response (excerpt):

```json
{
  "id": "ddf6f55b-e8e7-463a-bf71-0fa33711d833",
  "status": "dropOffTransaction"
}
```

#### `POST /api/mock-delivery/orders/<orderId>/open`

Example request:

```http
POST /api/mock-delivery/orders/ddf6f55b-e8e7-463a-bf71-0fa33711d833/open
Authorization: Bearer <token>
```

Example `200` response (excerpt):

```json
{
  "id": "ddf6f55b-e8e7-463a-bf71-0fa33711d833",
  "status": "pickUpTransaction"
}
```

#### `POST /api/mock-delivery/orders/<orderId>/ready`

Example request:

```http
POST /api/mock-delivery/orders/ddf6f55b-e8e7-463a-bf71-0fa33711d833/ready
Authorization: Bearer <token>
```

Example `200` response (excerpt):

```json
{
  "id": "ddf6f55b-e8e7-463a-bf71-0fa33711d833",
  "status": "accepted",
  "ready": true
}
```

#### `POST /api/mock-delivery/orders/<orderId>/return-to-pickup`

Example request:

```http
POST /api/mock-delivery/orders/ddf6f55b-e8e7-463a-bf71-0fa33711d833/return-to-pickup
Authorization: Bearer <token>
```

Example `200` response (excerpt):

```json
{
  "id": "ddf6f55b-e8e7-463a-bf71-0fa33711d833",
  "status": "returnTransporting"
}
```

#### `GET /api/mock-delivery/robots`

Example request:

```http
GET /api/mock-delivery/robots
Authorization: Bearer <token>
```

Example `200` response: see `Robots` schema above.

#### `GET /api/mock-delivery/user`

Example request:

```http
GET /api/mock-delivery/user
Authorization: Bearer <token>
```

Example `200` response: see `UIUser` schema above.

### Avride schema parity matrix (required + nullable)

This is a compact, implementation-facing map from `avride_api_sample.yaml`.

| Schema | Required fields | Nullable fields (`null` allowed) | Notes |
| --- | --- | --- | --- |
| `CreateInput` | `id`, `dst` | none | `src`/`dst` can be either `{lat,lon[,address]}` or `{extId}` |
| `OrderPoint` | `lat`, `lon` | none | Optional `address`, `extId` |
| `OrderRequestPoint` | `address` | `address` | Used under `request.src` and `request.dst` |
| `OrderRequest` | `src`, `dst` | none | Optional `clientName` |
| `ETA` | none | none | Fields: `pickUp`, `dropOff`, `return` |
| `Position` | `yaw`, `lat`, `lon` | none | `yaw` in `[-180, 180]` in sample |
| `RobotState` | `name`, `position`, `route`, `deliveringOtherOrders` | `route` | `route` is array of `LatLon` or `null` |
| `OrderState` | `id`, `extId`, `src`, `dst`, `scheduledPickUp`, `request`, `createdAt`, `status`, `ready`, `eta`, `robots` | `extId`, `robots` | `status` enum includes `new`..`returnCompleted` + `canceled` |
| `Orders` | `orders` | `orders` | Top-level response for list orders |
| `Robots` | `robots` | `robots` | Top-level response for list robots |
| `ExternalFeatures` | none | none | Boolean capability flags |
| `UIConfig` | `dispatchRadius`, `countryCode`, `omitPhone`, `newOrderSound` | `dispatchRadius`, `predefinedOrders` | `predefinedOrders` is optional and nullable |
| `UIUser` | `firstName`, `lastName`, `login`, `email`, `roles`, `partnerId`, `features` | `firstName`, `lastName`, `roles` | `config` present in sample schema, not marked required |
| `ErrorModel` | none | `errors` | RFC7807-style fields: `type`, `title`, `status`, `detail`, etc. |

### Endpoint to schema map

| Endpoint | Request schema | Success response schema |
| --- | --- | --- |
| `GET /api/mock-delivery/orders` | query only (`robot`, `only_active`) | `Orders` |
| `POST /api/mock-delivery/orders` | `CreateInput` | `OrderState` (`201`) |
| `GET /api/mock-delivery/orders/<orderId>` | path `orderId` | `OrderState` |
| `POST /api/mock-delivery/orders/<orderId>/cancel` | path `orderId` | `OrderState` |
| `POST /api/mock-delivery/orders/<orderId>/close` | path `orderId` | `OrderState` |
| `POST /api/mock-delivery/orders/<orderId>/open` | path `orderId` | `OrderState` |
| `POST /api/mock-delivery/orders/<orderId>/ready` | path `orderId` | `OrderState` |
| `POST /api/mock-delivery/orders/<orderId>/return-to-pickup` | path `orderId` | `OrderState` |
| `GET /api/mock-delivery/robots` | none | `Robots` |
| `GET /api/mock-delivery/user` | none | `UIUser` |

## Deploy on Render (Django Admin CSS)

With `DJANGO_DEBUG=False`, Django does not serve `/static/` by itself. The admin relies on CSS/JS under `/static/admin/`. This project uses **[WhiteNoise](https://github.com/evansd/whitenoise)** to serve collected static files in production.

1. Ensure the **Render build** runs collectstatic after installing dependencies:

   ```bash
   pip install -r requirements.txt && python manage.py collectstatic --noinput
   ```

2. Set env vars including your Render hostname, for example:

   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS=your-service.onrender.com`

3. Redeploy. Open `/admin/` again; styles should load.

If admin is still unstyled, check the browser Network tab for `/static/admin/…` URLs (404 means collectstatic did not run in the build step, or `STATIC_ROOT` is not persisted in the slug that runs gunicorn/uvicorn).

## WebSocket

- `ws://localhost:8000/ws/orders/`

## Suggested next step

Connect the existing admin, user, and vendor frontends to these APIs and then add role-based permissions and a real robot provider adapter.
