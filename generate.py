import os
import csv
import uuid
import hashlib
import qrcode
from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------
VERIFY_BASE_URL = "https://verify.savannahedc.com/?id="
TEMPLATE_BG = "templates/card_exec_bg.png" # Standard CR80 Card Background (1012x638 px)

# Output Folders
OUTPUT_CARDS = "output/printable_cards"
OUTPUT_QRS = "output/qrcodes"
os.makedirs(OUTPUT_CARDS, exist_ok=True)
os.makedirs(OUTPUT_QRS, exist_ok=True)

def generate_cards_from_csv(csv_filepath):
    sql_statements = []

    with open(csv_filepath, mode='r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # Generate unique random UUID for each person
            person_uuid = str(uuid.uuid4())
            staff_id = row['StaffID']
            full_name = row['FullName']
            title = row['Title']
            department = row['Department']
            cadre = row['Cadre']
            phone = row['Phone']
            photo_path = row['PhotoPath']
            issued_date = "2026-07-21"
            
            # Simple Security Hash
            sec_hash = hashlib.sha256(f"{person_uuid}:{staff_id}".encode()).hexdigest()[:12]

            # ------------------------------------------------------
            # 1. CREATE QR CODE
            # ------------------------------------------------------
            verify_url = f"{VERIFY_BASE_URL}{person_uuid}"
            qr = qrcode.QRCode(box_size=4, border=1)
            qr.add_data(verify_url)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="#0A1931", back_color="white").convert("RGBA")
            
            qr_img.save(f"{OUTPUT_QRS}/{staff_id}_qr.png")

            # ------------------------------------------------------
            # 2. CREATE PRINTABLE ID CARD
            # ------------------------------------------------------
            # Open template background exported from CorelDraw
            if os.path.exists(TEMPLATE_BG):
                card = Image.open(TEMPLATE_BG).convert("RGBA")
            else:
                # Fallback blank template if image is missing
                card = Image.new("RGBA", (1012, 638), "#0A1931")

            # Paste Staff Photo (Box size: 220 x 270 px)
            if os.path.exists(photo_path):
                photo = Image.open(photo_path).convert("RGBA").resize((220, 270))
                card.paste(photo, (60, 180))

            # Paste QR Code (Box size: 150 x 150 px)
            qr_resized = qr_img.resize((150, 150))
            card.paste(qr_resized, (790, 430))

            # Draw Text
            draw = ImageDraw.Draw(card)
            try:
                font_title = ImageFont.truetype("arial.ttf", 32)
                font_sub = ImageFont.truetype("arial.ttf", 22)
            except:
                font_title = font_sub = ImageFont.load_default()

            # Add Text to Card
            draw.text((310, 200), full_name.upper(), fill="#FFFFFF", font=font_title)
            draw.text((310, 250), title, fill="#5DB922", font=font_sub)
            draw.text((310, 290), f"ID: {staff_id}", fill="#FFFFFF", font=font_sub)

            # Save Composite Printable Card
            card_filename = f"{OUTPUT_CARDS}/{staff_id}_{full_name.replace(' ', '_')}.png"
            card.save(card_filename)

            # ------------------------------------------------------
            # 3. BUILD SQL SEED FOR DATABASE
            # ------------------------------------------------------
            r2_key = f"{person_uuid}.jpg"
            sql = f"INSERT INTO staff_directory (uuid, staff_id, full_name, designation, department, cadre, phone_number, photo_r2_key, issued_date, security_hash) VALUES ('{person_uuid}', '{staff_id}', '{full_name}', '{title}', '{department}', '{cadre}', '{phone}', '{r2_key}', '{issued_date}', '{sec_hash}');\n"
            sql_statements.append(sql)

            print(f" Ready: {full_name} ({staff_id})")

    # Write SQL commands to seed file
    with open("output/insert_staff.sql", "w") as f:
        f.writelines(sql_statements)

    print("\n Success! All cards generated in 'output/printable_cards'")
    print(" SQL Statements generated in 'output/insert_staff.sql'")

if __name__ == "__main__":
    run_batch_processing = generate_cards_from_csv("executives.csv")