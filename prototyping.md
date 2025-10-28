### Data models

- Order
    - id: str
    - products: dict[str, int] (product id and count)
    - status: OrderStatus
    - bill: str (refer to, by ID)
    - placed: DateTime
    - fulfilled: DateTime | None
    - paid: DateTime | None
    - total: float
    - payments: list[str] # payment id
    
- Bill
    - id: str
    - image: str (http url)

- Payment
    - id: str
    - date: DateTime
    - amount: float

- OrderStatus (can be an enum)
    - label: str
    - nice: str (maybe I don't need this?)

- Client
    - id: str (unique)
    - name: str
    - email: str
    - orders: OrderList

- Product
    - id: str
    - name: str
    - size: SizeLabel

- SizeLabel (enum)
    - name: str