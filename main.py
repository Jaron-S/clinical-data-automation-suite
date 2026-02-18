import sys
from src.data_sim import generate_data
from src.etl import clean_and_standardize
from src.logic import run_checks
from src.reporter import generate_excel

def main():
    print("==========================================")
    print("   Clinical Data Automation Suite (CDAS)  ")
    print("               Phase 1                    ")
    print("==========================================")
    
    # Step 1: Data Generation
    try:
        generate_data()
    except Exception as e:
        print(f"[ERROR] Data Generation failed: {e}")
        sys.exit(1)
        
    # Step 2: ETL
    try:
        edc_df, lab_df = clean_and_standardize("raw_edc_visits.csv", "raw_lab_results.csv")
        if edc_df is None or lab_df is None:
            print("[ERROR] ETL failed to produce dataframes.")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] ETL process failed: {e}")
        sys.exit(1)
        
    # Step 3: Logic & Safety Checks
    try:
        safety_df, recon_df = run_checks(edc_df, lab_df)
    except Exception as e:
        print(f"[ERROR] Logic checks failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    # Step 4: Reporting
    try:
        generate_excel(safety_df, recon_df, "Query_Log.xlsx")
    except Exception as e:
        print(f"[ERROR] Report generation failed: {e}")
        sys.exit(1)
        
    print("==========================================")
    print("[SUCCESS] CDAS Pipeline Completed.")
    print("Check 'Query_Log.xlsx' for results.")
    print("==========================================")

if __name__ == "__main__":
    main()
