import requests

def fetch_ashby(boards):
    jobs = []
    for board in boards:
        url = f"https://jobs.ashbyhq.com/api/posting/{board}"
        try:
            r = requests.get(url, timeout=20, headers={"User-Agent":"Mozilla/5.0"})
            if r.status_code == 404:
                continue
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"⚠️ Ashby {board} error:", e)
            continue
        for it in data.get("jobs", []):
            locs = it.get("locations") or []
            loc = ", ".join(locs) if isinstance(locs, list) else (locs or "")
            rem = any("remote" in (l or "").lower() for l in (locs if isinstance(locs, list) else [loc]))
            jobs.append({
                "job_id": f"ashby_{board}_{it.get('id')}",
                "source": f"ashby:{board}",
                "company": board,
                "title": it.get("title",""),
                "location": loc,
                "remote": rem,
                "contract_type": "",
                "seniority": "",
                "workload": "",
                "published_at": it.get("updatedAt",""),
                "apply_url": it.get("jobUrl") or "",
                "tags": ",".join(it.get("departments") or []),
                "salary": "",
                "currency": "",
                "description_short": (it.get("shortDescription") or "")[:280],
                "requires_human": True
            })
    return jobs
