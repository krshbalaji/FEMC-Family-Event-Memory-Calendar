from __future__ import annotations

import datetime
from typing import List, Optional, Dict

from .models import (
    ActionType, ResourceType, TransactionRecord, ActionProposal, AnomalySeverity,
    AnomalyType, AuditAnomaly, CelebrationArtifact, CelebrationArtifactType,
    Confidence, ContextDiscoveryResult, DashboardEntryType, DashboardProjectionEntry,
    DashboardSummary, DataExportResult, Event, EventCategory, EventStatus,
    EventWithMemories, ExportValidationResult, FamilyTopologyResult, InsightAnalysis,
    MediaAlbum, MediaItem, MediaType, Memory, Notification, NotificationStatus,
    NotificationType, Place, ProposalStatus, ProposalType, RecurrenceRule, Relationship,
    RelationshipType, ReminderConfig, ReminderStatus, ReminderType, RepairClassification,
    RepairProposal, RichEventDetail, RichPersonDetail, ShareLink, ShareResourceType,
    TimelineItemType, TimelineProjectionEntry, _utc_now, ValidationReport,
    VisibilityLevel, ContextType, AgeGroup, Language, GuideMode, SceneDefinition,
    GuideSessionState, MayilPracticeWorld,
)

from .repositories import CanonicalRepository, DerivedRepository, TransactionMemoryRepository
from .services import (
    MayilGuidedExperienceService, TransactionMemoryService, AuthorizationService,
    CalendarService, CelebrationStudioService, DashboardService, DataPortabilityService,
    EventService, IdentityService, MayilService, MediaService, MemoryService,
    NotificationService, PlaceService, ReminderService, SearchService, SharingService,
    TimelineService, VelGuardianService,
)


class FEMCApi:
    def __init__(self) -> None:
        self.canonical = CanonicalRepository()
        self.derived = DerivedRepository()
        self.authorization = AuthorizationService()
        self.identity = IdentityService(self.canonical)
        self.event = EventService(self.canonical, self.derived, self.authorization)
        self.calendar = CalendarService(self.canonical, self.derived, self.authorization)
        self.memory = MemoryService(self.canonical, self.derived, self.authorization)
        self.place = PlaceService(self.canonical, self.derived, self.authorization)
        self.media = MediaService(self.canonical, self.derived, self.authorization)
        self.timeline = TimelineService(self.canonical, self.derived, self.authorization)
        self.notification = NotificationService(self.canonical, self.authorization)
        self.reminder = ReminderService(self.canonical, self.authorization, self.notification)
        self.sharing = SharingService(self.canonical, self.authorization)
        self.dashboard = DashboardService(
            self.canonical, self.derived, self.authorization, self.calendar, self.event,
            self.memory, self.media, self.reminder, self.notification,
        )
        self.celebration_studio = CelebrationStudioService(
            self.canonical, self.derived, self.authorization, self.media
        )
        self.data_portability = DataPortabilityService(self.canonical, self.derived, self.authorization)
        self.mayil = MayilService(self.canonical, self.derived, self.authorization, self.event)
        self.guardian = VelGuardianService(
            self.canonical, self.derived, self.authorization, self.calendar, self.timeline,
            self.dashboard, celebration_studio_service=self.celebration_studio,
        )
        self.search = SearchService(self.derived)
        self.transaction_repository = TransactionMemoryRepository()
        self.transaction_memory = TransactionMemoryService(
            self.transaction_repository, self.canonical, self.authorization
        )
        self.data_portability.transaction_service = self.transaction_memory
        self.guided_experience = MayilGuidedExperienceService(
            self.canonical, self.derived, self.authorization, self.transaction_memory
        )

    def create_session(self, account_id: str, duration_minutes: int = 60):
        return self.identity.create_session(account_id, duration_minutes=duration_minutes)

    def _validate_session(self, session_id: str):
        session = self.canonical.get_session(session_id)
        if session is None:
            raise PermissionError("Invalid session")
        if session.expires_at is not None and session.expires_at < _utc_now():
            raise PermissionError("Session expired")
        return session

    def resolve_family_context_for_session(self, session_id: str):
        session = self._validate_session(session_id)
        return self.identity.resolve_family_context(session.account_id)

    def create_event_for_session(self, session_id: str, title: str, description: str,
                                 family_context_id: Optional[str], start_time: datetime.datetime,
                                 end_time: Optional[datetime.datetime],
                                 visibility: VisibilityLevel = VisibilityLevel.FAMILY,
                                 place_id: Optional[str] = None,
                                 recurrence_rule: Optional[RecurrenceRule] = None,
                                 category: EventCategory = EventCategory.GENERAL,
                                 target_person_ids: Optional[List[str]] = None,
                                 milestone_year: Optional[int] = None,
                                 milestone_anchor_date: Optional[datetime.date] = None) -> Event:
        session = self._validate_session(session_id)
        return self.event.create_event(
            owner_id=session.account_id, title=title, description=description,
            family_context_id=family_context_id, start_time=start_time, end_time=end_time,
            visibility=visibility, place_id=place_id, recurrence_rule=recurrence_rule,
            category=category, target_person_ids=target_person_ids,
            milestone_year=milestone_year, milestone_anchor_date=milestone_anchor_date,
        )

    def build_rich_event_detail_for_session(self, session_id: str, event_id: str) -> RichEventDetail:
        session = self._validate_session(session_id)
        return self.dashboard.build_rich_event_detail(session.account_id, event_id)

    def build_rich_person_detail_for_session(self, session_id: str, person_id: str) -> RichPersonDetail:
        session = self._validate_session(session_id)
        return self.dashboard.build_rich_person_detail(session.account_id, person_id)

    def get_dashboard_summary_for_session(self, session_id: str, family_context_id: str) -> DashboardSummary:
        session = self._validate_session(session_id)
        return self.dashboard.generate_dashboard_summary(session.account_id, family_context_id)

    def project_dashboard_entries_for_session(self, session_id: str, family_context_id: str) -> List[DashboardProjectionEntry]:
        session = self._validate_session(session_id)
        return self.dashboard.project_dashboard_entries(session.account_id, family_context_id)

    def get_dashboard_projection_for_session(self, session_id: str, family_context_id: str) -> List[DashboardProjectionEntry]:
        session = self._validate_session(session_id)
        return self.dashboard.get_dashboard_projection(session.account_id, family_context_id)

    def configure_reminder_for_session(self, session_id: str, event_id: str, offset_minutes: int = 15,
                                       reminder_type: ReminderType = ReminderType.EVENT_START) -> ReminderConfig:
        session = self._validate_session(session_id)
        return self.reminder.create_reminder(
            created_by_id=session.account_id, event_id=event_id,
            offset_minutes=offset_minutes, reminder_type=reminder_type,
        )

    def list_reminders_for_event_for_session(self, session_id: str, event_id: str) -> List[ReminderConfig]:
        session = self._validate_session(session_id)
        return self.reminder.list_reminders_for_event(session.account_id, event_id)

    def trigger_due_reminders_for_session(self, session_id: str, family_context_id: str,
                                          current_time: Optional[datetime.datetime] = None) -> List[Notification]:
        session = self._validate_session(session_id)
        return self.reminder.evaluate_due_reminders(
            account_id=session.account_id, family_context_id=family_context_id, current_time=current_time
        )

    def get_event_for_session(self, session_id: str, event_id: str) -> Event:
        session = self._validate_session(session_id)
        return self.event.get_event_for_account(event_id, session.account_id)

    def get_calendar_for_session(self, session_id: str, family_context_id: str,
                                 start_date: Optional[datetime.date] = None,
                                 end_date: Optional[datetime.date] = None):
        session = self._validate_session(session_id)
        return self.calendar.get_calendar_for_context(
            session.account_id, family_context_id, start_date=start_date, end_date=end_date
        )

    def update_event_status_for_session(self, session_id: str, event_id: str, status: EventStatus) -> Event:
        session = self._validate_session(session_id)
        return self.event.update_event_status(session.account_id, event_id, status)

    def create_memory_for_session(self, session_id: str, event_id: str, narrative: str,
                                  visibility: VisibilityLevel = VisibilityLevel.FAMILY) -> Memory:
        session = self._validate_session(session_id)
        event = self.canonical.get_event(event_id)
        if event is None:
            raise ValueError("Event does not exist")
        self.event.get_event_for_account(event_id, session.account_id)
        return self.memory.create_memory(
            subject_id=session.account_id, narrative=narrative, visibility=visibility,
            created_by_id=session.account_id, event_id=event_id,
        )

    def get_memory_for_session(self, session_id: str, memory_id: str) -> Memory:
        session = self._validate_session(session_id)
        return self.memory.get_memory_for_account(memory_id, session.account_id)

    def get_event_with_memories_for_session(self, session_id: str, event_id: str) -> EventWithMemories:
        session = self._validate_session(session_id)
        event = self.event.get_event_for_account(event_id, session.account_id)
        if event is None:
            raise ValueError("Event does not exist")
        memories = self.memory.list_memories_for_event_for_account(event_id, session.account_id)
        return EventWithMemories(event=event, memories=memories)

    def discover_context_for_session(self, session_id: str, family_context_id: str) -> ContextDiscoveryResult:
        session = self._validate_session(session_id)
        context = self.identity.resolve_family_context(session.account_id)
        if context is None or context.id != family_context_id:
            raise PermissionError("Account is not authorized for this family context")
        calendar_entries = self.calendar.get_calendar_for_context(session.account_id, family_context_id)
        memories = self.memory.list_memories_for_context_for_account(family_context_id, session.account_id)
        return ContextDiscoveryResult(context=context, calendar_entries=calendar_entries, memories=memories)

    def search_for_session(self, session_id: str, query: str):
        session = self._validate_session(session_id)
        results = self.search.search(query)
        visible_results = []
        for entry in results:
            try:
                if entry.type == "event":
                    self.event.get_event_for_account(entry.id, session.account_id)
                    visible_results.append(entry)
                elif entry.type == "memory":
                    self.memory.get_memory_for_account(entry.id, session.account_id)
                    visible_results.append(entry)
            except PermissionError:
                continue
        return visible_results

    def create_relationship_for_session(self, session_id: str, source_person_id: str, target_person_id: str,
                                        relationship_type: RelationshipType = RelationshipType.MEMBER,
                                        confidence: Confidence = Confidence.MEDIUM) -> Relationship:
        session = self._validate_session(session_id)
        if self.canonical.get_person(source_person_id) is None or self.canonical.get_person(target_person_id) is None:
            raise ValueError("Referenced person does not exist")
        if self.identity.resolve_family_context(session.account_id) is None:
            raise PermissionError("Account is not authorized to create relationships")
        return self.identity.create_relationship(
            source_person_id=source_person_id, target_person_id=target_person_id,
            relationship_type=relationship_type, confidence=confidence,
        )

    def get_family_topology_for_session(self, session_id: str, family_context_id: str) -> FamilyTopologyResult:
        session = self._validate_session(session_id)
        return self.identity.get_family_topology_for_account(family_context_id, session.account_id)

    def create_place_for_session(self, session_id: str, name: str, address: str = "",
                                 family_context_id: Optional[str] = None,
                                 visibility: VisibilityLevel = VisibilityLevel.FAMILY) -> Place:
        session = self._validate_session(session_id)
        return self.place.create_place(
            created_by_id=session.account_id, name=name, address=address,
            family_context_id=family_context_id, visibility=visibility,
        )

    def get_place_for_session(self, session_id: str, place_id: str) -> Place:
        session = self._validate_session(session_id)
        place = self.place.get_place_for_account(place_id, session.account_id)
        if place is None:
            raise ValueError("Place does not exist")
        return place

    def list_places_for_session(self, session_id: str, family_context_id: str) -> List[Place]:
        session = self._validate_session(session_id)
        return self.place.list_places_for_context_for_account(family_context_id, session.account_id)

    def create_media_item_for_session(self, session_id: str, uri: str,
                                      media_type: MediaType = MediaType.PHOTO,
                                      caption: str = "", family_context_id: Optional[str] = None,
                                      event_id: Optional[str] = None, memory_id: Optional[str] = None,
                                      visibility: VisibilityLevel = VisibilityLevel.FAMILY) -> MediaItem:
        session = self._validate_session(session_id)
        return self.media.create_media_item(
            owner_id=session.account_id, uri=uri, media_type=media_type, caption=caption,
            family_context_id=family_context_id, event_id=event_id, memory_id=memory_id,
            visibility=visibility,
        )

    def get_media_item_for_session(self, session_id: str, media_id: str) -> MediaItem:
        session = self._validate_session(session_id)
        item = self.media.get_media_item_for_account(media_id, session.account_id)
        if item is None:
            raise ValueError("Media item does not exist")
        return item

    def list_media_items_for_event_for_session(self, session_id: str, event_id: str) -> List[MediaItem]:
        session = self._validate_session(session_id)
        return self.media.list_media_items_for_event_for_account(event_id, session.account_id)

    def list_media_items_for_memory_for_session(self, session_id: str, memory_id: str) -> List[MediaItem]:
        session = self._validate_session(session_id)
        return self.media.list_media_items_for_memory_for_account(memory_id, session.account_id)

    def create_media_album_for_session(self, session_id: str, title: str, description: str = "",
                                       family_context_id: Optional[str] = None,
                                       media_ids: Optional[List[str]] = None,
                                       visibility: VisibilityLevel = VisibilityLevel.FAMILY) -> MediaAlbum:
        session = self._validate_session(session_id)
        return self.media.create_media_album(
            owner_id=session.account_id, title=title, description=description,
            family_context_id=family_context_id, media_ids=media_ids, visibility=visibility,
        )

    def get_media_album_for_session(self, session_id: str, album_id: str) -> MediaAlbum:
        session = self._validate_session(session_id)
        album = self.media.get_media_album_for_account(album_id, session.account_id)
        if album is None:
            raise ValueError("Media album does not exist")
        return album

    def add_media_to_album_for_session(self, session_id: str, album_id: str, media_id: str) -> MediaAlbum:
        session = self._validate_session(session_id)
        return self.media.add_media_to_album(album_id, media_id, session.account_id)

    def get_timeline_for_session(self, session_id: str, family_context_id: str,
                                 limit: Optional[int] = None) -> List[TimelineProjectionEntry]:
        session = self._validate_session(session_id)
        return self.timeline.get_timeline_for_family_context_for_account(
            family_context_id=family_context_id, account_id=session.account_id, limit=limit
        )

    def create_notification_for_session(self, session_id: str, recipient_id: str,
                                        notification_type: NotificationType, title: str, message: str,
                                        family_context_id: Optional[str] = None,
                                        target_resource_id: Optional[str] = None) -> Notification:
        session = self._validate_session(session_id)
        return self.notification.create_notification(
            sender_id=session.account_id, recipient_id=recipient_id, notification_type=notification_type,
            title=title, message=message, family_context_id=family_context_id,
            target_resource_id=target_resource_id,
        )

    def get_notification_for_session(self, session_id: str, notification_id: str) -> Notification:
        session = self._validate_session(session_id)
        notif = self.notification.get_notification_for_account(notification_id, session.account_id)
        if notif is None:
            raise ValueError("Notification does not exist")
        return notif

    def list_notifications_for_session(self, session_id: str) -> List[Notification]:
        session = self._validate_session(session_id)
        return self.notification.list_notifications_for_account(session.account_id)

    def mark_notification_read_for_session(self, session_id: str, notification_id: str) -> Notification:
        session = self._validate_session(session_id)
        return self.notification.mark_notification_read(notification_id, session.account_id)

    def create_share_link_for_session(self, session_id: str, resource_type: ShareResourceType,
                                      resource_id: str, family_context_id: Optional[str] = None,
                                      expires_in_minutes: Optional[int] = None) -> ShareLink:
        session = self._validate_session(session_id)
        return self.sharing.create_share_link(
            created_by_id=session.account_id, resource_type=resource_type, resource_id=resource_id,
            family_context_id=family_context_id, expires_in_minutes=expires_in_minutes,
        )

    def resolve_share_token(self, token: str):
        return self.sharing.resolve_share_token(token)

    def revoke_share_link_for_session(self, session_id: str, token: str) -> ShareLink:
        session = self._validate_session(session_id)
        return self.sharing.revoke_share_link(token, session.account_id)

    def get_memory_bundle_for_session(self, session_id: str, memory_id: str) -> Dict[str, object]:
        session = self._validate_session(session_id)
        memory = self.memory.get_memory_for_account(memory_id, session.account_id)
        event = self.canonical.get_event(memory.event_id) if memory.event_id else None
        if event is not None:
            self.event.get_event_for_account(event.id, session.account_id)
        context = self.canonical.get_family_context(event.family_context_id) if event and event.family_context_id else None
        if context is None:
            context = self.identity.resolve_family_context(session.account_id)
        person = self.canonical.get_person(memory.subject_id)
        media_items = self.media.list_media_items_for_memory_for_account(memory.id, session.account_id)
        return {"memory": memory, "event": event, "person": person, "family_context": context, "media_items": media_items}

    def get_share_resource_bundle(self, token: str) -> Dict[str, object]:
        resource = self.sharing.resolve_share_token(token)
        owner_id = getattr(resource, "owner_id", None)
        if isinstance(resource, Event):
            return {"resource_type": ShareResourceType.EVENT.value, "resource": resource,
                    "media_items": self.media.list_media_items_for_event_for_account(resource.id, owner_id)}
        if isinstance(resource, Memory):
            event = self.canonical.get_event(resource.event_id) if resource.event_id else None
            subject_id = resource.provenance.created_by_id if resource.provenance else resource.subject_id
            return {"resource_type": ShareResourceType.MEMORY.value, "resource": resource,
                    "event": event, "person": self.canonical.get_person(resource.subject_id),
                    "media_items": self.media.list_media_items_for_memory_for_account(resource.id, subject_id)}
        if isinstance(resource, MediaItem):
            return {"resource_type": ShareResourceType.MEDIA_ITEM.value, "resource": resource,
                    "memory": self.canonical.get_memory(resource.memory_id) if resource.memory_id else None,
                    "event": self.canonical.get_event(resource.event_id) if resource.event_id else None}
        if isinstance(resource, MediaAlbum):
            return {"resource_type": ShareResourceType.MEDIA_ALBUM.value, "resource": resource,
                    "media_items": [self.canonical.get_media_item(i) for i in resource.media_ids if self.canonical.get_media_item(i)]}
        if isinstance(resource, CelebrationArtifact):
            return {"resource_type": "celebration_artifact", "resource": resource}
        raise ValueError("Unsupported share resource")

    def get_guided_experience_state_for_session(self, session_id: str):
        session = self._validate_session(session_id)
        return self.guided_experience.get_session(session.account_id)

    def initialize_guided_experience_for_session(self, session_id: str, family_context_id: str,
                                                 mode: GuideMode = GuideMode.LEARN_BY_DOING,
                                                 context_type: ContextType = ContextType.FAMILY,
                                                 age_group: AgeGroup = AgeGroup.MIXED,
                                                 include_family: bool = True,
                                                 language: Language = Language.ENGLISH) -> GuideSessionState:
        session = self._validate_session(session_id)
        return self.guided_experience.initialize_session(
            session.account_id, family_context_id, mode, context_type, age_group, include_family, language
        )

    def get_shared_journey_scenes_for_session(self, session_id: str):
        session = self._validate_session(session_id)
        st = self.guided_experience.get_session(session.account_id)
        return self.guided_experience.get_shared_journey_scenes(
            st.context_type if st else ContextType.FAMILY, st.language if st else Language.ENGLISH
        )

    def validate_guided_action_for_session(self, session_id: str, action_type: ActionType, control_id: str,
                                           resource_id: str, resource_label: str = "", operation: str = "") -> dict:
        session = self._validate_session(session_id)
        return self.guided_experience.validate_user_action(
            session.account_id, action_type, control_id, resource_id, resource_label, operation
        )

    def switch_guided_experience_mode_for_session(self, session_id: str, new_mode: GuideMode) -> GuideSessionState:
        session = self._validate_session(session_id)
        return self.guided_experience.switch_mode(session.account_id, new_mode)

    def reset_guided_experience_for_session(self, session_id: str) -> GuideSessionState:
        session = self._validate_session(session_id)
        return self.guided_experience.reset_guided_session(session.account_id)

    def start_practice_world_for_session(self, session_id: str, family_context_id: str,
                                         context_type: ContextType = ContextType.FAMILY,
                                         age_group: AgeGroup = AgeGroup.MIXED,
                                         include_family: bool = True,
                                         language: Language = Language.ENGLISH) -> MayilPracticeWorld:
        session = self._validate_session(session_id)
        return self.guided_experience.get_or_create_practice_world(
            session.account_id, family_context_id, context_type, age_group, include_family, language
        )

    def get_practice_world_state_for_session(self, session_id: str) -> Optional[MayilPracticeWorld]:
        session = self._validate_session(session_id)
        return self.guided_experience.practice_worlds.get(session.account_id)

    def execute_simulated_action_for_session(self, session_id: str, action_type: ActionType,
                                             control_id: str, resource_type: ResourceType = ResourceType.EVENT,
                                             payload: Optional[dict] = None) -> dict:
        session = self._validate_session(session_id)
        return self.guided_experience.execute_simulated_action(
            session.account_id, action_type, control_id, resource_type, payload
        )

    def explain_practice_history_for_session(self, session_id: str) -> dict:
        session = self._validate_session(session_id)
        return self.guided_experience.explain_practice_history(session.account_id)

    def reset_practice_world_for_session(self, session_id: str) -> MayilPracticeWorld:
        session = self._validate_session(session_id)
        return self.guided_experience.reset_practice_world(session.account_id)

    def exit_practice_world_for_session(self, session_id: str) -> dict:
        session = self._validate_session(session_id)
        return self.guided_experience.exit_practice_world(session.account_id)

    def _resolve_view_context(self, session_id: str, family_context_id: Optional[str] = None):
        session = self._validate_session(session_id)
        fc_id = family_context_id
        if not fc_id:
            fc = self.identity.resolve_family_context(session.account_id)
            if fc:
                fc_id = fc.id
        st = self.guided_experience.get_session(session.account_id)
        is_lbd = st is not None and st.current_mode == GuideMode.LEARN_BY_DOING
        pw = self.guided_experience.practice_worlds.get(session.account_id) if is_lbd else None
        if is_lbd and pw is None and fc_id:
            pw = self.guided_experience.get_or_create_practice_world(session.account_id, fc_id)
        return session, fc_id, pw

    def get_members_projection(self, session_id: str, account_sessions: Dict[str, str], active_account_id: str):
        session, _, pw = self._resolve_view_context(session_id)
        if pw is not None:
            return self.guided_experience.get_practice_members_projection(account_sessions, active_account_id, pw)
        members = []
        for acc_id, sess_id in account_sessions.items():
            acc = self.canonical.get_account(acc_id)
            per = self.canonical.get_person(acc.person_id) if acc and acc.person_id else None
            if acc and per:
                members.append({"account_id": acc.id, "person_id": per.id, "name": per.name,
                                "email": acc.email, "username": acc.username, "session_id": sess_id,
                                "is_active": acc.id == active_account_id})
        return members

    def get_events_projection(self, session_id: str, family_context_id: str, default_event_id: str):
        session, fc_id, pw = self._resolve_view_context(session_id, family_context_id)
        if pw is not None:
            return self.guided_experience.get_practice_calendar_projection(pw), self.guided_experience.get_practice_event_detail_projection(pw)
        calendar = self.calendar.get_calendar_for_context(session.account_id, fc_id)
        try:
            detail = self.dashboard.build_rich_event_detail(session.account_id, default_event_id)
        except Exception:
            detail = {}
        return calendar, detail

    def get_timeline_projection(self, session_id: str, family_context_id: str, default_event_id: str):
        session, fc_id, pw = self._resolve_view_context(session_id, family_context_id)
        if pw is not None:
            return self.guided_experience.get_practice_timeline_projection(pw), {}
        try:
            event_memories = self.get_event_with_memories_for_session(session_id, default_event_id)
        except Exception:
            event_memories = None
        return self.timeline.get_timeline_for_family_context_for_account(fc_id, session.account_id), event_memories

    def get_media_projection(self, session_id: str, family_context_id: str, user_account_id: str):
        session, fc_id, pw = self._resolve_view_context(session_id, family_context_id)
        if pw is not None:
            return self.guided_experience.get_practice_media_projection(pw), []
        context = self.canonical.get_family_context(fc_id)
        items = [m for m in self.canonical.list_media_items() if m.family_context_id == fc_id and self.authorization.can_view_media_item(user_account_id, m, context)]
        albums = [a for a in self.canonical.list_media_albums() if a.family_context_id == fc_id and self.authorization.can_view_media_album(user_account_id, a, context)]
        return items, albums

    def get_celebrations_projection(self, session_id: str, family_context_id: str):
        session, fc_id, pw = self._resolve_view_context(session_id, family_context_id)
        if pw is not None:
            return self.guided_experience.get_practice_celebrations_projection(pw)
        return self.celebration_studio.list_celebration_artifacts(session.account_id, fc_id)

    def get_sharing_projection(self, session_id: str, family_context_id: str):
        session, fc_id, pw = self._resolve_view_context(session_id, family_context_id)
        if pw is not None:
            return self.guided_experience.get_practice_sharing_projection(pw)
        return [l for l in self.canonical.list_share_links() if l.family_context_id == fc_id]

    def get_export_projection(self, session_id: str, family_context_id: str):
        session, fc_id, pw = self._resolve_view_context(session_id, family_context_id)
        if pw is not None:
            return self.guided_experience.get_practice_export_projection(pw), {"is_valid": True, "errors": [], "warnings": [], "record_counts": {}}
        export_data = self.data_portability.export_family_context_for_account(session.account_id, fc_id)
        serialization = self.data_portability.serialize_family_context(export_data)
        return serialization, self.data_portability.validate_data_export(serialization)

    def get_history_projection(self, session_id: str, family_context_id: str):
        session, fc_id, pw = self._resolve_view_context(session_id, family_context_id)
        if pw is not None:
            return self.guided_experience.get_practice_history_projection(pw)
        history = self.transaction_memory.get_transaction_history_for_session(session_id, fc_id, limit=50)
        res = [r.__dict__ for r in history]
        for r in res:
            if isinstance(r.get("timestamp"), datetime.datetime):
                r["timestamp"] = r["timestamp"].isoformat()
            r["action_type"] = str(r["action_type"])
            r["resource_type"] = str(r["resource_type"])
            r["visibility"] = str(r["visibility"])
        return res
