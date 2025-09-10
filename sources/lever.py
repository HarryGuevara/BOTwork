import requests, re

def fetch_lever(boards):
    jobs = []
    for board in boards:
        url = f"https://api.lever.co/v0/postings/{board}?mode=json"
        try:
            r = requests.get(url, timeout=20, headers={"User-Agent":"Mozilla/5.0"})
            if r.status_code == 404:
                continue
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"⚠️ Lever {board} error:", e)
            continue
        for it in data:
            cats = it.get("categories") or {}
            loc = cats.get("location")
            if isinstance(loc, dict):
                loc = loc.get("name","")
            rem = "remote" in (loc or "").lower() if isinstance(loc, str) else False
            commitment = cats.get("commitment")
            if isinstance(commitment, dict):
                commitment = commitment.get("name","")
            jobs.append({
                "job_id": f"lever_{board}_{it.get('id')}",
                "source": f"lever:{board}",
                "company": board,
                "title": it.get("text",""),
                "location": loc or "",
                "remote": rem,
                "contract_type": commitment or "",
                "seniority": "",
                "workload": commitment or "",
                "published_at": it.get("createdAt",""),
                "apply_url": it.get("hostedUrl") or "",
                "tags": ",".join(filter(None, [(cats.get("team") or ""), str(commitment or ""), str(loc or "")])),
                "salary": "",
                "currency": "",
                "description_short": re.sub("<.*?>"," ", it.get("description") or "")[:280],
                "requires_human": True
            })
    return jobs
