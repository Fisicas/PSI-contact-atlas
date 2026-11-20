# Browser review — 1.1.0-rc.2

*Historical review record. For v1.1.0 publication and citation information, see [release notes](RELEASE_NOTES_1.1.0.md) and the [citation guide](CITATION.md).*

Completed November 20, 2026 after explicit permission for isolated local browser testing. Fresh headless Chrome 157.0.8103.79 and Edge 157.0.4341.60 used temporary nonpersistent contexts. No personal/open browser, published site, or external service was controlled. Page traffic was restricted to local HTTP, file, blob and data resources.

Chrome checked all 160 scene pages: table values, original label toggles, common-scale defaults, closed/lazy density panels, both density modes, native protomer identity and four explicit 1JB0 unavailable panels. Edge checked six representative/edge scenes. Both browsers checked all four 40-row comparison tables (1,617 numeric values), missing-reason tooltips, sorting/reset, scene controls/history/fullscreen, themes and persistence, and 42 route/theme/viewport combinations each (1440, 768 and 390 px).

Forty actual image exports were decoded: 20 PNGs and 20 GIFs, including phone-width GIFs. GIFs contain 75 distinct frames at 80 ms/frame for the selected six-second turn. Fifty actual native-data downloads match the canonical files byte for byte across HTTP/file delivery in both browsers. Search, method filters (3 X-ray / 19 cryo-EM entries) and phone matrix horizontal scrolling were exercised.

## Observed issues and corrections

1. A delayed scene resize callback tried to update a removed scale note after navigation. Observers now disconnect during cleanup, scheduled callbacks check ownership, and stale scene/preview loads are ignored. Deliberately delayed navigation tests pass.
2. At a 390 px viewport a PNG export caption measured 4,402 px within a 2,560 px image. PNG/GIF export captions now wrap at word boundaries with adequate footer height. The molecular plot and default label routines are unchanged.
3. Chrome file previews opened mmCIF/PyMOL text instead of saving it. Lazy per-scene classic-script payloads now save the exact UTF-8 canonical bytes through Blob downloads. The original downloadable files and normal HTTP anchors are retained. All 480 payload assets are independently hash/byte/identity checked; no coordinate or newline conversion occurs.

All final browser runs show zero JavaScript errors, failed requests, page overflow findings or blocked external requests. The eight new-entry canvas sheets (32 environments) and representative desktop/tablet/phone, light/dark, density and export screenshots were visually inspected. At matched integer host dimensions, all 64 baseline/current molecule-and-label regions match pixel for pixel; 48 complete bitmaps match exactly. The remaining 16 phone bitmaps differ only along one scale-bar stroke scanline. The molecular drawing and label code itself is byte-identical.

## Reproduction and limits

Use a separate suitable browser-test environment or a separate `pip --target` directory with `build/requirements-browser.txt`; do not upgrade a shared scientific environment. The website itself remains static and has no new runtime dependency. Example from the repo root:

```text
python tests/browser_review.py --repo . --work-dir PATH_OUTSIDE_REPO --runtime SEPARATE_PACKAGE_DIRECTORY --engine chrome --executable PATH_TO_CHROME
```

Use a new output folder for every run (`--out run_v02`, etc.). The script refuses an existing run folder and always launches a fresh headless browser/context. `--smoke` narrows the scene sweep while keeping comparison/layout/export/download checks. Windows Chrome/Edge executable defaults are supplied; pass `--executable` explicitly elsewhere. Local full-resolution screenshots, original failed runs, regressions and actual downloaded files remain in the separate browser-review audit folder; the compact source-bound receipt is [browser_review_rc2_v01.json](../build/provenance/checks/browser_review_rc2_v01.json).

These are Windows headless desktop browsers at emulated widths, not physical mobile devices, Safari/Firefox, or a complete accessibility audit. Browser success does not validate chemical geometry, occupancy, redox state or hydrogen bonding. Scientific qualifications remain in [SCIENTIFIC_REVIEW.md](SCIENTIFIC_REVIEW.md). GitHub CI has not run; no publication action occurred.

## rc.3 scientific-note follow-up

Fresh isolated Chrome 157.0.8103.79 checked all 160 rc.3 scene pages, including 16 new local-density/water/axial warning placements, all four comparison tables, 42 layout/theme/viewport combinations, 18 actual decoded image exports and 25 byte-exact native downloads. No JavaScript, request, external-traffic or layout issues were reported. The 21 available-data entries now show completed scoped-review notes; 1JB0 remains unreviewed/unavailable. The earlier rc.2 Edge runs remain evidence for their original candidate; Edge was not rerun for rc.3. Current compact receipt: [browser_review_rc3_v01.json](../build/provenance/checks/browser_review_rc3_v01.json). No molecular viewer/label code or scientific values changed.


## Current v06 interactive-density review

The candidate now integrates all 156 available interactive density scenes (39 protomers / 21 structures) and 208 exact clickable thumbnail presets, retaining every static image. The full atlas remains 22 structures / 40 protomers / 160 scenes; 1JB0's four density routes are explicitly unavailable. The 312-load file/HTTP browser review and independent native-atom/map/preset verifier pass. New receipts state current scope separately from historical original-viewer checks. Original molecule/label algorithms, native source files, canonical contacts/downloads, static figures and selected branding are preserved. See [interactive methods](INTERACTIVE_DENSITY.md) and [current validation receipts](VALIDATION.md). Publication, remote CI and live settings remain pending approval.
