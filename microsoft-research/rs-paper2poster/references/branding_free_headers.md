# Headers without institution names or logos

Use an explicit header template, not a prompt asking the model to delete logos.
These templates apply to any body layout in their orientation; there is no need
to duplicate the column layouts.

| Orientation | `--header` | Web label | Structure |
|---|---|---|---|
| Landscape | `v6` | Clean centered · no institutions/logos | Full-width centered title and authors; venue text below |
| Landscape | `v7` | Clean left · no institutions/logos | Left-aligned title and authors; venue text on the right |
| Portrait | `pv6` | Clean centered · no institutions/logos | Full-width centered title and authors; venue text and QR row below |
| Portrait | `pv7` | Clean left · no institutions/logos | Left-aligned title and authors; compact venue/QR rail on the right |

All four omit institution names, affiliation legends, institution logos,
conference logos and contact lines from the header. They retain the paper title
and author names. Venue text and available Paper/Code QR tiles are not logos and
remain supported. Landscape follows the existing Scan-to-Read placement rules:
`3col` has no QR; other layouts use their body scan section. Portrait keeps its
QR tiles in the header. Missing venue/QR content collapses without leaving an
empty branding rail.

## Selection

- For “不要机构名和 logo”, “no affiliations/logos”, or equivalent requests,
  choose `v6` for Landscape or `pv6` for Portrait unless left alignment is wanted.
- `--header random` and the portal's Auto option intentionally retain the existing
  branded pools (`v1`–`v5` / `pv1`–`pv5`). Unbranded headers are opt-in; explicit
  choices also stay fixed when other axes use random/batch selection.
- Keep the template's `data-institution-branding="none"` marker and structure.
  Never restore a logo zone or institution legend, even when upstream logo assets
  already exist. Do not delete those shared assets: other outputs may need them.
- Fill `{{AUTHORS_PLAIN}}` with **names only**, in paper order, with no institution
  names, superscripts, affiliation indices or contribution/correspondence markers.
  Do not reuse the marked-up `{{AUTHORS}}` value. The new headers have no
  `{{AUTHOR_LEGEND}}`, `{{CONTACT}}`, `{{LOGO_n}}` or `{{VENUE_LOGO}}` slots.
- Skip logo fetching/recovery for this poster. Still run `fit_logos.py`: it skips
  logo auto-completion for these headers but retains QR labelling/normalization.
  Run preflight after filling and fitting; it rejects reintroduced logo markup,
  affiliation containers and author superscripts in an unbranded header.
- If a cached poster uses another header, explicitly rebuild it and re-export
  HTML/PDF/PNG/PPTX rather than returning the stale branded outputs.

This is a presentation choice, **not anonymous-review redaction**. Authors,
paper links, scientific figures and research text remain; institution names
inside source figures or the paper title are not scrubbed.

```bash
python references/compose_poster.py --orientation landscape \
  --layout half --header v6 --style solid --theme blue --out <outdir>/poster.html
python references/compose_poster.py --orientation portrait \
  --layout half --header pv7 --style simple --theme teal --out <outdir>/poster.html
```

Continue with `references/build_poster.py` and the normal measured-fill/export
workflow. `POSTER_HEADER=v6|v7|pv6|pv7` is also supported by the CLI; keep the
chosen orientation compatible with the header.
