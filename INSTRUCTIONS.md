# How to Update the Ward List Data

This guide explains how to download the current ward list from the Church website, clean it, and upload it to the Quiz App.

## Phase 1: Download Data from LCR

1.  Log in to **[LCR (Leader and Clerk Resources)](https://lcr.churchofjesuschrist.org/)** using your Church Account.
2.  On the menu, go to **Membership** → **Member List**.
3.  Click the **Print** button (usually a printer icon or "Print/Export" near the top right of the list).
4.  Choose **Export to CSV**.
    * *Note:* Do NOT choose PDF. We need the data file.
5.  Save the file to your computer (e.g., in your Downloads folder). It will usually be named `Member List.csv`.

---

## Phase 2: Clean the File

The file you downloaded contains "header information" (like the Ward Name and Date) at the top that prevents the computer from reading the names. We must remove this.

### Option A: Using the Automated Script (Recommended)
If your administrator provided the `clean_ward_list.py` script:
1.  Open your terminal or command prompt.
2.  Run the script:
    ```bash
    python3 clean_ward_list.py "path/to/Member List.csv"
    ```
3.  This will create a new file named **`ward_data_clean.csv`**. Use this file for the upload.

### Option B: Manual Cleaning (Excel/Numbers)
1.  Open the downloaded CSV file in Excel or Numbers.
2.  Highlight the top rows that contain the Ward Name, Stake Name, and Date.
3.  **Delete these rows.**
4.  Ensure the **very first row** (Row 1) now contains the column headers (e.g., "Preferred Name", "Household Position", "Phone", etc.).
5.  **Save/Export** the file as **CSV (Comma Delimited)**.

---

## Phase 3: Upload to the Quiz

1.  Open your web browser and go to the Quiz Website (ask your administrator for the link).
2.  Click the **Choose File** (or Browse) button.
3.  Select the **Cleaned** CSV file (e.g., `ward_data_clean.csv`).
4.  Click **Start Quiz**.

---

## ⚠️ Important Security Note
This file contains real member contact information.
* **Delete the CSV files** from your Downloads folder immediately after uploading.
* **Empty your Trash/Recycle Bin**.