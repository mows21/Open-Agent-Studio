# Lead Engine Agent 🎯

**AI-Powered Lead Generation & Management System built with Claude Agent SDK**

Transform your sales process with intelligent lead generation, qualification, scoring, and enrichment powered by Claude's advanced AI capabilities.

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/mows21/Open-Agent-Studio.git
cd Open-Agent-Studio

# Install lead engine dependencies
pip install -r requirements_lead_engine.txt

# Set up your API key
export ANTHROPIC_API_KEY='your-api-key-here'
```

### Run the Demo

```bash
python examples/lead_engine_demo.py
```

### Basic Usage

```python
from lead_engine_agent import LeadEngineAgent, Lead, LeadSource
import asyncio

# Initialize
agent = LeadEngineAgent(api_key="your-api-key")

# Add a lead
lead = Lead(
    name="John Smith",
    email="john@techcorp.com",
    company="TechCorp",
    title="VP of Engineering",
    source=LeadSource.LINKEDIN
)
agent.add_lead(lead)

# Use natural language to qualify leads
async def qualify():
    result = await agent.process_lead_request(
        "Qualify all leads for enterprise SaaS targeting VPs and CTOs"
    )
    print(result)

asyncio.run(qualify())
```

---

## ✨ Features

### 🤖 AI-Powered Intelligence
- **Natural Language Interface**: Describe what you want in plain English
- **Intelligent Qualification**: AI analyzes leads against your criteria
- **Smart Scoring**: Multi-factor scoring based on fit and potential
- **Contextual Reasoning**: See why each lead was qualified or scored

### 📊 Lead Management
- **Complete CRUD Operations**: Create, read, update, delete leads
- **Advanced Filtering**: Filter by status, score, tags, company, etc.
- **Tag System**: Categorize and segment leads flexibly
- **Interaction Tracking**: Log emails, calls, meetings, notes

### 🔄 Automation & Integration
- **MCP Server**: Model Context Protocol for tool integration
- **Browser Automation**: Scrape leads from LinkedIn, websites
- **Data Import/Export**: JSON and CSV support
- **Enrichment Ready**: Integrate with Clearbit, Hunter, Apollo

### 📈 Analytics & Reporting
- **Lead Statistics**: Real-time analytics on your pipeline
- **Score Distribution**: Visualize lead quality
- **Source Tracking**: Attribution across channels
- **Campaign Management**: Organize lead gen campaigns

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│      Natural Language Request       │
│  "Find qualified tech leads with    │
│   scores above 70"                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Lead Engine Agent              │
│      (Claude Agent SDK)             │
│  • Understands intent               │
│  • Plans execution                  │
│  • Orchestrates tools               │
└──────────────┬──────────────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│Lead MCP│ │Browser │ │Desktop │
│ Server │ │  MCP   │ │  MCP   │
└───┬────┘ └───┬────┘ └───┬────┘
    │          │          │
    └──────────┼──────────┘
               ▼
    ┌──────────────────┐
    │  Lead Database   │
    │  (SQLAlchemy)    │
    └──────────────────┘
```

---

## 📁 Project Structure

```
Open-Agent-Studio/
├── lead_engine_agent.py         # Core agent with AI logic
├── lead_database.py              # SQLAlchemy models & operations
├── requirements_lead_engine.txt  # Dependencies
├── README_LEAD_ENGINE.md         # This file
├── LEAD_ENGINE_GUIDE.md          # Comprehensive guide
│
├── mcp_servers/
│   └── lead_engine_mcp.py       # MCP server for tools
│
└── examples/
    └── lead_engine_demo.py      # Complete demo script
```

---

## 📖 Use Cases

### 1. Sales Development Representatives (SDRs)
```python
# Generate leads from LinkedIn
result = await agent.process_lead_request(
    "Find 50 VPs of Sales in SaaS companies in San Francisco"
)

# Qualify and prioritize
result = await agent.process_lead_request(
    "Score and rank all leads by likelihood to convert"
)

# Export for outreach
leads = agent.get_all_leads(filters={"status": "qualified"})
agent.export_leads(leads, format='csv')
```

### 2. Marketing Teams
```python
# Import leads from campaign
await agent.process_lead_request(
    "Import leads from webinar_attendees.csv"
)

# Segment for nurturing
result = await agent.process_lead_request(
    "Tag leads by company size and industry for targeted campaigns"
)

# Track campaign performance
stats = db.get_lead_stats()
```

### 3. Account Executives
```python
# Find high-value opportunities
high_value = agent.get_all_leads(filters={
    "min_score": 80,
    "status": "qualified"
})

# Enrich with additional data
result = await agent.process_lead_request(
    "Enrich top 20 leads with company and contact data"
)
```

---

## 🎓 Examples

### Example 1: Intelligent Lead Qualification

```python
# Define your ideal customer profile in natural language
result = await agent.process_lead_request(
    """Qualify leads for our enterprise SaaS product:
    - Target: VP-level and C-suite executives
    - Industries: Technology, SaaS, Software
    - Company size: 50-1000 employees
    - Must have complete contact information
    - Exclude consultants and agencies""",
    context={
        "min_score": 65,
        "disqualifying_keywords": ["consultant", "agency", "freelance"]
    }
)

# Claude analyzes each lead and provides reasoning
for lead in result['result']['leads']:
    print(f"{lead['name']}: {lead['score']}/100")
    print(f"Reasoning: {lead['notes']}")
```

### Example 2: Multi-Source Lead Generation

```python
# Generate from multiple sources
await agent.process_lead_request(
    "Generate leads from LinkedIn, company websites, and conference attendees"
)

# Deduplicate and score
await agent.process_lead_request(
    "Remove duplicates by email and score remaining leads"
)

# Export qualified leads
result = await agent.process_lead_request(
    "Export qualified leads with scores above 70 to salesforce_import.csv"
)
```

### Example 3: Lead Nurturing Campaign

```python
# Create campaign
campaign = db.create_campaign({
    "name": "Q4 Enterprise Outreach",
    "campaign_type": "email",
    "target_criteria": {
        "status": "qualified",
        "min_score": 70,
        "tags": ["enterprise"]
    }
})

# Find target leads
result = await agent.process_lead_request(
    "Find all qualified enterprise leads for Q4 campaign"
)

# Track interactions
for lead in target_leads:
    db.add_interaction({
        "lead_id": lead.id,
        "interaction_type": "email",
        "subject": "Exclusive Q4 Offer",
        "outcome": "sent"
    })
```

---

## 🛠️ MCP Tools

The Lead Engine MCP Server provides 14 tools:

| Tool | Description |
|------|-------------|
| `create_lead` | Create new lead |
| `get_lead` | Get lead by ID |
| `search_leads` | Search with filters |
| `update_lead` | Update lead info |
| `qualify_lead` | Qualify/disqualify lead |
| `score_lead` | Update lead score |
| `add_interaction` | Log interaction |
| `get_lead_interactions` | Get interaction history |
| `create_campaign` | Create campaign |
| `list_campaigns` | List campaigns |
| `get_lead_stats` | Get analytics |
| `export_leads` | Export to file |
| `import_leads` | Import from file |
| `enrich_lead` | Enrich with external data |

### Running the MCP Server

```bash
python mcp_servers/lead_engine_mcp.py
```

---

## 💾 Database Schema

### Leads
- Contact info (name, email, company, title, phone)
- URLs (LinkedIn, website)
- Metadata (source, status, score, notes)
- Custom fields (JSON)
- Timestamps

### Interactions
- Lead relationship
- Type (email, call, meeting, note)
- Subject, description, outcome
- Created by, timestamps

### Campaigns
- Name, description, type
- Target criteria
- Performance metrics
- Status tracking

### Scoring History
- Lead relationship
- Score changes
- Reasoning
- Attribution (AI, manual, system)

---

## 🔌 Integration Examples

### With CRM (Salesforce, HubSpot)

```python
# Export qualified leads for CRM import
qualified = agent.get_all_leads(filters={"status": "qualified"})
csv_data = agent.export_leads(qualified, format='csv')

# Upload to CRM (pseudo-code)
crm_client.import_leads(csv_data)
```

### With Email Marketing (Mailchimp, SendGrid)

```python
# Get leads for email campaign
campaign_leads = agent.get_all_leads(filters={
    "tags": ["nurture"],
    "min_score": 50
})

# Sync to email platform
for lead in campaign_leads:
    email_platform.add_subscriber({
        "email": lead.email,
        "name": lead.name,
        "tags": lead.tags
    })
```

### With Enrichment APIs (Clearbit, Hunter)

```python
# The lead engine includes mock enrichment
# Integrate real APIs:

import clearbit

clearbit.key = 'your_clearbit_key'

for lead in high_value_leads:
    # Enrich with Clearbit
    person = clearbit.Person.find(email=lead.email)
    company = clearbit.Company.find(domain=lead.company_domain)

    # Update lead
    agent.update_lead(lead.id, {
        'custom_fields': {
            'clearbit_person': person,
            'clearbit_company': company
        }
    })
```

---

## 📊 Performance & Scaling

### SQLite (Development)
- Perfect for < 10,000 leads
- Zero configuration
- Single file database

### PostgreSQL (Production)
- Recommended for > 10,000 leads
- Concurrent access
- Better performance

```bash
# Switch to PostgreSQL
export DATABASE_URL="postgresql://user:pass@localhost/leads"
```

### Optimization Tips
1. **Index frequently queried fields** (email, company, status)
2. **Use pagination** for large result sets
3. **Batch AI operations** to reduce API calls
4. **Cache enrichment results** to avoid duplicate lookups
5. **Queue long-running tasks** with Celery

---

## 🔒 Security & Compliance

### Data Protection
- Encrypt sensitive fields (emails, phones)
- Hash API keys
- Use secure connections
- Regular backups

### GDPR Compliance
```python
# Right to deletion
agent.delete_lead(lead_id)

# Right to data export
lead_data = agent.get_lead(lead_id).to_dict()
```

### Access Control
- Implement user authentication
- Role-based permissions
- Audit logging

---

## 🧪 Testing

Run the comprehensive demo:
```bash
python examples/lead_engine_demo.py
```

This tests:
- ✅ Lead CRUD operations
- ✅ AI qualification (requires API key)
- ✅ AI scoring (requires API key)
- ✅ Filtering and search
- ✅ Import/Export
- ✅ Analytics
- ✅ Database operations

---

## 📚 Documentation

- **[LEAD_ENGINE_GUIDE.md](LEAD_ENGINE_GUIDE.md)** - Comprehensive guide
- **[examples/lead_engine_demo.py](examples/lead_engine_demo.py)** - Working examples
- **Code Comments** - Detailed inline documentation

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Additional enrichment API integrations
- [ ] More sophisticated scoring algorithms
- [ ] UI/dashboard for lead management
- [ ] Advanced analytics and reporting
- [ ] Integration with more CRMs
- [ ] Bulk operations optimization
- [ ] Real-time lead generation workflows

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

Built with:
- **[Claude Agent SDK](https://docs.anthropic.com/)** by Anthropic
- **[SQLAlchemy](https://www.sqlalchemy.org/)** for database ORM
- **[MCP](https://modelcontextprotocol.io/)** for tool integration

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/mows21/Open-Agent-Studio/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mows21/Open-Agent-Studio/discussions)
- **Documentation**: See `LEAD_ENGINE_GUIDE.md`

---

## 🎯 What's Next?

1. **Try the demo**: `python examples/lead_engine_demo.py`
2. **Read the guide**: `LEAD_ENGINE_GUIDE.md`
3. **Build your first workflow**: Start with lead import/export
4. **Integrate with your stack**: CRM, email marketing, etc.
5. **Scale up**: Move to PostgreSQL for production

---

**Ready to transform your lead generation? Get started now! 🚀**
