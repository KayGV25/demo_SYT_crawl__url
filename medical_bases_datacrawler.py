import requests
from bs4 import BeautifulSoup
import csv
import os
import pandas as pd


def get_expertise(hospital_id, macoso):
    url = "https://tracuu.medinet.org.vn/api/v1/public/kt_cskcb?page=1&results_per_page=30"
    payload = {"cosokcb_id": hospital_id, "macoso": macoso, "page": 1, "text": ""}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    datas = response.json().get("objects", [])
    expertise_list = []
    for data in datas:
        expertise_list.append(
            {
                "stt_thongtu": data.get("stt_thongtu"),
                "ten": data.get("ten")
            }
        )
    return "\n".join([f"{item['stt_thongtu']} {item['ten']}" for item in expertise_list])



def detail_data(detail_re, hospital_id):
    soup = BeautifulSoup(detail_re.text, "html.parser")
    # print(response.text)
    # Locate the main wrapper containing all hospital data
    wrapper = soup.find("div", class_="wrapper-facility")
    if not wrapper:
        return {"error": "Hospital data not found"}

    ma_co_so = wrapper.find('input', {'id': 'macoso'}).get("value")

    # Hospital Name
    hospital_name = wrapper.find("h3", class_="title-primary coso-ten pe-0")
    hospital_name = hospital_name.text.strip() if hospital_name else "N/A"

    # License Info
    license_info = wrapper.find("div", class_="item-hopital-date")
    license_number = "N/A"
    license_issuance_date = "N/A"

    if license_info:
        license_span = license_info.find("span", class_="fw-bold")
        if license_span:
            license_number = license_span.text.strip()
            # Extract text after span (e.g., " - Ngày cấp: 13/01/2014")
            text_after_span = license_span.next_sibling
            if text_after_span:
                # Extract just the date using split
                parts = text_after_span.split("Ngày cấp:")
                if len(parts) > 1:
                    license_issuance_date = parts[1].strip()

    # Address
    address_div = wrapper.find("div", class_="text-card")
    if address_div:
        address = address_div.text.strip().split("Chỉ đường")[0].strip()
    else:
        address = "N/A"
    
    # Extract additional details
    details_div = wrapper.find("div", class_="row pt-2")
    details = {
        "form_of_operation": "N/A",
        "scope_of_expertise": "N/A",
        "status": "N/A",
    }

    if details_div:
        for row in details_div.find_all(["div"], class_=["col-lg-12 col-12 py-1 row", "col-12 py-1 row"]):
            label = row.find("span", class_="fw-bold")
            value = row.find_all("span")[1] if row.find_all("span") else None
            if label and value:
                label_text = label.text.strip()
                value_text = value.text.strip()

                if "Hình thức tổ chức" in label_text:
                    details["form_of_operation"] = value_text
                elif "Phạm vi chuyên môn" in label_text:
                    details["scope_of_expertise"] = value_text
                elif "Tình trạng" in label_text:
                    details["status"] = value_text

    # Return dictionary
    return {
        "hospital_name": hospital_name,
        "address": address,
        "form_of_operation": details["form_of_operation"],
        "scope_of_expertise": details["scope_of_expertise"],
        "license_number": license_number,
        "file": " ",
        "ad_info": " ",
        "license_issuance_date": license_issuance_date,
        "status": details["status"].split("\n")[0],
        "technical_info": get_expertise(hospital_id, ma_co_so)
    }

# Step 1: Call API to search for hospitals
hospitals = []
url_search = "https://tracuu.medinet.org.vn/cosokhamchuabenh"
for i in range(6,11):
    payload = {"key_word": "răng hàm mặt", "page": i, "results_per_page": 10}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url_search, json=payload, headers=headers)
    if response.status_code == 200:
        html_content = response.text

        # Step 2: Parse the HTML and extract all hospital IDs
        soup = BeautifulSoup(html_content, "html.parser")
        hospital_tags = soup.find_all("h5", class_="card-title card-title-custom coso")

        hospital_ids = [tag["data-class"] for tag in hospital_tags if tag.has_attr("data-class")]
        # Step 3: Loop through each hospital ID and fetch its details
        for hospital_id in hospital_ids:
            url_detail = f"https://tracuu.medinet.org.vn/detail/{hospital_id}"
            detail_response = requests.get(url_detail)

            if detail_response.status_code == 200:
                hospitals.append(detail_data(detail_response, hospital_id))

            else:
                print(f"Failed to fetch details for hospital ID: {hospital_id}")

    else:
        print("Failed to fetch search results.")
        break

# csv_filename = "medical_bases.csv"
excel_filename = "medical_bases.xlsx"

if os.path.exists(excel_filename):
    os.remove(excel_filename)
df = pd.DataFrame(hospitals)
with pd.ExcelWriter(excel_filename, engine="xlsxwriter") as writer:
    df.to_excel(writer, sheet_name="Sheet1", index=False)
    
    # Get the workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    
    # Create a format for wrapped text
    wrap_format = workbook.add_format({"text_wrap": True})
    
    # Set all columns to use text wrap
    worksheet.set_column("A:Z", 30, wrap_format)  # Adjust column width if needed

print(f"Excel exported successfully: {excel_filename}")
# if os.path.exists(csv_filename):
#     os.remove(csv_filename)

# fieldnames = hospitals[0].keys()
# with open(csv_filename, mode="w", newline="", encoding="utf-8-sig") as file:
#     writer = csv.DictWriter(file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL, delimiter=",")

#     # Write header
#     writer.writeheader()

#     # Write rows
#     writer.writerows(hospitals)
# print(hospitals[0])
# print(f"Data successfully exported to {csv_filename}")


# url_detail = f"https://tracuu.medinet.org.vn/detail/92034a22-4a81-4eeb-8bf1-662c2ada3631"
# print(url_detail)
# detail_response = requests.get(url_detail)
# print(detail_data(detail_response))