# SCHEMA — 이음:교재

> 스키마 이름은 `edu`로 가정했다. 이음허브의 스키마 분리 규칙에 맞게 바꿔도 된다(시드 SQL도 함께 바꿀 것).
> **모든 표에 RLS를 반드시 켠다** (과거 RLS 없이 배포한 사고 재발 방지).

## 1단계 (MVP)

```sql
create schema if not exists edu;

create table edu.bible_simulations (
  no          int primary key check (no between 1 and 9999),
  title       text not null,
  testament   text not null check (testament in ('구약','신약')),
  book        text not null,            -- 성경책 이름 (예: 사무엘상)
  book_order  int  not null,            -- 1(창세기)~66(요한계시록)
  ref         text not null,            -- 참조 구절 (예: 삼상 17:1-58)
  characters  text[] not null default '{}',
  summary     text not null,
  meaning     text not null,
  themes      text[] not null default '{}',
  question    text not null,            -- 나눔 질문
  audience    text[] not null default '{}',  -- 어린이/청소년/성인
  style       text not null default 'v1' check (style in ('v1','v2')),
  path        text not null,            -- bible-sim 사이트 안 경로 (/s/094.html)
  is_published boolean not null default true,
  updated_at  timestamptz not null default now()
);
create index on edu.bible_simulations (book_order, no);
create index on edu.bible_simulations using gin (themes);

alter table edu.bible_simulations enable row level security;

-- 로그인한 사용자는 공개된 교재 목록을 읽을 수 있다
create policy "bible_sim_read" on edu.bible_simulations
  for select to authenticated using (is_published);

-- 쓰기는 관리자만 (허브의 기존 관리자 판별 함수로 교체할 것)
create policy "bible_sim_admin_write" on edu.bible_simulations
  for all to authenticated
  using (public.is_admin(auth.uid())) with check (public.is_admin(auth.uid()));
```

데이터 넣기: `hub/seed_bible_simulations.sql` 실행 (512행, 다시 실행해도 안전한 upsert).

## 2단계

```sql
-- 반(순/부서)별 교재 배정
create table edu.bible_sim_assignments (
  id          uuid primary key default gen_random_uuid(),
  group_id    uuid not null,            -- 허브의 반/부서 표 id로 FK 연결
  no          int  not null references edu.bible_simulations(no),
  week_of     date not null,            -- 해당 주 주일 날짜
  note        text,
  assigned_by uuid not null default auth.uid(),
  created_at  timestamptz not null default now(),
  unique (group_id, no, week_of)
);
alter table edu.bible_sim_assignments enable row level security;
-- 읽기: 해당 반 소속 / 쓰기: 해당 반 교사 (허브 권한 함수로 작성)

-- 학습 기록
create table edu.bible_sim_progress (
  user_id     uuid not null default auth.uid(),
  no          int  not null references edu.bible_simulations(no),
  first_opened_at timestamptz not null default now(),
  last_opened_at  timestamptz not null default now(),
  open_count  int not null default 1,
  primary key (user_id, no)
);
alter table edu.bible_sim_progress enable row level security;
create policy "own_progress" on edu.bible_sim_progress
  for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
-- 교사 조회 정책은 반 소속 관계로 별도 작성
```

## 원본 데이터 출처
- `catalog.json` (bible-sim 사이트 루트): 512편 전체 필드
- 필드 대응: catalog `no,title,testament,book,book_order,ref,characters,summary,meaning,themes,question,audience,style,path` → 표 컬럼 동일
