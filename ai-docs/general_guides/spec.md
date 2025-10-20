# Flash Cards Learning App — Comprehensive Developer Specification

## 1. Overview
A Windows desktop flash card learning app in Python (PySide6, SQLite, packaged as EXE). Features: persistent DB, flexible scheduling, weighted selection, import/export, sidebar UI, robust error handling, and thorough testing.
A Windows desktop application for flash card learning, packaged as a standalone EXE. Features include persistent DB, flexible scheduling, weighted card selection, import/export, and a modern sidebar UI.

## 2. Technology Stack & Dependencies
### Core Dependencies
- Python 3.11+
- PySide6 (Qt for Python) - GUI framework
- SQLAlchemy 2.0+ - ORM and database operations
- SQLite3 - Database engine
- PyInstaller - Application packaging

### Development Dependencies
- pytest - Testing framework
- pytest-qt - Qt/PySide6 testing utilities
- pytest-cov - Test coverage reporting
- black - Code formatting
- isort - Import sorting
- flake8 - Code linting
- mypy - Static type checking

### Optional Dependencies
- Inno Setup - Windows installer creation
- python-dotenv - Environment configuration
- logging - Built-in Python logging
- uuid - UUID generation (built-in)
- datetime - Date/time handling (built-in)

## 3. Architecture & File Structure
Strict separation of Model (SQLAlchemy ORM, business logic), View (PySide6 widgets), Controller (event logic).
  - `ui/` — PySide6 UI code
  - `database/` — SQLAlchemy models and DB logic
  - `core/` — Business logic, scheduling, selection
    - `serialization/` — Data serialization/deserialization
  - `main.py` — App entry point, initializes GUI, DB, controllers
  - `ai-docs/` — Documentation/specs

## 3. Data Models
### FlashCard
- `flash_card_uuid` (UUID, canonical 36-char)
- `name` (str, required)
- `question` (str, required)
- `answer` (str, required)
- `difficulty` (int, 1–10, default 5)
- `active` (bool)
- `creation_datetime` (datetime)
- `update_datetime` (datetime)
- `deleted` (bool)
- `category_uuid` (UUID, required)

### Category
- `category_uuid` (UUID, canonical 36-char)
- `name` (str, required)
- `active` (bool)
- `deleted` (bool)
- `priority` (int, >=1, required)
- `creation_datetime` (datetime)
- `update_datetime` (datetime)

### Schedule
- `schedule_uuid` (UUID, primary key)
- `scope` (str: 'global', 'category', 'card')
- `category_uuid` (UUID, nullable)
- `flash_card_uuid` (UUID, nullable)
- `allowed_days` (str, e.g. 'Mon,Tue,Wed')
- `start_hour` (int)
- `end_hour` (int)
- `frequency_mode` (str: 'times_per_week', 'times_per_day', 'fixed_interval')
- `times_per_week` (int, nullable)
- `min_times_per_day` (int, nullable)
- `max_times_per_day` (int, nullable)
- `interval_minutes` (int, nullable)
- `creation_datetime` (datetime)
- `update_datetime` (datetime)
- `active` (bool)
- `deleted` (bool)

### ScheduledEvent
- `event_uuid` (UUID, primary key)
- `schedule_uuid` (UUID, foreign key)
- `flash_card_uuid` (UUID, foreign key)
- `scheduled_datetime` (datetime)
- `status` (str: 'pending', 'completed', 'ignored', etc)

### Settings
- `setting_key` (str, primary key)
- `setting_value` (str/json)
- `update_datetime` (datetime)

## 4. Data Handling & Serialization
### Data Model Serialization
- All models support serialization to multiple formats:
  - JSON: For API interactions and settings storage
  - CSV: For user-friendly import/export
  - SQLite: For database persistence
  - Binary: For efficient backup/restore operations

### Serialization Features
- Type safety and validation during serialization/deserialization
- Schema versioning for backward compatibility
- Custom serializers for complex types (UUID, datetime)
- Efficient binary serialization for large datasets
- Compression support for serialized data

### Import/Export Handling
- Flexible CSV header schema (case-insensitive, aliases)
- Required fields: FlashCard — name, question, answer, category_uuid/name; Category — name, priority
- Import: match by UUID if present, else by name; preview, error log, partial import
- Export: all fields, canonical headers
- Option to overwrite or merge on import
- Support for different character encodings
- Batch processing for large datasets

## 5. Scheduling & Frequency
Scheduling rules at global, category, and card level (precedence: card > category > global)
All scheduling and frequency parameters are stored in normalized tables in the SQLite database:
  - Schedules can be modified, deactivated, or deleted at any moment via the UI or API
  - `schedules` table: stores global, category, and card-level rules (foreign keys to category/card as needed)
  - Each schedule row includes allowed timeframes, days, frequency mode, and parameters
  - Scheduled question times for preview/upcoming can be computed on-the-fly or cached in `scheduled_events` table

Frequency modes (all confirmed):
1. Times-per-week:
   - Specify N times per week (1-7)
   - System randomly chooses N allowed days from the allowed-days set
   - Chosen days persist for the entire week
   - New random selection each week

2. Times-per-day (min-max):
   - Specify minimum and maximum times per allowed day
   - System randomly selects count between min-max for each day
   - Divides allowed timeframe into equal slots
   - Applies ±15% time jitter to each slot
   - Different random count possible each day

3. Fixed intervals:
   - Specify fixed interval in minutes
   - System schedules questions at exact intervals
   - Only within allowed timeframe
   - Consistent timing each day
Preview upcoming scheduled questions
Export/import schedule settings as part of DB or as JSON

## 6. Selection Algorithm
- Weighted random selection:
  - `weight = (category_priority ^ alpha) * (difficulty ^ beta)`
  - Default: alpha=1.5, beta=1.0 (confirmed values)
  - alpha controls category priority influence
  - beta controls difficulty influence
  - Higher priority/difficulty = more frequent
  - Selection probability proportional to weight

## 7. UI/UX Flows
### Navigation & Layout
- Sidebar navigation with sections:
  - Dashboard
  - Cards
  - Categories
  - Schedule
  - Import/Export
  - Review Log
  - Settings

### Cards Section
- List/search/filter cards
- Add/edit/delete individual cards
- Bulk import/export
- Activate/deactivate cards
- Assign to categories
- View card statistics

### Categories Section
- List/search/filter categories
- Add/edit/delete categories
- Activate/deactivate categories
- Adjust priority (affects selection weight)
- Assign cards to categories
- Bulk import/export
- View category statistics

### Schedule Section
- View/edit schedules at all levels:
  - Global defaults
  - Category-specific
  - Individual cards
- Set timeframes and allowed days
- Configure frequency modes
- Preview upcoming scheduled questions
- Export/import schedule settings

### Import/Export Section
- Import CSV with preview
- Error logging for invalid entries
- Support partial imports
- Export all data with canonical headers
- Configurable overwrite/merge options

### Review Log Section (all confirmed)
- List/search/filter all review events
- View detailed event information:
  - Timestamp
  - Card details
  - User's answer
  - Difficulty adjustments
- Export log to CSV
- Filter by:
  - Card
  - Category
  - Date range
  - Rating
- Show summary statistics:
  - Correct percentage
  - Average difficulty
  - Progress trends

### Settings Section
- Configure default scheduling parameters
- Adjust selection algorithm weights (alpha/beta)
- Manage system preferences
- Handle edge cases:
  - Timezone settings
  - DST transitions
  - Missed schedules
  - System permissions

## 11. Packaging & Installer
- PyInstaller for EXE
- Ready for external installer (e.g., Inno Setup) to bundle EXE and blank DB

## 12. Background Operation & System Tray
### Startup & Background
- Automatic start with Windows (configurable)
- Runs as a background Windows service
- Minimal resource usage when minimized

### System Tray Integration
- Always-visible tray icon with status indication
- Right-click menu with common actions:
  - Show/Hide main window
  - Quick add card
  - View upcoming reviews
  - Pause/Resume scheduling
  - Access settings
  - Exit application

### Notifications & Alerts
- Toast notifications for scheduled reviews
- Custom notification sound options
- Do Not Disturb mode support
- Notification aggregation for multiple cards

### Window Management
- Minimize to tray option (configurable)
- Close button behavior options:
  - Exit application
  - Minimize to tray
  - Prompt user
- Quick restore with double-click
- Global hotkey support (configurable)

## 13. Error Handling & Logging
- Log Levels and Storage:
  - Error logs stored in file system and database
  - Rotating log files with size limits
  - Critical errors logged to Windows Event Log
  - Different log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

- Error Scenarios:
  - Database connection failures
  - File system access issues
  - CSV import/export errors
  - Scheduling conflicts
  - Background service failures
  - UI operation timeouts

- User Notifications:
  - Non-blocking toast notifications for background events
  - Modal dialogs for critical errors requiring action
  - Status bar updates for general information
  - Error summaries in relevant UI sections

- Recovery Mechanisms:
  - Automatic retry for background operations
  - Database connection pool with reconnection logic
  - Transaction rollback handling
  - Corrupt file detection and recovery

## 14. Data Backup & Recovery
- Automatic Backups:
  - Configurable backup frequency (default: daily)
  - Rolling backup retention (last 7 days)
  - Backup before major operations (import, bulk updates)

- Backup Storage:
  - User-configurable backup location
  - Compressed SQLite database dumps
  - Settings and schedules included
  - Backup file naming convention with timestamps

- Recovery Options:
  - One-click restore from backup
  - Point-in-time recovery
  - Partial restore capabilities
  - Backup integrity verification

## 15. Performance Requirements
- Database Performance:
  - Support up to 100,000 cards
  - Support up to 1,000 categories
  - < 1 second response time for card selection
  - < 2 seconds for import/export operations

- Memory Usage:
  - Maximum 500MB RAM usage
  - Efficient resource cleanup
  - Lazy loading for card content
  - Image size limits for cards

- UI Responsiveness:
  - < 100ms for UI operations
  - Async loading for large datasets
  - Progress indicators for long operations
  - Efficient list virtualization

## 16. Security & Data Privacy
- Data Protection:
  - Optional database encryption
  - Secure storage of sensitive settings
  - Export file encryption option
  - Secure temporary file handling

- Access Control:
  - Optional password protection
  - Windows user integration
  - Feature-level access control
  - Audit logging for sensitive operations

## 17. Final Notes
- All business logic and DB access isolated from UI
- Clean, robust, distributable code
- Ready for developer handoff
- Regular security updates support
- Comprehensive testing coverage
- Performance monitoring capabilities
