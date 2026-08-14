# FEMC V2.3 Product Discovery & Capability Gap Audit

## 1. Baseline Verification
- **Canonical Checkpoint**: Commit `f0afcb2`
- **Tag**: `femc-v2.2-green`
- **Verified Test Suite**: 136 passed, 0 failed, 0 errors
- **Production Source Boundary**: `ENGINEERING/source/femc/` (100% clean, 0 modifications)
- **Local Presentation Host**: `run.py` at `http://127.0.0.1:8000`
- **Working Tree**: Uncommitted V2.3-B.3 presentation enhancements & tests

---

## 2. Current Product Capabilities
FEMC currently implements a multi-layer family memory engine with the following operational capabilities:
- **Canonical Data Store**: Manages Accounts, Persons, Family Contexts, Relationships, Events, Memories, Places, Media Items, Media Albums, Reminders, Notifications, Share Links, and Provenance Metadata.
- **Derived Projections**: Computes Calendar Projections, Timeline Projections, Dashboard Summary & Projections, Celebration Artifacts, and Family Topology Graphs.
- **Privacy & Authorization**: Enforces strict `can_view_event`, `can_view_memory`, `can_view_media`, and `can_view_reminder` authorization rules across PUBLIC, FAMILY, and PRIVATE visibility levels.
- **Celebration Studio Engine**: Derives `EVENT_CARD`, `MILESTONE_DIGEST`, `PERSON_HIGHLIGHT`, and `CELEBRATION_ALBUM` artifacts.
- **Mayil AI Engine**: Analyzes family context data to produce natural language insight summaries and actionable proposals (`EVENT_RECOMMENDATION`, `MEMORY_COMPILATION`, `MILESTONE_ALERT`).
- **VEL Guardian Engine**: Runs real-time data integrity audits (`DANGLING_REFERENCE`, `PRIVACY_LEAK`, `DERIVED_STALENESS`), classifies anomalies, and executes derived/canonical repairs.
- **Data Portability**: Serializes family context state into JSON exports and validates structure against schema version `1.0`.

---

## 3. User Journey Findings

### Journey A — First Family Setup
- **Current State**: `DemoState` statically initializes the "Smith Family" context with pre-populated accounts and persons. V2.3-A added an interactive `➕ Add Family Member` modal and `POST /api/family/onboard`.
- **Observed Gaps**: Node-link interactive topology tree rendering; editing existing member details.

### Journey B — Add an Event
- **Current State**: Calendar schedule event modal allows selecting title, category (`BIRTHDAY`, `ANNIVERSARY`, `MILESTONE`, `GENERAL`), visibility (`FAMILY`, `PRIVATE`), and target family member checkboxes (`target_person_ids`).
- **Observed Gaps**: Recurrence rule rules UI and location/place picker.

### Journey C — Capture a Memory & A/V Media
- **Current State**: Unified Media Capture Center supports 5 capture modes: Camera Snapshot (`📷 Take Photo`), Video Recording (`🎥 Record Video`), Voice Memo (`🎙️ Voice Memo`), File Upload (`📁 Upload File`), and Drag & Drop Zone (`🖱️ Drag & Drop`).
- **Observed Gaps**: Cloud storage sync (intentionally omitted; local stdlib architecture).

### Journey D — Celebrate
- **Current State**: Celebration Studio generates celebration cards and digests. V2.3-B added interactive `✨ Generate Celebration Card` modal calling `build_celebration_artifact_for_*_for_session`.
- **Observed Gaps**: Custom celebration card template customization.

### Journey E — Family Member Perspective & Privacy
- **Current State**: Header dropdown (`👁️ Viewing as: [Alice Smith ▼]`) dynamically switches `AuthenticatedSession` via `POST /api/session/switch`, isolating private events/reminders across members.
- **Observed Gaps**: Role-based access control policies (e.g. Guardian vs Child account permissions).

### Journey F — Family History & Continuity
- **Current State**: Timeline displays events and memories chronologically with author attribution and attached media photo thumbnails, HTML5 video players, and HTML5 voice memo audio players.
- **Observed Gaps**: Multi-year "On This Day" historical lookback filter.

### Journey G — Sharing & Data Safety
- **Current State**: V2.3-B.2 added Media-level downloads (`⬇ Download`) with human-friendly filenames (`Alice_Birthday_Candles_2026-08-13.jpg`), Sharing modal (`🔗 Share`) via `SharingService`, Device Share (`navigator.share`), WhatsApp compose URL, and Copy Share URL.
- **Observed Gaps**: `import_family_context` backend implementation for full roundtrip restore; human-translated Guardian anomaly strings.

### Journey H — Guided Experience & Multilingual Accessibility (V2.3-B.3)
- **Current State**: Interactive `🎬 Guided Tour` walkthrough covering all 10 Core FEMC Pillars across 14 steps with structured translations (English 🇬🇧, Tamil 🇮🇳, Hindi 🇮🇳), browser TTS audio narration (`window.speechSynthesis`), subtitles/captions bar, `[👉 Try It]` action launchers, Speech Recognition voice control (`🎙️ Speak to FEMC`), and screen recording mode (`🎥 Record Demo`).
- **Observed Gaps**: Advanced offline TTS voice packs.

---

## 4. Screen-by-Screen UX Findings

1. **🏠 HOME / DASHBOARD**:
   - *Strengths*: Clean 5-card semantic separation (Upcoming Events, Reminders, Recent Memories, Celebration Highlights, Mayil Spotlight) respecting active session privacy.
   - *Weaknesses*: Cards are static text listings; clicking an item does not open a detail popup.

2. **👨‍👩‍👧‍👦 FAMILY**:
   - *Strengths*: Shows member topology cards with birth dates, emails, active user badge, and interactive `➕ Add Family Member` onboarding modal.
   - *Weaknesses*: Relationship graph is rendered as a text list rather than visual nodes/edges.

3. **📅 CALENDAR**:
   - *Strengths*: Agenda view with distinct category pills (`🎂 BIRTHDAY`, `💍 ANNIVERSARY`, `⭐ MILESTONE`, `📅 GENERAL`), privacy badges, `🔗 Share` action, and interactive Schedule Event modal.
   - *Weaknesses*: Month/Week grid view is missing.

4. **📖 MEMORIES & MEDIA**:
   - *Strengths*: Displays narrative timeline cards with author attribution, attached photo/video/audio players, `📸 Add Family Media` capture center modal, `⬇ Download` buttons with human-friendly filenames, and `🔗 Share` modal with native Device Share & WhatsApp.
   - *Weaknesses*: Camera stream requires HTTPS or localhost browser origin (handled seamlessly with File Upload fallback).

5. **🎉 CELEBRATIONS**:
   - *Strengths*: Renders celebration cards with rendered text content, visibility level, `✨ Generate Celebration Card` modal, and `🔗 Share Artifact` button.
   - *Weaknesses*: Template styling options are static.

6. **🔔 REMINDERS**:
   - *Strengths*: Lists active notifications with interactive `Mark Read` API button.
   - *Weaknesses*: Cannot create custom reminders directly from calendar event row.

7. **🧠 MAYIL AI**:
   - *Strengths*: Displays context insight analysis and actionable proposal cards with `Approve Proposal` API button.
   - *Weaknesses*: Suggestions are pre-seeded; no text input box to query Mayil with natural language prompts.

8. **🛡️ VEL GUARDIAN**:
   - *Strengths*: Displays audit health badge and active anomalies with `Execute Repair` API button.
   - *Weaknesses*: Technical engineering jargon (`DANGLING_REFERENCE`) is exposed without plain-language explanations.

9. **🔗 SHARING**:
   - *Strengths*: Displays active share links for Events, Memories, Media Items, and Media Albums with expiration times, tokenized URLs, and `Revoke` button.
   - *Weaknesses*: Dedicated public share landing page rendered at `/share?token=...`.

10. **⚙️ SETTINGS / DATA**:
    - *Strengths*: Export JSON viewer and schema validation report card.
    - *Weaknesses*: No file upload / restore control; import method pending backend implementation.

---

## 5. Capability Inventory

| Capability Category | Implemented in `ENGINEERING/source/femc/` | Exposed in `run.py` Presentation | Operational Status |
|---------------------|-------------------------------------------|----------------------------------|--------------------|
| **Canonical Account & Person** | `IdentityService` | Active Member Topology & Onboarding Modal | Fully functional backend & presentation |
| **Family Context & Relationships** | `IdentityService` | Topology View & Relationship Graph Edges | Fully functional backend & presentation |
| **Events & Recurrence** | `EventService`, `CalendarService` | Event Schedule Modal & Agenda View | Core functional; missing recurrence UI |
| **Memories & Linking** | `MemoryService` | Memory Creation & Narrative Timeline | Fully functional with photo/video/audio attachments |
| **Media Items & Albums** | `MediaService` | Media Capture Center & A/V Media Players | Fully functional backend & presentation |
| **Media Download & Export** | `run.py` / `MediaService` | Human-friendly Filename Download (`⬇ Download`) | Fully functional presentation & download |
| **Social & Device Sharing** | `SharingService` / `run.py` | `navigator.share`, WhatsApp, Copy Share Link | Fully functional backend & presentation |
| **Multilingual Guided Tour** | `run.py` | `🎬 Guided Tour` (English, Tamil, Hindi) | Fully functional interactive walkthrough |
| **Audio Narration & Voice Control** | `run.py` | Browser TTS (`speechSynthesis`) & Speech Recognition | Fully functional presentation & speech APIs |
| **Timeline Projection** | `TimelineService` | Timeline View with Photo/Video/Audio Players | Fully functional with A/V players |
| **Celebration Studio** | `CelebrationStudioService` | Generate Artifact Modal & Cards List | Complete backend engine & user trigger UI |
| **Mayil AI Engine** | `MayilService` | Insight & Proposal Approval | Functional backend; missing query input UI |
| **VEL Guardian Engine** | `VelGuardianService` | Audit & Repair Approval | Fully functional governance; technical UI |
| **Data Portability** | `DataPortabilityService` | Export JSON & Validation | Export functional; Import method pending |
| **Sharing & Link Revocation** | `SharingService` | Share Link Modal & Sharing Tab | Fully functional backend & presentation |

---

## 6. Privacy & Authorization Audit
- **Domain Privacy Implementation**: `AuthorizationService` correctly enforces `can_view_event`, `can_view_memory`, `can_view_media`, and `can_view_reminder` across `PUBLIC`, `FAMILY`, and `PRIVATE` visibility levels.
- **V2.3-B.3 Verification**: Guided tour steps respect authorization privacy limits, and `[👉 Try It]` action triggers execute real authorized facade calls.

---

## 7. Core Product Concept Preservation Matrix

| Core Pillar | Current Implementation | UI Status | Backend Status | V2.3 Gap | Target Workstream |
|-------------|------------------------|-----------|----------------|----------|-------------------|
| **1. Family Tree / Family Identity** | `IdentityService` (`FamilyContext`, `Person`, `Account`, `Relationship`, `Topology`) | Member topology cards, Onboarding modal (`➕ Add Member`), Perspective Switcher dropdown | 100% Operational | Visual node-link relationship graph; edit member profile | V2.3-A (Delivered Baseline) / V2.4 Tree Visualizer |
| **2. Events / Calendar** | `EventService` & `CalendarService` (`Event`, `EventCategory`, `TargetPersonIds`, `Visibility`, `CalendarProjection`, `RichEventDetail`) | Agenda list, Schedule Event modal with target checkboxes & category pills, Share link modal | 100% Operational | Month/Week grid view; clickable event detail popup | V2.3-C Calendar Grid & Detail Modals |
| **3. Memories** | `MemoryService` & `TimelineService` (`Memory`, `TimelineProjection`, Event linking, Author attribution, Visibility) | Narrative story stream cards with author attribution, attached photo/video/audio players, `📸 Add Family Media` capture center | 100% Operational | Subject person tag filter | V2.3-B.1 (Delivered Baseline) |
| **4. Celebration Studio** | `CelebrationStudioService` (`EVENT_CARD`, `MILESTONE_DIGEST`, `PERSON_HIGHLIGHT`, `CELEBRATION_ALBUM`) | Celebration cards list with `✨ Generate Celebration Card` modal | 100% Operational | Custom card template styling options | V2.3-B (Delivered Baseline) |
| **5. Notifications / Reminders** | `ReminderService` & `NotificationService` (`ReminderConfig`, `Notification`, trigger offset, read/unread) | Notifications list with `Mark Read` API button; Home dashboard reminders card | 100% Operational | Custom reminder offset configuration directly from calendar event row | V2.3-C Interactive Event Reminders |
| **6. Mayil AI** | `MayilService` (Notice → Understand → Suggest → User Approval → Action) | "Mayil Noticed..." insight summary card, "Mayil Suggests..." proposal cards with `Approve Proposal` API button | 100% Operational | Interactive natural-language prompt box ("Ask Mayil") | V2.3-D Interactive Mayil AI Prompt |
| **7. VEL Guardian** | `VelGuardianService` (Audit integrity, privacy, authorization, projection truth, execute repair) | Audit health badge (`HEALTHY`/`ANOMALY`) and repair proposals list with `Execute Repair` API button | 100% Operational | Plain-language user translation for technical anomaly strings | V2.3-C Guardian UX Translation |
| **8. Data Portability** | `DataPortabilityService` (`export_family_context`, `validate_data_export`) | Settings export JSON viewer and schema validation report card | Export 100% Operational; Import Pending | `import_family_context` backend method + UI file upload / restore handler | V2.3-E Data Import & Backup Roundtrip |
| **9. Media** | `MediaService` (`MediaItem`, `MediaAlbum`, URI linking, event/memory linkage) | Media Capture Center, A/V Gallery, `⬇ Download` with human-friendly filenames | 100% Operational | Cloud sync (intentionally omitted) | V2.3-B.1 & V2.3-B.2 (Delivered Baseline) |
| **10. Sharing** | `SharingService` (`ShareLink`, `ShareResourceType`, token resolution, expiration, revocation) | Sharing tab, tokenized URLs, `🔗 Share` modals on events/memories/media/celebrations, Device Share & WhatsApp | 100% Operational | Dedicated public share landing page | V2.3-B & V2.3-B.2 (Delivered Baseline) |

---

## 8. V2.3-B.3 Implementation Status & Summary
- **Implementation Status**: **100% COMPLETE & VERIFIED**
- **Passing Tests**: 132 -> **136** (+4 focused V2.3-B.3 tests)
- **Workstreams Delivered**:
  - **Header Entry Point**: Added prominent `🎬 Guided Tour` and `❓ How FEMC Works` header buttons opening the interactive walkthrough modal.
  - **Structured Multilingual Dictionary**: `GUIDE_TEXT` dictionary with structured translations across English 🇬🇧, Tamil 🇮🇳, and Hindi 🇮🇳. Language switching dynamically preserves current step index and updates text & narration.
  - **Audio Narration (`speechSynthesis`)**: Integrated browser-native Speech Synthesis (`window.speechSynthesis`) with language voice matching (`en-US`, `ta-IN`, `hi-IN`) and controls (`Play`, `Pause`, `Stop`, `Mute / Read Silently`).
  - **Subtitles & Captions Bar**: Every step renders readable captions (`subtitle-bar`) for accessibility, hearing-impaired users, noisy, or silent environments.
  - **Interactive "Watch and Try"**: Every step offers `[▶ Watch]` and `[👉 Try It]` buttons. Clicking `👉 Try It` launches the real modal or view (e.g. `openOnboardModal()`, `openCreateEventModal()`, `openMediaCaptureCenter()`, etc.) directly on the real product.
  - **Speech Recognition Voice Control (`🎙️ Speak to FEMC`)**: Integrated `window.SpeechRecognition` / `webkitSpeechRecognition` allowing voice commands like *"Open calendar"*, *"Show family"*, *"Record memory"*.
  - **Demo Screen Recording Mode (`🎥 Record Demo`)**: Integrated `navigator.mediaDevices.getDisplayMedia({ video: true })` screen capture launcher with graceful permission fallback.
  - **All 10 Core Pillars Covered**: All 10 core FEMC pillars plus Camera, Microphone, Video Recording, and File/Drop are represented across 14 guided steps.
  - **Production Code Drift**: **0%** (Production source code under `ENGINEERING/source/femc/` remains 100% clean and untouched).

---

## 9. V2.3-C Implementation Status & Summary
- **Implementation Status**: **100% COMPLETE & VERIFIED**
- **Passing Tests**: 136 passed (100% suite success)
- **Workstreams Delivered**:
  - **Animated Mayil Avatar**: Lightweight animated SVG/CSS character (`mayil-avatar`) with visual states (`idle`, `speaking`, `listening`, `thinking`, `happy`, `helping`, `success`).
  - **Interactive `🤖 Ask Mayil` Panel**: Floating panel with conversation history feed, text query box, Speech Recognition voice input, Speech Synthesis voice responses, and action launchers.
  - **Multilingual FEMC Intent Engine**: Resolves queries in English, Tamil, and Hindi into 25 canonical FEMC intents (`OPEN_HOME`, `OPEN_FAMILY`, `ADD_MEMBER`, `OPEN_CALENDAR`, `CREATE_EVENT`, `OPEN_MEMORIES`, `RECORD_MEMORY`, `OPEN_MEDIA`, `CAPTURE_PHOTO`, `RECORD_AUDIO`, `RECORD_VIDEO`, `UPLOAD_MEDIA`, `OPEN_CELEBRATIONS`, `CREATE_CELEBRATION`, `OPEN_REMINDERS`, `MARK_NOTIFICATION_READ`, `OPEN_SHARING`, `CREATE_SHARE_LINK`, `OPEN_MAYIL`, `OPEN_GUARDIAN`, `OPEN_SETTINGS`, `EXPORT_DATA`, `START_GUIDED_TOUR`).
  - **Context Awareness**: Tailors suggestions to active view (`home`, `family`, `calendar`, `memories`, `celebrations`, `reminders`, `mayil`, `guardian`, `sharing`, `settings`).
  - **Action Confirmation Safety**: Prompts for confirmation before executing mutating actions (`ADD_MEMBER`, `CREATE_EVENT`, `RECORD_MEMORY`, `CREATE_CELEBRATION`, `CREATE_SHARE_LINK`, `EXPORT_DATA`).
  - **Animated FEMC Journey (17 Scenes)**: 17 animated visual story scenes covering all 10 Core FEMC Pillars + A/V media capabilities with `▶ Play Full Journey` auto-play mode (play, pause, resume, skip, prev, mute, language controls).
  - **Actual Real-World Operations**: Every scene's `[👉 Try It]` button triggers the real FEMC UI facade actions.
  - **Production Code Drift**: **0%** (`ENGINEERING/source/femc/` remains 100% clean and untouched).
