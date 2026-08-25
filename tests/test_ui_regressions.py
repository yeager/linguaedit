"""Regression tests for bugs that parser-only tests cannot catch."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace

FIXTURES = Path(__file__).parent / "fixtures"


def _window(qapp, monkeypatch, tmp_path):
    import linguaedit.services.settings as settings_module
    import linguaedit.ui.window as window_module

    monkeypatch.setattr(window_module, "_RECENT_FILE", tmp_path / "recent.json")
    monkeypatch.setattr(settings_module, "_SETTINGS_FILE", tmp_path / "settings.json")
    settings_module.Settings.reset_instance()
    win = window_module.LinguaEditWindow()
    win._recovery_journal = window_module.RecoveryJournal(tmp_path / "recovery")
    return win


def test_switching_tabs_preserves_each_catalog(qapp, monkeypatch, tmp_path):
    win = _window(qapp, monkeypatch, tmp_path)
    try:
        win._load_file(str(FIXTURES / "test.po"))
        win._load_file(str(FIXTURES / "test.ts"))
        assert win._tabs[0].file_data is not None
        assert win._tabs[1].file_data is not None

        win._tab_widget.setCurrentIndex(0)
        qapp.processEvents()
        assert win._file_type == "po"
        win._tab_widget.setCurrentIndex(1)
        qapp.processEvents()
        assert win._file_type == "ts"
        assert win._file_data is win._tabs[1].file_data
    finally:
        win._modified = False
        win.close()


def test_closing_a_tab_keeps_remaining_tab_mapping(qapp, monkeypatch, tmp_path):
    win = _window(qapp, monkeypatch, tmp_path)
    try:
        win._load_file(str(FIXTURES / "test.po"))
        win._load_file(str(FIXTURES / "test.ts"))
        win._modified = False
        for tab in win._tabs.values():
            tab.modified = False
        win._on_tab_close(0)
        assert win._tab_widget.count() == 1
        assert set(win._tabs) == {0}
        assert win._tabs[0].file_type == "ts"
        assert win._file_type == "ts"
    finally:
        win._modified = False
        win.close()


def test_chrome_messages_uses_chrome_parser(qapp, monkeypatch, tmp_path):
    locale_dir = tmp_path / "_locales"
    locale_dir.mkdir()
    path = locale_dir / "messages.json"
    path.write_text((FIXTURES / "chrome_messages.json").read_text(), encoding="utf-8")

    win = _window(qapp, monkeypatch, tmp_path)
    try:
        win._load_file(str(path))
        assert win._file_type == "chrome_i18n"
        assert win._file_data.total_count == 4
        greeting = next(entry for entry in win._file_data.entries if entry.key == "greeting")
        assert greeting.placeholders
    finally:
        win._modified = False
        win.close()


def test_empty_html_report_and_pdf_export(qapp, monkeypatch, tmp_path):
    win = _window(qapp, monkeypatch, tmp_path)
    try:
        win._file_data = type("EmptyCatalog", (), {"path": tmp_path / "empty.po"})()
        html_path = tmp_path / "report.html"
        win._generate_custom_report([], str(html_path), bilingual=True, include_fuzzy=True)
        html = html_path.read_text(encoding="utf-8")
        assert "0 (0.0%)" in html

        pdf_path = tmp_path / "report.pdf"
        win._generate_custom_report([], str(pdf_path), bilingual=True, include_fuzzy=True)
        assert pdf_path.read_bytes().startswith(b"%PDF")
    finally:
        win._modified = False
        win.close()


def test_shortcuts_are_unique(qapp, monkeypatch, tmp_path):
    from PySide6.QtGui import QAction, QShortcut

    win = _window(qapp, monkeypatch, tmp_path)
    try:
        bindings = defaultdict(list)
        for action in win.findChildren(QAction):
            key = action.shortcut().toString().casefold()
            if key:
                bindings[key].append(action.text())
        for shortcut in win.findChildren(QShortcut):
            key = shortcut.key().toString().casefold()
            if key:
                bindings[key].append("QShortcut")
        duplicates = {key: owners for key, owners in bindings.items() if len(owners) > 1}
        assert duplicates == {}
    finally:
        win.close()


def test_inline_edit_updates_catalog(qapp, monkeypatch, tmp_path):
    win = _window(qapp, monkeypatch, tmp_path)
    try:
        win._app_settings.set_value("inline_editing_enabled", True)
        win._load_file(str(FIXTURES / "test.po"))
        item = win._tree.topLevelItem(0)
        idx = item.data(0, 0x0100)  # Qt.UserRole
        column = win._translation_column()
        item.setText(column, "Inline translation")
        assert win._file_data.entries[idx].msgstr == "Inline translation"
        assert win._modified
    finally:
        win._modified = False
        win.close()


def test_source_tree_does_not_include_compiled_translations():
    assert not list((Path("src/linguaedit/translations")).glob("*.qm"))


def test_review_mode_shows_controls_and_updates_status(qapp, monkeypatch, tmp_path):
    win = _window(qapp, monkeypatch, tmp_path)
    try:
        win._load_file(str(FIXTURES / "test.po"))
        win._toggle_review_mode()
        assert not win._review_toolbar.isHidden()
        win._set_review_status("approved")
        assert win._review_status[win._current_index] == "approved"
        assert "Approved" in win._review_status_label.text()
    finally:
        win._modified = False
        win.close()


def test_pseudolocalize_action_updates_current_translation(qapp, monkeypatch, tmp_path):
    win = _window(qapp, monkeypatch, tmp_path)
    try:
        win._load_file(str(FIXTURES / "test.po"))
        win._on_pseudolocalize_current()
        assert win._trans_view.toPlainText().startswith("⟦")
        assert win._modified
    finally:
        win._modified = False
        win.close()


def test_locale_map_double_click_requests_real_file(qapp, tmp_path):
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QListWidgetItem

    from linguaedit.ui.locale_map_dialog import LocaleMapDialog

    locale_file = tmp_path / "messages.po"
    locale_file.write_text("", encoding="utf-8")
    dialog = LocaleMapDialog(project_path=str(tmp_path))
    opened = []
    dialog.file_open_requested.connect(opened.append)
    item = QListWidgetItem(locale_file.name)
    item.setData(Qt.UserRole, str(locale_file))
    dialog._on_file_double_clicked(item)
    assert opened == [str(locale_file.resolve())]


def test_generic_header_metadata_round_trip(qapp):
    from linguaedit.ui.header_dialog import HeaderDialog

    data = SimpleNamespace(metadata={
        "name": "Original", "version": "1", "description": "Text", "custom": 42
    })
    dialog = HeaderDialog(file_type="json", file_data=data)
    assert dialog._generic_name.text() == "Original"
    dialog._generic_name.setText("Updated")
    dialog._generic_description.setPlainText("")
    dialog._save_generic_changes()
    assert data.metadata == {"name": "Updated", "version": "1", "custom": 42}


def test_search_dialog_emits_navigation_direction(qapp):
    from linguaedit.ui.search_replace_dialog import SearchReplaceDialog

    dialog = SearchReplaceDialog()
    events = []
    dialog.navigation_requested.connect(lambda *args: events.append(args))
    dialog.set_search_text("term")
    dialog._find_next()
    dialog._find_previous()
    assert events[0][-1] == 1
    assert events[1][-1] == -1


def test_search_and_replace_respects_options():
    from linguaedit.services.text_search import matches, replace

    assert matches("A cat", "cat", whole_words=True)
    assert not matches("catalog", "cat", whole_words=True)
    replaced, count = replace("Cat catalog CAT", "cat", "dog", whole_words=True)
    assert replaced == "dog catalog dog"
    assert count == 2
