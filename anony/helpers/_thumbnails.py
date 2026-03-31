import os
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from collections import Counter
from anony import config
from anony.helpers import Track

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Thumbnail:
    def __init__(self):
        self.size = (1280, 720)
        self.session: aiohttp.ClientSession | None = None
        
        # --- Font သတ်မှတ်ခြင်း (Error ကာကွယ်ရေးအပိုင်း) ---
        title_font_path = os.path.join(BASE_DIR, "Raleway-Bold.ttf")
        info_font_path = os.path.join(BASE_DIR, "Inter-Light.ttf")

        # Font ဖိုင်ရှိမရှိ စစ်ဆေးပြီး မရှိလျှင် စက်ထဲက ပုံမှန် Font သုံးရန်
        try:
            self.font_title = ImageFont.truetype(title_font_path, 40)
            self.font_info = ImageFont.truetype(info_font_path, 30)
            self.font_credit = ImageFont.truetype(info_font_path, 24)
        except:
            # Font ဖိုင်ရှာမတွေ့ပါက Error မတက်ဘဲ Default Font ကို သုံးမည်
            self.font_title = ImageFont.load_default()
            self.font_info = ImageFont.load_default()
            self.font_credit = ImageFont.load_default()

    async def start(self) -> None:
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

    async def save_thumb(self, output_path: str, url: str) -> str:
        if not self.session or self.session.closed:
            await self.start()
        async with self.session.get(url) as resp:
            if resp.status == 200:
                with open(output_path, "wb") as f:
                    f.write(await resp.read())
        return output_path

    def _truncate_text(self, draw, text, font, max_width):
        if draw.textlength(text, font=font) <= max_width:
            return text
        return text[:25] + "..."

    async def generate(self, song: Track) -> str:
        try:
            os.makedirs("cache", exist_ok=True)
            temp = f"cache/temp_{song.id}.jpg"
            output = f"cache/{song.id}.png"
            
            if os.path.exists(output):
                return output

            await self.save_thumb(temp, song.thumbnail)
            raw_cover = Image.open(temp).convert("RGBA")
            
            # --- ၁။ Background (Blurred) ---
            bg = ImageOps.fit(raw_cover, self.size, method=Image.Resampling.LANCZOS)
            bg = bg.filter(ImageFilter.GaussianBlur(30))
            bg = ImageEnhance.Brightness(bg).enhance(0.4)

            # --- ၂။ Rounded Cover (Player Style) ---
            portrait_size = (600, 350)
            portrait = ImageOps.fit(raw_cover, portrait_size, method=Image.Resampling.LANCZOS)
            mask = Image.new("L", portrait_size, 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, *portrait_size), 30, fill=255)
            portrait.putalpha(mask)
            
            px, py = (self.size[0] - portrait_size[0]) // 2, 70
            bg.paste(portrait, (px, py), portrait)

            # --- ၃။ စာသားများနှင့် Credits ---
            draw = ImageDraw.Draw(bg)
            tx_top = py + portrait_size[1] + 40
            
            # သီချင်းနာမည်
            title = self._truncate_text(draw, (song.title or "Unknown").upper(), self.font_title, 1000)
            draw.text((self.size[0]//2, tx_top), title, font=self.font_title, fill="white", anchor="ma")

            # အဆိုတော်/Channel
            info = f"{song.channel_name} • {song.view_count}"
            draw.text((self.size[0]//2, tx_top + 60), info, font=self.font_info, fill=(200, 200, 200), anchor="ma")

            # --- ၄။ Progress Bar ---
            bar_w, bar_h = 550, 6
            bx, by = (self.size[0] - bar_w) // 2, tx_top + 130
            draw.rounded_rectangle((bx, by, bx + bar_w, by + bar_h), 3, fill=(100, 100, 100)) # Empty Bar
            draw.rounded_rectangle((bx, by, bx + 220, by + bar_h), 3, fill=(255, 215, 0)) # Gold Progress

            # --- ၅။ သင့်နာမည် (အောက်ခြေတွင် ထည့်ရန်) ---
            # "Thaw Zin" နေရာတွင် သင်ကြိုက်တဲ့နာမည် ပြောင်းရေးပါ
            my_name = "Credit by @HANTHAR999"
            draw.text((self.size[0]//2, self.size[1]-50), my_name, font=self.font_credit, fill=(150, 150, 150, 180), anchor="ma")

            bg.save(output, "PNG")
            if os.path.exists(temp):
                os.remove(temp)
            return output

        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return config.DEFAULT_THUMB
