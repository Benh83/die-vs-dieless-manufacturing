"""Embed model.py into index.html so the page also works when opened as a local file.
On GitHub Pages the page fetches model.py directly; the embedded copy is the fallback.
Run after editing model.py:  python build.py"""
import re, pathlib
root = pathlib.Path(__file__).parent
src = (root / "model.py").read_text()
html = (root / "index.html").read_text()
block = '<script type="text/x-python" id="model-src">\n' + src + '\n</script>'
html, n = re.subn(r'<script type="text/x-python" id="model-src">.*?</script>', lambda m: block, html, flags=re.S)
assert n == 1, "model-src block not found"
(root / "index.html").write_text(html)
print("embedded model.py into index.html")
