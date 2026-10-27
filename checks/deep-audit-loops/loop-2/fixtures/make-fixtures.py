#!/usr/bin/env python3
"""L2-D fixture generator (harness-only; writes under fixtures/)."""
import json, os

d = os.path.dirname(os.path.abspath(__file__))

def w(name, text, mode='w'):
    with open(os.path.join(d, name), mode, newline='') as f:
        f.write(text)

w('l2d-a.md', '# L2D Alpha\n\n- item one\n- item two\n\n> quoted line\n\nSome **bold** and *em* text.\n')
w('l2d-crlf.txt', 'line one\r\nline two\r\nline three\r\n')
w('l2d-table.html', '<html><body><h1>L2D Table Doc</h1><p>Intro <strong>bold</strong> text.</p>'
                    '<table><tbody><tr><td>A1</td><td>B1</td></tr><tr><td>A2</td><td>B2</td></tr></tbody></table></body></html>')
w('l2d-empty.md', '')
w('l2d-empty.txt', '')
w('l2d-data.json', '{"project":"l2d","items":[1,2,3],"note":"plain data file, not a backup"}')
w('l2d-fake.docx', 'this is not really a word document, just plain text with a docx extension\nsecond line\n')
w('l2d-unknown.xyz', 'unsupported content\n')
w('l2d-bad-parse.json', '{not json at all')
w('l2d-bad-format.json', json.dumps({"format": "wrong-format", "schemaVersion": 1, "scope": "all", "notebook": {}}))

# huge md ~5MB
with open(os.path.join(d, 'l2d-huge.md'), 'w') as f:
    f.write('# Huge Fixture\n\n')
    for i in range(60000):
        f.write('Paragraph %d: the quick brown fox jumps over the lazy dog repeatedly.\n' % i)

# minimal structured Google export (two tabs: parent + child)
g = {
    "format": "notepad-google-docs",
    "document": {
        "title": "L2D Google Doc",
        "tabs": [
            {
                "tabProperties": {"tabId": "t1", "title": "Main tab"},
                "documentTab": {"body": {"content": [
                    {"paragraph": {"elements": [{"textRun": {"content": "Hello from google tab one"}}]}},
                    {"paragraph": {"elements": [{"textRun": {"content": "Second paragraph with bold",
                                                              "textStyle": {"bold": True}}}]}}
                ]}},
                "childTabs": [
                    {
                        "tabProperties": {"tabId": "t2", "title": "Sub tab"},
                        "documentTab": {"body": {"content": [
                            {"paragraph": {"elements": [{"textRun": {"content": "Sub tab content"}}]}}
                        ]}}
                    }
                ]
            }
        ]
    }
}
w('l2d-google.json', json.dumps(g, indent=1))
print('fixtures written to', d)
