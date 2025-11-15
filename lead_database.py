"""
Lead Database Models - SQLAlchemy models for persistent lead storage

Provides database models and operations for the Lead Engine Agent
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime,
    Text, Float, JSON, ForeignKey, Table, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import enum

Base = declarative_base()


# Association table for lead tags (many-to-many)
lead_tags = Table(
    'lead_tags',
    Base.metadata,
    Column('lead_id', Integer, ForeignKey('leads.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)


class LeadStatusEnum(enum.Enum):
    """Lead status enumeration for database"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    NURTURING = "nurturing"
    CONVERTED = "converted"
    LOST = "lost"


class LeadSourceEnum(enum.Enum):
    """Lead source enumeration for database"""
    LINKEDIN = "linkedin"
    WEBSITE = "website"
    EMAIL = "email"
    REFERRAL = "referral"
    COLD_OUTREACH = "cold_outreach"
    SOCIAL_MEDIA = "social_media"
    MANUAL = "manual"
    API = "api"


class LeadDB(Base):
    """SQLAlchemy Lead model"""
    __tablename__ = 'leads'

    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(255), unique=True, nullable=True)

    # Contact information
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    title = Column(String(255))
    phone = Column(String(50))

    # URLs
    linkedin_url = Column(String(500))
    website = Column(String(500))

    # Metadata
    source = Column(SQLEnum(LeadSourceEnum), default=LeadSourceEnum.MANUAL)
    status = Column(SQLEnum(LeadStatusEnum), default=LeadStatusEnum.NEW, index=True)
    score = Column(Integer, default=0, index=True)

    # Notes and custom data
    notes = Column(Text, default="")
    custom_fields = Column(JSON, default={})

    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    last_contacted = Column(DateTime, nullable=True)

    # Relationships
    tags = relationship("TagDB", secondary=lead_tags, back_populates="leads")
    interactions = relationship("InteractionDB", back_populates="lead", cascade="all, delete-orphan")
    scoring_history = relationship("LeadScoreHistoryDB", back_populates="lead", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'external_id': self.external_id,
            'name': self.name,
            'email': self.email,
            'company': self.company,
            'title': self.title,
            'phone': self.phone,
            'linkedin_url': self.linkedin_url,
            'website': self.website,
            'source': self.source.value if self.source else None,
            'status': self.status.value if self.status else None,
            'score': self.score,
            'notes': self.notes,
            'custom_fields': self.custom_fields or {},
            'tags': [tag.name for tag in self.tags],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_contacted': self.last_contacted.isoformat() if self.last_contacted else None,
        }


class TagDB(Base):
    """Tag model for categorizing leads"""
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), default="#3B82F6")  # Hex color code
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    leads = relationship("LeadDB", secondary=lead_tags, back_populates="tags")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'lead_count': len(self.leads)
        }


class InteractionDB(Base):
    """Interaction/Activity model for tracking lead engagement"""
    __tablename__ = 'interactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=False)

    interaction_type = Column(String(50), nullable=False)  # email, call, meeting, note, etc.
    subject = Column(String(500))
    description = Column(Text)
    outcome = Column(String(100))  # positive, negative, neutral, no_response

    # Metadata
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    created_by = Column(String(255))  # User who created the interaction
    metadata = Column(JSON, default={})

    # Relationships
    lead = relationship("LeadDB", back_populates="interactions")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'interaction_type': self.interaction_type,
            'subject': self.subject,
            'description': self.description,
            'outcome': self.outcome,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'metadata': self.metadata or {}
        }


class LeadScoreHistoryDB(Base):
    """Track lead score changes over time"""
    __tablename__ = 'lead_score_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=False)

    old_score = Column(Integer)
    new_score = Column(Integer, nullable=False)
    reason = Column(Text)  # Why the score changed
    changed_by = Column(String(100))  # 'ai', 'manual', 'system'

    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # Relationships
    lead = relationship("LeadDB", back_populates="scoring_history")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'old_score': self.old_score,
            'new_score': self.new_score,
            'reason': self.reason,
            'changed_by': self.changed_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CampaignDB(Base):
    """Campaign model for organizing lead generation/nurturing campaigns"""
    __tablename__ = 'campaigns'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    campaign_type = Column(String(50))  # email, linkedin, cold_call, etc.
    status = Column(String(50), default='draft')  # draft, active, paused, completed

    # Targeting
    target_criteria = Column(JSON, default={})  # Filters for target leads

    # Performance metrics
    leads_targeted = Column(Integer, default=0)
    leads_contacted = Column(Integer, default=0)
    leads_responded = Column(Integer, default=0)
    leads_converted = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'campaign_type': self.campaign_type,
            'status': self.status,
            'target_criteria': self.target_criteria or {},
            'performance': {
                'targeted': self.leads_targeted,
                'contacted': self.leads_contacted,
                'responded': self.leads_responded,
                'converted': self.leads_converted,
                'response_rate': (self.leads_responded / self.leads_contacted * 100) if self.leads_contacted > 0 else 0,
                'conversion_rate': (self.leads_converted / self.leads_contacted * 100) if self.leads_contacted > 0 else 0
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class LeadDatabase:
    """Database manager for lead operations"""

    def __init__(self, db_url: str = "sqlite:///leads.db"):
        """
        Initialize database connection

        Args:
            db_url: SQLAlchemy database URL
        """
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    # Lead CRUD operations
    def create_lead(self, lead_data: Dict[str, Any]) -> LeadDB:
        """Create a new lead"""
        session = self.get_session()
        try:
            # Handle tags separately
            tag_names = lead_data.pop('tags', [])

            # Convert enum strings to enum objects
            if 'source' in lead_data and isinstance(lead_data['source'], str):
                lead_data['source'] = LeadSourceEnum(lead_data['source'])
            if 'status' in lead_data and isinstance(lead_data['status'], str):
                lead_data['status'] = LeadStatusEnum(lead_data['status'])

            lead = LeadDB(**lead_data)

            # Add tags
            for tag_name in tag_names:
                tag = self.get_or_create_tag(session, tag_name)
                lead.tags.append(tag)

            session.add(lead)
            session.commit()
            session.refresh(lead)
            return lead
        finally:
            session.close()

    def get_lead(self, lead_id: int) -> Optional[LeadDB]:
        """Get lead by ID"""
        session = self.get_session()
        try:
            return session.query(LeadDB).filter(LeadDB.id == lead_id).first()
        finally:
            session.close()

    def get_lead_by_email(self, email: str) -> Optional[LeadDB]:
        """Get lead by email"""
        session = self.get_session()
        try:
            return session.query(LeadDB).filter(LeadDB.email == email).first()
        finally:
            session.close()

    def update_lead(self, lead_id: int, updates: Dict[str, Any]) -> Optional[LeadDB]:
        """Update lead"""
        session = self.get_session()
        try:
            lead = session.query(LeadDB).filter(LeadDB.id == lead_id).first()
            if not lead:
                return None

            # Handle tags separately
            if 'tags' in updates:
                tag_names = updates.pop('tags')
                lead.tags.clear()
                for tag_name in tag_names:
                    tag = self.get_or_create_tag(session, tag_name)
                    lead.tags.append(tag)

            # Update other fields
            for key, value in updates.items():
                if hasattr(lead, key):
                    setattr(lead, key, value)

            lead.updated_at = datetime.now()
            session.commit()
            session.refresh(lead)
            return lead
        finally:
            session.close()

    def delete_lead(self, lead_id: int) -> bool:
        """Delete lead"""
        session = self.get_session()
        try:
            lead = session.query(LeadDB).filter(LeadDB.id == lead_id).first()
            if lead:
                session.delete(lead)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def list_leads(self, filters: Dict[str, Any] = None, limit: int = 100, offset: int = 0) -> List[LeadDB]:
        """List leads with filters"""
        session = self.get_session()
        try:
            query = session.query(LeadDB)

            if filters:
                if 'status' in filters:
                    if isinstance(filters['status'], str):
                        query = query.filter(LeadDB.status == LeadStatusEnum(filters['status']))
                    else:
                        query = query.filter(LeadDB.status == filters['status'])

                if 'min_score' in filters:
                    query = query.filter(LeadDB.score >= filters['min_score'])

                if 'max_score' in filters:
                    query = query.filter(LeadDB.score <= filters['max_score'])

                if 'company' in filters:
                    query = query.filter(LeadDB.company.ilike(f"%{filters['company']}%"))

                if 'tags' in filters:
                    for tag_name in filters['tags']:
                        query = query.join(LeadDB.tags).filter(TagDB.name == tag_name)

            return query.limit(limit).offset(offset).all()
        finally:
            session.close()

    def update_lead_score(self, lead_id: int, new_score: int, reason: str = None, changed_by: str = 'system') -> bool:
        """Update lead score and track history"""
        session = self.get_session()
        try:
            lead = session.query(LeadDB).filter(LeadDB.id == lead_id).first()
            if not lead:
                return False

            old_score = lead.score
            lead.score = new_score
            lead.updated_at = datetime.now()

            # Track score history
            history = LeadScoreHistoryDB(
                lead_id=lead_id,
                old_score=old_score,
                new_score=new_score,
                reason=reason,
                changed_by=changed_by
            )
            session.add(history)
            session.commit()
            return True
        finally:
            session.close()

    # Tag operations
    def get_or_create_tag(self, session: Session, tag_name: str) -> TagDB:
        """Get existing tag or create new one"""
        tag = session.query(TagDB).filter(TagDB.name == tag_name).first()
        if not tag:
            tag = TagDB(name=tag_name)
            session.add(tag)
            session.flush()
        return tag

    def list_tags(self) -> List[TagDB]:
        """List all tags"""
        session = self.get_session()
        try:
            return session.query(TagDB).all()
        finally:
            session.close()

    # Interaction operations
    def add_interaction(self, interaction_data: Dict[str, Any]) -> InteractionDB:
        """Add interaction to lead"""
        session = self.get_session()
        try:
            interaction = InteractionDB(**interaction_data)
            session.add(interaction)

            # Update last_contacted on lead
            if interaction_data.get('lead_id'):
                lead = session.query(LeadDB).filter(LeadDB.id == interaction_data['lead_id']).first()
                if lead:
                    lead.last_contacted = datetime.now()
                    lead.updated_at = datetime.now()

            session.commit()
            session.refresh(interaction)
            return interaction
        finally:
            session.close()

    def get_lead_interactions(self, lead_id: int, limit: int = 50) -> List[InteractionDB]:
        """Get interactions for a lead"""
        session = self.get_session()
        try:
            return session.query(InteractionDB)\
                .filter(InteractionDB.lead_id == lead_id)\
                .order_by(InteractionDB.created_at.desc())\
                .limit(limit)\
                .all()
        finally:
            session.close()

    # Campaign operations
    def create_campaign(self, campaign_data: Dict[str, Any]) -> CampaignDB:
        """Create a new campaign"""
        session = self.get_session()
        try:
            campaign = CampaignDB(**campaign_data)
            session.add(campaign)
            session.commit()
            session.refresh(campaign)
            return campaign
        finally:
            session.close()

    def list_campaigns(self, status: str = None) -> List[CampaignDB]:
        """List campaigns"""
        session = self.get_session()
        try:
            query = session.query(CampaignDB)
            if status:
                query = query.filter(CampaignDB.status == status)
            return query.order_by(CampaignDB.created_at.desc()).all()
        finally:
            session.close()

    # Analytics
    def get_lead_stats(self) -> Dict[str, Any]:
        """Get lead statistics"""
        session = self.get_session()
        try:
            total_leads = session.query(LeadDB).count()

            status_counts = {}
            for status in LeadStatusEnum:
                count = session.query(LeadDB).filter(LeadDB.status == status).count()
                status_counts[status.value] = count

            avg_score = session.query(LeadDB).with_entities(
                sqlalchemy.func.avg(LeadDB.score)
            ).scalar() or 0

            return {
                'total_leads': total_leads,
                'status_breakdown': status_counts,
                'average_score': round(float(avg_score), 2),
                'high_quality_leads': session.query(LeadDB).filter(LeadDB.score >= 70).count(),
                'qualified_leads': session.query(LeadDB).filter(LeadDB.status == LeadStatusEnum.QUALIFIED).count()
            }
        finally:
            session.close()


# Utility function for easy database access
import sqlalchemy

def get_lead_database(db_url: str = "sqlite:///leads.db") -> LeadDatabase:
    """Get or create lead database instance"""
    return LeadDatabase(db_url)


if __name__ == "__main__":
    # Example usage
    db = LeadDatabase()

    # Create sample lead
    lead = db.create_lead({
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'company': 'Example Corp',
        'title': 'VP of Engineering',
        'source': 'linkedin',
        'tags': ['tech', 'enterprise']
    })
    print(f"Created lead: {lead.to_dict()}")

    # Get stats
    stats = db.get_lead_stats()
    print(f"Lead stats: {json.dumps(stats, indent=2)}")
