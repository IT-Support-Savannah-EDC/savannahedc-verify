import os
import csv
import uuid
import hashlib
import shutil
import qrcode

# ------------------------------------------------------------------
# UPDATED CONFIGURATION
# ------------------------------------------------------------------
VERIFY_BASE_URL = "https://verifystaff.savannahedc.com/?id="

# Create Output Folders
os.makedirs("output/qrcodes", exist_ok=True)
os.makedirs("output/r2_photos", exist_ok=True)

sql_statements = []

# Process Test CSV
with open("test_staff.csv", mode="r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # 1. Generate unique random UUID
        test_uuid = str(uuid.uuid4())
        staff_id = row['StaffID']
        full_name = row['FullName']
        
        # 2. Build QR Code with new URL
        qr_url = f"{VERIFY_BASE_URL}{test_uuid}"
        qr = qrcode.QRCode(box_size=6, border=2)
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#0A1931", back_color="white")
        
        safe_staff_id = staff_id.replace('/', '_')
        qr_filename = f"output/qrcodes/{safe_staff_id}_QR.png"
        qr_img.save(qr_filename)

        # 3. Rename & Copy Photo for R2 Bucket Upload
        r2_photo_name = f"{test_uuid}.jpg"
        if os.path.exists(row['PhotoPath']):
            shutil.copy(row['PhotoPath'], f"output/r2_photos/{r2_photo_name}")

        # 4. Create SQL statement for Cloudflare D1
        sec_hash = hashlib.sha256(f"{test_uuid}:{staff_id}".encode()).hexdigest()[:12]
        sql = (
            f"INSERT INTO staff_directory "
            f"(uuid, staff_id, full_name, designation, department, cadre, phone_number, photo_r2_key, issued_date, security_hash) "
            f"VALUES ('{test_uuid}', '{staff_id}', '{full_name}', '{row['Title']}', '{row['Department']}', "
            f"'{row['Cadre']}', '{row['Phone']}', '{r2_photo_name}', '2026-07-22', '{sec_hash}');\n"
        )
        sql_statements.append(sql)

        print(f"✅ Created test record for: {full_name}")
        print(f"   ├─ QR Code: {qr_filename}")
        print(f"   ├─ Target URL: {qr_url}")
        print(f"   └─ R2 Photo File: output/r2_photos/{r2_photo_name}\n")

# Write SQL to file
with open("output/insert_test_data.sql", "w") as f:
    f.writelines(sql_statements)

print("🚀 Execution complete! Check the 'output' directory.")