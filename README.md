# GeoSpatial Việt — website bản tin Geoawesome bằng tiếng Việt — bản 2.0

Website tĩnh (HTML/CSS/JS), tương thích điện thoại và máy tính, dùng `data.json` làm dữ liệu. Bản 2.0 thêm **Góc nhìn nhà địa lý**, hiển thị dưới dạng cửa sổ chi tiết và bộ lọc riêng. Bản mẫu có sáu bài minh họa từ Geoawesome, hiển thị đúng ngày đăng gốc. Không có lời khẳng định rằng bài mới xuất hiện hàng ngày.

## Xem nhanh ở máy tính

```bash
cd geospatial-viet
python -m http.server 8000
```
Truy cập http://localhost:8000/ (không mở file `index.html` bằng `file://` vì trình duyệt thường chặn đọc JSON).

## Xuất bản miễn phí với GitHub Pages (gói đã tối ưu triển khai)

1. Tạo repository GitHub **public** tên `geospatial-viet`. Tải **nội dung bên trong** thư mục `geospatial-viet` lên thẳng gốc repository, đặc biệt giữ `.github/workflows/daily.yml` (nếu tải qua web không thấy thư mục ẩn, tạo file workflow bằng GitHub editor hoặc dùng GitHub Desktop).
2. Trong **Settings → Pages → Build and deployment → Source**, chọn **GitHub Actions** (KHÔNG dùng Deploy from a branch đối với workflow này).
3. Vào **Settings → Secrets and variables → Actions → New repository secret** tạo `OPENAI_API_KEY` với khóa API do bạn tạo tại OpenAI. Có thể bỏ qua bước này để thử giao diện, nhưng khi có tin mới sẽ không được dịch tự động.
4. Chọn **Actions → GeoSpatial Viet - Update and Publish → Run workflow** và mở nhật ký xem `update-and-deploy`. Cần cho phép chạy Actions nếu GitHub hỏi.
5. Website xuất bản tại `https://<username>.github.io/geospatial-viet/`.
6. Workflow chạy 01:00 UTC (~08:00 Việt Nam) mỗi ngày, và cũng xuất bản lại khi có thay đổi ở nhánh `main`. GitHub Actions schedule có thể trễ.

**Lưu ý:** Quy trình sẽ chạy khi được kích hoạt và GitHub Pages chỉ hoạt động sau khi bạn thiết lập repository. `git push` có thể thất bại nếu nhánh bị bảo vệ hoặc tài khoản/chính sách repository không cho phép ghi bằng Actions. RSS Geoawesome chưa được bảo đảm truy cập được, xem nhật ký Actions.

## Cơ chế hoạt động

- `scripts/update.py` thử đọc `https://geoawesome.com/feed/` và feed tin tức; chỉ nhận đường dẫn thuộc geoawesome.com.
- Tách tiêu đề, trích đoạn RSS, tác giả, ngày, nhãn chủ đề. Không tự động sao chép bài toàn văn.
- Nếu đã cấu hình `OPENAI_API_KEY`, AI tạo tiêu đề và tóm tắt **dựa trên phần trích đoạn RSS**, không tự suy diễn nội dung ngoài nguồn.
- Giữ dữ liệu cũ khi feed lỗi; nếu không có bài mới trong ngày thì không giả định có tin mới.
- Nếu không có API key, bài mới vẫn được thu thập nhưng giữ tiêu đề tiếng Anh và ghi rõ chưa có tóm tắt tiếng Việt. Sáu bài mẫu đã biên tập tiếng Việt vẫn được giữ.
- RSS có thể bị chặn hoặc thay đổi cấu trúc, cần kiểm tra bản ghi trong Actions để xử lý; URL `/feed/` được dùng theo quy ước WordPress nhưng **chưa xác minh truy cập thành công** từ môi trường kiểm tra.

## Sở hữu trí tuệ và lưu ý

GeoSpatial Việt là bản tin tổng hợp độc lập, không đại diện cho Geoawesome. Ghi rõ nguồn, tên tác giả và liên kết trực tiếp. Không dùng máy dịch để sao chép toàn văn các bài báo; muốn tái xuất bản toàn văn hoặc ảnh độc quyền, cần xin phép chủ sở hữu. Không dùng logo gốc. Bản dịch/tóm tắt AI phải được kiểm tra trước khi dùng trong tài liệu học thuật.

## Cấu trúc

- `index.html`: giao diện, tìm kiếm, lọc, bài đã lưu trong trình duyệt.
- `data.json`: nội dung bài viết.
- `scripts/update.py`: bộ đồng bộ và tóm tắt.
- `.github/workflows/daily.yml`: lịch tự động.

## Tùy biến

- Đổi tên/logo ở `index.html`.
- Chỉnh chuyên mục trong danh sách `topics` (giao diện) và `CATEGORIES` (Python).
- Chuyển nguồn tin, bổ sung kiểm duyệt biên tập và cơ sở dữ liệu nếu mở rộng thành cổng thông tin nghiên cứu.

## Góc nhìn nhà địa lý (v2.0)

- Nhấn nút **✦ GÓC NHÌN NHÀ ĐỊA LÝ** dưới bài để xem: giá trị khoa học, hướng ứng dụng Việt Nam, công cụ/phương pháp và gợi ý nghiên cứu/bài tập.
- Bật **Chỉ hiện bài có Góc nhìn nhà địa lý** để lọc bài đã được phân tích.
- Các phân tích minh họa trong `data.json` là định hướng do biên tập viên đề xuất, **không phải thông tin xác nhận trong bài gốc**.
- Khi có `OPENAI_API_KEY`, bài RSS mới được tạo thêm đối tượng `geo_perspective` từ tiêu đề và trích đoạn. Do đầu vào ngắn, phân tích mang tính gợi ý và cần người biên tập kiểm tra.
- Bài cũ đã lưu trước nâng cấp mà thiếu `geo_perspective` vẫn hiển thị bình thường; không có nút phân tích.
- Không đưa API key lên giao diện, chỉ lưu dưới GitHub Actions Secrets.
