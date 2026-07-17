from utils.database import load_data

def get_recommendations(disease, age, weight, symptoms_text):
    """
    Evaluates inputs against recommendation rules.
    Returns matching recommendation record and a list of pediatric/weight warnings if applicable.
    """
    rules = load_data("recommendations")
    matched_rule = None
    
    # 1. First try matching by disease name (case insensitive)
    if disease:
        disease_clean = str(disease).strip().lower()
        for rule in rules:
            if rule.get("disease").lower() == disease_clean:
                matched_rule = rule
                break
                
    # 2. If no direct disease match, calculate symptom matching score
    if not matched_rule and symptoms_text:
        symptoms_list = [s.strip().lower() for s in symptoms_text.replace(",", " ").split() if len(s.strip()) > 2]
        best_score = 0
        for rule in rules:
            rule_symptoms = [s.lower() for s in rule.get("symptoms", [])]
            match_count = sum(1 for sym in symptoms_list if any(sym in r_sym for r_sym in rule_symptoms))
            
            if match_count > 0:
                score = match_count / len(rule_symptoms)
                if score > best_score:
                    best_score = score
                    matched_rule = rule
                    
    if not matched_rule:
        return None, []

    # 3. Generate safety/pediatric warning checks
    warnings = []
    try:
        age_val = int(age)
        if age_val < 12:
            warnings.append("⚠️ Pediatric Alert: Dosage may need adjustment for children under 12. Consult a Pediatrician.")
    except:
        pass

    try:
        weight_val = float(weight)
        if weight_val < 35:
            warnings.append("⚠️ Underweight Alert: Standard dosage is calibrated for normal adult weights (>45kg). Doctor supervision recommended.")
        elif weight_val > 150:
            warnings.append("⚠️ High Body Mass Alert: Dosage absorption rates may vary. Verify with cardiologist or general physician.")
    except:
        pass

    return matched_rule, warnings
