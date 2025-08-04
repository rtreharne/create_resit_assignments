import json
import os
import csv
from dotenv import load_dotenv
from canvasapi import Canvas
from canvasapi.exceptions import ResourceDoesNotExist
from tqdm import tqdm

# Load environment variables
load_dotenv()
API_URL = os.getenv("CANVAS_API_URL")
API_TOKEN = os.getenv("CANVAS_API_TOKEN")

if not API_URL or not API_TOKEN:
    raise ValueError("Missing CANVAS_API_URL or CANVAS_API_TOKEN in .env file.")

# Initialize Canvas API
canvas = Canvas(API_URL, API_TOKEN)

# Load course list
with open("subject_course_list_all.json") as f:
    course_ids = json.load(f)

results = []

# Progress bar
for course_id in tqdm(course_ids, desc="Checking courses"):
    try:
        course = canvas.get_course(course_id, use_sis_id=True)
        modules = course.get_modules()
        found_module = False
        has_items = False

        for module in modules:
            if module.name.strip() == "Resit Information 24/25":
                found_module = True
                items = list(module.get_module_items())
                has_items = len(items) > 0
                break

        results.append({
            "course_id": course_id,
            "course_name": course.name,
            "course_url": f"{API_URL}/courses/{course.id}",
            "module_found": "Yes" if found_module else "No",
            "module_has_items": "Yes" if has_items else "No"
        })

    except ResourceDoesNotExist:
        results.append({
            "course_id": course_id,
            "course_name": "Course not found",
            "course_url": "",
            "module_found": "No",
            "module_has_items": "-"
        })
    except Exception as e:
        results.append({
            "course_id": course_id,
            "course_name": f"Error: {str(e)}",
            "course_url": "",
            "module_found": "Error",
            "module_has_items": "-"
        })

# Save to CSV
csv_file = "resit_module_report.csv"
with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["course_id", "course_name", "course_url", "module_found", "module_has_items"])
    writer.writeheader()
    writer.writerows(results)

print(f"\n✅ Report saved to {csv_file}")
