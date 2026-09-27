#!/usr/bin/env python3
"""성경 이야기 교재 512편 → 교재 전용 정적 사이트(bible-sim) 빌드"""
import re, json, glob, os, shutil

SRC = "/home/claude/src"
OUT = "/home/claude/bible-sim"

BOOKS = ["창세기","출애굽기","레위기","민수기","신명기","여호수아","사사기","룻기","사무엘상","사무엘하",
 "열왕기상","열왕기하","역대상","역대하","에스라","느헤미야","에스더","욥기","시편","잠언","전도서","아가",
 "이사야","예레미야","예레미야애가","에스겔","다니엘","호세아","요엘","아모스","오바댜","요나","미가","나훔",
 "하박국","스바냐","학개","스가랴","말라기",
 "마태복음","마가복음","누가복음","요한복음","사도행전","로마서","고린도전서","고린도후서","갈라디아서",
 "에베소서","빌립보서","골로새서","데살로니가전서","데살로니가후서","디모데전서","디모데후서","디도서",
 "빌레몬서","히브리서","야고보서","베드로전서","베드로후서","요한일서","요한이서","요한삼서","유다서","요한계시록"]
AUD = {"C": "어린이", "Y": "청소년", "A": "성인"}
V2_FROM = 300  # #300부터 v2 시네마틱 스타일

master = open(f"{SRC}/성경_이야기_교재_마스터.html", encoding="utf-8").read()
data = json.loads(re.search(r'<script type="application/json" id="bible-data">(.*?)</script>', master, re.S).group(1))
byid = {d["id"]: d for d in data}

if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(f"{OUT}/s")

catalog = []
for f in sorted(glob.glob(f"{SRC}/[0-9][0-9][0-9]_*.html")):
    base = os.path.basename(f)
    n = int(base[:3])
    d = byid[n]
    shutil.copyfile(f, f"{OUT}/s/{n:03d}.html")
    catalog.append({
        "no": n,
        "title": d["ti"],
        "testament": d["t"],
        "book": d["b"],
        "book_order": BOOKS.index(d["b"]) + 1,
        "ref": d["r"],
        "characters": [c.strip() for c in d["c"].split(",") if c.strip()],
        "summary": d["s"],
        "meaning": d["m"],
        "themes": [t.strip() for t in d["th"].split(",") if t.strip()],
        "question": d["q"],
        "audience": [AUD[a] for a in d["a"] if a in AUD],
        "style": "v2" if n >= V2_FROM else "v1",
        "path": f"/s/{n:03d}.html",
        "source_file": base,
        "bytes": os.path.getsize(f),
    })

assert len(catalog) == 512, len(catalog)
json.dump({"version": 1, "count": len(catalog), "books": BOOKS, "items": catalog},
          open(f"{OUT}/catalog.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 페이지 템플릿에 목록 데이터 인라인 (첫 화면 빠르게)
slim = [{k: c[k] for k in ("no","title","testament","book","book_order","ref","summary","themes","audience","style")} for c in catalog]
for page in ("index.html", "view.html"):
    tpl = open(f"/home/claude/tpl_{page}", encoding="utf-8").read()
    tpl = tpl.replace("/*__CATALOG__*/[]", json.dumps(slim, ensure_ascii=False))
    open(f"{OUT}/{page}", "w", encoding="utf-8").write(tpl)

json.dump({
    "cleanUrls": True,
    "headers": [
        {"source": "/s/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=3600, stale-while-revalidate=86400"}]},
        {"source": "/(.*)", "headers": [
            {"key": "Content-Security-Policy", "value": "frame-ancestors *"},
            {"key": "Access-Control-Allow-Origin", "value": "*"}]}
    ],
    "redirects": [{"source": "/:n(\\d{1,3})", "destination": "/view?n=:n", "permanent": False}]
}, open(f"{OUT}/vercel.json", "w"), indent=2)

# 이음허브 Supabase 시드 SQL
def q(s): return "'" + s.replace("'", "''") + "'"
def arr(a): return "ARRAY[" + ",".join(q(x) for x in a) + "]::text[]" if a else "'{}'::text[]"
rows = [f"({c['no']},{q(c['title'])},{q(c['testament'])},{q(c['book'])},{c['book_order']},{q(c['ref'])},"
        f"{arr(c['characters'])},{q(c['summary'])},{q(c['meaning'])},{arr(c['themes'])},{q(c['question'])},"
        f"{arr(c['audience'])},{q(c['style'])},{q(c['path'])})" for c in catalog]
sql = ("-- 성경 이야기 교재 512편 목록 시드 (catalog.json에서 자동 생성)\n"
       "insert into edu.bible_simulations (no,title,testament,book,book_order,ref,characters,summary,meaning,themes,question,audience,style,path)\nvalues\n"
       + ",\n".join(rows) +
       "\non conflict (no) do update set title=excluded.title, testament=excluded.testament, book=excluded.book,"
       " book_order=excluded.book_order, ref=excluded.ref, characters=excluded.characters, summary=excluded.summary,"
       " meaning=excluded.meaning, themes=excluded.themes, question=excluded.question, audience=excluded.audience,"
       " style=excluded.style, path=excluded.path, updated_at=now();\n")
os.makedirs(f"{OUT}/hub", exist_ok=True)
open(f"{OUT}/hub/seed_bible_simulations.sql", "w", encoding="utf-8").write(sql)
print("ok", len(catalog), "v2:", sum(c["style"] == "v2" for c in catalog))
