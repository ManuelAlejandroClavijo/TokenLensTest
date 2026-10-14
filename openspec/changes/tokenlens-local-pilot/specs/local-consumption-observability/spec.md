## ADDED Requirements

### Requirement: Local operation
The system SHALL serve its React application and API on loopback through a single Uvicorn service and SHALL persist pilot data in local SQLite.

#### Scenario: Start compiled application
- **WHEN** the user runs `python pilot.py run` after dependencies are installed
- **THEN** the application SHALL be reachable at `http://127.0.0.1:4318` without running a frontend development server

### Requirement: Observed consumption ledger
The system SHALL keep separate non-cached input, output, cache-read and cache-creation counters from received API request events. It SHALL NOT add OTel metric snapshots to the request ledger.

#### Scenario: Metrics and events describe the same usage
- **WHEN** a request event and corresponding cumulative metric points arrive
- **THEN** the request SHALL be counted once and metrics SHALL remain inspection snapshots

### Requirement: Stable request deduplication
The system SHALL deduplicate retransmitted requests with a stable server ID within a source and session. Records without a server ID SHALL be labeled with their weaker identity quality.

#### Scenario: Duplicate export
- **WHEN** an API event with the same session and request ID arrives twice
- **THEN** ledger token totals SHALL increment only once

### Requirement: Prompt attribution snapshot
The system SHALL associate requests with the HU, change and phase selected for their prompt. It SHALL NOT infer historical attribution from the session's current binding.

#### Scenario: Phase changes while events are delayed
- **WHEN** a prompt starts in planning and the session changes to apply before its request arrives
- **THEN** that request SHALL retain planning

#### Scenario: Hook arrives late
- **WHEN** a prompt hook was emitted before a new future-only binding but arrives after it
- **THEN** attribution SHALL use the binding timeline at emission time

### Requirement: Explicit historical correction
The system SHALL support future-only, single-prompt and full-session attribution scopes and SHALL audit manual changes.

#### Scenario: Correct first unassigned prompt
- **WHEN** the user chooses a retrospective prompt scope
- **THEN** the selected prompt's requests SHALL be relabeled and the action SHALL be auditable

### Requirement: Metadata minimization
The system SHALL persist only allowlisted metadata and SHALL NOT store prompt text, assistant response text, tool arguments or raw API bodies.

#### Scenario: Export includes sensitive fields
- **WHEN** an OTLP event contains a prompt or API body attribute
- **THEN** those fields SHALL NOT be written to the database

### Requirement: Synthetic data separation
The system SHALL isolate demo data from real-capture data and SHALL identify demo views and exports as synthetic.

#### Scenario: Regenerate demo
- **WHEN** the user regenerates demo fixtures
- **THEN** real-capture data SHALL remain unchanged

### Requirement: Safe configuration lifecycle
The installer SHALL back up existing settings before modifying them, require consent to replace conflicting telemetry and refuse default restoration over subsequent edits.

#### Scenario: Settings changed after installation
- **WHEN** restore detects changed settings
- **THEN** it SHALL stop without overwriting them unless force is explicitly requested

### Requirement: Transparent limits
The system SHALL distinguish observed tokens, unknown data and estimated equivalent cost. It SHALL NOT label equivalent cost as actual subscription billing or optimization signals as proven waste.

#### Scenario: Missing reported cost
- **WHEN** a request event omits cost
- **THEN** the cost SHALL remain unknown and the UI SHALL warn about incomplete aggregates
