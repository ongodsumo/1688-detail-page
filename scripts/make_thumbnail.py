"""상품 사진에서 스마트스토어 대표이미지(정사각)를 잘라낸다.

박스를 지정하지 않으면 가로 기준 정사각으로 가운데를 자른다.
공급처 이미지에 컬러칩·로고가 남아 있으면 --box로 그 영역을 피해 지정한다.

사용법:
    python make_thumbnail.py 원본.jpg 대표_1.jpg
    python make_thumbnail.py 원본.jpg 대표_1.jpg --box 100,120,1340
"""

import argparse
from pathlib import Path

from PIL import Image

OUT_SIZE = 1000  # 네이버 권장 대표이미지 한 변


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--box", help="left,top,size — 생략하면 가로 기준 가운데 정사각")
    args = ap.parse_args()

    # 1688 상세 이미지는 GIF(팔레트 모드)로 올라온 게 많은데 그대로는 JPEG로 저장되지 않는다
    im = Image.open(args.src).convert("RGB")
    if args.box:
        left, top, size = (int(v) for v in args.box.split(","))
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
