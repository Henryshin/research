# -*- coding: utf-8 -*-
"""각 리포트 상단(KPI 카드 아래)에 THESIS / CATALYST / RISK 3줄 요약을 넣는다.

왜 필요한가 — 영어권 개인투자자는 한국 증권사 보고서 문법(1장부터 순서대로)으로
읽지 않는다. 결론·촉매·리스크를 맨 위에서 먼저 보고 계속 읽을지 결정한다.

원칙: **원문에 없는 주장은 절대 넣지 않는다.** 아래 문구는 전부 각 리포트의
결론·밸류에이션 절에 실제로 있는 문장에서만 뽑았다. 새 종목 추가 시에도
반드시 그 리포트가 실제로 한 말만 쓸 것.

사용
  python _tools/add_tldr.py            # dry-run
  python _tools/add_tldr.py --apply
  python _tools/add_tldr.py --remove --apply
"""
import re
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CSS_MARK = '/* tldr */'
CSS_BLOCK = """
  /* tldr */
  .tldr { border-left:3px solid var(--accent); padding:2px 0 2px 18px; margin:0 0 20px; }
  .tldr-row { display:flex; gap:14px; align-items:baseline; padding:7px 0; }
  .tldr-row + .tldr-row { border-top:1px solid var(--line); }
  .tldr-k { flex:0 0 74px; font-size:11.5px; font-weight:800; letter-spacing:0.7px; color:var(--accent); text-transform:uppercase; }
  .tldr-v { font-size:14.5px; color:var(--ink); line-height:1.65; word-break:keep-all; }
  @media (max-width:520px) {
    .tldr { padding-left:14px; }
    .tldr-row { flex-direction:column; gap:2px; padding:6px 0; }
    .tldr-k { flex:none; }
    .tldr-v { font-size:14px; }
  }
"""

KEYS_KO = ('투자논지', '촉매', '리스크')
KEYS_EN = ('THESIS', 'CATALYST', 'RISK')

DATA = {
    'hana-micron-067310-osat-packaging': {
        'ko': [
            '국내 OSAT 1위. 현재가 33,200원은 Base TP(28,160원)는 이미 넘어섰으나 Bull TP(45,500원)를 27% 밑도는 구간.',
            'Q1 2026 OSAT 영업이익률이 역사적 6~8%대에서 12.2%로 도약. 베트남 증설 가동률 정상화와 IDM의 HBM 집중에 따른 범용 메모리 외주 확대가 동시에 작용.',
            'FY25 금융비용 880억원이 영업이익의 69%를 잠식. 비지배지분까지 겹쳐 영업이익에서 지배주주순이익으로의 전환율이 29.8%에 그침.',
        ],
        'en': [
            "Korea's #1 OSAT. At 33,200 KRW the stock has already cleared the Base TP of 28,160 but sits 27% below the Bull TP of 45,500.",
            'Q1 2026 OSAT operating margin jumped from a historical 6-8% to 12.2%, as Vietnam capacity normalized just as IDMs pushed commodity memory back-end work out to OSATs.',
            'FY25 financial costs of 88.0bn KRW consumed 69% of operating profit. With minority interests on top, only 29.8% of operating profit reached controlling shareholders.',
        ],
    },
    'tck-064760-sic-ring': {
        'ko': [
            'CVD SiC 포커스링 글로벌 80~90% 독점. 다만 보수 가정에서는 Base -11.0% / Bull -4.3% / Best +2.4%로 세 시나리오가 모두 현재가(201,500원) 부근에 몰려 진입 매력이 제한적.',
            '선단공정(비포마켓) 증설이 유일한 매출 동인. 3년 누적 capa +15% / +25% / +35%가 시나리오를 가르며, HBM 웨이퍼 잠식이 18%에서 30%로 늘어 capa 증가를 가속.',
            '후발 경쟁(와이엠씨·와이컴·디에스테크노) 진입으로 OPM이 FY22 39%에서 FY25 28%로 약 11%p 하락. 독점 마진이 한 단계 낮아짐.',
        ],
        'en': [
            'An 80-90% global monopoly in CVD SiC focus rings. Yet on conservative assumptions all three cases cluster around the current 201,500 KRW: Base -11.0%, Bull -4.3%, Best +2.4%.',
            'Leading-edge (before-market) capacity expansion is the only revenue driver modeled. Cumulative 3-year capacity of +15%/+25%/+35% separates the cases, accelerated by HBM wafer share rising from 18% to 30%.',
            'Late entrants (YMC, Wycom, DS Techno) pushed operating margin down about 11pp, from 39% in FY22 to 28% in FY25. The monopoly margin has stepped down.',
        ],
    },
    'kioxia-285a-nand-memory': {
        'ko': [
            '세계 3위 NAND 순수 플레이. 탑다운(TAM x 점유율) 보수 추정에서 Base -78.9% / Bull -52.6% / Best -5.9%로 세 시나리오 모두 현재가(63,290엔)를 하회.',
            '현재가를 PER 8배로 정당화하려면 FY2028 NAND TAM이 2026년 대비 약 2.9배(약 64조엔)로 커지는 구조적 슈퍼사이클이 필요. AI 추론용 SSD 수요가 OPM 60%대를 상시화하면 상향 여지.',
            'NAND가 공급 과잉으로 전환되면 단가·마진이 급락해 Base(-78.9%)로 수렴. OPM이 FY2023 -23.5%에서 FY2025 +37.2%로 60%p 가까이 출렁인 단일 사업 구조.',
        ],
        'en': [
            "The world's #3 NAND pure-play. On a conservative top-down (TAM x share) basis every case lands below the current 63,290 JPY: Base -78.9%, Bull -52.6%, Best -5.9%.",
            'Justifying the current price at 8x earnings requires FY2028 NAND TAM roughly 2.9x its 2026 level (~64tn JPY) — a structural supercycle. AI inference SSD demand holding operating margin in the 60s would force an upgrade.',
            'If NAND swings to oversupply, pricing and margin collapse and the case converges on Base at -78.9%. Operating margin swung nearly 60pp, from -23.5% in FY2023 to +37.2% in FY2025.',
        ],
    },
    'dongjin-semichem-005290-euv-photoresist': {
        'ko': [
            '국내 유일의 포토레지스트 양산사. 현재가 43,050원은 바텀업 Base TP(59,900원)를 39.1% 밑돌지만, 구조는 검증된 본업 위에 미검증 EUV·HBM 옵션을 얹은 멀티플.',
            'EUV 감광액과 HBM CMP 슬러리 신규 라인이 실제 물량으로 실현되는지가 세 시나리오를 가름. 본업은 이미 회복 국면으로 OPM이 FY25 14.4%에서 1Q26 20.3%로 반등.',
            'EUV 감광액은 일본 4사가 95% 이상을 점유. 동사 양산 점유 확대가 지연되면 EUV 증분과 프리미엄 멀티플의 근거가 함께 약해짐.',
        ],
        'en': [
            "Korea's only mass-production photoresist maker. At 43,050 KRW it trades 39.1% below the bottom-up Base TP of 59,900 — but the multiple prices a verified core business plus an unverified EUV/HBM option.",
            'Whether the new EUV photoresist and HBM CMP slurry lines convert into real volume is what separates the three cases. The core business is already recovering, with operating margin rebounding from 14.4% in FY25 to 20.3% in 1Q26.',
            'Four Japanese suppliers hold over 95% of the EUV photoresist market. If the ramp in qualified share slips, both the EUV increment and the premium multiple lose their basis.',
        ],
    },
    'soulbrain-357780-semiconductor-materials': {
        'ko': [
            '국내 고순도 식각액 1위. 단가(P)가 아니라 물량(Q)에 실적이 연동되는 Q 레버리지 구조이며, 현재가 281,500원은 탑다운 Base TP(약 361,000원)를 28% 하회.',
            '소재 시장(SAM) 성장과 점유율 확대가 상방을 결정. Base는 SAM 120억달러·점유 5.9% 고정, Bull은 연 11% 성장·점유 6.6%를 가정. 1Q26 매출 2,638억원(+25.9% YoY), OPM 16.9%.',
            '고객이 삼성전자·SK하이닉스에 집중돼 양사 capex 사이클에 실적이 묶임. 메모리 capex가 컨센서스를 하회하거나 점유율이 정체되면 Base 하단으로 회귀.',
        ],
        'en': [
            "Korea's leader in high-purity etchants. Earnings track volume (Q), not price (P), and at 281,500 KRW the stock sits 28% below the top-down Base TP of roughly 361,000.",
            'Upside is set by materials SAM growth times share gain. Base holds SAM at $12bn and share at 5.9%; Bull assumes 11% annual growth and 6.6% share. 1Q26 revenue was 263.8bn KRW (+25.9% YoY) at a 16.9% operating margin.',
            'Customers are concentrated in Samsung Electronics and SK hynix, tying earnings to their capex cycle. If memory capex undershoots consensus or share stalls, the case reverts to the low end of Base.',
        ],
    },
    'spg-058610-blackstone-futronic': {
        'ko': [
            '로봇용 정밀 감속기 국산화 업체. 트레일링 PER 114배이고 BULL 가정을 반영한 FY29E 기준으로도 23.7배로, 성장 제조업 25배 멀티플을 적용하면 현재 주가가 적정 수준.',
            '정밀 감속기 양산 확대. 2024년 매출 약 130억원에서 2026년 13만대, 2029년 33만대 생산을 반영. 일본산 대비 40% 이상 가격 경쟁력과 납기 1년에서 1개월 단축이 근거.',
            '밸류에이션 자체가 부담. 현재 PER 114배, FY29E 포워드 기준으로도 26배로 오버밸류에이션 구간에 진입한 것으로 판단. (원문에 별도 리스크 절 없음)',
        ],
        'en': [
            'A domestic supplier of precision reducers for robots. Trailing P/E is 114x and even the bull-case FY29E figure is 23.7x, so on a 25x growth-manufacturing multiple the current price looks fair.',
            'The precision-reducer ramp. From roughly 13.0bn KRW of revenue in 2024, the model carries 130k units in 2026 rising to 330k in 2029, supported by a 40%+ price advantage over Japanese parts and lead times cut from a year to a month.',
            'Valuation itself. At 114x trailing and 26x on FY29E forward earnings, the report judges the stock to have entered overvalued territory. (The original carries no separate risk section.)',
        ],
    },
    'rainbow-robotics-277810-samsung-humanoid': {
        'ko': [
            '삼성전자가 35%를 보유한 로봇 자회사. 이익 기반으로는 Base -97.9% / Bull -90.9% / Best -33.7%로 전 구간 고평가이며, 극단 상방 시나리오조차 현재가(487,000원)를 33.7% 밑돎.',
            '주가가 실적이 아니라 삼성 이벤트(콜옵션 행사·휴머노이드 공개·자율공장 발주)에 반응하는 이벤트 드리븐 구조. 확인 지표는 분기 영업흑자 정착, 삼성향 수주의 계약 공시 전환, 자체 감속기 양산 적용.',
            '현 시총 9.45조원은 Best TP조차 33.7% 하회하며 2026년 고점 979,000원에서 이미 50.3% 조정. 잔여 콜옵션 458만주가 이익 시현 전 행사되면 소액주주가 상방을 공유하지 못할 수 있음.',
        ],
        'en': [
            "Samsung Electronics' 35%-owned robotics affiliate. On earnings every case is overvalued — Base -97.9%, Bull -90.9%, Best -33.7% — with even the extreme upside case 33.7% below the current 487,000 KRW.",
            'The stock is event-driven rather than earnings-driven, reacting to Samsung events (call-option exercise, humanoid reveals, autonomous-factory orders). The checkpoints are sustained quarterly operating profit, Samsung orders converting into disclosed contracts, and in-house reducers reaching production.',
            'The 9.45tn KRW market cap sits 33.7% above even the Best TP, and the stock has already fallen 50.3% from its 2026 high of 979,000. If the remaining 4.58m call-option shares are exercised before profits arrive, minority holders may not share the upside.',
        ],
    },
}


def build(lines, keys):
    rows = ''.join(
        f'    <div class="tldr-row"><span class="tldr-k">{k}</span><span class="tldr-v">{v}</span></div>\n'
        for k, v in zip(keys, lines))
    return f'  <div class="tldr">\n{rows}  </div>\n\n'


def main():
    apply_ = '--apply' in sys.argv
    remove = '--remove' in sys.argv
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    touched = 0
    for slug, langs in sorted(DATA.items()):
        path = os.path.join(slug, 'index.html')
        if not os.path.exists(path):
            print(f'  SKIP (없음)        {slug}')
            continue
        src = open(path, encoding='utf-8').read()
        has = '<div class="tldr">' in src

        if remove:
            if not has:
                print(f'  SKIP (없음)        {slug}')
                continue
            out = re.sub(r'  <div class="tldr">\n(?:.*\n)*?  </div>\n\n', '', src)
            out = out.replace(CSS_BLOCK, '')
            print(f'  REMOVE             {slug}')
        else:
            if has:
                print(f'  SKIP (이미 적용)   {slug}')
                continue
            out = src
            if CSS_MARK not in out:
                out = out.replace('\n/* type-scale:', CSS_BLOCK + '\n/* type-scale:', 1)
            ok = 0
            for lang, keys in (('ko', KEYS_KO), ('en', KEYS_EN)):
                anchor = f'  <div class="section" id="{lang[0] if lang == "ko" else "e"}s1">'
                anchor = '  <div class="section" id="%s1">' % ('ks' if lang == 'ko' else 'es')
                if anchor not in out:
                    print(f'      ! anchor 없음: {anchor}')
                    continue
                out = out.replace(anchor, build(langs[lang], keys) + anchor, 1)
                ok += 1
            if ok != 2:
                print(f'  SKIP (앵커 {ok}/2)   {slug}')
                continue
            print(f'  ADD                {slug}')

        touched += 1
        if apply_:
            open(path, 'w', encoding='utf-8', newline='').write(out)

    verb = '제거' if remove else '적용'
    print(f'\n{"DRY RUN — " if not apply_ else ""}{touched}개 리포트 {verb}'
          f'{" 예정. 실제 반영은 --apply" if not apply_ else " 완료."}')


if __name__ == '__main__':
    main()
