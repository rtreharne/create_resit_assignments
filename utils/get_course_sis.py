import pandas as pd
import json

def read_excel(fname):
    df = pd.read_excel(fname)
    return df

def create_course_list(fname):
    df = read_excel(fname)

    df["Subject-Course"] = df["Subject"].astype(str) + df["Course"].astype(str) + '-202425'

    # Get a unique list
    unique_values = df["Subject-Course"].unique().tolist()

    # Save to JSON
    with open("subject_course_list_all.json", "w") as f:
        json.dump(unique_values, f, indent=2)

if __name__ == "__main__":
    create_course_list("/home/freddie/create_resit_assignments/yr_1_2.xlsx")