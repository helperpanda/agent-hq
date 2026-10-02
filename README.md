# 🐼 Agent HQ

헬퍼판다 1인기업 에이전트 본부. Claude Code 서브에이전트 + GitHub Pages 캐릭터 대시보드.

## 1. 세팅 (10분)
```bash
# 1) 이 폴더를 GitHub에 private 레포로 올리기
cd agent-hq
git init && git add . && git commit -m "init agent hq"
gh repo create agent-hq --private --source=. --push

# 2) 비밀키
cp .env.example .env   # PEXELS_API_KEY 등 입력
```

**대시보드 켜기:** GitHub 레포 → Settings → Pages → Source: `Deploy from a branch`, Branch: `main` / `/docs` → Save
→ 1~2분 뒤 `https://<깃허브아이디>.github.io/agent-hq/` 에서 캐릭터 사무실이 보임.

> ⚠️ 무료 계정은 private 레포에 Pages를 못 켜. 방법 2개:
> - 레포는 private 유지 + 대시보드만 별도 public 레포로 (`docs/`만 push)
> - 또는 레포 public (단, `outbox/`·`reports/`가 공개되니 `.gitignore`에 추가할 것)
> 상태 메시지엔 비밀정보가 안 들어가게 CLAUDE.md에 규칙을 넣어뒀어.

## 2. 에이전트 써보기
```bash
claude
> cardnews 에이전트로 오늘 카드뉴스 만들어줘
> 판다 팀장, 오늘 보고해줘
```
에이전트가 일할 때마다 `scripts/status.py`로 상태를 남기고, push하면 대시보드에 반영돼.

## 3. 자동 실행 (GCP VM 크론)
```cron
# crontab -e  (서버 시간대가 KST 기준일 때)
0 6 * * *    cd ~/agent-hq && git pull -q && claude -p "cardnews 에이전트로 오늘 카드뉴스 만들어" && python scripts/status.py cardnews waiting "8:30 예약 업로드 필요" --push
0 7 * * *    cd ~/agent-hq && git pull -q && claude -p "blog 에이전트로 오늘 원고 1편 만들어" && git add -A && git commit -qm "blog daily" && git push -q
0 10 * * 2,4,6 cd ~/agent-hq && git pull -q && claude -p "shorts 에이전트로 쇼츠 대본 2편 만들어" && git add -A && git commit -qm "shorts" && git push -q
0 21 * * *   cd ~/agent-hq && git pull -q && claude -p "chief 에이전트로 오늘 일일 보고 작성" && git add -A && git commit -qm "daily report" && git push -q
0 20 * * 0   cd ~/agent-hq && git pull -q && claude -p "analyst 에이전트로 주간 리포트 작성" && git add -A && git commit -qm "weekly" && git push -q
```
서버 시간대 확인: `timedatectl` → 아니면 `sudo timedatectl set-timezone Asia/Seoul`

## 4. 캐릭터 상태
| 상태 | 화면 |
|---|---|
| working | 타이핑 모션 + 초록 모니터 |
| waiting | 폴짝폴짝 + 노란 배지 (사장 승인 필요) |
| done | 파란 모니터 |
| error | 덜덜 떨림 + 빨간 모니터 |
| idle | z z |

## 5. 다음 단계
- [ ] 카드뉴스 기존 Cowork 파이프라인 → `divisions/cardnews/render.py` 이관
- [ ] 쇼츠 2주치 성과를 `metrics/shorts.csv`에 입력
- [ ] 블로그 주제 정해서 `divisions/blog/playbook.md`에 기록
- [ ] Phase 2: 🐻 stock 활성화 (08:30 / 16:00 텔레그램)
