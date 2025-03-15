from dataclasses import dataclass
from enum import Enum


class CaptchaTiles(Enum):
    rc_image_tile_33 = 'rc-image-tile-33'
    rc_image_tile_44 = 'rc-image-tile-44'


@dataclass
class CaptchaCell:
    cell_num: int
    cell_coord: list[tuple[float, float], ...] = None


CAPTCHA_CELL = {CaptchaTiles.rc_image_tile_33.value: CaptchaCell(cell_num=9),
                CaptchaTiles.rc_image_tile_44.value: CaptchaCell(cell_num=16)
                }

OBJECT_NOT_FOUND: str = 'Objects not found!'
CELL_NOT_FOUND: str = 'Cell outlines not found!'
