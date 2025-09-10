import requests, re

def fetch_greenhouse(boards):
    jobs = []
    for board in boards:
        url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
        try:
            r = requests.get(url, timeout=20, headers={"User-Agent":"Mozilla/5.0"})
            if r.status_code == 404:
                continue
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"⚠️ Greenhouse {board} error:", e)
            continue
        for item in data.get("jobs", []):
            loc = (item.get("location") or {}).get("name","")
            rem = "remote" in (loc or "").lower() or "anywhere" in (loc or "").lower()
            apply_url = item.get("absolute_url") or ""
            company = board
            title = item.get("title","")
            tags = []
            if item.get("departments"):
                tags += [d.get("name","") for d in item["departments"]]
            if item.get("offices"):
                tags += [o.get("name","") for o in item["offices"]]
            desc = (item.get("content") or "")
            desc_short = re.sub("<.*?>", " ", desc)[:280]
            jobs.append({
                "job_id": f"gh_{board}_{item.get('id')}",
                "source": f"greenhouse:{board}",
                "company": company,
                "title": title,
                "location": loc,
                "remote": rem,
                "contract_type": "",
                "seniority": "",
                "workload": "",
                "published_at": item.get("updated_at",""),
                "apply_url": apply_url,
                "tags": ",".join(tags),
                "salary": "",
                "currency": "",
                "description_short": desc_short,
                "requires_human": True
            })
    return jobs
