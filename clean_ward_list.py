import csv
import os
import sys

def clean_lcr_export(input_filename, output_filename="ward_data_clean.csv"):
    """
    Reads a raw LCR export, finds the actual header row, 
    removes the metadata at the top, and saves a clean CSV.
    """
    
    # The column name we look for to identify the start of real data.
    # LCR almost always starts with "Preferred Name" or "Individual Name".
    HEADER_ANCHOR = "Preferred Name"

    print(f"Processing: {input_filename}...")

    if not os.path.exists(input_filename):
        print(f"❌ Error: The file '{input_filename}' was not found.")
        return

    try:
        # 'utf-8-sig' handles the BOM (Byte Order Mark) often found in Excel exports
        with open(input_filename, 'r', encoding='utf-8-sig', errors='replace') as f_in:
            reader = csv.reader(f_in)
            all_rows = list(reader)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return

    # 1. Find the Header Row
    start_index = -1
    for i, row in enumerate(all_rows):
        # We check if our anchor text is in any column in this row
        if HEADER_ANCHOR in row:
            start_index = i
            break

    if start_index == -1:
        print(f"❌ Error: Could not find the header row.")
        print(f"   (I was looking for a column named '{HEADER_ANCHOR}')")
        return

    # 2. Slice the data (Keep everything from the header row down)
    clean_rows = all_rows[start_index:]
    
    # 3. Optional: Filter logic (e.g., remove empty rows)
    # This keeps only rows that actually have a name in the anchor column
    anchor_col_index = clean_rows[0].index(HEADER_ANCHOR)
    final_rows = [clean_rows[0]] # Add header
    
    for row in clean_rows[1:]:
        if len(row) > anchor_col_index and row[anchor_col_index].strip():
            final_rows.append(row)

    # 4. Save to new file
    try:
        with open(output_filename, 'w', newline='', encoding='utf-8') as f_out:
            writer = csv.writer(f_out)
            writer.writerows(final_rows)
        
        print(f"✅ Success!")
        print(f"   Cleaned file saved as: {output_filename}")
        print(f"   Found {len(final_rows) - 1} members.")
        
    except PermissionError:
        print(f"❌ Error: Could not write to {output_filename}. Is it open in Excel?")

if __name__ == "__main__":
    # If dragged and dropped, or run with arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        clean_lcr_export(input_file)
    else:
        # Interactive mode
        target = input("Enter the name of your downloaded CSV file (e.g. MemberList.csv): ").strip()
        clean_lcr_export(target)