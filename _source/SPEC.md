# 리포트 빌드 규격 (SPEC)

`_source/<slug>.md` 원고 하나를 배포 가능한 `<slug>/index.html` 로 바꾸는 규칙과
배포 체크리스트. **디자인은 이 문서에 고정돼 있고 리포트마다 바꾸지 않는다.**

- 원고 템플릿: `_source/TEMPLATE.md`
- 레퍼런스 구현: `kioxia-285a-nand-memory/index.html` (7섹션 최신 표준)
- `spg-058610-blackstone-futronic` 은 **구형 4섹션 · 레거시 차트 계약**이라 참고만 하고 따라 하지 말 것

---

## 1. 파이프라인

```
로컬 원본 보고서 (한글, hwp/docx/txt)
        │
        ├─ STEP 1  구조 매핑 → _source/<slug>.md 의 KO 본문
        ├─ STEP 2  영문화     → 같은 파일의 EN 본문 (구조 1:1 대응)
        ├─ STEP 3  주가 데이터 → <slug>/chart-data.js
        ├─ STEP 4  빌드       → <slug>/index.html
        ├─ STEP 5  사이트 등록 → 루트 index.html · sitemap.xml · hreflang
        └─ STEP 6  검증 후 커밋·푸시
```

원고 1건 = **md 1개 + 폴더 1개(index.html, chart-data.js, 선택 assets/)**.

---

## 2. 디렉토리 규약

```
research/
├── index.html                 # 루트 목록 페이지 — 리포트 추가 시마다 카드 1장 추가
├── sitemap.xml                # 리포트 추가 시마다 <url> 1개 추가
├── robots.txt                 # 고정
├── .nojekyll                  # 고정 (밑줄 디렉토리 보존)
├── _source/                   # ★ 원고(md) — 이 문서의 대상. 배포물 아님
│   ├── SPEC.md
│   ├── TEMPLATE.md
│   └── <slug>.md
├── _tools/
│   ├── add_hreflang.py        # canonical 기준 hreflang 주입 (idempotent)
│   └── medium_export.py       # 배포된 EN 본문 → Medium 붙여넣기용 md
├── _medium/                   # medium_export.py 산출물 (생성물, 직접 수정 금지)
└── <slug>/
    ├── index.html
    ├── chart-data.js
    └── assets/                # 선택. 이미지·GIF
```

### slug 규칙
`<회사영문>-<종목코드>-<핵심키워드>` 소문자 하이픈.
예) `kioxia-285a-nand-memory`, `tck-064760-sic-ring`, `dongjin-semichem-005290-euv-photoresist`

한 번 배포한 slug는 **절대 바꾸지 않는다** (canonical·sitemap·외부 링크가 깨짐).

---

## 3. 디자인 시스템 (고정 — 변경 금지)

리포트마다 색·폰트·간격을 새로 정하지 않는다. 아래를 그대로 복사한다.

### 3.1 팔레트 (올리브)

| 토큰 | 라이트 | 다크 | 용도 |
|---|---|---|---|
| `--bg` | `#f7f7f2` | `#14160f` | 페이지 배경 |
| `--card` | `#fffefb` | `#1c1f15` | 카드/섹션 배경 |
| `--ink` | `#16180f` | `#edeee6` | 본문 강조 |
| `--ink-soft` | `#3f4433` | `#c2c5b4` | 본문 |
| `--ink-faint` | `#7d8271` | `#8b8f7d` | 캡션·라벨 |
| `--line` | `#ecede3` | `#262a1c` | 테두리·표 헤더 |
| `--line-2` | `#d9dbc9` | `#363b28` | 강한 테두리 |
| `--brand` | `#3f4d1e` | `#55652c` | 알약·번호배지·활성버튼 |
| `--accent` | `#55652c` | `#b5c193` | 링크·강조 |
| `--accent-hero` | `#a9b491` | `#a9b491` | 히어로 장식 도형 |
| `--neg` | `#c05b41` | `#e08a70` | 하락·경고 KPI |
| `--warn` | `#c98b2d` | `#d9a952` | 주의 KPI |
| `--note-bg` | `#f3f4ea` | `#191c12` | filter-note·disclaimer |
| `--hl` | `#eef0e2` | `#262a18` | 표 강조행 |

`<meta name="theme-color" content="#3f4d1e">` 고정.

### 3.2 타이포
- 폰트: **Pretendard** (jsDelivr CDN) → 시스템 폰트 폴백
- `font-variant-numeric: tabular-nums` — 표 숫자 정렬 유지
- 본문 13px / 한국어 본문(`.lang-ko`)은 13.5px + `word-break:keep-all`

### 3.3 레이아웃
- `.container` max-width **1080px** (루트 목록 페이지만 820px)
- 반응형 브레이크포인트 **860px**(태블릿) / **520px**(폰) — 둘 다 필수
- 스티키 `.nav` — 홈 링크 + 언어 토글 + TOC

### 3.4 컴포넌트 목록

| 컴포넌트 | 클래스 | 비고 |
|---|---|---|
| 히어로 | `.hero` > `.eyebrow` `h1` `.lede` `.meta` | `.lede`는 최신 표준(권장) |
| KPI 카드 | `.kpi-grid` > `.kpi-card[.neg\|.warn]` > `.label` `.value` `.unit` `.sub` | 정확히 4장 |
| 섹션 | `.section#es{n}` / `#ks{n}` > `h2 > .num` + `.sub-h` | |
| 표 | `.tbl-wrap` > `table.tbl` — `.rowlab` `.num` `tr.hl` | 가로 스크롤 래퍼 필수 |
| 주석·출처 | `.filter-note` | |
| 그림 그리드 | `figure.reducer-figs` > `.rfig` > `.imgbox` `.cap` + `.rfig-credit` | 선택 |
| 차트 | `.section#price-chart` + `.chart-range` + `#price-chart-box` | |
| 면책 | `.disclaimer` > `.ct-ko` / `.ct-en` | 전 리포트 공통 문구 |
| 푸터 | `footer.report-foot` | article 내부 (언어별 1개씩) |

---

## 4. md → HTML 매핑표

`<article id="lang-ko" class="lang-ko" lang="ko" hidden>` 안은 `ks{n}`,
`<article id="lang-en" lang="en" hidden>` 안은 `es{n}` 을 쓴다. 그 외 규칙은 동일.

### 4.1 섹션

```md
## 3. 산업 분석
> 3.1 원리 · 3.2 경쟁 구도 · 3.3 수요 동인
```
```html
<div class="section" id="ks3">
  <h2><span class="num">3</span>산업 분석</h2>
  <div class="sub-h">3.1 원리 · 3.2 경쟁 구도 · 3.3 수요 동인</div>
```
- `## ` 바로 뒤 `> ` 한 줄은 **반드시** `.sub-h` 로 변환. 없으면 생략 가능하나 최신 표준은 항상 넣는다.
- 섹션은 다음 `## ` 또는 본문 끝에서 `</div>` 로 닫는다.

### 4.2 소제목

```md
### 3.1. 원리
#### 3.1.1. 세부
```
```html
<h3><span class="no">3.1.</span>원리</h3>
<h4>3.1.1. 세부</h4>
```
- `h3` 는 번호를 `.no` 스팬으로 분리, `h4` 는 번호를 텍스트 그대로 둔다.
- `#### Base — 요약` 처럼 번호 없는 h4도 허용(시나리오 설명).

### 4.3 문단 / 인라인

| md | html |
|---|---|
| 일반 줄 | `<p>…</p>` |
| `**굵게**` | `<b>…</b>` (`.section p b` 가 `--ink` 로 강조) |
| `*기울임*` | `<em>…</em>` |
| `&`, `<`, `>` | `&amp;` `&lt;` `&gt;` 로 반드시 이스케이프 |

### 4.4 표

````md
:::table hl=3
| 기업 | 점유율 | 비고 |
|---|---:|---|
| A사 | 28% | … |
| B사 | 22% | … |
| C사 | 14% | … |
:::
````
```html
<div class="tbl-wrap">
<table class="tbl">
  <thead><tr><th>기업</th><th class="num">점유율</th><th>비고</th></tr></thead>
  <tbody>
    <tr><td class="rowlab">A사</td><td class="num">28%</td><td>…</td></tr>
    <tr><td class="rowlab">B사</td><td class="num">22%</td><td>…</td></tr>
    <tr class="hl"><td class="rowlab">C사</td><td class="num">14%</td><td>…</td></tr>
  </tbody>
</table>
</div>
```

변환 규칙:
- **`---:` 정렬 열** → `th`/`td` 에 `class="num"` (우측 정렬 + tabular-nums)
- **첫 번째 열** → `td class="rowlab"` (굵게)
- **`hl=n`** → n번째 **본문 행**(1-based)에 `tr class="hl"`. `hl=last` = 마지막 행. 복수는 `hl=2,5`. 없으면 생략
- `.tbl-wrap` 래퍼는 **모바일 가로 스크롤용이라 생략 금지**

### 4.5 주석 / 출처

````md
:::note
**출처** — TrendForce (2026-04). 점유율은 매출 기준 근사치.
:::
````
```html
<div class="filter-note"><b>출처</b> — TrendForce (2026-04). 점유율은 매출 기준 근사치.</div>
```
관례: 출처는 `**출처** —` / `**Source** —`, 계산 주석은 `**주:**` / `**Note:**`.

### 4.6 리스트

```md
- **사이클 피크 리스크** — 현재 주가는 피크 실적의 다년 지속을 선반영.
```
```html
<ul>
  <li><b>사이클 피크 리스크</b> — 현재 주가는 피크 실적의 다년 지속을 선반영.</li>
</ul>
```

### 4.7 그림 그리드 (선택)

````md
:::figs credit="출처: Wikimedia Commons — Planetary Gear Animation (Laserlicht, CC0)"
- planetary.gif | **유성(Planetary) 감속기** | 여러 기어가 태양기어 주위를 도는 구조 · 높은 강성
- harmonic.gif  | **하모닉(SH) 감속기**    | 얇은 플렉스플라인의 탄성 변형 · 초경량·초정밀
- cycloidal.gif | **RV(SR) 감속기**        | 사이클로이드 롤러 구동 · 고강성·고부하
:::
````
```html
<figure class="reducer-figs">
  <div class="rfig">
    <div class="imgbox"><img src="assets/planetary.gif" alt="유성 감속기 작동 원리 애니메이션" loading="lazy" width="300"></div>
    <div class="cap"><b>유성(Planetary) 감속기</b><span>여러 기어가 태양기어 주위를 도는 구조 · 높은 강성</span></div>
  </div>
  …
</figure>
<div class="rfig-credit">출처: Wikimedia Commons — Planetary Gear Animation (Laserlicht, CC0)</div>
```
- `loading="lazy"` 와 `alt` 필수. 이미지는 3장 기준(그리드가 3열 → 2열 → 1열로 반응).
- 남의 이미지는 **라이선스 표기 필수**, 실제 제품과 다를 수 있다는 문구 권장.

### 4.8 front-matter → HTML

| front-matter | 반영 위치 |
|---|---|
| `title.en` | `<title>` · `og:title` · JSON-LD `headline` |
| `description` | `meta[name=description]` · JSON-LD `description` |
| `og_description` / `twitter_*` | 각 meta 태그 |
| `keywords` | `meta[name=keywords]` (쉼표 결합) · JSON-LD `keywords` |
| `slug` | `canonical` = `https://henryshin.github.io/research/<slug>/` |
| `published` / `updated` | JSON-LD `datePublished` / `dateModified` |
| `company` / `exchange` / `ticker` | JSON-LD `about[0]` (`Corporation`, `tickerSymbol`) |
| `eyebrow` / `h1` / `lede` / `hero_meta` | `.hero` 내부 (언어별) |
| `kpi[]` | `.kpi-grid` (언어별 4장) |
| `toc[]` | `<script>` 의 `var TOC = {en:[…], ko:[…]}` |
| `lang_key` | `localStorage` 키 `"<lang_key>-lang"` |
| `chart.*` | `chart-data.js` 의 `window.ASOF/REFPX/REFLABEL/CURSYM` |
| `footer_note` | `footer.report-foot` 첫 줄 |
| `index_card` | 루트 `index.html` 의 `a.card` |

JSON-LD `@type` 은 **`AnalysisNewsArticle`** 고정, `inLanguage: ["en","ko"]`.

`tickerSymbol` 접두사는 거래소별로 다르다:

| `exchange` | `tickerSymbol` | `chart.yahoo_symbol` |
|---|---|---|
| KOSPI | `KRX:000000` | `000000.KS` |
| KOSDAQ | `KRX:000000` | `000000.KQ` |
| TSE Prime | `TYO:285A` | `285A.T` |
| NASDAQ / NYSE | `NASDAQ:TICKER` / `NYSE:TICKER` | `TICKER` |

---

## 5. 차트 계약 (chart-data.js)

```js
window.OHLC=[{t:"2025-08-01",o:1,h:2,l:0,c:1}, …];
window.ASOF="2026-08-01";
window.REFPX=63290;
window.REFLABEL="63,290 (07-31)";
window.CURSYM="₩";
```

- 전역 이름은 **`window.OHLC`** (SPG의 `SPG_OHLC` 는 레거시 — 신규는 쓰지 않는다)
- `t` 는 `YYYY-MM-DD`, o/h/l/c 는 숫자(콤마·통화기호 없음)
- 기간은 **최근 1년 일봉** 기준(상장 1년 미만이면 상장일부터)
- 데이터는 Yahoo Finance 일봉. 심볼 규칙: KOSPI `000000.KS` / KOSDAQ `000000.KQ` / 도쿄 `285A.T` / 미국 `TICKER`
- `index.html` 쪽 스크립트는 전 리포트 공통이며 `var sym = window.CURSYM || '₩';` 로 통화기호를 받는다 — **하드코딩 금지**
- 차트가 없으면 `chart.enabled: false` 로 두고 `#price-chart` 섹션과 두 `<script>` 태그를 통째로 뺀다

---

## 6. 이중언어 동작

- 두 `<article>` 이 한 DOM에 있고 `hidden` 속성으로 토글된다.
- 언어 결정 우선순위: `?lang=` 쿼리 → `localStorage["<lang_key>-lang"]` → 브라우저 언어(`ko` 시작이면 ko) → `en`
- `<article>` **밖**의 공용 영역(차트 제목, 차트 주석, 면책)은 `.ct-ko` / `.ct-en` 로 언어 분기한다.
- TOC는 언어별 라벨로 JS가 재생성한다.

---

## 7. 배포 체크리스트

원고 하나를 올릴 때 아래를 **순서대로 전부** 수행한다. 하나라도 빠지면 배포 불가.

- [ ] **1. 원고** `_source/<slug>.md` 작성 — `<<...>>` 플레이스홀더 0개
- [ ] **2. 구조 검증** — KO/EN 섹션 수·h3 수·h4 수·표 수·표 열 수 전부 일치
- [ ] **3. 목차** — `toc` 항목 수 = 섹션 수, 순서 일치
- [ ] **4. KPI** — 정확히 4장, 값/단위 KO·EN 정합
- [ ] **5. chart-data.js** 생성 — `OHLC`/`ASOF`/`REFPX`/`REFLABEL`/`CURSYM` 5개 전부
- [ ] **6. index.html 빌드** — 섹션 id `ks1..ksN` / `es1..esN`, `lang_key` 반영
- [ ] **7. 면책 조항** — 공통 문구 그대로 복사 (§8 참조, 문구 수정 금지)
- [ ] **8. 모바일 CSS** — 860px·520px 브레이크포인트 둘 다 포함
- [ ] **9. 루트 `index.html`** — `index_card` 를 카드로 추가, **최신 글이 맨 위**
- [ ] **10. `sitemap.xml`** — `<url>` 추가 (`priority` 1.0, `changefreq` monthly), 루트 `lastmod` 갱신
- [ ] **11. hreflang** — `python _tools/add_hreflang.py <slug>` 실행
- [ ] **12. 링크 확인** — `href="../"` 홈 링크, canonical/og:url 이 실제 slug와 일치
- [ ] **13. 렌더 확인** — 라이트/다크 · 데스크톱/모바일 · KO/EN 4조합
- [ ] **14. 커밋·푸시**
- [ ] **15. (선택) Medium** — `python _tools/medium_export.py <slug>`

---

## 8. 면책 조항 (공통 · 수정 금지)

모든 리포트의 `<article>` **바깥**, `</div>` (container) 직전에 그대로 넣는다.

```html
<div class="disclaimer">
  <div class="ct-ko" hidden>
    <h3>면책 조항 (Disclaimer)</h3>
    <p>본 보고서는 작성자 개인의 견해를 담은 <b>정보 제공용 자료</b>이며, 특정 종목의 매수·매도·보유를 권유하거나 유도하기 위한 <b>투자 자문 또는 투자 권유가 아닙니다.</b> 작성자는 공인된 투자자문업자·금융투자업자가 아닙니다.</p>
    <p>본 자료는 공개된 자료(DART 공시, 금융정보 제공사, 언론 등)를 바탕으로 작성되었으나 그 <b>정확성·완전성·적시성을 보장하지 않으며</b>, 수치·전망·추정치는 오류를 포함할 수 있고 사전 고지 없이 변경될 수 있습니다. 미래 실적·목표주가 등 전망 정보는 불확실성을 내포하며 실제 결과와 다를 수 있습니다.</p>
    <p>작성자는 본 자료에서 다룬 종목을 보유하고 있거나 향후 매매할 수 있습니다. 모든 투자의 <b>최종 판단과 책임은 투자자 본인</b>에게 있으며, 작성자는 본 자료의 이용으로 발생하는 어떠한 직·간접적 손실에 대해서도 책임지지 않습니다. 투자 전 반드시 스스로 확인(DYOR)하시고 필요 시 전문가와 상담하시기 바랍니다.</p>
  </div>
  <div class="ct-en" hidden>
    <h3>Disclaimer</h3>
    <p>This report reflects the author's personal opinions and is provided <b>for informational purposes only.</b> It is <b>not investment advice, nor a recommendation or solicitation</b> to buy, sell, or hold any security. The author is not a licensed investment adviser or financial professional.</p>
    <p>The material is based on publicly available sources (regulatory filings, financial-data providers, news, etc.) but its <b>accuracy, completeness, and timeliness are not guaranteed</b>; figures, projections, and estimates may contain errors and are subject to change without notice. Forward-looking statements such as forecasts and price targets involve uncertainty and may differ materially from actual results.</p>
    <p>The author may hold or may in the future trade positions in the securities discussed. <b>All investment decisions and their consequences are solely the reader's own responsibility;</b> the author accepts no liability for any direct or indirect loss arising from the use of this material. Always do your own research (DYOR) and consult a qualified professional where appropriate.</p>
  </div>
</div>
```

---

## 9. 함정 (실제로 깨졌던 것들)

1. **`.ct-ko` / `.ct-en` 은 `div` 로 감쌀 것.** 면책처럼 여러 `<p>` 를 묶을 때 `span` 을 쓰면
   인라인 요소가 블록을 감싸는 꼴이 되어 레이아웃이 붕괴한다. 차트 제목처럼 **한 줄 텍스트일 때만** `span` 허용.
2. **`hidden` 속성을 두 `<article>` 에 모두 붙여둘 것.** 초기 렌더에서 두 언어가 동시에 보였다 사라지는 깜빡임 방지.
3. **`.tbl-wrap` 생략 금지.** 폰에서 넓은 표가 페이지 전체를 가로로 밀어버린다.
4. **모바일 CSS는 나중에 붙이면 반드시 누락된다.** 빌드 시점에 860/520 두 블록을 처음부터 포함.
5. **`hreflang` 은 손으로 쓰지 말고 `add_hreflang.py`.** 손으로 넣으면 재편집 때 중복·유실된다(실제 유실 사고 있었음).
6. **`sitemap.xml` 과 루트 `index.html` 갱신을 잊지 말 것.** 리포트는 배포됐는데 아무도 찾아올 수 없는 상태가 된다.
7. **`_medium/*.md` 는 생성물.** 직접 고치지 말고 `medium_export.py` 를 다시 돌린다.
8. **`num` 클래스는 두 군데서 쓰인다** — `h2 > span.num`(번호 배지)과 `td.num`(우측정렬 숫자).
   파서를 만든다면 태그로 구분해야 한다(`medium_export.py` 가 같은 이유로 태그 검사를 한다).
9. **slug 변경 금지.** canonical·sitemap·외부 유입이 전부 깨진다.

---

## 10. 규격 변경 시

디자인/구조를 바꾸면 **기존 리포트 전체에 소급 적용**하고 이 문서를 함께 고친다.
(과거에 면책 박스와 모바일 CSS를 뒤늦게 의무화하면서 5개 리포트를 일괄 백필한 전례가 있다.)
한 리포트만 다르게 생긴 상태를 남기지 않는다.
