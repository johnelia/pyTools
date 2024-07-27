import os
import mysql.connector
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

# Define your MySQL database connection parameters
db_config = {
    'user': 'root',
    'password': 'G00gl386!',
    'host': 'localhost',
    'database': 'software_inventory',
}

def fetch_data():
    engine = create_engine(
        f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}")
    query = "SELECT * FROM installed_software ORDER BY last_ran DESC"
    df = pd.read_sql(query, engine)
    return df

def compare_data(current_df, previous_df):
    # Print column names for debugging
    print("Current DataFrame columns:", current_df.columns)
    print("Previous DataFrame columns:", previous_df.columns)

    # Ensure the 'name' column exists in both DataFrames
    if 'name' not in current_df.columns or 'name' not in previous_df.columns:
        raise KeyError("The 'name' column is missing in one of the DataFrames.")

    merged_df = current_df.merge(previous_df, on='name', suffixes=('_current', '_previous'), how='outer',
                                 indicator=True)
    added = merged_df[merged_df['_merge'] == 'left_only']
    removed = merged_df[merged_df['_merge'] == 'right_only']
    changed = merged_df[(merged_df['_merge'] == 'both') &
                        ((merged_df['version_current'] != merged_df['version_previous']) |
                         (merged_df['publisher_current'] != merged_df['publisher_previous']) |
                         (merged_df['install_date_current'] != merged_df['install_date_previous']))]
    return added, removed, changed

def generate_html(current_df, added, removed, changed):
    current_df_html = current_df.to_html(index=False)
    added_html = added.to_html(index=False) if not added.empty else "<p>No software added.</p>"
    removed_html = removed.to_html(index=False) if not removed.empty else "<p>No software removed.</p>"
    changed_html = changed.to_html(index=False) if not changed.empty else "<p>No software changed.</p>"

    html_content = f"""
    <html>
    <head>
        <title>Software Inventory Report</title>
        <style>
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .added {{ background-color: #c8e6c9; }}
            .removed {{ background-color: #ffcdd2; }}
            .changed {{ background-color: #fff9c4; }}
        </style>
    </head>
    <body>
        <h1>Software Inventory Report</h1>
        <h2>Current Software List (Sorted by Last Ran Date)</h2>
        {current_df_html}
        <h2>Added Software</h2>
        {added_html}
        <h2>Removed Software</h2>
        {removed_html}
        <h2>Changed Software</h2>
        {changed_html}
    </body>
    </html>
    """

    filename = f"software_inventory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(filename, 'w') as file:
        file.write(html_content)

    print(f"Report generated: {filename}")

def main():
    # Fetch current data
    current_df = fetch_data()

    # Fetch previous data
    if os.path.exists('previous_software_inventory.csv'):
        previous_df = pd.read_csv('previous_software_inventory.csv')
        if previous_df.empty:
            previous_df = pd.DataFrame(columns=current_df.columns)
    else:
        previous_df = pd.DataFrame(columns=current_df.columns)

    # Compare data
    added, removed, changed = compare_data(current_df, previous_df)

    # Generate HTML report
    generate_html(current_df, added, removed, changed)

    # Save current data for the next comparison with a timestamp in the filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    current_csv_filename = f"software_inventory_{timestamp}.csv"
    current_df.to_csv(current_csv_filename, index=False)

    # Update the previous CSV for the next comparison
    current_df.to_csv('previous_software_inventory.csv', index=False)

if __name__ == "__main__":
    main()
