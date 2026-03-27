# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic

import os
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from collections import Counter
from anony import config
from anony.helpers import Track

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_TITLE_PATH = os.path.join(BASE_DIR, "Raleway-Bold.ttf")
FONT_INFO_PATH = os.path.join(BASE_DIR, "Inter-Light.ttf")

class Thumbnail:
    def __init__(self):
        self.size = (1280, 720)
        self.font_title = ImageFont.truetype(FONT_TITLE_PATH, 32)
        self.font_info = ImageFont.truetype(FONT_INFO_PATH, 28)
        self.margin_x, self.margin_y = 80, 60

    async def save_thumb(self, output_path: str, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    with open(output_path, "wb") as f:
                        f.write(await resp.read())
        return output_path

    def _truncate_text(self, draw, text, font, max_width):
        if draw.textlength(text, font=font) <= max_width:
            return text
        return text[:37] + ".."

    def _get_dominant_colors(self, image):
        img = image.copy().resize((50, 50)).convert("RGB")
        return Counter(list(img.getdata())).most_common(1)[0][0]

    async def generate(self, song: Track) -> str:
        try:
            os.makedirs("cache", exist_ok=True)
            temp, output = f"cache/temp_{song.id}.jpg", f"cache/{song.id}.png"
            if os.path.exists(output):
                return output

            await self.save_thumb(temp, song.thumbnail)
            raw_cover = Image.open(temp).convert("RGBA")
            
            bg = ImageOps.fit(raw_cover, self.size, method=Image.Resampling.LANCZOS)
            bg = bg.filter(ImageFilter.GaussianBlur(40))
            bg = ImageEnhance.Brightness(bg).enhance(0.5)
            bg = ImageEnhance.Contrast(bg).enhance(1.6)
            bg = ImageEnhance.Color(bg).enhance(2.0)

            portrait_size = (540, 500)
            portrait = ImageOps.fit(raw_cover, portrait_size, method=Image.Resampling.LANCZOS)
            portrait = ImageEnhance.Contrast(portrait).enhance(1.2)
            portrait = ImageEnhance.Color(portrait).enhance(1.5)
            
            mask = Image.new("L", portrait_size, 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, *portrait_size), 30, fill=255)
            portrait.putalpha(mask)

            px, py = (self.size[0] - portrait_size[0]) // 2, 70
            bg.paste(portrait, (px, py), portrait)

            draw = ImageDraw.Draw(bg)
            tx_top = py + portrait_size[1] + 50
            safe_w = self.size[0] - 160

            title = self._truncate_text(draw, song.title.upper(), self.font_title, safe_w)
            info = f"{song.channel_name}  •  {str(song.view_count)}"

            draw.text((self.size[0] // 2, tx_top), title, font=self.font_title, fill=(255, 255, 255), anchor="ma")
            draw.text((self.size[0] // 2, tx_top + 55), info, font=self.font_info, fill=(255, 255, 255, 210), anchor="ma")

            dominant = self._get_dominant_colors(raw_cover)
            bx, bt, bb = self.size[0] - 80, py + 20, py + portrait_size[1] - 20
            draw.rounded_rectangle((bx - 5, bt, bx + 5, bb), 5, fill=(255, 255, 255, 40))
            
            prog_h = int((bb - bt) * 0.7)
            draw.rounded_rectangle((bx - 5, bb - prog_h, bx + 5, bb), 5, fill=dominant)

            bg.save(output, "PNG")
            if os.path.exists(temp):
                os.remove(temp)
            return output

        except Exception as e:
            print(f"Error: {e}")
            return config.DEFAULT_THUMB
