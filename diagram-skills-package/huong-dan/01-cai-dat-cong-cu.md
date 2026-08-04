# 01 — Cài đặt công cụ render (theo engine)

> Mỗi nhóm skill dùng một engine render khác nhau. Chỉ cài cái bạn cần. Bảng dưới đây ghi rõ skill nào cần gì.

| Engine | Skill | Bắt buộc | Cần internet? |
|---|---|---|---|
| **Mermaid** | `/sequence` `/activity` `/state` `/erd` | Node ≥18, `@mermaid-js/mermaid-cli` (mmdc), Chrome | Không (sau khi cài) |
| **PlantUML** | `/activity-swimlane` `/usecase-diagram` | Python 3 (encode), curl | **Có** (render qua plantuml.com) |
| **D2** | `/d2-activity` `/d2-erd` `/d2-architect` | binary `d2`; Chrome (nếu muốn PNG) | Không |
| **BPMN** | `/bpmn` | Node ≥18 + `npm install` trong engine; browser để mở editor | Chỉ khi mở editor HTML (bpmn-js qua CDN) |
| **DBML** | `/dbdiagram` | `@dbml/cli` (Node) | Không |

---

## 1. Node.js (nền cho Mermaid, BPMN, DBML)

Cần Node ≥18 (khuyến nghị ≥20). Kiểm tra:
```bash
node --version
```
Chưa có → cài qua [nodejs.org](https://nodejs.org) hoặc `nvm`.

---

## 2. Mermaid CLI (`mmdc`) — cho `/sequence /activity /state /erd`

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc --version   # kiểm tra
```

Mermaid CLI cần **Chrome** để render. Nếu máy chưa có Chrome cho headless:
```bash
npx puppeteer browsers install chrome
```
Ghi lại đường dẫn Chrome nếu `mmdc` báo thiếu — set biến môi trường:
```bash
export PUPPETEER_EXECUTABLE_PATH="/đường/dẫn/tới/Google Chrome for Testing"
```

> Skill gọi `mermaid-verify.mjs` (trong `.claude/scripts/`) để **compile-check** mọi block Mermaid sau khi ghi — bắt lỗi cú pháp trước khi báo "xong". Script tự tìm Chrome; nếu fail, set `PUPPETEER_EXECUTABLE_PATH`.

---

## 3. D2 — cho `/d2-activity /d2-erd /d2-architect`

```bash
curl -fsSL https://d2lang.com/install.sh | sh -s --
d2 --version   # kiểm tra
```
D2 cài mặc định vào `~/.local/bin/d2`. Đảm bảo thư mục này trong `PATH`.

- SVG render **không cần internet**.
- PNG cần Chrome (script `render.sh` tự tìm Chrome ở `~/.puppeteer-cache` hoặc `google-chrome`/`chromium`). Không có Chrome → vẫn có SVG (mở được bằng browser).

> Cả 3 skill D2 dùng chung `render.sh` đặt tại `.claude/skills/d2-activity/render.sh`. Skill tự gọi — bạn không cần nhớ đường dẫn d2/Chrome.

---

## 4. PlantUML — cho `/activity-swimlane /usecase-diagram`

**Không cần cài Java/plantuml.jar.** Skill encode diagram rồi gọi server công khai `plantuml.com` để lấy `.svg`. Chỉ cần:
```bash
python3 --version   # cho script plantuml_encode.py
curl --version      # để gọi server
```

> ⚠️ **Lưu ý riêng tư:** nội dung diagram (tên actor, tên bước) được **gửi qua internet** tới plantuml.com mỗi lần render. Nếu nghiệp vụ nhạy cảm → cài PlantUML + Java local và sửa `render.sh` trỏ về server nội bộ, hoặc dùng engine khác (Mermaid/D2 render offline).

---

## 5. BPMN — cho `/bpmn`

Engine BPMN cần cài dependency **một lần**:
```bash
cd <workspace>/.claude/skills/bpmn/engine
npm install
```
> Gói chia sẻ **không kèm `node_modules`** (nặng ~11MB) — bạn chạy `npm install` để tải. Có sẵn `package.json` + `package-lock.json`.

Sau đó skill tự chạy engine. Xem BPMN:
- Mở `docs/{feature}/bpmn/{feature}-bpmn-editor.html` bằng browser (kéo-thả sửa như bpmn.io — cần mạng vì bpmn-js tải qua CDN).
- Hoặc import file `.bpmn` vào Camunda Modeler / Bizagi / draw.io (offline).

---

## 6. DBML — cho `/dbdiagram`

```bash
npm install -g @dbml/cli
dbml2sql --version   # kiểm tra
```
Skill validate DBML bằng cách export SQL: `dbml2sql {feature}.dbml --postgres`. Fail = DBML sai cú pháp.

Xem sơ đồ: dán `.dbml` vào [dbdiagram.io](https://dbdiagram.io) hoặc publish [dbdocs.io](https://dbdocs.io). File `.sql` import thẳng PostgreSQL.

---

## Bảng kiểm nhanh sau khi cài

```bash
node --version            # ≥18
mmdc --version            # Mermaid (nếu dùng /sequence /activity /state /erd)
d2 --version              # D2 (nếu dùng /d2-*)
python3 --version         # PlantUML encode (nếu dùng /activity-swimlane /usecase-diagram)
dbml2sql --version        # DBML (nếu dùng /dbdiagram)
```

Chỉ cần dòng tương ứng với skill bạn định dùng chạy OK là đủ.
