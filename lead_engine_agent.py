"""
Lead Engine Agent - Claude Agent SDK powered lead generation and management system

This module provides intelligent lead generation, qualification, scoring, and enrichment
using the Claude Agent SDK integrated with Open Agent Studio's automation capabilities.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

from anthropic import Anthropic


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LeadStatus(Enum):
    """Lead status enumeration"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    NURTURING = "nurturing"
    CONVERTED = "converted"
    LOST = "lost"


class LeadSource(Enum):
    """Lead source enumeration"""
    LINKEDIN = "linkedin"
    WEBSITE = "website"
    EMAIL = "email"
    REFERRAL = "referral"
    COLD_OUTREACH = "cold_outreach"
    SOCIAL_MEDIA = "social_media"
    MANUAL = "manual"
    API = "api"


@dataclass
class Lead:
    """Lead data model"""
    id: Optional[str] = None
    name: str = ""
    email: str = ""
    company: str = ""
    title: str = ""
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    website: Optional[str] = None
    source: LeadSource = LeadSource.MANUAL
    status: LeadStatus = LeadStatus.NEW
    score: int = 0
    notes: str = ""
    tags: List[str] = None
    custom_fields: Dict[str, Any] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_contacted: Optional[datetime] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.custom_fields is None:
            self.custom_fields = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert lead to dictionary"""
        data = asdict(self)
        # Convert enums to strings
        data['source'] = self.source.value
        data['status'] = self.status.value
        # Convert datetime objects
        for field in ['created_at', 'updated_at', 'last_contacted']:
            if data[field]:
                data[field] = data[field].isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Lead':
        """Create lead from dictionary"""
        # Convert string enums back
        if 'source' in data and isinstance(data['source'], str):
            data['source'] = LeadSource(data['source'])
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = LeadStatus(data['status'])
        # Convert datetime strings back
        for field in ['created_at', 'updated_at', 'last_contacted']:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])
        return cls(**data)


@dataclass
class LeadQualificationCriteria:
    """Criteria for qualifying leads"""
    required_fields: List[str] = None  # Fields that must be present
    company_size_min: Optional[int] = None
    company_size_max: Optional[int] = None
    industries: List[str] = None  # Target industries
    job_titles: List[str] = None  # Target job titles/roles
    locations: List[str] = None  # Target locations
    min_score: int = 50  # Minimum score to be considered qualified
    disqualifying_keywords: List[str] = None  # Keywords that disqualify a lead

    def __post_init__(self):
        if self.required_fields is None:
            self.required_fields = ['name', 'email', 'company']
        if self.industries is None:
            self.industries = []
        if self.job_titles is None:
            self.job_titles = []
        if self.locations is None:
            self.locations = []
        if self.disqualifying_keywords is None:
            self.disqualifying_keywords = []


@dataclass
class TaskStep:
    """Represents a single step in lead generation or enrichment"""
    description: str
    tool: str
    parameters: Dict[str, Any]
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Any] = None
    error: Optional[str] = None


class LeadEngineAgent:
    """
    Lead Engine Agent powered by Claude Agent SDK

    Capabilities:
    - Lead generation from various sources (LinkedIn, websites, databases)
    - Intelligent lead qualification and scoring
    - Lead enrichment (finding additional data)
    - Automated lead nurturing
    - Lead segmentation and tagging
    """

    def __init__(self, api_key: str, mcp_client=None):
        """
        Initialize Lead Engine Agent

        Args:
            api_key: Anthropic API key
            mcp_client: Optional MCP client for tool execution
        """
        self.client = Anthropic(api_key=api_key)
        self.mcp_client = mcp_client
        self.leads_database = {}  # In-memory storage (replace with SQLAlchemy)

        logger.info("Lead Engine Agent initialized")

    async def process_lead_request(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a natural language lead request

        Args:
            request: User's natural language request
            context: Optional context (qualification criteria, filters, etc.)

        Returns:
            Result dictionary with leads, status, and metadata
        """
        logger.info(f"Processing lead request: {request}")

        try:
            # Step 1: Understand the intent
            intent = await self._understand_intent(request, context)
            logger.info(f"Intent identified: {intent['action']}")

            # Step 2: Create execution plan
            plan = await self._create_plan(intent)
            logger.info(f"Execution plan created with {len(plan)} steps")

            # Step 3: Execute the plan
            result = await self._execute_plan(plan)
            logger.info(f"Plan execution completed")

            return {
                "success": True,
                "intent": intent,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error processing lead request: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _understand_intent(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Use Claude to understand user intent from natural language

        Returns intent classification and extracted parameters
        """
        system_prompt = """You are a lead generation and management AI assistant.
Analyze the user's request and identify:
1. The primary action (generate, qualify, enrich, score, segment, export, nurture)
2. The target source (linkedin, website, database, etc.)
3. Any filters or criteria mentioned
4. The desired output format

Return your analysis as JSON with this structure:
{
    "action": "generate|qualify|enrich|score|segment|export|nurture",
    "source": "linkedin|website|database|manual|etc",
    "filters": {
        "industry": [],
        "job_title": [],
        "location": [],
        "company_size": null,
        "keywords": []
    },
    "output_format": "json|csv|workflow",
    "limit": 10,
    "additional_context": ""
}"""

        context_str = f"\nAdditional context: {json.dumps(context)}" if context else ""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": f"User request: {request}{context_str}\n\nProvide your analysis in JSON format."
            }]
        )

        # Extract JSON from response
        response_text = message.content[0].text

        # Try to extract JSON from response
        try:
            # Look for JSON block
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()

            intent = json.loads(json_str)
            return intent
        except json.JSONDecodeError:
            # Fallback to simple intent
            logger.warning("Could not parse JSON intent, using fallback")
            return {
                "action": "generate",
                "source": "manual",
                "filters": {},
                "output_format": "json",
                "limit": 10,
                "additional_context": request
            }

    async def _create_plan(self, intent: Dict[str, Any]) -> List[TaskStep]:
        """
        Create an execution plan based on the intent
        """
        plan = []
        action = intent.get('action', 'generate')

        if action == 'generate':
            # Plan for lead generation
            source = intent.get('source', 'manual')

            if source == 'linkedin':
                plan.append(TaskStep(
                    description="Navigate to LinkedIn and search for leads",
                    tool="playwright_navigate",
                    parameters={
                        "url": "https://www.linkedin.com",
                        "filters": intent.get('filters', {})
                    }
                ))
                plan.append(TaskStep(
                    description="Extract lead information from search results",
                    tool="playwright_extract",
                    parameters={
                        "selector": ".search-result__info",
                        "limit": intent.get('limit', 10)
                    }
                ))

            elif source == 'website':
                plan.append(TaskStep(
                    description="Scrape leads from website contact pages",
                    tool="playwright_navigate",
                    parameters={
                        "url": intent.get('filters', {}).get('website_url', ''),
                    }
                ))
                plan.append(TaskStep(
                    description="Extract contact information",
                    tool="playwright_extract",
                    parameters={
                        "patterns": ["email", "phone", "name"]
                    }
                ))

        elif action == 'qualify':
            plan.append(TaskStep(
                description="Load leads to qualify",
                tool="load_leads",
                parameters={"filters": intent.get('filters', {})}
            ))
            plan.append(TaskStep(
                description="Analyze and score leads using AI",
                tool="ai_qualify_leads",
                parameters={"criteria": intent.get('filters', {})}
            ))

        elif action == 'enrich':
            plan.append(TaskStep(
                description="Load leads to enrich",
                tool="load_leads",
                parameters={"filters": intent.get('filters', {})}
            ))
            plan.append(TaskStep(
                description="Enrich leads with additional data",
                tool="enrich_leads",
                parameters={"sources": ["clearbit", "hunter", "apollo"]}
            ))

        elif action == 'score':
            plan.append(TaskStep(
                description="Load leads to score",
                tool="load_leads",
                parameters={"filters": intent.get('filters', {})}
            ))
            plan.append(TaskStep(
                description="Calculate lead scores using AI",
                tool="ai_score_leads",
                parameters={"criteria": intent.get('filters', {})}
            ))

        return plan

    async def _execute_plan(self, plan: List[TaskStep]) -> Dict[str, Any]:
        """
        Execute the plan step by step
        """
        results = {
            "steps_completed": 0,
            "steps_failed": 0,
            "leads": [],
            "details": []
        }

        for step in plan:
            try:
                step.status = "running"
                logger.info(f"Executing: {step.description}")

                # Execute based on tool
                if step.tool.startswith("playwright_"):
                    result = await self._execute_playwright_tool(step)
                elif step.tool.startswith("ai_"):
                    result = await self._execute_ai_tool(step)
                else:
                    result = await self._execute_internal_tool(step)

                step.status = "completed"
                step.result = result
                results["steps_completed"] += 1
                results["details"].append({
                    "step": step.description,
                    "status": "completed",
                    "result": result
                })

                # Accumulate leads if present in result
                if isinstance(result, dict) and 'leads' in result:
                    results["leads"].extend(result['leads'])

            except Exception as e:
                step.status = "failed"
                step.error = str(e)
                results["steps_failed"] += 1
                results["details"].append({
                    "step": step.description,
                    "status": "failed",
                    "error": str(e)
                })
                logger.error(f"Step failed: {step.description} - {str(e)}")

        return results

    async def _execute_playwright_tool(self, step: TaskStep) -> Dict[str, Any]:
        """Execute browser automation tools via MCP"""
        if not self.mcp_client:
            return {"error": "MCP client not available", "leads": []}

        # This would call the actual playwright MCP server
        # For now, return mock data
        logger.info(f"Would execute playwright tool: {step.tool}")
        return {"leads": [], "status": "mock_execution"}

    async def _execute_ai_tool(self, step: TaskStep) -> Dict[str, Any]:
        """Execute AI-powered tools using Claude"""
        tool_name = step.tool

        if tool_name == "ai_qualify_leads":
            return await self._ai_qualify_leads(step.parameters)
        elif tool_name == "ai_score_leads":
            return await self._ai_score_leads(step.parameters)
        else:
            return {"error": f"Unknown AI tool: {tool_name}"}

    async def _execute_internal_tool(self, step: TaskStep) -> Dict[str, Any]:
        """Execute internal lead engine tools"""
        tool_name = step.tool

        if tool_name == "load_leads":
            return await self._load_leads(step.parameters)
        elif tool_name == "enrich_leads":
            return await self._enrich_leads(step.parameters)
        else:
            return {"error": f"Unknown internal tool: {tool_name}"}

    async def _ai_qualify_leads(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Claude to intelligently qualify leads
        """
        criteria = parameters.get('criteria', {})
        leads = parameters.get('leads', list(self.leads_database.values()))

        qualified_leads = []

        for lead in leads:
            # Use Claude to analyze the lead
            analysis = await self._analyze_lead_with_ai(lead, criteria)

            if analysis.get('qualified', False):
                lead.status = LeadStatus.QUALIFIED
                lead.score = analysis.get('score', 50)
                lead.notes += f"\n[AI Qualification] {analysis.get('reasoning', '')}"
                qualified_leads.append(lead)
            else:
                lead.status = LeadStatus.UNQUALIFIED
                lead.notes += f"\n[AI Disqualification] {analysis.get('reasoning', '')}"

        return {
            "leads": [lead.to_dict() for lead in qualified_leads],
            "total_analyzed": len(leads),
            "qualified_count": len(qualified_leads)
        }

    async def _ai_score_leads(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Claude to score leads based on multiple factors
        """
        criteria = parameters.get('criteria', {})
        leads = parameters.get('leads', list(self.leads_database.values()))

        scored_leads = []

        for lead in leads:
            # Use Claude to score the lead
            scoring = await self._score_lead_with_ai(lead, criteria)

            lead.score = scoring.get('score', 0)
            lead.notes += f"\n[AI Scoring] {scoring.get('reasoning', '')}"
            scored_leads.append(lead)

        # Sort by score
        scored_leads.sort(key=lambda x: x.score, reverse=True)

        return {
            "leads": [lead.to_dict() for lead in scored_leads],
            "average_score": sum(l.score for l in scored_leads) / len(scored_leads) if scored_leads else 0
        }

    async def _analyze_lead_with_ai(self, lead: Lead, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Claude to analyze and qualify a single lead
        """
        prompt = f"""Analyze this lead and determine if they should be qualified based on the criteria.

Lead Information:
- Name: {lead.name}
- Company: {lead.company}
- Title: {lead.title}
- Email: {lead.email}
- LinkedIn: {lead.linkedin_url}
- Notes: {lead.notes}
- Tags: {', '.join(lead.tags)}

Qualification Criteria:
{json.dumps(criteria, indent=2)}

Provide your analysis in JSON format:
{{
    "qualified": true/false,
    "score": 0-100,
    "reasoning": "Brief explanation",
    "suggested_tags": ["tag1", "tag2"],
    "next_actions": ["action1", "action2"]
}}"""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        try:
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()

            return json.loads(json_str)
        except:
            return {"qualified": False, "score": 0, "reasoning": "Analysis failed"}

    async def _score_lead_with_ai(self, lead: Lead, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Claude to score a lead comprehensively
        """
        prompt = f"""Score this lead from 0-100 based on their fit with our ideal customer profile.

Lead Information:
- Name: {lead.name}
- Company: {lead.company}
- Title: {lead.title}
- Email: {lead.email}
- Current Score: {lead.score}
- Status: {lead.status.value}
- Notes: {lead.notes}

Scoring Criteria:
{json.dumps(criteria, indent=2)}

Consider:
1. Job title relevance (0-25 points)
2. Company fit (0-25 points)
3. Contact information quality (0-20 points)
4. Engagement potential (0-30 points)

Provide JSON:
{{
    "score": 0-100,
    "reasoning": "Breakdown of scoring",
    "strengths": ["strength1", "strength2"],
    "concerns": ["concern1", "concern2"]
}}"""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        try:
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()

            return json.loads(json_str)
        except:
            return {"score": lead.score, "reasoning": "Scoring failed"}

    async def _load_leads(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Load leads from database with filters"""
        filters = parameters.get('filters', {})

        # Filter leads from database
        filtered_leads = []
        for lead in self.leads_database.values():
            if self._matches_filters(lead, filters):
                filtered_leads.append(lead)

        return {
            "leads": filtered_leads,
            "count": len(filtered_leads)
        }

    async def _enrich_leads(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich leads with additional data from external sources"""
        leads = parameters.get('leads', list(self.leads_database.values()))
        sources = parameters.get('sources', [])

        enriched_count = 0

        for lead in leads:
            # Mock enrichment - in production, integrate with APIs
            if 'clearbit' in sources and lead.email:
                # Would call Clearbit API here
                lead.custom_fields['enriched_by'] = lead.custom_fields.get('enriched_by', [])
                lead.custom_fields['enriched_by'].append('clearbit')
                enriched_count += 1

            lead.updated_at = datetime.now()

        return {
            "leads": [lead.to_dict() for lead in leads],
            "enriched_count": enriched_count
        }

    def _matches_filters(self, lead: Lead, filters: Dict[str, Any]) -> bool:
        """Check if lead matches filter criteria"""
        if filters.get('status') and lead.status.value != filters['status']:
            return False
        if filters.get('min_score') and lead.score < filters['min_score']:
            return False
        if filters.get('company') and filters['company'].lower() not in lead.company.lower():
            return False
        if filters.get('tags') and not any(tag in lead.tags for tag in filters['tags']):
            return False
        return True

    def add_lead(self, lead: Lead) -> str:
        """Add a lead to the database"""
        if not lead.id:
            lead.id = f"lead_{len(self.leads_database) + 1}_{int(datetime.now().timestamp())}"

        self.leads_database[lead.id] = lead
        logger.info(f"Added lead: {lead.name} ({lead.id})")
        return lead.id

    def get_lead(self, lead_id: str) -> Optional[Lead]:
        """Get a lead by ID"""
        return self.leads_database.get(lead_id)

    def update_lead(self, lead_id: str, updates: Dict[str, Any]) -> bool:
        """Update a lead"""
        lead = self.leads_database.get(lead_id)
        if not lead:
            return False

        for key, value in updates.items():
            if hasattr(lead, key):
                setattr(lead, key, value)

        lead.updated_at = datetime.now()
        logger.info(f"Updated lead: {lead_id}")
        return True

    def delete_lead(self, lead_id: str) -> bool:
        """Delete a lead"""
        if lead_id in self.leads_database:
            del self.leads_database[lead_id]
            logger.info(f"Deleted lead: {lead_id}")
            return True
        return False

    def get_all_leads(self, filters: Dict[str, Any] = None) -> List[Lead]:
        """Get all leads with optional filters"""
        leads = list(self.leads_database.values())

        if filters:
            leads = [lead for lead in leads if self._matches_filters(lead, filters)]

        return leads

    def export_leads(self, leads: List[Lead], format: str = 'json') -> str:
        """Export leads to JSON or CSV format"""
        if format == 'json':
            return json.dumps([lead.to_dict() for lead in leads], indent=2, default=str)
        elif format == 'csv':
            # Simple CSV export
            if not leads:
                return ""

            headers = ['id', 'name', 'email', 'company', 'title', 'phone', 'score', 'status', 'source']
            rows = [','.join(headers)]

            for lead in leads:
                row = [
                    lead.id or '',
                    lead.name,
                    lead.email,
                    lead.company,
                    lead.title,
                    lead.phone or '',
                    str(lead.score),
                    lead.status.value,
                    lead.source.value
                ]
                rows.append(','.join(f'"{item}"' for item in row))

            return '\n'.join(rows)
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Example usage
async def main():
    """Example usage of Lead Engine Agent"""
    import os

    # Initialize agent
    api_key = os.getenv('ANTHROPIC_API_KEY', 'your-api-key-here')
    agent = LeadEngineAgent(api_key=api_key)

    # Add some sample leads
    sample_leads = [
        Lead(
            name="John Smith",
            email="john.smith@techcorp.com",
            company="TechCorp Inc",
            title="VP of Engineering",
            source=LeadSource.LINKEDIN,
            tags=["tech", "enterprise"]
        ),
        Lead(
            name="Sarah Johnson",
            email="sarah.j@startup.io",
            company="StartupIO",
            title="CTO",
            source=LeadSource.REFERRAL,
            tags=["tech", "startup"]
        ),
        Lead(
            name="Mike Williams",
            email="mike@sales.com",
            company="Sales Corp",
            title="Sales Manager",
            source=LeadSource.COLD_OUTREACH,
            tags=["sales"]
        )
    ]

    for lead in sample_leads:
        agent.add_lead(lead)

    print(f"Added {len(sample_leads)} sample leads\n")

    # Example 1: Qualify leads
    print("=" * 60)
    print("Example 1: Qualifying leads for enterprise software")
    print("=" * 60)
    result = await agent.process_lead_request(
        "Qualify leads for enterprise software targeting VPs and CTOs in tech companies",
        context={
            "min_score": 60,
            "target_titles": ["VP", "CTO", "Director"],
            "target_industries": ["tech", "software"]
        }
    )
    print(json.dumps(result, indent=2, default=str))

    # Example 2: Score leads
    print("\n" + "=" * 60)
    print("Example 2: Scoring all leads")
    print("=" * 60)
    result = await agent.process_lead_request(
        "Score all leads based on title seniority and company type"
    )
    print(json.dumps(result, indent=2, default=str))

    # Example 3: Export qualified leads
    print("\n" + "=" * 60)
    print("Example 3: Export qualified leads")
    print("=" * 60)
    qualified_leads = agent.get_all_leads(filters={"status": "qualified"})
    csv_export = agent.export_leads(qualified_leads, format='csv')
    print("CSV Export:")
    print(csv_export)


if __name__ == "__main__":
    asyncio.run(main())
