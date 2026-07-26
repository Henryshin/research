---
# ═══════════════════════════════════════════════════════
#  리포트 원고 템플릿 — 복사해서 사용
# ═══════════════════════════════════════════════════════
#  1. 이 파일을 _source/<slug>.md 로 복사한다.
#       예: _source/hanmi-semiconductor-042700-tc-bonder.md
#  2. << >> 로 감싼 부분을 전부 채운다. 하나라도 남으면 빌드 금지.
#  3. 변환 규칙은 _source/SPEC.md §4 매핑표를 따른다.
#
#  불변 규칙 3가지
#   · KO/EN 두 본문은 섹션·소제목·표의 개수와 순서가 완전히 동일해야 한다.
#     (한쪽에만 문단·표를 추가하지 말 것)
#   · 표의 열 개수와 정렬(---:)도 KO/EN 동일해야 한다.
#   · toc 항목 수 = 본문 섹션 수.  kpi 는 정확히 4개.
# ═══════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════
# 1. 식별자 / 배포 경로
# ═══════════════════════════════════════════════════════
slug: <<company-000000-keyword>>      # 폴더명 = URL 경로. 소문자-하이픈. 예: kioxia-285a-nand-memory
lang_key: <<company>>                 # localStorage 키 접두사 → "<lang_key>-lang". 예: kioxia
exchange: <<KOSDAQ>>                  # KOSPI | KOSDAQ | TSE Prime | NASDAQ | NYSE ...
ticker: <<000000>>
company:
  ko: <<한글 회사명>>
  en: <<English Company Name>>

# ═══════════════════════════════════════════════════════
# 2. 발행 메타
# ═══════════════════════════════════════════════════════
published: <<2026-08-01>>             # 최초 작성일 → JSON-LD datePublished
updated:   <<2026-08-01>>             # 수치 업데이트일 → JSON-LD dateModified
version:   <<v1>>                     # 원고 버전. 없으면 이 줄 삭제

hero_meta:                            # 히어로 하단 메타 라인 (· 로 구분되어 렌더)
  ko:
    - "최초작성 <<2026-08>>"
    - "수치 업데이트 <<2026-08-01>> (기준주가 <<00,000>>원, <<07-31>> 종가)"
  en:
    - "Original <<Aug 2026>>"
    - "Figures updated <<2026-08-01>> (ref. price <<00,000 KRW>>, <<Jul 31>> close)"

# ═══════════════════════════════════════════════════════
# 3. SEO / 소셜
# ═══════════════════════════════════════════════════════
title:                                # <title> · og:title · JSON-LD headline. 60~70자 권장
  en: "<<Company (000000) Equity Analysis — One-line Hook>>"
h1:                                   # 히어로 대제목. title보다 짧게
  ko: "<<회사명(000000) 분석보고서>>"
  en: "<<Company (000000) Equity Analysis>>"
eyebrow:                              # 히어로 알약 라벨. CSS가 대문자로 변환
  ko: "Equity Analysis · <<KOSDAQ 000000>>"
  en: "Equity Analysis · <<KOSDAQ 000000>>"
lede:                                 # h1 아래 한 줄 요약. · 로 항목 나열하는 스타일
  ko: "<<핵심 포지션 · 투자 논점 · 거래소 · 섹터 · 주가 00,000원 · 시총 0.0조원 (2026-08-01)>>"
  en: "<<core position · thesis · exchange · sector · share price 00,000 KRW · market cap ~0.0tn KRW (2026-08-01)>>"

description: "<<150~160자. 회사 정체성 + 이 리포트가 다루는 것 + Korean/English + Figures updated 날짜.>>"
og_description: "<<description 압축판. 110~130자.>>"
twitter_title: "<<Company (000000) Equity Analysis>>"
twitter_description: "<<90~110자.>>"
keywords:                             # 앞 5개가 Medium 태그로 재사용됨 → 영문/숫자 위주를 앞에 배치
  - <<Company Name>>
  - <<000000>>
  - <<KOSDAQ>>
  - <<한글 회사명>>
  - <<key theme>>
  - <<peer company>>

# ═══════════════════════════════════════════════════════
# 4. KPI 카드 — 정확히 4장
#    tone 생략=올리브(기본) | neg=적색 테두리 | warn=황색 테두리
#    관례: 1)현재가 2)시가총액 3)밸류에이션(neg) 4)목표주가·전망PER(warn)
# ═══════════════════════════════════════════════════════
kpi:
  - label: { ko: "현재가",      en: "Share price" }
    value: "<<00,000>>"
    unit:  { ko: "원",          en: "KRW" }
    sub:   { ko: "52주 <<00,000 ~ 000,000>>원", en: "52w range <<00,000 – 000,000>>" }

  - label: { ko: "시가총액",    en: "Market cap" }
    value: "<<0,000>>"
    unit:  { ko: "억원",        en: "bn KRW" }
    sub:   { ko: "발행주식수 약 <<0,000만>> 주", en: "~<<00.0M>> shares out" }

  - tone: neg
    label: { ko: "트레일링 PER", en: "Trailing P/E" }
    value: "<<00>>"
    unit:  { ko: "배",          en: "x" }
    sub:   { ko: "<<25년 순이익 000억 기준>>", en: "<<On 2025 NP of 00.0bn KRW>>" }

  - tone: warn
    label: { ko: "<<29F PER (BULL)>>", en: "<<29E P/E (Bull)>>" }
    value: "<<00.0>>"
    unit:  { ko: "배",          en: "x" }
    sub:   { ko: "<<선택. 없으면 삭제>>", en: "<<optional; delete line if unused>>" }

# ═══════════════════════════════════════════════════════
# 5. 주가 차트
#    OHLC 원본은 <slug>/chart-data.js 에 별도 생성 (SPEC.md STEP 3 참조)
# ═══════════════════════════════════════════════════════
chart:
  enabled: true                       # 차트 없이 낼 경우 false → price-chart 섹션 통째 생략
  yahoo_symbol: "<<000000.KQ>>"       # 000000.KS(KOSPI) | 000000.KQ(KOSDAQ) | 285A.T(TSE) | TICKER(US)
  asof:     <<2026-08-01>>            # window.ASOF
  refpx:    <<00000>>                 # window.REFPX  — 숫자만, 콤마 없이
  reflabel: "<<00,000 (07-31)>>"      # window.REFLABEL — 차트 기준선 라벨
  cursym:   "<<₩>>"                   # window.CURSYM — ₩ | ¥ | $
  note:                               # 차트 하단 filter-note
    ko: "**주:** 정적 스냅샷(<<2026-08-01>> 기준, Yahoo Finance 일봉). 실시간이 아니며 정보 제공용임."
    en: "**Note:** static snapshot as of <<2026-08-01>> (Yahoo Finance daily). Not real-time; for information only."

# ═══════════════════════════════════════════════════════
# 6. 목차 — 본문 섹션 수와 반드시 일치 (순서도 동일)
# ═══════════════════════════════════════════════════════
toc:
  - { ko: "1 · 회사 개요",   en: "1 · Overview" }
  - { ko: "2 · 지배구조",    en: "2 · Ownership" }
  - { ko: "3 · 산업 분석",   en: "3 · Industry" }
  - { ko: "4 · 사업 모델",   en: "4 · Business" }
  - { ko: "5 · 재무 분석",   en: "5 · Financials" }
  - { ko: "6 · 밸류에이션",  en: "6 · Valuation" }
  - { ko: "7 · 결론",        en: "7 · Conclusion" }

# ═══════════════════════════════════════════════════════
# 7. 루트 index.html 카드 (최신 글이 맨 위)
# ═══════════════════════════════════════════════════════
index_card:
  tag: "<<KOSDAQ 000000>>"
  title: "<<Company (000000) Equity Analysis>>"
  summary: "<<2~3줄. 투자 논점 압축 + 'Figures updated Aug 1, 2026.' 로 마감>>"
  meta: "<<Original Aug 2026 · Figures updated 2026-08-01 · Sector tag · Theme tag>>"

# ═══════════════════════════════════════════════════════
# 8. 푸터 근거 문장 (선택 — 없으면 footer_note 통째 삭제)
# ═══════════════════════════════════════════════════════
footer_note:
  ko: "<<현재가 00,000원 · 시가총액 0.0조원(2026-07-31 종가 기준). 재무·산업·경쟁 정보는 ... 를 종합함.>>"
  en: "<<Current price 00,000 KRW · market cap ~0.0tn KRW (Jul 31, 2026 close). Financial/industry/competitive information is based on ...>>"

# ═══════════════════════════════════════════════════════
# 9. 이미지 자산 (선택 — 없으면 assets 통째 삭제)
#    파일은 <slug>/assets/ 에 둔다. 라이선스 표기 필수.
# ═══════════════════════════════════════════════════════
assets:
  - file: <<diagram.gif>>
    license: "<<Wikimedia Commons — Title (Author, CC0)>>"
---


<!-- ══════════════════════════════════════════════════════════
     본문 시작.
     아래 두 블록(KO / EN)은 구조가 1:1로 대응해야 한다.
     사용 가능한 문법은 SPEC.md §4 매핑표 참조:
       ## 1. 제목        → 섹션 (번호 배지 + h2)
       > 소제목 요약      → .sub-h  (섹션 h2 바로 아래 1줄)
       ### 1.1. 제목      → h3
       #### 1.1.1. 제목   → h4
       일반 문단          → p
       :::table hl=n     → .tbl-wrap > table.tbl   (---: 정렬열 = .num, 1열 = .rowlab)
       :::note           → .filter-note  (출처/주석)
       :::figs           → figure.reducer-figs  (이미지 3장 그리드)
       - **라벨** — 설명  → ul > li (리스크 목록 등)
     ══════════════════════════════════════════════════════════ -->


# ══════════════ KO ══════════════

## 1. 회사 개요
> 1.1 기본 정보 · 1.2 핵심 사업모델 · 1.3 주요 제품군

### 1.1. 기본 정보
<<설립 연혁, 상장 시점, 무엇을 만드는 회사인지 3~4문장.>>

:::table
| 항목 | 내용 | 항목 | 내용 |
|---|---|---|---|
| 종목명 / 코드 | <<회사명 / 000000>> | 시가총액 | <<0,000억원 (2026-08-01)>> |
| 설립 | <<0000년>> | 현재가 | <<00,000원>> |
| 본사 | <<소재지>> | 발행주식수 | <<00,000,000>> |
| 상장 | <<KOSDAQ 0000년>> | 결산월 | <<12월>> |
| 주요 제품 | <<...>> | 대표이사 | <<...>> |
:::

### 1.2. 핵심 사업모델
<<수익이 어디서 나오는지. 2~3문단.>>

### 1.3. 주요 제품군
<<매출 구성 설명 1문단 + 표.>>

:::table hl=4
| 제품군 | 주요 용도 및 특징 | 주요 납품처 | 매출 비중 (%) |
|---|---|---|---:|
| <<...>> | <<...>> | <<...>> | <<00.0>> |
:::
:::note
**출처** — <<DART 사업보고서(2025) 기준.>>
:::


## 2. 지배구조
> 2.1 지분 구조 · 2.2 희석 요인 및 오버행

### 2.1. 지분 구조
<<최대주주 및 특수관계인 지분율, 경영권 안정성 1~2문단.>>

:::table hl=last
| 주주명 | 관계 | 보유 주식수 | 지분율 (%) |
|---|---|---:|---:|
| <<...>> | <<본인 (최대주주)>> | <<0,000,000>> | <<00.00>> |
| 합계 | | <<0,000,000>> | <<00.00>> |
:::

### 2.2. 희석 요인 및 오버행(Overhang)
<<CB/BW 잔액, 보호예수 해제, 대주주 매각 가능성.>>


## 3. 산업 분석
> 3.1 <<원리·구조>> · 3.2 <<경쟁 구도>> · 3.3 <<수요 동인>>

### 3.1. <<제품/기술이 어떻게 작동하는가>>
<<비전문가도 읽히도록 기초부터. 2~3문단.>>

### 3.2. <<글로벌 경쟁 구도>>
<<점유율 구조 1~2문단 + 표.>>

:::table hl=3
| 기업 | 점유율 | 순위 | 비고 |
|---|---:|---|---|
| <<...>> | <<00%>> | <<#1>> | <<...>> |
:::
:::note
**출처** — <<조사기관 (기준분기). 점유율은 매출 기준 근사치.>>
:::

### 3.3. <<수요 동인과 병목>>
<<사이클을 만드는 메커니즘. 결론부터 쓰고 근거를 붙인다.>>


## 4. 사업 모델
> 4.1 매출 구조 · 4.2 고객 및 전방 수요

### 4.1. 매출 구조
<<부문별 매출 비중과 수익성.>>

:::table
| 항목 | <<2024>> | <<2025>> | 비고 |
|---|---:|---:|---|
| 매출액 | <<...>> | <<...>> | <<+00% YoY>> |
| 영업이익 | <<...>> | <<...>> | <<OPM 00% → 00%>> |
:::

### 4.2. 고객 및 전방 수요
<<고객 집중도, 교섭력, 전방 산업별 수요 성격.>>


## 5. 재무 분석
> <<사이클성 · 수익성 · 재무구조>>

<<최근 5년 흐름을 사이클성/수익성/재무구조 3축으로 서술.>>

:::table hl=last
| 항목 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---:|---:|---:|---:|---:|
| 매출액 | <<...>> | <<...>> | <<...>> | <<...>> | <<...>> |
| 영업이익 | <<...>> | <<...>> | <<...>> | <<...>> | <<...>> |
| 영업이익률 | <<...>> | <<...>> | <<...>> | <<...>> | <<...>> |
| 순이익 | <<...>> | <<...>> | <<...>> | <<...>> | <<...>> |
| EPS (원) | <<...>> | <<...>> | <<...>> | <<...>> | <<...>> |
:::
:::note
**출처** — <<DART 공시 / 데이터 제공사. 단위: 억원.>>
:::


## 6. 밸류에이션
> 6.1 적용 PER · 6.2 시나리오 · 6.3 시나리오 설명 · 6.4 리스크

<<현재 밸류에이션 진단 1~2문단.>>

### 6.1. 적용 PER
<<피어 대비 어느 수준을 적용하고 왜 그런지.>>

:::table hl=last
| 글로벌 피어 | 사업 | 포워드 PER |
|---|---|---:|
| <<...>> | <<...>> | <<0.0>> |
| 적용 PER | <<보수적 관점>> | <<0>> |
:::
:::note
**출처** — <<데이터 출처 (기준일). 전부 포워드 기준.>>
:::

### 6.2. 시나리오 표 (<<2029E>>)
<<공통 가정: 발행주식수, 세율, 적용 PER.>>

:::table hl=last
| 항목 | Base | Bull | Best |
|---|---:|---:|---:|
| <<시장 규모>> | <<...>> | <<...>> | <<...>> |
| <<점유율>> | <<...>> | <<...>> | <<...>> |
| 매출액 | <<...>> | <<...>> | <<...>> |
| 영업이익률 | <<...>> | <<...>> | <<...>> |
| 순이익 | <<...>> | <<...>> | <<...>> |
| EPS | <<...>> | <<...>> | <<...>> |
| 적용 PER (배) | <<...>> | <<...>> | <<...>> |
| 목표주가 | <<...>> | <<...>> | <<...>> |
| 현재가 대비 | <<−00.0%>> | <<−00.0%>> | <<+00.0%>> |
:::
:::note
**주:** <<기준주가 00,000원(2026-07-31 종가) 기준 재계산. 가정·수식은 원본 모델 그대로임.>>
:::

### 6.3. 시나리오 설명

#### Base — <<한 줄 요약>>
<<가정과 함의.>>

#### Bull — <<한 줄 요약>>
<<가정과 함의.>>

#### Best — <<한 줄 요약>>
<<가정과 함의.>>

### 6.4. 리스크 요인
- **<<리스크 1>>** — <<설명.>>
- **<<리스크 2>>** — <<설명.>>
- **<<리스크 3>>** — <<설명.>>


## 7. 결론
> <<한 줄 판정 요약>>

<<시나리오 결과를 숫자로 재확인 1문단.>>

<<이 종목의 구조적 성격(사이클/해자/집중도) 1문단.>>

<<현재가를 정당화하려면 무엇이 필요한지 1문단.>>

<<보유자·신규 진입자에게 주는 실무적 함의 1문단.>>


# ══════════════ EN ══════════════

## 1. Company Overview
> 1.1 Basic information · 1.2 Core business model · 1.3 Main product lines

### 1.1. Basic Information
<<Mirror of KO 1.1. Same paragraph count.>>

:::table
| Item | Detail | Item | Detail |
|---|---|---|---|
| Ticker / code | <<Company / 000000>> | Market cap | <<...>> |
| Founded | <<...>> | Share price | <<...>> |
| HQ | <<...>> | Shares outstanding | <<...>> |
| Listing | <<...>> | Fiscal year-end | <<...>> |
| Key products | <<...>> | CEO | <<...>> |
:::

### 1.2. Core Business Model
<<...>>

### 1.3. Main Product Lines
<<...>>

:::table hl=4
| Product line | Main uses / characteristics | Key customers | Rev. share (%) |
|---|---|---|---:|
| <<...>> | <<...>> | <<...>> | <<00.0>> |
:::
:::note
**Source** — <<...>>
:::


## 2. Ownership Structure
> 2.1 Shareholding structure · 2.2 Dilution & overhang

### 2.1. Shareholding Structure
<<...>>

:::table hl=last
| Shareholder | Relation | Shares held | Stake (%) |
|---|---|---:|---:|
| <<Name (한글이름)>> | <<Principal (largest shareholder)>> | <<0,000,000>> | <<00.00>> |
| Total | | <<0,000,000>> | <<00.00>> |
:::

### 2.2. Dilution & Overhang
<<...>>


## 3. Industry Analysis
> 3.1 <<How it works>> · 3.2 <<Competitive landscape>> · 3.3 <<Demand drivers>>

### 3.1. <<How It Works>>
<<...>>

### 3.2. <<Global Competitive Landscape>>
<<...>>

:::table hl=3
| Company | Share | Rank | Notes |
|---|---:|---|---|
| <<...>> | <<00%>> | <<#1>> | <<...>> |
:::
:::note
**Source** — <<...>>
:::

### 3.3. <<Demand Drivers & Bottleneck>>
<<...>>


## 4. Business Model
> 4.1 Revenue mix · 4.2 Customers & end-demand

### 4.1. Revenue Structure
<<...>>

:::table
| Item | <<FY2024>> | <<FY2025>> | Notes |
|---|---:|---:|---|
| Revenue | <<...>> | <<...>> | <<+00% YoY>> |
| Operating profit | <<...>> | <<...>> | <<OPM 00% → 00%>> |
:::

### 4.2. Customers & End-Demand
<<...>>


## 5. Financial Analysis
> <<Cyclicality · profitability · financial structure>>

<<...>>

:::table hl=last
| Item | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---:|---:|---:|---:|---:|
| Revenue | <<...>> | <<...>> | <<...>> | <<...>> | <<...>> |
| Operating profit | <<...>> | <<...>> | <<...>> | <<...>> | <<...>> |
| OPM | <<...>> | <<...>> | <<...>> | <<...>> | <<...>> |
| Net profit | <<...>> | <<...>> | <<...>> | <<...>> | <<...>> |
| EPS (KRW) | <<...>> | <<...>> | <<...>> | <<...>> | <<...>> |
:::
:::note
**Source** — <<Regulatory filings / data provider. Unit: 100M KRW.>>
:::


## 6. Valuation
> 6.1 Applied P/E · 6.2 Scenarios · 6.3 Narratives · 6.4 Risks

<<...>>

### 6.1. Applied P/E
<<...>>

:::table hl=last
| Global peer | Business | Forward P/E |
|---|---|---:|
| <<...>> | <<...>> | <<0.0>> |
| Applied P/E | <<conservative>> | <<0>> |
:::
:::note
**Source** — <<...>>
:::

### 6.2. Scenario Table (<<FY2029E>>)
<<Common assumptions: shares outstanding, tax rate, applied P/E.>>

:::table hl=last
| Item | Base | Bull | Best |
|---|---:|---:|---:|
| <<TAM>> | <<...>> | <<...>> | <<...>> |
| <<Share>> | <<...>> | <<...>> | <<...>> |
| Revenue | <<...>> | <<...>> | <<...>> |
| OPM | <<...>> | <<...>> | <<...>> |
| Net profit | <<...>> | <<...>> | <<...>> |
| EPS | <<...>> | <<...>> | <<...>> |
| Applied P/E (x) | <<...>> | <<...>> | <<...>> |
| Target price | <<...>> | <<...>> | <<...>> |
| vs current price | <<−00.0%>> | <<−00.0%>> | <<+00.0%>> |
:::
:::note
**Note:** <<recomputed on the 00,000 KRW close (Jul 31, 2026). Assumptions and formulas unchanged from the original model.>>
:::

### 6.3. Scenario Narratives

#### Base — <<one-line summary>>
<<...>>

#### Bull — <<one-line summary>>
<<...>>

#### Best — <<one-line summary>>
<<...>>

### 6.4. Risk Factors
- **<<Risk 1>>** — <<...>>
- **<<Risk 2>>** — <<...>>
- **<<Risk 3>>** — <<...>>


## 7. Conclusion
> <<one-line verdict>>

<<...>>

<<...>>

<<...>>

<<...>>
