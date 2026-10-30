# GeoSpatial Việt 3.0

Website GitHub Pages đọc tin Geoawesome và đăng **bài phân tích tiếng Việt độc lập** theo nội dung bài gốc khi truy cập được. Không tự động tái xuất bản bản dịch nguyên văn hoặc lưu toàn văn gốc.

## Cập nhật repository đang chạy

1. Giải nén. Trong `geospatial-viet/`, tải đè các tệp `index.html`, `scripts/update.py`, `requirements.txt`, `README.md` và `.github/workflows/daily.yml` lên **đúng đường dẫn** trên repository `truongtvhus-ai/geospatial-viet`. **Không xóa `data.json` trên GitHub**: giữ dữ liệu của bạn; tệp data.json trong ZIP chỉ là bản mẫu tham khảo.
2. Nếu tải một thư mục qua trình duyệt không giữ cấu trúc, mở trực tiếp tệp tương ứng trên GitHub, bấm Edit (biểu tượng bút), dán nội dung và Commit, hoặc dùng GitHub Desktop.
3. Settings → Pages → Source: **GitHub Actions**.
4. Settings → Secrets and variables → Actions → Repository secrets: giữ `OPENAI_API_KEY` (đã thiết lập từ bản 2.0). Không bao giờ đưa khóa vào code hoặc data.json.
5. Actions → `GeoSpatial Viet - Update and Publish` → Run workflow → main. Kiểm tra các bước `Fetch and summarize new items`, `Deploy website`.
6. Trang: https://truongtvhus-ai.github.io/geospatial-viet/ . Workflow chạy theo lịch `0 1 * * *` (~08:00 Việt Nam, có thể trễ).

## Có gì mới?

- `scripts/update.py`: trích văn bản nội dung chính bằng trafilatura để **phân tích trong bộ nhớ**, không công khai hay lưu toàn văn nguồn.
- OpenAI API tạo JSON: `analysis.lead`, `scientific_context`, `methods_and_data`, `findings_and_implications`, `limitations`, `vietnam_applications`, `learning_activity`, `editorial_note`; cùng `geo_perspective`.
- Mỗi tin có nút **Đọc phân tích chi tiết** và **Góc nhìn nhà địa lý**; ghi rõ khi chỉ căn cứ RSS.
- Các bài cũ 2.0 chưa có trường `analysis`, được hiển thị như dữ liệu cũ, **không tự biến thành nội dung toàn văn**.
- Hạn chế tối đa số bài mới mỗi lượt với `MAX_NEW_ARTICLES` (mặc định 8) để kiểm soát chi phí API.

## Quyền nội dung

Bài phân tích là sản phẩm mới, diễn đạt độc lập và dẫn nguồn gốc. **Không** đăng lại bản dịch toàn văn, ảnh gốc hay bảng gốc khi chưa được phép. Để có chế độ dịch toàn văn cho bài có giấy phép, cần thêm danh sách cho phép và bước xác minh quyền trước khi triển khai.

## Khắc phục

- Không có tin mới: kiểm tra URL RSS, chính sách truy cập trang nguồn, nhật ký Actions.
- Chỉ có RSS: `source_basis = rss_only` nghĩa là trích xuất toàn văn không thành công hoặc quá ngắn.
- Không tạo phân tích: kiểm tra `OPENAI_API_KEY`, tín dụng API và lỗi trong Actions; không đăng khóa lên Issue.
- `data.json` không đổi: có thể không có bài mới, hay feed lỗi; bản cũ được giữ nguyên.
- `Actions` bị từ chối push: Settings → Actions → General → Workflow permissions → Read and write permissions (nếu cho phép); kiểm tra branch protection.

## Tùy chọn

- `OPENAI_MODEL`: mặc định `gpt-4.1-mini`.
- `MAX_NEW_ARTICLES`: mặc định 8.
- `MAX_SOURCE_WORDS`: mặc định 8500.

Bản này là mã nguồn mẫu chưa được kiểm thử trực tiếp với hạ tầng GitHub và Geoawesome tại thời điểm tạo. Kiểm tra nhật ký của workflow để xác nhận tin mới thực tế.
