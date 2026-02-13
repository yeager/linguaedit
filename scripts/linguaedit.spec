Name:           linguaedit
Version:        1.8.6
Release:        1%{?dist}
Summary:        Professional translation editor
License:        GPL-3.0-or-later
URL:            https://github.com/yeager/linguaedit
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
Requires:       python3 >= 3.10
Recommends:     ffmpeg hunspell python3-polib python3-pyyaml

%prep
%setup -q

%description
A PySide6/Qt6 translation editor supporting 17+ file formats with
translation memory, glossary, AI review, linting, Zen mode, and more.

%install
# Python package
mkdir -p %{buildroot}/usr/lib/python3/dist-packages
cp -r src/linguaedit %{buildroot}/usr/lib/python3/dist-packages/
find %{buildroot} -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Binary
mkdir -p %{buildroot}/usr/bin
install -m 755 scripts/linguaedit-gui %{buildroot}/usr/bin/

# Desktop + MIME + icon
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/mime/packages
mkdir -p %{buildroot}/usr/share/icons/hicolor/scalable/apps
install -m 644 data/io.github.yeager.linguaedit.desktop %{buildroot}/usr/share/applications/
install -m 644 data/io.github.yeager.linguaedit.xml %{buildroot}/usr/share/mime/packages/
install -m 644 data/icons/io.github.yeager.linguaedit.svg %{buildroot}/usr/share/icons/hicolor/scalable/apps/

# Man page
mkdir -p %{buildroot}/usr/share/man/man1
install -m 644 man/linguaedit-gui.1.gz %{buildroot}/usr/share/man/man1/

# Docs
mkdir -p %{buildroot}/usr/share/doc/%{name}
install -m 644 README.md CHANGELOG.md %{buildroot}/usr/share/doc/%{name}/

%post
update-desktop-database /usr/share/applications 2>/dev/null || true
update-mime-database /usr/share/mime 2>/dev/null || true
gtk-update-icon-cache /usr/share/icons/hicolor 2>/dev/null || true

%postun
update-desktop-database /usr/share/applications 2>/dev/null || true
update-mime-database /usr/share/mime 2>/dev/null || true

%files
/usr/bin/linguaedit-gui
/usr/lib/python3/dist-packages/linguaedit/
/usr/share/applications/io.github.yeager.linguaedit.desktop
/usr/share/mime/packages/io.github.yeager.linguaedit.xml
/usr/share/icons/hicolor/scalable/apps/io.github.yeager.linguaedit.svg
/usr/share/man/man1/linguaedit-gui.1.gz
%doc /usr/share/doc/%{name}/README.md
%doc /usr/share/doc/%{name}/CHANGELOG.md
%license LICENSE

%changelog
* Fri Feb 13 2026 Daniel Nylander <daniel@danielnylander.se> - 1.8.6-1
- Pre-translate runs in background QThread (UI no longer freezes)
- API key field added directly in Pre-translate dialog
- Source language auto-detection (Auto-detect option)
- Transifex integration for community translations (18 languages)
- All Swedish source strings replaced with English (proper i18n)
- .ts/.qm build automation in CI for all languages

* Fri Feb 13 2026 Daniel Nylander <daniel@danielnylander.se> - 1.8.5-1
- Pre-translate: API error dialog with skip/continue/stop
- Pre-translate: keep completed translations on cancel
- Pre-translate: progress dialog with ETA and cancel button
- Fix Lingva: update dead lingva.ml URL to translate.plausibility.cloud
- i18n: move pre-translate strings to correct LinguaEditWindow context
- i18n: fix context placement for 36 strings + add update_translations.py
- i18n: fix 4 missing newlines in translations + add 12 new strings
- i18n: Redaktör → Redigerare (editor)
- keystore: remove -T '' flag from macOS Keychain storage

* Fri Feb 13 2026 Daniel Nylander <daniel@danielnylander.se> - 1.8.4-1
- i18n: translate 51 missing strings
- i18n: fix 50 DeepL mistranslations
- i18n: fix accelerator translations mangled by DeepL
- i18n: wrap 2 OCR dialog strings in self.tr()

* Fri Feb 13 2026 Daniel Nylander <daniel@danielnylander.se> - 1.8.1-1
- Complete Swedish translation (285 to 1323 strings)
- Video subtitle overlay: translation-only yellow, source red when untranslated
- Include .qm translation files in git
- macOS icon fixes

* Thu Feb 13 2026 Daniel Nylander <daniel@danielnylander.se> - 1.8.0-1
- Video preview rewrite, live-update tree view, extended selection
- Unity MonoBehaviour parser, SRT roundtrip fix, QThread crash fix
- macOS SIGSEGV fix, dark mode contrast, Python 3.13+ compat

* Mon Feb 09 2026 Daniel Nylander <daniel@danielnylander.se> - 1.3.2-1
- Bug fixes, QSettings, 90 unit tests (see CHANGELOG.md)

* Sun Feb 09 2026 Daniel Nylander <daniel@danielnylander.se> - 1.3.1-1
- Bug fixes and UI polish (see CHANGELOG.md)

* Mon Feb 09 2026 Daniel Nylander <daniel@danielnylander.se> - 1.3.0-1
- Cross-platform credential storage
- Video preview synced with subtitle editing
- Concordance search, segment split/merge
- Security: XXE protection in all XML parsers
