"""1688 상품 이미지를 한 번에 내려받는다.

이미지 URL 목록은 브라우저에서 먼저 뽑아 텍스트 파일로 넘긴다 (한 줄에 하나).
상세 본문은 Shadow DOM 안에 있어 일반 스크래핑으로는 안 잡히기 때문이다.
1688 CDN은 Referer 헤더가 없으면 요청을 거부하므로 헤더를 붙여 받는다.

사용법:
    python fetch_1688_images.py urls.txt "상세페이지/상품명" --prefix 본문
"""

import argparse
import re
import sys
from pathlib import Path

import requests

# 윈도우 한글 콘솔(cp949)에서 도움말·진행 메시지가 깨지거나 멈추지 않게 UTF-8로 출력한다
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://detail.1688.com/",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", help="이미지 URL이 한 줄에 하나씩 든 텍스트 파일")
    ap.add_argument("out_dir", help="저장할 폴더")
    ap.add_argument("--prefix", default="img", help="파일명 앞머리 (예: 갤러리 / 본문)")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    urls = [u.strip() for u in Path(args.urls).read_text(encoding="utf-8").splitlines() if u.strip()]

    ok = 0
    for i, url in enumerate(urls, 1):
        # 알리 CDN은 파일명 끝에 리사이즈 접미사(.jpg_.webp, .jpg_100x100.jpg 등)가 붙는다 — 원본을 받으려면 떼어낸다
        clean = re.sub(r"(\.(?:jpe?g|png|gif))_.*$", r"\1", url.split("?")[0], flags=re.I)
        ext = "gif" if clean.endswith(".gif") else "jpg"
        # 파일명에 원본 해시 앞부분을 남겨 나중에 원본과 대조하기 쉽게 한다
        stem = clean.rsplit("/", 1)[-1][:12]
        res = requests.get(clean, headers=HEADERS, timeout=30)
        if res.status_code != 200:
            print(f"  실패 {i:02d} {res.status_code} {stem}")
            continue
        (out_dir / f"{args.prefix}_{i:02d}_{stem}.{ext}").write_bytes(res.content)
        ok += 1

    print(f"{out_dir} 에 {ok}/{len(urls)}장 저장")


if __name__ == "__main__":
    main()
