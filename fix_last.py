with open('translations/linguaedit_sv.ts', 'r') as f:
    content = f.read()

old = 'Segment 1: \u201c{}\u201d  |  Segment 2: \u201c{}\u201d</source>\n        <translation type="unfinished" />'
new = 'Segment 1: \u201c{}\u201d  |  Segment 2: \u201c{}\u201d</source>\n        <translation>Segment 1: \u201c{}\u201d  |  Segment 2: \u201c{}\u201d</translation>'
content = content.replace(old, new)

with open('translations/linguaedit_sv.ts', 'w') as f:
    f.write(content)
