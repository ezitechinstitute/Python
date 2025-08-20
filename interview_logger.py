import json
import os
from datetime import datetime

LOG_FILE = "interview_logs.json"

def save_log(candidate_name, questions_and_answers):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "candidate": candidate_name,
        "interview": questions_and_answers
    }

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r+") as file:
            data = json.load(file)
            data.append(log_entry)
            file.seek(0)
            json.dump(data, file, indent=4)
    else:
        with open(LOG_FILE, "w") as file:
            json.dump([log_entry], file, indent=4)
