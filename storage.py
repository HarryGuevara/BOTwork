import os, csv
from datetime import datetime

class JobStorage:
    def __init__(self, config):
        self.csv_path = config.get("storage", {}).get("csv_path", "data/jobs.csv")
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)

    def load_existing_ids(self):
        if not os.path.exists(self.csv_path):
            return set()
        with open(self.csv_path, "r", encoding="utf-8", newline="") as f:
            rdr = csv.DictReader(f)
            return {row.get("job_id") for row in rdr if row.get("job_id")}

    def append_jobs(self, jobs):
        exists = os.path.exists(self.csv_path)
        fieldnames = ["job_id","source","company","title","location","remote","contract_type",
                      "seniority","workload","published_at","apply_url","tags",
                      "salary","currency","description_short","saved_at","requires_human",
                      "application_status","applied_at","notes"]
        now = datetime.utcnow().isoformat()

        with open(self.csv_path, "a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            if not exists:
                w.writeheader()
            for j in jobs:
                j.setdefault("saved_at", now)
                j.setdefault("requires_human", "")
                j.setdefault("application_status", "pending")
                j.setdefault("applied_at", "")
                j.setdefault("notes", "")
                for k in fieldnames:
                    j.setdefault(k, "")
                w.writerow({k: j.get(k, "") for k in fieldnames})
        return jobs

    def mark_applied(self, job_id):
        if not os.path.exists(self.csv_path):
            return False
        rows = []
        found = False
        with open(self.csv_path, "r", encoding="utf-8", newline="") as f:
            rdr = csv.DictReader(f)
            rows = list(rdr)
            flds = rdr.fieldnames
        for r in rows:
            if r.get("job_id") == job_id:
                r["application_status"] = "applied"
                r["applied_at"] = datetime.utcnow().isoformat()
                found = True
                break
        if not found:
            return False
        with open(self.csv_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=flds)
            w.writeheader()
            w.writerows(rows)
        return True
