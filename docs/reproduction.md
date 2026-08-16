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
