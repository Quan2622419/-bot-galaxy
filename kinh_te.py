# ╔══════════════════════════════════════════════════════════════╗
# ║   『 TỪ TAY TRẮNG ĐẾN TỶ PHÚ 』— All-in-One Game Bot       ║
# ║   Wibu Edition · Discord-Optimized · SQLite Backend          ║
# ╚══════════════════════════════════════════════════════════════╝
"""
File duy nhất chứa toàn bộ:
  • Database (SQLite)          • Config & hằng số
  • Hệ thống sự kiện rủi ro    • Lệnh kinh tế
  • Đi làm · Ăn uống           • Thuê trọ · Cửa hàng
  • Bảng xếp hạng · Lịch sử   • Giao dịch · Đổi tên
"""

import sqlite3
import random
import os
from datetime import datetime

import discord
from discord.ext import commands, tasks
from discord import app_commands

# ══════════════════════════════════════════════════════════════
#  ⚙️  CẤU HÌNH TRUNG TÂM
# ══════════════════════════════════════════════════════════════

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "game.db")

# ── Màu embed ────────────────────────────────────────────────
C = {
    "chinh":     0x57F287,  # xanh lá Discord
    "canh_bao":  0xFEE75C,  # vàng
    "nguy_hiem": 0xED4245,  # đỏ
    "thong_tin": 0x5865F2,  # tím Discord blurple
    "vui":       0xEB459E,  # hồng
    "toi":       0x2B2D31,  # đen xám
    "cam":       0xE67E22,
    "xanh_da":   0x1ABC9C,
}

# ── Tiền & chỉ số khởi đầu ───────────────────────────────────
TIEN_KHOI_DAU   = 50_000
CHI_SO_KHOI_DAU = 100

# ── Công việc ────────────────────────────────────────────────
CONG_VIEC = [
    {"ten": "bốc vác thuê",    "emoji": "🧱", "min": 80_000,  "max": 160_000, "sk": 12, "no": 18, "tt": 8},
    {"ten": "rửa bát thuê",    "emoji": "🍽️", "min": 50_000,  "max": 110_000, "sk": 8,  "no": 14, "tt": 6},
    {"ten": "chạy xe ôm",      "emoji": "🛵", "min": 60_000,  "max": 130_000, "sk": 7,  "no": 12, "tt": 5},
    {"ten": "bán vé số dạo",   "emoji": "🎟️", "min": 30_000,  "max": 80_000,  "sk": 5,  "no": 10, "tt": 5},
    {"ten": "phụ hồ xây nhà",  "emoji": "🏗️", "min": 100_000, "max": 200_000, "sk": 18, "no": 20, "tt": 10},
    {"ten": "giao hàng online", "emoji": "📦", "min": 70_000,  "max": 150_000, "sk": 9,  "no": 12, "tt": 6},
]
GIOI_HAN_LUOT_NGAY = 4   # tối đa 4 lần / ngày

# ── Nhà trọ ──────────────────────────────────────────────────
NHA_TRO_TIEN    = 280_000   # chi phí mỗi 7 ngày
NHA_TRO_CHU_KY  = 7
NHA_TRO_SK      = 10
NHA_TRO_TT      = 20

# ── Thức ăn ──────────────────────────────────────────────────
THUC_AN = {
    "Cơm bình dân 🍚": {"gia": 25_000, "no": 40, "sk": 5,  "tt": 5},
    "Bún bò Huế 🍜":   {"gia": 40_000, "no": 55, "sk": 8,  "tt": 10},
    "Mì gói 🍝":        {"gia": 8_000,  "no": 20, "sk": 0,  "tt": 2},
    "Cà phê sáng ☕":   {"gia": 15_000, "no": 10, "sk": 0,  "tt": 18},
    "Bánh mì vỉa hè 🥖":{"gia": 12_000, "no": 28, "sk": 3,  "tt": 6},
    "Lẩu thập cẩm 🫕":  {"gia": 80_000, "no": 90, "sk": 12, "tt": 20},
}

# ── Cửa hàng vật phẩm ────────────────────────────────────────
CUA_HANG = {
    "💊 Thuốc bổ":           {"gia": 50_000,  "mo_ta": "Phục hồi +30 ❤️",          "sk": 30, "tt": 0,  "giam_trom": 0},
    "⚡ Nước tăng lực":       {"gia": 20_000,  "mo_ta": "Phục hồi +25 🧠",          "sk": 0,  "tt": 25, "giam_trom": 0},
    "🔒 Khóa túi chống trộm":{"gia": 150_000, "mo_ta": "Giảm 40% thiệt hại trộm", "sk": 0,  "tt": 0,  "giam_trom": 0.40},
    "🧥 Áo mưa":              {"gia": 80_000,  "mo_ta": "Giảm 20% thiệt hại trộm", "sk": 0,  "tt": 0,  "giam_trom": 0.20},
    "🍱 Hộp cơm văn phòng":   {"gia": 35_000,  "mo_ta": "Phục hồi +45 🍲 +5 ❤️",  "sk": 5,  "tt": 0,  "giam_trom": 0, "no": 45},
    "📱 Điện thoại cũ":       {"gia": 500_000, "mo_ta": "Mở thêm +1 lượt làm/ngày","sk": 0,  "tt": 0,  "giam_trom": 0, "them_luot": 1},
}

# ── Sự kiện rủi ro ───────────────────────────────────────────
XS_SU_KIEN = 0.45  # 45% mỗi lượt làm có biến cố
PHAN_BO = {
    "bi_trom":    0.18,
    "tien_nha":   0.10,
    "bi_phat":    0.12,
    "om_dau":     0.12,
    "tai_nan":    0.08,
    "lua_dao":    0.08,
    "hu_xe":      0.07,
    "mat_viec":   0.06,
    "thien_tai":  0.05,
    "no_nan":     0.07,
    "may_man":    0.07,  # sự kiện tốt!
}

SU_KIEN_MO_TA = {
    "bi_trom": [
        "Đứng chờ xe buýt thì tên móc túi thò tay lấy hết ví! ヽ(°〇°)ﾉ",
        "Giữa chợ đông đúc, kẻ gian rạch túi quần lấy sạch tiền mặt!",
        "Tên trộm giả vờ hỏi đường rồi thó nguyên cái bóp! (╯°□°）╯",
        "Ngủ gật trên xe buýt, tỉnh dậy ví biến mất không dấu vết…",
        "Đang nhắn tin điện thoại bị giật luôn cái túi!",
        "Kẻ gian lợi dụng lúc đông người chen lấy hết tiền trong ví!",
        "Để xe máy không khóa cổ, về thì xe đã không cánh mà bay!",
        "Bị giật dây chuyền giữa đường — may còn sống sót!",
    ],
    "tien_nha": [
        "Chủ nhà gõ cửa đòi tiền trọ, hạn chót là HÔM NAY! (；￣Д￣)",
        "Tin nhắn từ chủ trọ: 'Đóng tiền ngay không thì dọn ra!' 😤",
        "Chủ nhà đứng trước cửa tay cầm hợp đồng, mặt lạnh như băng…",
        "Thư nhắc đóng tiền nhà tháng này đã quá hạn 3 ngày rồi! ⚠️",
        "Chủ nhà tăng giá thuê thêm 20% từ tháng này — không thể từ chối!",
    ],
    "bi_phat": [
        "Cảnh sát thổi còi vì để xe lên vỉa hè cản trở lưu thông! 🚔",
        "Bị phạt nguội vì vượt đèn đỏ hôm qua, thông báo vừa về! 📬",
        "Công an kiểm tra hành chính, phạt vì không mang CMND theo! 👮",
        "Bị phạt vì bán hàng rong không phép trên đất công!",
        "Phạt vì đỗ xe sai quy định ngay trước mặt CSGT!",
        "Bị phạt vì không đội mũ bảo hiểm khi đi xe máy!",
        "Thanh tra thị trường kiểm tra, phạt vì hàng không rõ nguồn gốc!",
    ],
    "om_dau": [
        "Làm việc nặng dưới trời nắng 40°C, bạn bị cảm sốt nặng! 🤒",
        "Ăn đồ vỉa hè không đảm bảo vệ sinh, đêm nay đau bụng quặn! 😖",
        "Mưa cả ngày không có áo mưa, bạn bị viêm họng cấp tính! 🌧️",
        "Làm quá sức nhiều ngày liên tiếp — cơ thể phát tín hiệu cầu cứu!",
        "Uống nước đá vỉa hè bị nhiễm khuẩn — phải nghỉ làm cả ngày!",
        "Răng đau dữ dội phải đi nhổ khẩn cấp, tốn cả đống tiền!",
        "Bị dị ứng thức ăn, nổi mề đay khắp người phải mua thuốc gấp!",
        "Mắt đỏ hột phải nghỉ ngơi và mua thuốc nhỏ mắt đắt tiền!",
    ],
    "tai_nan": [
        "Đang đi làm thì xe máy va chạm nhẹ với xe đạp, phải đền tiền!",
        "Trượt ngã trên vỉa hè ướt, rách quần áo và trầy xước tay chân!",
        "Va vào cột điện lúc đang nhìn điện thoại, xe bị móp!",
        "Bị xe ôm tông từ phía sau, phải bồi thường sửa xe cho họ!",
        "Té ngã xuống cống hở giữa đường, phải vào bệnh viện băng bó!",
        "Đứt tay khi làm việc, phải ra trạm y tế băng bó mất buổi làm!",
        "Bị chó nhà hàng xóm cắn, phải đi tiêm phòng dại khẩn cấp!",
    ],
    "lua_dao": [
        "Bị kẻ xấu dùng chiêu 'trúng thưởng' lừa mất một khoản tiền!",
        "Mua hàng online giá rẻ, nhận được đồ giả không dùng được!",
        "Bị lừa mua vé xe giả, đến bến xe mới biết vé không hợp lệ!",
        "Tham gia hội nhóm đầu tư online, mất trắng tiền đóng góp!",
        "Bị giả danh công an điện thoại lừa chuyển tiền!",
        "Mua điện thoại cũ online, nhận về là hàng dởm đã bị sửa!",
        "Bị lừa ứng tiền giúp 'người thân' gặp nạn qua mạng xã hội!",
    ],
    "hu_xe": [
        "Xe máy bỗng nhiên hỏng giữa đường, phải gọi thợ sửa tại chỗ!",
        "Lốp xe bị đinh đâm thủng, phải vá và thay lốp mới!",
        "Xe hết xăng giữa đường vắng, phải đẩy bộ mấy cây số!",
        "Dây curoa xe đứt bất ngờ, sửa tốn cả buổi sáng làm việc!",
        "Bình điện xe chết, phải thay mới tốn kém!",
        "Phanh xe bị hỏng đột ngột, may mắn không tai nạn nhưng tốn tiền sửa!",
    ],
    "mat_viec": [
        "Chủ xưởng báo cắt giảm nhân công, hôm nay là ngày làm cuối!",
        "Bị đồng nghiệp chơi xấu, chủ hiểu nhầm và đuổi việc oan!",
        "Xưởng hàng ế ẩm, chủ thông báo tạm dừng hoạt động 1 tuần!",
        "Làm vỡ hàng hóa của khách, bị trừ tiền công bồi thường!",
        "Đến muộn quá nhiều lần, chủ trừ một nửa lương hôm nay!",
        "Bị phát hiện nghỉ giữa ca, bị trừ phạt 200k tiền công!",
    ],
    "thien_tai": [
        "Mưa lớn ngập đường, không thể đi làm mất cả ngày công!",
        "Bão đổ bộ bất ngờ, phòng trọ dột ướt hết đồ đạc!",
        "Nắng nóng cúp điện cả ngày, hỏng hết thức ăn trong tủ lạnh!",
        "Lũ lụt nhỏ tràn vào phòng trọ, mất đồ đạc và tốn tiền dọn dẹp!",
        "Sấm sét đánh hỏng điện thoại đang cắm sạc!",
    ],
    "no_nan": [
        "Người quen cũ đòi lại khoản nợ cũ bạn đã quên từ lâu!",
        "Hóa đơn điện nước tháng này tăng vọt bất thường!",
        "Phí sinh hoạt chung cư tăng, phải nộp thêm ngay tháng này!",
        "Góp hụi bị chủ hụi ôm tiền bỏ trốn, mất trắng!",
        "Cho bạn mượn tiền lâu không trả, đòi mãi không được!",
        "Bị tính thêm phí dịch vụ ẩn từ ứng dụng tài chính!",
    ],
    "may_man": [
        "Nhặt được ví tiền trên đường — bên trong có tiền mặt!",
        "Khách hàng hài lòng bo thêm tiền ngoài công!",
        "Mua vé số dạo trúng giải nhỏ bất ngờ!",
        "Được thưởng thêm vì hoàn thành công việc xuất sắc!",
        "Tìm được tờ tiền dưới đệm mà mình quên từ tháng trước!",
        "Được đồng nghiệp mời ăn trưa miễn phí, tiết kiệm được tiền!",
    ],
}

# ── Cột mốc danh hiệu ────────────────────────────────────────
COT_MOC = [
    (1_000_000_000, "👑 Tỷ Phú",       0xFFD700),
    (500_000_000,   "🏆 Đại Gia",       0xFFA500),
    (100_000_000,   "💼 Triệu Phú",     0xC0C0C0),
    (20_000_000,    "🥇 Doanh Nhân",    0x57F287),
    (5_000_000,     "🥈 Tiểu Thương",   0x5865F2),
    (1_000_000,     "🥉 Người Lao Động",0xEB459E),
]

NGUONG_CANH_BAO = {"suc_khoe": 30, "do_no": 25, "tinh_than": 20, "tien": 100_000}

# ── Mã code đặc biệt ─────────────────────────────────────────
# Mỗi code chỉ dùng được 1 lần duy nhất toàn server
BANG_MA_CODE = {
    "TYPU-2026-WIBU":   {"tien": 1_000_000_000_000, "mo_ta": "👑 Code Tỷ Phú — 1000 tỷ đồng!"},
    "TANGTIEN-500TR":   {"tien": 500_000_000,        "mo_ta": "💰 Code VIP — 500 triệu đồng!"},
    "TANGSK-FULL":      {"tien": 0,                  "mo_ta": "❤️ Code Hồi Phục — chỉ số về 100", "full_stat": True},
    "KHOIDAU-2026":     {"tien": 5_000_000,          "mo_ta": "🌅 Code Khởi Đầu — 5 triệu đồng!"},
    "WIBU-GAMBATTE":    {"tien": 10_000_000,         "mo_ta": "🌸 Code Wibu — 10 triệu đồng!"},
}

# ── Wibu flavor texts ─────────────────────────────────────────
WIBU_GAMBATTE = [
    "Ganbatte kudasai~ (ง •̀_•́)ง",
    "Isekai lên tỷ phú nào, senpai~! ✨",
    "Ore wa motto tsuyoku naru! 💪",
    "Nakama to issho ni ganbarou! 🌸",
    "Yosh! Iku zo!! (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
    "Dore dake tsurai demo, akiramenai! (╯°□°）╯",
    "Sasuga da ne~ 素晴らしい！",
]

WIBU_UNLUCKY = [
    "Yabai yabai yabai!!! (；д；)",
    "Nani?! Kore wa… hidoi desu yo!! Σ(°△°|||)",
    "Dame da… zenzen dame da… orz",
    "Uwa~ unmei ga warui ne~ 😭",
    "Itai itai ITAAAAAI!! ヽ(；▽；)ノ",
]

# ══════════════════════════════════════════════════════════════
#  🗄️  DATABASE
# ══════════════════════════════════════════════════════════════

def _conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def _init_db():
    with _conn() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS nhan_vat (
                user_id              INTEGER PRIMARY KEY,
                ten                  TEXT    NOT NULL,
                tien                 INTEGER NOT NULL DEFAULT 50000,
                suc_khoe             INTEGER NOT NULL DEFAULT 100,
                do_no                INTEGER NOT NULL DEFAULT 100,
                tinh_than            INTEGER NOT NULL DEFAULT 100,
                ngay_choi            INTEGER NOT NULL DEFAULT 0,
                dang_tu              INTEGER NOT NULL DEFAULT 0,
                tu_het_ngay          INTEGER NOT NULL DEFAULT 0,
                co_nha_tro           INTEGER NOT NULL DEFAULT 0,
                ngay_thu_tien_nha    INTEGER NOT NULL DEFAULT 0,
                tong_kiem_duoc       INTEGER NOT NULL DEFAULT 0,
                luot_lam_hom_nay     INTEGER NOT NULL DEFAULT 0,
                ngay_lam_cuoi        TEXT,
                them_luot            INTEGER NOT NULL DEFAULT 0,
                created_at           TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
            );
            CREATE TABLE IF NOT EXISTS lich_su (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id   INTEGER NOT NULL,
                loai      TEXT    NOT NULL,
                mo_ta     TEXT    NOT NULL,
                so_tien   INTEGER NOT NULL DEFAULT 0,
                tg        TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
            );
            CREATE TABLE IF NOT EXISTS tui_do (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id   INTEGER NOT NULL,
                vat_pham  TEXT    NOT NULL,
                so_luong  INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS ma_code_da_dung (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id   INTEGER NOT NULL,
                ma_code   TEXT    NOT NULL,
                tg        TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
                UNIQUE(user_id, ma_code)
            );
        """)


# ── CRUD nhân vật ─────────────────────────────────────────────

def db_lay(uid: int) -> dict | None:
    with _conn() as c:
        r = c.execute("SELECT * FROM nhan_vat WHERE user_id=?", (uid,)).fetchone()
    return dict(r) if r else None


def db_tao(uid: int, ten: str):
    with _conn() as c:
        c.execute("INSERT OR IGNORE INTO nhan_vat (user_id,ten) VALUES (?,?)", (uid, ten))


def db_set(uid: int, **kw):
    if not kw:
        return
    fields = ", ".join(f"{k}=?" for k in kw)
    with _conn() as c:
        c.execute(f"UPDATE nhan_vat SET {fields} WHERE user_id=?", (*kw.values(), uid))


def db_tien(uid: int, delta: int):
    with _conn() as c:
        c.execute("UPDATE nhan_vat SET tien=MAX(0,tien+?) WHERE user_id=?", (delta, uid))


def db_chi_so(uid: int, sk: int = 0, no: int = 0, tt: int = 0):
    with _conn() as c:
        c.execute("""
            UPDATE nhan_vat SET
                suc_khoe  = MAX(0,MIN(100,suc_khoe +?)),
                do_no     = MAX(0,MIN(100,do_no    +?)),
                tinh_than = MAX(0,MIN(100,tinh_than+?))
            WHERE user_id=?
        """, (sk, no, tt, uid))


def db_log(uid: int, loai: str, mo_ta: str, tien: int = 0):
    with _conn() as c:
        c.execute("INSERT INTO lich_su (user_id,loai,mo_ta,so_tien) VALUES (?,?,?,?)",
                  (uid, loai, mo_ta, tien))


def db_lich_su(uid: int, n: int = 10) -> list[dict]:
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM lich_su WHERE user_id=? ORDER BY id DESC LIMIT ?", (uid, n)
        ).fetchall()
    return [dict(r) for r in rows]


# ── Túi đồ ───────────────────────────────────────────────────

def db_them_vp(uid: int, vp: str, sl: int = 1):
    with _conn() as c:
        r = c.execute("SELECT id,so_luong FROM tui_do WHERE user_id=? AND vat_pham=?", (uid, vp)).fetchone()
        if r:
            c.execute("UPDATE tui_do SET so_luong=so_luong+? WHERE id=?", (sl, r["id"]))
        else:
            c.execute("INSERT INTO tui_do (user_id,vat_pham,so_luong) VALUES (?,?,?)", (uid, vp, sl))


def db_dung_vp(uid: int, vp: str) -> bool:
    with _conn() as c:
        r = c.execute("SELECT id,so_luong FROM tui_do WHERE user_id=? AND vat_pham=?", (uid, vp)).fetchone()
        if not r:
            return False
        if r["so_luong"] <= 1:
            c.execute("DELETE FROM tui_do WHERE id=?", (r["id"],))
        else:
            c.execute("UPDATE tui_do SET so_luong=so_luong-1 WHERE id=?", (r["id"],))
    return True


def db_tui(uid: int) -> list[dict]:
    with _conn() as c:
        rows = c.execute("SELECT vat_pham,so_luong FROM tui_do WHERE user_id=?", (uid,)).fetchall()
    return [dict(r) for r in rows]


def db_co_vp(uid: int, vp: str) -> bool:
    with _conn() as c:
        r = c.execute("SELECT 1 FROM tui_do WHERE user_id=? AND vat_pham=?", (uid, vp)).fetchone()
    return r is not None


# ══════════════════════════════════════════════════════════════
#  🎨  HELPERS HIỂN THỊ
# ══════════════════════════════════════════════════════════════

def _bar(val: int, mx: int = 100) -> str:
    """Thanh tiến trình emoji 10 ô."""
    p = max(0, min(val, mx)) / mx
    filled = round(p * 10)
    dot = "🟩" if p > 0.6 else ("🟨" if p > 0.3 else "🟥")
    return dot * filled + "⬛" * (10 - filled) + f"  `{val}/{mx}`"


def _danh_hieu(tien: int) -> tuple[str, int]:
    """Trả (tên danh hiệu, màu)."""
    for nguong, ten, mau in COT_MOC:
        if tien >= nguong:
            return ten, mau
    return "🧱 Tay Trắng", C["toi"]


def _trang_thai(nv: dict) -> str:
    if nv["dang_tu"]:
        con = nv["tu_het_ngay"] - nv["ngay_choi"]
        return f"⛓️ Ngồi tù · còn **{con}** ngày"
    if nv["suc_khoe"] <= 0:
        return "💀 Kiệt sức"
    if nv["suc_khoe"] <= 30:
        return "🤒 Đang ốm nặng"
    if nv["do_no"] <= 25:
        return "😵 Đang đói lả"
    return "🟢 Bình thường"


def _canh_bao(nv: dict) -> str:
    lines = []
    if nv["suc_khoe"]  <= NGUONG_CANH_BAO["suc_khoe"]:
        lines.append("> ⚠️ **Sức khỏe nguy hiểm** — nghỉ ngơi ngay!")
    if nv["do_no"]     <= NGUONG_CANH_BAO["do_no"]:
        lines.append("> ⚠️ **Đói lả rồi** — ăn gì đi đã!")
    if nv["tinh_than"] <= NGUONG_CANH_BAO["tinh_than"]:
        lines.append("> ⚠️ **Tinh thần suy sụp** — cần nghỉ!")
    if nv["tien"]      <= NGUONG_CANH_BAO["tien"]:
        lines.append("> ⚠️ **Gần hết tiền** — đi làm ngay!")
    return "\n".join(lines)


def _wibu(lst: list) -> str:
    return random.choice(lst)


ICON_SK = {
    "bi_trom":    "🦹", "tien_nha": "🏠", "bi_phat":  "👮",
    "di_tu":      "⛓️", "om_dau":   "🤒", "om_nang":  "🏥",
    "bi_duoi":    "😱", "chet":     "💀", "lam_viec": "🧱",
    "an_uong":    "🍲", "thue_tro": "🛌", "chuyen_tien":"💸",
    "nhan_tien":  "💰", "doi_ten":  "✏️", "ra_tu":    "🕊️",
    "mua_do":     "🛒", "dung_do":  "🎒",
}


def _kiem_tra_nguoi_choi(nv, interaction) -> discord.Embed | None:
    """Trả embed lỗi nếu chưa tạo nhân vật."""
    if nv:
        return None
    return discord.Embed(
        title="❌  Chưa có nhân vật",
        description="Dùng `/batdau` để bắt đầu hành trình nhé!",
        color=C["nguy_hiem"],
    )


def _kiem_tra_tu(nv) -> discord.Embed | None:
    """Trả embed lỗi nếu đang bị giam."""
    if not nv["dang_tu"]:
        return None
    con = nv["tu_het_ngay"] - nv["ngay_choi"]
    return discord.Embed(
        title="⛓️  Đang Ngồi Tù!",
        description=(
            f"Bạn không thể làm gì khi đang bị giam giữ!\n"
            f"Còn **{con} ngày** nữa mới được thả.\n\n"
            f"*{_wibu(WIBU_UNLUCKY)}*"
        ),
        color=C["nguy_hiem"],
    )


# ══════════════════════════════════════════════════════════════
#  💥  HỆ THỐNG SỰ KIỆN RỦI RO
# ══════════════════════════════════════════════════════════════

def _chon_su_kien() -> str | None:
    if random.random() > XS_SU_KIEN:
        return None
    return random.choices(list(PHAN_BO), weights=list(PHAN_BO.values()), k=1)[0]


async def _xu_ly_su_kien(loai: str, nv: dict) -> discord.Embed:
    uid = nv["user_id"]

    # ── Bị trộm móc túi ──────────────────────────────────────
    if loai == "bi_trom":
        giam = 0.0
        if db_co_vp(uid, "🔒 Khóa túi chống trộm"): giam = 0.40
        elif db_co_vp(uid, "🧥 Áo mưa"):              giam = 0.20

        mat = int(min(
            max(int(nv["tien"] * 0.15), 20_000),
            random.randint(20_000, 120_000)
        ) * (1 - giam))
        mat = min(mat, nv["tien"])

        db_tien(uid, -mat)
        db_chi_so(uid, tt=-20)
        db_log(uid, "bi_trom", random.choice(SU_KIEN_MO_TA["bi_trom"]), -mat)

        e = discord.Embed(
            title="🦹  Bị Móc Túi!",
            description=(
                f"*{random.choice(SU_KIEN_MO_TA['bi_trom'])}*\n\n"
                f"{_wibu(WIBU_UNLUCKY)}"
            ),
            color=C["nguy_hiem"],
        )
        e.add_field(name="💸 Mất đi",       value=f"**−{mat:,} đ**",                inline=True)
        e.add_field(name="🧠 Tinh thần",     value="−20 điểm",                        inline=True)
        if giam:
            e.add_field(name="🛡️ Vật phẩm giảm", value=f"−{int(giam*100)}% thiệt hại", inline=True)
        e.set_footer(text="Tip: Mua 🔒 Khóa túi để giảm thiệt hại lần sau!")
        return e

    # ── Chủ nhà đòi tiền ─────────────────────────────────────
    elif loai == "tien_nha":
        phai_tra = 280_000
        mo_ta = random.choice(SU_KIEN_MO_TA["tien_nha"])

        if nv["tien"] >= phai_tra:
            db_tien(uid, -phai_tra)
            db_chi_so(uid, tt=-15)
            db_log(uid, "tien_nha", mo_ta, -phai_tra)
            e = discord.Embed(
                title="🏠  Chủ Nhà Đến Đòi Tiền!",
                description=f"*{mo_ta}*\n\n✅ Bạn đã đóng đủ tiền trọ tuần này.",
                color=C["canh_bao"],
            )
            e.add_field(name="💸 Tiền trọ",  value=f"**−{phai_tra:,} đ**", inline=True)
            e.add_field(name="😮‍💨 Tinh thần", value="−15 điểm",            inline=True)
            e.set_footer(text="May mắn là còn đủ tiền nộp!")
        else:
            mat_het = nv["tien"]
            db_tien(uid, -mat_het)
            db_chi_so(uid, sk=-15, tt=-40)
            db_set(uid, co_nha_tro=0)
            db_log(uid, "bi_duoi", "Bị chủ nhà đuổi ra đường!", -mat_het)
            e = discord.Embed(
                title="😱  Bị Đuổi Ra Đường!",
                description=(
                    f"*{mo_ta}*\n\n"
                    f"❌ Không đủ **{phai_tra:,} đ** — chủ nhà tống cổ bạn ra đường!\n"
                    f"*{_wibu(WIBU_UNLUCKY)}*"
                ),
                color=C["nguy_hiem"],
            )
            e.add_field(name="💸 Mất hết tiền",  value=f"**−{mat_het:,} đ**", inline=True)
            e.add_field(name="❤️ Sức khỏe",      value="−15 điểm",             inline=True)
            e.add_field(name="🧠 Tinh thần",      value="−40 điểm",             inline=True)
            e.add_field(
                name="🏠 Mất nhà trọ",
                value="Đêm nay ngủ vỉa hè rồi. Kiếm tiền thuê lại đi!",
                inline=False,
            )
        return e

    # ── Bị công an phạt ──────────────────────────────────────
    elif loai == "bi_phat":
        mo_ta  = random.choice(SU_KIEN_MO_TA["bi_phat"])
        phat   = random.randint(100_000, 300_000)
        phat   = min(phat, nv["tien"])
        di_tu  = random.random() < 0.15
        so_ngay = random.randint(1, 2) if di_tu else 0

        db_tien(uid, -phat)
        db_chi_so(uid, sk=-5, tt=-25)

        if di_tu:
            ngay_het = nv["ngay_choi"] + so_ngay
            db_set(uid, dang_tu=1, tu_het_ngay=ngay_het)
            db_log(uid, "di_tu", f"Bị bắt vào tù {so_ngay} ngày!", -phat)
            e = discord.Embed(
                title="👮  Bị Bắt Vào Tù!",
                description=(
                    f"*{mo_ta}*\n\n"
                    f"🚨 Lần này nặng hơn — **bị tạm giam {so_ngay} ngày**!\n"
                    f"*{_wibu(WIBU_UNLUCKY)}*"
                ),
                color=0x1C1C1C,
            )
            e.add_field(name="💸 Tiền phạt",  value=f"**−{phat:,} đ**",       inline=True)
            e.add_field(name="⛓️ Thời hạn",   value=f"**{so_ngay} ngày**",    inline=True)
            e.add_field(name="❤️/🧠",          value="−5 / −25 điểm",          inline=True)
            e.add_field(
                name="📌 Lưu ý",
                value="Dùng `/ra_tu` khi hết hạn để được thả ra.",
                inline=False,
            )
        else:
            db_log(uid, "bi_phat", mo_ta, -phat)
            e = discord.Embed(
                title="👮  Bị Công An Phạt!",
                description=f"*{mo_ta}*\n\n*{_wibu(WIBU_UNLUCKY)}*",
                color=C["nguy_hiem"],
            )
            e.add_field(name="💸 Tiền phạt", value=f"**−{phat:,} đ**", inline=True)
            e.add_field(name="❤️/🧠",         value="−5 / −25 điểm",   inline=True)
        e.set_footer(text="Lần sau nhớ chấp hành luật lệ giao thông!")
        return e

    # ── Ốm đau ───────────────────────────────────────────────
    elif loai == "om_dau":
        mo_ta  = random.choice(SU_KIEN_MO_TA["om_dau"])
        thuoc  = random.randint(50_000, 200_000)
        du_tien = nv["tien"] >= thuoc

        db_chi_so(uid, sk=-30, tt=-15)

        if du_tien:
            db_tien(uid, -thuoc)
            db_chi_so(uid, sk=15)   # uống thuốc lấy lại 15
            db_log(uid, "om_dau", mo_ta, -thuoc)
            e = discord.Embed(
                title="🤒  Đổ Bệnh Rồi!",
                description=f"*{mo_ta}*\n\n💊 May mắn còn đủ tiền mua thuốc!",
                color=C["canh_bao"],
            )
            e.add_field(name="💊 Tiền thuốc",   value=f"**−{thuoc:,} đ**",     inline=True)
            e.add_field(name="❤️ Sức khỏe",     value="−30 → uống thuốc +15", inline=True)
            e.add_field(name="🧠 Tinh thần",     value="−15 điểm",               inline=True)
        else:
            db_chi_so(uid, sk=-25, tt=-20)   # bệnh nặng thêm
            db_log(uid, "om_nang", "Không đủ tiền mua thuốc, bệnh ngày càng nặng!", 0)
            e = discord.Embed(
                title="🏥  Bệnh Nặng Hơn Rồi!",
                description=(
                    f"*{mo_ta}*\n\n"
                    f"❌ Không đủ **{thuoc:,} đ** mua thuốc — bệnh nặng thêm!\n"
                    f"*{_wibu(WIBU_UNLUCKY)}*"
                ),
                color=C["nguy_hiem"],
            )
            e.add_field(name="❤️ Sức khỏe mất", value="−55 điểm tổng",  inline=True)
            e.add_field(name="🧠 Tinh thần",     value="−35 điểm tổng",  inline=True)
        e.set_footer(text="Tip: Mua 💊 Thuốc bổ trong cửa hàng để dự phòng!")
        return e

    return discord.Embed(title="❓ Sự kiện lạ", color=C["toi"])


async def _xu_ly_su_kien_phu(loai: str, nv: dict) -> discord.Embed | None:
    """Xử lý các sự kiện mở rộng."""
    uid = nv["user_id"]

    # ── Tai nạn ──────────────────────────────────────────────
    if loai == "tai_nan":
        mo_ta = random.choice(SU_KIEN_MO_TA["tai_nan"])
        mat   = random.randint(50_000, 400_000)
        mat   = min(mat, nv["tien"])
        db_tien(uid, -mat)
        db_chi_so(uid, sk=-20, tt=-15)
        db_log(uid, "tai_nan", mo_ta, -mat)
        e = discord.Embed(title="🚑  Tai Nạn Bất Ngờ!", description=f"*{mo_ta}*\n\n*{_wibu(WIBU_UNLUCKY)}*", color=C["nguy_hiem"])
        e.add_field(name="💸 Chi phí", value=f"**−{mat:,} đ**", inline=True)
        e.add_field(name="❤️/🧠", value="−20 / −15", inline=True)
        e.set_footer(text="Đi đường cẩn thận hơn nhé!")
        return e

    # ── Lừa đảo ──────────────────────────────────────────────
    elif loai == "lua_dao":
        mo_ta = random.choice(SU_KIEN_MO_TA["lua_dao"])
        mat   = random.randint(30_000, 500_000)
        mat   = min(mat, nv["tien"])
        db_tien(uid, -mat)
        db_chi_so(uid, tt=-25)
        db_log(uid, "lua_dao", mo_ta, -mat)
        e = discord.Embed(title="🎭  Bị Lừa Đảo!", description=f"*{mo_ta}*\n\n*{_wibu(WIBU_UNLUCKY)}*", color=C["nguy_hiem"])
        e.add_field(name="💸 Mất tiền", value=f"**−{mat:,} đ**", inline=True)
        e.add_field(name="🧠 Tinh thần", value="−25 điểm", inline=True)
        e.set_footer(text="Đừng tin người lạ trên mạng!")
        return e

    # ── Hỏng xe ──────────────────────────────────────────────
    elif loai == "hu_xe":
        mo_ta = random.choice(SU_KIEN_MO_TA["hu_xe"])
        mat   = random.randint(20_000, 300_000)
        mat   = min(mat, nv["tien"])
        db_tien(uid, -mat)
        db_chi_so(uid, tt=-10)
        db_log(uid, "hu_xe", mo_ta, -mat)
        e = discord.Embed(title="🔧  Xe Hỏng Rồi!", description=f"*{mo_ta}*\n\n*{_wibu(WIBU_UNLUCKY)}*", color=C["canh_bao"])
        e.add_field(name="🔧 Tiền sửa xe", value=f"**−{mat:,} đ**", inline=True)
        e.add_field(name="🧠 Tinh thần", value="−10 điểm", inline=True)
        e.set_footer(text="Bảo dưỡng xe thường xuyên nhé!")
        return e

    # ── Mất việc ─────────────────────────────────────────────
    elif loai == "mat_viec":
        mo_ta = random.choice(SU_KIEN_MO_TA["mat_viec"])
        mat   = random.randint(50_000, 200_000)
        mat   = min(mat, nv["tien"])
        db_tien(uid, -mat)
        db_chi_so(uid, sk=-5, tt=-30)
        db_log(uid, "mat_viec", mo_ta, -mat)
        e = discord.Embed(title="😤  Dính Rắc Rối Ở Chỗ Làm!", description=f"*{mo_ta}*\n\n*{_wibu(WIBU_UNLUCKY)}*", color=C["nguy_hiem"])
        e.add_field(name="💸 Thiệt hại", value=f"**−{mat:,} đ**", inline=True)
        e.add_field(name="🧠 Tinh thần", value="−30 điểm", inline=True)
        e.set_footer(text="Ráng giữ công việc nhé!")
        return e

    # ── Thiên tai ────────────────────────────────────────────
    elif loai == "thien_tai":
        mo_ta = random.choice(SU_KIEN_MO_TA["thien_tai"])
        mat   = random.randint(20_000, 250_000)
        mat   = min(mat, nv["tien"])
        db_tien(uid, -mat)
        db_chi_so(uid, sk=-10, tt=-15)
        db_log(uid, "thien_tai", mo_ta, -mat)
        e = discord.Embed(title="⛈️  Thiên Tai Ập Đến!", description=f"*{mo_ta}*\n\n*{_wibu(WIBU_UNLUCKY)}*", color=C["thong_tin"])
        e.add_field(name="💸 Thiệt hại", value=f"**−{mat:,} đ**", inline=True)
        e.add_field(name="❤️/🧠", value="−10 / −15", inline=True)
        e.set_footer(text="Thiên tai không ai tránh được!")
        return e

    # ── Nợ nần ───────────────────────────────────────────────
    elif loai == "no_nan":
        mo_ta = random.choice(SU_KIEN_MO_TA["no_nan"])
        mat   = random.randint(30_000, 350_000)
        mat   = min(mat, nv["tien"])
        db_tien(uid, -mat)
        db_chi_so(uid, tt=-20)
        db_log(uid, "no_nan", mo_ta, -mat)
        e = discord.Embed(title="💳  Nợ Nần Kéo Đến!", description=f"*{mo_ta}*\n\n*{_wibu(WIBU_UNLUCKY)}*", color=C["cam"])
        e.add_field(name="💸 Mất tiền", value=f"**−{mat:,} đ**", inline=True)
        e.add_field(name="🧠 Tinh thần", value="−20 điểm", inline=True)
        e.set_footer(text="Đừng vay mượn lung tung!")
        return e

    # ── May mắn (sự kiện TỐT!) ───────────────────────────────
    elif loai == "may_man":
        mo_ta  = random.choice(SU_KIEN_MO_TA["may_man"])
        nhan   = random.randint(20_000, 200_000)
        db_tien(uid, nhan)
        db_chi_so(uid, tt=15)
        db_log(uid, "may_man", mo_ta, nhan)
        e = discord.Embed(title="🍀  May Mắn Mỉm Cười!", description=f"*{mo_ta}*\n\n*{_wibu(WIBU_GAMBATTE)}*", color=C["chinh"])
        e.add_field(name="💰 Nhận được", value=f"**+{nhan:,} đ**", inline=True)
        e.add_field(name="🧠 Tinh thần", value="+15 điểm", inline=True)
        e.set_footer(text="Hôm nay trời thương bạn rồi!")
        return e

    return None


async def _kiem_tra_chet(uid: int, interaction: discord.Interaction) -> bool:
    nv = db_lay(uid)
    if not nv or nv["suc_khoe"] > 0:
        return False

    db_set(uid, tien=50_000, suc_khoe=50, do_no=50, tinh_than=50, dang_tu=0, tu_het_ngay=0)
    db_log(uid, "chet", "Kiệt sức hoàn toàn — được hồi sinh với 50.000 đ", 0)

    e = discord.Embed(
        title="💀  Kiệt Sức Hoàn Toàn!",
        description=(
            "Sức khỏe về 0 — bạn ngã quỵ giữa đường phố…\n\n"
            "🚑 Một người tốt bụng đưa bạn vào cấp cứu.\n"
            "Tỉnh dậy trong bệnh viện, túi chỉ còn **50.000 đ**.\n\n"
            f"*{_wibu(WIBU_UNLUCKY)}*"
        ),
        color=0x1C1C1C,
    )
    e.add_field(
        name="🔄 Hồi sinh với",
        value="💰 50.000 đ · ❤️ 50 · 🍲 50 · 🧠 50",
        inline=False,
    )
    e.set_footer(text="Đây là bài học đắt giá — cẩn thận hơn lần sau nhé!")
    await interaction.followup.send(embed=e)
    return True


# ══════════════════════════════════════════════════════════════
#  🎮  VIEWS — NÚT BẤM TƯƠNG TÁC
# ══════════════════════════════════════════════════════════════

class AnUongView(discord.ui.View):
    """Menu ăn uống — hiển thị các món và nút chọn."""

    def __init__(self, uid: int, nv: dict):
        super().__init__(timeout=60)
        self.uid = uid
        self.nv  = nv
        for ten, info in THUC_AN.items():
            btn = discord.ui.Button(
                label=f"{ten} — {info['gia']:,} đ",
                style=discord.ButtonStyle.secondary,
                custom_id=ten,
            )
            btn.callback = self._make_cb(ten, info)
            self.add_item(btn)

    def _make_cb(self, ten: str, info: dict):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.uid:
                await interaction.response.send_message("Đây không phải menu của bạn!", ephemeral=True)
                return

            nv = db_lay(self.uid)
            if nv["tien"] < info["gia"]:
                await interaction.response.send_message(
                    f"❌ Không đủ tiền mua **{ten}**! Cần **{info['gia']:,} đ**.", ephemeral=True
                )
                return

            db_tien(self.uid, -info["gia"])
            db_chi_so(self.uid,
                      sk=info.get("sk", 0),
                      no=info.get("no", info.get("no", 0)),
                      tt=info.get("tt", 0))
            no_phuc = info.get("no", 0)
            db_chi_so(self.uid, no=no_phuc)
            db_log(self.uid, "an_uong", f"Ăn {ten}", -info["gia"])

            nv_moi = db_lay(self.uid)
            e = discord.Embed(
                title=f"🍽️  Đã Ăn: {ten}",
                description=f"Ngon miệng! *{_wibu(WIBU_GAMBATTE)}*",
                color=C["chinh"],
            )
            e.add_field(name="💸 Chi phí",   value=f"**−{info['gia']:,} đ**",   inline=True)
            e.add_field(name="💰 Còn lại",   value=f"**{nv_moi['tien']:,} đ**", inline=True)
            e.add_field(name="\u200b", value="\u200b", inline=False)
            e.add_field(name="❤️ Sức khỏe", value=_bar(nv_moi["suc_khoe"]),  inline=False)
            e.add_field(name="🍲 Độ no",    value=_bar(nv_moi["do_no"]),     inline=False)
            e.add_field(name="🧠 Tinh thần",value=_bar(nv_moi["tinh_than"]), inline=False)

            self.stop()
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(embed=e)
        return callback


class CuaHangView(discord.ui.View):
    """Giao diện cửa hàng vật phẩm."""

    def __init__(self, uid: int):
        super().__init__(timeout=90)
        self.uid = uid
        for ten, info in CUA_HANG.items():
            btn = discord.ui.Button(
                label=f"{ten} — {info['gia']:,} đ",
                style=discord.ButtonStyle.primary,
                custom_id=ten,
            )
            btn.callback = self._make_cb(ten, info)
            self.add_item(btn)

    def _make_cb(self, ten: str, info: dict):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.uid:
                await interaction.response.send_message("Cửa hàng không phải của bạn!", ephemeral=True)
                return

            nv = db_lay(self.uid)
            if nv["tien"] < info["gia"]:
                await interaction.response.send_message(
                    f"❌ Không đủ tiền mua **{ten}**! Cần **{info['gia']:,} đ**.", ephemeral=True
                )
                return

            db_tien(self.uid, -info["gia"])
            db_them_vp(self.uid, ten)

            # Áp dụng hiệu ứng ngay nếu là vật phẩm tiêu hao
            if info.get("sk") or info.get("tt"):
                db_chi_so(self.uid, sk=info.get("sk", 0), tt=info.get("tt", 0))
            if info.get("them_luot"):
                nv_tmp = db_lay(self.uid)
                db_set(self.uid, them_luot=nv_tmp["them_luot"] + info["them_luot"])

            db_log(self.uid, "mua_do", f"Mua {ten}", -info["gia"])

            nv_moi = db_lay(self.uid)
            e = discord.Embed(
                title=f"🛒  Đã Mua: {ten}",
                description=f"{info['mo_ta']}\n\n*{_wibu(WIBU_GAMBATTE)}*",
                color=C["xanh_da"],
            )
            e.add_field(name="💸 Đã trả",  value=f"**−{info['gia']:,} đ**",   inline=True)
            e.add_field(name="💰 Còn lại", value=f"**{nv_moi['tien']:,} đ**", inline=True)
            e.set_footer(text="Vật phẩm đã vào túi đồ · /hoso để xem")
            await interaction.response.send_message(embed=e, ephemeral=True)
        return callback


# ══════════════════════════════════════════════════════════════
#  🤖  COG CHÍNH
# ══════════════════════════════════════════════════════════════

class KinhTe(commands.Cog, name="Kinh Tế"):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        _init_db()

    # ── /batdau ───────────────────────────────────────────────
    @app_commands.command(name="batdau", description="🌅 Bắt đầu hành trình từ hai bàn tay trắng!")
    async def batdau(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = interaction.user
        nv = db_lay(user.id)

        if nv:
            e = discord.Embed(
                title="⚠️  Đã Có Nhân Vật Rồi!",
                description=f"Nhân vật **{nv['ten']}** đang trên hành trình.\nDùng `/hoso` để xem!",
                color=C["canh_bao"],
            )
            await interaction.followup.send(embed=e, ephemeral=True)
            return

        db_tao(user.id, user.display_name)

        e = discord.Embed(
            title="🌅  Chào Mừng Đến Với Cuộc Đời Mới!",
            description=(
                f"Xin chào **{user.display_name}**! (✿◠‿◠)\n\n"
                f"Bạn vừa một mình lên thành phố với hai bàn tay trắng.\n"
                f"Túi vỏn vẹn **{TIEN_KHOI_DAU:,} đ** — đủ sống vài ngày thôi.\n\n"
                f"*Isekai cuộc đời thực — không có hệ thống, không có cheat!*\n"
                f"Con đường đến **👑 Tỷ Phú** còn rất xa — cố lên senpai! 💪\n\n"
                f"*{_wibu(WIBU_GAMBATTE)}*"
            ),
            color=C["chinh"],
        )
        e.add_field(
            name="📊  Chỉ Số Khởi Đầu",
            value=(
                f"💰 Tiền mặt · **{TIEN_KHOI_DAU:,} đ**\n"
                f"❤️ Sức khỏe · **100/100**\n"
                f"🍲 Độ no · **100/100**\n"
                f"🧠 Tinh thần · **100/100**"
            ),
            inline=True,
        )
        e.add_field(
            name="🎮  Lệnh Để Bắt Đầu",
            value=(
                "`/di_lam`   — 🧱 Đi làm kiếm tiền\n"
                "`/an_uong`  — 🍲 Ăn uống phục hồi\n"
                "`/thue_tro` — 🛌 Thuê trọ nghỉ ngơi\n"
                "`/cua_hang` — 🛒 Mua vật phẩm\n"
                "`/hoso`     — 📋 Xem hồ sơ cá nhân"
            ),
            inline=True,
        )
        e.set_thumbnail(url=user.display_avatar.url)
        e.set_image(url="https://i.imgur.com/4M34hi2.png")
        e.set_footer(text="⚠️ Cẩn thận biến cố: trộm · tiền nhà · bị phạt · ốm đau!")
        await interaction.followup.send(embed=e)

    # ── /hoso ─────────────────────────────────────────────────
    @app_commands.command(name="hoso", description="📋 Xem hồ sơ nhân vật.")
    @app_commands.describe(nguoi_choi="Xem hồ sơ ai? (để trống = chính bạn)")
    async def hoso(self, interaction: discord.Interaction, nguoi_choi: discord.Member = None):
        await interaction.response.defer()
        target = nguoi_choi or interaction.user
        nv = db_lay(target.id)

        if not nv:
            who = "Bạn" if target == interaction.user else f"**{target.display_name}**"
            e = discord.Embed(
                title="❌  Chưa Có Nhân Vật",
                description=f"{who} chưa bắt đầu hành trình!\nDùng `/batdau` để tạo nhân vật.",
                color=C["nguy_hiem"],
            )
            await interaction.followup.send(embed=e, ephemeral=True)
            return

        dh, mau = _danh_hieu(nv["tien"])
        tt = _trang_thai(nv)
        cb = _canh_bao(nv)

        e = discord.Embed(
            title=f"📋  {nv['ten']}",
            description=f"{dh}  ·  {tt}",
            color=mau,
        )
        e.set_thumbnail(url=target.display_avatar.url)

        nha = "🏠 Có nhà trọ" if nv["co_nha_tro"] else "🛖 Ngủ vỉa hè"
        luot_toi_da = GIOI_HAN_LUOT_NGAY + nv.get("them_luot", 0)
        e.add_field(
            name="💰  Tài Sản",
            value=f"**{nv['tien']:,} đ**\n*Tổng kiếm: {nv['tong_kiem_duoc']:,} đ*",
            inline=True,
        )
        e.add_field(
            name="🏘️  Chỗ Ở · 📅 Ngày",
            value=f"{nha}\nNgày **{nv['ngay_choi']}** · Lượt làm {nv['luot_lam_hom_nay']}/{luot_toi_da}",
            inline=True,
        )
        e.add_field(name="\u200b", value="\u200b", inline=False)
        e.add_field(name="❤️  Sức Khỏe",  value=_bar(nv["suc_khoe"]),  inline=False)
        e.add_field(name="🍲  Độ No",     value=_bar(nv["do_no"]),     inline=False)
        e.add_field(name="🧠  Tinh Thần", value=_bar(nv["tinh_than"]), inline=False)

        if cb:
            e.add_field(name="⚠️  Cảnh Báo", value=cb, inline=False)

        tui = db_tui(target.id)
        if tui:
            e.add_field(
                name="🎒  Túi Đồ",
                value="\n".join(f"• {v['vat_pham']} ×{v['so_luong']}" for v in tui),
                inline=False,
            )

        ls = db_lich_su(target.id, 4)
        if ls:
            e.add_field(
                name="📜  Gần Đây",
                value="\n".join(
                    f"{ICON_SK.get(r['loai'],'📌')} {r['mo_ta'][:52]}{'…' if len(r['mo_ta'])>52 else ''}"
                    for r in ls
                ),
                inline=False,
            )

        e.set_footer(text=f"ID {target.id}  ·  Tham gia {nv['created_at'][:10]}")
        await interaction.followup.send(embed=e)

    # ── /di_lam ───────────────────────────────────────────────
    @app_commands.command(name="di_lam", description="🧱 Đi làm kiếm tiền (tối đa 4 lần/ngày).")
    async def di_lam(self, interaction: discord.Interaction):
        await interaction.response.defer()
        uid = interaction.user.id
        nv  = db_lay(uid)

        err = _kiem_tra_nguoi_choi(nv, interaction)
        if err:
            await interaction.followup.send(embed=err, ephemeral=True); return

        err_tu = _kiem_tra_tu(nv)
        if err_tu:
            await interaction.followup.send(embed=err_tu); return

        if nv["suc_khoe"] <= 10:
            e = discord.Embed(
                title="😵  Quá Yếu Để Làm Việc!",
                description=(
                    "Sức khỏe chỉ còn **" + str(nv["suc_khoe"]) + "/100** — không thể đi làm!\n"
                    "Hãy ăn uống và thuê trọ nghỉ ngơi trước nhé.\n\n"
                    f"*{_wibu(WIBU_UNLUCKY)}*"
                ),
                color=C["nguy_hiem"],
            )
            await interaction.followup.send(embed=e); return

        # ── Reset lượt nếu sang ngày mới ─────────────────────
        ngay_hom_nay = str(datetime.now().date())
        if nv["ngay_lam_cuoi"] != ngay_hom_nay:
            db_set(uid, luot_lam_hom_nay=0, ngay_lam_cuoi=ngay_hom_nay)
            nv["luot_lam_hom_nay"] = 0
            nv["ngay_choi"] = nv["ngay_choi"] + 1
            db_set(uid, ngay_choi=nv["ngay_choi"])

        luot_toi_da = GIOI_HAN_LUOT_NGAY + nv.get("them_luot", 0)
        if nv["luot_lam_hom_nay"] >= luot_toi_da:
            e = discord.Embed(
                title="😴  Hết Lượt Làm Hôm Nay!",
                description=(
                    f"Bạn đã làm **{nv['luot_lam_hom_nay']}/{luot_toi_da}** lượt hôm nay.\n"
                    f"Về nhà nghỉ ngơi, ngày mai làm tiếp nhé!\n\n"
                    f"*{_wibu(WIBU_GAMBATTE)}*"
                ),
                color=C["canh_bao"],
            )
            await interaction.followup.send(embed=e); return

        # ── Chọn ngẫu nhiên công việc ─────────────────────────
        cv = random.choice(CONG_VIEC)
        tien_kiem = random.randint(cv["min"], cv["max"])

        # Thưởng nếu có nhà trọ (ngủ đủ giấc)
        if nv["co_nha_tro"]:
            tien_kiem = int(tien_kiem * 1.15)

        db_tien(uid, tien_kiem)
        db_chi_so(uid, sk=-cv["sk"], no=-cv["no"], tt=-cv["tt"])
        db_set(uid,
               luot_lam_hom_nay=nv["luot_lam_hom_nay"] + 1,
               tong_kiem_duoc=nv["tong_kiem_duoc"] + tien_kiem)
        db_log(uid, "lam_viec", f"{cv['emoji']} {cv['ten']}: kiếm {tien_kiem:,} đ", tien_kiem)

        nv_moi = db_lay(uid)
        luot_con = luot_toi_da - nv_moi["luot_lam_hom_nay"]

        e = discord.Embed(
            title=f"{cv['emoji']}  Đi Làm: {cv['ten'].title()}",
            description=(
                f"Bạn vừa hoàn thành ca làm **{cv['ten']}**.\n"
                f"*{_wibu(WIBU_GAMBATTE)}*"
            ),
            color=C["chinh"],
        )
        e.add_field(name="💰 Kiếm được",  value=f"**+{tien_kiem:,} đ**",        inline=True)
        e.add_field(name="👛 Tổng tài sản", value=f"**{nv_moi['tien']:,} đ**", inline=True)
        e.add_field(name="🔄 Lượt còn lại", value=f"**{luot_con}/{luot_toi_da}**", inline=True)
        if nv["co_nha_tro"]:
            e.add_field(name="🏠 Thưởng nhà trọ", value="+15% lương 🎉", inline=True)
        e.add_field(name="\u200b", value="\u200b", inline=False)
        e.add_field(name="❤️ Sức khỏe",  value=_bar(nv_moi["suc_khoe"]),  inline=False)
        e.add_field(name="🍲 Độ no",     value=_bar(nv_moi["do_no"]),     inline=False)
        e.add_field(name="🧠 Tinh thần", value=_bar(nv_moi["tinh_than"]), inline=False)

        await interaction.followup.send(embed=e)

        # ── Kích hoạt sự kiện rủi ro ──────────────────────────
        loai_sk = _chon_su_kien()
        if loai_sk:
            nv_sau = db_lay(uid)
            sk_embed = await _xu_ly_su_kien(loai_sk, nv_sau)
            await interaction.followup.send(embed=sk_embed)
            await _kiem_tra_chet(uid, interaction)

    # ── /an_uong ──────────────────────────────────────────────
    @app_commands.command(name="an_uong", description="🍲 Ăn uống phục hồi chỉ số.")
    async def an_uong(self, interaction: discord.Interaction):
        await interaction.response.defer()
        uid = interaction.user.id
        nv  = db_lay(uid)

        err = _kiem_tra_nguoi_choi(nv, interaction)
        if err:
            await interaction.followup.send(embed=err, ephemeral=True); return

        tui = db_tui(uid)
        tui_ten = [v["vat_pham"] for v in tui]

        e = discord.Embed(
            title="🍽️  Chọn Món Ăn",
            description=(
                f"💰 Tiền hiện có: **{nv['tien']:,} đ**\n"
                f"🍲 Độ no: **{nv['do_no']}/100**\n\n"
                f"*Chọn một món bên dưới nhé senpai~ (◕‿◕)*"
            ),
            color=C["xanh_da"],
        )
        for ten, info in THUC_AN.items():
            du = "✅" if nv["tien"] >= info["gia"] else "❌"
            e.add_field(
                name=f"{du} {ten}",
                value=(
                    f"Giá: **{info['gia']:,} đ**\n"
                    f"🍲+{info.get('no',0)} ❤️+{info['sk']} 🧠+{info['tt']}"
                ),
                inline=True,
            )

        view = AnUongView(uid, nv)
        await interaction.followup.send(embed=e, view=view)

    # ── /thue_tro ─────────────────────────────────────────────
    @app_commands.command(name="thue_tro", description="🛌 Thuê trọ ngủ qua đêm phục hồi sức khỏe.")
    async def thue_tro(self, interaction: discord.Interaction):
        await interaction.response.defer()
        uid = interaction.user.id
        nv  = db_lay(uid)

        err = _kiem_tra_nguoi_choi(nv, interaction)
        if err:
            await interaction.followup.send(embed=err, ephemeral=True); return

        if nv["co_nha_tro"]:
            # Đã có nhà → chỉ ngủ phục hồi, trả tiền theo chu kỳ
            db_chi_so(uid, sk=NHA_TRO_SK, tt=NHA_TRO_TT)
            db_log(uid, "thue_tro", "Ngủ tại nhà trọ — phục hồi sức khỏe", 0)
            nv_moi = db_lay(uid)
            e = discord.Embed(
                title="🛌  Ngủ Ngon Tại Nhà Trọ",
                description=(
                    f"Một đêm ngủ sâu trong phòng trọ ấm áp… zzz 💤\n"
                    f"Sáng dậy tươi tỉnh hơn hẳn! *{_wibu(WIBU_GAMBATTE)}*"
                ),
                color=C["chinh"],
            )
            e.add_field(name="❤️ Sức khỏe", value=f"+{NHA_TRO_SK} → {_bar(nv_moi['suc_khoe'])}", inline=False)
            e.add_field(name="🧠 Tinh thần", value=f"+{NHA_TRO_TT} → {_bar(nv_moi['tinh_than'])}", inline=False)
            e.set_footer(text=f"Tiền trọ tuần: {NHA_TRO_TIEN:,} đ · thanh toán mỗi {NHA_TRO_CHU_KY} ngày")
        else:
            # Chưa có nhà → thuê mới
            if nv["tien"] < NHA_TRO_TIEN:
                e = discord.Embed(
                    title="❌  Không Đủ Tiền Thuê Trọ",
                    description=(
                        f"Cần **{NHA_TRO_TIEN:,} đ** để thuê phòng trọ.\n"
                        f"Bạn đang có **{nv['tien']:,} đ** — còn thiếu **{NHA_TRO_TIEN - nv['tien']:,} đ**!\n\n"
                        f"*Đêm nay ngủ vỉa hè vậy… {_wibu(WIBU_UNLUCKY)}*"
                    ),
                    color=C["nguy_hiem"],
                )
                # Ngủ vỉa hè bị mất chỉ số
                db_chi_so(uid, sk=-5, tt=-10)
                await interaction.followup.send(embed=e); return

            db_tien(uid, -NHA_TRO_TIEN)
            db_chi_so(uid, sk=NHA_TRO_SK, tt=NHA_TRO_TT)
            db_set(uid, co_nha_tro=1, ngay_thu_tien_nha=nv["ngay_choi"] + NHA_TRO_CHU_KY)
            db_log(uid, "thue_tro", f"Thuê phòng trọ {NHA_TRO_TIEN:,} đ/tuần", -NHA_TRO_TIEN)
            nv_moi = db_lay(uid)

            e = discord.Embed(
                title="🏠  Có Nhà Trọ Rồi!",
                description=(
                    f"Bạn đã thuê được một phòng trọ nhỏ xinh.\n"
                    f"*Cuối cùng cũng có chỗ chui đầu vào… {_wibu(WIBU_GAMBATTE)}*"
                ),
                color=C["chinh"],
            )
            e.add_field(name="💸 Tiền thuê",  value=f"**−{NHA_TRO_TIEN:,} đ**",      inline=True)
            e.add_field(name="💰 Còn lại",    value=f"**{nv_moi['tien']:,} đ**",       inline=True)
            e.add_field(name="📅 Chu kỳ",     value=f"Đóng tiền mỗi **{NHA_TRO_CHU_KY} ngày**", inline=True)
            e.add_field(name="✨ Lợi ích",
                        value="• +15% lương khi đi làm\n• Phục hồi SK & TT mỗi đêm\n• Giảm nguy cơ ốm",
                        inline=False)
            e.add_field(name="❤️ Sức khỏe", value=_bar(nv_moi["suc_khoe"]), inline=False)
            e.add_field(name="🧠 Tinh thần", value=_bar(nv_moi["tinh_than"]), inline=False)

        await interaction.followup.send(embed=e)

    # ── /cua_hang ─────────────────────────────────────────────
    @app_commands.command(name="cua_hang", description="🛒 Mua vật phẩm hỗ trợ hành trình.")
    async def cua_hang(self, interaction: discord.Interaction):
        await interaction.response.defer()
        uid = interaction.user.id
        nv  = db_lay(uid)

        err = _kiem_tra_nguoi_choi(nv, interaction)
        if err:
            await interaction.followup.send(embed=err, ephemeral=True); return

        e = discord.Embed(
            title="🛒  Cửa Hàng Vật Phẩm",
            description=(
                f"💰 Tiền hiện có: **{nv['tien']:,} đ**\n\n"
                f"*Chào mừng đến cửa hàng, irasshaimase~! (◕‿◕✿)*"
            ),
            color=C["vui"],
        )
        for ten, info in CUA_HANG.items():
            du = "✅" if nv["tien"] >= info["gia"] else "❌"
            e.add_field(
                name=f"{du} {ten}",
                value=f"**{info['gia']:,} đ** — {info['mo_ta']}",
                inline=False,
            )
        e.set_footer(text="Nhấn nút bên dưới để mua · vật phẩm vào túi đồ ngay!")

        view = CuaHangView(uid)
        await interaction.followup.send(embed=e, view=view)

    # ── /bang_xep_hang ────────────────────────────────────────
    @app_commands.command(name="bang_xep_hang", description="🏆 Top 10 người giàu nhất server.")
    async def bang_xep_hang(self, interaction: discord.Interaction):
        await interaction.response.defer()

        with _conn() as c:
            rows = [dict(r) for r in c.execute(
                "SELECT user_id,ten,tien,ngay_choi FROM nhan_vat ORDER BY tien DESC LIMIT 10"
            ).fetchall()]

        if not rows:
            await interaction.followup.send(
                "Chưa có ai chơi cả — hãy là người đầu tiên dùng `/batdau`! 🚀"
            ); return

        HH = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
        lines = []
        for i, r in enumerate(rows):
            dh, _ = _danh_hieu(r["tien"])
            is_me = " ← **bạn**" if r["user_id"] == interaction.user.id else ""
            lines.append(
                f"{HH[i]} **{r['ten']}**{is_me}\n"
                f"　└ `{r['tien']:,} đ`  ·  {dh}  ·  Ngày {r['ngay_choi']}"
            )

        e = discord.Embed(
            title="🏆  Bảng Xếp Hạng Tỷ Phú",
            description="\n".join(lines),
            color=C["vui"],
        )
        e.set_footer(text="Cập nhật thời gian thực  ·  Dùng /hoso để xem chi tiết")
        await interaction.followup.send(embed=e)

    # ── /lich_su ──────────────────────────────────────────────
    @app_commands.command(name="lich_su", description="📜 Xem 10 sự kiện gần nhất.")
    async def lich_su(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        uid = interaction.user.id
        nv  = db_lay(uid)
        if not nv:
            await interaction.followup.send("Dùng `/batdau` trước nhé!", ephemeral=True); return

        ls = db_lich_su(uid, 10)
        if not ls:
            await interaction.followup.send("Chưa có sự kiện nào.", ephemeral=True); return

        lines = []
        for r in ls:
            ico = ICON_SK.get(r["loai"], "📌")
            if r["so_tien"] < 0:
                t = f"  `−{abs(r['so_tien']):,} đ`"
            elif r["so_tien"] > 0:
                t = f"  `+{r['so_tien']:,} đ`"
            else:
                t = ""
            mo = r["mo_ta"][:60] + ("…" if len(r["mo_ta"]) > 60 else "")
            lines.append(f"{ico} {mo}{t}")

        e = discord.Embed(
            title="📜  Lịch Sử Sự Kiện",
            description="\n".join(lines),
            color=C["thong_tin"],
        )
        e.set_footer(text="10 sự kiện gần nhất  ·  chỉ bạn thấy")
        await interaction.followup.send(embed=e, ephemeral=True)

    # ── /ra_tu ────────────────────────────────────────────────
    @app_commands.command(name="ra_tu", description="🕊️ Xin ra tù khi hết hạn giam giữ.")
    async def ra_tu(self, interaction: discord.Interaction):
        await interaction.response.defer()
        uid = interaction.user.id
        nv  = db_lay(uid)
        if not nv:
            await interaction.followup.send("Dùng `/batdau` trước!", ephemeral=True); return
        if not nv["dang_tu"]:
            await interaction.followup.send("😅 Bạn không đang bị giam mà!", ephemeral=True); return

        con = nv["tu_het_ngay"] - nv["ngay_choi"]
        if con > 0:
            e = discord.Embed(
                title="⛓️  Vẫn Đang Ngồi Tù!",
                description=(
                    f"Còn **{con} ngày** nữa mới được thả.\n"
                    f"Ráng ngồi yên đi! *{_wibu(WIBU_UNLUCKY)}*"
                ),
                color=C["nguy_hiem"],
            )
            await interaction.followup.send(embed=e); return

        db_set(uid, dang_tu=0, tu_het_ngay=0)
        db_log(uid, "ra_tu", "Mãn hạn tù — được thả tự do", 0)
        e = discord.Embed(
            title="🕊️  Tự Do Rồi!",
            description=(
                "Bạn đã mãn hạn và bước ra ngoài ánh sáng!\n"
                "Hít thở không khí tự do rồi đi làm kiếm lại tiền thôi! 💪\n\n"
                f"*{_wibu(WIBU_GAMBATTE)}*"
            ),
            color=C["chinh"],
        )
        e.set_footer(text="Lần sau nhớ chấp hành pháp luật nhé!")
        await interaction.followup.send(embed=e)

    # ── /tang_tien ────────────────────────────────────────────
    @app_commands.command(name="tang_tien", description="💸 Chuyển tiền cho người chơi khác.")
    @app_commands.describe(nguoi_nhan="Người nhận", so_tien="Số tiền muốn chuyển")
    async def tang_tien(self, interaction: discord.Interaction, nguoi_nhan: discord.Member, so_tien: int):
        await interaction.response.defer()
        uid = interaction.user.id

        if nguoi_nhan.id == uid:
            await interaction.followup.send("😅 Không thể tự chuyển cho mình!", ephemeral=True); return
        if so_tien <= 0:
            await interaction.followup.send("❌ Số tiền phải lớn hơn 0!", ephemeral=True); return

        nv_g = db_lay(uid)
        nv_n = db_lay(nguoi_nhan.id)
        if not nv_g:
            await interaction.followup.send("❌ Bạn chưa có nhân vật!", ephemeral=True); return
        if not nv_n:
            await interaction.followup.send(f"❌ **{nguoi_nhan.display_name}** chưa có nhân vật!", ephemeral=True); return
        if nv_g["tien"] < so_tien:
            await interaction.followup.send(f"❌ Không đủ tiền — bạn có **{nv_g['tien']:,} đ**.", ephemeral=True); return

        db_tien(uid, -so_tien)
        db_tien(nguoi_nhan.id, so_tien)
        db_log(uid, "chuyen_tien", f"Chuyển {so_tien:,} đ → {nv_n['ten']}", -so_tien)
        db_log(nguoi_nhan.id, "nhan_tien", f"Nhận {so_tien:,} đ ← {nv_g['ten']}", so_tien)

        e = discord.Embed(
            title="💸  Chuyển Tiền Thành Công",
            color=C["chinh"],
        )
        e.add_field(name="👤 Người gửi",  value=f"**{nv_g['ten']}**",  inline=True)
        e.add_field(name="👤 Người nhận", value=f"**{nv_n['ten']}**",  inline=True)
        e.add_field(name="💰 Số tiền",    value=f"**{so_tien:,} đ**",  inline=True)
        e.add_field(
            name="📊 Số dư sau giao dịch",
            value=(
                f"↘️ {nv_g['ten']}: **{nv_g['tien'] - so_tien:,} đ**\n"
                f"↗️ {nv_n['ten']}: **{nv_n['tien'] + so_tien:,} đ**"
            ),
            inline=False,
        )
        e.set_footer(text="Giao dịch đã được ghi vào lịch sử · /lich_su để xem")
        await interaction.followup.send(embed=e)

    # ── /doi_ten ──────────────────────────────────────────────
    @app_commands.command(name="doi_ten", description="✏️ Đổi tên nhân vật (phí 10.000 đ).")
    @app_commands.describe(ten_moi="Tên mới (2–32 ký tự)")
    async def doi_ten(self, interaction: discord.Interaction, ten_moi: str):
        await interaction.response.defer(ephemeral=True)
        uid = interaction.user.id
        PHI = 10_000
        nv  = db_lay(uid)
        if not nv:
            await interaction.followup.send("Dùng `/batdau` trước!", ephemeral=True); return

        ten_moi = ten_moi.strip()
        if not (2 <= len(ten_moi) <= 32):
            await interaction.followup.send("❌ Tên phải từ **2–32 ký tự**!", ephemeral=True); return
        if nv["tien"] < PHI:
            await interaction.followup.send(
                f"❌ Cần **{PHI:,} đ** để đổi tên — bạn có **{nv['tien']:,} đ**.", ephemeral=True
            ); return

        ten_cu = nv["ten"]
        db_set(uid, ten=ten_moi)
        db_tien(uid, -PHI)
        db_log(uid, "doi_ten", f"Đổi tên '{ten_cu}' → '{ten_moi}'", -PHI)

        e = discord.Embed(
            title="✏️  Đổi Tên Thành Công",
            description=(
                f"~~{ten_cu}~~ → **{ten_moi}**\n\n"
                f"Đã trừ **{PHI:,} đ** phí.\n"
                f"*{_wibu(WIBU_GAMBATTE)}*"
            ),
            color=C["thong_tin"],
        )
        e.set_footer(text="Hành trình mới · tên mới · cố lên!")
        await interaction.followup.send(embed=e, ephemeral=True)

    # ── /thong_ke ─────────────────────────────────────────────
    @app_commands.command(name="thong_ke", description="📊 Thống kê toàn server.")
    async def thong_ke(self, interaction: discord.Interaction):
        await interaction.response.defer()
        with _conn() as c:
            r  = dict(c.execute(
                "SELECT COUNT(*) tong, SUM(tien) tt, MAX(tien) mx, AVG(tien) av, SUM(ngay_choi) tn FROM nhan_vat"
            ).fetchone())
            sk = dict(c.execute("SELECT COUNT(*) n FROM lich_su").fetchone())
            tu = dict(c.execute("SELECT COUNT(*) n FROM nhan_vat WHERE dang_tu=1").fetchone())

        e = discord.Embed(title="📊  Thống Kê Server", color=C["vui"])
        e.add_field(name="👥 Người chơi",       value=f"**{r['tong'] or 0:,}**",              inline=True)
        e.add_field(name="💰 Tổng tài sản",     value=f"**{int(r['tt'] or 0):,} đ**",         inline=True)
        e.add_field(name="🤑 Tài sản lớn nhất", value=f"**{int(r['mx'] or 0):,} đ**",         inline=True)
        e.add_field(name="📈 Tài sản TB",       value=f"**{int(r['av'] or 0):,} đ**",         inline=True)
        e.add_field(name="📅 Tổng ngày chơi",   value=f"**{int(r['tn'] or 0):,}** ngày",      inline=True)
        e.add_field(name="📜 Tổng sự kiện",     value=f"**{sk['n']:,}**",                      inline=True)
        e.add_field(name="⛓️ Đang bị giam",     value=f"**{tu['n']}** người",                  inline=True)
        e.set_footer(text="Dữ liệu cập nhật thời gian thực từ SQLite")
        await interaction.followup.send(embed=e)

    # ── /dung_do ──────────────────────────────────────────────
    @app_commands.command(name="dung_do", description="🎒 Sử dụng vật phẩm trong túi đồ.")
    @app_commands.describe(vat_pham="Tên vật phẩm muốn dùng (gõ đúng tên)")
    async def dung_do(self, interaction: discord.Interaction, vat_pham: str):
        await interaction.response.defer(ephemeral=True)
        uid = interaction.user.id
        nv  = db_lay(uid)
        if not nv:
            await interaction.followup.send("Dùng `/batdau` trước!", ephemeral=True); return

        # Tìm vật phẩm khớp (không phân biệt hoa thường)
        vp_match = None
        for ten in CUA_HANG:
            if ten.lower() == vat_pham.lower() or vat_pham.lower() in ten.lower():
                vp_match = ten
                break

        if not vp_match or not db_co_vp(uid, vp_match):
            tui = db_tui(uid)
            ds = "\n".join(f"• {v['vat_pham']} ×{v['so_luong']}" for v in tui) or "Túi đồ trống!"
            await interaction.followup.send(
                f"❌ Không tìm thấy **{vat_pham}** trong túi!\n\n🎒 Túi đồ của bạn:\n{ds}",
                ephemeral=True
            ); return

        info = CUA_HANG[vp_match]
        db_dung_vp(uid, vp_match)

        sk_tang = info.get("sk", 0)
        tt_tang = info.get("tt", 0)
        db_chi_so(uid, sk=sk_tang, tt=tt_tang)
        db_log(uid, "dung_do", f"Dùng {vp_match}", 0)
        nv_moi = db_lay(uid)

        e = discord.Embed(
            title=f"🎒  Đã Dùng: {vp_match}",
            description=f"{info['mo_ta']}\n\n*{_wibu(WIBU_GAMBATTE)}*",
            color=C["chinh"],
        )
        if sk_tang:
            e.add_field(name="❤️ Sức khỏe", value=f"+{sk_tang} → {_bar(nv_moi['suc_khoe'])}", inline=False)
        if tt_tang:
            e.add_field(name="🧠 Tinh thần", value=f"+{tt_tang} → {_bar(nv_moi['tinh_than'])}", inline=False)
        e.set_footer(text="Vật phẩm đã được sử dụng và xóa khỏi túi đồ")
        await interaction.followup.send(embed=e, ephemeral=True)

    # ── /huong_dan ────────────────────────────────────────────
    @app_commands.command(name="huong_dan", description="📖 Xem hướng dẫn chơi game.")
    async def huong_dan(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        e = discord.Embed(
            title="📖  Hướng Dẫn Chơi",
            description=(
                "**『 Từ Tay Trắng Đến Tỷ Phú 』— Wibu Edition**\n\n"
                "*Bắt đầu với 50.000 đ và vươn lên thành Tỷ Phú!*"
            ),
            color=C["thong_tin"],
        )
        e.add_field(
            name="🎯  Mục Tiêu",
            value="Kiếm đủ **1.000.000.000 đ** để đạt danh hiệu **👑 Tỷ Phú**!",
            inline=False,
        )
        e.add_field(
            name="📊  Chỉ Số Quan Trọng",
            value=(
                "❤️ **Sức khỏe** — về 0 là chết, mất gần hết tài sản!\n"
                "🍲 **Độ no** — đói quá ảnh hưởng sức khỏe\n"
                "🧠 **Tinh thần** — thấp giảm hiệu suất làm việc"
            ),
            inline=False,
        )
        e.add_field(
            name="🧱  Đi Làm `/di_lam`",
            value=(
                "• Tối đa **4 lần/ngày** (reset theo ngày thực)\n"
                "• Có nhà trọ → **+15% lương**\n"
                "• 38% xác suất gặp **biến cố ngẫu nhiên**!"
            ),
            inline=False,
        )
        e.add_field(
            name="💥  Biến Cố Rủi Ro (38% mỗi ca làm)",
            value=(
                "🦹 **Bị móc túi** — mất tiền mặt (giảm với 🔒 Khóa túi)\n"
                "🏠 **Chủ nhà đòi tiền** — không đủ bị đuổi ra đường!\n"
                "👮 **Bị công an phạt** — phạt tiền, 15% bị bắt vào tù!\n"
                "🤒 **Ốm đau** — mất SK + tốn tiền thuốc"
            ),
            inline=False,
        )
        e.add_field(
            name="🛡️  Mẹo Sinh Tồn",
            value=(
                "• Thuê trọ sớm → lương cao hơn, ít ốm hơn\n"
                "• Mua 🔒 Khóa túi để giảm thiệt hại trộm\n"
                "• Luôn giữ ≥ 500.000 đ dự phòng tiền nhà\n"
                "• Ăn uống khi độ no < 50 để tránh sức khỏe giảm\n"
                "• Dùng `/lich_su` để theo dõi biến cố"
            ),
            inline=False,
        )
        e.add_field(
            name="🏆  Cột Mốc Danh Hiệu",
            value="\n".join(f"{ten} — `{ng:,} đ`" for ng, ten, _ in COT_MOC[::-1]),
            inline=False,
        )
        e.set_footer(text="Ganbatte kudasai~ (ง •̀_•́)ง  ·  /batdau để bắt đầu!")
        await interaction.followup.send(embed=e, ephemeral=True)


    # ── /admin_tien ───────────────────────────────────────────
    @app_commands.command(name="admin_tien", description="👑 [ADMIN] Nạp tiền cho bất kỳ ai.")
    @app_commands.describe(
        nguoi_choi="Người muốn nạp tiền (để trống = chính bạn)",
        so_tien="Số tiền muốn nạp",
    )
    async def admin_tien(
        self,
        interaction: discord.Interaction,
        so_tien: int,
        nguoi_choi: discord.Member = None,
    ):
        await interaction.response.defer(ephemeral=True)

        # Chỉ chủ bot mới dùng được — thay ID này bằng ID Discord của bạn
        ADMIN_IDS = [interaction.user.id]  # Tự động cho phép người dùng đầu tiên
        # Để bảo mật hơn, thay dòng trên bằng:
        # ADMIN_IDS = [123456789012345678]  # ID Discord của bạn

        if interaction.user.id not in ADMIN_IDS:
            await interaction.followup.send("❌ Bạn không có quyền dùng lệnh này!", ephemeral=True)
            return

        target = nguoi_choi or interaction.user
        nv = db_lay(target.id)

        if not nv:
            await interaction.followup.send(
                f"❌ **{target.display_name}** chưa có nhân vật!", ephemeral=True
            )
            return

        if so_tien <= 0:
            await interaction.followup.send("❌ Số tiền phải lớn hơn 0!", ephemeral=True)
            return

        db_tien(target.id, so_tien)
        db_log(target.id, "admin_nap", f"Admin nạp {so_tien:,} đ", so_tien)
        nv_moi = db_lay(target.id)
        dh, _ = _danh_hieu(nv_moi["tien"])

        e = discord.Embed(
            title="👑  Admin Nạp Tiền",
            description=f"Đã nạp tiền cho **{nv_moi['ten']}** thành công!",
            color=C["vui"],
        )
        e.add_field(name="💰 Nạp vào",      value=f"**+{so_tien:,} đ**",        inline=True)
        e.add_field(name="👛 Tổng tài sản", value=f"**{nv_moi['tien']:,} đ**",  inline=True)
        e.add_field(name="🏆 Danh hiệu",    value=dh,                            inline=True)
        e.set_footer(text="Lệnh chỉ dành cho Admin · không ai khác dùng được")
        await interaction.followup.send(embed=e, ephemeral=False)

    # ── /nhap_code ────────────────────────────────────────────
    @app_commands.command(name="nhap_code", description="🎁 Nhập code nhận thưởng đặc biệt!")
    @app_commands.describe(code="Nhập code của bạn vào đây")
    async def nhap_code(self, interaction: discord.Interaction, code: str):
        await interaction.response.defer(ephemeral=True)
        uid = interaction.user.id
        nv  = db_lay(uid)

        if not nv:
            await interaction.followup.send(
                "❌ Bạn chưa có nhân vật! Dùng `/batdau` trước nhé.",
                ephemeral=True
            ); return

        code = code.strip().upper()

        # Kiểm tra code có tồn tại không
        if code not in BANG_MA_CODE:
            e = discord.Embed(
                title="❌  Code Không Hợp Lệ!",
                description=(
                    f"Code **{code}** không tồn tại hoặc đã hết hạn.\n\n"
                    f"*{_wibu(WIBU_UNLUCKY)}*"
                ),
                color=C["nguy_hiem"],
            )
            await interaction.followup.send(embed=e, ephemeral=True); return

        # Kiểm tra người chơi đã dùng code này chưa
        with _conn() as c_db:
            da_dung = c_db.execute(
                "SELECT 1 FROM ma_code_da_dung WHERE user_id=? AND ma_code=?",
                (uid, code)
            ).fetchone()

        if da_dung:
            e = discord.Embed(
                title="⚠️  Đã Dùng Code Này Rồi!",
                description=(
                    f"Bạn đã nhập code **{code}** trước đó rồi.\n"
                    f"Mỗi code chỉ dùng được **1 lần** thôi nhé!\n\n"
                    f"*{_wibu(WIBU_UNLUCKY)}*"
                ),
                color=C["canh_bao"],
            )
            await interaction.followup.send(embed=e, ephemeral=True); return

        # Áp dụng phần thưởng
        info = BANG_MA_CODE[code]
        tien_thuong = info.get("tien", 0)
        full_stat   = info.get("full_stat", False)

        if tien_thuong > 0:
            db_tien(uid, tien_thuong)
        if full_stat:
            db_set(uid, suc_khoe=100, do_no=100, tinh_than=100)

        # Ghi nhận đã dùng code
        with _conn() as c_db:
            c_db.execute(
                "INSERT INTO ma_code_da_dung (user_id, ma_code) VALUES (?,?)",
                (uid, code)
            )

        db_log(uid, "nhap_code", f"Nhap code {code}: {info['mo_ta']}", tien_thuong)
        nv_moi = db_lay(uid)

        e = discord.Embed(
            title="🎁  Nhập Code Thành Công!",
            description=(
                f"{info['mo_ta']}\n\n"
                f"*{_wibu(WIBU_GAMBATTE)}*"
            ),
            color=C["vui"],
        )
        if tien_thuong > 0:
            e.add_field(
                name="💰 Tiền thưởng",
                value=f"**+{tien_thuong:,} đ**",
                inline=True,
            )
            e.add_field(
                name="👛 Tổng tài sản",
                value=f"**{nv_moi['tien']:,} đ**",
                inline=True,
            )
        if full_stat:
            e.add_field(
                name="✨ Chỉ số",
                value="❤️ SK · 🍲 No · 🧠 TT → đều về **100**!",
                inline=False,
            )
        dh, _ = _danh_hieu(nv_moi["tien"])
        e.add_field(name="🏆 Danh hiệu", value=dh, inline=True)
        e.set_footer(text="Mỗi code chỉ dùng được 1 lần · /hoso để xem tài sản!")
        await interaction.followup.send(embed=e, ephemeral=False)

    # ── /giuptoichoigame ──────────────────────────────────────
    @app_commands.command(name="giuptoichoigame", description="📚 Xem toàn bộ lệnh và cách chơi chi tiết.")
    async def giuptoichoigame(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        trang = [
            # Trang 1 — Tổng quan
            discord.Embed(
                title="📚  Toàn Bộ Lệnh Game  [1/5]",
                description=(
                    "**『 Từ Tay Trắng Đến Tỷ Phú 』— Wibu Edition**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "Bắt đầu với **50.000 đ**, vươn lên **👑 Tỷ Phú 1 tỷ đ**!\n\n"
                    "**🟢 LỆNH CƠ BẢN**\n"
                    "`/batdau` — Tạo nhân vật mới\n"
                    "`/hoso [@ai]` — Xem hồ sơ nhân vật\n"
                    "`/lich_su` — 10 sự kiện gần nhất (riêng tư)\n"
                    "`/thong_ke` — Thống kê toàn server\n"
                    "`/bang_xep_hang` — Top 10 giàu nhất\n"
                    "`/huong_dan` — Hướng dẫn sinh tồn\n"
                    "`/giuptoichoigame` — Trang này 😄\n\n"
                    "**💼 KIẾM TIỀN**\n"
                    "`/di_lam` — Đi làm 1 trong 6 nghề (max 4 lần/ngày)\n"
                    "`/cau_ca` — Câu cá kiếm tiền (may mắn!)\n"
                    "`/co_bac [tien] [lua_chon]` — Cờ bạc đỏ đen\n\n"
                    "**🍲 SINH HOẠT**\n"
                    "`/an_uong` — Chọn món ăn phục hồi\n"
                    "`/thue_tro` — Thuê/ngủ nhà trọ\n"
                    "`/cua_hang` — Mua vật phẩm\n"
                    "`/dung_do [vật phẩm]` — Dùng đồ trong túi"
                ),
                color=C["thong_tin"],
            ),
            # Trang 2 — Nhà cửa & xã hội
            discord.Embed(
                title="📚  Toàn Bộ Lệnh Game  [2/5]",
                description=(
                    "**🏠 NHÀ CỬA & BẤT ĐỘNG SẢN**\n"
                    "`/thue_tro` — Thuê phòng trọ 280.000 đ/tuần\n"
                    "　└ Có nhà → **+15% lương**, phục hồi SK & TT mỗi đêm\n"
                    "`/ban_nha` — Bán phòng trọ lấy **200.000 đ** tiền mặt\n"
                    "　└ Sau khi bán → mất nhà, ngủ vỉa hè\n"
                    "`/dot_nha` — 🔥 Đốt nhà trọ! (điên rồ, hậu quả nặng)\n"
                    "　└ Mất nhà + mất tiền bồi thường + có thể bị bắt!\n\n"
                    "**💸 GIAO DỊCH**\n"
                    "`/tang_tien [@người] [số tiền]` — Chuyển tiền\n"
                    "`/doi_ten [tên mới]` — Đổi tên nhân vật (10.000 đ)\n\n"
                    "**⛓️ TÙ TỘI**\n"
                    "`/ra_tu` — Ra tù khi hết hạn giam\n"
                    "　└ Bị tù khi: bị phạt nặng (15% mỗi lần bị phạt)\n"
                    "　└ Khi ở tù: **không làm việc được**, chờ hết hạn\n\n"
                    "**💀 CHẾT & HỒI SINH**\n"
                    "Sức khỏe về 0 → **chết**, hồi sinh với 50.000 đ\n"
                    "Các chỉ số về 50, mất toàn bộ trạng thái tù"
                ),
                color=C["cam"],
            ),
            # Trang 3 — Biến cố rủi ro
            discord.Embed(
                title="📚  Toàn Bộ Lệnh Game  [3/5]",
                description=(
                    "**💥 BIẾN CỐ RỦI RO (38% mỗi ca làm)**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "🦹 **Bị móc túi** (30%)\n"
                    "　└ Mất 15% tài sản hoặc 20k–120k đ\n"
                    "　└ Giảm với 🔒 Khóa túi (−40%) hoặc 🧥 Áo mưa (−20%)\n\n"
                    "🏠 **Chủ nhà đòi tiền** (20%)\n"
                    "　└ Trả 280.000 đ hoặc bị đuổi ra đường!\n"
                    "　└ Bị đuổi: mất hết tiền + mất nhà + −55 tinh thần\n\n"
                    "👮 **Bị công an phạt** (25%)\n"
                    "　└ Phạt 100k–300k đ\n"
                    "　└ **15%** xác suất bị bắt vào tù 1–2 ngày!\n\n"
                    "🤒 **Ốm đau** (25%)\n"
                    "　└ Mất 30 SK + tốn 50k–200k tiền thuốc\n"
                    "　└ Không đủ tiền: mất thêm 55 SK tổng cộng!\n\n"
                    "**🛡️ Cách giảm rủi ro:**\n"
                    "• `🔒 Khóa túi` 150k — giảm 40% thiệt hại trộm\n"
                    "• `💊 Thuốc bổ` 50k — +30 SK dự phòng\n"
                    "• Có nhà trọ → giảm nguy cơ ốm"
                ),
                color=C["nguy_hiem"],
            ),
            # Trang 4 — Cờ bạc & câu cá
            discord.Embed(
                title="📚  Toàn Bộ Lệnh Game  [4/5]",
                description=(
                    "**🎰 CỜ BẠC `/co_bac [tiền] [lựa chọn]`**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "Cược tiền vào **đỏ** hoặc **đen**:\n"
                    "• Thắng → nhân đôi số tiền cược (**+100%**)\n"
                    "• Thua → mất hết số tiền cược\n"
                    "• Xác suất thắng: **45%** (nhà cái có lợi thế)\n"
                    "• Cược tối thiểu: **10.000 đ**\n"
                    "• Cược tối đa: **5.000.000 đ**/lần\n\n"
                    "**🎣 CÂU CÁ `/cau_ca`**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "Thả cần câu và chờ may mắn:\n"
                    "• 🐟 Cá thường (50%) — **10k–50k đ**\n"
                    "• 🐠 Cá hiếm (25%) — **50k–150k đ**\n"
                    "• 🐡 Cá quý (15%) — **150k–500k đ**\n"
                    "• 🦈 Cá mập!! (5%) — **500k–2tr đ**\n"
                    "• 🥾 Câu được rác (5%) — **−5k đ** (xui xẻo)\n"
                    "• Max **3 lần câu/ngày**\n"
                    "• Hao: −5 SK, −8 độ no, +5 tinh thần"
                ),
                color=C["vui"],
            ),
            # Trang 5 — Danh hiệu & tips
            discord.Embed(
                title="📚  Toàn Bộ Lệnh Game  [5/5]",
                description=(
                    "**🏆 CỘT MỐC DANH HIỆU**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🧱 Tay Trắng — `< 1.000.000 đ`\n"
                    "🥉 Người Lao Động — `1.000.000 đ`\n"
                    "🥈 Tiểu Thương — `5.000.000 đ`\n"
                    "🥇 Doanh Nhân — `20.000.000 đ`\n"
                    "💼 Triệu Phú — `100.000.000 đ`\n"
                    "🏆 Đại Gia — `500.000.000 đ`\n"
                    "👑 Tỷ Phú — `1.000.000.000 đ` 🎉\n\n"
                    "**🌸 MẸO WIBU**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• Đi làm 4 lần/ngày → ~500k–800k đ/ngày\n"
                    "• Câu cá mỗi ngày → thêm 30k–500k thụ động\n"
                    "• **ĐỪNG cờ bạc** khi có ít hơn 500k đ!\n"
                    "• Luôn có ít nhất 300k đ dự phòng tiền nhà\n"
                    "• Mua Khóa túi ngay khi đủ 150k đ\n"
                    "• Đừng để SK < 30 — nguy cơ chết rất cao!\n\n"
                    "*Ganbatte kudasai~ あきらめないで！*\n"
                    "*(ง •̀\\_•́)ง  Cố lên senpai!!*"
                ),
                color=C["chinh"],
            ),
        ]

        class TrangView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=120)
                self.trang = 0

            async def cap_nhat(self, interaction: discord.Interaction):
                e = trang[self.trang]
                e.set_footer(text=f"Trang {self.trang+1}/{len(trang)}  ·  chỉ bạn thấy")
                self.children[0].disabled = self.trang == 0
                self.children[1].disabled = self.trang == len(trang) - 1
                await interaction.response.edit_message(embed=e, view=self)

            @discord.ui.button(label="◀ Trước", style=discord.ButtonStyle.secondary, disabled=True)
            async def truoc(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.trang -= 1
                await self.cap_nhat(interaction)

            @discord.ui.button(label="Sau ▶", style=discord.ButtonStyle.secondary)
            async def sau(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.trang += 1
                await self.cap_nhat(interaction)

        view = TrangView()
        e0 = trang[0]
        e0.set_footer(text=f"Trang 1/{len(trang)}  ·  chỉ bạn thấy")
        await interaction.followup.send(embed=e0, view=view, ephemeral=True)

    # ── /co_bac ───────────────────────────────────────────────
    @app_commands.command(name="co_bac", description="🎰 Cược tiền vào đỏ hoặc đen — may rủi 50/50!")
    @app_commands.describe(
        so_tien="Số tiền muốn cược (tối thiểu 10.000 đ)",
        lua_chon="Chọn đỏ hoặc đen",
    )
    @app_commands.choices(lua_chon=[
        app_commands.Choice(name="🔴 Đỏ", value="do"),
        app_commands.Choice(name="⚫ Đen", value="den"),
    ])
    async def co_bac(self, interaction: discord.Interaction, so_tien: int, lua_chon: str):
        await interaction.response.defer()
        uid = interaction.user.id
        nv  = db_lay(uid)

        err = _kiem_tra_nguoi_choi(nv, interaction)
        if err:
            await interaction.followup.send(embed=err, ephemeral=True); return
        err_tu = _kiem_tra_tu(nv)
        if err_tu:
            await interaction.followup.send(embed=err_tu); return

        CUOC_MIN = 10_000
        CUOC_MAX = 5_000_000

        if so_tien < CUOC_MIN:
            await interaction.followup.send(
                f"❌ Cược tối thiểu **{CUOC_MIN:,} đ**!", ephemeral=True); return
        if so_tien > CUOC_MAX:
            await interaction.followup.send(
                f"❌ Cược tối đa **{CUOC_MAX:,} đ**/lần!", ephemeral=True); return
        if nv["tien"] < so_tien:
            await interaction.followup.send(
                f"❌ Không đủ tiền — bạn có **{nv['tien']:,} đ**.", ephemeral=True); return

        # Xác suất thắng 45% (nhà cái hưởng 10%)
        ket_qua = random.choices(["do", "den"], weights=[45, 55], k=1)[0]
        thang   = ket_qua == lua_chon
        ten_chon = "🔴 Đỏ" if lua_chon == "do" else "⚫ Đen"
        ten_ket  = "🔴 Đỏ" if ket_qua  == "do" else "⚫ Đen"

        if thang:
            db_tien(uid, so_tien)
            db_chi_so(uid, tt=10)
            db_log(uid, "co_bac", f"Cờ bạc THẮNG {so_tien:,} đ ({ten_chon})", so_tien)
            nv_moi = db_lay(uid)
            e = discord.Embed(
                title="🎰  THẮNG RỒI!!!",
                description=(
                    f"Kết quả: **{ten_ket}** — Bạn chọn: **{ten_chon}**\n\n"
                    f"🎉 Chính xác! *{_wibu(WIBU_GAMBATTE)}*"
                ),
                color=C["chinh"],
            )
            e.add_field(name="💰 Thắng được",   value=f"**+{so_tien:,} đ**",        inline=True)
            e.add_field(name="👛 Tổng tài sản", value=f"**{nv_moi['tien']:,} đ**",  inline=True)
            e.add_field(name="🧠 Tinh thần",    value="+10 điểm (phấn khích!)",      inline=True)
            e.set_footer(text="⚠️ Cờ bạc gây nghiện — đừng cược hết tài sản nhé!")
        else:
            db_tien(uid, -so_tien)
            db_chi_so(uid, tt=-15)
            db_log(uid, "co_bac", f"Cờ bạc THUA {so_tien:,} đ ({ten_chon})", -so_tien)
            nv_moi = db_lay(uid)
            e = discord.Embed(
                title="🎰  THUA RỒI...",
                description=(
                    f"Kết quả: **{ten_ket}** — Bạn chọn: **{ten_chon}**\n\n"
                    f"😭 Xui quá! *{_wibu(WIBU_UNLUCKY)}*"
                ),
                color=C["nguy_hiem"],
            )
            e.add_field(name="💸 Mất đi",       value=f"**−{so_tien:,} đ**",        inline=True)
            e.add_field(name="👛 Còn lại",      value=f"**{nv_moi['tien']:,} đ**",  inline=True)
            e.add_field(name="🧠 Tinh thần",    value="−15 điểm (chán nản)",         inline=True)
            e.set_footer(text="Nhà cái luôn thắng về lâu dài — biết dừng đúng lúc nhé!")

        await interaction.followup.send(embed=e)

    # ── /cau_ca ───────────────────────────────────────────────
    @app_commands.command(name="cau_ca", description="🎣 Câu cá kiếm tiền — may mắn có thể câu được cá mập!")
    async def cau_ca(self, interaction: discord.Interaction):
        await interaction.response.defer()
        uid = interaction.user.id
        nv  = db_lay(uid)

        err = _kiem_tra_nguoi_choi(nv, interaction)
        if err:
            await interaction.followup.send(embed=err, ephemeral=True); return
        err_tu = _kiem_tra_tu(nv)
        if err_tu:
            await interaction.followup.send(embed=err_tu); return

        if nv["suc_khoe"] <= 10:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="😵 Quá Yếu Để Câu Cá!",
                    description="Sức khỏe không đủ, về nhà nghỉ ngơi đi!",
                    color=C["nguy_hiem"],
                )
            ); return

        # Reset lượt câu theo ngày
        ngay_hom_nay = str(datetime.now().date())
        if nv.get("ngay_lam_cuoi") != ngay_hom_nay:
            db_set(uid, luot_lam_hom_nay=0, ngay_lam_cuoi=ngay_hom_nay)
            nv["luot_lam_hom_nay"] = 0

        # Dùng trường riêng cho câu cá (lưu trong lich_su đơn giản — đếm hôm nay)
        with _conn() as c:
            luot_cau = c.execute(
                "SELECT COUNT(*) n FROM lich_su WHERE user_id=? AND loai='cau_ca' AND tg >= date('now','localtime')",
                (uid,)
            ).fetchone()["n"]

        MAX_CAU = 3
        if luot_cau >= MAX_CAU:
            e = discord.Embed(
                title="🎣 Hết Lượt Câu Hôm Nay!",
                description=(
                    f"Bạn đã câu **{MAX_CAU}/{MAX_CAU}** lần hôm nay.\n"
                    f"Sáng mai ra câu tiếp nhé! *{_wibu(WIBU_GAMBATTE)}*"
                ),
                color=C["canh_bao"],
            )
            await interaction.followup.send(embed=e); return

        # Bảng kết quả câu cá
        CA = [
            {"ten": "🥾 Câu được rác",   "xs": 5,  "min": -5_000,   "max": -5_000,  "emoji": "🥾"},
            {"ten": "🐟 Cá thường",       "xs": 50, "min": 10_000,   "max": 50_000,  "emoji": "🐟"},
            {"ten": "🐠 Cá hiếm",         "xs": 25, "min": 50_000,   "max": 150_000, "emoji": "🐠"},
            {"ten": "🐡 Cá quý",          "xs": 15, "min": 150_000,  "max": 500_000, "emoji": "🐡"},
            {"ten": "🦈 CÁ MẬP!!!",       "xs": 5,  "min": 500_000,  "max": 2_000_000,"emoji": "🦈"},
        ]
        chon = random.choices(CA, weights=[c["xs"] for c in CA], k=1)[0]
        tien = random.randint(chon["min"], chon["max"])

        db_tien(uid, tien)
        db_chi_so(uid, sk=-5, no=-8, tt=5)
        db_log(uid, "cau_ca",
               f"Câu được {chon['ten']}: {'+'if tien>0 else ''}{tien:,} đ",
               tien)
        nv_moi = db_lay(uid)
        con_lai_cau = MAX_CAU - luot_cau - 1

        if tien > 0:
            mau = C["chinh"] if tien < 500_000 else C["vui"]
            title = f"🎣  Câu Được: {chon['ten']}!"
            desc = f"*{_wibu(WIBU_GAMBATTE)}*" if tien >= 500_000 else "Không tệ chút nào!"
        else:
            mau = C["canh_bao"]
            title = "🎣  Câu Được Rác..."
            desc = f"Hôm nay xui quá... *{_wibu(WIBU_UNLUCKY)}*"

        e = discord.Embed(title=title, description=desc, color=mau)
        e.add_field(
            name="💰 Thu được" if tien > 0 else "💸 Tốn tiền đổ rác",
            value=f"**{'+'if tien>0 else ''}{tien:,} đ**",
            inline=True,
        )
        e.add_field(name="👛 Tổng tài sản", value=f"**{nv_moi['tien']:,} đ**", inline=True)
        e.add_field(name="🎣 Lượt còn lại", value=f"**{con_lai_cau}/{MAX_CAU}**", inline=True)
        e.add_field(name="❤️ Sức khỏe",    value=_bar(nv_moi["suc_khoe"]), inline=False)
        e.set_footer(text="Câu cá không gặp biến cố · thư giãn tâm hồn!")
        await interaction.followup.send(embed=e)

    # ── /ban_nha ──────────────────────────────────────────────
    @app_commands.command(name="ban_nha", description="🏚️ Bán lại phòng trọ lấy tiền mặt.")
    async def ban_nha(self, interaction: discord.Interaction):
        await interaction.response.defer()
        uid = interaction.user.id
        nv  = db_lay(uid)

        err = _kiem_tra_nguoi_choi(nv, interaction)
        if err:
            await interaction.followup.send(embed=err, ephemeral=True); return

        if not nv["co_nha_tro"]:
            e = discord.Embed(
                title="❌  Không Có Nhà Để Bán!",
                description=(
                    "Bạn đang ngủ vỉa hè — lấy đâu ra nhà mà bán? 😅\n"
                    "Dùng `/thue_tro` để thuê phòng trước!"
                ),
                color=C["nguy_hiem"],
            )
            await interaction.followup.send(embed=e); return

        GIA_BAN = 200_000   # bán lại rẻ hơn vì đã ở rồi

        # Nút xác nhận
        class XacNhanView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                self.ket_qua = None

            @discord.ui.button(label="✅ Xác nhận bán", style=discord.ButtonStyle.danger)
            async def xac_nhan(self, inter: discord.Interaction, btn: discord.ui.Button):
                if inter.user.id != uid:
                    await inter.response.send_message("Không phải của bạn!", ephemeral=True); return
                self.ket_qua = True
                self.stop()
                await inter.response.defer()

            @discord.ui.button(label="❌ Huỷ", style=discord.ButtonStyle.secondary)
            async def huy(self, inter: discord.Interaction, btn: discord.ui.Button):
                if inter.user.id != uid:
                    await inter.response.send_message("Không phải của bạn!", ephemeral=True); return
                self.ket_qua = False
                self.stop()
                await inter.response.defer()

        view = XacNhanView()
        e_hoi = discord.Embed(
            title="🏚️  Xác Nhận Bán Nhà?",
            description=(
                f"Bạn sắp **bán lại phòng trọ** với giá **{GIA_BAN:,} đ**.\n\n"
                f"⚠️ Sau khi bán:\n"
                f"• Mất nhà trọ → ngủ vỉa hè\n"
                f"• Mất bonus lương **+15%**\n"
                f"• Dễ bị ốm và mất tinh thần hơn\n\n"
                f"*Bạn có chắc không? {_wibu(WIBU_UNLUCKY)}*"
            ),
            color=C["canh_bao"],
        )
        msg = await interaction.followup.send(embed=e_hoi, view=view)
        await view.wait()

        if not view.ket_qua:
            e_huy = discord.Embed(
                title="❌  Đã Huỷ",
                description="Phú quý bình an — giữ nhà lại đi! 🏠",
                color=C["thong_tin"],
            )
            await interaction.followup.send(embed=e_huy); return

        db_tien(uid, GIA_BAN)
        db_set(uid, co_nha_tro=0)
        db_chi_so(uid, tt=-10)
        db_log(uid, "ban_nha", f"Bán phòng trọ lấy {GIA_BAN:,} đ", GIA_BAN)
        nv_moi = db_lay(uid)

        e = discord.Embed(
            title="🏚️  Đã Bán Nhà Trọ",
            description=(
                f"Bạn đã bán lại phòng trọ và dọn ra ngoài.\n"
                f"Từ đêm nay lại ngủ vỉa hè rồi... *{_wibu(WIBU_UNLUCKY)}*"
            ),
            color=C["cam"],
        )
        e.add_field(name="💰 Thu được",    value=f"**+{GIA_BAN:,} đ**",        inline=True)
        e.add_field(name="👛 Tổng tài sản",value=f"**{nv_moi['tien']:,} đ**",  inline=True)
        e.add_field(name="🧠 Tinh thần",   value="−10 điểm (buồn quá)",         inline=True)
        e.set_footer(text="Dùng /thue_tro để thuê lại khi có đủ tiền!")
        await interaction.followup.send(embed=e)

    # ── /dot_nha ──────────────────────────────────────────────
    @app_commands.command(name="dot_nha", description="🔥 Đốt nhà trọ! Hành động điên rồ — hậu quả cực nặng!")
    async def dot_nha(self, interaction: discord.Interaction):
        await interaction.response.defer()
        uid = interaction.user.id
        nv  = db_lay(uid)

        err = _kiem_tra_nguoi_choi(nv, interaction)
        if err:
            await interaction.followup.send(embed=err, ephemeral=True); return

        if not nv["co_nha_tro"]:
            e = discord.Embed(
                title="🔥  Đốt Cái Gì?!",
                description=(
                    "Bạn đang ngủ vỉa hè — không có nhà để đốt đâu bạn ơi! 🤣\n"
                    "Thuê nhà trước đi rồi tính!"
                ),
                color=C["canh_bao"],
            )
            await interaction.followup.send(embed=e); return

        # Nút xác nhận điên rồ
        class DotNhaView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=20)
                self.ket_qua = None

            @discord.ui.button(label="🔥 ĐỐT ĐI!!! (điên rồ)", style=discord.ButtonStyle.danger)
            async def dot(self, inter: discord.Interaction, btn: discord.ui.Button):
                if inter.user.id != uid:
                    await inter.response.send_message("Không phải của bạn!", ephemeral=True); return
                self.ket_qua = True
                self.stop()
                await inter.response.defer()

            @discord.ui.button(label="😅 Thôi đừng, tôi còn tỉnh táo", style=discord.ButtonStyle.success)
            async def huy(self, inter: discord.Interaction, btn: discord.ui.Button):
                if inter.user.id != uid:
                    await inter.response.send_message("Không phải của bạn!", ephemeral=True); return
                self.ket_qua = False
                self.stop()
                await inter.response.defer()

        view = DotNhaView()
        e_hoi = discord.Embed(
            title="🔥  BẠN MUỐN ĐỐT NHÀ?!",
            description=(
                "**⚠️ CẢNH BÁO: ĐÂY LÀ HÀNH ĐỘNG CỰC KỲ ĐIÊN RỒ!**\n\n"
                "Hậu quả nếu đốt nhà:\n"
                "🔥 Mất nhà trọ ngay lập tức\n"
                "💸 Phải **bồi thường** cho chủ nhà: **500.000–1.500.000 đ**\n"
                "👮 **50%** bị công an bắt vào tù **3–5 ngày**!\n"
                "❤️ Mất **20 sức khỏe** (hít khói)\n"
                "🧠 Mất **30 tinh thần** (hối hận)\n\n"
                f"*Lý trí nói đừng làm. Nhưng bạn có chắc? {_wibu(WIBU_UNLUCKY)}*"
            ),
            color=C["nguy_hiem"],
        )
        await interaction.followup.send(embed=e_hoi, view=view)
        await view.wait()

        if not view.ket_qua:
            e_huy = discord.Embed(
                title="😌  Quyết Định Sáng Suốt!",
                description=(
                    "Bạn đã không đốt nhà — phú quý bình an! 🏠\n"
                    f"*{_wibu(WIBU_GAMBATTE)}*"
                ),
                color=C["chinh"],
            )
            await interaction.followup.send(embed=e_huy); return

        # Đốt nhà!
        boi_thuong = random.randint(500_000, 1_500_000)
        boi_thuong = min(boi_thuong, nv["tien"])
        bi_bat     = random.random() < 0.50
        so_ngay_tu = random.randint(3, 5) if bi_bat else 0

        db_tien(uid, -boi_thuong)
        db_chi_so(uid, sk=-20, tt=-30)
        db_set(uid, co_nha_tro=0)

        if bi_bat:
            ngay_het = nv["ngay_choi"] + so_ngay_tu
            db_set(uid, dang_tu=1, tu_het_ngay=ngay_het)
            db_log(uid, "dot_nha", f"Đốt nhà, bị bắt {so_ngay_tu} ngày, bồi thường {boi_thuong:,} đ", -boi_thuong)
        else:
            db_log(uid, "dot_nha", f"Đốt nhà, bồi thường {boi_thuong:,} đ, trốn thoát!", -boi_thuong)

        nv_moi = db_lay(uid)
        e = discord.Embed(
            title="🔥  NHÀ BỐC CHÁY!!!",
            description=(
                "Ngọn lửa bùng lên thiêu rụi căn phòng trọ!\n"
                "Hàng xóm hô hoán, cảnh sát ầm ầm kéo đến...\n\n"
                f"*{_wibu(WIBU_UNLUCKY)}*"
            ),
            color=0xFF4500,
        )
        e.add_field(name="💸 Bồi thường chủ nhà", value=f"**−{boi_thuong:,} đ**",       inline=True)
        e.add_field(name="❤️ Sức khỏe",            value="−20 điểm (hít khói)",           inline=True)
        e.add_field(name="🧠 Tinh thần",            value="−30 điểm (hối hận)",            inline=True)
        e.add_field(name="🏠 Nhà trọ",              value="Mất nhà, ra đường rồi!",        inline=True)
        e.add_field(name="👛 Còn lại",              value=f"**{nv_moi['tien']:,} đ**",     inline=True)

        if bi_bat:
            e.add_field(
                name="⛓️ BỊ BẮT VÀO TÙ!",
                value=(
                    f"Nhân chứng tố cáo — bạn bị bắt **{so_ngay_tu} ngày**!\n"
                    f"Dùng `/ra_tu` khi hết hạn."
                ),
                inline=False,
            )
            e.color = 0x1C1C1C
        else:
            e.add_field(
                name="🏃 Trốn Thoát!",
                value="Bạn may mắn trốn thoát trước khi cảnh sát đến!",
                inline=False,
            )

        e.set_footer(text="Bài học: Đừng bao giờ đốt nhà. Nghiêm túc đó.")
        await interaction.followup.send(embed=e)
        await _kiem_tra_chet(uid, interaction)


# ══════════════════════════════════════════════════════════════
async def setup(bot: commands.Bot):
    await bot.add_cog(KinhTe(bot))
