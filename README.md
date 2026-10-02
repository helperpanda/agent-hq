# 🐼 Agent HQ

헬퍼판다 1인기업 에이전트 본부. Claude Code 서브에이전트 + GitHub Actions 자동 실행 + 픽셀 캐릭터 대시보드.

- 대시보드: https://helperpanda.github.io/agent-hq/
- 운영 규칙·구성·스케줄: [`CLAUDE.md`](CLAUDE.md)
- 에이전트: 🐼 chief(일일 보고·회고) · 🐰 blog(트렌드 정보성 블로그 원고+이미지) · 🦉 analyst(쇼츠 성과 분석)
- 결과물/성과 데이터는 비공개 레포 `agent-hq-data`에 저장

## 필요한 Secrets (레포 Settings → Secrets and variables → Actions)
| 이름 | 용도 |
|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` | 에이전트 실행 (`claude setup-token`으로 발급) |
| `DATA_REPO_PAT` | 비공개 데이터 레포 읽기/쓰기 (fine-grained, 해당 레포 Contents RW) |
| `PEXELS_API_KEY` | 블로그 사진 검색 (무료, pexels.com/api) |

## 수동 실행
Actions 탭 → agents → Run workflow → `chief | analyst | daily | blog | improver` 선택.
