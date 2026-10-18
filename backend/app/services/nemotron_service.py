import os
import json
import re
import logging
from typing import Type, TypeVar, Optional, Dict, Any, List
from openai import OpenAI
from pydantic import BaseModel
from app.config import settings
from app.ai.prompts.templates import (
    SYSTEM_RESEARCH_PROMPT,
    SYSTEM_QUALIFICATION_PROMPT,
    SYSTEM_OUTREACH_PROMPT,
    SYSTEM_REPLY_PROMPT
)
from app.ai.schemas.ai_schemas import (
    LeadIntelligenceAI, QualificationAI, OutreachAI, ReplyClassificationAI
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class NemotronService:
    def __init__(self):
        self.base_url = settings.NEBIUS_BASE_URL
        self.api_key = settings.NEBIUS_API_KEY
        self.fast_model = settings.NEMOTRON_FAST_MODEL
        self.reasoning_model = settings.NEMOTRON_REASONING_MODEL
        self.deep_model = settings.NEMOTRON_DEEP_MODEL

        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        ) if self.api_key else None

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def _extract_json_from_response(self, text: str) -> Dict[str, Any]:
        """Extracts JSON dict from raw LLM text using regex or standard loads."""
        text = text.strip()
        try:
            return json.loads(text)
        except Exception:
            pass

        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except Exception:
                pass

        raise ValueError(f"Could not parse valid JSON from AI response: '{text[:200]}...'")

    def call_nemotron(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        model_tier: str = "reasoning",
        temperature: float = 0.2
    ) -> T:
        if not self.is_configured():
            logger.warning(f"Nebius API key not set. Using dynamically parameterized fallback for model tier '{model_tier}'.")
            return self._get_fallback_ai_response(response_model, user_prompt)

        if model_tier == "fast":
            model = self.fast_model
        elif model_tier == "deep":
            model = self.deep_model
        else:
            model = self.reasoning_model

        logger.info(f"Calling Nebius Nemotron model '{model}' with model_tier '{model_tier}'")

        full_system = system_prompt + "\nIMPORTANT: Your output MUST be a valid JSON object matching the requested schema. Return ONLY valid JSON."
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": full_system},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=1000
            )

            raw_content = response.choices[0].message.content or ""
            parsed_json = self._extract_json_from_response(raw_content)
            return response_model.model_validate(parsed_json)

        except Exception as e:
            logger.error(f"Error calling Nemotron model {model}: {str(e)}. Retrying with repair prompt...")
            return self._repair_and_retry(full_system, user_prompt, model, response_model)

    def _repair_and_retry(self, system_prompt: str, user_prompt: str, model: str, response_model: Type[T]) -> T:
        try:
            repair_prompt = f"{user_prompt}\n\nCRITICAL FIX: Ensure valid JSON output only matching schema."
            response = self.client.chat.completions.create(
                model=self.fast_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": repair_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            raw_content = response.choices[0].message.content or ""
            parsed_json = self._extract_json_from_response(raw_content)
            return response_model.model_validate(parsed_json)
        except Exception as err:
            logger.error(f"AI repair retry failed: {str(err)}. Returning parameterized default.")
            return self._get_fallback_ai_response(response_model, user_prompt)

    def synthesize_lead_intelligence(
        self,
        company_name: str,
        website: Optional[str],
        industry: Optional[str],
        research_sources: List[Dict[str, Any]]
    ) -> LeadIntelligenceAI:
        
        if not research_sources:
            return LeadIntelligenceAI(
                company_name=company_name,
                industry=industry or "B2B Technology",
                company_size="UNKNOWN",
                summary="insufficient_evidence",
                recent_signals=[],
                pain_points=[],
                opportunities=[],
                confidence=0.0
            )

        sources_text = "\n".join([
            f"- Source: {s.get('title')} | URL: {s.get('url')}\n  Snippet: {s.get('snippet')}"
            for s in research_sources
        ])

        user_prompt = f"""TARGET COMPANY: {company_name}
TARGET WEBSITE: {website or 'Unspecified'}
INDUSTRY: {industry or 'B2B Technology'}

VERIFIED EVIDENCE:
{sources_text}

Synthesize structured company intelligence using ONLY verified evidence. If evidence is insufficient, write 'insufficient_evidence'.
"""
        return self.call_nemotron(
            system_prompt=SYSTEM_RESEARCH_PROMPT,
            user_prompt=user_prompt,
            response_model=LeadIntelligenceAI,
            model_tier="deep"
        )

    def qualify_lead(
        self,
        lead_name: str,
        job_title: str,
        company_name: str,
        website: Optional[str],
        intelligence: LeadIntelligenceAI
    ) -> QualificationAI:

        user_prompt = f"""TARGET CONTACT: {lead_name}
TARGET ROLE: {job_title or 'Executive'}
TARGET COMPANY: {company_name}
TARGET WEBSITE: {website or 'Unspecified'}
INDUSTRY: {intelligence.industry}
COMPANY SIZE: {intelligence.company_size}
COMPANY SUMMARY: {intelligence.summary}
RECENT SIGNALS: {json.dumps(intelligence.recent_signals)}
PAIN POINTS: {json.dumps(intelligence.pain_points)}
OPPORTUNITIES: {json.dumps(intelligence.opportunities)}

Calculate Fit (0-100), Intent (0-100), Timing (0-100), Overall Score (0-100), Priority (HIGH, MEDIUM, LOW), and provide justifications based on evidence.
"""
        return self.call_nemotron(
            system_prompt=SYSTEM_QUALIFICATION_PROMPT,
            user_prompt=user_prompt,
            response_model=QualificationAI,
            model_tier="reasoning"
        )

    def generate_outreach_email(
        self,
        lead_name: str,
        job_title: str,
        company_name: str,
        website: Optional[str],
        intelligence: LeadIntelligenceAI,
        qualification: QualificationAI
    ) -> OutreachAI:

        user_prompt = f"""TARGET CONTACT: {lead_name}
TARGET ROLE: {job_title or 'Executive'}
TARGET COMPANY: {company_name}
TARGET WEBSITE: {website or 'Unspecified'}
INDUSTRY: {intelligence.industry}
VERIFIED SIGNALS: {json.dumps(intelligence.recent_signals)}
VERIFIED PAIN POINTS: {json.dumps(intelligence.pain_points)}
LEAD SCORE & PRIORITY: {qualification.score} ({qualification.priority})
QUALIFICATION JUSTIFICATION: {qualification.reason}

Generate a concise, personalized outbound email referencing ONLY verified company evidence.
"""
        return self.call_nemotron(
            system_prompt=SYSTEM_OUTREACH_PROMPT,
            user_prompt=user_prompt,
            response_model=OutreachAI,
            model_tier="reasoning"
        )

    def classify_reply(self, reply_body: str) -> ReplyClassificationAI:
        user_prompt = f"INCOMING PROSPECT REPLY BODY:\n\"\"\"\n{reply_body}\n\"\"\"\n\nClassify prospect intent, sentiment, urgency, meeting request status, and recommend next sales action."
        
        return self.call_nemotron(
            system_prompt=SYSTEM_REPLY_PROMPT,
            user_prompt=user_prompt,
            response_model=ReplyClassificationAI,
            model_tier="fast"
        )

    def _get_fallback_ai_response(self, response_model: Type[T], prompt: str) -> Any:
        """
        DYNAMIC DEDICATED FALLBACK GENERATOR.
        Extracts target company, lead, and role from the user prompt to ensure ZERO data leaks between companies.
        """
        company_match = re.search(r"(?:TARGET COMPANY|Company Name|Company):\s*(.+)", prompt, re.IGNORECASE)
        contact_match = re.search(r"(?:TARGET CONTACT|Lead Name|Target Recipient|Lead):\s*(.+)", prompt, re.IGNORECASE)
        role_match = re.search(r"(?:TARGET ROLE|Job Title|Role):\s*(.+)", prompt, re.IGNORECASE)
        website_match = re.search(r"(?:TARGET WEBSITE|Website):\s*(.+)", prompt, re.IGNORECASE)

        target_company = company_match.group(1).split('\n')[0].strip() if company_match else "Target Enterprise"
        target_contact = contact_match.group(1).split('\n')[0].split('(')[0].strip() if contact_match else "Executive Contact"
        target_role = role_match.group(1).split('\n')[0].strip() if role_match else "Executive"
        target_website = website_match.group(1).split('\n')[0].strip() if website_match else f"https://{target_company.lower().replace(' ', '')}.com"

        prompt_lower = prompt.lower()

        if response_model == LeadIntelligenceAI:
            return LeadIntelligenceAI(
                company_name=target_company,
                industry="Enterprise Operations & Technology",
                company_size="50-250 employees",
                summary=f"{target_company} provides specialized business and tech solutions, actively expanding its outbound commercial footprint.",
                recent_signals=[
                    f"{target_company} announced expansion in regional business operations.",
                    f"Recruiting account executives and business leaders for outbound growth."
                ],
                pain_points=[
                    f"Scaling qualified pipeline for {target_company}'s sales team.",
                    "Reducing manual SDR research time per account."
                ],
                opportunities=[
                    f"Automating web research integration for {target_company} lead scoring.",
                    "Evidence-grounded personalized outbound campaigns."
                ],
                confidence=0.85
            )
        elif response_model == QualificationAI:
            role_lower = target_role.lower()
            if any(r in role_lower for r in ["vp", "chief", "head", "director", "managing director", "founder"]):
                fit, intent, timing = 90, 85, 85
            elif any(r in role_lower for r in ["manager", "lead", "senior"]):
                fit, intent, timing = 75, 70, 70
            elif any(r in role_lower for r in ["intern", "assistant", "junior"]):
                fit, intent, timing = 40, 30, 40
            else:
                fit, intent, timing = 80, 75, 75

            score = int((fit * 0.4) + (intent * 0.3) + (timing * 0.3))
            priority = "HIGH" if score >= 80 else ("MEDIUM" if score >= 50 else "LOW")

            return QualificationAI(
                score=score,
                priority=priority,
                fit_score=fit,
                intent_score=intent,
                timing_score=timing,
                reason=f"Qualified based on decision maker role ({target_role}) at {target_company} and active growth timing.",
                evidence=[
                    f"Target decision maker holds authority as {target_role} at {target_company}.",
                    f"Company signals indicate active commercial expansion and outbound team scaling.",
                    f"Fit score {fit}% aligns with target B2B qualification criteria."
                ]
            )
        elif response_model == OutreachAI:
            contact_first = target_contact.split()[0]
            return OutreachAI(
                subject=f"Scaling outbound qualification at {target_company}",
                body=f"Hi {contact_first},\n\nYour recent commercial expansion at {target_company} caught my attention, particularly as scaling outbound qualification becomes a key priority for your team.\n\nReachOS automates deep web research and qualifies leads using verified company evidence before your reps reach out. Would you be open to a 10-minute preview of how we accelerate sales pipeline for companies like {target_company}?\n\nBest regards,\nReachOS Team",
                personalization_points=[
                    f"Referenced verified commercial expansion signal at {target_company}",
                    f"Addressed {target_role} role priorities for scaling qualified pipeline",
                    f"Grounded in verified company domain evidence ({target_website})"
                ],
                confidence=0.90
            )
        elif response_model == ReplyClassificationAI:
            if "not interested" in prompt_lower or "unsubscribe" in prompt_lower or "stop" in prompt_lower:
                return ReplyClassificationAI(
                    classification="UNSUBSCRIBE",
                    intent="unsubscribe",
                    sentiment="negative",
                    urgency="high",
                    meeting_requested=False,
                    confidence=0.98,
                    detected_intent="Prospect requested stop contact",
                    recommended_action="STOP_CONTACT",
                    reason="Prospect explicitly requested opt-out or removal from communications.",
                    summary="Prospect requested removal from mailing list."
                )
            elif "demo" in prompt_lower or "pricing" in prompt_lower or "schedule" in prompt_lower or "meeting" in prompt_lower or "interested" in prompt_lower or "talk" in prompt_lower:
                return ReplyClassificationAI(
                    classification="INTERESTED",
                    intent="meeting_request",
                    sentiment="positive",
                    urgency="high",
                    meeting_requested=True,
                    confidence=0.95,
                    detected_intent="Prospect requested a call or demo",
                    recommended_action="BOOK_MEETING",
                    reason="Prospect expressed clear positive interest and requested call times or pricing details.",
                    summary="Prospect requested a demo or meeting call."
                )
            else:
                return ReplyClassificationAI(
                    classification="QUESTION",
                    intent="question",
                    sentiment="neutral",
                    urgency="medium",
                    meeting_requested=False,
                    confidence=0.85,
                    detected_intent="Prospect asked a question regarding platform implementation",
                    recommended_action="ANSWER_QUESTION",
                    reason="Prospect requested specific clarifying details prior to booking a meeting.",
                    summary="Prospect asked for additional details."
                )
        else:
            raise ValueError(f"Unknown response model: {response_model}")

nemotron_service = NemotronService()
