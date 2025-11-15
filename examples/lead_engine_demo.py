"""
Lead Engine Agent - Complete Demo

This script demonstrates all major features of the Lead Engine Agent:
1. Basic lead management (create, read, update, delete)
2. AI-powered lead qualification
3. AI-powered lead scoring
4. Lead enrichment
5. Campaign management
6. Analytics and reporting
7. Import/Export functionality
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lead_engine_agent import (
    LeadEngineAgent, Lead, LeadSource, LeadStatus, LeadQualificationCriteria
)
from lead_database import LeadDatabase


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


async def demo_basic_operations(agent: LeadEngineAgent):
    """Demonstrate basic CRUD operations"""
    print_section("1. Basic Lead Management")

    # Create sample leads
    sample_leads = [
        Lead(
            name="Alice Johnson",
            email="alice.johnson@techcorp.com",
            company="TechCorp Inc",
            title="VP of Engineering",
            phone="+1-555-0101",
            linkedin_url="https://linkedin.com/in/alicejohnson",
            source=LeadSource.LINKEDIN,
            tags=["tech", "enterprise", "hot-lead"]
        ),
        Lead(
            name="Bob Smith",
            email="bob@startup.io",
            company="StartupIO",
            title="CTO",
            phone="+1-555-0102",
            linkedin_url="https://linkedin.com/in/bobsmith",
            source=LeadSource.REFERRAL,
            tags=["tech", "startup"]
        ),
        Lead(
            name="Carol Williams",
            email="carol.w@bigcorp.com",
            company="BigCorp Ltd",
            title="Director of IT",
            phone="+1-555-0103",
            source=LeadSource.WEBSITE,
            tags=["enterprise", "it"]
        ),
        Lead(
            name="David Chen",
            email="david.chen@innovate.com",
            company="Innovate Systems",
            title="Head of Product",
            linkedin_url="https://linkedin.com/in/davidchen",
            source=LeadSource.COLD_OUTREACH,
            tags=["product", "saas"]
        ),
        Lead(
            name="Emma Davis",
            email="emma.davis@consulting.com",
            company="Davis Consulting",
            title="Senior Consultant",
            phone="+1-555-0105",
            source=LeadSource.EMAIL,
            tags=["consulting", "small-business"]
        )
    ]

    lead_ids = []
    for lead in sample_leads:
        lead_id = agent.add_lead(lead)
        lead_ids.append(lead_id)
        print(f"✓ Created lead: {lead.name} ({lead.company}) - ID: {lead_id}")

    print(f"\nTotal leads created: {len(lead_ids)}")

    # Read a lead
    print(f"\n--- Reading Lead Details ---")
    lead = agent.get_lead(lead_ids[0])
    if lead:
        print(f"Name: {lead.name}")
        print(f"Company: {lead.company}")
        print(f"Title: {lead.title}")
        print(f"Email: {lead.email}")
        print(f"Tags: {', '.join(lead.tags)}")

    # Update a lead
    print(f"\n--- Updating Lead ---")
    agent.update_lead(lead_ids[0], {
        "score": 75,
        "notes": "High priority - expressed interest in our product",
        "status": LeadStatus.CONTACTED
    })
    print(f"✓ Updated lead {lead_ids[0]} with new score and notes")

    # Get all leads
    print(f"\n--- All Leads ---")
    all_leads = agent.get_all_leads()
    for lead in all_leads:
        print(f"  • {lead.name} - {lead.company} (Score: {lead.score})")

    return lead_ids


async def demo_ai_qualification(agent: LeadEngineAgent):
    """Demonstrate AI-powered lead qualification"""
    print_section("2. AI-Powered Lead Qualification")

    print("Qualifying leads for enterprise SaaS product...")
    print("Target: VPs and C-level in tech companies\n")

    result = await agent.process_lead_request(
        """Qualify leads for our enterprise SaaS product targeting:
        - VPs, CTOs, and C-level executives
        - Technology companies
        - Strong preference for companies with 'Corp', 'Systems', or 'Tech' in name
        - Must have valid contact information""",
        context={
            "min_score": 60,
            "target_titles": ["VP", "CTO", "CEO", "Director", "Head"],
            "industries": ["Technology", "Software", "SaaS"]
        }
    )

    if result["success"]:
        qualified = result["result"]["leads"]
        print(f"✓ Qualified {len(qualified)} out of {result['result']['total_analyzed']} leads\n")

        for lead_data in qualified:
            print(f"  ✓ {lead_data['name']} - {lead_data['title']} at {lead_data['company']}")
            print(f"    Score: {lead_data['score']} | Status: {lead_data['status']}")
            # Show AI reasoning (from notes)
            if '[AI Qualification]' in lead_data.get('notes', ''):
                reasoning = lead_data['notes'].split('[AI Qualification]')[-1].strip()
                print(f"    Reasoning: {reasoning[:100]}...")
            print()
    else:
        print(f"✗ Qualification failed: {result['error']}")


async def demo_ai_scoring(agent: LeadEngineAgent):
    """Demonstrate AI-powered lead scoring"""
    print_section("3. AI-Powered Lead Scoring")

    print("Scoring all leads based on:")
    print("  • Job title seniority (25 points)")
    print("  • Company fit (25 points)")
    print("  • Contact information completeness (20 points)")
    print("  • Engagement potential (30 points)\n")

    result = await agent.process_lead_request(
        "Score all leads based on job title seniority, company type, contact completeness, and engagement potential"
    )

    if result["success"]:
        leads = result["result"]["leads"]
        avg_score = result["result"]["average_score"]

        print(f"✓ Scored {len(leads)} leads (Average score: {avg_score:.1f})\n")
        print("Top leads by score:")

        # Sort by score
        leads_sorted = sorted(leads, key=lambda x: x["score"], reverse=True)

        for i, lead_data in enumerate(leads_sorted[:5], 1):
            print(f"  {i}. {lead_data['name']} - Score: {lead_data['score']}/100")
            print(f"     {lead_data['title']} at {lead_data['company']}")
            if '[AI Scoring]' in lead_data.get('notes', ''):
                scoring_info = lead_data['notes'].split('[AI Scoring]')[-1].strip()
                print(f"     {scoring_info[:80]}...")
            print()
    else:
        print(f"✗ Scoring failed: {result['error']}")


async def demo_filtering_and_search(agent: LeadEngineAgent):
    """Demonstrate lead filtering and search"""
    print_section("4. Lead Filtering & Search")

    # Filter by status
    print("--- Filtering by Status ---")
    qualified_leads = agent.get_all_leads(filters={"status": "qualified"})
    print(f"Qualified leads: {len(qualified_leads)}")
    for lead in qualified_leads:
        print(f"  • {lead.name} ({lead.company})")

    # Filter by score
    print("\n--- High-Value Leads (Score >= 70) ---")
    high_value = agent.get_all_leads(filters={"min_score": 70})
    print(f"High-value leads: {len(high_value)}")
    for lead in high_value:
        print(f"  • {lead.name} - Score: {lead.score}")

    # Filter by tags
    print("\n--- Leads Tagged 'enterprise' ---")
    enterprise_leads = agent.get_all_leads(filters={"tags": ["enterprise"]})
    print(f"Enterprise leads: {len(enterprise_leads)}")
    for lead in enterprise_leads:
        print(f"  • {lead.name} ({lead.company})")


async def demo_export_import(agent: LeadEngineAgent):
    """Demonstrate import/export functionality"""
    print_section("5. Import & Export")

    # Export to JSON
    print("--- Exporting Qualified Leads to JSON ---")
    qualified_leads = agent.get_all_leads(filters={"status": "qualified"})

    if qualified_leads:
        json_export = agent.export_leads(qualified_leads, format='json')

        filename = "qualified_leads_export.json"
        with open(filename, 'w') as f:
            f.write(json_export)

        print(f"✓ Exported {len(qualified_leads)} qualified leads to {filename}")
        print(f"  File size: {len(json_export)} bytes")
    else:
        print("No qualified leads to export")

    # Export to CSV
    print("\n--- Exporting All Leads to CSV ---")
    all_leads = agent.get_all_leads()

    if all_leads:
        csv_export = agent.export_leads(all_leads, format='csv')

        filename = "all_leads_export.csv"
        with open(filename, 'w') as f:
            f.write(csv_export)

        print(f"✓ Exported {len(all_leads)} leads to {filename}")
        print(f"  File size: {len(csv_export)} bytes")

        # Show first few lines
        print("\n  Preview:")
        for line in csv_export.split('\n')[:3]:
            print(f"  {line}")


async def demo_analytics(agent: LeadEngineAgent):
    """Demonstrate analytics and reporting"""
    print_section("6. Analytics & Reporting")

    all_leads = agent.get_all_leads()

    # Status breakdown
    print("--- Lead Status Breakdown ---")
    status_counts = {}
    for lead in all_leads:
        status = lead.status.value
        status_counts[status] = status_counts.get(status, 0) + 1

    for status, count in sorted(status_counts.items()):
        percentage = (count / len(all_leads) * 100) if all_leads else 0
        print(f"  {status.upper():<15} : {count:>3} ({percentage:>5.1f}%)")

    # Source breakdown
    print("\n--- Lead Source Breakdown ---")
    source_counts = {}
    for lead in all_leads:
        source = lead.source.value
        source_counts[source] = source_counts.get(source, 0) + 1

    for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(all_leads) * 100) if all_leads else 0
        print(f"  {source.upper():<15} : {count:>3} ({percentage:>5.1f}%)")

    # Score distribution
    print("\n--- Lead Score Distribution ---")
    if all_leads:
        scores = [lead.score for lead in all_leads]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)

        print(f"  Average Score: {avg_score:.1f}")
        print(f"  Highest Score: {max_score}")
        print(f"  Lowest Score:  {min_score}")

        # Score ranges
        ranges = {
            "0-25 (Low)": 0,
            "26-50 (Medium)": 0,
            "51-75 (High)": 0,
            "76-100 (Excellent)": 0
        }

        for score in scores:
            if score <= 25:
                ranges["0-25 (Low)"] += 1
            elif score <= 50:
                ranges["26-50 (Medium)"] += 1
            elif score <= 75:
                ranges["51-75 (High)"] += 1
            else:
                ranges["76-100 (Excellent)"] += 1

        print("\n  Score Ranges:")
        for range_name, count in ranges.items():
            percentage = (count / len(all_leads) * 100) if all_leads else 0
            bar = "█" * int(percentage / 5)
            print(f"  {range_name:<20} : {bar} {count} ({percentage:.1f}%)")

    # Tag analytics
    print("\n--- Most Used Tags ---")
    tag_counts = {}
    for lead in all_leads:
        for tag in lead.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  #{tag:<15} : {count} leads")


async def demo_database_operations():
    """Demonstrate direct database operations"""
    print_section("7. Database Operations (Advanced)")

    db = LeadDatabase()

    # Get statistics
    print("--- Database Statistics ---")
    stats = db.get_lead_stats()
    print(json.dumps(stats, indent=2))

    # Add interaction
    print("\n--- Adding Interaction ---")
    leads = db.list_leads(limit=1)
    if leads:
        lead = leads[0]
        interaction = db.add_interaction({
            "lead_id": lead.id,
            "interaction_type": "email",
            "subject": "Product Demo Request",
            "description": "Sent initial email requesting a product demo",
            "outcome": "positive",
            "created_by": "demo_script"
        })
        print(f"✓ Added interaction to {lead.name}")
        print(f"  Type: {interaction.interaction_type}")
        print(f"  Subject: {interaction.subject}")

    # List tags
    print("\n--- Available Tags ---")
    tags = db.list_tags()
    for tag in tags:
        print(f"  • {tag.name} ({len(tag.leads)} leads)")


async def demo_custom_criteria():
    """Demonstrate custom qualification criteria"""
    print_section("8. Custom Qualification Criteria")

    # Create strict enterprise criteria
    criteria = LeadQualificationCriteria(
        required_fields=['name', 'email', 'company', 'title', 'phone'],
        company_size_min=50,
        company_size_max=1000,
        industries=['Technology', 'Software', 'SaaS'],
        job_titles=['VP', 'CTO', 'CEO', 'Director', 'Head of'],
        min_score=70,
        disqualifying_keywords=['student', 'intern', 'looking for job']
    )

    print("Custom Enterprise Criteria:")
    print(f"  • Required fields: {', '.join(criteria.required_fields)}")
    print(f"  • Company size: {criteria.company_size_min}-{criteria.company_size_max}")
    print(f"  • Target industries: {', '.join(criteria.industries)}")
    print(f"  • Target titles: {', '.join(criteria.job_titles)}")
    print(f"  • Minimum score: {criteria.min_score}")
    print(f"  • Disqualifying keywords: {', '.join(criteria.disqualifying_keywords)}")

    print("\n(In production, this would be used in qualification workflows)")


async def main():
    """Run complete demo"""
    print("\n" + "=" * 70)
    print("  LEAD ENGINE AGENT - COMPREHENSIVE DEMO")
    print("=" * 70)

    # Get API key from environment
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        print("\n⚠️  WARNING: ANTHROPIC_API_KEY not set in environment")
        print("    AI-powered features will be limited in this demo")
        print("    Set your API key with: export ANTHROPIC_API_KEY='your-key'\n")
        api_key = "demo-key"  # Placeholder for demo

    # Initialize agent
    agent = LeadEngineAgent(api_key=api_key)

    try:
        # Run demos
        lead_ids = await demo_basic_operations(agent)

        if api_key != "demo-key":
            # Only run AI demos if we have a real API key
            await demo_ai_qualification(agent)
            await demo_ai_scoring(agent)
        else:
            print_section("2-3. AI Features (Skipped - No API Key)")
            print("Set ANTHROPIC_API_KEY to see AI qualification and scoring demos")

        await demo_filtering_and_search(agent)
        await demo_export_import(agent)
        await demo_analytics(agent)
        await demo_database_operations()
        await demo_custom_criteria()

        # Final summary
        print_section("Demo Complete!")
        print("✓ Created and managed leads")
        if api_key != "demo-key":
            print("✓ Performed AI qualification and scoring")
        print("✓ Filtered and searched leads")
        print("✓ Exported leads to JSON and CSV")
        print("✓ Analyzed lead distribution and metrics")
        print("✓ Demonstrated database operations")
        print("✓ Showed custom qualification criteria")

        print("\nNext steps:")
        print("  1. Review exported files: qualified_leads_export.json, all_leads_export.csv")
        print("  2. Explore the Lead Engine Guide: LEAD_ENGINE_GUIDE.md")
        print("  3. Integrate with your CRM or sales workflow")
        print("  4. Set up automated lead generation workflows")

        print("\n" + "=" * 70 + "\n")

    except Exception as e:
        print(f"\n✗ Demo error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
