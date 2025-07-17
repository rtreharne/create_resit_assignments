# Canvas Resit Assignment Duplicator

This script automates the process of duplicating Canvas assignments for resit assessments. It identifies all published assignments in a course, checks for existing resit versions, duplicates them (if eligible), renames them according to a standard format, and assigns them to a dedicated assignment group with appropriate dates.

---

## ✨ Features

- Authenticates with the Canvas LMS via API using a `.env` file
- Identifies and duplicates published assignments (excluding drafts or already duplicated resits)
- Renames the duplicated assignment to follow `RESIT <Original Name>` format
- Moves resit assignments to a group named `RESITS 20242X`
- Sets specific unlock, lock, and due dates
- Generates a timestamped CSV log with success and error details for each assignment

---

## 📁 Requirements

- Python 3.8+
- A valid Canvas API token with appropriate scopes
- SIS course IDs stored in `subject_course_list.json`
- `.env` file configured with your Canvas credentials

---

## 📦 Setup

1. **Clone the repository** and navigate into the project directory.

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** in the root directory:
   ```env
   CANVAS_API_URL=https://<your-canvas-domain>
   CANVAS_API_TOKEN=<your-canvas-api-token>
   ```

5. **Create a `subject_course_list.json` file** in the same directory containing a list of course SIS IDs:
   ```json
   [
     "BIO123-202425",
     "CHEM456-202425"
   ]
   ```

---

## ▶️ Running the Script

Once setup is complete, run the script using:

```bash
python duplicate_resits.py
```

A CSV log file (e.g., `resit_assignment_log_20250717_093201.csv`) will be generated in the same directory with the following columns:

- `course`
- `assignment_name`
- `assignment_url`
- `error` (will show "Created" if successful, or error message if failed)

---



## 📄 License

MIT License

---

## 📬 Contact

For questions or contributions, contact **Dr. Robert Treharne** at [R.Treharne@liverpool.ac.uk](mailto:R.Treharne@liverpool.ac.uk).
