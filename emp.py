import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Configuration ---
DB_FILE = "dbh.xlsx"
OUTPUT_FILE = "Training_Responses.xlsx"

st.set_page_config(page_title="Participant Log System", layout="centered")

st.title("🏨 Participant Log System")
st.write("---")

# Load Master Data
if os.path.exists(DB_FILE):
    df_master = pd.read_excel(DB_FILE)
    df_master.columns = [str(c).strip() for c in df_master.columns]
    df_master['EMPLID'] = df_master['EMPLID'].astype(str).str.strip()
else:
    st.error(f"Master file '{DB_FILE}' not found on GitHub!")
    st.stop()

# EMPLID Input
emplid_input = st.text_input("Enter EMPLID:", placeholder="Type and press Enter")

if emplid_input:
    res = df_master[df_master['EMPLID'] == emplid_input.strip()]
    
    if not res.empty:
        emp_details = res.iloc[0]
        
        with st.form("checkin_form"):
            st.subheader(f"Welcome, {emp_details['NAME']}")
            st.text(f"Branch: {emp_details['Place of Posting']}")
            
            now = datetime.now()
            
            col1, col2 = st.columns(2)
            with col1:
                in_date = st.text_input("Check-in Date", value=now.strftime("%d-%m-%Y"))
                in_time = st.text_input("Check-in Time", value=now.strftime("%H:%M"))
            
            with col2:
                out_date = st.text_input("Check-out Date", value=now.strftime("%d-%m-%Y"))
                out_time = st.text_input("Check-out Time", value="00:00")
            
            st.markdown("---")
            stay_type = st.radio("Stay Details", ["Hostel", "Other"])
            stay_val = st.text_input("Room No / Hotel Details")
            
            submit = st.form_submit_button("SAVE LOG")
            
            if submit:
                # 17:15 Rule for check-out
                if out_time != "00:00":
                    try:
                        h, m = map(int, out_time.split(":"))
                        if h < 17 or (h == 17 and m < 15):
                            st.error("Check-out must be after 17:15!")
                            st.stop()
                    except:
                        st.error("Time format must be HH:MM")
                        st.stop()

                new_data = {
                    "EMPLID": emplid_input,
                    "Name": emp_details['NAME'],
                    "Branch": emp_details['Place of Posting'],
                    "Check-in Date": in_date,
                    "Check-in Time": in_time,
                    "Check-out Date": out_date,
                    "Check-out Time": out_time,
                    "Stay Details": f"{stay_type}({stay_val})",
                    "Update_Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Save to Excel
                if os.path.exists(OUTPUT_FILE):
                    df_resp = pd.read_excel(OUTPUT_FILE)
                else:
                    df_resp = pd.DataFrame()
                
                df_resp = pd.concat([df_resp, pd.DataFrame([new_data])], ignore_index=True)
                df_resp.to_excel(OUTPUT_FILE, index=False)
                st.success("Data Saved Successfully!")
    else:
        st.error("EMPLID not found!")
