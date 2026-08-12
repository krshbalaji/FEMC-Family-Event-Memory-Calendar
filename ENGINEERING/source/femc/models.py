from __future__ import annotations

import dataclasses
import datetime
import enum
import uuid
from dataclasses import dataclass, field
from typing import List, Optional


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




