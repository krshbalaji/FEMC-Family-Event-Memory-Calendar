from __future__ import annotations

import dataclasses
import datetime
import enum
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _new_id() -> str:
    return str(uuid.uuid4())


class VisibilityLevel(str, enum.Enum):
    PUBLIC = "public"
    FAMILY = "family"
    PRIVATE = "private"


class EventStatus(str, enum.Enum):
    PLANNED = "planned"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class EventCategory(str, enum.Enum):
    BIRTHDAY = "birthday"
    ANNIVERSARY = "anniversary"
    MILESTONE = "milestone"
    HOLIDAY = "holiday"
    GENERAL = "general"


class DashboardEntryType(str, enum.Enum):
    UPCOMING_EVENT = "upcoming_event"
    RECURRING_EVENT = "recurring_event"
    DUE_REMINDER = "due_reminder"
    RECENT_MEMORY = "recent_memory"
    ACTIVE_NOTIFICATION = "active_notification"
    CELEBRATION_HIGHLIGHT = "celebration_highlight"


class CelebrationArtifactType(str, enum.Enum):
    BIRTHDAY_CARD = "birthday_card"
    ANNIVERSARY_CARD = "anniversary_card"
    MILESTONE_CARD = "milestone_card"
    FAMILY_MEMORY_CARD = "family_memory_card"
    EVENT_HIGHLIGHT = "event_highlight"
    CELEBRATION_ALBUM = "celebration_album"




class MediaType(str, enum.Enum):
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


class TimelineItemType(str, enum.Enum):
    EVENT = "event"
    MEMORY = "memory"
    MEDIA = "media"
    PLACE = "place"


class NotificationType(str, enum.Enum):
    EVENT_INVITE = "event_invite"
    MEMORY_ADDED = "memory_added"
    RELATIONSHIP_UPDATE = "relationship_update"
    SYSTEM_ALERT = "system_alert"


class NotificationStatus(str, enum.Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"


class ShareResourceType(str, enum.Enum):
    EVENT = "event"
    MEMORY = "memory"
    MEDIA_ITEM = "media_item"
    MEDIA_ALBUM = "media_album"


class RecurrenceFrequency(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class ReminderType(str, enum.Enum):
    EVENT_START = "event_start"
    EVENT_PREPARATION = "event_preparation"
    CUSTOM = "custom"


class ReminderStatus(str, enum.Enum):
    PENDING = "pending"
    TRIGGERED = "triggered"
    CANCELLED = "cancelled"


@dataclass
class RecurrenceRule:
    frequency: RecurrenceFrequency = RecurrenceFrequency.DAILY
    interval: int = 1
    until_date: Optional[datetime.date] = None



class ProposalStatus(str, enum.Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"


class ProposalType(str, enum.Enum):
    EVENT_RECOMMENDATION = "event_recommendation"
    MEMORY_ENHANCEMENT = "memory_enhancement"
    RELATIONSHIP_SUGGESTION = "relationship_suggestion"
    CALENDAR_OPTIMIZATION = "calendar_optimization"


class AnomalySeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AnomalyType(str, enum.Enum):
    DANGLING_REFERENCE = "dangling_reference"
    PROJECTION_DESYNC = "projection_desync"
    PROVENANCE_MISSING = "provenance_missing"
    PRIVACY_INVARIANT_VIOLATION = "privacy_invariant_violation"
    TOPOLOGY_INCONSISTENCY = "topology_inconsistency"







class RelationshipType(str, enum.Enum):
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    PARTNER = "partner"
    MEMBER = "member"


class Confidence(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ProvenanceSourceType(str, enum.Enum):
    USER = "user"
    SYSTEM = "system"
    IMPORT = "import"


@dataclass(frozen=True)
class ProvenanceMetadata:
    source_type: ProvenanceSourceType
    source_id: str
    created_by_id: str
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    audit_trail: List[str] = field(default_factory=list)


@dataclass
class Person:
    id: str = field(default_factory=_new_id)
    name: str = ""
    birth_date: Optional[datetime.date] = None
    relationships: List[str] = field(default_factory=list)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class Account:
    id: str = field(default_factory=_new_id)
    username: str = ""
    email: str = ""
    person_id: str = ""
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class AuthenticatedSession:
    session_id: str = field(default_factory=_new_id)
    account_id: str = ""
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    expires_at: Optional[datetime.datetime] = None


@dataclass
class Relationship:
    id: str = field(default_factory=_new_id)
    source_person_id: str = ""
    target_person_id: str = ""
    relationship_type: RelationshipType = RelationshipType.MEMBER
    confidence: Confidence = Confidence.MEDIUM
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class FamilyContext:
    id: str = field(default_factory=_new_id)
    name: str = ""
    member_ids: List[str] = field(default_factory=list)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    provenance: Optional[ProvenanceMetadata] = None


@dataclass
class Consent:
    granted_by_id: str = ""
    granted_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    scope: str = ""
    is_active: bool = True


@dataclass
class Place:
    id: str = field(default_factory=_new_id)
    name: str = ""
    address: str = ""
    family_context_id: Optional[str] = None
    visibility: VisibilityLevel = VisibilityLevel.FAMILY
    provenance: Optional[ProvenanceMetadata] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class Event:
    id: str = field(default_factory=_new_id)
    title: str = ""
    description: str = ""
    owner_id: str = ""
    family_context_id: Optional[str] = None
    place_id: Optional[str] = None
    start_time: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    end_time: Optional[datetime.datetime] = None
    status: EventStatus = EventStatus.PLANNED
    visibility: VisibilityLevel = VisibilityLevel.FAMILY
    consent: Optional[Consent] = None
    recurrence_rule: Optional[RecurrenceRule] = None
    category: EventCategory = EventCategory.GENERAL
    target_person_ids: List[str] = field(default_factory=list)
    milestone_year: Optional[int] = None
    milestone_anchor_date: Optional[datetime.date] = None
    provenance: Optional[ProvenanceMetadata] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class ReminderConfig:
    id: str = field(default_factory=_new_id)
    event_id: str = ""
    family_context_id: Optional[str] = None
    offset_minutes: int = 15
    reminder_type: ReminderType = ReminderType.EVENT_START
    status: ReminderStatus = ReminderStatus.PENDING
    last_triggered_at: Optional[datetime.datetime] = None
    created_by_id: str = ""
    provenance: Optional[ProvenanceMetadata] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class RichEventDetail:
    event: Event
    place: Optional[Place] = None
    memories: List[Memory] = field(default_factory=list)
    media_items: List[MediaItem] = field(default_factory=list)
    reminders: List[ReminderConfig] = field(default_factory=list)
    target_persons: List[Person] = field(default_factory=list)
    milestone_year: Optional[int] = None
    upcoming_occurrences: List[datetime.date] = field(default_factory=list)


@dataclass
class RichPersonDetail:
    person: Person
    account: Optional[Account] = None
    relationships: List[Relationship] = field(default_factory=list)
    events: List[Event] = field(default_factory=list)
    memories: List[Memory] = field(default_factory=list)
    media_items: List[MediaItem] = field(default_factory=list)
    milestones: List[Event] = field(default_factory=list)


@dataclass
class DashboardProjectionEntry:
    id: str = field(default_factory=_new_id)
    family_context_id: str = ""
    item_type: DashboardEntryType = DashboardEntryType.UPCOMING_EVENT
    title: str = ""
    subtitle: str = ""
    date_or_time: Optional[datetime.datetime] = None
    ref_id: str = ""
    visibility: VisibilityLevel = VisibilityLevel.FAMILY


@dataclass
class DashboardSummary:
    family_context: FamilyContext
    member_count: int = 0
    upcoming_events: List[RichEventDetail] = field(default_factory=list)
    due_reminders: List[ReminderConfig] = field(default_factory=list)
    recent_memories: List[Memory] = field(default_factory=list)
    active_notifications: List[Notification] = field(default_factory=list)
    celebration_highlights: List[RichEventDetail] = field(default_factory=list)


@dataclass
class CelebrationArtifact:
    id: str = field(default_factory=_new_id)
    artifact_type: CelebrationArtifactType = CelebrationArtifactType.EVENT_HIGHLIGHT
    title: str = ""
    subtitle: str = ""
    rendered_content: str = ""
    content_hash: str = ""
    family_context_id: str = ""
    source_event_id: Optional[str] = None
    source_person_id: Optional[str] = None
    source_memory_id: Optional[str] = None
    media_item_id: Optional[str] = None
    visibility: VisibilityLevel = VisibilityLevel.FAMILY
    provenance: Optional[ProvenanceMetadata] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)





@dataclass
class Memory:
    id: str = field(default_factory=_new_id)
    event_id: Optional[str] = None
    subject_id: str = ""
    narrative: str = ""
    recorded_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    visibility: VisibilityLevel = VisibilityLevel.FAMILY
    provenance: Optional[ProvenanceMetadata] = None


@dataclass
class MediaItem:
    id: str = field(default_factory=_new_id)
    uri: str = ""
    media_type: MediaType = MediaType.PHOTO
    caption: str = ""
    owner_id: str = ""
    family_context_id: Optional[str] = None
    event_id: Optional[str] = None
    memory_id: Optional[str] = None
    visibility: VisibilityLevel = VisibilityLevel.FAMILY
    provenance: Optional[ProvenanceMetadata] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class MediaAlbum:
    id: str = field(default_factory=_new_id)
    title: str = ""
    description: str = ""
    owner_id: str = ""
    family_context_id: Optional[str] = None
    media_ids: List[str] = field(default_factory=list)
    visibility: VisibilityLevel = VisibilityLevel.FAMILY
    provenance: Optional[ProvenanceMetadata] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)



@dataclass
class SearchResultEntry:
    id: str
    type: str
    title: str
    excerpt: str
    visibility: VisibilityLevel


@dataclass
class CalendarProjectionEntry:
    event_id: str
    title: str
    date: datetime.date
    status: EventStatus
    visibility: VisibilityLevel
    family_context_id: Optional[str] = None


@dataclass
class TimelineProjectionEntry:
    id: str
    item_type: TimelineItemType
    timestamp: datetime.datetime
    title: str
    summary: str
    owner_id: str
    family_context_id: Optional[str]
    visibility: VisibilityLevel
    ref_id: str



@dataclass
class EventWithMemories:
    event: Event
    memories: List[Memory] = field(default_factory=list)


@dataclass
class ContextDiscoveryResult:
    context: FamilyContext
    calendar_entries: List[CalendarProjectionEntry] = field(default_factory=list)
    memories: List[Memory] = field(default_factory=list)


@dataclass
class FamilyTopologyMember:
    account: Account
    person: Optional[Person] = None


@dataclass
class FamilyTopologyResult:
    context: FamilyContext
    members: List[FamilyTopologyMember] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)


@dataclass
class Notification:
    id: str = field(default_factory=_new_id)
    recipient_id: str = ""
    sender_id: str = ""
    notification_type: NotificationType = NotificationType.SYSTEM_ALERT
    title: str = ""
    message: str = ""
    family_context_id: Optional[str] = None
    target_resource_id: Optional[str] = None
    status: NotificationStatus = NotificationStatus.UNREAD
    visibility: VisibilityLevel = VisibilityLevel.PRIVATE
    provenance: Optional[ProvenanceMetadata] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class ShareLink:
    id: str = field(default_factory=_new_id)
    token: str = field(default_factory=_new_id)
    resource_type: ShareResourceType = ShareResourceType.EVENT
    resource_id: str = ""
    created_by_id: str = ""
    family_context_id: Optional[str] = None
    is_revoked: bool = False
    expires_at: Optional[datetime.datetime] = None
    provenance: Optional[ProvenanceMetadata] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class DataExportResult:
    export_id: str = field(default_factory=_new_id)
    family_context_id: str = ""
    exported_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    schema_version: str = "1.0"
    provenance: Optional[ProvenanceMetadata] = None
    records: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)


@dataclass
class ExportValidationResult:
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    record_counts: Dict[str, int] = field(default_factory=dict)


@dataclass
class ActionProposal:
    id: str = field(default_factory=_new_id)
    proposal_type: ProposalType = ProposalType.EVENT_RECOMMENDATION
    title: str = ""
    reasoning: str = ""
    proposed_changes: Dict[str, Any] = field(default_factory=dict)
    confidence: Confidence = Confidence.MEDIUM
    family_context_id: str = ""
    target_account_id: str = ""
    status: ProposalStatus = ProposalStatus.PROPOSED
    provenance: Optional[ProvenanceMetadata] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class InsightAnalysis:
    id: str = field(default_factory=_new_id)
    title: str = ""
    analysis_summary: str = ""
    family_context_id: str = ""
    confidence: Confidence = Confidence.MEDIUM
    provenance: Optional[ProvenanceMetadata] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


class RepairClassification(str, enum.Enum):
    DERIVED_ONLY = "DERIVED_ONLY"
    CANONICAL_REPAIR = "CANONICAL_REPAIR"


@dataclass
class RepairProposal:
    id: str = field(default_factory=_new_id)
    anomaly_id: str = ""
    proposed_repair_action: str = ""
    target_entity_type: str = ""
    target_entity_id: str = ""
    family_context_id: str = ""
    classification: RepairClassification = RepairClassification.DERIVED_ONLY
    requires_human_approval: bool = False
    is_executed: bool = False
    provenance: Optional[ProvenanceMetadata] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)



@dataclass
class AuditAnomaly:
    id: str = field(default_factory=_new_id)
    anomaly_type: AnomalyType = AnomalyType.DANGLING_REFERENCE
    severity: AnomalySeverity = AnomalySeverity.WARNING
    description: str = ""
    affected_entity_id: str = ""
    family_context_id: str = ""
    repair_proposal: Optional[RepairProposal] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class ValidationReport:
    is_valid: bool = True
    checked_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    total_entities_inspected: int = 0
    anomalies: List[AuditAnomaly] = field(default_factory=list)






