Place a Unicode Devanagari-capable TrueType font here (e.g. `NotoSansDevanagari-Regular.ttf`,
free from Google Fonts) to enable proper Hindi/Marathi PDF rendering.

Without a font file in this folder, Hindi/Marathi report requests automatically
and gracefully fall back to English text (reportlab's built-in PDF base fonts
only cover Latin script, and no network access was available in the build
environment to download one automatically).
