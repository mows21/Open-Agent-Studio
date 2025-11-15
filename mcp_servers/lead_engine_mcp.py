"""
Lead Engine MCP Server - Model Context Protocol server for lead operations

Provides MCP tools for:
- Lead generation and capture
- Lead qualification and scoring
- Lead enrichment
- Lead management (CRUD)
- Campaign management
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lead_database import (
    LeadDatabase, LeadDB, InteractionDB, CampaignDB,
    LeadStatusEnum, LeadSourceEnum
)

try:
    from mcp.server import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    import mcp.types as types
except ImportError:
    print("Warning: MCP not installed. Install with: pip install mcp")
    # Mock classes for development
    class Server:
        def __init__(self, name):
            self.name = name

    class types:
        @staticmethod
        def Tool(*args, **kwargs):
            pass


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lead_engine_mcp")

# Initialize database
db = LeadDatabase()

# Create MCP server
server = Server("lead-engine-mcp")


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    List available lead engine tools
    """
    return [
        types.Tool(
            name="create_lead",
            description="Create a new lead in the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Lead's full name"
                    },
                    "email": {
                        "type": "string",
                        "description": "Lead's email address"
                    },
                    "company": {
                        "type": "string",
                        "description": "Company name"
                    },
                    "title": {
                        "type": "string",
                        "description": "Job title"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Phone number (optional)"
                    },
                    "linkedin_url": {
                        "type": "string",
                        "description": "LinkedIn profile URL (optional)"
                    },
                    "website": {
                        "type": "string",
                        "description": "Company website (optional)"
                    },
                    "source": {
                        "type": "string",
                        "description": "Lead source (linkedin, website, email, referral, etc.)"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags for categorizing the lead"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Additional notes about the lead"
                    }
                },
                "required": ["name", "email", "company"]
            }
        ),
        types.Tool(
            name="get_lead",
            description="Get lead information by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "lead_id": {
                        "type": "integer",
                        "description": "Lead ID"
                    }
                },
                "required": ["lead_id"]
            }
        ),
        types.Tool(
            name="search_leads",
            description="Search and filter leads",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by status (new, contacted, qualified, etc.)"
                    },
                    "min_score": {
                        "type": "integer",
                        "description": "Minimum lead score"
                    },
                    "max_score": {
                        "type": "integer",
                        "description": "Maximum lead score"
                    },
                    "company": {
                        "type": "string",
                        "description": "Filter by company name (partial match)"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 100
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Offset for pagination",
                        "default": 0
                    }
                }
            }
        ),
        types.Tool(
            name="update_lead",
            description="Update lead information",
            inputSchema={
                "type": "object",
                "properties": {
                    "lead_id": {
                        "type": "integer",
                        "description": "Lead ID to update"
                    },
                    "updates": {
                        "type": "object",
                        "description": "Fields to update (name, email, company, title, status, score, etc.)"
                    }
                },
                "required": ["lead_id", "updates"]
            }
        ),
        types.Tool(
            name="qualify_lead",
            description="Qualify a lead and update status",
            inputSchema={
                "type": "object",
                "properties": {
                    "lead_id": {
                        "type": "integer",
                        "description": "Lead ID to qualify"
                    },
                    "qualified": {
                        "type": "boolean",
                        "description": "Whether the lead is qualified"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Qualification reason"
                    },
                    "score": {
                        "type": "integer",
                        "description": "Updated lead score (0-100)"
                    }
                },
                "required": ["lead_id", "qualified"]
            }
        ),
        types.Tool(
            name="score_lead",
            description="Update lead score",
            inputSchema={
                "type": "object",
                "properties": {
                    "lead_id": {
                        "type": "integer",
                        "description": "Lead ID"
                    },
                    "score": {
                        "type": "integer",
                        "description": "New score (0-100)"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for score change"
                    }
                },
                "required": ["lead_id", "score"]
            }
        ),
        types.Tool(
            name="add_interaction",
            description="Add interaction/activity to a lead",
            inputSchema={
                "type": "object",
                "properties": {
                    "lead_id": {
                        "type": "integer",
                        "description": "Lead ID"
                    },
                    "interaction_type": {
                        "type": "string",
                        "description": "Type of interaction (email, call, meeting, note, etc.)"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Interaction subject"
                    },
                    "description": {
                        "type": "string",
                        "description": "Interaction details"
                    },
                    "outcome": {
                        "type": "string",
                        "description": "Outcome (positive, negative, neutral, no_response)"
                    }
                },
                "required": ["lead_id", "interaction_type", "description"]
            }
        ),
        types.Tool(
            name="get_lead_interactions",
            description="Get interaction history for a lead",
            inputSchema={
                "type": "object",
                "properties": {
                    "lead_id": {
                        "type": "integer",
                        "description": "Lead ID"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of interactions to return",
                        "default": 50
                    }
                },
                "required": ["lead_id"]
            }
        ),
        types.Tool(
            name="create_campaign",
            description="Create a lead generation/nurturing campaign",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Campaign name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Campaign description"
                    },
                    "campaign_type": {
                        "type": "string",
                        "description": "Campaign type (email, linkedin, cold_call, etc.)"
                    },
                    "target_criteria": {
                        "type": "object",
                        "description": "Target lead criteria (filters)"
                    }
                },
                "required": ["name", "campaign_type"]
            }
        ),
        types.Tool(
            name="list_campaigns",
            description="List campaigns",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by campaign status (draft, active, paused, completed)"
                    }
                }
            }
        ),
        types.Tool(
            name="get_lead_stats",
            description="Get lead statistics and analytics",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="export_leads",
            description="Export leads to JSON or CSV",
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Filters for which leads to export"
                    },
                    "format": {
                        "type": "string",
                        "description": "Export format (json or csv)",
                        "enum": ["json", "csv"],
                        "default": "json"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Output filename"
                    }
                },
                "required": ["filename"]
            }
        ),
        types.Tool(
            name="import_leads",
            description="Import leads from JSON or CSV file",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Input filename"
                    },
                    "format": {
                        "type": "string",
                        "description": "Import format (json or csv)",
                        "enum": ["json", "csv"],
                        "default": "json"
                    },
                    "source": {
                        "type": "string",
                        "description": "Source identifier for imported leads"
                    }
                },
                "required": ["filename"]
            }
        ),
        types.Tool(
            name="enrich_lead",
            description="Enrich lead with additional data from external sources",
            inputSchema={
                "type": "object",
                "properties": {
                    "lead_id": {
                        "type": "integer",
                        "description": "Lead ID to enrich"
                    },
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Enrichment sources (clearbit, hunter, apollo, etc.)"
                    }
                },
                "required": ["lead_id"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict
) -> List[types.TextContent]:
    """
    Handle tool execution
    """
    try:
        logger.info(f"Executing tool: {name} with args: {arguments}")

        if name == "create_lead":
            result = await create_lead_tool(arguments)

        elif name == "get_lead":
            result = await get_lead_tool(arguments)

        elif name == "search_leads":
            result = await search_leads_tool(arguments)

        elif name == "update_lead":
            result = await update_lead_tool(arguments)

        elif name == "qualify_lead":
            result = await qualify_lead_tool(arguments)

        elif name == "score_lead":
            result = await score_lead_tool(arguments)

        elif name == "add_interaction":
            result = await add_interaction_tool(arguments)

        elif name == "get_lead_interactions":
            result = await get_lead_interactions_tool(arguments)

        elif name == "create_campaign":
            result = await create_campaign_tool(arguments)

        elif name == "list_campaigns":
            result = await list_campaigns_tool(arguments)

        elif name == "get_lead_stats":
            result = await get_lead_stats_tool(arguments)

        elif name == "export_leads":
            result = await export_leads_tool(arguments)

        elif name == "import_leads":
            result = await import_leads_tool(arguments)

        elif name == "enrich_lead":
            result = await enrich_lead_tool(arguments)

        else:
            result = {"error": f"Unknown tool: {name}"}

        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": str(e)})
        )]


# Tool implementations
async def create_lead_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new lead"""
    try:
        lead = db.create_lead(args)
        return {
            "success": True,
            "lead": lead.to_dict(),
            "message": f"Created lead: {lead.name}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_lead_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get lead by ID"""
    lead = db.get_lead(args['lead_id'])
    if lead:
        return {
            "success": True,
            "lead": lead.to_dict()
        }
    return {
        "success": False,
        "error": f"Lead not found: {args['lead_id']}"
    }


async def search_leads_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Search leads with filters"""
    limit = args.pop('limit', 100)
    offset = args.pop('offset', 0)

    leads = db.list_leads(filters=args, limit=limit, offset=offset)

    return {
        "success": True,
        "leads": [lead.to_dict() for lead in leads],
        "count": len(leads),
        "limit": limit,
        "offset": offset
    }


async def update_lead_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Update lead"""
    lead_id = args['lead_id']
    updates = args['updates']

    lead = db.update_lead(lead_id, updates)
    if lead:
        return {
            "success": True,
            "lead": lead.to_dict(),
            "message": f"Updated lead: {lead_id}"
        }
    return {
        "success": False,
        "error": f"Lead not found: {lead_id}"
    }


async def qualify_lead_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Qualify a lead"""
    lead_id = args['lead_id']
    qualified = args['qualified']
    reason = args.get('reason', '')
    score = args.get('score')

    updates = {
        'status': LeadStatusEnum.QUALIFIED if qualified else LeadStatusEnum.UNQUALIFIED
    }

    if reason:
        lead = db.get_lead(lead_id)
        if lead:
            updates['notes'] = lead.notes + f"\n[Qualification] {reason}"

    if score is not None:
        db.update_lead_score(lead_id, score, reason=reason, changed_by='qualification')

    lead = db.update_lead(lead_id, updates)
    if lead:
        return {
            "success": True,
            "lead": lead.to_dict(),
            "message": f"Lead {'qualified' if qualified else 'unqualified'}"
        }
    return {
        "success": False,
        "error": f"Lead not found: {lead_id}"
    }


async def score_lead_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Score a lead"""
    lead_id = args['lead_id']
    score = args['score']
    reason = args.get('reason', 'Manual score update')

    success = db.update_lead_score(lead_id, score, reason=reason, changed_by='manual')

    if success:
        lead = db.get_lead(lead_id)
        return {
            "success": True,
            "lead": lead.to_dict() if lead else None,
            "message": f"Updated score to {score}"
        }
    return {
        "success": False,
        "error": f"Lead not found: {lead_id}"
    }


async def add_interaction_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Add interaction to lead"""
    interaction = db.add_interaction(args)
    return {
        "success": True,
        "interaction": interaction.to_dict(),
        "message": "Interaction added"
    }


async def get_lead_interactions_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get lead interactions"""
    lead_id = args['lead_id']
    limit = args.get('limit', 50)

    interactions = db.get_lead_interactions(lead_id, limit=limit)

    return {
        "success": True,
        "interactions": [i.to_dict() for i in interactions],
        "count": len(interactions)
    }


async def create_campaign_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Create campaign"""
    campaign = db.create_campaign(args)
    return {
        "success": True,
        "campaign": campaign.to_dict(),
        "message": f"Created campaign: {campaign.name}"
    }


async def list_campaigns_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """List campaigns"""
    status = args.get('status')
    campaigns = db.list_campaigns(status=status)

    return {
        "success": True,
        "campaigns": [c.to_dict() for c in campaigns],
        "count": len(campaigns)
    }


async def get_lead_stats_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get lead statistics"""
    stats = db.get_lead_stats()
    return {
        "success": True,
        "stats": stats
    }


async def export_leads_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Export leads to file"""
    filters = args.get('filters', {})
    format_type = args.get('format', 'json')
    filename = args['filename']

    leads = db.list_leads(filters=filters, limit=10000)

    if format_type == 'json':
        data = json.dumps([lead.to_dict() for lead in leads], indent=2, default=str)
    elif format_type == 'csv':
        # Simple CSV export
        if not leads:
            data = ""
        else:
            headers = ['id', 'name', 'email', 'company', 'title', 'phone', 'score', 'status', 'source']
            rows = [','.join(headers)]
            for lead in leads:
                row = [
                    str(lead.id),
                    lead.name,
                    lead.email,
                    lead.company,
                    lead.title or '',
                    lead.phone or '',
                    str(lead.score),
                    lead.status.value,
                    lead.source.value
                ]
                rows.append(','.join(f'"{item}"' for item in row))
            data = '\n'.join(rows)
    else:
        return {"success": False, "error": f"Unsupported format: {format_type}"}

    # Write to file
    with open(filename, 'w') as f:
        f.write(data)

    return {
        "success": True,
        "filename": filename,
        "format": format_type,
        "count": len(leads),
        "message": f"Exported {len(leads)} leads to {filename}"
    }


async def import_leads_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Import leads from file"""
    filename = args['filename']
    format_type = args.get('format', 'json')
    source = args.get('source', 'import')

    if not os.path.exists(filename):
        return {"success": False, "error": f"File not found: {filename}"}

    with open(filename, 'r') as f:
        data = f.read()

    imported_count = 0
    errors = []

    if format_type == 'json':
        try:
            leads_data = json.loads(data)
            for lead_data in leads_data:
                try:
                    if 'source' not in lead_data:
                        lead_data['source'] = source
                    db.create_lead(lead_data)
                    imported_count += 1
                except Exception as e:
                    errors.append(f"Error importing {lead_data.get('email', 'unknown')}: {str(e)}")
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Invalid JSON: {str(e)}"}

    elif format_type == 'csv':
        lines = data.strip().split('\n')
        if len(lines) < 2:
            return {"success": False, "error": "CSV file is empty"}

        headers = [h.strip('"') for h in lines[0].split(',')]

        for line in lines[1:]:
            try:
                values = [v.strip('"') for v in line.split(',')]
                lead_data = dict(zip(headers, values))
                if 'source' not in lead_data:
                    lead_data['source'] = source
                db.create_lead(lead_data)
                imported_count += 1
            except Exception as e:
                errors.append(f"Error importing line: {str(e)}")

    return {
        "success": True,
        "imported_count": imported_count,
        "errors": errors[:10],  # Return first 10 errors
        "message": f"Imported {imported_count} leads from {filename}"
    }


async def enrich_lead_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich lead with external data"""
    lead_id = args['lead_id']
    sources = args.get('sources', ['clearbit'])

    lead = db.get_lead(lead_id)
    if not lead:
        return {"success": False, "error": f"Lead not found: {lead_id}"}

    # Mock enrichment - in production, integrate with actual APIs
    enrichment_data = {}

    for source in sources:
        if source == 'clearbit':
            # Would call Clearbit API here
            enrichment_data['clearbit'] = {
                "enriched_at": datetime.now().isoformat(),
                "company_size": "50-100",
                "industry": "Technology"
            }
        elif source == 'hunter':
            # Would call Hunter API here
            enrichment_data['hunter'] = {
                "email_verified": True,
                "confidence": 95
            }

    # Update lead with enrichment data
    custom_fields = lead.custom_fields or {}
    custom_fields['enrichment'] = enrichment_data

    db.update_lead(lead_id, {'custom_fields': custom_fields})

    return {
        "success": True,
        "lead_id": lead_id,
        "enrichment_sources": sources,
        "enrichment_data": enrichment_data,
        "message": f"Enriched lead from {len(sources)} sources"
    }


async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="lead-engine-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
