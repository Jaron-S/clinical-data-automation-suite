import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_data():
    """
    Generates simulated clinical data for EDC visits and Lab results.
    Outputs: raw_edc_visits.csv, raw_lab_results.csv
    """
    print("[INFO] Generating messy clinical data...")
    
    num_patients = 100
    subject_ids = [f"SUBJ-{i:03d}" for i in range(1, num_patients + 1)]
    
    # --- Generate EDC Data ---
    edc_data = []
    
    start_date = datetime(2023, 1, 1)
    
    for subj in subject_ids:
        # Simulate a visit date
        visit_date = start_date + timedelta(days=random.randint(0, 365))
        visit_date_str = visit_date.strftime("%Y-%m-%d")
        
        # Raw_Temp: Mixed units and formats
        temp_scenarios = [
            (36.5, 37.5, "C"),      # Normal C
            (97.0, 99.5, "F"),      # Normal F
            (38.0, 39.5, "C"),      # Fever C
            (100.4, 103.0, "F"),    # Fever F
            (98.0, 99.0, ""),       # No unit (assume F usually, but messy)
        ]
        
        scenario = random.choice(temp_scenarios)
        val = round(random.uniform(scenario[0], scenario[1]), 1)
        unit = scenario[2]
        
        if unit:
            raw_temp = f"{val} {unit}"
        else:
            raw_temp = f"{val}" # Just the number
            
        # Raw_HR: Numbers, typos, outliers
        hr_val = random.choice(
            [str(random.randint(60, 100))] * 80 +  # Normal keys
            [str(random.randint(101, 120))] * 10 + # Tachycardia
            ["High", "Not Done", "TBD"] * 5 +    # Typos/Strings
            ["900"] * 2                           # Outliers
        )
        
        # Respiratory Rate
        rr_val = random.randint(12, 25)
        
        # Blood Draw Performed?
        blood_draw = random.choice(["Yes"] * 80 + ["No"] * 20)
        
        # PII Generation
        initials = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
        dob = start_date - timedelta(days=random.randint(365*20, 365*70)) # Ages 20-70 approx
        dob_str = dob.strftime("%Y-%m-%d")

        edc_data.append({
            "SubjectID": subj,
            "VisitDate": visit_date_str,
            "PatientInitials": initials,
            "DateOfBirth": dob_str,
            "Raw_Temp": raw_temp,
            "Raw_HR": hr_val,
            "Raw_RR": rr_val,
            "Blood_Draw_Performed": blood_draw
        })
        
    edc_df = pd.DataFrame(edc_data)
    edc_df.to_csv("raw_edc_visits.csv", index=False)
    print(f"[INFO] raw_edc_visits.csv created with {len(edc_df)} rows.")

    # --- Generate Lab Data ---
    # Logic: If Blood_Draw_Performed is Yes, usually there is a lab result.
    # Missing Recon: 5 patients have Yes but no lab result.
    
    lab_data = []
    
    # Select 5 subjects to have MISSING lab data despite having blood draw
    missing_recon_subjs = random.sample(subject_ids, 5)
    
    for row in edc_data:
        subj = row["SubjectID"]
        if row["Blood_Draw_Performed"] == "Yes":
             if subj in missing_recon_subjs:
                 continue # Skip generating lab result -> Missing Recon scenario
             
             # Generate lab result
             # WBC: Normal 4.5-11.0. Abnormal <4.0 or >12.0
             wbc = round(random.uniform(3.0, 15.0), 1)
             
             lab_data.append({
                 "SubjectID": subj,
                 "VisitDate": row["VisitDate"], # Match SVSTDTC logic
                 "SampleID": f"SMP-{random.randint(10000, 99999)}",
                 "WBC": wbc
             })
             
    lab_df = pd.DataFrame(lab_data)
    lab_df.to_csv("raw_lab_results.csv", index=False)
    print(f"[INFO] raw_lab_results.csv created with {len(lab_df)} rows.")

if __name__ == "__main__":
    generate_data()
