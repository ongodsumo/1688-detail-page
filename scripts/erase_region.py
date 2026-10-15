"""상품 사진에서 로고·문구·컬러칩 같은 영역을 지운다.

주변 픽셀로 메우는 방식(inpaint)이라 흰 스튜디오 배경처럼 **단순한 배경 위에 얹힌 것**은
거의 티가 나지 않게 지워진다. 반대로 옷감 무늬나 인물 위에 겹친 로고는 뭉개지므로
그런 자리는 포토샵 생성형 채우기를 쓰는 게 낫다.

좌표는 % 로 준다. 원본 해상도가 달라도 같은 값을 쓸 수 있다.

사용법:
    # 좌측 컬러칩 지우기 (left,top,width,height 를 %로)
    python erase_region.py 원본.jpg --box 2,38,8,18

    # 여러 군데 한 번에
    python erase_region.py 원본.jpg --box 2,38,8,18 --box 62,70,36,22

    # 결과를 덮어쓰기 (기본은 _clean 붙여 새 파일로 저장)
    python erase_region.py 원본.jpg --box 2,38,8,18 --inplace
"""

import argparse
from pathlib import Path

import cv2
import numpy as np

MARGIN = 4  # 지울 영역을 살짝 넓혀 로고 가장자리가 남지 않게 한다


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--box", action="append", required=True,
                    help="left,top,width,height (%% 단위). 여러 번 쓸 수 있다")
    ap.add_argument("--fill", metavar="auto|RRGGBB",
                    help="단색으로 채운다. 흰 배경 위의 로고·칩은 이쪽이 깨끗하다. "
                         "생략하면 주변을 번지게 하는 inpaint를 쓴다(무늬 있는 배경용)")
    ap.add_argument("--inplace", action="store_true", help="원본을 덮어쓴다")
    args = ap.parse_args()

    src = Path(args.src)
    img = cv2.imdecode(np.fromfile(src, dtype=np.uint8), cv2.IMREAD_COLOR)  # 한글 경로 대응
    h, w = img.shape[:2]

    # 지울 자리를 흰색으로 칠한 마스크를 만든다
    mask = np.zeros((h, w), dtype=np.uint8)
    for box in args.box:
        bl, bt, bw, bh = (float(v) for v in box.split(","))
        x0 = max(0, int(w * bl / 100) - MARGIN)
        y0 = max(0, int(h * bt / 100) - MARGIN)
        x1 = min(w, int(w * (bl + bw) / 100) + MARGIN)
        y1 = min(h, int(h * (bt + bh) / 100) + MARGIN)
        mask[y0:y1, x0:x1] = 255
        print(f"  지움 {bl},{bt},{bw},{bh}%  → 픽셀 ({x0},{y0})-({x1},{y1})")

    if args.fill:
        # 단색 채우기 — 배경이 균일할 때 쓴다. inpaint와 달리 옆의 옷 색을 끌어오지 않는다
        if args.fill == "auto":
            # 박스 테두리 바깥 픽셀 중 밝은 쪽(배경)을 골라 그 색으로 채운다
            ring = cv2.dilate(mask, np.ones((25, 25), np.uint8)) - mask
            px = img[ring > 0]
            bright = px[px.mean(axis=1) >= np.percentile(px.mean(axis=1), 75)]
            color = bright.mean(axis=0)
            print(f"  자동 추출 배경색 BGR {color.round(0)}")
        else:
            r, g, b = (int(args.fill[i:i + 2], 16) for i in (0, 2, 4))
            color = np.array([b, g, r], dtype=float)
        out = img.copy()
        out[mask > 0] = color
    else:
        out = cv2.inpaint(img, mask, 5, cv2.INPAINT_TELEA)

    dst = src if args.inplace else src.with_name(f"{src.stem}_clean{src.suffix}")
    cv2.imencode(src.suffix, out, [cv2.IMWRITE_JPEG_QUALITY, 95])[1].tofile(dst)
    print(f"저장: {dst.name}")


if __name__ == "__main__":
    main()
