"""상세페이지 HTML을 스마트스토어 업로드용 이미지로 잘라 저장한다.

사용법:
    python html_to_images.py "상품명/output/상세페이지_2026-07-31.html"
    python html_to_images.py "상품명/output/상세페이지_2026-07-31.html" --mobile

이미지는 HTML의 <section> 경계에서 나뉜다.
결과: HTML과 같은 폴더의 images/<HTML파일명>/ 안에 상세_01.jpg, 상세_02.jpg ... 로 저장된다.
"""

import argparse
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

# (렌더링 뷰포트 폭, 저장 폭). 모바일은 좁게 렌더링해 CSS가 1열로 접히게 한 뒤
# 네이버 모바일 권장 폭으로 키운다 — 860px를 축소하면 글자만 작아져 안 읽힌다.
DESKTOP = (860, 860)
MOBILE = (480, 750)

SCALE = 2        # 최소 렌더링 배율 — 글자가 선명해진다
MIN_HEIGHT = 400  # 이보다 짧은 섹션은 앞 이미지에 붙인다 (푸터가 따로 떨어지지 않도록)


def capture(html_path, out_dir, view_width, out_width):
    """HTML을 통짜 이미지로 렌더링하고, 각 섹션의 시작 y좌표(CSS px)를 함께 반환한다."""
    shot = out_dir / "_full.png"
    # 저장 폭이 렌더링 픽셀보다 크면 업스케일로 흐려지므로, 배율을 저장 폭에 맞춰 올린다
    scale = max(SCALE, -(-out_width // view_width))
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": view_width, "height": 1000},
            device_scale_factor=scale,
        )
        page.goto(html_path.resolve().as_uri())
        page.wait_for_load_state("networkidle")
        # 브라우저가 계산한 실제 레이아웃 위치를 받아온다 — CSS를 고쳐도 자동으로 따라온다
        tops = page.evaluate(
            "() => Array.from(document.querySelectorAll('.page > section, .page > article, .page > footer'))"
            "        .map(el => el.getBoundingClientRect().top + window.scrollY)"
        )
        # 고해상도·긴 페이지는 기본 30초를 넘길 수 있어 넉넉히 잡는다
        page.screenshot(path=str(shot), full_page=True, timeout=180000)
        browser.close()
    return shot, tops


def slice_image(shot, out_dir, tops, view_width, out_width):
    """섹션 경계에서 잘라 여러 장으로 저장한다."""
    img = Image.open(shot).convert("RGB")
    img = img.resize((out_width, round(img.height * out_width / img.width)), Image.LANCZOS)

    # CSS px로 받은 섹션 위치를 저장 폭 기준으로 환산
    ratio = out_width / view_width
    cuts = [0] + [round(t * ratio) for t in tops if 0 < round(t * ratio) < img.height]
    cuts.append(img.height)

    # 너무 짧은 조각은 앞에 합친다
    merged = [cuts[0]]
    for c in cuts[1:-1]:
        if c - merged[-1] >= MIN_HEIGHT:
            merged.append(c)
    merged.append(img.height)
    # 마지막 조각(주로 푸터)도 짧으면 앞에 합친다
    if len(merged) > 2 and merged[-1] - merged[-2] < MIN_HEIGHT:
        del merged[-2]

    saved = []
    for i in range(len(merged) - 1):
        piece = img.crop((0, merged[i], out_width, merged[i + 1]))
        path = out_dir / f"상세_{i + 1:02d}.jpg"
        piece.save(path, quality=92, subsampling=0)
        saved.append((path, piece.height))
    return saved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html", help="상세페이지 HTML 경로")
    ap.add_argument("--mobile", action="store_true", help="모바일 레이아웃으로 출력")
    ap.add_argument("--width", type=int, help="저장 폭(px) 지정 — 미지정 시 기본값(860/750)")
    args = ap.parse_args()

    view_width, out_width = MOBILE if args.mobile else DESKTOP
    if args.width:
        out_width = args.width
    suffix = "_mobile" if args.mobile else ""

    html_path = Path(args.html)
    # 같은 폴더에 시안이 여러 개일 때 서로 덮어쓰지 않도록 파일명별로 폴더를 나눈다
    out_dir = html_path.parent / "images" / (html_path.stem + suffix)
    out_dir.mkdir(parents=True, exist_ok=True)

    shot, tops = capture(html_path, out_dir, view_width, out_width)
    saved = slice_image(shot, out_dir, tops, view_width, out_width)
    shot.unlink()  # 통짜 원본은 지운다

    print(f"{out_dir} 에 {len(saved)}장 저장")
    for path, height in saved:
        kb = path.stat().st_size // 1024
        print(f"  {path.name}  {out_width}x{height}  {kb}KB")


if __name__ == "__main__":
    main()
