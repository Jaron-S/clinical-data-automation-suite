import streamlit as st
import pandas as pd
import os
from src.data_sim import generate_data
from src.etl import clean_and_standardize
from src.logic import run_checks
from src.reporter import generate_excel
from src.privacy import apply_privacy

# Page Config
st.set_page_config(page_title="CDAS - Clinical Data Automation Suite", page_icon="🏥", layout="wide")



# Main Area
st.title("Clinical Data Automation Suite 🏥")
st.markdown("### QC & Reconciliation Dashboard")

with st.expander("About This Pipeline"):
    st.markdown("""
    This automated pipeline simulates a Clinical Data Management workflow:
    1.  **Ingestion**: Accepts raw CSV exports from EDC (Electronic Data Capture) and Central Lab systems.
    2.  **ETL**: Standardizes column names and formats to **CDISC SDTM** standards.
    3.  **Logic Checks**: 
        *   **Safety**: Flags patients meeting SIRS criteria (Potential Sepsis).
        *   **Reconciliation**: Identifies missing lab samples for visits where a blood draw was confirmed.
    4.  **Privacy**: Applies region-specific masking (Alberta HIA, HIPAA, PIPEDA) to PII before reporting.
    """)

col1, col2 = st.columns(2)

with col1:
    edc_file = st.file_uploader("Upload EDC Visits (.csv)", type=["csv"], help="Required columns: SubjectID, VisitDate, Raw_Temp, Raw_HR, Raw_RR, Blood_Draw_Performed")

with col2:
    lab_file = st.file_uploader("Upload Lab Results (.csv)", type=["csv"], help="Required columns: SubjectID, VisitDate, SampleID, WBC")

if st.button("Use Demo Data", help="Generates synthetic clinical data with built-in dirtiness (typos, outliers) for testing."):
    with st.spinner("Generating demo data..."):
        generate_data() # Generates raw_edc_visits.csv and raw_lab_results.csv in current dir
        st.success("Demo Data Generated!")
        # Simulating file upload by reading into session state or just using filenames later
        # But to be consistent with file_uploader, we can just point to the files on disk if no upload is present.
        st.session_state['use_demo'] = True


# Study Region Configuration
col_region, col_spacer = st.columns([1, 2])
with col_region:
    region = st.selectbox("Select Study Region (Privacy Protocol)", ["Canada (PIPEDA)", "Alberta (HIA)", "British Columbia (PIPA)", "Ontario (PHIPA)", "USA (HIPAA)"], index=0, help="Determines how PII (Initials, DOB) is masked in the output.")

# Logic to run pipeline
if st.button("Run Compliance Checks", help="Executes the full pipeline: ETL -> Safety Logic -> Reporting"):
    
    edc_path = None
    lab_path = None
    
    # 1. Handle Input Sources
    if st.session_state.get('use_demo'):
        edc_path = "raw_edc_visits.csv"
        lab_path = "raw_lab_results.csv"
        
        if not os.path.exists(edc_path) or not os.path.exists(lab_path):
             st.error("Demo data not found. Please click 'Use Demo Data' first.")
             st.stop()
             
    elif edc_file and lab_file:
        # Save uploaded files to temp
        edc_path = "temp_edc.csv"
        lab_path = "temp_lab.csv"
        
        with open(edc_path, "wb") as f:
            f.write(edc_file.getbuffer())
            
        with open(lab_path, "wb") as f:
            f.write(lab_file.getbuffer())
    else:
        st.warning("Please upload both files or use demo data.")
        st.stop()

    # 2. Run ETL & Logic
    try:
        with st.spinner("Running ETL and Safety Checks..."):
            edc_df, lab_df = clean_and_standardize(edc_path, lab_path)
            
            if edc_df is None or lab_df is None:
                st.error("ETL Process Failed.")
                st.stop()
                
            safety_df, recon_df = run_checks(edc_df, lab_df)

            # --- Privacy Layer ---
            st.info(f"Privacy Protocol Active: {region} - PII Masking Applied.")
            safety_df_clean = apply_privacy(safety_df, region)
            recon_df_clean = apply_privacy(recon_df, region)
            
            # Generate Report
            output_file = "Query_Log.xlsx"
            generate_excel(safety_df_clean, recon_df_clean, output_file)
            
        # 3. Dashboard Metrics
        st.divider()
        st.subheader("Study Metrics")
        
        m1, m2, m3 = st.columns(3)
        num_patients = edc_df['USUBJID'].nunique()
        sepsis_flags = len(safety_df)
        missing_labs = len(recon_df)
        
        m1.metric("Total Patients", num_patients)
        m2.metric("Sepsis Flags", sepsis_flags, delta="-High Risk" if sepsis_flags > 0 else "Normal", delta_color="inverse")
        m3.metric("Missing Lab Samples", missing_labs, delta="Recon Issue" if missing_labs > 0 else "Clean", delta_color="inverse")
        
        # 4. Data Preview
        if not safety_df.empty:
            st.subheader("Safety Flags Detected")
            st.warning(f"Found {len(safety_df)} potential safety issues.")

            st.dataframe(safety_df_clean.style.applymap(lambda x: 'background-color: #ffcccc', subset=['Query_Text']))
        else:
            st.success("No Safety Flags detected.")
            
        # 5. Download
        with open(output_file, "rb") as f:
            st.download_button(
                label="Download Query Log (Excel)",
                data=f,
                file_name="Query_Log.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
    except Exception as e:
        st.error(f"An error occurred: {e}")
        # Optional: Print traceback for debugging
        import traceback
        st.text(traceback.format_exc())

    # Cleanup temp files if used
    if edc_file and lab_file:
        try:
             os.remove("temp_edc.csv")
             os.remove("temp_lab.csv")
        except:
            pass
