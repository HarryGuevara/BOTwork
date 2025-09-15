import requests
from bs4 import BeautifulSoup

RSS_URL = "https://remotive.com/remote-jobs.rss"

def fetch_remotive():
    try:
        r = requests.get(RSS_URL, timeout=35, headers={"User-Agent":"Mozilla/5.0"})
        r.raise_for_status()
    except Exception as e:
        print("⚠️ Remotive error:", e)
        return []
    # Usar parser XML (tienes lxml en requirements)
    soup = BeautifulSoup(r.text, "xml")
    items = soup.find_all("item")
    jobs = []
    for it in items:
        title = it.title.text.strip() if it.title else ""
        link = it.link.text.strip() if it.link else ""
        pub = it.pubDate.text.strip() if it.pubDate else ""
        desc = it.description.text.strip() if it.description else ""
        company = ""
        # Remotive titula como "Role at Company" a menudo
        if " at " in title:
            t = title.split(" at ", 1)
            title = t[0].strip()
            company = t[1].strip()
        jobs.append({
            "job_id": f"remotive_{hash(link)}",
            "source": "remotive",
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
