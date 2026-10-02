# AGENT HQ — 헬퍼판다 1인기업 운영본부

이 레포는 사장(사람) 1명 + AI 에이전트 팀으로 부업을 사업처럼 돌리는 본부다.
최종 목표: 사장은 **승인과 결정만**, 나머지 반복 작업은 에이전트가 처리한다.

## 팀 구성 (Phase 1)
| 에이전트 | 캐릭터 | 담당 | 파일 |
|---|---|---|---|
| chief | 🐼 판다 팀장 | 일정 관리, 다른 에이전트 호출, 일일 보고 | `.claude/agents/chief.md` |
| analyst | 🦉 부엉이 분석가 | 성과 데이터 분석, 개선안 | `.claude/agents/analyst.md` |
| shorts | 🦦 수달 PD | 자연과학 키즈 쇼츠 | `.claude/agents/shorts.md` |
| cardnews | 🦊 여우 에디터 | 인스타 카드뉴스 (매일 3장) | `.claude/agents/cardnews.md` |
| blog | 🐰 토끼 블로거 | 네이버 블로그 원고 | `.claude/agents/blog.md` |
| stock | 🐻 곰 애널리스트 | (Phase 2) 국내주식 분석 리포트 | `.claude/agents/stock.md` |

## 절대 규칙
1. **상태 보고 필수:** 모든 에이전트는 작업 시작/종료 시 상태를 기록한다.
   ```bash
   python scripts/status.py <agent> working "무슨 작업 중인지 한 줄"
   python scripts/status.py <agent> done "결과 한 줄"
   python scripts/status.py <agent> waiting "사장 승인 필요: 이유"
   python scripts/status.py <agent> error "에러 내용"
   ```
   이 기록이 GitHub Pages 대시보드(`docs/`)에 캐릭터로 표시된다.
2. **사람 승인 게이트:** 아래는 절대 자동으로 하지 않는다. 결과물을 `outbox/`에 만들고 `waiting` 상태로 보고만 한다.
   - SNS/블로그 실제 발행, 계정 설정 변경
   - 돈이 나가거나 들어오는 모든 작업
   - 주식 매매 (stock 에이전트는 주문 권한 자체가 없다)
3. **비밀정보 금지:** API 키, 비밀번호, 토큰은 `.env`에만. 절대 커밋/로그/상태 메시지에 쓰지 않는다.
4. **성과 기록:** 결과물을 만들면 `metrics/<division>.csv`에 한 줄 추가한다. analyst가 이걸 읽는다.
5. **짧게 보고:** 사장은 간결한 걸 좋아한다. 보고는 한국어, 핵심만.

## 폴더 구조
```
divisions/<분야>/   분야별 코드, 프롬프트, 템플릿
outbox/<분야>/      사장 승인 대기 중인 결과물
metrics/            성과 CSV (analyst 입력)
reports/daily/      chief 일일 보고 (YYYY-MM-DD.md)
reports/weekly/     analyst 주간 리포트
docs/               캐릭터 대시보드 (GitHub Pages)
scripts/            공용 스크립트 (status.py 등)
```

## 스케줄 (서버 크론에서 `claude -p` 로 실행)
| 시간 (KST) | 작업 |
|---|---|
| 06:00 매일 | cardnews: 카드뉴스 3장 생성 → outbox |
| 07:00 매일 | blog: 원고 1편 생성 → outbox |
| 05:30 매일 | analyst(일일): 전날 성과·승인/반려 피드백 → playbook 반영 (입력 없으면 생략) |
| 10:00 매일 | shorts: 쇼츠 기획 + 대본 1편 → outbox |
| 21:00 매일 | chief: 일일 보고서 작성 |
| 일 20:00 | analyst: 주간 성과 리포트 + 다음 주 개선안 |
| (Phase 2) 08:30 / 16:00 평일 | stock: 장전 브리핑 / 장마감 리포트 |

## 새 에이전트 추가 방법
1. `.claude/agents/<이름>.md` 작성 (기존 파일 복사해서 수정)
2. `divisions/<이름>/`, `metrics/<이름>.csv` 생성
3. `docs/data/team.json`에 캐릭터 추가
4. 위 스케줄 표 + 크론에 한 줄 추가
