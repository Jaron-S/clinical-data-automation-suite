import pandas as pd
import numpy as np

def run_checks(edc_df, lab_df):
    """
    Runs safety and reconciliation checks.
    Returns: safety_df (rows with sepsis flags), recon_df (missing labs)
    """
    print("[INFO] Running logic checks...")
    
    # --- Merge Data ---
    # Left join EDC with Lab to find missing labs
    merged_df = pd.merge(edc_df, lab_df, on=["USUBJID", "SVSTDTC"], how="left")
    
    # --- Reconciliation Check ---
    # Flag: Blood_Draw_Performed == "Yes" AND SampleID is Null
    recon_mask = (merged_df["Blood_Draw_Performed"] == "Yes") & (merged_df["SampleID"].isnull())
    recon_df = merged_df[recon_mask].copy()
    recon_df["Query_Text"] = "Lab sample missing despite blood draw confirmation."
    
    if not recon_df.empty:
        print(f"[WARN] Found {len(recon_df)} reconciliation issues.")

    # --- Safety Check (Sepsis) ---
    # Criteria:
    # 1. Temp > 38 C or < 36 C
    # 2. HR > 90
    # 3. RR > 20
    # 4. WBC > 12 (12,000) or < 4 (4,000) - Assuming units in 10^3/uL based on data_sim
    
    # We need to calculate flags for each criterion
    # Temp
    # Note: VSSTRESN_TEMP is in C
    temp_flag = (merged_df["VSSTRESN_TEMP"] > 38) | (merged_df["VSSTRESN_TEMP"] < 36)
    
    # HR
    hr_flag = merged_df["VSSTRESN_HR"] > 90
    
    # RR
    rr_flag = merged_df["Raw_RR"] > 20
    
    # WBC
    # WBC is in Lab data. 
    # data_sim generates WBC between 3.0 and 15.0. 
    # Criteria: > 12 or < 4
    wbc_flag = (merged_df["WBC"] > 12) | (merged_df["WBC"] < 4)
    
    # Sum flags (False=0, True=1)
    # We need at least 2 flags to be "Potential Sepsis"
    criteria_count = temp_flag.astype(int) + hr_flag.astype(int) + rr_flag.astype(int) + wbc_flag.astype(int)
    
    safety_mask = criteria_count >= 2
    safety_df = merged_df[safety_mask].copy()
    safety_df["Query_Text"] = "Potential Sepsis: >= 2 criteria met. Please confirm clinical status."
    
    if not safety_df.empty:
        print(f"[WARN] Found {len(safety_df)} potential sepsis cases.")
        
    return safety_df, recon_df

if __name__ == "__main__":
    # Test stub
    pass
