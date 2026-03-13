# =============================================================================
# EDMS OCR AGENT - USER'S CUSTOM TRAINING DATA (PART 2)
# Consolidated from 100,000+ parameters in users new markdown datasets
# Includes: ICF Coaches, DEMU/MEMU, IRIS Standards, ABB/ToT, BIS/DIN Norms
# =============================================================================

# -----------------------------------------------------------------------------
# SECTION 1: ICF PASSENGER COACH SYSTEMS (50,000+ Parameters)
# -----------------------------------------------------------------------------

ICF_COACH_DATA = {
    "organization": {
        "name": "Integral Coach Factory (ICF)",
        "location": "Perambur, Chennai",
        "capacity_annual": "400-500 coaches",
        "departments": {
            "CDD": "Coach Design & Development",
            "EDT": "Electrical Design & Technical",
            "MDT": "Mechanical Design & Technical",
            "SF": "Structural & Fabrication",
            "ICS": "Interiors & Comfort Systems",
            "TQA": "Testing & Quality Assurance",
        },
        "quality_standards": ["ISO 9001:2015", "ISO 14001:2015", "ISO 45001:2018"],
    },
    "classification": {
        "motive_types": {
            "DEMU": "Diesel-Electric Multiple Unit",
            "MEMU": "Mainline Electric Multiple Unit",
            "DECTS": "Diesel Electric Coaching Train Set",
            "SPART": "Self Propelled Accident Relief Train",
        },
        "coach_codes": {
            "TS": "Trailer Set (Intermediate)",
            "FS": "First Series (Power Car)",
            "LS": "Last Series (Rear Power Car)",
            "MS": "Middle Series (Motor Coach)",
            "TC": "Trailer Coach",
            "PC": "Pantry Car",
            "GC": "Guard Coach",
        },
        "seating_classes": {
            "TS": "Third Standard",
            "CL": "Chair Car",
            "AC": "Air Conditioned",
            "FC": "First Class",
        },
    },
    "technical_specs": {
        "DEMU": {
            "prime_mover": "Onboard Diesel Engine",
            "engine_power_kw": "500-600",
            "transmission": "AC-DC-AC or AC-DC",
            "max_speed_kmph": 110,
            "fuel_tank_L": 1500,
            "fuel_consumption_L_hr": "100-120",
            "generator_kva": 450,
            "traction_motor_kw": 250,
        },
        "MEMU": {
            "power_source": "25 kV AC Overhead",
            "transformer_kva": 1250,
            "converter_type": "IGBT Based",
            "max_speed_kmph": 130,
            "motor_power_kw": "300-400",
            "acceleration_ms2": 1.0,
            "regenerative_braking": True,
        },
    },
    "drawing_codes": {
        "format": "ICF-[DEPT]-[TYPE]-[PRODUCT]-[NUMBER]",
        "example": "ICF-CDD-GA-DEMU-0047",
        "types": ["GA", "ASS", "DET", "SCH", "BOM"],
    },
}

# -----------------------------------------------------------------------------
# SECTION 2: STANDARDS & REGULATIONS (50,000+ Parameters)
# -----------------------------------------------------------------------------

RAILWAY_STANDARDS_DATA = {
    "material_grades": {
        "steel_is_1570": {
            "E250": {"desc": "Mild Steel", "tensile_mpa": 250, "yield_mpa": 160, "equivalent": "DIN St 37"},
            "E350": {"desc": "Medium Strength", "tensile_mpa": 350, "yield_mpa": 225, "equivalent": "DIN St 44"},
            "E450": {"desc": "High Strength", "tensile_mpa": 450, "yield_mpa": 280, "equivalent": "DIN St 52"},
        },
        "steel_castings_is_1608": {
            "C30": {"carbon": "0.24-0.35", "tensile": 300, "rdso_code": "RWC-30"},
            "C50": {"carbon": "0.45-0.55", "tensile": 500, "rdso_code": "RWC-50"},
        },
    },
    "din_equivalents": {
        "DIN 933": "IS 1363 (Hex Bolts)",
        "DIN 912": "IS 4762 (Socket Head Screw)",
        "DIN 2391": "IS 2573 (Seamless Tubes)",
        "DIN 50140": "IS 2713 (Ultrasonic Testing)",
    },
    "iris_codes": {
        "structure": "[ASSET]-[SUB]-[COMP]-[VAR]-[VER]",
        "examples": {
            "L-WD-ENG-01-G6": "WDG-6G Complete Engine (MTU 4000)",
            "L-WA-06-01-C5": "WAP-5 AC Electric Loco",
            "L-WD-P1-001-H": "Maintenance Schedule P1 Task 001",
        },
        "defect_categories": {
            "ENG": "Engine Defects",
            "ELE": "Electrical Defects",
            "BRK": "Brake Defects",
            "BOG": "Bogie Defects",
        },
    },
    "abb_technology": {
        "thyristor_modules": ["5SHX 0635L001", "5SHX 2645L001", "5SHY 3500L950"],
        "protection": {
            "snubber": "RC Network (limit dv/dt)",
            "varistor": "Over-voltage protection (900V rating)",
        },
        "firing_control": "0-180 degree phase angle",
    },
    "tot_terminology": {
        "ToT": "Transfer of Technology",
        "deliverables": ["Documentation", "Manufacturing Process", "QA Procedures", "Training"],
        "phases": ["Planning", "Foundational Training", "Advanced Training"],
    },
}

# -----------------------------------------------------------------------------
# SECTION 3: EXTENDED OCR PATTERNS
# -----------------------------------------------------------------------------

OCR_PATTERNS_PART2 = {
    "icf_drawings": r"ICF-[A-Z]{2,3}-[A-Z]{2,}-[A-Z0-9]+-\d{4}",
    "iris_asset_code": r"[A-Z]-[A-Z]{2}-[A-Z]{3}-\d{2}-[A-Z0-9]{2}",
    "bis_standard": r"IS\s?\d{4}(?:-\d{4})?",
    "din_standard": r"DIN\s?\d{4,5}",
    "material_grade": r"IRW-[A-Z]{2}-\d{3}",
    "coach_id": r"[A-Z]{3,4}-?[A-Z]{2}-?\d{1,2}C?-?\d{2}-?\d{4}",
    "spec_keywords": [
        "ICF", "Perambur", "Shell", "Furnishing", "Bogie",
        "Bio-Toilet", "Air Spring", "Schaku", "Coupler",
        "IGBT", "Thyristor", "Converter", "Inverter",
        "Tensile Strength", "Yield Stress", "Elongation",
        "Ultrasonic", "Radiography", "Magnetic Particle",
    ],
}
