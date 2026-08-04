---
type: srs-flows
feature: food-delivery
updated: 2026-07-14
---

# Food Delivery — Sơ đồ luồng (Sequence + Activity)

> Bản mẫu do bộ **diagram-skills** sinh ra. Mỗi flow một section. Sequence diagram (output `/sequence`) và activity/flowchart (output `/activity`) cùng sống trong file này — theo quy ước `srs/{feature}-flows.md`.
>
> **Bối cảnh nghiệp vụ (dùng chung cho mọi diagram trong bộ example):** Ứng dụng đặt & giao đồ ăn. 4 vai trò: **Khách** đặt món, **Nhà hàng** xác nhận + chuẩn bị, **Shipper** nhận + giao, **Hệ thống** điều phối + tính tiền + gọi cổng thanh toán. Các nhánh khó: nhà hàng từ chối, hết shipper, khách hủy, giao thất bại, hoàn tiền.

---

## Flow: Đặt món và thanh toán (happy + error) — Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Khach as Khách
    participant App as Ứng dụng
    participant NH as Nhà hàng
    participant PG as Cổng thanh toán
    participant Ship as Shipper

    Khach->>App: Chọn món + địa chỉ giao
    App->>App: Tính phí món + phí ship + khuyến mãi
    App-->>Khach: Hiển thị tổng tiền
    Khach->>App: Xác nhận đặt + chọn thanh toán online

    App->>PG: Tạo giao dịch thanh toán
    alt Thanh toán thành công
        PG-->>App: Xác nhận đã thu tiền (webhook)
        App->>NH: Gửi đơn mới
        alt Nhà hàng xác nhận
            NH-->>App: Đã nhận, bắt đầu chuẩn bị
            App->>Ship: Tìm shipper gần nhất
            Ship-->>App: Nhận cuốc
            App-->>Khach: Đơn đã được nhận, đang chuẩn bị
        else Nhà hàng từ chối / quá 5 phút không phản hồi
            NH-->>App: Từ chối (hết món)
            App->>PG: Yêu cầu hoàn tiền
            PG-->>App: Đã hoàn tiền
            App-->>Khach: Xin lỗi, nhà hàng không nhận đơn — đã hoàn tiền
        end
    else Thanh toán thất bại
        PG-->>App: Từ chối (thẻ không đủ số dư)
        App-->>Khach: Thanh toán thất bại, thử lại
    end
```

---

## Flow: Giao hàng và xác nhận (happy + giao thất bại) — Sequence

```mermaid
sequenceDiagram
    autonumber
    participant App as Ứng dụng
    participant Ship as Shipper
    actor Khach as Khách
    participant NH as Nhà hàng

    NH-->>App: Món đã sẵn sàng
    App->>Ship: Thông báo tới lấy món
    Ship->>NH: Tới lấy món
    NH-->>Ship: Giao món cho shipper
    Ship-->>App: Đã lấy món, đang giao
    App-->>Khach: Shipper đang trên đường (theo dõi bản đồ)

    Ship->>Khach: Tới nơi giao món
    alt Giao thành công
        Khach-->>Ship: Nhận món
        Ship-->>App: Xác nhận đã giao
        App-->>Khach: Hoàn tất — mời đánh giá
    else Không liên lạc được khách (3 lần trong 10 phút)
        Ship-->>App: Báo giao thất bại
        App->>NH: Ghi nhận đơn giao lỗi
        App-->>Khach: Giao thất bại — liên hệ CSKH để xử lý
    end
```

---

## Flow: Xử lý đơn hàng đầu-cuối (Activity / flowchart)

```mermaid
flowchart TD
    A([Khách đặt món]) --> B[Tính tổng tiền]
    B --> C{Thanh toán online?}
    C -->|Có| D[Gọi cổng thanh toán]
    C -->|COD| E[Bỏ qua thanh toán trước]
    D --> F{Thu tiền OK?}
    F -->|Không| G([Kết thúc: báo thất bại]):::stop
    F -->|Có| H[Gửi đơn tới nhà hàng]
    E --> H
    H --> I{Nhà hàng nhận đơn trong 5 phút?}
    I -->|Không| J[Hoàn tiền nếu đã thu]
    J --> K([Kết thúc: hủy đơn]):::stop
    I -->|Có| L[Nhà hàng chuẩn bị món]
    L --> M[Tìm & gán shipper]
    M --> N{Có shipper nhận?}
    N -->|Không trong 15 phút| J
    N -->|Có| O[Shipper lấy món & giao]
    O --> P{Giao thành công?}
    P -->|Không| Q[Chuyển CSKH xử lý / hoàn tiền]
    Q --> R([Kết thúc: giao lỗi]):::stop
    P -->|Có| S[Khách nhận món]
    S --> T{Thanh toán COD?}
    T -->|Có| U[Shipper thu tiền mặt]
    T -->|Không| V[Ghi nhận đã thanh toán online]
    U --> W([Hoàn tất đơn]):::done
    V --> W

    classDef stop fill:#fde,stroke:#c33;
    classDef done fill:#dfd,stroke:#3a3;
```
