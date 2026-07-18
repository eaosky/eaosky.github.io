# EAO Target Scout — Emirates Astronomical Observatory

A **rig-aware, all-sky** astrophotography target planner for the EAO site
(23.578079817186588, 54.745467101634326). Pick a camera and enter focal length +
f-ratio, and the whole list re-ranks by **how well each target fills *your*
frame** — think like a photographer, not an astronomer. Covers both **narrowband
emission** targets and **broadband** targets (galaxies, clusters, reflection &
dark nebulae, bright PNe/SNRs). Hosted on GitHub Pages, live from a Google Sheet
override layer, expanded by a weekly cloud job.

Live: `https://arunvijayp-cmyk.github.io/eao/`

## How it works
- **Framing-first ranking (balanced):** framing fit is the dominant score factor
  (0.45), then culmination altitude (0.20), surface brightness (0.20), dark-sky
  hours (0.15). Nothing is hidden — too-small and mosaic-scale targets are
  demoted and flagged. Change the focal length and the list re-orders live.
- **Fast at scale:** observability (altitude, best months, dark-hours) depends
  only on the fixed site, so it's **precomputed** for the whole catalogue; the
  browser only does the rig-dependent framing/scoring math when you change
  cameras. Stays snappy across thousands of targets.
- **Data layers (merged, in priority order):**
  1. Your **Google Sheet** overrides/additions (win by name)
  2. `catalog.json` — the cloud-built comprehensive catalogue
  3. built-in seed (132 curated NB+BB targets) as fallback

## The cloud catalogue builder (`.github/workflows/build_catalog.yml`)
Runs weekly in GitHub's cloud (PC off). Pulls **OpenNGC** (all NGC/IC) + VizieR
(**Sharpless** HII, **Green** SNRs), classifies each object NB/BB/both, filters
to your sky window and imageable sizes, precomputes observability, and commits
`catalog.json`. There's a **Run workflow** button for on-demand rebuilds.

## Your Google Sheet
`EAO Target Scout — My Targets (overrides)` — add rows to include or override
targets. Columns: `name, common_name, type, imaging_type (NB/BB/both), ra_deg,
dec_deg, size_major_arcmin, size_minor_arcmin, magnitude, surface_brightness,
emission, note, ref_url`. RA/Dec in decimal degrees. Share it "Anyone with the
link – Viewer" for the dashboard to read it. Hand-added targets get their
observability computed in-browser automatically.

## Rebuild locally
```
python3 data/build_seed.py       # regenerate the seed (needs the narrowband-scout engine)
python3 webapp/build_webapp.py <SHEET_ID> <GID>   # rebuild dist/index.html
```

## Caveats
- Bulk-catalogue objects have **estimated** sizes/emission and plain
  designations; your curated seed + Sheet entries are the vetted layer.
- In-browser observability for hand-added targets omits precession/refraction
  (~1° in marginal twilight months); best-months/scores are unaffected.
