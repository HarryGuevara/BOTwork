import requests

def fetch_remoteok():
    url = "https://remoteok.com/api"
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent":"Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print("⚠️ RemoteOK error:", e)
        return []
    jobs = []
    for item in data:
        if not isinstance(item, dict) or "id" not in item:
            continue
        jobs.append({
            "job_id": f"remoteok_{item.get('id')}",
            "source": "remoteok",
            "company": item.get("company",""),
            "title": item.get("position",""),
            "location": item.get("location","Remote") or "Remote",
            "remote": True,
            "contract_type": "",
            "seniority": "",
            "workload": "",
            "published_at": item.get("date",""),
            "apply_url": item.get("url",""),
            "tags": ",".join(item.get("tags") or []),
            "salary": (item.get("salary") or ""),
            "currency": "",
            "description_short": (item.get("description") or "")[:280],
            "requires_human": True
        })
    return jobs
