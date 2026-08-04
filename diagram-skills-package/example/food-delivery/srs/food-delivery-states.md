---
type: srs-states
feature: food-delivery
updated: 2026-07-14
---

# Food Delivery — Sơ đồ trạng thái (State diagrams)

> Output `/state`. Mỗi entity một section `## State: {Entity}`.

---

## State: Order (Đơn hàng)

```mermaid
stateDiagram-v2
    [*] --> PendingPayment: Khách đặt món
    PendingPayment --> Paid: Thu tiền thành công
    PendingPayment --> Cancelled: Thanh toán thất bại / khách hủy
    Paid --> RestaurantAccepted: Nhà hàng nhận đơn
    Paid --> Refunding: Nhà hàng từ chối / hết shipper
    RestaurantAccepted --> Preparing: Bắt đầu chuẩn bị
    Preparing --> ReadyForPickup: Món xong
    ReadyForPickup --> Delivering: Shipper lấy món
    Delivering --> Delivered: Khách nhận món
    Delivering --> DeliveryFailed: Giao thất bại
    DeliveryFailed --> Refunding: CSKH duyệt hoàn tiền
    Refunding --> Refunded: Đã hoàn tiền
    Delivered --> [*]
    Refunded --> [*]
    Cancelled --> [*]

    note right of Refunding
        Chỉ hoàn khi đã thu tiền online.
        Đơn COD hủy → không hoàn.
    end note
```

---

## State: Payment (Giao dịch thanh toán)

```mermaid
stateDiagram-v2
    [*] --> Initiated: Tạo giao dịch
    Initiated --> Authorized: Cổng xác nhận giữ tiền
    Initiated --> Failed: Thẻ từ chối / timeout
    Authorized --> Captured: Nhà hàng nhận đơn (thu thật)
    Authorized --> Voided: Đơn hủy trước khi thu
    Captured --> Refunded: Hoàn tiền toàn phần
    Captured --> PartiallyRefunded: Hoàn một phần (giao thiếu món)
    Failed --> [*]
    Voided --> [*]
    Refunded --> [*]
    PartiallyRefunded --> [*]
```
