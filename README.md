# GCP IAM Policy Auditor 🛡️

A simple, command-line Python script that helps you audit Identity and Access Management (IAM) policies in your Google Cloud Platform (GCP) projects. It compares the actual principals (users, service accounts) in a project against an approved "source of truth" maintained in an Excel spreadsheet to quickly identify unauthorized or missing access.

## Features

-   ✅ **Interactive Project Selection:** Automatically lists your available GCP projects and lets you choose which one to audit.
-   📋 **Fetches Live Data:** Uses `gcloud` commands to pull the current IAM policy for the selected project.
-   🔎 **Compares Against a Source of Truth:** Reads a list of authorized principals from a `.xlsx` file.
-   🚨 **Clear Discrepancy Reporting:** Generates a report showing:
    -   **Unauthorized Principals:** Accounts that have access in GCP but are *not* on the approved list.
    -   **Missing Principals:** Accounts that are on the approved list but do *not* have access in GCP.
-   📄 **Saves Policy for Auditing:** Exports the fetched IAM policy to a JSON file for your records.

---

## Prerequisites

Before you begin, ensure you have the following installed and configured:

1.  **Python 3:** The script is written in Python 3.
2.  **Google Cloud SDK:** The `gcloud` command-line tool must be installed and authenticated. You should be able to run `gcloud auth login` and `gcloud projects list` successfully.
3.  **Python Libraries:** The script depends on `pandas` and `openpyxl`.

---

## ⚙️ Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/mfakhriabdillah/iam-auditor.git](https://github.com/mfakhriabdillah/iam-auditor.git)
    cd iam-auditor
    ```

2.  **Install the required Python libraries:**
    
    ```bash
    pip install -r requirements.txt
    ```

---

## Configuration

1.  **Prepare Your Spreadsheet:**
    Create an Excel (`.xlsx`) file that will serve as your source of truth. It must contain a column listing the email addresses of all authorized users.

    

2.  **Update the Script (if necessary):**
    Open the `iam_audit.py` script and check the `EMAIL_COLUMN_NAME` variable at the top. Make sure its value matches the name of the column header in your spreadsheet.
    ```python
    # The name of the column in your Excel file that contains the list of authorized principals.
    # Please change this to match your spreadsheet.
    EMAIL_COLUMN_NAME = "authorized_email" 
    ```

---

## 🚀 How to Run

1.  Navigate to the directory where the script is located in your terminal.

2.  Run the script using Python:
    ```bash
    python iam_audit.py
    ```

3.  Follow the on-screen prompts:
    -   First, it will display a numbered list of your GCP projects. Enter the number of the project you wish to audit.
    -   Next, it will ask for the path to your spreadsheet file (e.g., `iam_list.xlsx`).

The script will then execute the audit and print the report directly to your terminal.
