# Licensing and provenance

## Evidence threshold

An asset is `license_verified` only when the source identifies the work and the rights holder or authoritative distributor provides a license or public-domain dedication that covers the actual asset being used. A repository's software license does not automatically cover a model, texture, animation, screenshot, or bundled archive.

Record the license separately for geometry, texture, animation, sound, code, and documentation when they come from different sources.

## Rights decision

For each asset, answer independently:

- commercial use: `yes`, `no`, or `unknown`;
- modification/adaptation: `yes`, `no`, or `unknown`;
- redistribution of the asset or derivative: `yes`, `no`, or `unknown`;
- attribution required: `yes`, `no`, or `unknown`;
- NOTICE or copyright text required: `yes`, `no`, or `unknown`.

If any right required by the requested delivery is `no` or `unknown`, do not include the asset in a reusable delivery. Keep it as a rejected or pending candidate with the reason.

## Preferred records

- CC0 or an explicit public-domain dedication: preserve the source and checked date even when attribution is not legally required.
- CC BY: preserve title, author/licensor, source URL, license URL, and adaptation note.
- MIT, BSD, Apache-2.0, or similar: verify that the license applies to the asset, preserve the copyright and license text, and record NOTICE requirements.
- ShareAlike or copyleft: keep separate from permissive assets and document the resulting distribution obligations. Do not label it unrestricted.
- NC, ND, no-license, private terms, or ambiguous marketplace terms: reject for a general reusable library unless the user supplies additional permission.

Use SPDX identifiers where one exists, but keep the original license text or evidence URL. `NOASSERTION` means that the license was not established; it is not approval.

## Attribution record

Use a TASL-style record when applicable: title, author/licensor, source, license. Include the exact source URL rather than a shortened link. For adaptations, state that the file was modified or converted and identify the transformation.

## Hash and revision policy

- Hash every delivered source and export with SHA-256. Record the relative path, byte count, algorithm, and lowercase hexadecimal digest.
- Record an immutable revision when available: release tag, commit, asset version, or publication date. A mutable `main` URL alone is weak evidence.
- Hash the exact local file that is delivered. Recompute after any conversion or texture edit.
- Use `Get-FileHash -Algorithm SHA256` on Windows or an equivalent standard tool. Never print secrets or private URLs into the report.

## Candidate status values

`discovered` means a source was found; `license_verified` means rights evidence was checked; `downloaded` means bytes were saved locally; `converted` means a target export exists; `runtime_validated` means the target environment rendered or loaded it. A candidate may have multiple statuses, but later status never implies earlier rights approval.
