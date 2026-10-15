# 1688 링크 → 스마트스토어 상세페이지 (Claude Code 플러그인)

1688 상품 링크 하나를 주면 Claude가 아래 순서로 상세페이지를 만들어 줍니다.

1. 1688 상세 본문 이미지를 전부 내려받습니다
2. 이미지를 하나하나 열어 **쓸 컷 / 못 쓸 컷 / 지워야 할 중국어·로고**를 표로 정리합니다
3. 한국어 카피를 쓰고 HTML 상세페이지를 짭니다
4. 스마트스토어 업로드용 **모바일 1000px 이미지**로 잘라 저장하고 눈으로 검수합니다
5. 1000×1000 **대표이미지** 후보 3장을 만듭니다

> 결과물은 초안입니다. 소재·사이즈·성능 표기는 판매자가 실물과 공급처 자료로 꼭 확인하세요.

---

## 필요한 것

| 항목 | 설명 |
|---|---|
| Claude 유료 플랜 | Pro 이상 (Claude Code 사용 가능 플랜) |
| Claude Code | **Claude 데스크톱 앱(Code 탭)** 권장 — 1688 페이지를 여는 내장 브라우저가 들어 있습니다. 터미널용 Claude Code만 쓴다면 Chrome 확장(Claude in Chrome)이 필요합니다 |
| Python 3.10 이상 | 이미지 내려받기·자르기·추출에 씁니다 |
| 1688 계정 | 로그인해야 상세 본문 이미지가 보입니다 (1688 모바일 앱 QR 로그인) |

---

## 설치

### 1) 플러그인 설치

터미널(윈도우: PowerShell / 맥: 터미널)에서 두 줄을 실행합니다.

```bash
claude plugin marketplace add ongodsumo/1688-detail-page
claude plugin install detail-page-1688@ongodsumo
```

Claude Code 대화창에서 할 수도 있습니다.

```
/plugin marketplace add ongodsumo/1688-detail-page
/plugin install detail-page-1688@ongodsumo
```

설치 후 **Claude Code를 껐다 켜거나 새 세션을 엽니다.**

### 2) 파이썬 라이브러리 설치

```bash
pip install requests Pillow playwright opencv-python numpy
python -m playwright install chromium
```

맥에서 `python`/`pip`가 없다고 나오면 `python3`/`pip3`로 바꿔 실행하세요.
(설치를 안 해도 첫 실행 때 Claude가 확인하고 설치해도 되는지 물어봅니다.)

---

## 사용법

새 세션에서 입력합니다.

```
/상세페이지제작 https://detail.1688.com/offer/000000000000.html
```

이미 받아둔 이미지 폴더로 시작할 수도 있습니다.

```
/상세페이지제작 C:\상품사진\와플후디
```

같은 이름의 커맨드가 이미 있으면 `/detail-page-1688:상세페이지제작`으로 부르세요.

### 중간에 Claude가 물어보는 것

- 파이썬 라이브러리를 설치해도 되는지
- 1688 로그인 (화면에 로그인 페이지가 뜨면 휴대폰 1688 앱으로 QR을 찍으세요. Claude는 비밀번호를 입력하지 않습니다)
- 지워야 할 로고·중국어 목록 확인
- 브랜드명을 넣을지 (무브랜드 판매면 넣지 않음)
- 대표이미지 3장 중 어느 것을 쓸지

### 결과물 위치

```
<상품폴더>/
├─ 본문_01_xxx.jpg …            1688에서 받은 원본
└─ output/
   ├─ 상세페이지_YYYY-MM-DD.html  상세페이지 원본(HTML)
   ├─ images/상세페이지_…_mobile/  ★ 스마트스토어 업로드용 (1000px)
   ├─ images/상세페이지_…/         PC 확인용 (860px)
   └─ 대표이미지/                 ★ 대표이미지 1000×1000
```

---

## 들어 있는 것

| 구성 | 하는 일 |
|---|---|
| `commands/상세페이지제작.md` | 전체 절차 (0~6단계) |
| `agents/detail-asset-auditor` | 공급처 이미지 전수 점검 → 매니페스트 |
| `agents/detail-page-copywriter` | 한국어 카피 후보 작성 (없는 성능은 쓰지 않음) |
| `agents/detail-page-reviewer` | 추출한 이미지를 열어 크롭·정렬·로고 노출 검수 |
| `scripts/fetch_1688_images.py` | 1688 이미지 일괄 다운로드 (Referer 헤더 처리) |
| `scripts/erase_region.py` | 흰 배경 위 로고·컬러칩 지우기 |
| `scripts/html_to_images.py` | HTML → 섹션별 업로드 이미지 |
| `scripts/make_thumbnail.py` | 1000×1000 대표이미지 자르기 |
| `templates/detail_template.html` | 상세페이지 뼈대 (9개 섹션) |

---

## 업데이트 · 삭제

```bash
claude plugin marketplace update ongodsumo
claude plugin update detail-page-1688@ongodsumo
claude plugin uninstall detail-page-1688@ongodsumo
```

---

## 자주 막히는 곳

- **`python`을 찾을 수 없음** — 파이썬 설치 시 "Add Python to PATH"를 체크했는지 확인하세요. 맥은 `python3`.
- **이미지가 9장만 받아짐** — 1688에 로그인하지 않은 상태입니다. 로그인 후 다시 진행하세요.
- **브라우저 단계가 멈춤** — 데스크톱 앱의 브라우저 패널이 숨겨져 있으면 스크립트가 멈춥니다. 패널을 앞에 띄워 두세요.
- **토큰 사용량** — 이미지를 수십 장 열어보는 작업이라 한 상품에 사용량이 꽤 듭니다. 자산 점검·검수는 별도 에이전트로 나눠 메인 대화가 무거워지지 않게 했습니다.

## 주의

- 1688 이미지의 저작권은 공급처에 있습니다. 실제 판매에 쓸 때는 공급처 사용 허락 여부를 확인하세요.
- AI로 생성한 이미지를 상세페이지에 넣으면 그 사실을 표기하도록 되어 있습니다.
- 근거 없는 성능 수치(방수 등급·보온 온도 등)는 표시광고법 위반이 될 수 있어 카피에서 제외합니다.
