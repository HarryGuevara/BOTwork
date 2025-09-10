import requests
from bs4 import BeautifulSoup

RSS_URL = "https://weworkremotely.com/remote-jobs.rss"

def fetch_wwr():
    try:
        r = requests.get(RSS_URL, timeout=20, headers={"User-Agent":"Mozilla/5.0"})
        r.raise_for_status()
    except Exception as e:
        print("⚠️ WWR error:", e)
        return []
    soup = BeautifulSoup(r.text, "xml")
    items = soup.find_all("item")
    jobs = []
    for it in items:
        title = it.title.text if it.title else ""
        link = it.link.text if it.link else ""
        pub = it.pubDate.text if it.pubDate else ""
        desc = it.description.text if it.description else ""
        company = ""
        t = title.split("–", 1)
        if len(t) == 2:
            company, title = t[0].strip(), t[1].strip()
        jobs.append({
            "job_id": f"wwr_{hash(link)}",
            "source": "weworkremotely",
            "company": company,
            "title": title,
            "location": "Remote",
            "remote": True,
            "contract_type": "",
            "seniority": "",
            "workload": "",
            "published_at": pub,
            "apply_url": link,
            "tags": "",
            "salary": "",
            "currency": "",
            "description_short": desc[:280],
            "requires_human": True
        })
    return jobs
