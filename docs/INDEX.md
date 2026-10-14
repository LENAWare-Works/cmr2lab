# CMR2LRE documentation

Start with these:

- [Status](STATUS.md) — what works and what does not
- [Glossary](GLOSSARY.md) — unfamiliar terms in plain English
- [Install](INSTALLER.md) — the current installation path
- [Controls](CONTROLS.md) — controls and modes
- [Roadmap](WHERE-THIS-IS-GOING.md) — what is next

## Format and port reference

- [C3D geometry](C3D.md)
- [CAR assembly](CAR.md)
- [Container files](CONTAINER.md)
- [Port overview](PORT.md)
- [Build plan](PORT-PLAN.md)
- [Art provenance](ART-PROVENANCE.md)

## Open problems, and the two findings that close them

- [Scene ambient](AMBIENT-CONTRADICTION-RESOLVED.md) — why the lighting term measured as a
  1.0000 no-op, and why that measurement *is* the bug
- [Fog](FOG-VERIFIED-SPEC.md) — fog is gated by a capability bit the port reports as zero,
  so the game never sends it; the fix is a capability report, not a renderer feature

## Engineering evidence

The remaining reports document measured fixes and open rendering problems. They are useful
for contributors, but are not required to install or use the project. Begin with [Status](STATUS.md)
and follow links from there.
