# Ba lượt đọc, ba mục đích đọc, và phép tự kiểm tra hiểu

## Mục lục

1. Sáu đầu ra quan sát được của một phiên đọc tốt
2. Ba mục đích đọc
3. Ba lượt đọc (Keshav 2007, điều chỉnh)
4. Skimming - Scanning - Đọc sâu
5. Tự giải thích để kiểm tra hiểu

## 1. Sáu đầu ra quan sát được

Một phiên đọc đạt mục tiêu không nhất thiết phát hiện hướng mới; hiểu rõ một kỹ thuật nền tảng, chọn được baseline, hay nhận ra bài không phù hợp cũng là kết quả hợp lệ. Sau phiên đọc, người dùng cần:

1. Nêu bài toán và đóng góp chính bằng lời của mình (không chép abstract).
2. Tái dựng thành phần phương pháp/quy trình liên quan trực tiếp đến đề tài.
3. Chỉ ra căn cứ cụ thể (bảng, hình, phân tích độ phức tạp, định lý) cho các khẳng định trọng tâm.
4. Nhận diện giả định, điều kiện áp dụng, và những gì chưa được kiểm tra.
5. Phân biệt trong ghi chú: tác giả báo cáo / suy luận của người đọc / gợi ý của AI.
6. Xác định hành động tiếp theo (áp dụng thử, tra nền tảng, kiểm tra giả định, hay dừng đọc sâu).

Dùng danh sách này để đóng phiên: kiểm tra mục nào chưa đạt và nói thẳng với người dùng.

## 2. Ba mục đích đọc

| Mục đích     | Trọng tâm                                                                                                               | Lưu ý                                                                                         |
| ------------ | ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **Học**      | Khái niệm, định nghĩa, nguyên lý thuật toán, kiến trúc, cách cộng đồng đóng khung bài toán                              | Người mới vào chủ đề: ưu tiên tái dựng đúng và bổ sung nền, đừng ép phê bình hay tìm gap ngay |
| **Đánh giá** | Độ vững của khẳng định; liên hệ giả định - phương pháp - bằng chứng; phạm vi hiệu lực                                   | Cần `evaluation.md`                                                                           |
| **Sử dụng**  | Trích và kiểm tra thành phần dùng trực tiếp: baseline, benchmark, hàm mất mát, quy trình đo, định vị câu hỏi nghiên cứu | Chi tiết triển khai (tham số, tiền xử lý) trở nên quan trọng                                  |

Câu mục đích mẫu: "Trong phiên đọc này, tôi đọc bài X với mục đích chính là [Học/Đánh giá/Sử dụng] nhằm làm rõ: [câu hỏi cụ thể]." Hẹp tốt hơn rộng: không "tìm hiểu về phát hiện đối tượng" mà "học nguyên lý tính đặc trưng nhanh bằng ảnh tích phân và cách nó giảm chi phí".

Tách riêng hai nhận định trong ghi chú: **(1)** lập luận/căn cứ thuyết phục đến đâu, **(2)** có phục vụ mục tiêu hiện tại không.

## 3. Ba lượt đọc

| Lượt                        | Làm gì                                                                                                                                               | Thời gian dự kiến\*  | Kết thúc bằng                                                                      |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- | ---------------------------------------------------------------------------------- |
| **1 - Định hướng**          | Tiêu đề, Abstract, phần đóng góp trong Intro, tiêu đề các mục, hình/bảng chính, Conclusion                                                           | ~5-10 phút           | Quyết định: (a) dừng/lưu tra cứu (b) đọc chọn lọc (c) Lượt 2 (d) bổ sung nền trước |
| **2 - Phân tích**           | Tái dựng bài toán, ý tưởng giải pháp, giả định, cấu trúc phương pháp, mạch lập luận; đọc kỹ Methods và Results; có thể hoãn chứng minh dài ở phụ lục | tùy độ khó           | Bản tái dựng (bảng 7 thành phần) có nhãn, danh sách điểm chưa rõ                   |
| **3 - Thẩm định & sử dụng** | Kiểm tra căn cứ chi tiết của khẳng định trọng tâm; tự giải thích cơ chế; đối sánh các bài; quyết định cho nghiên cứu cá nhân                         | dành cho bài cốt lõi | Nhận định cân bằng + hành động tiếp theo                                           |

\*Thời gian chỉ là ngân sách linh hoạt, không phải thước đo năng lực. Có thể xen kẽ trạng thái tập trung chi tiết (focused) và khoảng nghỉ ngắn để xâu chuỗi bức tranh (diffuse).

Khung tư duy được huy động theo lượt: 5W1H (Lượt 1 và đầu Lượt 2), Tư duy máy tính (Lượt 2), Socratic và câu hỏi phân biệt (Lượt 2-3), tự giải thích (Lượt 3).

5W1H cho bài báo: What (bài toán, đối tượng đề xuất, đóng góp, kết quả) · Why (vì sao đáng quan tâm, vì sao chọn hướng này) · Who (dữ liệu/hệ thống gắn với đối tượng nào, so với phương pháp nào) · Where (miền dữ liệu, môi trường, cấu hình kiểm tra) · When (điều kiện phương pháp hoạt động tốt, khi nào kết quả đổi) · How (vận hành, triển khai, kiểm tra bằng quy trình nào). Không ép mọi bài có câu trả lời dài ngang nhau cho cả sáu.

## 4. Skimming - Scanning - Đọc sâu

- **Skimming:** nắm bài toán, loại đóng góp, bố cục, mức liên quan.
- **Scanning:** tìm vị trí một chi tiết cụ thể (kích thước ảnh đầu vào, cấu hình phần cứng, định nghĩa ký hiệu, chú thích bảng). Sau khi định vị vẫn phải đọc kỹ đoạn quanh nó.
- **Đọc sâu:** theo dõi mạch lập luận, kiểm tra biến đổi công thức, phân tích thiết kế thực nghiệm, xác định phạm vi kết luận.
- Scanning cho biết "thông tin nằm ở đâu"; chỉ đọc sâu mới trả lời "nó có nghĩa gì và được căn cứ nào hỗ trợ".

## 5. Tự giải thích để kiểm tra hiểu

Dấu hiệu cần kiểm tra thêm: người đọc chỉ lặp lại nguyên văn thuật ngữ của tác giả mà không diễn đạt lại được nguyên lý. Quy trình: (1) gấp bài và ghi chú, giải thích ngắn bài toán + ý chính + cách tác giả kiểm tra; (2) ghi chỗ lúng túng; (3) mở lại đúng vị trí, ưu tiên điểm ảnh hưởng mục tiêu đọc. Khi hỗ trợ: chỉ đặt 1-2 câu hỏi gợi mở tại chỗ mơ hồ, chưa viết hộ bản hoàn chỉnh.
