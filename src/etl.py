import pandas as pd
import numpy as np

def clean_and_standardize(edc_path, lab_path):
    """
    Cleans and standardizes EDC and Lab data.
    """
    print("[INFO] Starting ETL process...")
    try:
        edc_df = pd.read_csv(edc_path)
        lab_df = pd.read_csv(lab_path)
    except FileNotFoundError as e:
        print(f"[ERROR] Input file not found: {e}")
        return None, None

    # --- Standardize EDC ---
    # Rename columns
    edc_df.rename(columns={
        "SubjectID": "USUBJID",
        "VisitDate": "SVSTDTC",
        "PatientInitials": "INITIALS",
        "DateOfBirth": "BRTHDTC"
    }, inplace=True)
    
    # Ensure ISO 8601 Date
    edc_df["SVSTDTC"] = pd.to_datetime(edc_df["SVSTDTC"]).dt.strftime("%Y-%m-%d")
    if "BRTHDTC" in edc_df.columns:
        edc_df["BRTHDTC"] = pd.to_datetime(edc_df["BRTHDTC"]).dt.strftime("%Y-%m-%d")
    
    # --- Unit Conversion (Temp) ---
    def normalize_temp(val):
        """
        Parses temperature string, converts F to C.
        Returns numeric Celsius value.
        """
        if pd.isna(val):
            return np.nan
            
        val_str = str(val).upper().strip()
        
        # Detect unit
        unit = "F" # Default assumption if no unit and looks like F (e.g. > 50)
        numeric_part = ""
        
        if "C" in val_str:
            unit = "C"
            numeric_part = val_str.replace("C", "").strip()
        elif "F" in val_str:
            unit = "F"
            numeric_part = val_str.replace("F", "").strip()
        else:
            # Guess based on magnitude if just a number
            try:
                float_val = float(val_str)
                if float_val > 50: # Likely F
                    unit = "F"
                    numeric_part = val_str
                else:
                    unit = "C"
                    numeric_part = val_str
            except ValueError:
                return np.nan # Unparseable
                
        try:
            temp_c = float(numeric_part)
            if unit == "F":
                temp_c = (temp_c - 32) * 5/9
            return round(temp_c, 1)
        except ValueError:
            return np.nan

    edc_df["VSSTRESN_TEMP"] = edc_df["Raw_Temp"].apply(normalize_temp)
    
    # --- Handle Non-Numeric HR ---
    # Convert to numeric, coerce errors to NaN
    edc_df["VSSTRESN_HR"] = pd.to_numeric(edc_df["Raw_HR"], errors='coerce')
    
    # --- Standardize Lab ---
    lab_df.rename(columns={
        "SubjectID": "USUBJID",
        "VisitDate": "SVSTDTC"
    }, inplace=True)
    
    # Ensure ISO 8601
    lab_df["SVSTDTC"] = pd.to_datetime(lab_df["SVSTDTC"]).dt.strftime("%Y-%m-%d")
    
    print("[INFO] ETL Complete.")
    return edc_df, lab_df

if __name__ == "__main__":
    # Test run
    clean_and_standardize("raw_edc_visits.csv", "raw_lab_results.csv")
