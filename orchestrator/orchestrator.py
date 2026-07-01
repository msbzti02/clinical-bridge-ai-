import asyncio
from domain.schemas import RPMAlert, ClinicalContextBrief
from agents.triage_agent import TriageAgent
from agents.ehr_retrieval_agent import EHRRetrievalAgent
from agents.anamnesis_agent import AnamnesisAgent
from agents.synthesis_agent import SynthesisAgent
from orchestrator.safety_guardrails import SafetyGuardrails
from infrastructure.logger import logger

class Orchestrator:
    def __init__(self, prompt_version="v3.0"):
        self.triage_agent = TriageAgent(version=prompt_version)
        self.ehr_agent = EHRRetrievalAgent(version=prompt_version)
        self.anamnesis_agent = AnamnesisAgent(version=prompt_version)
        self.synthesis_agent = SynthesisAgent(version=prompt_version)
        self.guardrails = SafetyGuardrails()

    async def process_alert(self, alert: RPMAlert) -> ClinicalContextBrief:
        try:
            # 1. Triage (Max 60s)
            triage_decision = await asyncio.wait_for(self.triage_agent.triage(alert), timeout=60.0)
            
            # Critical Alert Bypass
            if triage_decision.escalate_immediately:
                logger.log_event("critical_alert_bypass", alert_id=str(alert.alert_id))
                ccb = ClinicalContextBrief(
                    alert_summary=triage_decision.urgency_rationale,
                    ehr_context="[Bypassed due to critical urgency]",
                    patient_reported_context="[Bypassed due to critical urgency]",
                    data_conflicts=[],
                    clinical_considerations=["CRITICAL ALERT: IMMEDIATE ATTENTION REQUIRED"],
                    recommended_actions=["Review patient vitals immediately", "Contact patient"],
                    confidence_score=1.0,
                    source_citations=[],
                    disclaimer="⚠️ EDUCATIONAL PROTOTYPE ONLY. This output is not a clinical tool and must not be used for actual clinical decision-making. All data is simulated. A qualified clinician must review this information before any action is taken.",
                    reasoning_trace=triage_decision.reasoning_trace
                )
                return ccb

            # 2. Parallel Retrieval (Max 60s)
            ehr_task = asyncio.create_task(self.ehr_agent.retrieve(str(alert.patient_id), triage_decision.ehr_query_params, triage_decision.clinical_question))
            anamnesis_task = asyncio.create_task(self.anamnesis_agent.retrieve(str(alert.patient_id), triage_decision.anamnesis_query_params, triage_decision.clinical_question))
            
            ehr_findings, anamnesis_findings = None, None
            
            try:
                ehr_findings = await asyncio.wait_for(ehr_task, timeout=60.0)
            except Exception as e:
                logger.log_event("ehr_retrieval_timeout_or_error", error=str(e))
                
            try:
                anamnesis_findings = await asyncio.wait_for(anamnesis_task, timeout=60.0)
            except Exception as e:
                logger.log_event("anamnesis_retrieval_timeout_or_error", error=str(e))
                
            # 3. Synthesis (Max 60s)
            ccb = await asyncio.wait_for(self.synthesis_agent.synthesize(alert, triage_decision, ehr_findings, anamnesis_findings), timeout=60.0)
            
            # 4. Safety Guardrails
            safe_ccb = self.guardrails.enforce(ccb, alert)
            return safe_ccb
            
        except asyncio.TimeoutError:
            logger.log_event("pipeline_timeout", alert_id=str(alert.alert_id))
            raise RuntimeError("Pipeline exceeded maximum timeout.")
        except Exception as e:
            logger.log_event("pipeline_error", error=str(e))
            raise e
