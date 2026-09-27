# CLAUDE.md — 이음:교재 모듈 작업 규칙

## 스택
Next.js 14 (App Router) · Supabase · Vercel · Tailwind CSS · shadcn/ui — 이음허브 기존 규칙을 그대로 따른다.

## 핵심 원칙
1. **교재 HTML은 허브 저장소에 넣지 않는다.** 교재는 bible-sim 사이트에만 있고, 허브는 iframe으로 불러온다.
2. 교재 주소는 환경변수 하나로 관리한다: `NEXT_PUBLIC_BIBLE_SIM_URL=https://<bible-sim 배포 주소>` (공개값이라 NEXT_PUBLIC 사용 가능. API 키는 절대 NEXT_PUBLIC 금지)
3. 교재 URL 규칙: `${BIBLE_SIM_URL}/s/${String(no).padStart(3,"0")}`
4. **새 표는 만들자마자 RLS를 켜고 정책을 쓴다.** 정책 없는 표는 배포 금지.
5. 목록 데이터는 Supabase `edu.bible_simulations`에서 읽는다. catalog.json을 런타임에 직접 fetch하지 않는다 (시드 원본 용도).

## iframe 사용법
```tsx
<iframe
  src={`${process.env.NEXT_PUBLIC_BIBLE_SIM_URL}/s/${pad(no)}`}
  title={`${no}. ${title}`}
  allow="fullscreen; autoplay"
  className="w-full h-[calc(100dvh-56px)] border-0"
/>
```
- bible-sim은 `frame-ancestors *` 헤더라 어느 도메인에서도 iframe으로 열린다.
- 대안: 이전/다음 버튼까지 포함된 `${URL}/view?n=94&embed=1` 를 통째로 iframe에 넣어도 된다. 교재가 바뀔 때마다 `postMessage({type:'bible-sim:open', no, title})`를 보내므로 학습 기록에 쓸 수 있다.

## 화면 규칙
- 모바일 우선. 360px 폭에서 가로 스크롤 금지
- 글꼴: 제목 Gowun Batang, 본문 Noto Sans KR (교재와 통일)
- 구약 색 주황갈색 계열, 신약 색 파랑 계열
- 목록 512행은 한 번에 받아와서 클라이언트에서 필터링한다 (행이 작아서 페이지네이션 불필요)

## 하지 말 것
- 교재 HTML 수정, 복사, 허브 public 폴더에 넣기
- Supabase Storage에 교재 HTML 업로드
- RLS 없이 표 생성
