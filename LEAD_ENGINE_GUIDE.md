# Lead Engine Agent - Comprehensive Guide

## Overview

The Lead Engine Agent is an intelligent lead generation and management system powered by the Claude Agent SDK. It seamlessly integrates with Open Agent Studio to provide AI-powered lead operations including generation, qualification, scoring, enrichment, and nurturing.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   User Interface                         │
│         (Natural Language or API Requests)               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Lead Engine Agent                           │
│         (Claude Agent SDK - Intent & Planning)           │
│  - Understands natural language requests                 │
│  - Creates execution plans                               │
│  - Orchestrates tool execution                           │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌────────────────┐
│ Lead Engine  │ │ Browser  │ │ Desktop Auto   │
│   MCP Server │ │   MCP    │ │   MCP Server   │
│              │ │  Server  │ │                │
│ - CRUD Ops   │ │ - Web    │ │ - LinkedIn     │
│ - Qualify    │ │   Scrape │ │   Automation   │
│ - Score      │ │ - Data   │ │ - Form Fill    │
│ - Enrich     │ │   Extract│ │                │
└──────┬───────┘ └────┬─────┘ └────────┬───────┘
       │              │                 │
       └──────────────┼─────────────────┘
                      ▼
          ┌───────────────────────┐
          │   Lead Database       │
          │   (SQLAlchemy)        │
          │                       │
          │ - Leads               │
          │ - Interactions        │
          │ - Campaigns           │
          │ - Scoring History     │
          └───────────────────────┘
```

## Key Components

### 1. Lead Engine Agent (`lead_engine_agent.py`)

The core intelligence layer that:
- Processes natural language requests using Claude
- Creates execution plans for complex lead operations
- Orchestrates tool execution across MCP servers
- Performs AI-powered lead qualification and scoring

**Key Features:**
- Natural language interface
- Intelligent lead qualification
- AI-powered lead scoring
- Multi-source lead enrichment
- Automated workflow generation

### 2. Lead Database (`lead_database.py`)

SQLAlchemy-based persistent storage for:
- **Leads**: Contact information, scores, status, tags
- **Interactions**: Email, calls, meetings, notes
- **Campaigns**: Lead generation/nurturing campaigns
- **Scoring History**: Track score changes over time
- **Tags**: Categorize and segment leads

### 3. Lead Engine MCP Server (`mcp_servers/lead_engine_mcp.py`)

Model Context Protocol server providing tools for:
- Lead CRUD operations
- Lead qualification and scoring
- Interaction tracking
- Campaign management
- Data import/export
- Lead enrichment

## Installation

### Prerequisites

```bash
# Python 3.8+
python --version

# Install dependencies
pip install -r requirements_lead_engine.txt
```

### Required Dependencies

Create `requirements_lead_engine.txt`:

```
anthropic>=0.18.0
sqlalchemy>=2.0.0
mcp>=0.1.0
aiohttp>=3.9.0
python-dotenv>=1.0.0
```

### Environment Setup

Create a `.env` file:

```bash
# Anthropic API Key (required)
ANTHROPIC_API_KEY=your_api_key_here

# Database URL (optional, defaults to SQLite)
DATABASE_URL=sqlite:///leads.db

# Optional: External enrichment API keys
CLEARBIT_API_KEY=your_clearbit_key
HUNTER_API_KEY=your_hunter_key
APOLLO_API_KEY=your_apollo_key
```

## Quick Start

### 1. Basic Lead Management

```python
import asyncio
from lead_engine_agent import LeadEngineAgent, Lead, LeadSource

# Initialize agent
agent = LeadEngineAgent(api_key="your_api_key")

# Add a lead manually
lead = Lead(
    name="John Smith",
    email="john.smith@techcorp.com",
    company="TechCorp Inc",
    title="VP of Engineering",
    source=LeadSource.LINKEDIN,
    tags=["tech", "enterprise"]
)
agent.add_lead(lead)

# Process natural language request
async def example():
    result = await agent.process_lead_request(
        "Find all qualified leads in tech companies with a score above 70"
    )
    print(result)

asyncio.run(example())
```

### 2. AI-Powered Lead Qualification

```python
async def qualify_leads():
    # Qualify leads using natural language criteria
    result = await agent.process_lead_request(
        """Qualify leads for our enterprise SaaS product targeting:
        - VPs and C-level executives
        - Companies with 50-500 employees
        - Tech industry
        - Based in North America""",
        context={
            "min_score": 60,
            "target_titles": ["VP", "CTO", "CEO", "Director"],
            "industries": ["Technology", "Software"]
        }
    )

    print(f"Qualified {len(result['result']['leads'])} leads")
    for lead in result['result']['leads']:
        print(f"- {lead['name']} ({lead['company']}) - Score: {lead['score']}")

asyncio.run(qualify_leads())
```

### 3. Lead Scoring

```python
async def score_leads():
    # AI-powered scoring
    result = await agent.process_lead_request(
        "Score all leads based on job title seniority, company size, and engagement potential"
    )

    # Get top leads
    leads = sorted(
        result['result']['leads'],
        key=lambda x: x['score'],
        reverse=True
    )[:10]

    print("Top 10 leads:")
    for lead in leads:
        print(f"{lead['score']}: {lead['name']} - {lead['title']} at {lead['company']}")

asyncio.run(score_leads())
```

## Natural Language Examples

The Lead Engine Agent understands various natural language requests:

### Lead Generation
```
"Generate 50 leads from LinkedIn for VPs of Sales in the SaaS industry"
"Find leads from the contact pages of Fortune 500 company websites"
"Scrape leads from this conference attendee list: [URL]"
```

### Lead Qualification
```
"Qualify all new leads for our enterprise product"
"Mark leads as qualified if they're CTOs at companies with 100+ employees"
"Disqualify leads from companies in the retail industry"
```

### Lead Scoring
```
"Score all leads based on title, company size, and industry fit"
"Update scores for leads that opened our last email campaign"
"Rescore all qualified leads using updated criteria"
```

### Lead Enrichment
```
"Enrich all qualified leads with Clearbit data"
"Find LinkedIn profiles for leads missing them"
"Update company information for all leads at TechCorp"
```

### Analytics & Reporting
```
"Show me stats on all leads by status"
"Export qualified leads to CSV"
"What's our conversion rate for leads from LinkedIn?"
```

## Using the MCP Server

### Starting the Server

```bash
python mcp_servers/lead_engine_mcp.py
```

### Available Tools

#### `create_lead`
Create a new lead in the database.

```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "company": "Example Corp",
  "title": "CTO",
  "source": "linkedin",
  "tags": ["tech", "qualified"]
}
```

#### `search_leads`
Search and filter leads.

```json
{
  "status": "qualified",
  "min_score": 70,
  "tags": ["enterprise"],
  "limit": 50
}
```

#### `qualify_lead`
Qualify or disqualify a lead.

```json
{
  "lead_id": 123,
  "qualified": true,
  "reason": "Matches ideal customer profile",
  "score": 85
}
```

#### `score_lead`
Update lead score.

```json
{
  "lead_id": 123,
  "score": 90,
  "reason": "Engaged with last 3 emails"
}
```

#### `add_interaction`
Track interaction with a lead.

```json
{
  "lead_id": 123,
  "interaction_type": "email",
  "subject": "Product Demo Follow-up",
  "description": "Sent follow-up email after demo",
  "outcome": "positive"
}
```

#### `export_leads`
Export leads to file.

```json
{
  "filters": {"status": "qualified"},
  "format": "csv",
  "filename": "qualified_leads.csv"
}
```

## Database Schema

### Leads Table
```sql
CREATE TABLE leads (
    id INTEGER PRIMARY KEY,
    external_id VARCHAR(255) UNIQUE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    phone VARCHAR(50),
    linkedin_url VARCHAR(500),
    website VARCHAR(500),
    source ENUM,
    status ENUM,
    score INTEGER DEFAULT 0,
    notes TEXT,
    custom_fields JSON,
    created_at DATETIME,
    updated_at DATETIME,
    last_contacted DATETIME
);
```

### Interactions Table
```sql
CREATE TABLE interactions (
    id INTEGER PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    interaction_type VARCHAR(50),
    subject VARCHAR(500),
    description TEXT,
    outcome VARCHAR(100),
    created_at DATETIME,
    created_by VARCHAR(255),
    metadata JSON
);
```

### Campaigns Table
```sql
CREATE TABLE campaigns (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    campaign_type VARCHAR(50),
    status VARCHAR(50),
    target_criteria JSON,
    leads_targeted INTEGER,
    leads_contacted INTEGER,
    leads_responded INTEGER,
    leads_converted INTEGER,
    created_at DATETIME,
    started_at DATETIME,
    completed_at DATETIME
);
```

## Advanced Usage

### Custom Qualification Criteria

```python
from lead_engine_agent import LeadQualificationCriteria

criteria = LeadQualificationCriteria(
    required_fields=['name', 'email', 'company', 'title'],
    company_size_min=50,
    company_size_max=1000,
    industries=['Technology', 'Software', 'SaaS'],
    job_titles=['VP', 'CTO', 'CEO', 'Director', 'Head of'],
    locations=['United States', 'Canada', 'United Kingdom'],
    min_score=65,
    disqualifying_keywords=['student', 'intern', 'unemployed']
)

# Use in qualification
result = await agent.process_lead_request(
    "Qualify leads using strict enterprise criteria",
    context={"criteria": criteria}
)
```

### Building Lead Workflows

```python
# Multi-step workflow
async def lead_workflow():
    # Step 1: Import leads from LinkedIn export
    await agent.process_lead_request(
        "Import leads from linkedin_export.csv"
    )

    # Step 2: Enrich with additional data
    await agent.process_lead_request(
        "Enrich all new leads with Clearbit and Hunter"
    )

    # Step 3: Score and qualify
    await agent.process_lead_request(
        "Score and qualify all new leads for enterprise SaaS"
    )

    # Step 4: Create nurturing campaign
    await agent.process_lead_request(
        "Create email campaign targeting qualified leads"
    )

    # Step 5: Export for CRM import
    await agent.process_lead_request(
        "Export qualified leads to salesforce_import.csv"
    )
```

### Integration with Browser Automation

```python
# Generate leads from LinkedIn using browser automation
async def scrape_linkedin_leads():
    result = await agent.process_lead_request(
        """Navigate to LinkedIn and find leads matching:
        - Title: VP of Sales, Director of Sales
        - Industry: SaaS, Software
        - Location: San Francisco Bay Area
        - Extract first 50 results"""
    )

    # The agent will:
    # 1. Use playwright MCP to navigate to LinkedIn
    # 2. Perform search with criteria
    # 3. Extract lead data from results
    # 4. Create leads in database
    # 5. Auto-tag with source info

    return result
```

## Best Practices

### 1. Lead Scoring Strategy

Create a consistent scoring model:

- **Job Title (0-25 points)**
  - C-level: 25 points
  - VP: 20 points
  - Director: 15 points
  - Manager: 10 points
  - Other: 5 points

- **Company Fit (0-25 points)**
  - Perfect industry match: 25 points
  - Related industry: 15 points
  - Different industry: 5 points

- **Contact Quality (0-20 points)**
  - Has phone + email + LinkedIn: 20 points
  - Has email + one other: 15 points
  - Has email only: 10 points

- **Engagement (0-30 points)**
  - Opened 3+ emails: 30 points
  - Opened 1-2 emails: 20 points
  - No engagement: 0 points

### 2. Lead Status Workflow

Follow a clear status progression:

```
NEW → CONTACTED → QUALIFIED → NURTURING → CONVERTED
  ↓         ↓           ↓
UNQUALIFIED ← ─ ─ ─ ─ LOST
```

### 3. Data Hygiene

- **Deduplicate regularly**: Check for duplicate emails
- **Validate emails**: Use Hunter or similar services
- **Update regularly**: Refresh lead data every 6 months
- **Tag consistently**: Use a standardized tag taxonomy

### 4. Campaign Tracking

Always track:
- Source of lead (LinkedIn, website, referral, etc.)
- All interactions (emails, calls, meetings)
- Engagement metrics (open rates, response rates)
- Conversion attribution

## Troubleshooting

### Common Issues

**Issue**: "Lead not qualified despite matching criteria"
- **Solution**: Check the AI's reasoning in the lead notes. The AI may consider factors beyond explicit criteria.

**Issue**: "Slow performance with large lead lists"
- **Solution**: Use pagination (`limit` and `offset`) and process in batches.

**Issue**: "Enrichment not working"
- **Solution**: Verify API keys for enrichment services (Clearbit, Hunter, etc.) are set in `.env`.

**Issue**: "Database locked error"
- **Solution**: SQLite doesn't handle concurrent writes well. Consider using PostgreSQL for production.

## Production Deployment

### Database Migration

For production, use PostgreSQL:

```bash
# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/leads

# Install PostgreSQL driver
pip install psycopg2-binary
```

### Scaling Considerations

1. **Use a proper database**: PostgreSQL or MySQL instead of SQLite
2. **Add caching**: Redis for frequently accessed leads
3. **Queue long-running tasks**: Use Celery for enrichment jobs
4. **API rate limiting**: Respect third-party API limits
5. **Monitoring**: Track API usage, lead volume, qualification rates

### Security Best Practices

1. **Encrypt sensitive data**: Use database encryption for emails/phones
2. **API key rotation**: Regularly rotate Anthropic and enrichment API keys
3. **Access control**: Implement role-based access to lead data
4. **Audit logging**: Track who accesses/modifies lead data
5. **GDPR compliance**: Implement data deletion and export features

## API Reference

### LeadEngineAgent Class

```python
class LeadEngineAgent:
    def __init__(self, api_key: str, mcp_client=None)

    async def process_lead_request(
        self,
        request: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]

    def add_lead(self, lead: Lead) -> str
    def get_lead(self, lead_id: str) -> Optional[Lead]
    def update_lead(self, lead_id: str, updates: Dict[str, Any]) -> bool
    def delete_lead(self, lead_id: str) -> bool
    def get_all_leads(self, filters: Dict[str, Any] = None) -> List[Lead]
    def export_leads(self, leads: List[Lead], format: str = 'json') -> str
```

### Lead Class

```python
@dataclass
class Lead:
    id: Optional[str]
    name: str
    email: str
    company: str
    title: str
    phone: Optional[str]
    linkedin_url: Optional[str]
    website: Optional[str]
    source: LeadSource
    status: LeadStatus
    score: int
    notes: str
    tags: List[str]
    custom_fields: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    last_contacted: Optional[datetime]
```

## Examples

See `examples/lead_engine_demo.py` for complete working examples.

## Support & Contributing

- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Join our Discord community
- **Contributing**: See CONTRIBUTING.md

## License

MIT License - See LICENSE file for details

---

**Built with ❤️ using Claude Agent SDK**
