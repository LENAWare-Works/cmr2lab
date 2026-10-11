# Documentation index

Start here. This repo has two kinds of writing: **reference** (read to understand the
port and its formats) and **round reports** (the engineering journal — the play-by-play
of how each bug was found and killed). If you only want to know whether it works,
read `STATUS.md`.

## Start here

- `STATUS.md` — can I use this yet? The honest answer, first screen.
- `GLOSSARY.md` — every term in plain English (terminal, clone, bfl, DXT5, D3D7, RHI…).
- `WHERE-THIS-IS-GOING.md` — the roadmap.
- `CONTROLS.md` — controls and modes.
- `MODES.md` — game modes.

## The game and its files

- `CONTAINER.md` — the `.bfl` / `.c3d` file containers.
- `C3D.md` — the 3D model format.
- `CAR.md` — how a car is assembled from parts.
- `ART-PROVENANCE.md` — where the art comes from, and the legal line (code ships,
  assets do not).

## The port

- `PORT.md` — what the port is and how it is structured.
- `PORT-PLAN.md` — the build plan.
- `DEPENDENCY-MAP.md` — what depends on what.
- `RUNTIME-RELAY.md` — the phone-to-Deck relay.
- `INSTALLER.md` — the GUI installer.
- `DECK-UI-CONSTRAINT.md` — constraints the Deck's UI imposes.

## Engineering rounds (the journal)

These are the record of the work, newest ideas last. They are detailed and opinionated;
they exist so nothing is lost, not because you need to read them in order.

- `ROAD-r6-REPORT.md` — **the current wall named:** vertex colours are dropped, so the
  road has no shading. *Read this if you want to understand the lighting bug.*
- `ROAD-r5-REPORT.md` — the shipped binary reaches a race; the road is indistinguishable.
- `ROAD-TEXTURE-OWNER.md` — road textures do reach a draw.
- `FRAMING.md` / `CAMERA-AND-NEAR-PLANE.md` — the near-plane blow-up and camera.
- `DXT-COPY-PATH.md` — DXT5 textures were never decoded (fixed).
- `DEATH-AND-LIGHT.md` — the GPU lifetime fix and the ambient-light gap.
- `WHITE-CARD.md` / `ONE-WHEEL-FRAME.md` — the white box under the car.
- `GPU-LIFETIME-FIX.md` — the first GPU ring-timeout fix.
- `DRIVE-LOOP-REGRESSION.md` / `LAUNCHER-DEAD-BUILD.md` — regressions we introduced.
- `HUD-2D.md` — HUD state, measured.
- `DRAW-CENSUS-RACE.md` / `S2-CENSUS.md` — draw censuses.
- `P3-P1-REPORT.md` — the 64-bit port pass.
- `MENU-CAR*.md` — the menu carousel rounds (there are several; they are a series).
- `FRAME-FEEDBACK.md` / `FRAME-NOTE.md` — frame-by-frame evidence notes.
- `PLAY-CHECKPOINT.md` — the playable checkpoint.
- `DEPENDENCY-MAP-CHECKPOINT.md` — checkpoint for the dependency map.

## Internal and archive

- `notes/` — working notes passed between contributors. Kept for the record, not
  part of the documentation.
- `README-ARCHIVE.md` — the original README, preserved verbatim.
- `progress-archive.md` — the old append-only progress log.
