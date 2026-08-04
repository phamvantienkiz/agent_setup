Cách "buff" sức mạnh cho Claude Code

Sau 1 năm dùng Claude Code, "superpowers" là plugin mà mình ước gì có từ ngày đầu.

Nó giúp tăng tốc, nâng chất lượng và loại bỏ việc phải qua lại chỉnh sửa với Claude liên tục.

Không có nó, Claude thường bắt đầu build ngay mà không hỏi gì hay lập kế hoạch. Đôi khi ổn, nhưng đa phần bạn sẽ phải sửa sai mất cả tiếng.

"Superpowers" là một framework workflow mã nguồn mở do Jesse Vincent tạo ra. Hơn 125.000 sao trên GitHub và đang tăng rất nhanh.

##### Superpowers thực sự làm gì?

Hãy nghĩ một kỹ sư giỏi làm gì khi có task mới:

Không phải code ngay → mà đọc codebase → hỏi → cân nhắc trade-off → viết hướng tiếp cận → rồi mới build.

Superpowers buộc Claude làm đúng quy trình đó.

Nó có hơn 14 "kỹ năng" tự động kích hoạt:\
brainstorming, lập spec trước, TDD, subagent, debug có hệ thống...

Các kỹ năng là bắt buộc. Nếu áp dụng được thì Claude phải dùng.

##### Pipeline 7 giai đoạn

##### 1\. Brainstorming (quan trọng nhất)

Trước khi làm gì, Claude phải:

- Đọc context project (file, doc, commit)

- Hỏi từng câu (không hỏi dồn)

- Đưa ra 2--3 hướng + trade-off

- Trình bày thiết kế theo từng phần → xin approve

- Viết design doc

- Tự review spec

- Chờ bạn duyệt

Không có code cho đến khi duyệt xong.

##### 2\. Planning

Sau khi duyệt:

- Tạo plan chi tiết: dependency, file path, thứ tự làm

- Không được có:

- "TODO"

- "TBD"

- "làm sau"

Mỗi task phải đủ chi tiết để copy chạy luôn.

##### 3\. Subagent development

Claude không code trực tiếp.

Nó:

- Giao task cho nhiều subagent chạy song song

- Mỗi agent có context riêng

- Claude chỉ làm "manager"

##### 4\. Test-driven development (TDD)

Luật cứng:

Không có code nếu chưa có test fail

Quy trình:

- Viết test fail

- Viết code pass test

- Refactor

##### 5\. Code review 2 bước

- Review 1: đúng spec chưa?

- Review 2: code có sạch không?

Hai reviewer độc lập

##### 6\. Debug có hệ thống

Khi lỗi:

- Reproduce

- Tìm nguyên nhân

- Đặt 1 giả thuyết

- Fix nhỏ nhất có thể

- Verify

Sau 3 lần fail → dừng và xem lại kiến trúc

##### 7\. Hoàn tất branch

- Merge

- PR

- Cleanup

Ví dụ thực tế

Build landing page agency:

- Brainstorm 5 phút:

- hỏi framework

- hỏi design

- hỏi asset

- Đưa ra structure + animation + deploy

- Duyệt → dispatch agent

30 phút sau có page chạy

##### Trade-offs

- Tốn context window

- Task nhỏ thì hơi "overkill"

Nhưng cực mạnh với:

- feature lớn

- project multi-file

##### Insight quan trọng

"Prompt tốt hơn" có giới hạn.

Muốn scale → cần structure + workflow, không chỉ prompt.

##### Cách bắt đầu

- Cài plugin

- Trả lời brainstorming thật kỹ

- Duyệt plan

- Để agent chạy

Nếu bạn đang build hệ thống multi-agent (kiểu bạn đang nghiên cứu với Claude/OpenClaw), thì cái này gần như là blueprint chuẩn để scale dev bằng AI.
