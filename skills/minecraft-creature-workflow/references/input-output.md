# Inputs and outputs

## Minimum input card

Record these fields before modeling or conversion:

| Field | Required | Notes |
| --- | --- | --- |
| Creature id | Yes | Lowercase namespace/path identifier; do not use a display name as an id. |
| Creature class | Yes | `npc`, `mob`, `elite`, or `boss`. |
| Edition | Yes | `java`, `bedrock`, or `both`. |
| Minecraft version | Yes | Exact version or `unconfirmed`; never infer it from a filename. |
| Loader or pack version | Target-dependent | Fabric, Forge, NeoForge, Quilt, or Bedrock pack format. |
| Model target | Yes | Vanilla Java, Bedrock geometry, GeckoLib, or another explicitly named target. |
| Scale and hitbox | Yes | Record assumptions separately; model dimensions do not define gameplay collision automatically. |
| Animation list | Yes | Include names, loop behavior, trigger, length, and bone ownership. |
| Asset origin | Yes | `original`, `user-provided`, or `third-party`. |
| License evidence | Required for third-party | Source URL, revision, license text or authoritative evidence, and checked date. |

## Expected package layout

```text
creature-package/
  creature-manifest.json
  source/
    creature.bbmodel
  textures/
    creature.png
  exports/
    java-or-bedrock-or-geckolib-files
  code/
    renderer-and-entity-sources-if-applicable
  provenance/
    LICENSES/
    NOTICE.txt
    source-notes.md
  validation/
    validation-report.json
    validation-report.md
```

Use only the directories relevant to the target. Do not create placeholder files merely to satisfy the layout.

## Output classes

- `source`: editable `.bbmodel`, original texture source, and authoring notes.
- `runtime`: target exports and integration code.
- `provenance`: license evidence, attribution, NOTICE files, source URLs, revisions, and transformations.
- `validation`: machine-readable and human-readable reports, including missing checks.

## Creature-class guidance

- `npc`: prioritize readable idle, talk, look-at, walk, hurt, and interaction states.
- `mob`: prioritize locomotion, target acquisition, attack, hurt, death, and spawn states.
- `elite`: add telegraphs, phase-safe attack animations, equipment or variant slots, and readable cooldown states.
- `boss`: define phase transitions, invulnerability or casting poses, attack telegraphs, death sequence, and performance limits before detailed animation work.

These are workflow prompts only. They do not prescribe gameplay code or claim that a specific loader supports a feature.
