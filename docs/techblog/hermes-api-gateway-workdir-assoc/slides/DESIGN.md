# Lecture deck design contract

## 0. Research log
- Source: ../DESIGN.md and the other eleven supplied technical Markdown documents plus ../verification.json, read in full. Use their Civic Navy palette and operational evidence-first tone, not the proposed application's small typography.
- Skills: web-design (design-process) + diagrams (inline SVG architecture guidance). OMH frontend references provide prepared design/QA boundaries, not execution evidence.
- Queried local OMH palette/education, ux/education and font/docs. Retain source navy/sans rather than switching to cream/serif. No external brand assets or new web research: this is a version-bounded lecture from supplied material.

## 1. Atmosphere & identity
- Direction: Operational teaching deck; precise, readable, evidence-bounded.
- Audience assumption: Korean-speaking developers/researchers familiar with basic HTTP and files. Define BFF, DTO, SSE, idempotency, receipt and TOCTOU inline.
- Signature: each slide carries a source range and a provenance label (문서 기반 / 설계 제안 / 과거 관측 / 강의용 예시).
- Output owner/runtime: Hermes native file tools + local Python stdlib build + native browser verification. No BFF, model backend, Gateway change, profile, database or collector is implemented.
- Initial generation: new lecture artifact under slides/, original sources unchanged. Complete concept coverage takes priority over arbitrary page limits. No speaker notes; visible exercises with opt-in solution disclosure.

## 2. Color
- background #FFFFFF; surface #F4F6F9; ink #10233F; muted #4E5F78; border #D3DAE4; primary #1B3E7A; on-primary #FFFFFF.
- danger #A32118; warning #8A5A00; success #17633B: used with text labels, not truth certification.
- Diagram panel #10233F / inner #183453, diagram text #FFFFFF, secondary #D3DAE4; connections #76C9E6; approval/security edge #FFADA5. SVG arrows behind opaque node backgrounds; regions dashed; legend below boundaries.
- Main canvas white, chapter/diagram panels navy; no gradients, glass, decorative icons or card-grid boilerplate. AA contrast is an automated check target, not an unobserved claim.

## 3. Typography
- Main stack: LectureKorean, system-ui, sans-serif. Embed an OFL Korean WOFF2 subset under the renamed family LectureWikiSans, derived from locally installed NanumGothic with full attribution/license. Reuse existing cached FontTools with the Hermes interpreter's Brotli, without installation. Keep the original font unchanged. Chromium rejects the original zero-length TSI3 editor table; standard FontTools drops editor tables when creating the derivative. Record original/derivative hashes in font-provenance.json.
- Code: ui-monospace, Consolas, LectureKorean, monospace. Korean in code uses embedded font fallback.
- 1600×900 16:9 lecture canvas: title 58px, hero 86px, lead 30px, body 30px, table 26px, code 23px, SVG title/subtitle 27/23px, provenance 18px. Body line-height 1.5; headings 1.24. Weight 400/700. Smaller than the skill's default canvas is deliberate; fit and text bounds will be measured. Programmatically focused slide headings have no decorative outline; all interactive controls retain focus-visible indicators.
- CJK keep-all plus overflow-wrap:anywhere for identifiers; no line-clamp, no hidden educational content. Mobile reading mode uses body 18px/title 30px, not a shrunken desktop canvas.

## 4. Spacing & layout
- 4px base; 8/12/16/24/32/48/64/72px rhythm. Canvas padding 64px, top metadata 20px, footer reserved 56px. Flexible content area between title and footer.
- Layout primitives: statement/hero, left argument + right mechanism, comparison table, code + commentary, large inline SVG, question + revealable answer.
- Desktop fixed clipped viewport centers a transformed 1600×900 canvas; controls outside canvas. Below 900px, use normal-flow single-slide reading with document vertical scroll, wide diagrams/code have labelled focusable horizontal scroll.
- Print uses one 16:9 page per slide; all solutions visible, controls hidden. Long content must be split rather than scaled down indiscriminately.

## 5. Components and states
- Navigation buttons: min 44px, default/hover/focus-visible/active/disabled; endpoints disabled.
- Contents dialog: searchable slide index; visible label; default, searching, empty result; native dialog Escape/focus restoration. No network/loading state since static content is embedded.
- Exercise details: collapsed/expanded via native details/summary; printed expanded. Navigation keys do not hijack focused inputs/buttons/links/summary or IME composition.
- Source button opens in-document source excerpts with exact line numbers. Full original relative links also available; original links require the folder layout, but excerpts stay available when HTML is moved alone.
- LocalStorage remembers slide only, under a deck-specific key; storage failures do not prevent navigation. Hash deep links override stored page. No credentials or network requests.

## 6. Motion & interaction
- No slide animation by default; hover 120ms ease-out, reduced-motion disables transitions.
- Arrow/PageUp/PageDown/Space navigation; Home/End; T contents; F fullscreen; ? help. Visible buttons and progress count. Native browser printing.
- Focus changes deliberately on navigation but no forced focus jumps while reading. Dialog focus is restored to its trigger.

## 7. Depth & surface
- Flat white with sparse navy rules and restrained borders. No blanket shadows. Diagram panels flat with meaningful graph topology.

## 8. Accessibility, performance and QA boundary
- Semantic sections/headings, native controls, skip link, textual diagram alternatives, visible focus, status announced only on slide change.
- Target: offline rendering without auto network requests; no libraries/CDNs. Functional/geometry checks for every slide at 1440×900 and 1280×720, 768×1024, 375×812; SVG text containment and page overflow, contents filtering/Escape/focus, persistence/hash/keyboard/print count.
- The single embedded font increases file size intentionally for offline portability; no cold-load web-vitals baseline or field claims for this local deck. Record file size/load diagnostics but do not equate them with production performance.
- Screenshots and image review are distinct. If the image provider is unavailable, keep visual review incomplete and report actual DOM/render evidence. Full screen-reader/WCAG certification and live service tests are out of scope.
