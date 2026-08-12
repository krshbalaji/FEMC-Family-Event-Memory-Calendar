# ACA_PACK000 — Constitutional Master Index

This file is the canonical index pointer for constitutional packs in this repository.

Purpose
- Provide a single, discoverable entry that points to constitutional packs under the `CONSTITUTION/` folder.
- Document that constitutional content is authoritative for high-level policy and governance; implementation and architectural details live under `ARCHITECTURE/` and `ENGINEERING/` respectively.

Notes and usage
- This file intentionally does not duplicate constitutional content. It lists where to find constitutional packs and serves as the canonical navigation entry.
- To review constitutional material, inspect the files and subfolders under `CONSTITUTION/`.
- Authority model (conceptual):

	CONSTITUTION
		↓
	ARCHITECTURE
		↓
	cross-cutting offices / domain offices
		├── ENGINEERING — implementation authority
		├── PRIVACY — privacy policy/control authority
		├── MEMORY
		├── MEDIA
		├── CALENDAR
		├── EVENTS
		└── other domain offices

- Note: `ENGINEERING` and `PRIVACY` are peer cross-cutting authorities with distinct responsibilities; neither is a subordinate of the other.

See also
- [ARCHITECTURE/README.md](ARCHITECTURE/README.md) for architectural navigation.
