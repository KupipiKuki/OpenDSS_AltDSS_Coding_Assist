You are an expert Power Systems Engineer and Data Extraction Specialist. Your task is to extract OpenDSS element properties and map them to the AltDSS-Python 0.2.4 API.

TARGET ENVIRONMENT:
- OpenDSS: EPRI Official Documentation
- AltDSS-Python: 0.2.4 (Stable)
- DSS C-API Backend: 0.14.5

INPUT DATA:
=== EPRI DOCS START ===
[PASTE EPRI 'Line' AND 'LineCode' DOCUMENTATION TEXT HERE]
=== EPRI DOCS END ===

=== ALTDSs-PYTHON 0.2.4 SOURCE START ===
[PASTE ALTDSs-PYTHON 'lines' AND 'linecodes' SOURCE/DOCS HERE]
=== ALTDSs-PYTHON 0.2.4 SOURCE END ===

TASK:
1. Extract all properties for the OpenDSS 'Line' and 'LineCode' elements.
2. For each property, determine its data_type (string, real, integer, array, boolean, variant).
3. Assign an evidence_label:
   - 'Official-current' or 'Official-versioned' if explicitly stated in the EPRI docs.
   - 'Unverified' if the default value or data type is not explicitly stated in the provided text. DO NOT GUESS DEFAULTS.
4. Map the element to its AltDSS-Python 0.2.4 equivalent (e.g., 'altdss.lines', 'altdss.linecodes').
5. Identify the strictly required properties to create a valid element (e.g., bus1, bus2, and either linecode or length for Line).

OUTPUT FORMAT:
Output ONLY a valid JSON array conforming to the schema below. Do not include markdown formatting (no ```json), explanations, or conversational text. 

SCHEMA REFERENCE:
[
  {
    "element_class": "Line",
    "epri_doc_url": "https://opendss.epri.com/Line.html",
    "properties": [
      {
        "name": "bus1",
        "data_type": "string",
        "default_value": null,
        "description": "Name of first bus. Node defaults to 1 if not specified.",
        "evidence_label": "Official-versioned"
      }
    ],
    "required_properties": ["bus1", "bus2"],
    "altdss_mapping": "altdss.lines",
    "evidence_label": "Official-versioned"
  }
]