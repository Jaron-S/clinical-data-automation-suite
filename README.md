# Clinical Data Automation Suite (CDAS)

**Protocol ID:** CDAS-001  
**Version:** 1.1.0  
**Status:** Validation Complete  

## 1. Executive Summary
The **Clinical Data Automation Suite (CDAS)** is a specialized ETL (Extract, Transform, Load) and customized safety pipeline designed to simulate the workflow of a Modern Clinical Data Manager. It automates the ingestion of disparate clinical datasets, standardizes them to industry formats (**CDISC SDTM**), and executes complex logic to identify safety signals (Sepsis) and data integrity issues (Reconciliation) before exporting audit-ready query logs.

## 2. Technology Stack
*   **Core Engine:** Python 3.9+
*   **Data Processing:** Pandas (High-performance manipulation) & NumPy
*   **User Interface:** Streamlit (Interactive Web Dashboard)
*   **Reporting:** OpenPyXL (Excel automation)
*   **Testing:** Pytest (Clinical Logic Verification)

## 3. Key Features & Modules

### A. Automated ETL & Standardization (`src.etl`)
The pipeline performs real-time cleaning to align raw data with **CDISC SDTM** standards:
*   **Column Mapping:** Harmonizes legacy headers (e.g., `SubjectID` → `USUBJID`, `VisitDate` → `SVSTDTC`).
*   **Unit Normalization:** Algorithms automatically detect and convert Fahrenheit temperatures (>50) to Celsius (`VSSTRESN`).
*   **Type Coercion:** Handles non-numeric dirty data (e.g., "pending", "N/A") in vital signs.

### B. Clinical Safety Engine (`src.logic`)
The system implements a medical logic check to detect **Systemic Inflammatory Response Syndrome (SIRS)**, a precursor to Sepsis. It flags patients meeting **≥2 of the following criteria**:
1.  **Temperature:** > 38°C or < 36°C
2.  **Heart Rate (HR):** > 90 bpm
3.  **Respiratory Rate (RR):** > 20 breaths/min
4.  **WBC:** > 12,000/µL or < 4,000/µL

### C. Cross-Domain Reconciliation (`src.logic`)
Automates the comparison between EDC and Lab data to ensure data integrity:
*   **Logic:** Triggers a query if `Blood_Draw_Performed == "Yes"` in EDC but **no matching record** exists in the Lab dataset for that Subject/Visit.

### D. Privacy & Compliance Layer (`src.privacy`)
A configurable privacy module sanitizes PII (Personally Identifiable Information) based on the active regulatory region:
*   **USA (HIPAA):** Maintains Safe Harbor "Limited Data Set" (Initials visible, Year of Birth visible).
*   **Alberta (HIA) / BC (PIPA) / Ontario (PHIPA):** Strict de-identification (Initials Redacted, DOB masked to Year-Month).
*   **Canada (PIPEDA):** Commercial standard (Full DOB/Initials redaction).

## 4. Usage

### Web Dashboard (Recommended)
Launch the Streamlit interface for an interactive experience:
```bash
streamlit run app.py
```
*   **Upload**: Drag and drop `raw_edc_visits.csv` and `raw_lab_results.csv`.
*   **Demo Mode**: Click "Use Demo Data" to generate a fresh synthetic dataset with built-in "dirty" data.
*   **Privacy Controls**: Select a Study Region to apply specific de-identification rules.
*   **Download**: Export the `Query_Log.xlsx` for site queries.

### CLI Pipeline
Run the full pipeline head-to-head in the terminal:
```bash
python main.py
```

## 5. Outputs
The system generates a tangible deliverable for site communication:
*   **`Query_Log.xlsx`**: An expertly formatted Excel file containing:
    *   **Tab 1 (Safety Flags):** High-risk patients requiring immediate medical review.
    *   **Tab 2 (Reconciliation):** Operational data gaps requiring site data entry.
    *   **Format:** Rows are highlighted and include auto-generated "Query Text" for the site.

## 6. Installation
1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run Tests:
    ```bash
    pytest tests/
    ```
