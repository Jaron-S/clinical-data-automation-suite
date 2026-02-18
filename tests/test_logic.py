import pandas as pd
import pytest
from src.logic import run_checks

def test_sepsis_logic():
    """
    Verifies that the Sepsis logic correctly flags a patient with >= 2 criteria.
    Criteria:
    - Temp > 38 or < 36
    - HR > 90
    - RR > 20
    - WBC > 12 or < 4
    """
    
    # Create a dummy dataframe with one sepsis patient and one healthy patient
    data = [
        {
            "USUBJID": "SEPSIS-001", 
            "SVSTDTC": "2023-01-01", 
            "VSSTRESN_TEMP": 39.0, # Flag
            "VSSTRESN_HR": 100,    # Flag
            "Raw_RR": 18,          # Normal
            "WBC": 13.0,           # Flag (Total 3 flags)
            "Blood_Draw_Performed": "Yes",
            "SampleID": "SMP-001"
        },
        {
            "USUBJID": "HEALTHY-001", 
            "SVSTDTC": "2023-01-01", 
            "VSSTRESN_TEMP": 37.0, 
            "VSSTRESN_HR": 70,    
            "Raw_RR": 12,          
            "WBC": 6.0,
            "Blood_Draw_Performed": "Yes",
            "SampleID": "SMP-002"
        }
    ]
    
    df = pd.DataFrame(data)
    
    # Logic function expects merged data if called directly?
    # Logic.run_checks expects edc_df and lab_df and merges them.
    # Let's mock the inputdfs.
    
    edc_cols = ["USUBJID", "SVSTDTC", "VSSTRESN_TEMP", "VSSTRESN_HR", "Raw_RR", "Blood_Draw_Performed"]
    lab_cols = ["USUBJID", "SVSTDTC", "WBC", "SampleID"]
    
    edc_df = df[edc_cols].copy()
    lab_df = df[lab_cols].copy()
    
    safety_df, recon_df = run_checks(edc_df, lab_df)
    
    # Assertions
    assert "SEPSIS-001" in safety_df["USUBJID"].values, "Sepsis patient should be flagged"
    assert "HEALTHY-001" not in safety_df["USUBJID"].values, "Healthy patient should NOT be flagged"
    assert len(safety_df) == 1
