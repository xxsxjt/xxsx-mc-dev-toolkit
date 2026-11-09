# Format routing

## Blockbench source

Use the target-specific Blockbench project format when starting a new model. Save `.bbmodel` as the editable source and record the Blockbench format version. The `.bbmodel` format is JSON-based but is an internal project format and may change; it is not a general-purpose interchange contract.

## Java Edition

Choose one path and label it explicitly:

- **Vanilla-style Java model**: export or generate Java model code/layer definitions, texture files, and a client renderer registration appropriate to the exact loader/version.
- **GeckoLib**: export a GeckoLib model and animation JSON plus texture, then connect them through a `GeoModel` and animation controllers.
- **Other Java renderer**: name the library or renderer and document its exact import/export contract. Do not call it vanilla or GeckoLib by analogy.

The entity class, registration, renderer, model, texture, and animation are separate validation surfaces. Rendering code belongs on the client side; entity logic and registration need a side-specific review.

## Bedrock Edition

The usual resource-pack surfaces are:

- `models/entity/*.geo.json` for geometry;
- `textures/.../*.png` for textures;
- `animations/*.animation.json` for keyframes;
- `animation_controllers/*.animation_controllers.json` for states and transitions;
- client entity and render-controller JSON for binding geometry, textures, and animation names.

Check identifier casing, root bones, pivots, texture dimensions, resource paths, `format_version`, and Molang conditions. Test the complete reference chain instead of validating each JSON file in isolation.

## GeckoLib

At minimum, track:

- model: `resources/assets/<namespace>/geo/.../*.geo.json`;
- texture: `resources/assets/<namespace>/textures/.../*.png`;
- animation: `resources/assets/<namespace>/animations/.../*.animation.json`;
- Java `GeoModel` resource methods;
- controller registration and trigger logic;
- loader and GeckoLib version.

Animation controllers should have clear bone ownership. If two controllers modify the same bone concurrently, document the intended priority or split the channels.

## Conversion rules

- OBJ/glTF/FBX are source formats for conversion, not direct Minecraft entity deliverables.
- Bedrock geometry and GeckoLib share concepts but are not interchangeable by renaming files. Convert and inspect identifiers, pivots, coordinate conventions, animation channels, and resource locations.
- A texture conversion is a derived work. Preserve the original source record and record the tool, version, command or UI operation, and output hash.
- Never claim runtime compatibility from a successful JSON parse alone.

## Version evidence

For every Java target, record Minecraft, loader, mappings, Java, Gradle, and major library versions as one tuple. For Bedrock, record the pack format and the documentation version or game build used for validation. Keep unresolved fields as `unconfirmed`.
