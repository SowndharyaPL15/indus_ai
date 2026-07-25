import os
import random
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# Setup
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demo_dataset")
FOLDERS = [
    "01_SOPs", "02_Machine_Manuals", "03_Maintenance_Logs", "04_Incident_Reports",
    "05_Inspection_Reports", "06_Compliance", "07_Engineer_Notes",
    "08_Production_Reports", "09_Quality_Reports", "10_Safety_Reports", "11_Factory_Layout"
]

MACHINES = [
    "Pump P101", "Pump P102", "Boiler B201", "Compressor CP01", "Cooling Tower CT01",
    "Generator G101", "Conveyor C301", "Heat Exchanger HX01", "Heat Exchanger HX02", "Motor M101"
]
DEPARTMENTS = ["Maintenance", "Production", "Quality", "Safety", "Operations"]
ENGINEERS = ["Ravi Kumar", "Arun Prakash", "Suresh Babu", "Priya Nair", "Karthik Raj"]
ISSUES = [
    "Pump vibration", "Bearing failure", "Boiler pressure increase", "Motor overheating",
    "Lubrication issue", "Misalignment", "Compressor leakage", "Cooling tower failure",
    "Generator shutdown", "Conveyor jam"
]

styles = getSampleStyleSheet()
title_style = styles['Heading1']
title_style.textColor = colors.HexColor("#1e3a8a")
h2_style = styles['Heading2']
h2_style.textColor = colors.HexColor("#1d4ed8")
normal_style = styles['Normal']

def setup_dirs():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    for folder in FOLDERS:
        path = os.path.join(OUTPUT_DIR, folder)
        if not os.path.exists(path):
            os.makedirs(path)

def build_pdf(filepath, elements):
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    header = Paragraph("<b>INDUS Manufacturing Pvt. Ltd.</b> - Enterprise Document Control", styles['Normal'])
    elements.insert(0, header)
    elements.insert(1, Spacer(1, 20))
    
    doc.build(elements)

def gen_sops():
    folder = os.path.join(OUTPUT_DIR, "01_SOPs")
    for i in range(1, 21):
        machine = random.choice(MACHINES)
        doc_id = f"SOP-{i:03d}"
        elements = [
            Paragraph(f"Standard Operating Procedure: {doc_id}", title_style),
            Paragraph(f"<b>Machine:</b> {machine}", normal_style),
            Paragraph(f"<b>Revision Date:</b> {datetime.now().strftime('%Y-%m-%d')}", normal_style),
            Spacer(1, 12),
            Paragraph("<b>Purpose:</b> To establish safe and effective operating procedures.", normal_style),
            Paragraph("<b>Scope:</b> Applies to all operators in the Production department.", normal_style),
            Spacer(1, 12),
            Paragraph("<b>Required PPE:</b> Safety glasses, steel-toed boots, gloves.", normal_style),
            Paragraph("<b>Tools Required:</b> Standard toolkit, calibration gauge.", normal_style),
            Spacer(1, 12),
            Paragraph("<b>Step-by-step Procedure:</b>", h2_style),
            Paragraph("1. Ensure lockout/tagout is verified before starting.", normal_style),
            Paragraph("2. Check primary power feeds and lubrication levels.", normal_style),
            Paragraph("3. Initiate start sequence per manufacturer guidelines.", normal_style),
            Paragraph("4. Monitor for abnormal vibrations or sounds.", normal_style),
            Spacer(1, 12),
            Paragraph("<b>Safety Precautions:</b> Never bypass interlocks.", normal_style),
            Paragraph("<b>References:</b> ISO9001, Machine Manual", normal_style)
        ]
        build_pdf(os.path.join(folder, f"{doc_id}_{machine.replace(' ', '_')}.pdf"), elements)

def gen_manuals():
    folder = os.path.join(OUTPUT_DIR, "02_Machine_Manuals")
    for i in range(1, 16):
        machine = random.choice(MACHINES)
        doc_id = f"MAN-{i:03d}"
        elements = [
            Paragraph(f"Machine Manual: {doc_id}", title_style),
            Paragraph(f"<b>Machine Overview:</b> {machine}", h2_style),
            Paragraph("This manual covers the operating principles and structural limits of the asset.", normal_style),
            Spacer(1, 12),
            Paragraph("<b>Specifications:</b> 480V 3-Phase, 5000 RPM Max", normal_style),
            Paragraph("<b>Operating Limits:</b> Do not exceed 85C core temperature.", normal_style),
            Spacer(1, 12),
            Paragraph("<b>Maintenance Schedule:</b> Weekly lubrication, Monthly alignment check.", normal_style),
            Paragraph("<b>Common Faults:</b> " + ", ".join(random.sample(ISSUES, 2)), normal_style),
            Spacer(1, 12),
            Paragraph("<b>Troubleshooting:</b> Refer to SOP for step-by-step resolution.", normal_style),
            Paragraph("<b>Safety Notes:</b> Follow all plant safety regulations.", normal_style)
        ]
        build_pdf(os.path.join(folder, f"{doc_id}_{machine.replace(' ', '_')}.pdf"), elements)

def gen_maintenance_logs():
    folder = os.path.join(OUTPUT_DIR, "03_Maintenance_Logs")
    for i in range(1, 21):
        machine = random.choice(MACHINES)
        issue = random.choice(ISSUES)
        engineer = random.choice(ENGINEERS)
        doc_id = f"MLOG-{i:03d}"
        elements = [
            Paragraph(f"Maintenance Log: {doc_id}", title_style),
            Paragraph(f"<b>Machine:</b> {machine}", normal_style),
            Paragraph(f"<b>Date:</b> {(datetime.now() - timedelta(days=random.randint(1,30))).strftime('%Y-%m-%d')}", normal_style),
            Paragraph(f"<b>Engineer:</b> {engineer}", normal_style),
            Spacer(1, 12),
            Paragraph(f"<b>Issue:</b> {issue}", h2_style),
            Paragraph("<b>Symptoms:</b> Operator reported abnormal behavior during shift.", normal_style),
            Paragraph("<b>Root Cause:</b> Wear and tear on internal components.", normal_style),
            Paragraph("<b>Corrective Action:</b> Replaced affected parts and recalibrated.", normal_style),
            Paragraph(f"<b>Downtime:</b> {random.randint(1, 8)} hours", normal_style),
            Spacer(1, 12),
            Paragraph("<b>Remarks:</b> Resolved. References SOP-005 and Machine Manual.", normal_style)
        ]
        build_pdf(os.path.join(folder, f"{doc_id}_{machine.replace(' ', '_')}.pdf"), elements)

def gen_incident_reports():
    folder = os.path.join(OUTPUT_DIR, "04_Incident_Reports")
    for i in range(1, 21):
        machine = random.choice(MACHINES)
        doc_id = f"IR-{i:03d}"
        elements = [
            Paragraph(f"Incident Report: {doc_id}", title_style),
            Paragraph(f"<b>Machine:</b> {machine}", normal_style),
            Paragraph(f"<b>Date:</b> {(datetime.now() - timedelta(days=random.randint(1,30))).strftime('%Y-%m-%d')}", normal_style),
            Spacer(1, 12),
            Paragraph("<b>Description:</b> Safety limit triggered causing automatic shutdown.", normal_style),
            Paragraph("<b>Timeline:</b> Incident occurred at 14:30. Response initiated at 14:35.", normal_style),
            Paragraph(f"<b>Root Cause:</b> {random.choice(ISSUES)}", normal_style),
            Paragraph("<b>Impact:</b> Production halted temporarily.", normal_style),
            Paragraph("<b>Corrective Action:</b> Re-engaged safety protocols and cleared fault.", normal_style),
            Paragraph("<b>Preventive Action:</b> Update inspection checklist.", normal_style),
            Paragraph("<b>Status:</b> Closed", normal_style)
        ]
        build_pdf(os.path.join(folder, f"{doc_id}.pdf"), elements)

def gen_inspection_reports():
    folder = os.path.join(OUTPUT_DIR, "05_Inspection_Reports")
    for i in range(1, 16):
        machine = random.choice(MACHINES)
        doc_id = f"INS-{i:03d}"
        elements = [
            Paragraph(f"Inspection Report: {doc_id}", title_style),
            Paragraph(f"<b>Machine:</b> {machine}", normal_style),
            Paragraph(f"<b>Inspection Date:</b> {(datetime.now() - timedelta(days=random.randint(1,10))).strftime('%Y-%m-%d')}", normal_style),
            Paragraph(f"<b>Inspector:</b> {random.choice(ENGINEERS)}", normal_style),
            Spacer(1, 12),
            Paragraph("<b>Readings:</b>", h2_style),
            Paragraph(f"Temperature: {random.randint(40, 90)} C", normal_style),
            Paragraph(f"Pressure: {random.randint(10, 100)} PSI", normal_style),
            Paragraph("Vibration: Within normal limits", normal_style),
            Paragraph("Lubrication: Adequate", normal_style),
            Paragraph("Alignment: Verified", normal_style),
            Spacer(1, 12),
            Paragraph("<b>Overall Condition:</b> Satisfactory", normal_style),
            Paragraph("<b>Recommendations:</b> Continue standard monitoring schedule.", normal_style)
        ]
        build_pdf(os.path.join(folder, f"{doc_id}.pdf"), elements)

def gen_compliance():
    folder = os.path.join(OUTPUT_DIR, "06_Compliance")
    topics = ["ISO9001", "ISO45001", "Fire Safety", "Electrical Safety", "Permit to Work", "Risk Assessment", "Machine Safety", "Emergency Response"]
    for i in range(1, 11):
        topic = topics[i % len(topics)]
        doc_id = f"COMP-{i:03d}"
        elements = [
            Paragraph(f"Compliance Document: {doc_id}", title_style),
            Paragraph(f"<b>Subject:</b> {topic}", h2_style),
            Spacer(1, 12),
            Paragraph("This document outlines the regulatory and internal standards required for operations.", normal_style),
            Paragraph("<b>Key Requirements:</b> Strict adherence to safety guidelines and continuous monitoring.", normal_style),
            Spacer(1, 12),
            Paragraph("<b>Audited By:</b> Safety Department", normal_style),
            Paragraph("<b>Status:</b> Approved", normal_style)
        ]
        build_pdf(os.path.join(folder, f"{doc_id}_{topic.replace(' ', '_')}.pdf"), elements)

def gen_engineer_notes():
    folder = os.path.join(OUTPUT_DIR, "07_Engineer_Notes")
    for i in range(1, 21):
        machine = random.choice(MACHINES)
        issue = random.choice(ISSUES)
        doc_id = f"EN-{i:03d}"
        elements = [
            Paragraph(f"Engineer Note: {doc_id}", title_style),
            Paragraph(f"<b>Machine:</b> {machine}", normal_style),
            Paragraph(f"<b>Engineer:</b> {random.choice(ENGINEERS)}", normal_style),
            Spacer(1, 12),
            Paragraph("<b>Observation:</b> Recurring issues detected during peak load hours.", normal_style),
            Paragraph(f"<b>Practical Experience:</b> In dealing with {issue}, I found that adjusting the feed rate resolves the symptom.", normal_style),
            Paragraph("<b>Recommendation:</b> Update the SOP to reflect modified feed rates.", normal_style),
            Paragraph("<b>Validated Solution:</b> Yes, tested over 3 shifts.", normal_style),
            Paragraph("<b>Confidence:</b> High", normal_style)
        ]
        build_pdf(os.path.join(folder, f"{doc_id}.pdf"), elements)

def gen_reports(folder_name, prefix, count, fields):
    folder = os.path.join(OUTPUT_DIR, folder_name)
    for i in range(1, count + 1):
        doc_id = f"{prefix}-{i:03d}"
        elements = [
            Paragraph(f"Report: {doc_id}", title_style),
            Spacer(1, 12)
        ]
        for field in fields:
            elements.append(Paragraph(f"<b>{field}:</b> Recorded accurately.", normal_style))
        build_pdf(os.path.join(folder, f"{doc_id}.pdf"), elements)

def main():
    setup_dirs()
    gen_sops()
    gen_manuals()
    gen_maintenance_logs()
    gen_incident_reports()
    gen_inspection_reports()
    gen_compliance()
    gen_engineer_notes()
    
    gen_reports("08_Production_Reports", "PROD", 10, ["Daily Production", "Efficiency", "Downtime", "Machine Utilization", "OEE"])
    gen_reports("09_Quality_Reports", "QUAL", 10, ["Inspection Results", "Rejected Parts", "Root Cause", "Corrective Actions", "Quality Metrics"])
    gen_reports("10_Safety_Reports", "SAF", 10, ["Near Miss", "Unsafe Condition", "PPE Audit", "Fire Drill", "Hazard Observation"])
    gen_reports("11_Factory_Layout", "LAY", 5, ["Plant Layout", "Machine Locations", "Emergency Exits", "Production Flow", "Utility Layout"])
    print("Dataset generation complete. 155 PDFs created in /demo_dataset/")

if __name__ == "__main__":
    main()
