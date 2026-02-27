"""
Seed 32 sản phẩm đồ trẻ em Con Cưng — mô tả chi tiết chuyên nghiệp.
Chạy: python manage.py them_san_pham_mau
"""
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import DanhMuc, SanPham


class Command(BaseCommand):
    help = 'Seed 32 sản phẩm đồ trẻ em đầy đủ mô tả, ảnh, nổi bật'

    def handle(self, *args, **kwargs):
        self.stdout.write('\n👶  CON CƯNG — Seed 32 sản phẩm\n' + '═' * 60)

        # ── Tìm thư mục ảnh ─────────────────────────────────────────
        base_dir = Path(settings.BASE_DIR)
        thu_muc_anh = None
        for c in [base_dir / 'images', base_dir.parent / 'images']:
            if c.exists():
                thu_muc_anh = c
                break
        if hasattr(settings, 'IMAGES_DIR'):
            p = Path(settings.IMAGES_DIR)
            if p.exists():
                thu_muc_anh = p

        if thu_muc_anh:
            n = len(list(thu_muc_anh.glob('*.*')))
            self.stdout.write(f'📁 Ảnh: {thu_muc_anh} ({n} files)')
        else:
            self.stdout.write('⚠️  Không tìm thấy thư mục images/')

        media_sp = Path(settings.MEDIA_ROOT) / 'san_pham'
        media_sp.mkdir(parents=True, exist_ok=True)

        def anh(ten):
            if not thu_muc_anh or not ten:
                return ''
            for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                src = thu_muc_anh / f'{ten}{ext}'
                if src.exists():
                    dst = media_sp / f'{ten}{ext}'
                    shutil.copy2(src, dst)
                    return f'san_pham/{ten}{ext}'
            return ''

        # ── Danh mục ────────────────────────────────────────────────
        dm_data = [
            ('Sữa bột & Công thức',    'sua-bot-cong-thuc',   1),
            ('Ăn dặm & Dinh dưỡng',    'an-dam-dinh-duong',   2),
            ('Nước uống & Yến sào',    'nuoc-uong-yen-sao',   3),
            ('Bình sữa & Dụng cụ',     'binh-sua-dung-cu',    4),
            ('Ghế & Thiết bị cho bé',  'ghe-thiet-bi-cho-be', 5),
            ('Đồ chơi & Giáo dục',     'do-choi-giao-duc',    6),
            ('Thuốc & Chăm sóc sức khỏe', 'thuoc-suc-khoe',  7),
            ('Quần áo & Phụ kiện',     'quan-ao-phu-kien',    8),
        ]
        self.stdout.write('\n📂 Danh mục:')
        dm = {}
        for ten, slug, thu_tu in dm_data:
            obj, created = DanhMuc.objects.get_or_create(
                slug=slug, defaults={'ten': ten, 'thu_tu': thu_tu}
            )
            dm[slug] = obj
            self.stdout.write(f'  {"✅" if created else "⏭️ "} {ten}')

        # ── 32 Sản phẩm ─────────────────────────────────────────────
        products = [

            # ══════════════════════════════════════════════════════════
            # SUA_1..4 — Sữa bột công thức cao cấp
            # ══════════════════════════════════════════════════════════
            {
                'slug': 'sua-bot-cong-thuc', 'ten_anh': 'sua_1', 'noi_bat': True,
                'ten': 'Sữa bột Aptamil Profutura Số 1 dành cho trẻ 0–6 tháng tuổi (800g)',
                'ma': 'CC-SUA-001', 'gia': 890000, 'nhap': 640000, 'km': 820000,
                'brand': 'Aptamil', 'xuat_xu': 'Đức', 'kl': 800,
                'ngan': 'Sữa bột cao cấp nhập khẩu Đức, công thức tiệm cận sữa mẹ nhất hiện nay',
                'chi_tiet': (
                    'Aptamil Profutura Số 1 là thành quả của hơn 50 năm nghiên cứu chuyên sâu '
                    'về dinh dưỡng trẻ sơ sinh tại Viện Nghiên cứu Sức khỏe Trẻ em Châu Âu. '
                    'Công thức độc quyền kết hợp hệ prebiotics GOS/FOS tỷ lệ 9:1 — tỷ lệ xuất '
                    'hiện tự nhiên trong sữa mẹ, giúp nuôi dưỡng hệ vi sinh đường ruột có lợi '
                    'tương tự bé bú mẹ hoàn toàn. DHA từ tảo biển tự nhiên và ARA từ dầu nấm '
                    'hỗ trợ phát triển não bộ và thị giác tối ưu trong 6 tháng đầu đời — giai '
                    'đoạn não bộ phát triển nhanh nhất trong cuộc đời con người. Không chứa dầu '
                    'cọ, không gluten, không hormone tăng trưởng. Đạt chứng nhận an toàn thực '
                    'phẩm EU nghiêm ngặt. Được hơn 2 triệu bà mẹ Châu Âu tin dùng hàng năm.'
                ),
            },
            {
                'slug': 'sua-bot-cong-thuc', 'ten_anh': 'sua_2', 'noi_bat': True,
                'ten': 'Sữa bột Enfamil A+ Số 2 dành cho trẻ 6–12 tháng tuổi (900g)',
                'ma': 'CC-SUA-002', 'gia': 650000, 'nhap': 470000, 'km': None,
                'brand': 'Enfamil', 'xuat_xu': 'Mỹ', 'kl': 900,
                'ngan': 'Sữa Enfamil A+ bổ sung MFGM & DHA hỗ trợ não bộ và miễn dịch toàn diện',
                'chi_tiet': (
                    'Enfamil A+ Số 2 ứng dụng công thức MFGM (Milk Fat Globule Membrane — Màng '
                    'cầu mỡ sữa) kết hợp DHA, được chứng minh lâm sàng qua nghiên cứu 10 năm '
                    'tại Mỹ, Canada và Trung Quốc với hơn 4.000 trẻ tham gia. Trẻ dùng Enfamil '
                    'A+ có điểm IQ và khả năng ngôn ngữ cao hơn so với nhóm đối chứng. MFGM '
                    'là thành phần bao quanh các giọt béo trong sữa mẹ, đóng vai trò quan trọng '
                    'hình thành myelin — lớp bọc tế bào thần kinh giúp tăng tốc độ truyền tín '
                    'hiệu não bộ. Ngoài ra bổ sung Inositol, Choline, 12 loại vitamin và 10 '
                    'khoáng chất cân đối. Được hơn 4.500 bác sĩ nhi khoa Bắc Mỹ tin tưởng.'
                ),
            },
            {
                'slug': 'sua-bot-cong-thuc', 'ten_anh': 'sua_3', 'noi_bat': False,
                'ten': 'Sữa bột Nestlé NAN Optipro Số 3 cho trẻ 1–3 tuổi (800g)',
                'ma': 'CC-SUA-003', 'gia': 485000, 'nhap': 340000, 'km': 449000,
                'brand': 'Nestlé NAN', 'xuat_xu': 'Thụy Sĩ', 'kl': 800,
                'ngan': 'NAN Optipro hỗ trợ tiêu hóa, miễn dịch và phát triển não bộ cho bé 1–3 tuổi',
                'chi_tiet': (
                    'Nestlé NAN OPTIPRO 3 ứng dụng công nghệ OPTIPRO độc quyền — tối ưu hóa '
                    'hàm lượng protein ở mức vừa đủ cho phát triển, không dư thừa gây gánh '
                    'nặng thận. Protein chất lượng cao từ casein và whey tỷ lệ 40:60, giàu '
                    'axit amin thiết yếu Leucine kích thích tổng hợp cơ bắp. DHA từ dầu cá '
                    'tự nhiên và Lutein từ hoa cúc vạn thọ bảo vệ và phát triển thị giác. '
                    'Probiotics Bifidus BL sống được đến ruột già, giúp cân bằng hệ vi sinh '
                    'đường ruột, giảm tiêu chảy và táo bón. Canxi và Vitamin D3, K2 bộ ba '
                    'hoàn hảo cho xương và răng chắc khỏe. Vị sữa thơm ngon bé dễ chấp nhận.'
                ),
            },
            {
                'slug': 'sua-bot-cong-thuc', 'ten_anh': 'sua_4', 'noi_bat': False,
                'ten': 'Sữa bột Similac IQ Eye-Q Số 4 cho trẻ 2–6 tuổi (900g)',
                'ma': 'CC-SUA-004', 'gia': 520000, 'nhap': 370000, 'km': 479000,
                'brand': 'Similac', 'xuat_xu': 'Mỹ', 'kl': 900,
                'ngan': 'Similac IQ Eye-Q hệ dưỡng chất DHA–ARA–Taurine phát triển não và mắt bé',
                'chi_tiet': (
                    'Similac IQ Eye-Q Plus với hệ dưỡng chất não–mắt toàn diện gồm DHA (axit '
                    'béo omega-3 cấu tạo 60% chất béo não bộ), ARA (axit béo omega-6 cần cho '
                    'màng tế bào thần kinh) và Taurine (axit amin tự do dồi dào trong sữa mẹ, '
                    'thiết yếu cho thị giác và chức năng não). Nucleotides tăng cường tế bào '
                    'miễn dịch NK và lymphocyte B, giúp bé chống lại vi khuẩn và virus. '
                    'FOS prebiotics nuôi dưỡng lợi khuẩn Bifidus, cải thiện hấp thu canxi '
                    'và sắt. Không lactose nhân tạo, không hương liệu tổng hợp. Công thức '
                    'ít ngọt, khuyến khích thói quen ăn uống lành mạnh từ nhỏ cho bé 2–6 tuổi.'
                ),
            },

            # ══════════════════════════════════════════════════════════
            # BOT_SUA_1..4 — Ăn dặm & dinh dưỡng bổ sung
            # ══════════════════════════════════════════════════════════
            {
                'slug': 'an-dam-dinh-duong', 'ten_anh': 'bot_sua_1', 'noi_bat': True,
                'ten': 'Sữa bột Friso Gold Số 1 công nghệ LockNutri cho trẻ 0–6 tháng (800g)',
                'ma': 'CC-BOT-001', 'gia': 760000, 'nhap': 550000, 'km': 699000,
                'brand': 'Friso Gold', 'xuat_xu': 'Hà Lan', 'kl': 800,
                'ngan': 'Friso Gold LockNutri xử lý nhiệt một lần, bảo toàn protein tự nhiên tối đa',
                'chi_tiet': (
                    'Friso Gold Số 1 được sản xuất bằng công nghệ LockNutri độc quyền — quy '
                    'trình xử lý nhiệt chỉ một lần duy nhất từ sữa bò tươi đến thành phẩm, '
                    'giữ nguyên cấu trúc 3D tự nhiên của protein sữa. Protein ít biến tính '
                    'đồng nghĩa với tiêu hóa dễ dàng hơn 30% so với sữa xử lý nhiệt nhiều '
                    'lần — bé ít bị đầy bụng, ít trớ và ít táo bón. Nguồn sữa 100% từ bò '
                    'tươi của các trang trại Hà Lan đạt chứng nhận quốc tế, không kháng sinh, '
                    'không hormone tăng trưởng, không biến đổi gen. GOS prebiotics từ sữa '
                    'tăng cường miễn dịch. DHA từ tảo biển và Arachidonic acid ARA hỗ trợ '
                    'phát triển thần kinh. Vitamin A, C, D, E đầy đủ cho bé 0–6 tháng.'
                ),
            },
            {
                'slug': 'an-dam-dinh-duong', 'ten_anh': 'bot_sua_2', 'noi_bat': False,
                'ten': 'Sữa bột Dumex Dulac Số 2 hệ SYNBIO cho trẻ 6–12 tháng (800g)',
                'ma': 'CC-BOT-002', 'gia': 425000, 'nhap': 295000, 'km': None,
                'brand': 'Dumex', 'xuat_xu': 'Đan Mạch', 'kl': 800,
                'ngan': 'Dumex SYNBIO — prebiotic + probiotic sống được đến ruột già cho bé khỏe tiêu hóa',
                'chi_tiet': (
                    'Dumex Dulac Số 2 với hệ SYNBIO kết hợp prebiotic FOS/GOS (thức ăn cho '
                    'lợi khuẩn) và probiotic Bifidobacterium BB-12 (chủng lợi khuẩn được '
                    'nghiên cứu nhiều nhất thế giới, sống được qua axit dạ dày đến tận ruột '
                    'già). Sự kết hợp này tạo hệ sinh thái đường ruột cân bằng, giảm 40% '
                    'nguy cơ tiêu chảy do kháng sinh và 35% nguy cơ nhiễm trùng đường hô '
                    'hấp. Sắt hữu cơ (sắt sulfate) hấp thu gấp 2 lần sắt vô cơ, phòng ngừa '
                    'thiếu máu thiếu sắt thường gặp ở trẻ 6–12 tháng. DHA và ARA tỷ lệ 1:2 '
                    'giống sữa mẹ. Taurine hỗ trợ phát triển thị giác và chức năng não bộ.'
                ),
            },
            {
                'slug': 'an-dam-dinh-duong', 'ten_anh': 'bot_sua_3', 'noi_bat': False,
                'ten': 'Cháo ăn dặm Heinz vị Gà & Rau củ hữu cơ cho bé từ 6 tháng (200g)',
                'ma': 'CC-BOT-003', 'gia': 85000, 'nhap': 55000, 'km': 75000,
                'brand': 'Heinz Baby', 'xuat_xu': 'Anh', 'kl': 200,
                'ngan': 'Cháo ăn dặm Heinz từ gạo + gà tươi + rau củ hữu cơ, không bảo quản',
                'chi_tiet': (
                    'Heinz Baby Cháo Gà Rau Củ được chế biến từ gạo trắng xay nhuyễn, thịt '
                    'gà ta tươi và hỗn hợp cà rốt, đậu hà lan, bí đỏ hữu cơ — tất cả không '
                    'chất bảo quản, không màu nhân tạo, không đường bổ sung, không muối thêm. '
                    'Gạo được thủy phân sơ bộ giúp enzyme tiêu hóa non nớt của bé phân giải '
                    'tinh bột dễ dàng. Kết cấu mịn mượt được nghiên cứu riêng cho bé bắt đầu '
                    'ăn dặm giai đoạn Stage 1 (6–8 tháng). Tăng cường sắt hữu cơ, kẽm và '
                    'vitamin nhóm B hỗ trợ tăng trưởng và phát triển nhận thức. Thương hiệu '
                    'Heinz đã đồng hành cùng các bà mẹ trên 120 quốc gia suốt hơn 150 năm.'
                ),
            },
            {
                'slug': 'an-dam-dinh-duong', 'ten_anh': 'bot_sua_4', 'noi_bat': False,
                'ten': 'Bột ăn dặm Nestlé Cerelac Lúa mì & Sữa cho bé từ 6 tháng (200g)',
                'ma': 'CC-BOT-004', 'gia': 72000, 'nhap': 45000, 'km': None,
                'brand': 'Nestlé Cerelac', 'xuat_xu': 'Việt Nam', 'kl': 200,
                'ngan': 'Cerelac lúa mì sữa bổ sung 18 vitamin khoáng chất, giàu sắt cho bé ăn dặm',
                'chi_tiet': (
                    'Nestlé Cerelac Lúa Mì Sữa là sản phẩm ăn dặm kinh điển được hàng triệu '
                    'bà mẹ Việt Nam tin dùng qua nhiều thế hệ. Làm từ bột lúa mì tinh chế kết '
                    'hợp sữa bột nguyên kem, bổ sung 18 loại vitamin và khoáng chất thiết yếu. '
                    'Đặc biệt giàu sắt với hàm lượng gấp 2 lần nhu cầu khuyến nghị — phòng '
                    'ngừa hiệu quả thiếu máu dinh dưỡng, nguyên nhân hàng đầu gây chậm phát '
                    'triển trí tuệ ở trẻ nhỏ. Tinh bột được tiền thủy phân (pre-cooked) giúp '
                    'enzyme amylase tiêu hóa dễ hơn 50%. Vị ngọt tự nhiên từ sữa không cần '
                    'thêm đường. Pha nhanh trong 30 giây, tan đều không vón cục. Phù hợp từ '
                    '6 tháng, là nền tảng dinh dưỡng vững chắc cho hành trình ăn dặm của bé.'
                ),
            },

            # ══════════════════════════════════════════════════════════
            # DINH_DUONG_1..4 — Thực phẩm chức năng & dinh dưỡng bổ sung
            # ══════════════════════════════════════════════════════════
            {
                'slug': 'an-dam-dinh-duong', 'ten_anh': 'dinh_duong_1', 'noi_bat': False,
                'ten': 'Siro ăn ngon Hipp BIO Lysine & Kẽm kích thích vị giác cho bé từ 1 tuổi (100ml)',
                'ma': 'CC-DD-001', 'gia': 185000, 'nhap': 120000, 'km': 165000,
                'brand': 'Hipp Bio', 'xuat_xu': 'Đức', 'kl': 100,
                'ngan': 'Siro Hipp Bio hữu cơ kích thích ăn ngon cho bé biếng ăn, chậm tăng cân',
                'chi_tiet': (
                    'Siro Hipp BIO Lysine được bào chế từ nguyên liệu hữu cơ chứng nhận USDA '
                    'Organic và EU Organic. L-Lysine — axit amin thiết yếu mà cơ thể không tự '
                    'tổng hợp được, kích thích tiết acid dạ dày và enzyme tiêu hóa tăng cảm '
                    'giác đói tự nhiên. Kẽm gluconate hỗ trợ hơn 300 enzyme chuyển hóa, cải '
                    'thiện vị giác và khứu giác giúp bé nhận thức mùi vị thức ăn rõ ràng hơn. '
                    'Phức hợp vitamin B1–B2–B3–B6 chuyển hóa năng lượng từ carbohydrate, chất '
                    'béo và protein thành năng lượng sẵn dùng, kích thích thèm ăn. Hoàn toàn '
                    'tự nhiên, không chất bảo quản, không màu nhân tạo, không cồn, không '
                    'hương liệu tổng hợp. Vị dâu tây tự nhiên bé thích uống. Hiệu quả rõ '
                    'rệt sau 2–4 tuần sử dụng liên tục đều đặn mỗi ngày.'
                ),
            },
            {
                'slug': 'an-dam-dinh-duong', 'ten_anh': 'dinh_duong_2', 'noi_bat': False,
                'ten': 'Canxi Nano D3 K2 Ostelin dạng nhỏ giọt cho bé sơ sinh đến 12 tuổi (20ml)',
                'ma': 'CC-DD-002', 'gia': 245000, 'nhap': 160000, 'km': None,
                'brand': 'Ostelin', 'xuat_xu': 'Úc', 'kl': 20,
                'ngan': 'Canxi lỏng bộ ba Canxi–D3–K2 MK-7 tối ưu hấp thu xương và răng cho bé',
                'chi_tiet': (
                    'Ostelin Calcium Liquid với bộ ba vàng Canxi–Vitamin D3–Vitamin K2 MK-7 '
                    '(dạng menaquinone-7 từ natto Nhật Bản, sinh khả dụng cao nhất trong các '
                    'dạng K2). Cơ chế hoạt động hiệp đồng: D3 tăng hấp thu canxi tại ruột '
                    'non lên 300%, K2 MK-7 "hướng dẫn" canxi đi đúng vào xương và răng thay '
                    'vì lắng đọng trong mạch máu và mô mềm. Canxi dạng lỏng hấp thu nhanh '
                    'và hoàn toàn hơn viên nén. Không mùi, không màu, trộn được vào bất kỳ '
                    'thức ăn hay đồ uống nào của bé. Liều dùng linh hoạt bằng ống nhỏ giọt '
                    'kèm theo. Phù hợp đặc biệt cho bé ít ra nắng, bé sinh non, bé có nguy '
                    'cơ còi xương. Sản xuất tại Úc đạt chuẩn TGA nghiêm ngặt.'
                ),
            },
            {
                'slug': 'an-dam-dinh-duong', 'ten_anh': 'dinh_duong_3', 'noi_bat': False,
                'ten': 'DHA Omega-3 Coromega Baby dạng gel nhũ tương cho bé 0–12 tháng (90 gói)',
                'ma': 'CC-DD-003', 'gia': 395000, 'nhap': 270000, 'km': 359000,
                'brand': 'Coromega', 'xuat_xu': 'Mỹ', 'kl': 90,
                'ngan': 'DHA 350mg từ dầu cá hồi Alaska dạng gel hấp thu gấp 3 lần so với viên nang',
                'chi_tiet': (
                    'Coromega Baby cung cấp 350mg DHA tinh khiết mỗi gói, nguồn gốc từ dầu '
                    'cá hồi Alaska hoang dã được kiểm nghiệm độc lập tại phòng lab NSF '
                    'International — không phát hiện kim loại nặng, PCB, dioxin và hơn 200 '
                    'chất ô nhiễm. Công nghệ nhũ tương hóa CoroMax độc quyền tạo ra các hạt '
                    'dầu cực nhỏ (micelle) tương tự chất béo sữa mẹ, hấp thu qua niêm mạc '
                    'ruột non hiệu quả hơn 300% so với viên nang thông thường. DHA chiếm '
                    '60% chất béo não bộ và 40% màng tế bào võng mạc — thiết yếu cho trí '
                    'tuệ và thị lực trong hai năm đầu đời vàng. Vị cam chanh tự nhiên, không '
                    'mùi tanh, trộn được vào sữa. Chứng nhận Non-GMO và Sustainable Seafood.'
                ),
            },
            {
                'slug': 'an-dam-dinh-duong', 'ten_anh': 'dinh_duong_4', 'noi_bat': False,
                'ten': 'Men vi sinh Probiotic Blackmores Baby 3 tỷ CFU dạng bột (28 gói)',
                'ma': 'CC-DD-004', 'gia': 320000, 'nhap': 215000, 'km': None,
                'brand': 'Blackmores', 'xuat_xu': 'Úc', 'kl': 56,
                'ngan': 'Men vi sinh 4 chủng lợi khuẩn 3 tỷ CFU hỗ trợ tiêu hóa và miễn dịch bé',
                'chi_tiet': (
                    'Blackmores Baby Probiotic+ chứa tổ hợp 4 chủng lợi khuẩn được nghiên '
                    'cứu lâm sàng nhiều nhất thế giới: Lactobacillus rhamnosus GG (LGG — chủng '
                    'chuẩn vàng chống tiêu chảy do kháng sinh), L. acidophilus NCFM (cải thiện '
                    'hội chứng ruột kích thích), Bifidobacterium lactis Bi-07 và B. longum BB536 '
                    '(tăng cường IgA đường ruột và giảm dị ứng). Mỗi gói 3 tỷ CFU sống được '
                    'qua môi trường axit dạ dày nhờ công nghệ vi bao đặc biệt. Giảm 60% triệu '
                    'chứng đau bụng colic ở sơ sinh, 50% tiêu chảy do virus và 40% chàm dị '
                    'ứng trong năm đầu đời. Dạng bột không mùi vị, bảo quản ở nhiệt độ phòng.'
                ),
            },

            # ══════════════════════════════════════════════════════════
            # NUOC_YEN_1..4 — Nước uống & yến sào
            # ══════════════════════════════════════════════════════════
            {
                'slug': 'nuoc-uong-yen-sao', 'ten_anh': 'nuoc_yen_1', 'noi_bat': True,
                'ten': 'Nước yến chưng đường phèn Sanest Khánh Hòa hộp 6 chai x 70ml',
                'ma': 'CC-YEN-001', 'gia': 175000, 'nhap': 120000, 'km': 155000,
                'brand': 'Sanest', 'xuat_xu': 'Việt Nam', 'kl': 420,
                'ngan': 'Yến sào Khánh Hòa nguyên chất 100%, chưng cách thủy truyền thống cho bé 1 tuổi+',
                'chi_tiet': (
                    'Sanest là thương hiệu yến sào uy tín số 1 Việt Nam, thuộc Công ty Yến Sào '
                    'Khánh Hòa — đơn vị khai thác yến sào đảo tự nhiên lâu đời nhất. Mỗi chai '
                    '70ml sử dụng tổ yến thiên nhiên thực sự từ vùng đảo Khánh Hòa, chưng cách '
                    'thủy ở nhiệt độ 100°C trong 3 giờ theo phương pháp truyền thống — không '
                    'pha trộn tinh chất yến hay hương liệu tổng hợp. Glycoprotein (EGF — '
                    'Epidermal Growth Factor) trong tổ yến kích thích tế bào NK và lymphocyte '
                    'tăng cường miễn dịch. 18 loại axit amin thiết yếu cung cấp nguyên liệu '
                    'xây dựng tế bào thần kinh. Sialic acid hỗ trợ phát triển và kết nối '
                    'synapse não bộ. Đường phèn thiên nhiên vị ngọt thanh dịu. Tiệt trùng '
                    'UHT bảo quản 24 tháng, không cần tủ lạnh trước khi mở.'
                ),
            },
            {
                'slug': 'nuoc-uong-yen-sao', 'ten_anh': 'nuoc_yen_2', 'noi_bat': False,
                'ten': 'Sữa lúa mạch Nestlé Milo Active-Go hộp 180ml (thùng 48 hộp)',
                'ma': 'CC-YEN-002', 'gia': 360000, 'nhap': 250000, 'km': 329000,
                'brand': 'Nestlé Milo', 'xuat_xu': 'Việt Nam', 'kl': 8640,
                'ngan': 'Milo Active-Go hệ Activ-Go cung cấp năng lượng bền vững cho bé vận động cả ngày',
                'chi_tiet': (
                    'Nestlé Milo Active-Go là sản phẩm dinh dưỡng thể thao dành riêng cho '
                    'trẻ em với hệ dưỡng chất Activ-Go gồm Malt lúa mạch rang — nguồn carb '
                    'phức giải phóng năng lượng từ từ, không gây đột biến đường huyết. Canxi '
                    '30% DRI, Sắt 20% DRI, Vitamin B2, B3, B6, B12 toàn diện cho chuyển hóa '
                    'năng lượng từ thức ăn thành ATP hiệu quả. Chỉ số GI thấp hơn sữa thông '
                    'thường, phù hợp bé hoạt động thể chất cường độ vừa. Hộp Tetra Pak '
                    '180ml tiện lợi mang theo đi học, thể thao, dã ngoại. Không chứa chất '
                    'bảo quản, không màu nhân tạo. Được Liên đoàn Thể thao ASEAN chứng nhận '
                    'là thức uống dinh dưỡng thể thao chính thức cho vận động viên nhỏ tuổi.'
                ),
            },
            {
                'slug': 'nuoc-uong-yen-sao', 'ten_anh': 'nuoc_yen_3', 'noi_bat': False,
                'ten': 'Nước ép trái cây Heinz Baby Juice vị Táo & Lê nguyên chất (6 chai x 128ml)',
                'ma': 'CC-YEN-003', 'gia': 95000, 'nhap': 62000, 'km': None,
                'brand': 'Heinz Baby', 'xuat_xu': 'Anh', 'kl': 768,
                'ngan': 'Nước ép táo lê 100% tự nhiên không đường không bảo quản cho bé từ 6 tháng',
                'chi_tiet': (
                    'Heinz Baby Juice Táo Lê được ép lạnh từ trái cây tươi thu hoạch đúng mùa '
                    'tại các vườn cây hữu cơ châu Âu — 100% nước ép tự nhiên không pha thêm '
                    'nước, không bổ sung đường, không chất bảo quản. Vitamin C tự nhiên từ '
                    'táo và lê hỗ trợ miễn dịch và tăng hấp thu sắt phi heme từ thức ăn lên '
                    'đến 300%. Pectin tự nhiên trong táo nuôi dưỡng lợi khuẩn đường ruột. '
                    'Thanh trùng UHT nhiệt độ thấp giữ nguyên tối đa vitamin, khoáng chất '
                    'và hương vị tự nhiên. Chai 128ml vừa đúng một lần uống cho bé, tránh '
                    'oxy hóa sau khi mở. Pha loãng 1:1 với nước ấm cho bé dưới 12 tháng.'
                ),
            },
            {
                'slug': 'nuoc-uong-yen-sao', 'ten_anh': 'nuoc_yen_4', 'noi_bat': False,
                'ten': 'Cháo đông khô Wakodo vị Rau Bina & Cà Rốt cho bé từ 5 tháng (80g)',
                'ma': 'CC-YEN-004', 'gia': 65000, 'nhap': 42000, 'km': 58000,
                'brand': 'Wakodo', 'xuat_xu': 'Nhật Bản', 'kl': 80,
                'ngan': 'Cháo ăn dặm Nhật Bản Wakodo siêu mịn 0.1mm chuẩn vị bé Nhật từ 1951',
                'chi_tiet': (
                    'Wakodo là thương hiệu thực phẩm ăn dặm số 1 Nhật Bản từ năm 1951, được '
                    'tin dùng bởi hơn 70% bà mẹ Nhật. Cháo Rau Bina Cà Rốt nấu từ gạo '
                    'Japonica hạt tròn Nhật Bản (koshi hikari) và rau hữu cơ, nghiền siêu '
                    'mịn đạt độ mịn 0.1mm — mịn hơn lụa, tan hoàn toàn trong miệng bé. '
                    'Tuyệt đối không muối, không đường, không chất bảo quản, không phụ gia '
                    'thực phẩm — dựa hoàn toàn vào vị ngọt tự nhiên của rau củ để giúp bé '
                    'phát triển vị giác lành mạnh. Sắt từ rau bina tự nhiên (heme iron) '
                    'hấp thu dễ dàng. Công nghệ đông khô (freeze-drying) giữ nguyên 95% '
                    'vitamin và khoáng chất. Tan trong 30 giây với nước ấm 50°C. Phù hợp '
                    'bé từ 5 tháng, giai đoạn ăn dặm đầu tiên và quan trọng nhất.'
                ),
            },

            # ══════════════════════════════════════════════════════════
            # BINH_SUA_1..4 — Bình sữa các loại
            # ══════════════════════════════════════════════════════════
            {
                'slug': 'binh-sua-dung-cu', 'ten_anh': 'binh_sua_1', 'noi_bat': True,
                'ten': 'Bình sữa Pigeon SofTouch cổ rộng PPSU 240ml núm ti SS chống sặc',
                'ma': 'CC-BS-001', 'gia': 285000, 'nhap': 195000, 'km': None,
                'brand': 'Pigeon', 'xuat_xu': 'Nhật Bản', 'kl': 180,
                'ngan': 'Bình sữa PPSU Pigeon SofTouch van Y-cut chống sặc cho bé sơ sinh 0–3 tháng',
                'chi_tiet': (
                    'Pigeon SofTouch cổ rộng làm từ PPSU (Polyphenylsulfone) — loại nhựa y tế '
                    'cao cấp nhất hiện nay, chịu nhiệt 180°C không biến dạng, hoàn toàn không '
                    'chứa BPA, BPS, BPF và các hóa chất nội tiết gây rối loạn khác. Sau hàng '
                    'trăm chu kỳ tiệt trùng, nhựa PPSU không đổi màu, không mùi và không nhả '
                    'hóa chất. Núm ti SofTouch mô phỏng chính xác độ mềm mại và cấu trúc 3D '
                    'của ti mẹ giúp bé không bị "nhầm ti" (nipple confusion) khi chuyển đổi '
                    'bú mẹ và bú bình. Van Y-cut tự động điều chỉnh lưu lượng theo lực bú '
                    'của bé — bú nhẹ ra ít sữa, bú mạnh ra nhiều hơn, ngăn chặn chảy nhỏ '
                    'giọt và sặc sữa hoàn toàn. Cổ rộng 53mm dễ pha và vệ sinh sạch sẽ.'
                ),
            },
            {
                'slug': 'binh-sua-dung-cu', 'ten_anh': 'binh_sua_2', 'noi_bat': True,
                'ten': 'Bình sữa Philips Avent Natural 260ml núm ti tự nhiên hệ thống AirFree',
                'ma': 'CC-BS-002', 'gia': 245000, 'nhap': 165000, 'km': 219000,
                'brand': 'Philips Avent', 'xuat_xu': 'Hà Lan', 'kl': 160,
                'ngan': 'Avent Natural AirFree giảm 93% không khí nuốt vào, ngăn ngừa colic cho bé',
                'chi_tiet': (
                    'Philips Avent Natural với thiết kế đột phá: cổ bình nghiêng 69° và núm ti '
                    'đối xứng đa chiều hình vú tự nhiên — bé có thể ngậm bú từ bất kỳ góc độ '
                    'nào không cần điều chỉnh. Hệ thống van AirFree tích hợp trong ống thông '
                    'hơi trung tâm tạo áp suất âm liên tục giữ sữa luôn ngập đầu núm ti, kể '
                    'cả khi bình nghiêng nằm ngang hay dốc ngược — loại bỏ không khí trước '
                    'khi vào miệng bé. Nghiên cứu lâm sàng tại Đại học Hoàng gia London xác '
                    'nhận giảm 93% lượng không khí bé nuốt vào, giảm đáng kể colic (đau bụng '
                    'quấy khóc), ợ hơi và trào ngược. Núm ti silicon 4 cánh hoa mềm mại tự '
                    'nhiên. Nhựa PP không BPA, chịu tiệt trùng hấp và vi sóng.'
                ),
            },
            {
                'slug': 'binh-sua-dung-cu', 'ten_anh': 'binh_sua_3', 'noi_bat': False,
                'ten': "Bình sữa Dr. Brown's Options+ Wide-Neck 150ml chống đầy hơi và colic",
                'ma': 'CC-BS-003', 'gia': 215000, 'nhap': 145000, 'km': None,
                'brand': "Dr. Brown's", 'xuat_xu': 'Mỹ', 'kl': 140,
                'ngan': "Dr. Brown's ống thông hơi nội ống 2 tầng loại bỏ hoàn toàn bong bóng khí",
                'chi_tiet': (
                    "Dr. Brown's Options+ với hệ thống ống thông hơi nội ống 2 tầng được cấp "
                    'bằng sáng chế tại 40+ quốc gia — tạo ra luồng khí riêng biệt hoàn toàn '
                    'tách rời khỏi dòng sữa theo cơ chế piston. Bé bú sữa thuần túy không '
                    'lẫn bất kỳ bong bóng khí nào — loại bỏ triệt để nguyên nhân gây đầy hơi, '
                    'ợ hơi, trào ngược và colic. Nghiên cứu lâm sàng tại Johns Hopkins '
                    'University xác nhận giảm 60% triệu chứng colic. Bảo tồn tốt hơn vitamin '
                    'C và E nhạy cảm với oxy so với bình thường. Thiết kế Options+ cho phép '
                    'tháo bỏ ống thông hơi khi bé lớn hơn 3 tháng để bú với lực mạnh hơn. '
                    'Cổ rộng Wide-Neck dễ pha sữa và vệ sinh sạch sẽ. Không chứa BPA.'
                ),
            },
            {
                'slug': 'binh-sua-dung-cu', 'ten_anh': 'binh_sua_4', 'noi_bat': True,
                'ten': 'Bình sữa Comotomo Silicon Y tế 250ml mềm mô phỏng bầu ngực mẹ',
                'ma': 'CC-BS-004', 'gia': 485000, 'nhap': 340000, 'km': 449000,
                'brand': 'Comotomo', 'xuat_xu': 'Mỹ', 'kl': 200,
                'ngan': 'Bình silicon y tế siêu mềm, bóp nhẹ kiểm soát dòng sữa chủ động cho bé',
                'chi_tiet': (
                    'Comotomo là bình sữa duy nhất trên thị trường làm hoàn toàn từ silicon y '
                    'tế cấp độ cao nhất — không có lớp nhựa cứng bên trong, toàn bộ thân bình '
                    'mềm mại và ấm áp như ti mẹ thực sự. Bóp nhẹ thân bình để chủ động kiểm '
                    'soát lưu lượng sữa theo tốc độ bú của từng bé. Vành bình rộng 60mm mô '
                    'phỏng hình dạng bầu ngực mẹ giúp bé ôm miệng đúng tư thế, không bị '
                    '"nhầm ti" khi chuyển đổi bú mẹ và bú bình — đặc biệt quan trọng với '
                    'bé bú mẹ hoàn toàn. Chịu nhiệt từ -40°C đến +180°C, tiệt trùng hấp '
                    'được, vào máy rửa chén an toàn. Hai van thông hơi hai bên chống chân '
                    'không hoàn toàn. Không BPA, không BPS, không phthalate.'
                ),
            },

            # ══════════════════════════════════════════════════════════
            # GHE_NGOI_1..4 — Ghế & thiết bị
            # ══════════════════════════════════════════════════════════
            {
                'slug': 'ghe-thiet-bi-cho-be', 'ten_anh': 'ghe_ngoi_1', 'noi_bat': True,
                'ten': 'Ghế ăn dặm Aprica Yuralism 5 nấc điều chỉnh có khay và dây đai 5 điểm',
                'ma': 'CC-GHE-001', 'gia': 1250000, 'nhap': 860000, 'km': 1099000,
                'brand': 'Aprica', 'xuat_xu': 'Nhật Bản', 'kl': 5200,
                'ngan': 'Ghế ăn dặm Aprica Nhật Bản 5 nấc chiều cao, ngả 3 tư thế, dây đai 5 điểm',
                'chi_tiet': (
                    'Aprica Yuralism được thiết kế theo tiêu chuẩn an toàn và ergonomics Nhật '
                    'Bản khắt khe nhất. Khung nhôm nhẹ và thép carbon kết hợp chắc chắn, điều '
                    'chỉnh 5 nấc chiều cao từ 47cm đến 72cm phù hợp bất kỳ loại bàn ăn gia '
                    'đình nào. Tựa lưng ngả 3 tư thế: thẳng đứng 90° (ăn chính), ngả 120° '
                    '(ăn nhẹ/nghỉ) và ngả 150° (cho bú/ngủ ngắn). Dây đai an toàn 5 điểm '
                    'chuẩn châu Âu ECE R44 với khóa nút một tay tiện lợi — giữ bé an toàn '
                    'tuyệt đối kể cả khi bé cựa quậy. Hệ thống khay đôi: khay trong làm '
                    'mặt bàn ăn bé, khay ngoài chắn bảo vệ. Tháo lắp không cần dụng cụ. '
                    'Đệm ngồi dày 3cm bọc vải cotton cao cấp, tháo ra giặt máy được.'
                ),
            },
            {
                'slug': 'ghe-thiet-bi-cho-be', 'ten_anh': 'ghe_ngoi_2', 'noi_bat': False,
                'ten': 'Ghế tắm gội đa năng có tựa lưng và tựa đầu cho bé sơ sinh 0–18 tháng',
                'ma': 'CC-GHE-002', 'gia': 285000, 'nhap': 185000, 'km': 249000,
                'brand': 'Summer Infant', 'xuat_xu': 'Mỹ', 'kl': 800,
                'ngan': 'Ghế tắm bé chống trượt tựa lưng 45° giải phóng hai tay bố mẹ khi tắm cho bé',
                'chi_tiet': (
                    'Summer Infant Lil\' Luxuries giải phóng hoàn toàn hai tay bố mẹ khi tắm '
                    'bé, không cần một tay giữ một tay kỳ cọ. Tựa lưng nghiêng 45° hỗ trợ '
                    'hoàn hảo cho bé sơ sinh chưa tự ngồi vững. Đệm tựa đầu mềm mại có thể '
                    'điều chỉnh vị trí theo tuổi và kích thước đầu bé. Bề mặt ngồi có hoa '
                    'văn gân chống trơn trượt, 4 chân ghế có miếng cao su non chống trơn '
                    'đáy chậu và bồn tắm. Chất liệu nhựa PP không BPA, không độc hại tiếp '
                    'xúc trực tiếp với da bé nhạy cảm. Thiết kế gọn nhẹ, gấp phẳng lưu trữ '
                    'không chiếm không gian. Phù hợp bé từ sơ sinh đến 18 tháng (tối đa 9kg). '
                    'Vệ sinh đơn giản, lau sạch bằng khăn ướt hoặc rửa trực tiếp bằng vòi.'
                ),
            },
            {
                'slug': 'ghe-thiet-bi-cho-be', 'ten_anh': 'ghe_ngoi_3', 'noi_bat': False,
                'ten': 'Ghế rung bập bênh Fisher-Price Soothing Vibrations 5 tốc độ cho bé 0–6 tháng',
                'ma': 'CC-GHE-003', 'gia': 1850000, 'nhap': 1290000, 'km': 1650000,
                'brand': 'Fisher-Price', 'xuat_xu': 'Mỹ', 'kl': 3200,
                'ngan': 'Ghế rung 5 tốc độ + 16 giai điệu ru ngủ, giảm colic và quấy khóc cho sơ sinh',
                'chi_tiet': (
                    'Fisher-Price Soothing Vibrations với 5 mức rung êm ái mô phỏng chuyển '
                    'động nhịp nhàng khi bé còn trong bụng mẹ — cơ chế được chứng minh lâm '
                    'sàng giúp bé sơ sinh nhanh bình tĩnh và dễ đi vào giấc ngủ hơn 40% so '
                    'với không rung. Tích hợp 16 âm thanh: 8 âm thanh thiên nhiên (sóng biển, '
                    'tiếng mưa, tiếng chim...) và 8 giai điệu nhạc thiếu nhi êm dịu; bộ nhớ '
                    'âm thanh lần cuối sử dụng. Đai an toàn 3 điểm kép khóa nhanh. Thanh đồ '
                    'chơi treo 3 thú bông lắc lư kích thích thị giác và thính giác bé phát '
                    'triển. Góc ngả 3 mức từ bán nằm đến ngồi thẳng. Cần rung tháo rời được. '
                    'Dùng pin 4 AA hoặc adapter 6V (kèm theo). Phù hợp bé 0–6 tháng.'
                ),
            },
            {
                'slug': 'ghe-thiet-bi-cho-be', 'ten_anh': 'ghe_ngoi_4', 'noi_bat': False,
                'ten': 'Ghế ngồi sàn Bumbo Floor Seat 2024 có dây đai an toàn cho bé 3–12 tháng',
                'ma': 'CC-GHE-004', 'gia': 750000, 'nhap': 520000, 'km': 680000,
                'brand': 'Bumbo', 'xuat_xu': 'Nam Phi', 'kl': 1200,
                'ngan': 'Bumbo Floor Seat tập ngồi thẳng lưng tự nhiên, kích thích nhận thức bé 3–12 tháng',
                'chi_tiet': (
                    'Bumbo Floor Seat do kỹ sư người Nam Phi Jonty du Toit phát minh năm 2002, '
                    'hiện được bán tại 80+ quốc gia và giành nhiều giải thưởng thiết kế quốc '
                    'tế. Khoang ngồi hình chữ U thấp ôm sát hông và đùi bé, giữ tư thế ngồi '
                    'thẳng lưng tự nhiên hỗ trợ phát triển cơ lưng và cơ cổ mà không ép buộc. '
                    'Chất liệu polyurethane trọng lượng nhẹ đàn hồi tốt, không có góc cạnh '
                    'sắc nhọn, an toàn tuyệt đối kể cả khi bé ngã vào. Nâng cao quan điểm '
                    'nhìn của bé giúp quan sát và tương tác với thế giới xung quanh tốt hơn '
                    '— kích thích phát triển nhận thức và ngôn ngữ sớm. Kèm dây đai an toàn '
                    'phiên bản 2024. Vệ sinh dễ dàng bằng khăn ướt. Tải trọng tối đa 10kg.'
                ),
            },

            # ══════════════════════════════════════════════════════════
            # DO_CHOI_1..4 — Đồ chơi giáo dục
            # ══════════════════════════════════════════════════════════
            {
                'slug': 'do-choi-giao-duc', 'ten_anh': 'do_choi_1', 'noi_bat': True,
                'ten': 'Bộ xếp hình LEGO DUPLO Classic Brick Box 65 chi tiết cho bé 1.5–5 tuổi',
                'ma': 'CC-DCH-001', 'gia': 650000, 'nhap': 480000, 'km': 590000,
                'brand': 'LEGO DUPLO', 'xuat_xu': 'Đan Mạch', 'kl': 590,
                'ngan': 'LEGO DUPLO 65 mảnh ghép đa màu kích thước lớn, phát triển tư duy sáng tạo 3D',
                'chi_tiet': (
                    'LEGO DUPLO Classic Brick Box (10913) là bộ khởi đầu LEGO lý tưởng nhất '
                    'cho bé từ 1.5 tuổi. 65 mảnh ghép đa màu sắc kích thước lớn gấp 8 lần '
                    'LEGO thông thường — hoàn toàn an toàn, không nguy cơ nuốt. Bề mặt bo '
                    'tròn mịn màng, nhựa ABS cao cấp không BPA, không màu nhuộm độc hại. '
                    'Đạt chứng nhận an toàn EN 71 Châu Âu và ASTM F963 Mỹ. Chứa màu cơ '
                    'bản đủ để xây nhà, xe hơi, tháp cao hay bất kỳ thứ gì trí tưởng tượng '
                    'của bé nghĩ ra — phát triển tư duy không gian 3D, khả năng giải quyết '
                    'vấn đề, kỹ năng vận động tinh và sự kiên nhẫn. Hộp nhựa có tay xách và '
                    'nắp đậy tiện lưu trữ, bé tự dọn dẹp sau khi chơi. Tương thích 100% với '
                    'toàn bộ dòng sản phẩm LEGO DUPLO khác. Được chuyên gia giáo dục mầm non '
                    'khuyên dùng vì thúc đẩy học tập thông qua chơi hiệu quả.'
                ),
            },
            {
                'slug': 'do-choi-giao-duc', 'ten_anh': 'do_choi_2', 'noi_bat': False,
                'ten': 'Bộ đồ chơi nhà bếp nấu ăn mini 45 chi tiết cho bé gái 2–6 tuổi',
                'ma': 'CC-DCH-002', 'gia': 325000, 'nhap': 210000, 'km': 289000,
                'brand': 'Woby', 'xuat_xu': 'Việt Nam', 'kl': 650,
                'ngan': 'Nhà bếp mini 45 món rau củ cắt velcro phát triển kỹ năng xã hội và sáng tạo',
                'chi_tiet': (
                    'Bộ đồ chơi nhà bếp 45 món thiết kế theo phong cách Montessori, khuyến '
                    'khích học thông qua chơi và trải nghiệm thực tế. Bộ gồm nồi đôi + nắp, '
                    'chảo tay cầm, 3 dao nhựa, bộ 6 bát đĩa, muỗng nĩa, khay nướng, rổ '
                    'đựng, 12 miếng rau củ cắt được bằng velcro (cà rốt, dưa chuột, cà chua, '
                    'ớt, bắp, cam) và tạp dề nhỏ. Chất liệu nhựa ABS không BPA, màu sắc '
                    'rực rỡ bền không phai. Trò chơi nhập vai nấu ăn phát triển ngôn ngữ '
                    '(gọi tên đồ vật), kỹ năng xã hội (nấu cho người khác), trí tưởng tượng '
                    '(sáng tạo món ăn mới), sự tự tin và độc lập. Cắt rau củ velcro rèn '
                    'luyện khéo léo ngón tay chuẩn bị cho viết chữ. Hộp nhựa gọn có tay cầm.'
                ),
            },
            {
                'slug': 'do-choi-giao-duc', 'ten_anh': 'do_choi_3', 'noi_bat': False,
                'ten': 'Bảng vẽ LCD thông minh xóa được 8.5 inch cho bé 3–10 tuổi',
                'ma': 'CC-DCH-003', 'gia': 185000, 'nhap': 115000, 'km': None,
                'brand': 'Boogie Board', 'xuat_xu': 'Trung Quốc', 'kl': 280,
                'ngan': 'Bảng vẽ LCD không cần pin, không phát sáng xanh, xóa sạch một nút nhấn',
                'chi_tiet': (
                    'Bảng vẽ LCD 8.5 inch với công nghệ eWriter (Electronic Writer) tiết kiệm '
                    'điện tuyệt đối — không cần pin hay sạc điện để vẽ, chỉ tốn 1 lần năng '
                    'lượng nhỏ khi nhấn xóa. Màn hình LCD phản chiếu ánh sáng môi trường '
                    '(không tự phát sáng) — không bức xạ xanh (blue light) có hại, không '
                    'gây mỏi mắt và không làm rối loạn melatonin ảnh hưởng giấc ngủ của bé. '
                    'Bút vẽ không mực điều chỉnh độ đậm nhạt theo lực nhấn, cảm giác gần '
                    'giống viết trên giấy thật. Thay thế hoàn toàn giấy và bút — tiết kiệm '
                    'và thân thiện môi trường. Khóa màn hình tránh xóa nhầm khi bé vô tình '
                    'nhấn. Kèm giá đỡ bảng. Cho bé vẽ không giới hạn, phát triển sáng tạo '
                    'tự do mà không sợ tốn mực hay hết giấy.'
                ),
            },
            {
                'slug': 'do-choi-giao-duc', 'ten_anh': 'do_choi_4', 'noi_bat': False,
                'ten': 'Puzzle 3D gỗ 8 con vật rừng 48 mảnh kèm flashcard song ngữ cho bé 3–8 tuổi',
                'ma': 'CC-DCH-004', 'gia': 265000, 'nhap': 170000, 'km': 235000,
                'brand': 'Mideer', 'xuat_xu': 'Trung Quốc', 'kl': 420,
                'ngan': 'Puzzle 3D gỗ thông tự nhiên + flashcard Anh–Việt phát triển tư duy không gian',
                'chi_tiet': (
                    'Bộ puzzle 3D gồm 48 mảnh gỗ thông tự nhiên được cắt laser CNC chính xác '
                    'đến 0.1mm, sơn bằng màu thực phẩm gốc nước an toàn tuyệt đối. Lắp ghép '
                    'thành 8 con vật châu Phi 3D sống động đứng được: sư tử, voi, hươu cao '
                    'cổ, ngựa vằn, tê giác, hà mã, khỉ và vẹt. Mỗi con vật kèm 1 thẻ '
                    'flashcard in hình thật và tên gọi song ngữ Anh–Việt kèm phiên âm — '
                    'học từ vựng theo phương pháp hình ảnh tự nhiên nhất. Phát triển tư duy '
                    'không gian 3D, nhận diện hình dạng và màu sắc, kiên nhẫn và sự tập trung. '
                    'Mảnh ghép cạnh bo tròn an toàn cho bé 3 tuổi. Túi vải linen đựng kèm '
                    'theo tiện bảo quản và mang đi du lịch. Là quà tặng sinh nhật ý nghĩa.'
                ),
            },

            # ══════════════════════════════════════════════════════════
            # THUOC_1..4 — Thuốc & chăm sóc sức khỏe
            # ══════════════════════════════════════════════════════════
            {
                'slug': 'thuoc-suc-khoe', 'ten_anh': 'thuoc_1', 'noi_bat': False,
                'ten': 'Xịt rửa mũi Physiomer đẳng trương Baby từ nước biển Địa Trung Hải (135ml)',
                'ma': 'CC-THU-001', 'gia': 89000, 'nhap': 55000, 'km': 79000,
                'brand': 'Physiomer', 'xuat_xu': 'Pháp', 'kl': 135,
                'ngan': 'Xịt mũi sinh lý bé từ nước biển Địa Trung Hải tinh khiết, dùng được từ sơ sinh',
                'chi_tiet': (
                    'Physiomer Baby được chiết xuất từ nước biển Địa Trung Hải tinh khiết, '
                    'qua quy trình lọc màng nano loại bỏ hoàn toàn vi khuẩn, virus và tạp '
                    'chất. Nồng độ NaCl 0.9% đẳng trương hoàn toàn phù hợp áp suất thẩm '
                    'thấu của tế bào niêm mạc mũi — không gây kích ứng, không làm khô niêm '
                    'mạc khi sử dụng thường xuyên. pH 7.0–7.4 trung tính tự nhiên. Hệ thống '
                    'van đặc biệt cho phép xịt ở bất kỳ góc độ nào kể cả lộn ngược. Áp suất '
                    'xịt nhẹ nhàng được hiệu chỉnh chuyên biệt cho mũi nhỏ của trẻ sơ sinh, '
                    'không gây tổn thương niêm mạc. Làm sạch bụi bẩn, phấn hoa, vi khuẩn '
                    'trong hốc mũi, làm loãng dịch nhầy — bé thở thông, bú tốt và ngủ ngon. '
                    'Không chất bảo quản. An toàn dùng hàng ngày từ ngày đầu sau sinh.'
                ),
            },
            {
                'slug': 'thuoc-suc-khoe', 'ten_anh': 'thuoc_2', 'noi_bat': False,
                'ten': 'Kem bôi hăm tã Sudocrem Antiseptic Healing Cream 125g chống kích ứng da',
                'ma': 'CC-THU-002', 'gia': 145000, 'nhap': 95000, 'km': None,
                'brand': 'Sudocrem', 'xuat_xu': 'Anh', 'kl': 125,
                'ngan': 'Sudocrem Anh Quốc 90 năm uy tín — kem hăm tã 3 tác dụng làm dịu, dưỡng ẩm, kháng khuẩn',
                'chi_tiet': (
                    'Sudocrem được bào chế tại Dublin, Ireland từ năm 1931 bởi dược sĩ Thomas '
                    'Smith, hiện được bán tại 38 quốc gia và là kem hăm tã bán chạy nhất Vương '
                    'Quốc Anh và Ireland trong hơn 90 năm liên tiếp. Công thức độc quyền ba '
                    'tác dụng: Zinc Oxide (15.25%) tạo lớp màng vật lý chắn ẩm và làm dịu '
                    'vùng da bị kích ứng; Lanolin nước (Hypoallergenic Lanolin — dạng tinh '
                    'khiết không gây dị ứng) dưỡng ẩm sâu phục hồi hàng rào da; Benzyl '
                    'Benzoate và Benzyl Cinnamate kháng khuẩn nhẹ ngăn nhiễm trùng thứ phát. '
                    'Không steroids, không paraben, không mùi hắc nặng. Texture dạng kem '
                    'nhẹ thấm nhanh không nhờn dính. Dùng được từ sơ sinh đến người lớn.'
                ),
            },
            {
                'slug': 'thuoc-suc-khoe', 'ten_anh': 'thuoc_3', 'noi_bat': False,
                'ten': 'Nhiệt kế hồng ngoại không tiếp xúc Omron MC-720 đo trán 1 giây',
                'ma': 'CC-THU-003', 'gia': 650000, 'nhap': 450000, 'km': 589000,
                'brand': 'Omron', 'xuat_xu': 'Nhật Bản', 'kl': 120,
                'ngan': 'Nhiệt kế Omron hồng ngoại đo 1 giây ±0.2°C, lưu 60 lần đo, đèn báo 3 màu',
                'chi_tiet': (
                    'Omron MC-720 sử dụng cảm biến hồng ngoại thế hệ mới đo nhiệt độ chính '
                    'xác ±0.2°C trong chưa đến 1 giây — không cần chạm vào da bé đang ngủ. '
                    'Thuật toán bù trừ tự động tính đến nhiệt độ môi trường và khoảng cách '
                    'đo (1–3cm) để cho kết quả nhất quán trong mọi điều kiện. Chuyển đổi '
                    'thông minh 3 vị trí đo: trán, thái dương, tai với hệ số chuyển đổi riêng '
                    'từng vị trí. Bộ nhớ 60 lần đo kèm thời gian giúp theo dõi diễn biến '
                    'sốt theo thời gian thực. Đèn LED 3 màu tức thì: xanh lá (bình thường '
                    '≤37.4°C), vàng cam (sốt nhẹ 37.5–38.4°C), đỏ (sốt cao ≥38.5°C). '
                    'Chế độ im lặng — tắt âm báo đo đêm khuya không đánh thức cả nhà. '
                    'Pin AA 2 viên dùng được khoảng 3.000 lần đo. Bảo hành Omron 5 năm.'
                ),
            },
            {
                'slug': 'thuoc-suc-khoe', 'ten_anh': 'thuoc_4', 'noi_bat': False,
                'ten': 'Tinh dầu tràm Tiên Mộc Hương Huế nguyên chất 100% giữ ấm bé (30ml)',
                'ma': 'CC-THU-004', 'gia': 95000, 'nhap': 55000, 'km': 85000,
                'brand': 'Tiên Mộc Hương', 'xuat_xu': 'Việt Nam', 'kl': 30,
                'ngan': 'Tinh dầu tràm gió Huế nguyên chất chưng cất lạnh, giữ ấm và phòng cảm cho bé',
                'chi_tiet': (
                    'Tinh dầu tràm Tiên Mộc Hương được chưng cất từ lá tràm gió (Melaleuca '
                    'cajuputi) thu hái tươi tại vùng Phú Lộc, Thừa Thiên Huế — vùng tràm '
                    'nổi tiếng nhất Việt Nam với khí hậu đặc thù tạo nên chất lượng tinh dầu '
                    'cao nhất. Quy trình chưng cất lạnh (cold steam distillation) ở 40–50°C '
                    'giữ nguyên 100% thành phần hoạt chất không bị nhiệt phân hủy. Thành phần '
                    'chính 1,8-Cineole (55–65%) — hoạt chất có tác dụng kháng khuẩn mạnh '
                    '(ức chế S. aureus, E. coli), kháng virus cúm, giảm co thắt phế quản và '
                    'long đờm tự nhiên. Xoa lên lưng, ngực, gan bàn chân bé trước ngủ giúp '
                    'giữ ấm và phòng ngừa cảm lạnh. An toàn cho bé sơ sinh (pha 1:5 dầu '
                    'nền). Kiểm nghiệm GC-MS tại Viện Kiểm nghiệm Thuốc TP.HCM. Hương thơm '
                    'dịu mát tự nhiên, không hắc, không gây kích ứng đường hô hấp.'
                ),
            },
        ]

        # ── Ghi vào DB ──────────────────────────────────────────────
        self.stdout.write('\n🛍️  Thêm sản phẩm:\n')
        MA_NOI_BAT = []
        so_them = so_anh = so_skip = 0

        for p in products:
            duong_dan_anh = anh(p['ten_anh'])
            if duong_dan_anh:
                so_anh += 1

            defaults = {
                'ten':          p['ten'],
                'danh_muc':     dm[p['slug']],
                'mo_ta_ngan':   p['ngan'],
                'mo_ta_chi_tiet': p['chi_tiet'],
                'gia_ban':      p['gia'],
                'gia_nhap':     p['nhap'],
                'gia_khuyen_mai': p['km'],
                'thuong_hieu':  p['brand'],
                'xuat_xu':      p['xuat_xu'],
                'trong_luong':  p['kl'],
                'dang_ban':     True,
            }
            if duong_dan_anh:
                defaults['hinh_anh'] = duong_dan_anh

            sp, created = SanPham.objects.get_or_create(
                ma_san_pham=p['ma'], defaults=defaults
            )

            # Cập nhật ảnh nếu SP cũ chưa có ảnh
            if not created and duong_dan_anh and not sp.hinh_anh:
                sp.hinh_anh = duong_dan_anh
                sp.save()

            if created:
                so_them += 1
            else:
                so_skip += 1

            if p['noi_bat']:
                MA_NOI_BAT.append(p['ma'])

            icon = '⭐' if p['noi_bat'] else '  '
            img  = f"📷 {p['ten_anh']}" if duong_dan_anh else '  ─'
            self.stdout.write(
                f"  {icon} [{'✅' if created else '⏭️ '}] "
                f"{p['ten'][:52]:52s} {img}"
            )

        # ── Kết quả ──────────────────────────────────────────────────
        self.stdout.write('\n' + '═' * 60)
        self.stdout.write(self.style.SUCCESS(
            f'✅  HOÀN TẤT!\n'
            f'    📦 Thêm mới   : {so_them} sản phẩm\n'
            f'    ⏭️  Đã có sẵn  : {so_skip} sản phẩm\n'
            f'    📷 Ảnh gán OK : {so_anh} ảnh\n'
            f'    ⭐ Nổi bật    : {len(MA_NOI_BAT)} sản phẩm'
        ))
        self.stdout.write(f'\n👉 http://127.0.0.1:8000/')
        self.stdout.write(f'👉 http://127.0.0.1:8000/san-pham/\n')
        if not thu_muc_anh:
            self.stdout.write(self.style.WARNING(
                '💡 Đặt thư mục images/ cùng cấp manage.py rồi chạy lại để gán ảnh!'
            ))