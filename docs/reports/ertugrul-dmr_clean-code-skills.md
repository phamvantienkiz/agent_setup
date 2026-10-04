# Báo Cáo Phân Tích Tinh Túy Clean Code: `ertugrul-dmr/clean-code-skills`

- **Tên kho lưu trữ**: `ertugrul-dmr/clean-code-skills`
- **Định dạng**: Agent Skills (Google Antigravity, Anthropic Claude Code, Agent Skills open standard)
- **Giấy phép**: MIT License
- **Đường dẫn phân tích**: [ertugrul-dmr_clean-code-skills](file:///E:/gemini/agent_setup/ertugrul-dmr_clean-code-skills)

---

## 1. Tổng Quan & Động Lực Phát Triển (Motivation)

Kho lưu trữ `ertugrul-dmr/clean-code-skills` tiếp cận vấn đề nợ kỹ thuật (Technical Debt) do AI tạo ra thông qua các nghiên cứu định lượng thực tế:
- **GitClear (2024)**: Mức độ trùng lặp mã nguồn (Code Duplication) tăng gấp **4 lần** kể từ khi các công cụ AI lập trình bùng nổ.
- **Carnegie Mellon University**: Cảnh báo phân tích tĩnh tăng **+30%**, độ phức tạp mã nguồn (Code Complexity) tăng **+41%** sau khi lập trình viên sử dụng AI hỗ trợ.
- **Google DORA Report**: Ghi nhận mối tương quan tiêu cực giữa việc lạm dụng AI không kiểm soát và sự ổn định trong bàn giao phần mềm.

Để giải quyết tận gốc vấn đề này, tác giả đã mã hóa toàn bộ **66 nguyên tắc kinh điển trong cuốn sách *Clean Code* của Robert C. Martin (Uncle Bob)** thành các Agent Skills có thể tự kích hoạt hoặc chỉ định trực tiếp cho AI.

---

## 2. Kiến Trúc Tổ Chức: Phân Tuyến Ngôn Ngữ & Progressive Disclosure

Repo áp dụng mô hình tổ chức phân tuyến ngôn ngữ (Language Tracks):
```
skills/
├── python/
│   ├── boy-scout/          # Orchestrator: Điều phối dọn dẹp liên tục
│   ├── python-clean-code/  # Master Skill: Chứa trọn vẹn 66 quy tắc cho Python
│   ├── clean-comments/     # Quy tắc bình luận (C1-C5)
│   ├── clean-functions/    # Quy tắc hàm gọn gàng, rõ ràng (F1-F4)
│   ├── clean-general/      # Nguyên tắc thiết kế cốt lõi (DRY, SRP)
│   ├── clean-names/        # Đặt tên sáng sủa, không mơ hồ (N1-N7)
│   └── clean-tests/        # Kiểm thử nhanh, bao quát biên (T1-T9)
└── typescript/
    ├── boy-scout/          # Orchestrator cho TS
    ├── typescript-clean-code/ # Master Skill cho TypeScript (66 quy tắc + TS1-TS3)
    ├── clean-comments/
    ├── clean-functions/
    ├── clean-general/
    ├── clean-names/
    └── clean-tests/
```

### Cơ chế Progressive Disclosure (Tiết lộ dần thông tin)
- **Khám phá (Discovery)**: Agent ban đầu chỉ thấy `name` và `description` của skill, tiêu tốn rất ít token ngữ cảnh.
- **Kích hoạt (Activation)**: Khi người dùng yêu cầu viết code, review hoặc refactor, chỉ những skill tương ứng mới được nạp vào context.
- **Lưu ý quan trọng**: Tác giả khuyến cáo **chỉ cài đặt một tuyến ngôn ngữ (Python HOẶC TypeScript) vào một thư mục skills** để tránh xung đột tên skill (`boy-scout`, `clean-names`...).

---

## 3. Tinh Túy Cốt Lõi: The Boy Scout Rule (Quy Tắc Hướng Đạo Sinh)

Triết lý trung tâm chi phối toàn bộ repo là **Boy Scout Rule**:
> *"Always check a module in cleaner than when you checked it out."*  
> *(Luôn để lại module code sạch hơn một chút so với lúc bạn mở nó ra).*

- **Không cần hoàn hảo ngay lập tức**: Việc tái cấu trúc toàn diện (Big-Bang Rewrite) tiềm ẩn nhiều rủi ro. Thay vào đó, mỗi lần AI chạm vào một file để sửa lỗi hoặc thêm tính năng, nó bắt buộc phải thực hiện 1-2 cải tiến nhỏ:
  - Đổi một tên biến tối nghĩa thành tên rõ ý định.
  - Tách một hàm phụ từ đoạn code lồng nhau.
  - Xóa bỏ một comment thừa hoặc code bị comment-out.
  - Thay thế magic number bằng một hằng số có tên.

---

## 4. Hệ Thống 66 Quy Tắc Clean Code Chuẩn Hóa (Heuristics Index)

Repo phân loại toàn bộ các quy tắc theo hệ thống ký hiệu chuẩn từ Chương 17 của sách Clean Code:

### 1. Bình luận (Comments: C1 - C5)
- **C1**: Không để lại metadata trong comment (hãy dùng Git blame/log).
- **C2**: Xóa bỏ comment lỗi thời ngay lập tức.
- **C3**: Không viết comment lặp lại những gì code đã thể hiện rõ ràng.
- **C4**: Nếu bắt buộc phải viết comment, hãy viết thật súc tích và chuẩn xác.
- **C5**: **Tuyệt đối không commit code bị comment-out** (hãy xóa đi, Git sẽ lưu lịch sử).

### 2. Hàm (Functions: F1 - F4)
- **F1**: Tối đa 3 tham số (nhiều hơn phải gom thành Object/DTO/Dataclass).
- **F2**: Không dùng Output arguments (hàm phải trả về kết quả qua return).
- **F3**: **Không dùng Flag arguments** (`flag=True/False` rẽ nhánh logic bên trong; hãy tách thành 2 hàm riêng biệt).
- **F4**: Xóa ngay các dead functions không còn nơi nào gọi.

### 3. Nguyên tắc chung (General: G1 - G36)
- **G5 (DRY)**: Tuyệt đối không duplicate logic.
- **G6 / G34**: Một mức độ trừu tượng nhất quán trên mỗi hàm (SLAP).
- **G7**: Base class không được biết thông tin của class con.
- **G8**: Thu hẹp tối đa public interface.
- **G9 / G12**: Dọn sạch dead code và clutter.
- **G10**: Khai báo biến gần nơi sử dụng nhất.
- **G13 / G14**: Tránh Artificial Coupling và Feature Envy (hàm dùng dữ liệu của class khác nhiều hơn class mình).
- **G23**: **Polymorphism over if/else**: Dùng tính đa hình thay cho hàng loạt câu lệnh `if/elif/switch` phức tạp.
- **G25**: Dùng hằng số có tên, không dùng magic numbers.
- **G28 / G29**: Đóng gói điều kiện phức tạp vào hàm boolean rõ nghĩa; tránh điều kiện phủ định kép.
- **G30**: Mỗi hàm chỉ làm DUY NHẤT một việc.
- **G36 (Law of Demeter)**: Nguyên tắc một dấu chấm — chỉ nói chuyện với bạn bè thân thiết, không gọi xuyên chuỗi đối tượng (`a.getB().getC().doSomething()`).

### 4. Đặt tên (Names: N1 - N7)
- **N1**: Chọn tên bộc lộ ý định (Descriptive names).
- **N2**: Tên ở đúng tầng trừu tượng.
- **N3**: Dùng thuật ngữ tiêu chuẩn của domain.
- **N4**: Tên không được mơ hồ, nước đôi.
- **N5**: Chiều dài của tên tương ứng với phạm vi (scope) của biến.
- **N6**: Không mã hóa kiểu dữ liệu vào tên (loại bỏ Hungarian notation như `strName`, `arrList`).
- **N7**: Tên hàm phải mô tả rõ các hiệu ứng phụ (side effects) nếu có.

### 5. Đặc thù ngôn ngữ (P1-P3 cho Python & TS1-TS3 cho TypeScript)
- **P1 / TS1**: Cấm wildcard import (`from module import *`). Giữ import rõ ràng, ổn định.
- **P2 / TS2**: Dùng Enum hoặc Literal Union thay cho string/number constants trôi nổi.
- **P3 / TS3**: Bắt buộc Type Hinting trên các public interface; cấm dùng `any` ở ranh giới dữ liệu.

### 6. Kiểm thử (Tests: T1 - T9)
- **T1**: Test mọi thứ có khả năng bị hỏng.
- **T3 / T4**: Không bỏ qua test đơn giản; một test bị ignore là một câu hỏi về độ mơ hồ cần làm rõ.
- **T5**: Kiểm tra triệt để các điều kiện biên (Boundary conditions).
- **T6**: Viết test vét cạn ngay tại vị trí vừa xuất hiện bug.
- **T9**: Test phải chạy cực nhanh (mục tiêu <100ms) để duy trì thói quen chạy liên tục.

---

## 5. Ví Dụ Chuyển Đổi Thực Tế (Before vs After)

Một ví dụ xuất sắc trong tài liệu minh họa cách agent biến đổi code:

```python
# BEFORE (Vi phạm 10 lỗi: P1, C1, N1, F1, F3, C3, G23, G25...)
from utils import *  # P1: Wildcard import

# Author: John, Modified: 2024-01-15  # C1: Metadata comment
def proc(d, t, flag=False):  # N1: Tên tối nghĩa, F1: Quá nhiều tham số, F3: Flag arg
    # Process the data  # C3: Comment thừa
    x = []  # N1: Tên biến một chữ cái
    for i in d:
        if flag:  # F3: Rẽ nhánh theo cờ
            if i['type'] == 'A':  # G23: Magic string rẽ nhánh
                x.append(i['val'] * 1.0825)  # G25: Magic number
            elif i['type'] == 'B':
                x.append(i['val'] * 1.05)
        else:
            x.append(i['val'])
    return x
```

```python
# AFTER (Tuân thủ toàn diện các quy tắc Clean Code)
from dataclasses import dataclass
from typing import Literal

TAX_RATE_CA = 0.0825
TAX_RATE_NY = 0.05
TransactionType = Literal['CA', 'NY']

@dataclass(frozen=True)
class Transaction:
    value: float
    type: TransactionType

def apply_tax(transaction: Transaction) -> float:
    """Áp dụng thuế theo từng bang cụ thể."""
    tax_rates = {'CA': TAX_RATE_CA, 'NY': TAX_RATE_NY}
    return transaction.value * (1 + tax_rates[transaction.type])

def process_transactions_with_tax(transactions: list[Transaction]) -> list[float]:
    """Tính toán giá trị có thuế cho danh sách giao dịch."""
    return [apply_tax(t) for t in transactions]

def process_transactions_without_tax(transactions: list[Transaction]) -> list[float]:
    """Trích xuất giá trị gốc chưa thuế."""
    return [t.value for t in transactions]
```

---

## 6. Đánh Giá & Đề Xuất Cho Antigravity CLI

- **Ưu điểm lớn nhất**:
  - **100% Pure Markdown**: Không phụ thuộc bất kỳ script chạy ngầm nào, loại bỏ hoàn toàn mọi rủi ro bảo mật về thực thi mã.
  - **Mã quy tắc định danh chuẩn (Rule IDs)**: Khi AI review code, nó có thể trích dẫn chính xác `[F3] Flag argument`, `[G25] Magic number`... giúp báo cáo review ngắn gọn, đanh thép và có tính giáo dục cao.
  - Khái niệm **Boy Scout Rule** rất thích hợp để làm một chỉ dẫn hành vi mặc định trong file `AGENTS.md`.
- **Nhược điểm**:
  - Thiếu công cụ phân tích tĩnh tự động (static analysis script) đi kèm để tự verify như repo `btseee`.
  - Tách đôi Python và TypeScript làm 2 track khiến việc cấu hình cho các dự án Fullstack (Python Backend + TypeScript Frontend) bị cấn về mặt tên skill.
- **Đề xuất tích hợp**:
  - Rất thích hợp để trích xuất các bộ quy tắc đánh mã số (C1-C5, F1-F4, G1-G36, N1-N7, T1-T9) vào tài liệu chuẩn mực code hoặc bổ sung vào skill review code của Antigravity.
