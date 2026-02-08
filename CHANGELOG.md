# Changelog

All notable changes to LinguaEdit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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