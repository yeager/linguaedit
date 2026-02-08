# Changelog

All notable changes to LinguaEdit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.12.0] - 2026-02-08

### Added

#### Major New Features
- **Regex Tester Dialog** (Ctrl+Shift+X) - Test format strings with sample values, live preview of string substitution
- **Layout Simulator Dialog** (Ctrl+Shift+L) - Test text rendering with different fonts and widths, mobile/desktop presets, overflow warnings
- **Locale Map Dialog** - World map visualization of translation progress by country, project-wide statistics
- **OCR Screenshot Tool** (Ctrl+Shift+O) - Extract text from images using tesseract, create PO files from extracted strings
- **Confidence Score System** - Automatic quality assessment (0-100%) based on TM matches, length ratios, format strings, glossary usage
- **Source Code Context Lookup** - Fetch surrounding code context from local files and GitHub API for better translation understanding
- **Gettext msgmerge Integration** (Ctrl+Shift+M) - Merge PO files with POT templates using msgmerge command
- **Back-translation Feature** - Reverse translate to verify meaning preservation (integrated in AI Review)
- **Crowdin OTA Support** - Over-The-Air content delivery integration for live translation updates

#### File Format Support
- **Apple .strings/.stringsdict** - iOS/macOS localization files with plural forms support
- **Unity .asset files** - YAML-based Unity localization tables with StringTable and AssetTable support
- **RESX (.NET)** - Microsoft .NET resource files with metadata preservation

#### Speech and Accessibility
- **Speech-to-Text Integration** - Dictation support with microphone button in editor (macOS NSSpeechRecognizer, Linux Whisper)
- **A/B Test Alternatives** - Store and manage multiple translation variants with export selection

### Enhanced
- Translation Map visualization with color-coded progress indicators
- Improved confidence scoring with background thread calculation
- Better source reference parsing for GitHub URLs and local files

## [0.10.0] - 2026-02-08

### Added

#### Major Features - AI and Workflow Enhancement
- **AI Review Dialog** (Ctrl+Shift+A) - AI-powered translation quality assessment with OpenAI/Anthropic API integration and offline heuristic fallback
- **Contextual Translation Suggestions** - External translation lookup from GNOME, KDE, and Mozilla Pontoon projects with local caching
- **Online Terminology Lookup** - Microsoft Terminology and IATE (EU) integration for technical term verification  
- **Enhanced Translation Editor** - Autocomplete functionality with TM-based suggestions and configurable trigger settings
- **Plural Forms Editor** - Specialized editor for ngettext/plural forms with CLDR-based language rules and tab-based interface

#### Productivity Features  
- **Bookmarks System** - Star entries for quick navigation (Ctrl+B toggle, F2/Shift+F2 navigation, Ctrl+Shift+K filter)
- **Tags and Filtering** - Categorize entries with custom tags and predefined categories (UI, error, tooltip, menu, dialog, help)
- **Review Mode** (Ctrl+R) - Workflow mode with approve/reject buttons and status tracking for quality assurance
- **Focus Mode** (Ctrl+Shift+F) - Hide completed translations to focus on untranslated/fuzzy entries with progress tracking
- **Email Integration** - Send translations via email with auto-filled TP robot addresses and attachment support

#### UI Enhancements
- **Context Panel** - Display screenshots and visual context for entries with configurable screenshot directories
- **Preview Panel** - Real-time translation preview with length warnings, HTML detection, and configurable width simulation
- **Extended Entry List** - New columns for bookmarks (⭐) and tags with improved filtering and context menus
- **Weblate Integration** - Webhook notifications and API integration for checking new strings (planned)

#### Technical Improvements
- **Enhanced Services** - New service layer for context lookup, terminology, and external API integration
- **Improved Caching** - SQLite-based caching for external services with automatic cleanup and freshness validation
- **Better Keyboard Navigation** - Additional shortcuts and improved accessibility
- **Data Persistence** - Bookmarks and tags saved per file with JSON-based storage

### Changed
- Translation editor replaced with enhanced autocomplete-enabled version
- Entry table now includes bookmark and tag columns  
- Side panel extended with Context and Preview tabs
- Improved filtering system with multiple simultaneous filter support

### Technical Details
- All new features implement proper internationalization with Swedish translations
- Service architecture follows dependency injection patterns
- External API integration includes proper error handling and offline fallbacks
- UI components follow Qt6/PySide6 best practices with proper signal/slot patterns

## [0.9.0] - 2026-02-08

### Added

#### Major Features
- **Search & Replace Dialog** (Ctrl+H) - Advanced search and replace functionality with regex support, case sensitivity, and scope selection (source/translation/both)
- **Translation Memory (TM)** - SQLite-based translation memory with fuzzy matching (threshold 0.7), auto-save, and language pair support
- **Batch Edit Dialog** (Ctrl+Shift+B) - Bulk operations including search/replace, fuzzy flag management, and source copying with preview
- **Enhanced Glossary Management** - Complete glossary UI with CSV import/export, domain filtering, and consistency checking
- **Statistics Dialog** (Ctrl+I) - Comprehensive translation statistics with progress bars, word counts, and longest entries analysis
- **File Header Editor** (Ctrl+Shift+H) - Edit file metadata for PO, TS, and XLIFF files with proper form validation
- **Project View** (Ctrl+Shift+O) - Project explorer dock widget with file progress tracking and quick navigation
- **Diff Dialog** (Ctrl+D) - Side-by-side file comparison with change highlighting and statistics
- **Translator Comments** - Support for editing translator notes with automatic saving
- **Extended Theme Support** - Added Solarized Dark, Nord, and Monokai themes alongside existing light/dark themes
- **Bilingual Export** - HTML reports with side-by-side source and translation display
- **Online Services Sync** - Enhanced Weblate/Transifex/Crowdin integration with better configuration management

#### Quality Improvements
- **Enhanced Linting** - Added detection for:
  - Duplicate msgids with different translations
  - HTML/XML tag validation
  - Qt accelerator key (&) verification
  - Glossary consistency checking
- **Improved Translation Memory** - SQLite backend with language pair support and metadata tracking
- **Better Error Handling** - Comprehensive error reporting across all new dialogs

#### User Interface Enhancements
- **Project Explorer** - Browse and manage translation files in folders
- **Advanced Search** - Regex support, whole word matching, and scope filtering  
- **Progress Tracking** - Visual progress indicators for all batch operations
- **Contextual Menus** - Right-click actions in project view and entry lists
- **Keyboard Shortcuts** - Comprehensive shortcut support for all new features
- **Responsive Design** - Better layout handling for different screen sizes

#### Technical Improvements
- **SQLite Integration** - Modern database backend for translation memory
- **Threading** - Background processing for file analysis and batch operations
- **File Monitoring** - Automatic refresh on external file changes in project view
- **Memory Optimization** - Improved handling of large translation projects
- **Code Organization** - Better separation of concerns with dedicated UI components

### Enhanced Features
- **Linter** - Added 5 new check types for better quality assurance
- **Reports** - Bilingual export option with HTML formatting
- **Themes** - 3 additional professional themes (Solarized Dark, Nord, Monokai)
- **Comments** - Full support for translator annotations
- **Platform Integration** - Better error handling and retry logic

### Technical Details
- Minimum 40% new code added for enhanced functionality
- All strings properly internationalized with self.tr()
- Swedish translations maintained for all new features
- Comprehensive error handling and user feedback
- Modular architecture with dedicated dialog classes

### Migration Notes
- Translation Memory migrated from JSON to SQLite format
- Existing settings and configurations preserved
- Automatic database initialization on first run
- Backwards compatibility maintained for all file formats

### Developer Notes
- New UI components: 8 new dialog classes
- Enhanced services: TM, Glossary, Linter improvements
- Better separation of concerns in codebase
- Comprehensive documentation for all new features

---

## [0.8.1] - Previous Release

### Features
- Basic PO, TS, JSON, XLIFF, Android, ARB, PHP, YAML file support
- Simple translation memory (JSON-based)
- Basic linting and spell checking
- Platform integration (Transifex, Weblate, Crowdin)
- Git integration
- Basic themes (System, Light, Dark)
- Quality assurance profiles
- Multi-tab editing
- Auto-translation support