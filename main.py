"""
╔══════════════════════════════════════════════╗
║   『 TỪ TAY TRẮNG ĐẾN TỶ PHÚ 』            ║
║   Khởi động bot — chạy file này để bật bot  ║
╚══════════════════════════════════════════════╝

Cách chạy:
    python main.py
"""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# ── Đọc token từ file .env ────────────────────────────────────
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("❌ Không tìm thấy DISCORD_TOKEN trong file .env!")
    print("   Hãy mở file .env và điền token bot vào.")
    exit(1)

# ── Cấu hình bot ─────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",      # prefix không dùng nhưng cần khai báo
    intents=intents,
    help_command=None,
)

# ── Sự kiện khởi động ────────────────────────────────────────
@bot.event
async def on_ready():
    print("=" * 50)
    print(f"✅ Bot đã online: {bot.user} (ID: {bot.user.id})")
    print(f"📡 Đang kết nối {len(bot.guilds)} server")
    print("=" * 50)

    # Sync slash commands lên Discord
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Đã đồng bộ {len(synced)} lệnh slash")
    except Exception as e:
        print(f"⚠️  Lỗi sync lệnh: {e}")

    # Đặt trạng thái bot
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="Từ Tay Trắng Đến Tỷ Phú 💰 | /batdau"
        )
    )
    print("🎮 Bot sẵn sàng! Dùng /batdau để chơi.")

# ── Load cog game ─────────────────────────────────────────────
async def load_cogs():
    print("📦 Đang load cog...")
    await bot.load_extension("cogs.kinh_te")
    print("   ✅ cogs/kinh_te.py — OK")

# ── Chạy bot ─────────────────────────────────────────────────
import asyncio

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
