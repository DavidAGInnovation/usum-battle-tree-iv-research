# Reproduction guide

This guide uses external ROM, executable, and source paths as inputs. Do not copy the ROM, the extracted executable, or the source archive into the repository.

## Inputs

Set these shell variables to local copies of the required files:

```sh
ROM_3DS="/path/to/Pokemon Ultra Sun (USA) Decrypted.3ds"
CODE_BIN="/path/to/extracted/code.bin"
```

## Recover the retail AI archive and executable

With a decrypted US `.3ds` image, the bundled extractor recovers the exact
Battle AI GARC, all numbered AMX members, a JSON manifest, and the raw ExeFS
`.code` section:

```sh
python3 scripts/extract-retail-battle-ai.py \
  "/path/to/Pokemon Ultra Sun (USA) Decrypted.3ds" \
  /tmp/usum-retail-battle-ai
```

The manifest records the source RomFS path, GARC/member hashes, and the
`.code` hash. It is safe to keep the output outside the repository because
the ROM and the extracted executable are copyrighted retail inputs.

The archive-index source file `BattleAi.gaix` is not present in the supplied
snapshot. Its numeric map can nevertheless be checked against the archived
Pawn project/tool evidence and the retail member order documented in
[battle-ai.md](battle-ai.md):

```text
0 allowance   1 band       2 basic      3 double
4 expert      5 intrude    6 item       7 moving
8 pokechange  9 royal      10 strong
```

This is an exact numeric reconstruction of the index map; extracting the
original generated header or tracing `datIdx` at runtime would only provide an
additional direct artifact/corroboration.

The analyzed retail build produced an extracted raw `.code` file with SHA-256:

```text
b5388f7500d91be01499a99ca007c98212068608ed7c83c43952e1d5148e9e09
```

Hash the extracted file before relying on the addresses:

```sh
shasum -a 256 "$CODE_BIN"
```

## Static disassembly

The executable’s static `.code` mapping base for this analysis is `0x100000`. With radare2 (or an equivalent ARM32 disassembler):

```sh
radare2 -a arm -b 32 -m 0x100000 "$CODE_BIN"
```

Useful commands inside radare2:

```text
aaa                      # required before axt/xref queries
s 0x159790; pd 24       # normal trainer-ID IV selection
s 0x1581a8; pd 20       # generic partner branch
s 0x157a1c; pd 24       # ScoutLilie/scouted-partner path
s 0x15faf4; pd 32       # common constructor helper
s 0x158760; pd 180      # special trainer selector constants
s 0x4ad608; pd 80       # runtime CoreDataBlockB accessor
s 0x321498; pd 36       # HP IV setter
s 0x3215b0; pd 36       # Speed IV setter
s 0x3215f0; pd 36       # Attack IV setter
s 0x321630; pd 36       # Defense IV setter
s 0x321a88; pd 36       # Special Attack IV setter
s 0x321ac8; pd 36       # Special Defense IV setter
s 0x324d84; pd 96       # ChangeTalentPower dispatch
axt 0x324d84             # direct callers of ChangeTalentPower
s 0x320528; pd 48       # whole-core initialization copy
axt 0x320528             # direct callers of that initializer
```

The same locations as raw offsets are `0x59790`, `0x581a8`, `0x57a1c`,
`0x5faf4`, and `0x58760` respectively. The writer-inventory locations are
documented with both forms in the [retail writer inventory](retail-iv-routine.md#retail-binary-writer-inventory-for-the-analyzed-build).

## Source cross-check

For the Momiji snapshot documented in [docs/sources.md](sources.md), inspect the following files:

```text
prog/Field/FieldStatic/source/BattleInst/BattleInst.cpp
prog/Field/FieldStatic/source/BattleInst/BattleInstTool.cpp
prog/Field/FieldStatic/include/BattleInst/BattleInstData.h
prog/Savedata/include/BattleInstSave.h
prog/Savedata/source/BattleInstSave.cpp
```

The relevant source functions are `GetPowerRndNormal`, `MakeTrainerPokemon`, `MakePartnerPokemon`, `ScoutLilie`, `CreatePokemon`, `MakeAiPartner`, and `SetVsPokemon`.

## Optional local helper

The included `scripts/inspect-offsets.sh` helper prints the target offsets and, when given a raw `.code` file, invokes radare2 for a compact inspection.

## Battle-AI control-flow audit

After extracting and disassembling the eleven members of RomFS `/a/0/8/4`,
run the abstract reachability audit:

```sh
python3 scripts/audit-battle-ai-flow.py /path/to/pawn-lst-directory
```

The report separates all statically decoded branch opcodes from the subset in
the conservative may-reachable graph. It does not model the retail `AI_CMD`
native dispatcher or evaluate concrete battle-state predicates, so it cannot
by itself prove a total score/action ordering.

To reproduce the retail AI-mask candidate sweep after extracting the CROs and
`.code` section, run:

```sh
python3 scripts/audit-retail-ai-mask-writers.py \
  /tmp/usum-retail-battle-ai/code.bin \
  /path/to/extracted-cros \
  --main-text-size 0x4ba000 \
  --json /tmp/usum-ai-mask-writers.json
```

The sweep is intentionally an over-approximation of scalar, double-word, and
register-list stores using the two source-layout displacements `0x4` and
`0x1c`, while tracking local immediate and literal-pool constants. The
`0x4ba000` text bound comes from the retail NCCH ExHeader and excludes the raw
ExeFS `.code` read-only/data tail from the executable sweep. It records candidates,
relocation sites, scalar/double-word/register-list store forms, and a
conservative local register-provenance class for each candidate. It identifies
the three direct source-mapped writers in the retail `.code` (`0x58260`,
`0x582d4`, and `0x59370`). The source-complete verifier then lifts all
aliased/copied writers and PM_DEBUG exclusions. The committed summary of
the full retail run is [`recovered/retail-ai-mask-provenance.json`](../recovered/retail-ai-mask-provenance.json).

The final disposition of the former proof-boundary items is recorded in
[proof-closure.md](proof-closure.md).
The native-state separating example and the closed writer provenance
are in
[`recovered/proof-boundary-separation.json`](../recovered/proof-boundary-separation.json).

Verify the two concrete residual-store provenance examples with:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify-proof-boundary-separation.py \
  /tmp/usum-retail-battle-ai/code.bin \
  /path/to/extracted-cros
```

The verifier checks the exact bytes, proves that `.code:0x45ec` stores a
read-only/data-tail pointer, and resolves `Battle.cro:0x1e80` through its CRO
vtable relocation to RTTI `N4gfl26Effect6ConfigE`. It also confirms that the
candidate instruction itself has no relocation. These checks close the two
formerly unresolved stores; displacement alone is still not treated as a type
proof for unrelated over-approximate rows.

The field-sensitive whole-program theorem is reproduced with the source tree
and the complete extracted CRO set as additional inputs:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify-retail-ai-writer-whole-program.py \
  /tmp/usum-retail-battle-ai/code.bin \
  /path/to/extracted-cros \
  --source-root /path/to/extracted-source \
  --output /tmp/retail-ai-writer-whole-program.json
```

This verifier checks source/project completeness, the exact copied-field
fingerprints at `.code:0x61724`, `Battle.cro:0x8a25c`, and
`Battle.cro:0x8a414`, all 132 CROs, PM_DEBUG exclusions, and the two residual
value/type proofs. Its compact committed result is recorded in
[`recovered/retail-ai-writer-whole-program.json`](../recovered/retail-ai-writer-whole-program.json).

The section-aware pass also leaves one real Thumb same-offset collision at
`.code:0x688`. Verify its surrounding object behavior with:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify-retail-mask-layout-disproof.py \
  /tmp/usum-retail-battle-ai/code.bin
```

This check confirms that the sequence treats offset `0` as a bitfield and
builds a payload at `+0x24` after writing `8` at `+0x1c`; it therefore cannot
be either recovered source-defined `ai_bit` layout. It does not claim that
every unrelated same-displacement store in the stripped retail image has
been assigned a C++ object type.
