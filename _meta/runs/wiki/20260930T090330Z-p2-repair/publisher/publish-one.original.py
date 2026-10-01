import sys, json, re, hashlib, os, fcntl
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(".").resolve()
RUN = ROOT / "_meta/runs/wiki/20260929T083140Z-p2-resume"
VID = sys.argv[1]
now = datetime.now(timezone.utc)
today = now.strftime("%Y-%m-%d")
kst = now + timedelta(hours=9)
kst_min = kst.strftime("%H:%M")
assert not ("23:55" <= kst_min or kst_min <= "01:35"), f"no-publish window KST {kst_min}"

res = json.loads((RUN / VID / "attempt-result.json").read_text())
ver = json.loads((RUN / VID / "verify-report.json").read_text())
assert res.get("completed") and ver.get("passed"), f"attempt/verify not passed for {VID}"

doc = json.loads(re.search(r"\{.*\}", res["text"], re.S).group(0))
meta = json.loads((ROOT / f"raw/articles/4cff5b4f10ec/arxiv-{VID}/source.json").read_text())

def y(s):
    return " ".join(str(s).split()).replace('"', "'")
title = doc["title"]
abstract_line = (meta.get("abstract") or "").strip().split(". ")[0]
summary = y((abstract_line or title)[:160])
body = doc["markdown_body"].rstrip() + "\n"
read_scope = doc.get("read_scope") or []
unread_scope = doc.get("unread_scope") or []
tx = f"20260929T083140Z-p2-resume-{VID}"

page = (
    "---\n"
    f"title: \"{y(title)}\"\n"
    f"summary: \"{summary}\"\n"
    f"created: {today}\nupdated: {today}\nlast_reviewed: null\n"
    "type: entity\nstatus: draft\n"
    "tags: [paper, arxiv, ai-agent-security]\n"
    f"sources: [raw/articles/4cff5b4f10ec/arxiv-{VID}/source.html]\n"
    "confidence: medium\ncontested: false\ncontradictions: []\n"
    "schema: pkm-knowledge-page/v1\nrevision: 1\n"
    f"transaction_id: {tx}\n"
    "policy_revision: pkm-html-knowledge/v2\nprompt_revision: wiki-compile/v2\n"
    f"generation_ref: _meta/runs/wiki/20260929T083140Z-p2-resume/{VID}/attempt-result.json\n"
    f"read_scope: {json.dumps(read_scope, ensure_ascii=False)}\n"
    f"unread_scope: {json.dumps(unread_scope, ensure_ascii=False)}\n"
    "review_state: unreviewed\n---\n\n" + body
)

dest = ROOT / "entities" / f"arxiv-{VID}.md"
if dest.exists():
    raise SystemExit(f"refuse: existing page {dest}")

# --- publish under collection.lock with write-ahead journal ---
lock_path = ROOT / "_meta/locks/collection.lock"
lock_path.parent.mkdir(parents=True, exist_ok=True)
lock_fh = open(lock_path, "a+")
try:
    fcntl.flock(lock_fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    raise SystemExit("skipped_busy: collection.lock held")
try:
    # re-verify gates inside lock
    auto = json.loads((ROOT / "_meta/automation.json").read_text())
    assert auto["phase_authorizations"]["P2"] is True
    assert auto["policy_revision"] == "pkm-html-knowledge/v2"
    assert hashlib.sha256((ROOT / f"raw/articles/4cff5b4f10ec/arxiv-{VID}/source.html").read_bytes()).hexdigest() == res["source_sha256"]

    journal = RUN / VID / "publish-journal.json"
    journal.write_text(json.dumps({"tx": tx, "vid": VID, "intended": [str(dest.relative_to(ROOT)), "index.md", "log.md", "_meta/state/compilation.json"], "at": now.isoformat()}, ensure_ascii=False, indent=2) + "\n")

    tmp = dest.with_name(dest.name + ".tmp")
    tmp.write_text(page)
    tmp.replace(dest)

    # index update
    idx_path = ROOT / "index.md"
    idx = idx_path.read_text()
    entry = f"- [[entities/arxiv-{VID}]] — {y(title)} (draft, P2 파일럿 자동 컴파일)"
    assert "arxiv-" + VID not in idx
    idx = idx.replace("## Entities — 논문별 요약·분석·모델·도구\n\n아직 작성된 페이지가 없다.\n",
                      f"## Entities — 논문별 요약·분석·모델·도구\n\n{entry}\n", 1)
    total = int(re.search(r"Total pages: (\d+)", idx).group(1)) + 1
    idx = re.sub(r"Last updated: \d{4}-\d{2}-\d{2} \| Total pages: \d+", f"Last updated: {today} | Total pages: {total}", idx)
    tmp = idx_path.with_name("index.md.tmp")
    tmp.write_text(idx); tmp.replace(idx_path)

    # append-only log
    log_entry = (
        f"\n## [{today}] create | P2 파일럿 자동 컴파일 — arXiv {VID}\n\n"
        f"- 실행 `20260929T083140Z-p2-resume`, policy `pkm-html-knowledge/v2`, prompt `wiki-compile/v2`, 모델 `codex-lb/gpt-6-astra/xhigh`(사용자 비용 상한 제거·재개 승인 근거: `_meta/runs/wiki/20260929T083140Z-p2-resume/approval.json`). 이전 실행 `20260929T064035Z-p2-cost-waiver`의 로컬 시간초과 2회와 구별한다.\n"
        f"- 논문: {y(title)}. 원본 `raw/articles/4cff5b4f10ec/arxiv-{VID}/source.html`(SHA-256 `{res['source_sha256'][:16]}…`, {res.get('usage',{}).get('input_tokens','?')} 입력 토큰 관측)을 모델 컨텍스트로 직접 읽었다. 앵커 존재·인용 문자열 원문 대조 등 자동 검증 {sum(1 for c in ver['checks'] if c['ok'])}/{len(ver['checks'])} 통과.\n"
        f"- `entities/arxiv-{VID}.md` draft(status=draft, review_state=unreviewed) 게시. main_text_complete={doc.get('main_text_complete')}, 주장 {len(doc.get('claims') or [])}건, 비용 관측 없음(null, 0 아님). 도표·수식·부록 미검토 항목은 문서에 명시. 인간 검토 전이며 원문 확보와 별개로 의미 정확성을 보증하지 않는다.\n"
    )
    with open(ROOT / "log.md", "a") as f:
        f.write(log_entry)

    # compilation state update
    st_path = ROOT / "_meta/state/compilation.json"
    st = json.loads(st_path.read_text())
    item = next(i for i in st["items"] if i["version_id"] == VID)
    item.update({"status": "committed", "reason": None, "requested_scope": "P2 manual pilot",
                 "read_scope": read_scope, "unread_scope": unread_scope,
                 "work_key": tx, "output_refs": [f"entities/arxiv-{VID}.md"],
                 "receipt_ref": f"_meta/runs/wiki/20260929T083140Z-p2-resume/{VID}/publish-record.json",
                 "human_review": None})
    st["policy_revision"] = "pkm-html-knowledge/v2"
    st["contract_revision"] = "pkm-contracts/v2"
    st["cost_events"].append({"event_id": tx, "run_id": "20260929T083140Z-p2-resume", "role": "pilot",
                              "scope_id": VID, "created_at": now.isoformat(),
                              "kst_day": kst.strftime("%Y-%m-%d"), "status": "unknown",
                              "reserved_usd": None, "charged_usd": None,
                              "usage_receipt": f"_meta/runs/wiki/20260929T083140Z-p2-resume/{VID}/attempt-result.json"})
    st["last_run"] = "20260929T083140Z-p2-resume"
    tmp = st_path.with_name("compilation.json.tmp")
    tmp.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n"); tmp.replace(st_path)

    # durability
    for p in [dest, idx_path, ROOT / "log.md", st_path]:
        fh = os.open(p, os.O_RDONLY); os.fsync(fh); os.close(fh)

    # readback verification
    rb = dest.read_text()
    got = hashlib.sha256(dest.read_bytes()).hexdigest()
    idx2 = idx_path.read_text()
    record = {"vid": VID, "published_path": str(dest.relative_to(ROOT)), "sha256": got,
              "bytes": dest.stat().st_size, "title": title,
              "index_entry_present": f"entities/arxiv-{VID}" in idx2,
              "index_total_pages": total, "log_appended": log_entry[:60] in (ROOT / "log.md").read_text(),
              "state_status": next(i["status"] for i in json.loads(st_path.read_text())["items"] if i["version_id"] == VID),
              "frontmatter_ok": rb.startswith("---\n") and "transaction_id: " + tx in rb,
              "published_at": now.isoformat(), "cost_usd": None, "cost_status": "unobserved_not_zero"}
    assert record["index_entry_present"] and record["log_appended"] and record["state_status"] == "committed" and record["frontmatter_ok"]
    (RUN / VID / "publish-record.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(record, ensure_ascii=False))
finally:
    fcntl.flock(lock_fh, fcntl.LOCK_UN)
    lock_fh.close()
