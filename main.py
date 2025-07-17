import pandas
from canvasapi import Canvas
from dotenv import load_dotenv
import os
import requests
import time
import re
from canvasapi.exceptions import ResourceDoesNotExist
import json

# Load variables from .env file
load_dotenv()

# Access them using os.getenv
CANVAS_API_URL= os.getenv("CANVAS_API_URL")
CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN")

canvas = Canvas(CANVAS_API_URL, CANVAS_API_TOKEN)

def get_or_create_assignment_group(course, group_name, group_weight=None):
    """
    Get an existing assignment group by name, or create it if it doesn't exist.

    Args:
        course (canvasapi.course.Course): Canvas course object.
        group_name (str): Name of the assignment group to get or create.
        group_weight (float or None): Optional weight for the group (if weighted grading is used).

    Returns:
        canvasapi.assignment.AssignmentGroup: The existing or newly created group.
    """
    # Check if group already exists
    for group in course.get_assignment_groups():
        if group.name.strip().lower() == group_name.strip().lower():
            return group

    # Group doesn't exist — create it
    params = {"name": group_name}
    if group_weight is not None:
        params["group_weight"] = group_weight

    return course.create_assignment_group(**params)

def check_if_resit_exists(course_id, assignment_id):
    course = canvas.get_course(course_id)
    assignment = course.get_assignment(assignment_id)
    target_name = assignment.name.strip()

    # Get all assignment names
    assignments_list = [x.name for x in course.get_assignments()]

    # Filter for those that include the original name (case-insensitive)
    related = [name for name in assignments_list if target_name.lower() in name.lower()]

    # Join the filtered names and check for "RESIT"
    if "RESIT" in " ".join(related):
        return True

    return False

def duplicate_assignment(course_id, assignment_id):

    course = canvas.get_course(course_id)
    assignment = course.get_assignment(assignment_id)

    """
    Duplicates a Canvas assignment using the Canvas API.
    
    Args:
        course_id (str or int): Canvas course ID (not SIS ID).
        assignment_id (str or int): ID of the assignment to duplicate.
        api_token (str): Your Canvas API token.
        base_url (str): Base Canvas URL (default is Canvas Cloud).
    
    Returns:
        dict: The duplication job status response.
    """
    # Check RESIT assignment doesn't already exist
    resit_exists = check_if_resit_exists(course_id, assignment_id)

    if "draft" in assignment.name.lower():
        return None

    if resit_exists:
        return None
    else:
        url = f"{CANVAS_API_URL}/api/v1/courses/{course_id}/assignments/{assignment_id}/duplicate"
        headers = {
            "Authorization": f"Bearer {CANVAS_API_TOKEN}"
        }

        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            new_assignment_id = response.json()['id']
            new_assignment = update_assignment(course_id, new_assignment_id)
            return new_assignment
        else:
            print(f"Failed to duplicate assignment: {assignment.name} ")
            return None
    

def update_assignment(course_id, assignment_id):
    max_wait = 60  # seconds
    interval = 5   # seconds
    elapsed = 0

    course = canvas.get_course(course_id)

    print(f"Waiting for assignment {assignment_id} to become available...")

    while elapsed < max_wait:
        try:
            assignment = course.get_assignment(assignment_id)
            break  # Found it
        except ResourceDoesNotExist:
            time.sleep(interval)
            elapsed += interval
    else:
        raise TimeoutError(f"Assignment {assignment_id} not found after 60 seconds.")

    # Clean and rename
    original_name = assignment.name
    cleaned_name = re.sub(r'\s*copy\s*$', '', original_name, flags=re.IGNORECASE).strip()
    updated_name = f"RESIT {cleaned_name}"

    print(f"Updating assignment: '{original_name}' → '{updated_name}'")

    assignment_group = get_or_create_assignment_group(course, "RESITS 202425")

    # Update fields
    assignment.edit(assignment={
        "name": updated_name,
        "published": False,
        "unlock_at": "2025-08-11T09:00:00Z",
        "lock_at": "2025-08-25T16:00:00Z",
        "due_at": "2025-08-25T16:00:00Z",
        "assignment_group_id": assignment_group.id
    })

    print("Assignment successfully updated.")
    return assignment

    
def get_assignments(course_sis_id):
    course_code = course_sis_id.split("-")[0]
    course = canvas.get_course(course_sis_id, use_sis_id=True)
    assignments = [x for x in course.get_assignments() if course_code in x.name and x.published]

    return assignments

import csv
from pathlib import Path
from datetime import datetime

def create_log_file():
    """
    Creates a timestamped CSV log file with headers:
    course, assignment_name, assignment_url, error

    Returns:
        Path: Path to the created log file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"resit_assignment_log_{timestamp}.csv"
    log_path = Path(filename)

    with log_path.open(mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["course", "assignment_name", "assignment_url", "error"])

    return log_path



if __name__ == "__main__":


    with open("subject_course_list.json", "r", encoding="utf-8") as f:
        course_sis_id_list = json.load(f)

    for course_sis_id in course_sis_id_list:

        print("course_sis_id", course_sis_id)

        assignments = get_assignments(course_sis_id)
        log_path = create_log_file()
        for assignment in assignments:
            try:
                new_assignment = duplicate_assignment(assignment.course_id, assignment.id)
                new_assignment_url = f"https://{CANVAS_API_URL}/api/v1/courses/{assignment.course_id}/assignments/{assignment.id}"
                with open(log_path, "a", newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([course_sis_id, new_assignment.name, new_assignment_url, "Created"])
            except Exception as e:
                with open(log_path, "a", newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([course_sis_id, assignment.name, "", f"Error duplicating: {str(e)}"])
