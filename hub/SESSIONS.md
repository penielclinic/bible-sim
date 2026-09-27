# SESSIONS — 이음:교재 개발 순서

각 세션은 Claude Code에 그대로 붙여 넣어 진행한다. 세션이 끝날 때마다 화면으로 직접 확인한 뒤 다음으로 넘어간다.

## 세션 1 — DB 준비
- `SCHEMA.md`의 1단계 SQL로 `edu.bible_simulations` 표를 만들고 RLS를 켠다.
- 관리자 판별 함수는 허브의 기존 함수로 바꾼다.
- `seed_bible_simulations.sql`을 실행한다.
- ✅ 확인: `select count(*) from edu.bible_simulations;` → 512 / 로그인 안 한 상태로 조회하면 0행

## 세션 2 — 목록 화면 `/edu/bible`
- 서버 컴포넌트에서 512행을 한 번에 조회한다 (no, title, testament, book, book_order, ref, summary, themes, audience).
- 클라이언트에서 검색·구약/신약·성경책·주제·대상 필터와 정렬(번호 / 성경 순서)을 처리한다.
- shadcn/ui Card·Input·Select·ToggleGroup을 쓴다.
- ✅ 확인: "94" 검색 → 다윗과 골리앗 / 신약+요나 → 0편 / 휴대폰 폭 확인

## 세션 3 — 교재 보기 `/edu/bible/[no]`
- 상단 막대: 목록으로, 이전, 번호·제목·참조 구절, 다음
- 본문: iframe (CLAUDE.md 참고)
- 아래 접이식 패널: 요약 · 의미 · 나눔 질문
- ✅ 확인: 1번에서 이전 버튼 비활성, 512번에서 다음 버튼 비활성, 교재 안의 애니메이션·버튼 정상 작동

## 세션 4 — 메뉴 연결
- 이음허브 내비게이션에 "성경 이야기 교재" 추가 (교육 영역)
- `NEXT_PUBLIC_BIBLE_SIM_URL`을 Vercel 환경변수에 등록한다.
- ✅ 확인: 운영 배포에서 목록 → 교재 열기

## 세션 5 (2단계) — 수업 배정
- `edu.bible_sim_assignments` 표와 RLS
- 교사 화면: 반 선택 → 주일 날짜 → 교재 검색해서 배정
- 학생 홈: "이번 주 교재" 카드
- ✅ 확인: 교사 A가 배정한 교재가 다른 반 학생에게 보이지 않음

## 세션 6 (2단계) — 학습 기록
- 교재 보기 화면이 열릴 때 `edu.bible_sim_progress`를 upsert한다 (open_count + 1).
- 교사 화면: 반별 학생 × 배정 교재 진행표
- ✅ 확인: 본인 기록만 읽히는지 다른 계정으로 확인

## 운영 메모
- 교재를 리메이크하면: bible-sim 저장소의 `s/NNN.html`을 교체하고 push한다. 그다음 관리자 화면에서 해당 번호의 style을 v2로 바꾼다.
- 새 교재를 추가하면(513번 이후): bible-sim에 파일과 catalog.json을 추가하고, 시드 SQL을 다시 만들어 실행한다.
