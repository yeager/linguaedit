"""Main application window."""

from __future__ import annotations

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GLib, Pango

from pathlib import Path
from typing import Optional

from lexiloom import APP_ID, __version__
from lexiloom.parsers.po_parser import parse_po, save_po, POFileData, TranslationEntry
from lexiloom.parsers.ts_parser import parse_ts, save_ts, TSFileData
from lexiloom.parsers.json_parser import parse_json, save_json, JSONFileData
from lexiloom.services.linter import lint_entries, LintResult
from lexiloom.services.spellcheck import check_text, available_languages
from lexiloom.services.translator import translate, ENGINES, TranslationError


class LexiLoomWindow(Adw.ApplicationWindow):
    """Main editor window."""

    def __init__(self, app: Adw.Application):
        super().__init__(application=app, title="LexiLoom", default_width=1100, default_height=700)

        self._file_data = None  # POFileData | TSFileData | JSONFileData
        self._file_type = None  # "po", "ts", "json"
        self._current_index = -1
        self._modified = False
        self._spell_lang = "en_US"
        self._trans_engine = "lingva"
        self._trans_source = "en"
        self._trans_target = "sv"

        self._build_ui()
        self._setup_actions()

    def _build_ui(self):
        # Header bar
        self._header = Adw.HeaderBar()

        # Open button
        open_btn = Gtk.Button(icon_name="document-open-symbolic", tooltip_text="Open file")
        open_btn.connect("clicked", self._on_open)
        self._header.pack_start(open_btn)

        # Save button
        save_btn = Gtk.Button(icon_name="document-save-symbolic", tooltip_text="Save")
        save_btn.connect("clicked", self._on_save)
        self._header.pack_start(save_btn)

        # Menu button
        menu_btn = Gtk.MenuButton(icon_name="open-menu-symbolic", tooltip_text="Menu")
        menu = Gio.Menu()
        menu.append("Lint file", "win.lint")
        menu.append("Pre-translate all", "win.pretranslate")
        menu.append("Spell check current", "win.spellcheck")
        menu.append("File metadata…", "win.metadata")

        section2 = Gio.Menu()
        section2.append("GitHub PR…", "win.github_pr")
        menu.append_section("Integration", section2)

        section3 = Gio.Menu()
        section3.append("Check for updates", "win.check_updates")
        section3.append("Donate ♥", "win.donate")
        section3.append("About LexiLoom", "win.about")
        menu.append_section(None, section3)

        menu_btn.set_menu_model(menu)
        self._header.pack_end(menu_btn)

        # Main layout: paned
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_position(380)

        # Left: entry list
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Search
        self._search_entry = Gtk.SearchEntry(placeholder_text="Filter…")
        self._search_entry.connect("search-changed", self._on_search_changed)
        left_box.append(self._search_entry)

        # List
        sw = Gtk.ScrolledWindow(vexpand=True)
        self._listbox = Gtk.ListBox()
        self._listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._listbox.connect("row-selected", self._on_row_selected)
        sw.set_child(self._listbox)
        left_box.append(sw)

        # Stats bar
        self._stats_label = Gtk.Label(label="No file loaded", xalign=0.0, margin_start=8, margin_end=8, margin_top=4, margin_bottom=4)
        self._stats_label.add_css_class("dim-label")
        left_box.append(self._stats_label)

        paned.set_start_child(left_box)

        # Right: editor
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin_start=12, margin_end=12, margin_top=8, margin_bottom=8)

        # Source label
        right_box.append(Gtk.Label(label="Source (msgid)", xalign=0.0, css_classes=["heading"]))
        self._source_view = Gtk.TextView(editable=False, wrap_mode=Gtk.WrapMode.WORD_CHAR, vexpand=False)
        self._source_view.set_size_request(-1, 80)
        src_sw = Gtk.ScrolledWindow(child=self._source_view, vexpand=False)
        src_sw.set_size_request(-1, 80)
        right_box.append(src_sw)

        # Context / comment
        self._context_label = Gtk.Label(label="", xalign=0.0, wrap=True, css_classes=["dim-label"])
        right_box.append(self._context_label)

        # Translation
        right_box.append(Gtk.Label(label="Translation (msgstr)", xalign=0.0, css_classes=["heading"]))
        self._trans_view = Gtk.TextView(editable=True, wrap_mode=Gtk.WrapMode.WORD_CHAR, vexpand=True)
        trans_sw = Gtk.ScrolledWindow(child=self._trans_view, vexpand=True)
        right_box.append(trans_sw)

        # Buttons row
        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        translate_btn = Gtk.Button(label="Pre-translate")
        translate_btn.connect("clicked", self._on_translate_current)
        btn_row.append(translate_btn)

        spell_btn = Gtk.Button(label="Spell check")
        spell_btn.connect("clicked", self._on_spellcheck_current)
        btn_row.append(spell_btn)

        # Fuzzy toggle
        self._fuzzy_check = Gtk.CheckButton(label="Fuzzy")
        self._fuzzy_check.connect("toggled", self._on_fuzzy_toggled)
        btn_row.append(self._fuzzy_check)

        right_box.append(btn_row)

        # Spell/lint output
        self._info_label = Gtk.Label(label="", xalign=0.0, wrap=True, selectable=True)
        right_box.append(self._info_label)

        paned.set_end_child(right_box)

        # Assemble
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.append(self._header)
        main_box.append(paned)
        self.set_content(main_box)

    def _setup_actions(self):
        for name, cb in [
            ("lint", self._on_lint),
            ("pretranslate", self._on_pretranslate_all),
            ("spellcheck", self._on_spellcheck_current_action),
            ("metadata", self._on_show_metadata),
            ("github_pr", self._on_github_pr),
            ("check_updates", self._on_check_updates),
            ("donate", self._on_donate),
            ("about", self._on_about),
        ]:
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", cb)
            self.add_action(action)

    # --- File loading ---

    def _on_open(self, btn):
        dialog = Gtk.FileDialog()
        ff = Gtk.FileFilter()
        ff.set_name("Translation files (PO, TS, JSON)")
        ff.add_pattern("*.po")
        ff.add_pattern("*.pot")
        ff.add_pattern("*.ts")
        ff.add_pattern("*.json")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(ff)
        dialog.set_filters(filters)
        dialog.open(self, None, self._on_open_response)

    def _on_open_response(self, dialog, result):
        try:
            f = dialog.open_finish(result)
            path = f.get_path()
            self._load_file(path)
        except GLib.Error:
            pass

    def _load_file(self, path: str):
        p = Path(path)
        try:
            if p.suffix in (".po", ".pot"):
                self._file_data = parse_po(p)
                self._file_type = "po"
            elif p.suffix == ".ts":
                self._file_data = parse_ts(p)
                self._file_type = "ts"
            elif p.suffix == ".json":
                self._file_data = parse_json(p)
                self._file_type = "json"
            else:
                self._show_toast(f"Unsupported file type: {p.suffix}")
                return
        except Exception as e:
            self._show_toast(f"Error loading file: {e}")
            return

        self.set_title(f"LexiLoom — {p.name}")
        self._populate_list()
        self._update_stats()
        self._modified = False

    def _populate_list(self):
        # Clear
        while row := self._listbox.get_first_child():
            self._listbox.remove(row)

        entries = self._get_entries()
        for i, (msgid, msgstr, is_fuzzy) in enumerate(entries):
            label_text = msgid[:80].replace("\n", " ") if msgid else "(empty)"
            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_start=6, margin_end=6, margin_top=3, margin_bottom=3)
            src_label = Gtk.Label(label=label_text, xalign=0.0, ellipsize=Pango.EllipsizeMode.END)
            box.append(src_label)

            status = "✓" if msgstr else "○"
            if is_fuzzy:
                status = "~"
            status_label = Gtk.Label(label=f"{status} {msgstr[:50].replace(chr(10), ' ') if msgstr else '—'}", xalign=0.0, ellipsize=Pango.EllipsizeMode.END, css_classes=["dim-label"])
            box.append(status_label)

            row.set_child(box)
            self._listbox.append(row)

    def _get_entries(self) -> list[tuple[str, str, bool]]:
        """Return (msgid, msgstr, is_fuzzy) list regardless of file type."""
        if self._file_type == "po":
            return [(e.msgid, e.msgstr, e.fuzzy) for e in self._file_data.entries]
        elif self._file_type == "ts":
            return [(e.source, e.translation, e.is_fuzzy) for e in self._file_data.entries]
        elif self._file_type == "json":
            return [(e.key, e.value, False) for e in self._file_data.entries]
        return []

    def _update_stats(self):
        if not self._file_data:
            self._stats_label.set_label("No file loaded")
            return
        d = self._file_data
        self._stats_label.set_label(
            f"{d.translated_count}/{d.total_count} translated ({d.percent_translated}%) | "
            f"{getattr(d, 'fuzzy_count', 0)} fuzzy | {d.untranslated_count} untranslated"
        )

    # --- Row selection / editing ---

    def _on_row_selected(self, listbox, row):
        self._save_current_entry()
        if row is None:
            self._current_index = -1
            return
        self._current_index = row.get_index()
        self._display_entry(self._current_index)

    def _display_entry(self, idx: int):
        entries = self._get_entries()
        if idx < 0 or idx >= len(entries):
            return
        msgid, msgstr, is_fuzzy = entries[idx]

        self._source_view.get_buffer().set_text(msgid)
        self._trans_view.get_buffer().set_text(msgstr)
        self._fuzzy_check.set_active(is_fuzzy)

        # Context info
        ctx = ""
        if self._file_type == "po":
            e = self._file_data.entries[idx]
            parts = []
            if e.msgctxt:
                parts.append(f"Context: {e.msgctxt}")
            if e.comment:
                parts.append(f"Comment: {e.comment}")
            if e.tcomment:
                parts.append(f"Translator comment: {e.tcomment}")
            if e.occurrences:
                parts.append(f"References: {', '.join(f'{f}:{l}' for f, l in e.occurrences[:3])}")
            ctx = "\n".join(parts)
        elif self._file_type == "ts":
            e = self._file_data.entries[idx]
            parts = []
            if e.context_name:
                parts.append(f"Context: {e.context_name}")
            if e.comment:
                parts.append(f"Comment: {e.comment}")
            if e.location_file:
                parts.append(f"Location: {e.location_file}:{e.location_line}")
            ctx = "\n".join(parts)
        elif self._file_type == "json":
            ctx = f"Key: {self._file_data.entries[idx].key}"

        self._context_label.set_label(ctx)
        self._info_label.set_label("")

    def _save_current_entry(self):
        """Save current editor text back to data model."""
        if self._current_index < 0 or not self._file_data:
            return
        buf = self._trans_view.get_buffer()
        text = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False)

        if self._file_type == "po":
            entry = self._file_data.entries[self._current_index]
            if entry.msgstr != text:
                entry.msgstr = text
                self._modified = True
        elif self._file_type == "ts":
            entry = self._file_data.entries[self._current_index]
            if entry.translation != text:
                entry.translation = text
                if text and entry.translation_type == "unfinished":
                    entry.translation_type = ""
                self._modified = True
        elif self._file_type == "json":
            entry = self._file_data.entries[self._current_index]
            if entry.value != text:
                entry.value = text
                self._modified = True

    def _on_fuzzy_toggled(self, check):
        if self._current_index < 0 or not self._file_data:
            return
        if self._file_type == "po":
            entry = self._file_data.entries[self._current_index]
            if check.get_active():
                if "fuzzy" not in entry.flags:
                    entry.flags.append("fuzzy")
                entry.fuzzy = True
            else:
                entry.flags = [f for f in entry.flags if f != "fuzzy"]
                entry.fuzzy = False
            self._modified = True

    # --- Save ---

    def _on_save(self, btn):
        self._save_current_entry()
        if not self._file_data:
            return
        try:
            if self._file_type == "po":
                save_po(self._file_data)
            elif self._file_type == "ts":
                save_ts(self._file_data)
            elif self._file_type == "json":
                save_json(self._file_data)
            self._modified = False
            self._show_toast("Saved!")
            self._update_stats()
        except Exception as e:
            self._show_toast(f"Save error: {e}")

    # --- Search ---

    def _on_search_changed(self, entry):
        query = entry.get_text().lower()
        entries = self._get_entries()
        i = 0
        row = self._listbox.get_first_child()
        while row:
            if not query:
                row.set_visible(True)
            else:
                msgid, msgstr, _ = entries[i]
                row.set_visible(query in msgid.lower() or query in msgstr.lower())
            row = row.get_next_sibling()
            i += 1

    # --- Lint ---

    def _on_lint(self, action, param):
        if not self._file_data:
            self._show_toast("No file loaded")
            return
        self._save_current_entry()
        entries = self._get_entries()
        lint_input = []
        for i, (msgid, msgstr, is_fuzzy) in enumerate(entries):
            flags = ["fuzzy"] if is_fuzzy else []
            lint_input.append({"index": i, "msgid": msgid, "msgstr": msgstr, "flags": flags})
        result = lint_entries(lint_input)
        msg = f"Quality score: {result.score}%\nErrors: {result.error_count} | Warnings: {result.warning_count}\n\n"
        for issue in result.issues[:20]:
            src = issue.msgid[:40].replace("\n", " ")
            msg += f"[{issue.severity}] #{issue.entry_index}: {issue.message} — \"{src}\"\n"
        if len(result.issues) > 20:
            msg += f"\n… and {len(result.issues) - 20} more issues"
        self._show_dialog("Lint Results", msg)

    # --- Pre-translate ---

    def _on_translate_current(self, btn):
        if self._current_index < 0 or not self._file_data:
            return
        entries = self._get_entries()
        msgid = entries[self._current_index][0]
        if not msgid:
            return
        try:
            result = translate(msgid, engine=self._trans_engine,
                               source=self._trans_source, target=self._trans_target)
            self._trans_view.get_buffer().set_text(result)
            self._info_label.set_label(f"Translated via {self._trans_engine}")
        except TranslationError as e:
            self._info_label.set_label(str(e))

    def _on_pretranslate_all(self, action, param):
        if not self._file_data:
            self._show_toast("No file loaded")
            return
        self._save_current_entry()
        count = 0
        entries = self._get_entries()
        for i, (msgid, msgstr, _) in enumerate(entries):
            if msgstr or not msgid:
                continue
            try:
                result = translate(msgid, engine=self._trans_engine,
                                   source=self._trans_source, target=self._trans_target)
                if result:
                    if self._file_type == "po":
                        self._file_data.entries[i].msgstr = result
                    elif self._file_type == "ts":
                        self._file_data.entries[i].translation = result
                    elif self._file_type == "json":
                        self._file_data.entries[i].value = result
                    count += 1
            except TranslationError:
                continue
        self._modified = True
        self._populate_list()
        self._update_stats()
        self._show_toast(f"Pre-translated {count} entries via {self._trans_engine}")

    # --- Spellcheck ---

    def _on_spellcheck_current(self, btn):
        self._run_spellcheck()

    def _on_spellcheck_current_action(self, action, param):
        self._run_spellcheck()

    def _run_spellcheck(self):
        buf = self._trans_view.get_buffer()
        text = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False)
        if not text:
            self._info_label.set_label("No text to check")
            return
        issues = check_text(text, language=self._spell_lang)
        if not issues:
            self._info_label.set_label("✓ No spelling issues found")
        else:
            msg = "\n".join(
                f"'{i.word}' → {', '.join(i.suggestions[:3]) or '(no suggestions)'}"
                for i in issues[:10]
            )
            self._info_label.set_label(f"Spelling issues:\n{msg}")

    # --- Metadata ---

    def _on_show_metadata(self, action, param):
        if not self._file_data:
            self._show_toast("No file loaded")
            return

        if self._file_type == "po":
            meta = self._file_data.metadata
            lines = [f"{k}: {v}" for k, v in meta.items()]
            text = "\n".join(lines) or "No metadata"
        elif self._file_type == "ts":
            text = f"Language: {self._file_data.language}\nSource language: {self._file_data.source_language}"
        elif self._file_type == "json":
            text = f"File: {self._file_data.path.name}\nEntries: {self._file_data.total_count}"
        else:
            text = "No metadata"

        self._show_dialog("File Metadata", text)

    # --- GitHub PR ---

    def _on_github_pr(self, action, param):
        self._show_dialog("GitHub PR", "To push a PR, configure your GitHub token in\nPreferences → GitHub.\n\nThis feature will:\n1. Ask for auth token\n2. Fetch POT from the repo\n3. Create a branch\n4. Push your translation\n5. Open a PR\n\n(Full implementation in services/github.py)")

    # --- Updates ---

    def _on_check_updates(self, action, param):
        from lexiloom.services.updater import check_for_updates
        update = check_for_updates()
        if update:
            self._show_dialog("Update Available",
                              f"Version {update['version']} is available!\n\n{update['url']}")
        else:
            self._show_dialog("Up to date", f"You are running the latest version ({__version__}).")

    # --- Donate ---

    def _on_donate(self, action, param):
        import webbrowser
        self._show_dialog(
            "Donate ♥",
            "LexiLoom is free software.\n\n"
            "If you find it useful, consider supporting development:\n\n"
            "• GitHub Sponsors: github.com/sponsors/danielnylander\n"
            "• Ko-fi: ko-fi.com/danielnylander\n"
            "• PayPal: paypal.me/danielnylander"
        )

    # --- About ---

    def _on_about(self, action, param):
        about = Adw.AboutWindow(
            application_name="LexiLoom",
            application_icon="accessories-text-editor",
            version=__version__,
            developer_name="Daniel Nylander",
            license_type=Gtk.License.GPL_3_0,
            website="https://github.com/danielnylander/lexiloom",
            issue_url="https://github.com/danielnylander/lexiloom/issues",
            developers=["Daniel Nylander <po@danielnylander.se>"],
            copyright="© 2025 Daniel Nylander",
            comments="A translation file editor for PO, TS, and JSON files.",
            transient_for=self,
        )
        about.present()

    # --- Helpers ---

    def _show_toast(self, message: str):
        # Simple info bar approach since we don't have AdwToastOverlay in the hierarchy
        self._info_label.set_label(message)

    def _show_dialog(self, title: str, body: str):
        dialog = Adw.MessageDialog(
            heading=title,
            body=body,
            transient_for=self,
        )
        dialog.add_response("ok", "OK")
        dialog.present()
