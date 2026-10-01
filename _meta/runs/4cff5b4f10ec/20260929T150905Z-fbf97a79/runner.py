#!/usr/bin/env python3
"""Scheduled collection run — arxiv-html-preferred-pdf-fallback/v1, Cron 4cff5b4f10ec.

Performs: preflight, atomic mkdir lock, exact-query search (lastUpdatedDate desc,
client-side Atom updated filter), daily-attempt budget, HTML-first download with
confirmed-unavailability PDF fallback, atomic publication, state update, report.
"""
import json, os, sys, time, uuid, hashlib, re, shutil
import urllib.request, urllib.error, urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

ROOT = "/home/ainsdev/wiki/pkm-articles"
CRON_ID = "4cff5b4f10ec"
RUN_TAG = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
RUN_ID = f"{RUN_TAG}-{uuid.uuid4().hex[:8]}"
RUN_DIR = os.path.join(ROOT, "_meta", "runs", CRON_ID, RUN_ID)
STAGING_ROOT = os.path.join(ROOT, "_meta", "staging", CRON_ID, RUN_ID)
LOCK = os.path.join(ROOT, "_meta", "locks", "collection.lock")
STATE_PATH = os.path.join(ROOT, "_meta", "state", f"{CRON_ID}.json")

API = "https://export.arxiv.org/api/query"
UA = "Mozilla/5.0 (X11; Linux x86_64) personal-paper-wiki-collection"
NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
KST = timezone(timedelta(hours=9))

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def log(msg):
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}", flush=True)

def atomic_write_json(path, obj):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    tmp = path + ".tmp-" + uuid.uuid4().hex[:8]
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def http_get(url, timeout=60, accept=None, encoding_identity=True):
    headers = {"User-Agent": UA, "Accept": accept or "*/*"}
    if encoding_identity:
        headers["Accept-Encoding"] = "identity"
    req = urllib.request.Request(url, headers=headers)
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            return {
                "url": url, "final_url": r.geturl(), "status": r.status,
                "headers": {k.lower(): v for k, v in r.headers.items()},
                "body": body, "elapsed_s": round(time.time() - start, 3),
                "error": None,
            }
    except urllib.error.HTTPError as e:
        try:
            body = e.read()
        except Exception:
            body = b""
        return {
            "url": url, "final_url": getattr(e, "url", url), "status": e.code,
            "headers": {k.lower(): v for k, v in e.headers.items()} if e.headers else {},
            "body": body, "elapsed_s": round(time.time() - start, 3),
            "error": f"HTTP {e.code}",
        }
    except Exception as e:
        return {
            "url": url, "final_url": url, "status": None, "headers": {},
            "body": b"", "elapsed_s": round(time.time() - start, 3),
            "error": f"{type(e).__name__}: {e}",
        }

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

# ---------- preflight ----------
topics = load_json(os.path.join(ROOT, "_meta", "topics.json"))
topic = next(t for t in topics["topics"] if t["cron_id"] == CRON_ID)
state = load_json(STATE_PATH)
state_pipeline = state.get("pipeline_id")
policy_ok = (
    topic["pipeline"]["id"] == "arxiv-html-preferred-pdf-fallback/v1"
    and state_pipeline == "arxiv-html-preferred-pdf-fallback/v1"
    and topic["pipeline"].get("preprocessing_enabled") is False
    and topics.get("compile_wiki") is False
    and state.get("safety_block") is False
)
os.makedirs(RUN_DIR, exist_ok=True)
run = {
    "schema": "arxiv-html-collection-run/v1",
    "run_id": RUN_ID, "cron_id": CRON_ID,
    "type": "scheduled_html_pdf_original_collection",
    "pipeline_id": "arxiv-html-preferred-pdf-fallback/v1",
    "started_at": now_iso(),
    "kst_date": datetime.now(KST).strftime("%Y-%m-%d"),
}
preflight = {
    "checked_at": now_iso(),
    "topics_pipeline_id": topic["pipeline"]["id"],
    "state_pipeline_id": state_pipeline,
    "compile_wiki": topics.get("compile_wiki"),
    "preprocessing_enabled": topic["pipeline"].get("preprocessing_enabled"),
    "safety_block": state.get("safety_block"),
    "policy_match": policy_ok,
    "pending_count": len(state.get("pending", [])),
    "daily_attempts": state.get("daily_attempts", {}),
}
atomic_write_json(os.path.join(RUN_DIR, "preflight.json"), preflight)
if not policy_ok:
    run.update({"status": "aborted_policy_mismatch", "finished_at": now_iso()})
    atomic_write_json(os.path.join(RUN_DIR, "report.json"), run)
    print("[CRON_FAILURE] policy mismatch or safety_block — aborted")
    sys.exit(2)

# ---------- lock ----------
if os.path.exists(LOCK):
    try:
        owner = load_json(os.path.join(LOCK, "owner.json"))
    except Exception:
        owner = {"error": "unreadable owner"}
    run.update({"status": "skipped_busy", "finished_at": now_iso(), "lock_owner": owner})
    atomic_write_json(os.path.join(RUN_DIR, "report.json"), run)
    print("[SILENT-skip] collection lock busy — run recorded as skipped_busy")
    sys.exit(0)
os.makedirs(LOCK, exist_ok=False)
atomic_write_json(os.path.join(LOCK, "owner.json"), {
    "run_id": RUN_ID, "cron_id": CRON_ID, "type": "scheduled_collection",
    "acquired_at_utc": now_iso(), "pid": os.getpid(), "host": os.uname().nodename,
})

counts = {
    "search_pages": 0, "search_records_validated": 0, "candidates_in_window": 0,
    "new_html_saved": 0, "new_pdf_saved": 0, "duplicates_processed": 0,
    "new_html_unavailable": 0, "both_formats_unavailable": 0,
    "source_failures": 0, "unrecovered_core_failures": 0,
    "recovered_api_transport_failures": 0,
    "existing_sources_verified": 0, "html_unavailable_retry_not_due": 0,
    "new_daily_attempts": 0, "daily_attempts_today": 0,
}
failed_core = False
exit_code = 0
status = "completed_zero_results"

try:
    run_start = datetime.now(timezone.utc)
    window_upper = run_start
    floor = datetime.fromisoformat(state["first_window_floor"])
    prev_cp = datetime.fromisoformat(state["discovered_through"])
    window_lower = max(floor, prev_cp - timedelta(hours=topic["overlap_hours"]))
    log(f"window [{window_lower.isoformat()} .. {window_upper.isoformat()}]")

    # ---------- existing-source inventory ----------
    raw_root = os.path.join(ROOT, "raw", "articles", CRON_ID)
    existing = {}
    for d in sorted(os.listdir(raw_root)):
        p = os.path.join(raw_root, d)
        if not os.path.isdir(p) or not d.startswith("arxiv-"):
            continue
        sj = os.path.join(p, "source.json")
        if os.path.exists(sj):
            meta = load_json(sj)
            vid = meta.get("version_id")
            fmt = "pdf" if meta.get("schema") == "arxiv-pdf-source/v1" else "html"
            ent = {
                "dir": d, "format": fmt, "source_json": meta,
                "file": os.path.join(p, "source.html" if fmt == "html" else "source.pdf"),
            }
            ent["file_ok"] = os.path.isfile(ent["file"])
            if ent["file_ok"]:
                ent["sha256"] = sha256_file(ent["file"])
                ent["bytes"] = os.path.getsize(ent["file"])
                exp = meta.get("html_sha256") if fmt == "html" else meta.get("pdf_sha256")
                expb = meta.get("html_bytes") if fmt == "html" else meta.get("pdf_bytes")
                ent["hash_ok"] = (ent["sha256"] == exp) and (ent["bytes"] == expb)
            else:
                ent["hash_ok"] = False
            existing[vid] = ent
    inv_ok = all(e["file_ok"] and e["hash_ok"] for e in existing.values())
    log(f"inventory: {len(existing)} existing sources, all verified: {inv_ok}")
    counts["existing_sources_verified"] = len(existing)

    # ---------- search ----------
    api_q = topic["api_query"]
    search_pages = []
    records_all = []
    stop = False
    page = 0
    while not stop and page < topic["max_search_pages_per_run"]:
        url = (f"{API}?search_query={urllib.parse.quote(api_q)}"
               f"&sortBy=lastUpdatedDate&sortOrder=descending&start={page*100}&max_results=100")
        resp = http_get(url, timeout=90)
        rec = {"page": page, "url": url, "http_status": resp["status"],
               "error": resp["error"], "bytes": len(resp["body"])}
        counts["search_pages"] += 1
        if resp["error"] or resp["status"] != 200:
            rec["outcome"] = "http_failure"
            search_pages.append(rec)
            failed_core = True
            break
        try:
            root = ET.fromstring(resp["body"])
        except ET.ParseError as e:
            rec["outcome"] = f"xml_parse_error: {e}"
            search_pages.append(rec)
            failed_core = True
            break
        with open(os.path.join(RUN_DIR, f"search-page-{page:03d}.xml"), "wb") as f:
            f.write(resp["body"])
        entries = root.findall("a:entry", NS)
        rec["entries"] = len(entries)
        page_records = []
        for en in entries:
            rid = en.find("a:id", NS).text.strip().split("/abs/")[-1]
            upd = en.find("a:updated", NS).text.strip()
            pub = en.find("a:published", NS).text.strip()
            title = " ".join(en.find("a:title", NS).text.split())
            summ = " ".join(en.find("a:summary", NS).text.split())
            authors = [a.find("a:name", NS).text for a in en.findall("a:author", NS)]
            cats = [c.get("term") for c in en.findall("a:category", NS)]
            page_records.append({
                "version_id": rid, "updated": upd, "published": pub,
                "title": title, "authors": authors, "categories": cats,
                "abstract": summ,
            })
        records_all.extend(page_records)
        counts["search_records_validated"] += len(page_records)
        rec["records"] = page_records
        search_pages.append(rec)
        # validate: distinct ids, descending updated
        upd_list = [r["updated"] for r in page_records]
        descending = all(upd_list[i] >= upd_list[i+1] for i in range(len(upd_list)-1))
        rec["descending_ok"] = descending
        if not descending:
            rec["outcome"] = "ordering_violation"
            failed_core = True
            break
        oldest = upd_list[-1] if upd_list else None
        if len(entries) < 100 or (oldest and oldest < window_lower.isoformat()):
            stop = True
            rec["stop_reason"] = "window_lower_crossed" if (oldest and oldest < window_lower.isoformat()) else "exhausted"
        page += 1
        if not stop:
            time.sleep(topic["api_min_interval_seconds"])

    transport = {"direct_api_http_status": search_pages[0]["http_status"] if search_pages else None}
    search_complete = (not failed_core) and stop in (True,) and bool(search_pages) and all(
        p.get("http_status") == 200 for p in search_pages)
    # tolerate: exhausted naturally (len<100) or crossed floor
    if failed_core:
        status = "failed_search"
    else:
        # candidates in window: updated within (window_lower, window_upper]
        cands = []
        seen = set()
        for r in records_all:
            if r["version_id"] in seen:
                continue
            seen.add(r["version_id"])
            u = datetime.fromisoformat(r["updated"].replace("Z", "+00:00"))
            if window_lower < u <= window_upper:
                cands.append(r)
        counts["candidates_in_window"] = len(cands)
        log(f"search complete: {counts['search_records_validated']} records, "
            f"{len(cands)} candidates in window")
        atomic_write_json(os.path.join(RUN_DIR, "candidates.json"), {
            "window_lower": window_lower.isoformat(), "window_upper": window_upper.isoformat(),
            "candidates": cands,
        })
        # dedup against existing targets
        new_cands = [c for c in cands if c["version_id"] not in existing]
        dup_ids = [c["version_id"] for c in cands if c["version_id"] in existing]
        counts["duplicates_processed"] = len(dup_ids)

        # ---------- daily budget ----------
        kst_today = run["kst_date"]
        da = state.get("daily_attempts", {})
        today_list = list(da.get(kst_today, []))
        budget = topic["max_paper_attempts_per_kst_day"]
        available = [c for c in new_cands if c["version_id"] not in today_list]
        chosen = available[: max(0, budget - len(today_list))]
        reserved = [c["version_id"] for c in chosen]
        if reserved:
            state["daily_attempts"] = da
            state["daily_attempts"][kst_today] = today_list + reserved
            atomic_write_json(STATE_PATH, state)
            state = load_json(STATE_PATH)
            log(f"reserved daily attempts: {reserved}")

        # ---------- acquisition loop ----------
        attempts_evidence = []
        html_unavailable_new = []
        pending_new = []

        def base_of(v):
            m = re.match(r"^(.*)v\d+$", v)
            return m.group(1) if m else v

        def stage_publish(vid, fmt, body, meta_extra):
            enc = urllib.parse.quote(vid, safe=".")
            stage = os.path.join(STAGING_ROOT, f"arxiv-{enc}")
            os.makedirs(stage, exist_ok=True)
            fname = "source.html" if fmt == "html" else "source.pdf"
            fpath = os.path.join(stage, fname)
            with open(fpath, "wb") as f:
                f.write(body)
                f.flush()
                os.fsync(f.fileno())
            digest = sha256_file(fpath)
            nbytes = os.path.getsize(fpath)
            meta_extra.update({
                "sha256": digest, "bytes": nbytes, "staged_at": now_iso(),
            })
            atomic_write_json(os.path.join(stage, "source.json"), meta_extra)
            dest = os.path.join(raw_root, f"arxiv-{enc}")
            if os.path.exists(dest):
                return {"ok": False, "reason": "destination_exists", "dest": dest}
            # atomic publication: rename dir
            os.rename(stage, dest)
            return {"ok": True, "dest": dest, "sha256": digest, "bytes": nbytes}

        for cand in chosen:
            vid = cand["version_id"]
            log(f"acquiring {vid}: {cand['title'][:60]}")
            att = {"version_id": vid, "title": cand["title"], "steps": []}
            html_url = f"https://arxiv.org/html/{vid}"
            r = http_get(html_url, timeout=90, accept="text/html,application/xhtml+xml")
            att["steps"].append({"step": "html_fetch", "status": r["status"],
                                 "final_url": r["final_url"],
                                 "content_type": r["headers"].get("content-type", ""),
                                 "bytes": len(r["body"]), "error": r["error"]})
            html_ok = False
            if r["status"] == 200 and "text/html" in r["headers"].get("content-type", "").lower():
                final_ok = r["final_url"].rstrip("/").endswith(vid) or f"/html/{vid}" in r["final_url"]
                body = r["body"]
                complete = b"</html>" in body[-20000:].lower() if body else False
                title_like = (b"<title>" in body[:10000]) or (b"L aTeX" in body) or (b"latex" in body[:20000].lower())
                cl = r["headers"].get("content-length")
                cl_ok = (cl is None) or (int(cl) == len(body))
                html_ok = final_ok and complete and title_like and cl_ok
                att["steps"][-1].update({"final_ok": final_ok, "complete": complete,
                                          "title_like": title_like, "cl_ok": cl_ok})
            if html_ok:
                meta = {
                    "schema": "arxiv-html-source/v1",
                    "source": "arxiv", "base_id": base_of(vid),
                    "version_id": vid, "title": cand["title"],
                    "authors": cand["authors"], "abstract": cand["abstract"],
                    "published": cand["published"], "updated": cand["updated"],
                    "categories": cand["categories"],
                    "owning_cron_id": CRON_ID,
                    "source_url": html_url, "abs_url": f"https://arxiv.org/abs/{vid}",
                    "collected_at": now_iso(),
                    "html_file": "source.html",
                    "http_status": r["status"], "final_url": r["final_url"],
                    "content_type": r["headers"].get("content-type"),
                    "charset": "utf-8",
                    "capture_method": "http_response_body_no_rewrite",
                    "pipeline_id": "arxiv-html-preferred-pdf-fallback/v1",
                    "preprocessing": False, "wiki_compiled": False,
                    "offline_assets_bundled": False,
                }
                pub = stage_publish(vid, "html", r["body"], meta)
                att["html_publish"] = {k: v for k, v in pub.items() if k != "dest"} | {"dest": pub.get("dest", "")}
                if pub["ok"]:
                    counts["new_html_saved"] += 1
                    att["outcome"] = "html_saved"
                    existing[vid] = {"format": "html", "dir": f"arxiv-{urllib.parse.quote(vid, safe='.')}", "file_ok": True, "hash_ok": True}
                else:
                    counts["source_failures"] += 1
                    failed_core = True
                    att["outcome"] = "publish_failed"
                attempts_evidence.append(att)
                continue
            # HTML not ok — is it confirmed unavailable (404) or transport error?
            if r["status"] == 404:
                # confirm via abs fulltext link
                abs_url = f"https://arxiv.org/abs/{vid}"
                ra = http_get(abs_url, timeout=60, accept="text/html")
                att["steps"].append({"step": "abs_confirm", "status": ra["status"],
                                     "final_url": ra["final_url"], "error": ra["error"]})
                no_html_link = (ra["status"] == 200) and (
                    f"/html/{vid}" not in ra["body"].decode("utf-8", "replace"))
                if not no_html_link:
                    # abs page has html link → transient html fetch failure? keep pending, no pdf
                    pending_new.append({"source": "arxiv", "base_id": base_of(vid),
                                        "version_id": vid, "title": cand["title"],
                                        "abs_url": abs_url, "source_url": html_url,
                                        "target_format": "html",
                                        "reason": "html_transport_failure_no_pdf_fallback",
                                        "queued_at": now_iso()})
                    counts["source_failures"] += 1
                    att["outcome"] = "html_transport_failure_pending"
                    attempts_evidence.append(att)
                    continue
                # confirmed unavailable → record evidence, then PDF fallback
                ev_entry = {
                    "source": "arxiv", "base_id": base_of(vid),
                    "version_id": vid, "title": cand["title"],
                    "source_url": html_url, "abs_url": abs_url,
                    "status": "html_unavailable", "http_status": 404,
                    "checked_at": now_iso(),
                    "next_retry_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
                    "evidence_run": RUN_ID,
                }
                pdf_url = f"https://arxiv.org/pdf/{vid}"
                rp = http_get(pdf_url, timeout=120, accept="application/pdf")
                att["steps"].append({"step": "pdf_fetch", "status": rp["status"],
                                     "final_url": rp["final_url"],
                                     "content_type": rp["headers"].get("content-type", ""),
                                     "bytes": len(rp["body"]), "error": rp["error"]})
                pdf_ok = False
                if rp["status"] == 200 and "application/pdf" in rp["headers"].get("content-type", "").lower():
                    fu = rp["final_url"]
                    fu_ok = (fu.rstrip("/") == f"https://arxiv.org/pdf/{vid}" or
                             fu.rstrip("/") == f"https://arxiv.org/pdf/{vid}.pdf" or
                             fu.rstrip("/").endswith(vid) or fu.rstrip("/").endswith(vid + ".pdf"))
                    body = rp["body"]
                    head_ok = body[:5] == b"%PDF-"
                    tail_ok = b"%%EOF" in body[-1024:]
                    cl = rp["headers"].get("content-length")
                    cl_ok = (cl is None) or (int(cl) == len(body))
                    pdf_ok = fu_ok and head_ok and tail_ok and cl_ok
                    att["steps"][-1].update({"final_url_ok": fu_ok, "head_ok": head_ok,
                                              "tail_eof_ok": tail_ok, "cl_ok": cl_ok})
                if pdf_ok:
                    meta = {
                        "schema": "arxiv-pdf-source/v1", "source_format": "pdf",
                        "source": "arxiv", "base_id": base_of(vid),
                        "version_id": vid, "title": cand["title"],
                        "authors": cand["authors"], "abstract": cand["abstract"],
                        "published": cand["published"], "updated": cand["updated"],
                        "categories": cand["categories"],
                        "owning_cron_id": CRON_ID,
                        "source_url": pdf_url, "abs_url": abs_url,
                        "collected_at": now_iso(),
                        "pdf_file": "source.pdf",
                        "http_status": rp["status"], "final_url": rp["final_url"],
                        "content_type": rp["headers"].get("content_type") or rp["headers"].get("content-type"),
                        "capture_method": "http_response_body_no_rewrite",
                        "content_scope": "pdf_fulltext_as_served",
                        "pipeline_id": "arxiv-html-preferred-pdf-fallback/v1",
                        "html_url": html_url,
                        "html_unavailable": {
                            "checked_at": now_iso(), "http_status": 404,
                            "evidence_run": RUN_ID,
                        },
                        "preprocessing": False, "wiki_compiled": False,
                        "offline_assets_bundled": False,
                    }
                    pub = stage_publish(vid, "pdf", rp["body"], meta)
                    if pub["ok"]:
                        counts["new_pdf_saved"] += 1
                        ev_entry["local_fulltext_preserved"] = True
                        ev_entry["pdf_fallback_status"] = "captured"
                        ev_entry["fallback_source_path"] = os.path.relpath(os.path.join(raw_root, f"arxiv-{urllib.parse.quote(vid, safe='.')}", "source.pdf"), ROOT)
                        ev_entry["pdf_captured_at"] = now_iso()
                        att["outcome"] = "pdf_saved"
                    else:
                        counts["source_failures"] += 1
                        failed_core = True
                        att["outcome"] = "publish_failed"
                else:
                    if rp["status"] == 404:
                        counts["both_formats_unavailable"] += 1
                        pending_new.append({
                            "source": "arxiv", "base_id": base_of(vid),
                            "version_id": vid, "title": cand["title"],
                            "abs_url": abs_url, "source_url": pdf_url,
                            "target_format": "pdf",
                            "reason": "both_formats_unavailable",
                            "queued_at": now_iso(),
                            "next_attempt_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
                            "html_unavailable_evidence_run": RUN_ID,
                        })
                        att["outcome"] = "both_formats_unavailable"
                    else:
                        counts["source_failures"] += 1
                        failed_core = True
                        att["outcome"] = "pdf_transport_failure"
                html_unavailable_new.append(ev_entry)
            else:
                # 403/429/5xx/timeout → pending, no PDF fallback
                pending_new.append({"source": "arxiv", "base_id": base_of(vid),
                                    "version_id": vid, "title": cand["title"],
                                    "abs_url": f"https://arxiv.org/abs/{vid}",
                                    "source_url": html_url, "target_format": "html",
                                    "reason": f"html_transport_failure_status_{r['status']}",
                                    "queued_at": now_iso()})
                counts["source_failures"] += 1
                failed_core = True
                att["outcome"] = "html_transport_failure_pending"
            attempts_evidence.append(att)

        atomic_write_json(os.path.join(RUN_DIR, "attempts.json"), attempts_evidence)

        # ---------- state update ----------
        state = load_json(STATE_PATH)  # reload to keep our daily_attempts write
        new_cp = window_upper
        state["discovered_through"] = new_cp.isoformat()
        state["last_complete_at"] = now_iso()
        # merge html_unavailable
        hu = state.get("html_unavailable", [])
        hu_ids = {h["version_id"] for h in hu}
        for e in html_unavailable_new:
            if e["version_id"] not in hu_ids:
                hu.append(e)
            else:
                for i, x in enumerate(hu):
                    if x["version_id"] == e["version_id"]:
                        hu[i] = e
        state["html_unavailable"] = hu
        # pending: keep old + new
        pend = state.get("pending", [])
        pend_ids = {p["version_id"] for p in pend}
        for p in pending_new:
            if p["version_id"] not in pend_ids:
                pend.append(p)
        state["pending"] = pend
        counts["daily_attempts_today"] = len(state["daily_attempts"].get(kst_today, []))
        counts["pending"] = len(state["pending"])

        if failed_core:
            status = "completed_with_failures" if (counts["new_html_saved"] + counts["new_pdf_saved"]) > 0 else "failed_core"
            state["consecutive_failed_runs"] = state.get("consecutive_failed_runs", 0) + 1
        else:
            state["consecutive_failed_runs"] = 0
        if state["consecutive_failed_runs"] >= 3:
            state["safety_block"] = True
            state["safety_block_reason"] = "3 consecutive core failures (search/download/integrity)"
        run["last_run"] = None
        state["last_run"] = {
            "run_id": RUN_ID, "type": "scheduled_html_pdf_original_collection",
            "started_at": run["started_at"], "finished_at": now_iso(),
            "status": status, "search_performed": True,
            "discovery_checkpoint_advanced": True,
            "counts": counts, "report_path": os.path.relpath(os.path.join(RUN_DIR, "report.json"), ROOT),
        }
        atomic_write_json(STATE_PATH, state)

    # ---------- final verification ----------
    raw_root = os.path.join(ROOT, "raw", "articles", CRON_ID)
    final_html = 0
    final_pdf = 0
    problems = []
    for d in sorted(os.listdir(raw_root)):
        p = os.path.join(raw_root, d)
        if os.path.isdir(p) and d.startswith("arxiv-"):
            has_h = os.path.isfile(os.path.join(p, "source.html"))
            has_p = os.path.isfile(os.path.join(p, "source.pdf"))
            has_j = os.path.isfile(os.path.join(p, "source.json"))
            if has_h and has_p:
                problems.append(f"{d}: both formats present")
            if not has_j:
                problems.append(f"{d}: missing source.json")
            if has_h:
                final_html += 1
            elif has_p:
                final_pdf += 1
    atomic_write_json(os.path.join(RUN_DIR, "verification.json"), {
        "checked_at": now_iso(),
        "html_files": final_html, "pdf_files": final_pdf,
        "source_json_files": final_html + final_pdf,
        "total_targets": final_html + final_pdf,
        "problems": problems,
        "all_inventory_verified_before_run": inv_ok,
    })
    run["counts"] = counts
    run["final_counts"] = {"html": final_html, "pdf": final_pdf, "total": final_html + final_pdf}
    run["status"] = status
    run["finished_at"] = now_iso()
    run["elapsed_seconds"] = (datetime.now(timezone.utc) - run_start).total_seconds()
    run["query"] = api_q
    run["window_lower"] = window_lower.isoformat()
    run["window_upper"] = window_upper.isoformat()
    run["transport"] = transport
    run["target_ids"] = sorted(existing.keys())
    atomic_write_json(os.path.join(RUN_DIR, "report.json"), run)
    log(f"done status={status} html+{counts['new_html_saved']} pdf+{counts['new_pdf_saved']}")

except Exception as e:
    import traceback
    run["status"] = "error"
    run["error"] = f"{type(e).__name__}: {e}"
    run["traceback"] = traceback.format_exc()
    run["finished_at"] = now_iso()
    atomic_write_json(os.path.join(RUN_DIR, "report.json"), run)
    exit_code = 3
finally:
    try:
        atomic_write_json(os.path.join(RUN_DIR, "lock-release.json"), {
            "released_at": now_iso(), "run_id": RUN_ID,
        })
    except Exception:
        pass
    # only remove own lock
    try:
        owner = load_json(os.path.join(LOCK, "owner.json"))
        if owner.get("run_id") == RUN_ID:
            shutil.rmtree(LOCK)
    except Exception:
        pass
sys.exit(exit_code)
