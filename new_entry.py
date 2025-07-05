import datetime as dt
import pandas as pd
import streamlit as st

record_types = [
    "Weight",
    "Systolic Diastolic Pulse",
    "Glucose Ketone",
    "Glucose",
    "Ketone",
    "Cholesterol Triglycerides HDL LDL",
    "Cholesterol",
    "Uric Acid",
    "GE Fit Plus LN",
    "GE CS10G Body Composition",
    "GE CS10G",
    "Fora 6 BG HT HB",
]

selectbox_help = """
    * Weight: Body weight in pounds
    * Systolic Diastolic Pulse: Blood pressure mmgH and pulse in Beats/min
    * Glucose Ketone: Blood glucose in mg/dL and ketone mmol/L
    * Glucose: Blood glucose in mg/dL
    * Ketone: Blood ketone in mmol/L
    * Cholesterol Triglycerides HDL LDL: Lipid panel in mg/dL
    * Cholesterol: Total cholesterol in mg/dL
    * Uric Acid: Uric acid in mg/dL
    * GE Fit Plus LN: 13-in-1 body composition (Weight, Body Fat, BMI, Skeletal Muscle, Muscle Mass, Protein, BMR, Fat-Free Body Weight, Subcutaneous Fat, Visceral Fat, Body Water, Bone Mass, Metabolic Age)
    * GE CS10G Body Composition: 17-in-1 body composition (Weight, Body Water, Protein, Fat Mass, Bone Mass, Skeletal Muscle, Visceral Fat, Obesity, Weight Control, Fat Mass Control, Muscle Control, Health Assessment, Muscle Mass, BMR, Fat-Free Body Weight, Subcutaneous Fat, Metabolic Age)
    * GE CS10G: 9-in-1 body composition (Weight, Body Fat, BMI, Muscle Mass, BMR, Fat-Free Body Weight, Visceral Fat, Body Water, Bone Mass)
    * Fora 6 BG HT HB: Glucose in mg/dL, Haematocrit in %, and Haemoglobin in g/dL
    * Enter multiple values separated by space
"""

units = {
    "Weight": "lbs",
    "BMR": "kcal",
    "Systolic": "mmHg",
    "Diastolic": "mmHg",
    "Pulse": "Beats/min",
    "Glucose": "mg/dL",
    "Ketone": "mmol/L",
    "Cholesterol": "mg/dL",
    "Triglycerides": "mg/dL",
    "HDL": "mg/dL",
    "LDL": "mg/dL",
    "Uric Acid": "mg/dL",
    "Haematocrit": "%",
    "Haemoglobin": "g/dL",
}

def show():
    st.markdown("<b>New Entry</b>", unsafe_allow_html=True)
    with st.form("Add new entry"):
        cols = st.columns([1,1])
        with cols[0]: new_date = st.date_input("Date")
        with cols[1]: new_time = st.time_input("Time")  
        new_type = st.selectbox("Name", record_types, index=8, help=selectbox_help)
        new_value = st.text_input("Value(s)")  
        new_note = st.text_input("Note (optional)")  
        submitted = st.form_submit_button("Add")

    if submitted:
        try:
            names = new_type.split(" ")
            values = [float(v) for v in new_value.split(" ")]
            new_date = dt.datetime.combine(new_date, new_time)  # Combine date and time
            new_date = pd.to_datetime(new_date)
            if new_type == "GE Fit Plus LN":
                if len(values) != 13:
                    st.error("Please enter all 13 values for Weight, Body Fat, BMI, Skeletal Muscle, Muscle Mass, Protein, BMR, Fat-Free Body Weight, Subcutaneous Fat, Visceral Fat, Body Water, Bone Mass and Metabolic Age.")
                    st.stop()
                names = ["weight", "bdy_fat_pct", "bmi", "skl_msc_pct", "msc_mss", "prt_pct", 
                        "bmr", "ff_wgt", "sub_fat_pct", "vis_fat_idx", "bdy_wtr_pct", "bon_mss", "mtb_age"]
                kvs = dict(zip(names, values))
                # weight = body_fat + muscle_mass + bone_mass
                w = kvs["weight"]
                weight = { "Date": new_date, "Name": "Weight", "Value": w, "Units": units["Weight"], "Note": new_note }
                bmi = { "Date": new_date, "Name": "BMI", "Value": w*703/(5*12+6)**2, "Units": "", "Note": new_note }
                body_fat = { "Date": new_date, "Name": "Body Fat", "Value": w*kvs["bdy_fat_pct"]/100, "Units": units["Weight"], "Note": new_note }
                body_fat_pct = { "Date": new_date, "Name": "Body Fat %", "Value": kvs["bdy_fat_pct"], "Units": "%", "Note": new_note }
                subcutaneous_fat = { "Date": new_date, "Name": "Subcutaneous Fat", "Value": w*kvs["sub_fat_pct"]/100, "Units": units["Weight"], "Note": new_note }
                subcutaneous_fat_pct = { "Date": new_date, "Name": "Subcutaneous Fat %", "Value": kvs["sub_fat_pct"], "Units": "%", "Note": new_note }
                visceral_fat = { "Date": new_date, "Name": "Visceral Fat", "Value": w*(kvs["bdy_fat_pct"]-kvs["sub_fat_pct"])/100, "Units": units["Weight"], "Note": new_note }
                visceral_fat_pct = { "Date": new_date, "Name": "Visceral Fat %", "Value": kvs["bdy_fat_pct"]-kvs["sub_fat_pct"], "Units": "%", "Note": new_note }
                visceral_fat_index = { "Date": new_date, "Name": "Visceral Fat Index", "Value": kvs["vis_fat_idx"], "Units": "", "Note": new_note }
                muscle_mass = { "Date": new_date, "Name": "Muscle Mass", "Value": kvs["msc_mss"], "Units": units["Weight"], "Note": new_note }
                muscle_mass_pct = { "Date": new_date, "Name": "Muscle Mass %", "Value": 100*kvs["msc_mss"]/w, "Units": "%", "Note": new_note }
                skeletal_muscle = { "Date": new_date, "Name": "Skeletal Muscle", "Value": w*kvs["skl_msc_pct"]/100, "Units": units["Weight"], "Note": new_note }
                skeletal_muscle_pct = { "Date": new_date, "Name": "Skeletal Muscle %", "Value": kvs["skl_msc_pct"], "Units": "%", "Note": new_note }
                bone_mass = { "Date": new_date, "Name": "Bone Mass", "Value": kvs["bon_mss"], "Units": units["Weight"], "Note": new_note }
                bone_mass_pct = { "Date": new_date, "Name": "Bone Mass %", "Value": 100*kvs["bon_mss"]/w, "Units": "%", "Note": new_note }
                protein = { "Date": new_date, "Name": "Protein", "Value": w*kvs["prt_pct"]/100, "Units": units["Weight"], "Note": new_note }
                protein_pct = { "Date": new_date, "Name": "Protein %", "Value": kvs["prt_pct"], "Units": "%", "Note": new_note }
                body_water = { "Date": new_date, "Name": "Body Water", "Value": w*kvs["bdy_wtr_pct"]/100, "Units": units["Weight"], "Note": new_note }
                body_water_pct = { "Date": new_date, "Name": "Body Water %", "Value": kvs["bdy_wtr_pct"], "Units": "%", "Note": new_note }
                bmr = { "Date": new_date, "Name": "BMR", "Value": kvs["bmr"], "Units": units["BMR"], "Note": new_note }
                metabolic_age = { "Date": new_date, "Name": "Metabolic Age", "Value": kvs["mtb_age"], "Units": "Year", "Note": new_note }
                df = pd.concat([df, pd.DataFrame([weight, bmi, body_fat, body_fat_pct, subcutaneous_fat, subcutaneous_fat_pct, \
                                                visceral_fat, visceral_fat_pct, visceral_fat_index, muscle_mass, muscle_mass_pct, \
                                                skeletal_muscle, skeletal_muscle_pct, bone_mass, bone_mass_pct, protein, protein_pct, \
                                                body_water, body_water_pct, bmr, metabolic_age])], ignore_index=True)   
            elif new_type == "GE CS10G Body Composition":
                if len(values) != 17:
                    st.error("Please enter all 17 values.")
                    st.stop()
                names = ["weight", "bdy_wtr_pct", "prt_pct", "fat_mss_pct", "bon_mss_pct", "skl_msc", "vis_fat_idx", "obesity_pct", 
                        "wgt_ctrl", "fat_mss_ctrl", "msc_ctrl", "health_ass", "msc_mss", "bmr", "ff_wgt", "sub_fat_pct", "mtb_age"]
                kvs = dict(zip(names, values))
                # weight = body_fat + muscle_mass + bone_mass
                w = kvs["weight"]
                weight = { "Date": new_date, "Name": "Weight", "Value": w, "Units": units["Weight"], "Note": new_note }
                bmi = { "Date": new_date, "Name": "BMI", "Value": w*703/(5*12+6)**2, "Units": "", "Note": new_note }
                body_fat = { "Date": new_date, "Name": "Body Fat", "Value": w*kvs["fat_mss_pct"]/100, "Units": units["Weight"], "Note": new_note }
                body_fat_pct = { "Date": new_date, "Name": "Body Fat %", "Value": kvs["fat_mss_pct"], "Units": "%", "Note": new_note }
                subcutaneous_fat = { "Date": new_date, "Name": "Subcutaneous Fat", "Value": w*kvs["sub_fat_pct"]/100, "Units": units["Weight"], "Note": new_note }
                subcutaneous_fat_pct = { "Date": new_date, "Name": "Subcutaneous Fat %", "Value": kvs["sub_fat_pct"], "Units": "%", "Note": new_note }
                visceral_fat = { "Date": new_date, "Name": "Visceral Fat", "Value": w*(kvs["fat_mss_pct"]-kvs["sub_fat_pct"])/100, "Units": units["Weight"], "Note": new_note }
                visceral_fat_pct = { "Date": new_date, "Name": "Visceral Fat %", "Value": kvs["fat_mss_pct"]-kvs["sub_fat_pct"], "Units": "%", "Note": new_note }
                visceral_fat_index = { "Date": new_date, "Name": "Visceral Fat Index", "Value": kvs["vis_fat_idx"], "Units": "", "Note": new_note }
                muscle_mass = { "Date": new_date, "Name": "Muscle Mass", "Value": kvs["msc_mss"], "Units": units["Weight"], "Note": new_note }
                muscle_mass_pct = { "Date": new_date, "Name": "Muscle Mass %", "Value": 100*kvs["msc_mss"]/w, "Units": "%", "Note": new_note }
                skeletal_muscle = { "Date": new_date, "Name": "Skeletal Muscle", "Value": kvs["skl_msc"], "Units": units["Weight"], "Note": new_note }
                skeletal_muscle_pct = { "Date": new_date, "Name": "Skeletal Muscle %", "Value": 100*kvs["skl_msc"]/w, "Units": "%", "Note": new_note }
                bone_mass = { "Date": new_date, "Name": "Bone Mass", "Value": w*kvs["bon_mss_pct"]/100, "Units": units["Weight"], "Note": new_note }
                bone_mass_pct = { "Date": new_date, "Name": "Bone Mass %", "Value": kvs["bon_mss_pct"], "Units": "%", "Note": new_note }
                protein = { "Date": new_date, "Name": "Protein", "Value": w*kvs["prt_pct"]/100, "Units": units["Weight"], "Note": new_note }
                protein_pct = { "Date": new_date, "Name": "Protein %", "Value": kvs["prt_pct"], "Units": "%", "Note": new_note }
                body_water = { "Date": new_date, "Name": "Body Water", "Value": w*kvs["bdy_wtr_pct"]/100, "Units": units["Weight"], "Note": new_note }
                body_water_pct = { "Date": new_date, "Name": "Body Water %", "Value": kvs["bdy_wtr_pct"], "Units": "%", "Note": new_note }
                bmr = { "Date": new_date, "Name": "BMR", "Value": kvs["bmr"], "Units": units["BMR"], "Note": new_note }
                metabolic_age = { "Date": new_date, "Name": "Metabolic Age", "Value": kvs["mtb_age"], "Units": "Year", "Note": new_note }
                obesity_pct = { "Date": new_date, "Name": "Obesity %", "Value": kvs["obesity_pct"], "Units": "%", "Note": new_note }
                wgt_ctrl = { "Date": new_date, "Name": "Weight Control", "Value": kvs["wgt_ctrl"], "Units": "lbs", "Note": new_note }
                fat_mss_ctrl = { "Date": new_date, "Name": "Fat Mass Control", "Value": kvs["fat_mss_ctrl"], "Units": "lbs", "Note": new_note }
                msc_ctrl = { "Date": new_date, "Name": "Muscle Control", "Value": kvs["msc_ctrl"], "Units": "lbs", "Note": new_note }
                health_ass = { "Date": new_date, "Name": "Health Assessment", "Value": kvs["health_ass"], "Units": "Points", "Note": new_note }
                df = pd.concat([df, pd.DataFrame([weight, bmi, body_fat, body_fat_pct, subcutaneous_fat, subcutaneous_fat_pct, \
                                                visceral_fat, visceral_fat_pct, visceral_fat_index, muscle_mass, muscle_mass_pct, \
                                                skeletal_muscle, skeletal_muscle_pct, bone_mass, bone_mass_pct, protein, protein_pct, \
                                                body_water, body_water_pct, bmr, metabolic_age, \
                                                obesity_pct, wgt_ctrl, fat_mss_ctrl, msc_ctrl, health_ass])], ignore_index=True)   
            elif new_type == "GE CS10G":
                if len(values) != 9:
                    st.error("Please enter all 9 values for Weight, Body Fat, BMI, Muscle Mass, BMR, Fat-Free Body Weight, Visceral Fat, Body Water and Bone Mass.")
                    st.stop()
                names = ["weight", "bdy_fat_pct", "bmi", "msc_mss", "bmr", "ff_wgt", "vis_fat_idx", "bdy_wtr_pct", "bon_mss"]
                kvs = dict(zip(names, values))
                # weight = body_fat + muscle_mass + bone_mass
                w = kvs["weight"]
                weight = { "Date": new_date, "Name": "Weight", "Value": w, "Units": units["Weight"], "Note": new_note }
                bmi = { "Date": new_date, "Name": "BMI", "Value": w*703/(5*12+6)**2, "Units": "", "Note": new_note }
                body_fat = { "Date": new_date, "Name": "Body Fat", "Value": w*kvs["bdy_fat_pct"]/100, "Units": units["Weight"], "Note": new_note }
                body_fat_pct = { "Date": new_date, "Name": "Body Fat %", "Value": kvs["bdy_fat_pct"], "Units": "%", "Note": new_note }
                visceral_fat_index = { "Date": new_date, "Name": "Visceral Fat Index", "Value": kvs["vis_fat_idx"], "Units": "", "Note": new_note }
                muscle_mass = { "Date": new_date, "Name": "Muscle Mass", "Value": kvs["msc_mss"], "Units": units["Weight"], "Note": new_note }
                muscle_mass_pct = { "Date": new_date, "Name": "Muscle Mass %", "Value": 100*kvs["msc_mss"]/w, "Units": "%", "Note": new_note }
                bone_mass = { "Date": new_date, "Name": "Bone Mass", "Value": kvs["bon_mss"], "Units": units["Weight"], "Note": new_note }
                bone_mass_pct = { "Date": new_date, "Name": "Bone Mass %", "Value": 100*kvs["bon_mss"]/w, "Units": "%", "Note": new_note }
                body_water = { "Date": new_date, "Name": "Body Water", "Value": w*kvs["bdy_wtr_pct"]/100, "Units": units["Weight"], "Note": new_note }
                body_water_pct = { "Date": new_date, "Name": "Body Water %", "Value": kvs["bdy_wtr_pct"], "Units": "%", "Note": new_note }
                bmr = { "Date": new_date, "Name": "BMR", "Value": kvs["bmr"], "Units": units["BMR"], "Note": new_note }
                df = pd.concat([df, pd.DataFrame([weight, bmi, body_fat, body_fat_pct, \
                                                visceral_fat_index, muscle_mass, muscle_mass_pct, \
                                                bone_mass, bone_mass_pct, \
                                                body_water, body_water_pct, bmr])], ignore_index=True)   
            elif new_type == "Fora 6 BG HT HB":
                if len(values) != 3:
                    st.error("Please enter all 3 values for Glucose, Haematocrit, and Haemoglobin.")
                    st.stop()
                names = ["Glucose", "Haematocrit", "Haemoglobin"]
                kvs = dict(zip(names, values))            
                glucose = { "Date": new_date, "Name": "Glucose", "Value": kvs["Glucose"], "Units": units["Glucose"], "Note": new_note }
                haematocrit = { "Date": new_date, "Name": "Haematocrit", "Value": kvs["Haematocrit"], "Units": units["Haematocrit"], "Note": new_note }
                haemoglobin = { "Date": new_date, "Name": "Haemoglobin", "Value": kvs["Haemoglobin"], "Units": units["Haemoglobin"], "Note": new_note }
                df = pd.concat([df, pd.DataFrame([glucose, haematocrit, haemoglobin])], ignore_index=True)
            else:
                kvs = dict(zip(names, values))
                rows = []
                for name, value in kvs.items():
                    if name not in units: units[name] = ""  # Default unit if not specified
                    rows.append({ "Date": new_date, "Name": name, "Value": value, "Units": units[name], "Note": new_note })
                if "Weight" in names: # BMI = weight in lbs x 703 / (height in inches)^2
                    rows.append({ "Date": new_date, "Name": "BMI", "Value": kvs["Weight"]*703 / (5*12+6)**2, "Units": "", "Note": new_note })
                if "Glucose" in names and "Ketone" in names:
                    rows.append({ "Date": new_date, "Name": "Dr. Boz Ratio", "Value": kvs["Glucose"]/kvs["Ketone"], "Units": "", "Note": new_note })
                if "Cholesterol" in names and "HDL" in names:
                    rows.append({ "Date": new_date, "Name": "TC-HDL", "Value": kvs["TC"]-kvs["HDL"], "Units": units["Cholesterol"], "Note": new_note })
                    rows.append({ "Date": new_date, "Name": "TC/HDL", "Value": kvs["TC"]/kvs["HDL"], "Units": "", "Note": new_note })
                df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
            df.to_csv(f"data/{st.session_state['username']}/health_data.csv", index=False)  # Save updated DataFrame to CSV
            st.success("New data added!")
            st.rerun()  # Rerun the app to reflect the change
        except ValueError:
            st.error(f"Invalid value(s): {new_value}. Please enter valid number(s).")
