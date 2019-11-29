# -*- coding:utf-8 -*-
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw


class GoldenSeedPlaybillGen:
    def __init__(self, background_file, avatar_lt, avatar_wh, nickname_top, nickname_color, seed_file, fond_file):
        self.background_file = background_file
        self.nickname = None
        self.avatar_lt = avatar_lt
        self.avatar_wh = avatar_wh
        self.nickname_top = nickname_top
        self.nickname_color = nickname_color
        self.seed_img = Image.open(seed_file)
        self.font = ImageFont.truetype(fond_file, 32)

    @classmethod
    def draw_circle_avatar(cls, avatar_img, target_size):
        avatar_img = avatar_img.resize(target_size)
        bigsize = (avatar_img.size[0] * 3, avatar_img.size[1] * 3)

        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + bigsize, fill=255)

        mask = mask.resize(avatar_img.size, Image.ANTIALIAS)
        avatar_img.putalpha(mask)
        return avatar_img

    def __call__(self, avatar_file, nickname):
        avatar_img = Image.open(avatar_file).convert("RGBA")
        self.avatar_img = self.draw_circle_avatar(avatar_img, self.avatar_wh)
        self.nickname = nickname
        return self

    @property
    def playbill_img(self):
        background_img = Image.open(self.background_file)
        background_img.paste(self.avatar_img, self.avatar_lt, self.avatar_img)
        font_width, font_height = self.font.getsize(self.nickname)
        width = font_width + 5 + self.seed_img.size[0]

        if background_img.size[0] > width:
            x = int((background_img.size[0] - width) / 2)
        else:
            x = 0

        draw = ImageDraw.Draw(background_img)
        draw.text((x, self.nickname_top), self.nickname, self.nickname_color, font=self.font)

        seed_top = int(self.nickname_top + (font_height - self.seed_img.size[1]) / 2)
        seed_left = int(x + 5 + font_width)
        background_img.paste(self.seed_img, (seed_left, seed_top), self.seed_img)
        return background_img
