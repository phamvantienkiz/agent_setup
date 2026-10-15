# Hướng Dẫn Tích Hợp Trực Quan Hóa Đồ Họa 3D (3D CS Visualization Guide)

> **Mục tiêu:** Khi bài học hoặc chủ đề Khoa học Máy tính cần biểu diễn hình học không gian, phân bố vector đa chiều, mặt cong hàm số hoặc cấu trúc mạng lưới 3D, tài liệu này hướng dẫn cách nhúng trực tiếp canvas WebGL/Three.js vào trang Single-File HTML một cách mượt mà và trực quan.

---

## 1. Khi Nào Chủ Đề CS Cần Trực Quan Hóa 3D?

Trong chương trình Cao học Khoa học Máy tính (UIT), rất nhiều môn học đòi hỏi tư duy không gian:

| Môn Học / Lĩnh Vực | Ứng Dụng Biểu Diễn 3D Trực Quan | Kỹ Thuật Three.js / WebGL |
|:---|:---|:---|
| **Machine Learning / Data Mining** | • Không gian nhúng vector 3D (3D Word/Item Embeddings, t-SNE, UMAP, PCA).<br>• Siêu phẳng phân chia (Hyperplane & Margins của SVM).<br>• Cụm dữ liệu phân tán (3D K-Means, DBSCAN clusters). | Điểm hạt `THREE.Points`, đường bao mặt phẳng `THREE.PlaneGeometry`, lưới trục tọa độ `THREE.AxesHelper`. |
| **Deep Learning & Tối Ưu Hóa** | • Bề mặt hàm mất mát 3D (Loss Surface Landscape) với các điểm cực tiểu địa phương (local minima) và điểm yên ngựa (saddle point).<br>• Mô phỏng đường đi của Gradient Descent / Adam Optimizer. | Mặt cong tham số `THREE.ParametricGeometry` hoặc lưới địa hình `THREE.BufferGeometry`, đường quỹ đạo `THREE.Line`. |
| **Cấu Trúc Dữ Liệu Không Gian** | • Cây phân vùng không gian 3D: Octree, 3D KD-Tree, BVH (Bounding Volume Hierarchy).<br>• Cấu trúc dữ liệu hình học tính toán (Computational Geometry). | Các khối hộp bounding boxes `THREE.BoxHelper`, các mặt phẳng cắt không gian bán trong suốt. |
| **Đồ Thị Mạng & Đồ Thị Tri Thức** | • Đồ thị mạng nơ-ron đồ thị 3D (3D Graph Neural Networks - GNN).<br>• Đồ thị cộng đồng mạng xã hội phức tạp (Subgraphs 3D). | Lực hút lò xo (Force-directed layout 3D), liên kết ống `THREE.CylinderGeometry` hoặc đường thẳng phát sáng. |
| **Hệ Phân Tán (Distributed Systems)** | • Vòng băm nhất quán 3D (Consistent Hashing Ring trong giao thức Chord).<br>• Tô-pô mạng lưới các cụm máy chủ và luồng truyền thông điệp (Raft, Paxos). | Vòng xuyến `THREE.TorusGeometry`, các nút vệ tinh quay xung quanh với hiệu ứng ánh sáng. |

---

## 2. Mã Nguồn Chuẩn Nhúng Three.js Canvas Độc Lập

Canvas 3D phải chạy mượt mà, hỗ trợ xoay chuột (`OrbitControls`) và có giao diện điều khiển (HUD / Toolbar) sạch sẽ:

### 2.1 Thư Viện CDN Cần Nhúng:
```html
<!-- Three.js CDN -->
<script src="https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.min.js"></script>
<!-- OrbitControls cho phép xoay, pan và zoom chuột -->
<script src="https://cdn.jsdelivr.net/npm/three@0.158.0/examples/js/controls/OrbitControls.js"></script>
```

### 2.2 Khung Giao Diện HTML Canvas 3D:
```html
<div class="interactive-card">
    <h4>🌐 Trực Quan Hóa 3D: [Tên Bài Toán - Ví dụ: Không Gian Nhúng Vector / Hàm Mất Mát]</h4>
    <p class="subtitle">Giữ chuột trái để xoay không gian, chuột phải để dịch chuyển (pan), cuộn chuột để phóng to/thu nhỏ:</p>
    
    <div style="position: relative; width: 100%; height: 450px; background: #0f172a; border-radius: 8px; overflow: hidden;">
        <div id="threejs-canvas-container" style="width: 100%; height: 100%;"></div>
        
        <!-- Toolbar điều khiển góc nhìn nhanh -->
        <div style="position: absolute; bottom: 12px; left: 12px; display: flex; gap: 8px; z-index: 10;">
            <button class="interactive-btn" style="background: rgba(255,255,255,0.9); font-size: 0.8rem; padding: 4px 10px;" onclick="resetCamera3D()">Góc Nhìn Chuẩn</button>
            <button class="interactive-btn" style="background: rgba(255,255,255,0.9); font-size: 0.8rem; padding: 4px 10px;" onclick="toggleAutoRotate()">Xoay Tự Động</button>
        </div>
    </div>
</div>
```

### 2.3 JavaScript Khởi Tạo Cảnh 3D (Three.js Lifecycle):
```javascript
let scene, camera, renderer, controls;
let isAutoRotating = false;

function init3DVisualization() {
    const container = document.getElementById('threejs-canvas-container');
    if (!container) return;

    // 1. Khởi tạo Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f172a); // Màu nền Slate 900 hiện đại

    // 2. Khởi tạo Camera
    const width = container.clientWidth;
    const height = container.clientHeight;
    camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(15, 12, 18);

    // 3. Khởi tạo Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // 4. Khởi tạo OrbitControls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    // 5. Thêm Ánh Sáng (Lighting)
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x38bdf8, 1.2);
    dirLight.position.set(10, 20, 15);
    scene.add(dirLight);

    // 6. Thêm Lưới Tọa Độ (Grid & Axes)
    const gridHelper = new THREE.GridHelper(20, 20, 0x334155, 0x1e293b);
    gridHelper.position.y = -0.01;
    scene.add(gridHelper);

    const axesHelper = new THREE.AxesHelper(5);
    scene.add(axesHelper);

    // 7. Thêm Vật Thể Khoa Học Máy Tính (Ví dụ: Các điểm dữ liệu vector 3D)
    buildCSObjects();

    // 8. Vòng lặp Render (Render Loop)
    function animate() {
        requestAnimationFrame(animate);
        if (isAutoRotating) {
            controls.autoRotate = true;
            controls.autoRotateSpeed = 2.0;
        } else {
            controls.autoRotate = false;
        }
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    // 9. Xử lý Resize Màn Hình
    window.addEventListener('resize', () => {
        if (!container) return;
        const w = container.clientWidth;
        const h = container.clientHeight;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
    });
}

function buildCSObjects() {
    // Ví dụ: Tạo 3 cụm dữ liệu phân tán (Clusters) với màu sắc khác nhau
    const geometry = new THREE.SphereGeometry(0.2, 16, 16);
    const colors = [0x38bdf8, 0x10b981, 0xf43f5e];

    for (let c = 0; c < 3; c++) {
        const material = new THREE.MeshStandardMaterial({ 
            color: colors[c], 
            roughness: 0.3, 
            metalness: 0.2 
        });
        const center = new THREE.Vector3((c - 1) * 6, Math.sin(c) * 2 + 2, (c - 1) * 3);

        for (let i = 0; i < 30; i++) {
            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.set(
                center.x + (Math.random() - 0.5) * 4,
                center.y + (Math.random() - 0.5) * 3,
                center.z + (Math.random() - 0.5) * 4
            );
            scene.add(mesh);
        }
    }
}

function resetCamera3D() {
    if (!camera || !controls) return;
    camera.position.set(15, 12, 18);
    controls.target.set(0, 0, 0);
    controls.update();
}

function toggleAutoRotate() {
    isAutoRotating = !isAutoRotating;
}
```

---

## 3. Phối Hợp Cùng Sibling Skill `3dviz-pro-max`

Khi gặp các chủ đề đòi hỏi độ tinh xảo không gian cao (ví dụ: mô hình hóa cơ chế chú ý 3D Attention Head trong Transformer, hoạt ảnh biểu diễn luồng dữ liệu 3D, hoặc các cấu trúc phân tử sinh học / đồ thị khổng lồ):
1. **Tham khảo công thức (Recipes) của `3dviz-pro-max`**:
   - Sử dụng các preset ánh sáng chuyên nghiệp (Studio Softbox, Cyberpunk Neon, Dusk Golden Hour).
   - Sử dụng các vật liệu PBR cao cấp (Transmission Glass, Anodized Metal, Fresnel Glow).
2. **Nguyên tắc Clean Code**: Luôn giải phóng tài nguyên WebGL (`geometry.dispose()`, `material.dispose()`) để tránh rò rỉ bộ nhớ RAM của trình duyệt.
