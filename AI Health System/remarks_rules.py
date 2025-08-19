# remark_rules.py

def generate_remarks(results):
    remarks = []
    result_dict = {r["Test"]: r for r in results}

    # ✅ WBC
    if "WHITE BLOOD CELLS" in result_dict:
        status = result_dict["WHITE BLOOD CELLS"]["Status"]
        if status == "High":
            remarks.append("High WBC: Possible bacterial infection or inflammation.")
        elif status == "Low":
            remarks.append("Low WBC: Possible viral infection or bone marrow issue.")

    # ✅ Differential counts
    diff_rules = {
        "NEUTROPHILS": {
            "High": "High Neutrophils: Suggests bacterial infection.",
            "Low": "Low Neutrophils: May indicate bone marrow suppression or severe infection."
        },
        "LYMPHOCYTES": {
            "High": "High Lymphocytes: Suggests viral infection or chronic illness.",
            "Low": "Low Lymphocytes: May indicate HIV, steroid use, or immune suppression."
        },
        "EOSINOPHILS": {
            "High": "High Eosinophils: Suggests allergy or parasitic infection.",
            "Low": "Low Eosinophils: Usually not significant but may indicate stress response."
        },
        "MONOCYTES": {
            "High": "High Monocytes: Suggests chronic infection (like TB).",
            "Low": "Low Monocytes: May indicate bone marrow suppression."
        },
        "BASOPHILS": {
            "High": "High Basophils: May indicate allergic reaction or rare disorder.",
            "Low": "Low Basophils: Usually not significant."
        }
    }

    for test, conditions in diff_rules.items():
        if test in result_dict:
            status = result_dict[test]["Status"]
            if status in conditions:
                remarks.append(conditions[status])

    # ✅ Hb + MCV + RBC + HCT
    if "HEMOGLOBIN" in result_dict:
        hb_status = result_dict["HEMOGLOBIN"]["Status"]
        if hb_status == "Low":
            anemia_msg = "Low Hb: Possible anemia."
            if "MEAN CORPUSCULAR VOLUME" in result_dict:
                mcv_status = result_dict["MEAN CORPUSCULAR VOLUME"]["Status"]
                if mcv_status == "Low":
                    anemia_msg = "Low Hb with low MCV: Iron deficiency anemia."
                elif mcv_status == "High":
                    anemia_msg = "Low Hb with high MCV: Vitamin B12/Folate deficiency anemia."
            remarks.append(anemia_msg)

        elif hb_status == "High":
            remarks.append("High Hb: Possible dehydration or polycythemia.")

    if "RED BLOOD CELLS" in result_dict:
        if result_dict["RED BLOOD CELLS"]["Status"] == "Low":
            remarks.append("Low RBC: Supports anemia or marrow issue.")
        elif result_dict["RED BLOOD CELLS"]["Status"] == "High":
            remarks.append("High RBC: May indicate dehydration or polycythemia.")

    if "HEMATOCRIT" in result_dict:
        if result_dict["HEMATOCRIT"]["Status"] == "Low":
            remarks.append("Low Hematocrit: Suggests anemia or blood loss.")
        elif result_dict["HEMATOCRIT"]["Status"] == "High":
            remarks.append("High Hematocrit: May indicate dehydration or polycythemia.")

    # ✅ Platelets
    if "PLATELETS" in result_dict:
        status = result_dict["PLATELETS"]["Status"]
        if status == "Low":
            remarks.append("Low Platelets: Risk of bleeding (seen in dengue, marrow disorders).")
        elif status == "High":
            remarks.append("High Platelets: Risk of clotting (possible inflammation or marrow disease).")

    if not remarks:
        remarks.append("CBC values are within normal ranges.")

    return list(dict.fromkeys(remarks))  # remove duplicates
