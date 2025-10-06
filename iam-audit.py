import subprocess
import json
import sys
import pandas as pd

# --- Configuration ---
# The name of the column in your Excel file that contains the list of authorized principals.
# Please change this to match your spreadsheet.
EMAIL_COLUMN_NAME = "authorized_email" 

def run_shell_command(command):
    """A helper function to run a shell command and return its output."""
    try:
        # Runs the command. `check=True` will raise an error if the command fails.
        # `capture_output=True` and `text=True` capture the stdout/stderr as a string.
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing command: {e.cmd}")
        print(f"Error message: {e.stderr.strip()}")
        sys.exit(1) # Exit the script if a gcloud command fails

def select_gcp_project():
    """Lists all available GCP projects and prompts the user to select one."""
    print("🚀 Fetching available GCP projects...")
    command = 'gcloud projects list --format="value(projectId, name)" --sort-by=name'
    output = run_shell_command(command)
    
    # --- FIX IS HERE ---
    # Split each line only ONCE to correctly handle project names with spaces.
    # line.split(None, 1) splits the line into a maximum of two parts.
    projects = [line.split(None, 1) for line in output.splitlines()]
    
    if not projects:
        print("❌ No projects found. Please check your `gcloud` authentication.")
        sys.exit(1)

    # Display the projects in a numbered list
    print("\nPlease select a project to audit:")
    # Now this loop will work correctly because each item in 'projects' is a list of 2 elements.
    for i, (project_id, name) in enumerate(projects):
        print(f"  {i + 1}. {name} ({project_id})")

    # Get user's choice
    while True:
        try:
            choice = int(input(f"\nEnter number (1-{len(projects)}): "))
            if 1 <= choice <= len(projects):
                selected_project_id = projects[choice - 1][0]
                print(f"✅ You selected: {selected_project_id}\n")
                return selected_project_id
            else:
                print("Invalid number, please try again.")
        except ValueError:
            print("Please enter a valid number.")


def get_and_save_iam_policy(project_id):
    """Fetches the IAM policy for a project and saves it to a JSON file."""
    print(f"📋 Fetching IAM policy for project '{project_id}'...")
    command = f'gcloud projects get-iam-policy "{project_id}" --format="json"'
    iam_policy_json = run_shell_command(command)
    
    # Parse the JSON string into a Python dictionary
    iam_policy = json.loads(iam_policy_json)
    
    # Save the policy to a file for auditing purposes
    output_filename = f"{project_id}-iam-policy.json"
    with open(output_filename, "w") as f:
        json.dump(iam_policy, f, indent=2)
    print(f"📄 IAM policy saved to '{output_filename}'")
    
    return iam_policy

def extract_principals_from_policy(iam_policy):
    """Extracts all unique principals from an IAM policy object."""
    # Using a set to automatically handle duplicates
    principals = set()
    for binding in iam_policy.get("bindings", []):
        for member in binding.get("members", []):
            principals.add(member)
    return principals

def load_principals_from_spreadsheet(filepath):
    """Loads the source of truth principals from an Excel file."""
    try:
        print(f"\n📖 Reading authorized principals from '{filepath}'...")
        df = pd.read_excel(filepath)
        
        if EMAIL_COLUMN_NAME not in df.columns:
            print(f"❌ Error: Column '{EMAIL_COLUMN_NAME}' not found in the spreadsheet.")
            print(f"Available columns are: {list(df.columns)}")
            sys.exit(1)
            
        # Get principals, remove any empty rows, and convert to a set
        # We add the "user:" prefix to match the format from GCP IAM
        principals = set("user:" + email.strip() for email in df[EMAIL_COLUMN_NAME].dropna())
        print(f"Found {len(principals)} authorized principals in the spreadsheet.")
        return principals
    except FileNotFoundError:
        print(f"❌ Error: The file '{filepath}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An error occurred while reading the Excel file: {e}")
        sys.exit(1)

def main():
    """Main function to orchestrate the IAM audit."""
    project_id = select_gcp_project()
    
    # Get the file path for the source of truth
    spreadsheet_path = input("Enter the path to your spreadsheet (e.g., 'iam_list.xlsx'): ")
    
    # --- Main Logic ---
    iam_policy = get_and_save_iam_policy(project_id)
    
    # Extract principals from both sources
    gcp_principals = extract_principals_from_policy(iam_policy)
    authorized_principals = load_principals_from_spreadsheet(spreadsheet_path)

    print("\n🔄 Comparing GCP IAM principals with the spreadsheet...")

    # --- The Comparison ---
    # Use set difference to find principals in GCP that are NOT in the spreadsheet
    unauthorized_principals = gcp_principals - authorized_principals
    
    # (Optional but useful) Find principals in the spreadsheet who are NOT in GCP
    missing_principals = authorized_principals - gcp_principals

    print("\n" + "="*50)
    print("             IAM AUDIT REPORT")
    print("="*50)
    
    if not unauthorized_principals:
        print("\n✅ SUCCESS: No unauthorized principals found in the project!")
    else:
        print(f"\n🚨 ALERT: Found {len(unauthorized_principals)} unauthorized principals in GCP!")
        print("   These principals exist in the GCP project but are NOT in the spreadsheet:")
        # Sort the list for clean, readable output
        for principal in sorted(list(unauthorized_principals)):
            print(f"   - {principal}")
            
    if missing_principals:
        print("\nℹ️ INFO: The following principals are in the spreadsheet but are missing from the GCP project:")
        for principal in sorted(list(missing_principals)):
            print(f"   - {principal}")

    print("\n" + "="*50)
    print("Audit complete.")

if __name__ == "__main__":
    main()