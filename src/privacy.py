import pandas as pd

PRIVACY_CONFIG = {
    "Alberta (HIA)": {"scrub_initials": True, "mask_dob": "YearMonth"},
    "USA (HIPAA)": {"scrub_initials": False, "mask_dob": "Year"},
    "Canada (PIPEDA)": {"scrub_initials": True, "mask_dob": "Full"},
    "British Columbia (PIPA)": {"scrub_initials": True, "mask_dob": "YearMonth"},
    "Ontario (PHIPA)": {"scrub_initials": True, "mask_dob": "YearMonth"}
}

def apply_privacy(df, region):
    """
    Applies privacy rules to the DataFrame based on the selected region.
    """
    if region not in PRIVACY_CONFIG:
        return df
        
    config = PRIVACY_CONFIG[region]
    
    # Create a copy to avoid SettingWithCopy warnings on the original df
    df_scrubbed = df.copy()
    
    # --- Initials Scrubbing ---
    if config["scrub_initials"] and "INITIALS" in df_scrubbed.columns:
        df_scrubbed["INITIALS"] = "[REDACTED]"
        
    # --- DOB Masking ---
    if "BRTHDTC" in df_scrubbed.columns:
        mask_type = config["mask_dob"]
        
        def mask_date(date_str):
            if pd.isna(date_str):
                return date_str
            
            # Assuming YYYY-MM-DD
            try:
                parts = str(date_str).split("-")
                if len(parts) != 3:
                    return date_str
                    
                year, month, day = parts[0], parts[1], parts[2]
                
                if mask_type == "YearMonth":
                    return f"{year}-{month}-XX"
                elif mask_type == "Year":
                    return f"{year}"
                elif mask_type == "Full":
                    return "[REDACTED]"
                else:
                    return date_str
            except:
                return date_str
                
        df_scrubbed["BRTHDTC"] = df_scrubbed["BRTHDTC"].apply(mask_date)
        
    return df_scrubbed

if __name__ == "__main__":
    # Test
    test_data = {
        "INITIALS": ["ABC", "DEF"],
        "BRTHDTC": ["1990-05-12", "1985-11-23"]
    }
    df = pd.DataFrame(test_data)
    print("Original:\n", df)
    print("Alberta:\n", apply_privacy(df, "Alberta (HIA)"))
    print("USA:\n", apply_privacy(df, "USA (HIPAA)"))
