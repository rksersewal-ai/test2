"""
EDMS OCR Agent - Railway Document Intelligence
Enhanced with comprehensive Indian Railways training data (January 2026)
"""
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum

# Import comprehensive training data
from .training_data import (
    LOCOMOTIVE_DATABASE,
    MAINTENANCE_SCHEDULES,
    RDSO_SPECIFICATIONS,
    PRODUCTION_UNITS,
    DOCUMENT_TYPES,
    RAILWAY_ABBREVIATIONS,
    TECHNICAL_PARAMETERS,
    STRATEGIC_INITIATIVES_2026,
)

# Import extended drawing parameters
from .training_data_drawings import (
    DRAWING_NUMBERING_SYSTEMS,
    DRAWING_SHEET_STANDARDS,
    LOCOMOTIVE_COMPONENT_DRAWINGS,
    DRAWING_TYPES,
    MATERIAL_SPECIFICATIONS,
    TOLERANCE_STANDARDS,
    WELDING_SPECIFICATIONS,
)

# Import specifications, tender terms, and DETC data
from .training_data_specs import (
    RDSO_SPECIFICATION_DATABASE,
    TENDER_TERMINOLOGY,
    PRODUCTION_UNITS_EXTENDED,
    DETC_SPECIFICATIONS,
    DETC_COMPONENT_DRAWINGS,
    TECHNICAL_PARAMETERS as TECH_PARAMS_EXT,
    ABBREVIATIONS_EXTENDED,
)

# Import user's custom 70K+ parameter training data
from .training_data_user import (
    LOCOMOTIVE_SPECS_EXTENDED,
    ENGINE_PARAMETERS,
    IGBT_SPECIFICATIONS,
    DRAWING_STANDARDS,
    TENDER_FRAMEWORK,
    ABBREVIATIONS_USER,
    OCR_TRAINING_PATTERNS,
    PERFORMANCE_KPIS,
)

# Import user's additional 100K+ parameter training data (Part 2)
from .training_data_user_part2 import (
    ICF_COACH_DATA,
    RAILWAY_STANDARDS_DATA,
    OCR_PATTERNS_PART2,
)

# Import Engineering Drawing specialized training data (10K+ params)
from .training_data_engineering import (
    TITLE_BLOCK_PATTERNS,
    BOM_HEADERS,
    BOM_ROW_PATTERN,
    GDT_SYMBOLS,
    ADVANCED_TECH_TERMS,
    NOTE_KEYWORDS,
    DRAWING_CLASSIFICATION_RULES,
)


# =============================================================================
# DOCUMENT TYPE ENUMERATION
# =============================================================================

class DocumentType(Enum):
    MAINTENANCE_SCHEDULE = "Maintenance Schedule"
    SPECIAL_MAINTENANCE_INSTRUCTION = "Special Maintenance Instruction (SMI)"
    TECHNICAL_SPECIFICATION = "Technical Specification"
    ENGINEERING_DRAWING = "Engineering Drawing"
    JOB_CARD = "Job Card"
    SERVICE_RECORD = "Service Record"
    ENGINEERING_CHANGE = "Engineering Change"
    TECHNICAL_BULLETIN = "Technical Bulletin"
    CAMTECH_BULLETIN = "CAMTECH Bulletin"
    STR_DOCUMENT = "Schedule of Technical Requirements"
    IGBT_COMPONENT_MANUAL = "IGBT Component Manual"
    KAWACH_ATP_SYSTEM = "Kawach ATP System"
    DPWCS_MULTI_UNIT = "DPWCS Multi-Unit"
    EOTT_GUARD_FREE = "EOTT Guard-Free"
    BATTERY_ELECTRIC = "Battery-Electric"
    GREEN_HYDROGEN = "Green Hydrogen"
    TOT_DOCUMENT = "Transfer of Technology"
    RDSO_STANDARD = "RDSO Standard/Specification"
    DETC_DOCUMENT = "DETC (Diesel Electric Tower Car)"
    TENDER_DOCUMENT = "Tender/Procurement Document"
    OHE_DOCUMENT = "OHE (Overhead Equipment)"
    PASSENGER_COACH = "Passenger Coach (ICF/DEMU/MEMU)"
    STANDARD_REGULATION = "Standard/Regulation (IS/DIN/BIS/IRIS)"
    UNKNOWN = "Unknown"


# =============================================================================
# EXTRACTION RESULT DATACLASS
# =============================================================================

@dataclass
class ExtractionResult:
    document_type: str
    confidence_score: float
    locomotive_info: Dict[str, Any]
    maintenance_info: Dict[str, Any]
    references: Dict[str, List[str]]
    components: List[str]
    system_data: Dict[str, Any]
    abbreviations_found: Dict[str, str]
    rdso_specs_matched: List[str]
    production_units_referenced: List[str]
    strategic_initiatives: List[str]
    summary: str
    suggested_links: List[Dict[str, str]]
    coach_info: Dict[str, Any] = None
    standards: List[Dict[str, Any]] = None
    drawing_info: Dict[str, Any] = None
    advanced_tech: List[str] = None
    tender_info: List[Dict[str, str]] = None


# =============================================================================
# OCR PREPROCESSOR
# =============================================================================

class OCRPreprocessor:
    """Normalize and correct common OCR errors specific to railway documents"""

    COMMON_MISREADINGS = {
        r'\bO(?=[A-Z]-\d)': '0',
        r'(?<=\d)O(?=\d)': '0',
        r'(?<=[A-Z])l(?=\d)': '1',
        r'(?<=[A-Z])I(?=\d)': '1',
        r'\bROS0\b': 'RDSO',
        r'\bCLvV\b': 'CLW',
        r'\bDLvV\b': 'DLW',
        r'\bDMvV\b': 'DMW',
        r'([A-Z]{2,4})\s+(\d{2})': r'\1-\2',
        r'([A-Z]{2,4})\s*-\s*(\d)': r'\1-\2',
        r'(\d+)\s*[hH][pP]': r'\1 HP',
        r'(\d+)\s*[kK][wW]': r'\1 kW',
        r'(\d+)\s*[kK][mM]/[hH]': r'\1 km/h',
    }

    @staticmethod
    def normalize_text(text: str) -> str:
        normalized = text
        for pattern, replacement in OCRPreprocessor.COMMON_MISREADINGS.items():
            try:
                normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
            except re.error:
                continue
        return re.sub(r'\s+', ' ', normalized).strip()


# =============================================================================
# DOCUMENT CLASSIFIER
# =============================================================================

class DocumentClassifier:
    """Classify documents using training data patterns"""

    @staticmethod
    def classify(text: str) -> Tuple[str, float]:
        scores = {}

        # Check against DOCUMENT_TYPES from training data
        for doc_code, doc_info in DOCUMENT_TYPES.items():
            score = 0
            for pattern in doc_info.get('patterns', []):
                if re.search(pattern, text, re.IGNORECASE):
                    score += 3
            if 'numbering' in doc_info:
                if re.search(doc_info['numbering'], text, re.IGNORECASE):
                    score += 5
            if score > 0:
                scores[doc_info['name']] = score

        classification_rules = {
            DocumentType.MAINTENANCE_SCHEDULE: {
                'keywords': ['Maintenance Schedule', 'Periodic Overhaul', 'POH', 'IOH', 'Service', 'Interval'],
                'codes': [r'[PT][1-5]', r'M-?\d+', r'POH', r'IOH', r'AOH'],
            },
            DocumentType.SPECIAL_MAINTENANCE_INSTRUCTION: {
                'keywords': ['SMI', 'Special Maintenance', 'Instruction', 'CAMTECH'],
                'codes': [r'SMI[/-]', r'CAMTECH[/-]'],
            },
            DocumentType.IGBT_COMPONENT_MANUAL: {
                'keywords': ['IGBT', 'Thermal', 'Module', 'Temperature', 'Insulated Gate'],
                'patterns': [r'(?:60|75|80|85|95)\xb0C', r'thyristor', r'converter'],
            },
            DocumentType.KAWACH_ATP_SYSTEM: {
                'keywords': ['Kawach', 'ATP', 'SIL-4', 'SPAD', 'Automatic Train Protection', 'TCAS'],
                'codes': [r'v4\.0', r'RDSO/SPN/196'],
            },
            DocumentType.DPWCS_MULTI_UNIT: {
                'keywords': ['DPWCS', 'Multi-Unit', 'Wireless', 'Distributed Power'],
                'codes': [r'406.*MHz', r'407.*MHz', r'UHF'],
            },
            DocumentType.EOTT_GUARD_FREE: {
                'keywords': ['EOTT', 'Guard-Free', 'End of Train', 'Telemetry'],
            },
            DocumentType.BATTERY_ELECTRIC: {
                'keywords': ['Battery-Electric', 'Medha E6', 'Zero-Emission', 'Battery Shunter'],
            },
            DocumentType.GREEN_HYDROGEN: {
                'keywords': ['Green Hydrogen', 'H2', 'Hydrogen-Hybrid', 'Fuel Cell'],
            },
            DocumentType.TOT_DOCUMENT: {
                'keywords': ['Transfer of Technology', 'ToT', 'Technology Transfer', 'Make in India'],
                'codes': [r'GE\s+Transportation', r'Alstom', r'Adtranz', r'ABB'],
            },
            DocumentType.RDSO_STANDARD: {
                'keywords': ['RDSO', 'Research Designs', 'Standards Organisation', 'Specification'],
                'codes': [r'RDSO/[A-Z]+/[A-Z\d]+/\d+', r'SPN/\d+'],
            },
            DocumentType.ENGINEERING_DRAWING: {
                'keywords': ['Drawing', 'Drg', 'Assembly', 'Detail', 'Revision'],
                'codes': [r'Drg\.?\s*No\.?', r'Rev\s*[A-Z]', r'CLW/', r'DLW/', r'DMW/', r'RDSO/'],
            },
            DocumentType.DETC_DOCUMENT: {
                'keywords': ['DETC', 'Diesel Electric Tower Car', 'Tower Car', 'OHE Maintenance',
                             'Lifting Platform', 'Kirloskar Cummins', 'VTA-1710L', 'Telescopic Platform'],
                'codes': [r'DETC-', r'RDSO/ELRS/SPEC/DETC'],
            },
            DocumentType.TENDER_DOCUMENT: {
                'keywords': ['Tender', 'NIT', 'Notice Inviting', 'EOI', 'Expression of Interest',
                             'RFP', 'RFQ', 'EMD', 'Earnest Money', 'Bid', 'Quotation', 'GeM'],
                'codes': [r'NIT/', r'EOI/', r'RFP/', r'L1', r'IREPS', r'GEM\s*ID'],
            },
            DocumentType.OHE_DOCUMENT: {
                'keywords': ['OHE', 'Overhead Equipment', 'Contact Wire', 'Catenary', 'Pantograph',
                             'TSS', 'Traction Sub-Station', 'Section Insulator', 'Mast'],
                'codes': [r'25\s*kV', r'RDSO/EL/OHE'],
            },
            DocumentType.PASSENGER_COACH: {
                'keywords': ['ICF', 'Integral Coach Factory', 'Passenger Coach', 'Shell',
                             'Furnishing', 'Chair Car', 'Sleeper', 'DEMU', 'MEMU'],
                'codes': [r'ICF/\d+', r'DEMU/\d+', r'MEMU/\d+'],
            },
            DocumentType.STANDARD_REGULATION: {
                'keywords': ['Standard', 'Regulation', 'IS', 'DIN', 'BIS', 'IRIS', 'ISO'],
                'codes': [r'IS\s?\d{4}', r'DIN\s?\d{4}', r'BIS', r'IRIS\s?Code', r'ISO\s?\d{4}'],
            },
        }

        for doc_type, rules in classification_rules.items():
            score = scores.get(doc_type.value, 0)
            if 'keywords' in rules:
                for kw in rules['keywords']:
                    if re.search(re.escape(kw), text, re.IGNORECASE):
                        score += 2
            if 'codes' in rules:
                for code in rules['codes']:
                    if re.search(code, text, re.IGNORECASE):
                        score += 3
            if 'patterns' in rules:
                for pat in rules['patterns']:
                    if re.search(pat, text, re.IGNORECASE):
                        score += 2
            if score > 0:
                scores[doc_type.value] = score

        if not scores:
            return DocumentType.UNKNOWN.value, 0.0

        best_type = max(scores, key=scores.get)
        confidence = min(scores[best_type] / 15.0, 1.0)
        return best_type, confidence


# =============================================================================
# INFORMATION EXTRACTOR
# =============================================================================

class InformationExtractor:
    """Extract structured information using training data"""

    @staticmethod
    def extract(text: str, doc_type_str: str) -> Dict:
        data = {
            'locomotive': {},
            'maintenance': {},
            'references': {},
            'components': [],
            'system': {},
            'abbreviations': {},
            'rdso_specs': [],
            'production_units': [],
            'initiatives': [],
            'suggested_links': [],
            'coach_info': {},
            'standards': [],
            'drawing_info': {},
            'advanced_tech': [],
        }

        # 1. Locomotive Extraction
        for loco_model, loco_info in LOCOMOTIVE_DATABASE.items():
            patterns = [re.escape(loco_model)]
            if 'aliases' in loco_info:
                patterns.extend([re.escape(a) for a in loco_info['aliases']])
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    data['locomotive'] = {
                        'model': loco_model,
                        'type': loco_info.get('type'),
                        'power_hp': loco_info.get('power_hp'),
                        'power_kw': loco_info.get('power_kw'),
                        'manufacturer': loco_info.get('manufacturer'),
                        'tot_partner': loco_info.get('tot_partner'),
                        'use_case': loco_info.get('use_case'),
                    }
                    if loco_model in LOCOMOTIVE_SPECS_EXTENDED:
                        data['locomotive']['extended_specs'] = LOCOMOTIVE_SPECS_EXTENDED[loco_model]
                    data['suggested_links'].append({
                        'type': 'LOCOMOTIVE',
                        'text': loco_model,
                        'query': f"documents:locomotive={loco_model}",
                    })
                    break

        serial_match = re.search(r'(?:Serial|No\.|#|Loco No\.?)\s*[:.]?\s*(\d{5,6})', text, re.IGNORECASE)
        if serial_match:
            data['locomotive']['serial'] = serial_match.group(1)

        # 2. Maintenance Schedule Extraction
        for sched_code, sched_info in MAINTENANCE_SCHEDULES.items():
            if re.search(re.escape(sched_code), text, re.IGNORECASE):
                data['maintenance'] = {
                    'schedule_code': sched_code,
                    'name': sched_info.get('name'),
                    'scope': sched_info.get('scope'),
                    'periodicity_days': sched_info.get('periodicity_days'),
                    'location': sched_info.get('location'),
                }
                data['suggested_links'].append({
                    'type': 'MAINTENANCE',
                    'text': f"{sched_code} - {sched_info.get('name', '')}",
                    'query': f"documents:schedule={sched_code}",
                })
                break

        # 3. RDSO Specifications
        for spec_key, spec_info in RDSO_SPECIFICATIONS.items():
            spec_no = spec_info.get('spec_no', '')
            if spec_no and re.search(re.escape(spec_no), text, re.IGNORECASE):
                data['rdso_specs'].append({'key': spec_key, 'spec_no': spec_no, 'version': spec_info.get('version')})
                data['suggested_links'].append({
                    'type': 'RDSO_SPEC',
                    'text': f"{spec_key}: {spec_no}",
                    'query': f"documents:rdso={spec_no}",
                })
            if re.search(re.escape(spec_key), text, re.IGNORECASE):
                if not any(s['key'] == spec_key for s in data['rdso_specs']):
                    data['rdso_specs'].append({'key': spec_key})

        # 4. Production Units
        for unit_code, unit_info in PRODUCTION_UNITS.items():
            if re.search(r'\b' + re.escape(unit_code) + r'\b', text, re.IGNORECASE):
                data['production_units'].append({
                    'code': unit_code,
                    'name': unit_info.get('name'),
                    'location': unit_info.get('location'),
                })
            full_name = unit_info.get('name', '')
            if full_name and re.search(re.escape(full_name), text, re.IGNORECASE):
                if not any(u['code'] == unit_code for u in data['production_units']):
                    data['production_units'].append({
                        'code': unit_code,
                        'name': full_name,
                        'location': unit_info.get('location'),
                    })

        # 5. Document Reference Extraction
        smi_matches = re.findall(r'SMI[/-]?([A-Z]*)[/-]?(\d{4})[/-](\d{2,4})', text, re.IGNORECASE)
        if smi_matches:
            data['references']['smi'] = [f"SMI/{m[0]}/{m[1]}/{m[2]}" for m in smi_matches]
        jc_matches = re.findall(r'JC[/-]?(\d{4})[/-](\d{2,4})', text, re.IGNORECASE)
        if jc_matches:
            data['references']['job_card'] = [f"JC/{m[0]}/{m[1]}" for m in jc_matches]
        rdso_matches = re.findall(r'RDSO[/-]([A-Z]+)[/-]([A-Z\d]+)[/-](\d+)', text, re.IGNORECASE)
        if rdso_matches:
            data['references']['rdso_docs'] = [f"RDSO/{m[0]}/{m[1]}/{m[2]}" for m in rdso_matches]
        data['references']['dates'] = re.findall(r'(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})', text)

        # 6. Abbreviations
        all_abbreviations = {**RAILWAY_ABBREVIATIONS, **ABBREVIATIONS_USER}
        for abbr, full_form in all_abbreviations.items():
            if re.search(r'\b' + re.escape(abbr) + r'\b', text):
                data['abbreviations'][abbr] = full_form

        # 7. Components
        component_patterns = [
            ('IGBT', 'Insulated Gate Bipolar Transistor'),
            ('GTO', 'Gate Turn-Off Thyristor'),
            ('Main Generator', 'Main Generator'),
            ('Main Transformer', 'Main Transformer'),
            ('Alternator', 'Alternator'),
            ('Compressor', 'Compressor'),
            ('Brake Cylinder', 'Brake Cylinder'),
            ('Traction Motor', 'Traction Motor'),
            ('Pantograph', 'Pantograph'),
            ('Turbocharger', 'Turbocharger'),
            ('Governor', 'Governor'),
            ('Bogie', 'Bogie'),
            ('Wheelset', 'Wheelset'),
        ]
        for comp_short, comp_full in component_patterns:
            if re.search(re.escape(comp_short), text, re.IGNORECASE):
                data['components'].append(comp_full)

        # 8. Strategic Initiatives
        for initiative in STRATEGIC_INITIATIVES_2026.keys():
            data['initiatives'].append(initiative)

        # 8a. Engine & IGBT Parameters
        if 'ENGINE' in doc_type_str.upper() or 'LOCO' in doc_type_str.upper():
            for param, details in ENGINE_PARAMETERS.items():
                normalized_param = param.replace('_', r'[\s_-]*')
                if re.search(normalized_param, text, re.IGNORECASE):
                    if 'system_details' not in data['system']:
                        data['system']['system_details'] = {}
                    data['system']['system_details'][param] = details

        if 'IGBT' in doc_type_str.upper() or 'CONVERTER' in text.upper():
            if 'semiconductor' in IGBT_SPECIFICATIONS:
                device = IGBT_SPECIFICATIONS['semiconductor'].get('device', '')
                if device and re.search(re.escape(device), text, re.IGNORECASE):
                    if 'igbt_data' not in data['system']:
                        data['system']['igbt_data'] = {}
                    data['system']['igbt_data']['Device'] = device
                    data['system']['igbt_data']['Specs'] = IGBT_SPECIFICATIONS['semiconductor']

        # 8b. Tender Framework
        if 'TENDER' in doc_type_str.upper() or 'PROCUREMENT' in doc_type_str.upper():
            if 'tender_info' not in data:
                data['tender_info'] = []
            for code, name in TENDER_FRAMEWORK.get('classification', {}).items():
                if re.search(r'\b' + re.escape(name) + r'\b', text, re.IGNORECASE) or \
                   re.search(r'\b' + re.escape(code) + r'\b', text):
                    data['tender_info'].append({'term': code, 'desc': name})
            for section, values in TENDER_FRAMEWORK.items():
                if isinstance(values, dict):
                    for k in values.keys():
                        readable = k.replace('_', ' ')
                        if re.search(r'\b' + re.escape(readable) + r'\b', text, re.IGNORECASE):
                            data['tender_info'].append({'term': k, 'desc': f"Standard: {str(values[k])}"})
            for ta in ["NIT", "EMD", "EOI", "RFP"]:
                if re.search(r'\b' + re.escape(ta) + r'\b', text):
                    data['tender_info'].append({'term': ta, 'desc': "Tender Term Found"})

        # 9. ICF Coach & Passenger Systems
        for motive, desc in ICF_COACH_DATA.get('classification', {}).get('motive_types', {}).items():
            if re.search(r'\b' + re.escape(motive) + r'\b', text, re.IGNORECASE):
                data['coach_info']['motive_type'] = motive
                data['coach_info']['description'] = desc
                if motive in ICF_COACH_DATA.get('technical_specs', {}):
                    data['coach_info'].update(ICF_COACH_DATA['technical_specs'][motive])
                break
        for code, desc in ICF_COACH_DATA.get('classification', {}).get('coach_codes', {}).items():
            if re.search(r'\b' + re.escape(code) + r'\b', text):
                if 'types' not in data['coach_info']:
                    data['coach_info']['types'] = []
                data['coach_info']['types'].append(f"{code} ({desc})")

        # 10. Standards & Regulations
        for grade, info in RAILWAY_STANDARDS_DATA.get('material_grades', {}).get('steel_is_1570', {}).items():
            if re.search(r'\b' + re.escape(grade) + r'\b', text, re.IGNORECASE):
                data['standards'].append({
                    'type': 'IS Grade', 'code': grade,
                    'desc': info.get('desc'), 'equivalent': info.get('equivalent')
                })
        iris_matches = re.findall(OCR_PATTERNS_PART2['iris_asset_code'], text)
        if iris_matches:
            data['standards'].extend([{'type': 'IRIS Code', 'code': m} for m in iris_matches])
        for din, is_eq in RAILWAY_STANDARDS_DATA.get('din_equivalents', {}).items():
            if re.search(re.escape(din), text, re.IGNORECASE):
                data['standards'].append({'type': 'DIN Standard', 'code': din, 'equivalent': is_eq})

        # 11. Engineering Drawing Processing
        if doc_type_str == DocumentType.ENGINEERING_DRAWING.value or 'DRAWING' in doc_type_str.upper():
            drawing_data = EngineeringDrawingProcessor.process_drawing(text)
            data['drawing_info'] = drawing_data
            data['advanced_tech'].extend(drawing_data.get('advanced_tech', []))
            for item in drawing_data.get('bom_items', []):
                data['components'].append(f"{item['description']} (Qty: {item['qty']})")

        return data


# =============================================================================
# ENGINEERING DRAWING PROCESSOR
# =============================================================================

class EngineeringDrawingProcessor:
    """Specialized processor for Engineering Drawings (Title Blocks, BOMs, GD&T)"""

    @staticmethod
    def process_drawing(text: str) -> Dict[str, Any]:
        info = {
            'title_block': {},
            'bom_items': [],
            'gdt_symbols': [],
            'notes_found': [],
            'advanced_tech': [],
        }

        # 1. Title Block Extraction
        for field, pattern in TITLE_BLOCK_PATTERNS.items():
            match = pattern.search(text)
            if match:
                info['title_block'][field] = match.group(1).strip()

        # 2. BOM Extraction
        if any(h in text.upper() for h in BOM_HEADERS[:3]):
            matches = BOM_ROW_PATTERN.findall(text)
            for m in matches:
                if len(m) >= 3:
                    info['bom_items'].append({
                        'item_no': m[0], 'part_no': m[1],
                        'description': m[2], 'qty': m[3] if len(m) > 3 else "1"
                    })

        # 3. GD&T Symbol Detection
        for category, symbols in GDT_SYMBOLS.items():
            for name, details in symbols.items():
                if details.get('symbol') and details['symbol'] in text:
                    info['gdt_symbols'].append({'name': name, 'symbol': details['symbol'], 'category': category})
                elif any(k in text.lower() for k in details.get('keywords', [])):
                    info['gdt_symbols'].append({'name': name, 'category': category})

        # 4. Advanced Technology Detection
        for tech, terms in ADVANCED_TECH_TERMS.items():
            if any(re.search(r'\b' + re.escape(t) + r'\b', text, re.IGNORECASE) for t in terms):
                info['advanced_tech'].append(tech.replace('_', ' '))

        # 5. Engineering Notes
        for note in NOTE_KEYWORDS:
            if note in text.upper():
                info['notes_found'].append(note)

        return info


# =============================================================================
# MAIN RAILWAY OCR PIPELINE
# =============================================================================

class RailwayOCRPipeline:
    """Main processing pipeline for railway document OCR"""

    def process(self, ocr_text: str) -> ExtractionResult:
        # Step 1: Preprocess
        normalized = OCRPreprocessor.normalize_text(ocr_text)

        # Step 2: Classify
        doc_type, confidence = DocumentClassifier.classify(normalized)

        # Step 3: Extract
        extracted = InformationExtractor.extract(normalized, doc_type)

        # Step 4: Build Summary
        summary_parts = [f"Classified as **{doc_type}**"]
        if extracted['locomotive'].get('model'):
            loco = extracted['locomotive']
            summary_parts.append(f"for **{loco['model']}**")
            if loco.get('power_hp'):
                summary_parts.append(f"({loco['power_hp']} HP)")
        if extracted['maintenance'].get('schedule_code'):
            maint = extracted['maintenance']
            summary_parts.append(f"| Schedule: **{maint['schedule_code']}** ({maint.get('name', '')})")
        if extracted['rdso_specs']:
            specs = [s.get('spec_no', s.get('key')) for s in extracted['rdso_specs'][:2]]
            summary_parts.append(f"| RDSO: {', '.join(specs)}")
        if extracted['production_units']:
            units = [u['code'] for u in extracted['production_units'][:2]]
            summary_parts.append(f"| Units: {', '.join(units)}")
        if extracted.get('coach_info', {}).get('motive_type'):
            summary_parts.append(f"| Type: **{extracted['coach_info']['motive_type']}**")
        if extracted.get('standards'):
            stds = [s['code'] for s in extracted['standards'][:2]]
            summary_parts.append(f"| Standards: {', '.join(stds)}")
        if extracted.get('tender_info'):
            summary_parts.append(f"| Tender Terms Found: {len(extracted['tender_info'])}")
        if extracted.get('drawing_info', {}).get('title_block', {}).get('drawing_number'):
            drg = extracted['drawing_info']['title_block']
            summary_parts.append(f"| Drg No: **{drg['drawing_number']}**")

        return ExtractionResult(
            document_type=doc_type,
            confidence_score=round(confidence, 2),
            locomotive_info=extracted['locomotive'],
            maintenance_info=extracted['maintenance'],
            references=extracted['references'],
            components=extracted['components'],
            system_data=extracted.get('system', {}),
            abbreviations_found=extracted['abbreviations'],
            rdso_specs_matched=[s.get('spec_no', s.get('key')) for s in extracted['rdso_specs']],
            production_units_referenced=[u['code'] for u in extracted['production_units']],
            strategic_initiatives=extracted['initiatives'],
            summary=' '.join(summary_parts),
            suggested_links=extracted['suggested_links'],
            coach_info=extracted.get('coach_info', {}),
            standards=extracted.get('standards', []),
            drawing_info=extracted.get('drawing_info', {}),
            advanced_tech=extracted.get('advanced_tech', []),
            tender_info=extracted.get('tender_info', []),
        )
