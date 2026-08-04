---
type: srs-erd
feature: food-delivery
updated: 2026-07-14
---

# Food Delivery — ERD (Mermaid)

> Output `/erd`. Data model nhúng inline, kiểu gọn cho BA đọc. Tầng chi tiết hơn (kiểu DB thật + enum + index) xem `dbdiagram/food-delivery.dbml` (output `/dbdiagram`).

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    RESTAURANT ||--o{ ORDER : receives
    RESTAURANT ||--o{ MENU_ITEM : offers
    ORDER ||--|{ ORDER_LINE : contains
    MENU_ITEM ||--o{ ORDER_LINE : "listed in"
    ORDER ||--|| PAYMENT : "paid by"
    ORDER ||--o| DELIVERY : "delivered via"
    SHIPPER ||--o{ DELIVERY : handles
    ORDER ||--o{ REVIEW : "rated in"

    CUSTOMER {
        string id PK
        string name
        string phone
        string default_address
    }
    RESTAURANT {
        string id PK
        string name
        string address
        boolean is_open
    }
    MENU_ITEM {
        string id PK
        string restaurant_id FK
        string name
        int price
        boolean available
    }
    ORDER {
        string id PK
        string customer_id FK
        string restaurant_id FK
        string status
        int total_amount
        string payment_method
        datetime created_at
    }
    ORDER_LINE {
        string id PK
        string order_id FK
        string menu_item_id FK
        int quantity
        int line_total
    }
    PAYMENT {
        string id PK
        string order_id FK
        string status
        int amount
        string gateway_ref
    }
    DELIVERY {
        string id PK
        string order_id FK
        string shipper_id FK
        string status
        datetime picked_at
        datetime delivered_at
    }
    SHIPPER {
        string id PK
        string name
        string phone
        string vehicle
    }
    REVIEW {
        string id PK
        string order_id FK
        int rating
        string comment
    }
```
