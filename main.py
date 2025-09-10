import argparse, os, csv, sys, yaml, pytz
from dateutil import parser as dateparser
from datetime import datetime
from storage import JobStorage
from alerts import maybe_notify
from sources.remoteok import fetch_remoteok
from sources.weworkremotely import fetch_wwr
from sources.greenhouse import fetch_greenhouse
from sources.lever import fetch_lever
from sources.ashby import fetch_ashby

BOGOTA_TZ = pytz.timezone("America/Bogota")

def load_config():
    path = os.environ.get("JOBBOT_CONFIG", "config.yaml")
    if not os.path.exists(path):
        print("⚠️ No existe config.yaml. Crea uno primero.")
        sys.exit(1)
    return yaml.safe_load(open(path, "r", encoding="utf-8"))

def normalize_text(s):
    return (s or "").lower()

def job_matches(job, prefs):
    title = normalize_text(job.get("title"))
    desc = normalize_text(job.get("description_short"))
    tags_raw = job.get("tags")
    if isinstance(tags_raw, list):
        tags = ",".join(tags_raw)
    elif isinstance(tags_raw, str):
        tags = tags_raw
    else:
        tags = ""
    tags = normalize_text(tags)
    haystack = " ".join([title, desc, tags])

    tiers = (prefs or {}).get("keywords", {})
    must = [k.lower() for k in tiers.get("must", [])]
    should = [k.lower() for k in tiers.get("should", [])]
    nice = [k.lower() for k in tiers.get("nice", [])]

    if must and not all(k in haystack for k in must):
        return False
    if should and not any(k in haystack for k in should):
        return False

    exc = (prefs or {}).get("exclude_keywords") or []
    if any(k.lower() in haystack for k in exc):
        return False

    if (prefs or {}).get("remote_only", False) and str(job.get("remote")).lower() not in ["true","1","yes"]:
        return False

    allowed = [a.lower() for a in ((prefs or {}).get("allowed_countries") or [])]
    loc = normalize_text(job.get("location"))
    if allowed and allowed != ["*"]:
        if not any(a in loc for a in allowed):
            if not (job.get("remote") and "remote" in allowed):
                return False

    wl_prefs = [w.lower() for w in ((prefs or {}).get("workload") or [])]
    if wl_prefs:
        wl = normalize_text(job.get("workload"))
        if wl and not any(w in wl for w in wl_prefs):
            return False

    sen_prefs = [s.lower() for s in ((prefs or {}).get("seniority") or [])]
    if sen_prefs and not any(s in haystack for s in sen_prefs):
        return False

    return True

def dedupe(existing_ids, jobs):
    out = []
    for j in jobs:
        jid = j.get("job_id")
        if jid and jid not in existing_ids:
            out.append(j)
    return out

def crawl(config):
    storage = JobStorage(config)
    already = storage.load_existing_ids()
    all_new = []

    sources_cfg = config.get("sources", {})

    if sources_cfg.get("remoteok", {}).get("enabled", True):
        all_new += fetch_remoteok()

    if sources_cfg.get("weworkremotely", {}).get("enabled", True):
        all_new += fetch_wwr()

    if sources_cfg.get("greenhouse", {}).get("enabled", False):
        boards = sources_cfg["greenhouse"].get("boards", [])
        if boards:
            all_new += fetch_greenhouse(boards)

    if sources_cfg.get("lever", {}).get("enabled", False):
        boards = sources_cfg["lever"].get("boards", [])
        if boards:
            all_new += fetch_lever(boards)

    if sources_cfg.get("ashby", {}).get("enabled", False):
        boards = sources_cfg["ashby"].get("boards", [])
        if boards:
            all_new += fetch_ashby(boards)

    prefs = config.get("preferences", {})
    filtered = [j for j in all_new if job_matches(j, prefs)]
    new_unique = dedupe(already, filtered)

    print(f"Encontradas total: {len(all_new)}; tras filtro: {len(filtered)}; nuevas únicas: {len(new_unique)}")

    if not new_unique:
        print("No hay oferta")

def mark_applied(config, job_id):
    storage = JobStorage(config)
    updated = storage.mark_applied(job_id)
    if updated:
        print(f"✅ Marcada como aplicada: {job_id}")
    else:
        print(f"⚠️ No encontrada: {job_id}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--crawl", action="store_true", help="Buscar ofertas")
    ap.add_argument("--notify", action="store_true", help="Enviar alertas si hay nuevas")
    ap.add_argument("--applied", type=str, help="Marcar un job_id como aplicado")
    args = ap.parse_args()

    config = load_config()

    if args.applied:
        mark_applied(config, args.applied)
        return

    new_jobs = []
    if args.crawl:
        new_jobs = crawl(config)

    if args.notify and new_jobs:
        maybe_notify(config, new_jobs)

if __name__ == "__main__":
    main()
