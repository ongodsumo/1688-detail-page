"""상품 사진에서 스마트스토어 대표이미지(정사각)를 잘라낸다.

박스를 지정하지 않으면 가로 기준 정사각으로 가운데를 자른다.
공급처 이미지에 컬러칩·로고가 남아 있으면 --box로 그 영역을 피해 지정한다.

사용법:
    python make_thumbnail.py 원본.jpg 대표_1.jpg
    python make_thumbnail.py 원본.jpg 대표_1.jpg --box 5,8,90

--box 값은 % 단위다 (erase_region.py와 같다).
left·size는 원본 가로 기준, top은 세로 기준. 해상도가 달라도 같은 값을 쓸 수 있다.
"""

import argparse
import sys
from pathlib import Path

from PIL import Image

# 윈도우 한글 콘솔(cp949)에서 도움말·진행 메시지가 깨지거나 멈추지 않게 UTF-8로 출력한다
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OUT_SIZE = 1000  # 네이버 권장 대표이미지 한 변


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--box", help="left,top,size (%% 단위) - 생략하면 가로 기준 가운데 정사각")
    args = ap.parse_args()

    # 1688 상세 이미지는 GIF(팔레트 모드)로 올라온 게 많은데 그대로는 JPEG로 저장되지 않는다
    im = Image.open(args.src).convert("RGB")
    if args.box:
        # % 값을 픽셀로 환산한다 — 정사각이므로 size는 가로 기준
        bl, bt, bs = (float(v) for v in args.box.split(","))
        left, top, size = round(im.width * bl / 100), round(im.height * bt / 100), round(im.width * bs / 100)
        if left + size > im.width or top + size > im.height:
            print(f"  경고: 박스가 원본({im.width}x{im.height}) 밖으로 나간다 — 넘친 부분은 검게 채워진다")
    else:
        size = min(im.width, im.height)
        left = (im.width - size) // 2
        top = (im.height - size) // 2

    Path(args.dst).parent.mkdir(parents=True, exist_ok=True)
    im.crop((left, top, left + size, top + size)) \
      .resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS) \
      .save(args.dst, quality=93, subsampling=0)

    scale = OUT_SIZE / size
    note = " (업스케일: 화질 확인 필요)" if scale > 1.05 else ""
    print(f"{args.dst}  {size}px @({left},{top}) -> {OUT_SIZE}px{note}")


if __name__ == "__main__":
    main()
