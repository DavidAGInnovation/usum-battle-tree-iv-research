# Reproduction guide

This guide uses paths supplied by the researcher as external inputs. Do not copy the ROM, the extracted executable, or the source archive into this repository.

## Inputs

Set these shell variables to your own files:

```sh
ROM_3DS="/path/to/Pokemon Ultra Sun (USA) Decrypted.3ds"
CODE_BIN="/path/to/extracted/code.bin"
```

The original analysis used the retail image supplied in the research-artifacts directory and an extracted raw `.code` file with SHA-256:

```text
b5388f7500d91be01499a99ca007c98212068608ed7c83c43952e1d5148e9e09
```

Hash your own extracted file before relying on the addresses:

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
s 0x159790; pd 24       # normal trainer-ID IV selection
s 0x1581a8; pd 20       # generic partner branch
s 0x157a1c; pd 24       # ScoutLilie/scouted-partner path
s 0x15faf4; pd 32       # common constructor helper
s 0x158760; pd 180      # special trainer selector constants
```

The same locations as raw offsets are `0x59790`, `0x581a8`, `0x57a1c`, `0x5faf4`, and `0x58760` respectively.

## Source cross-check

For the supplied Momiji snapshot, inspect the following files:

```text
prog/Field/FieldStatic/source/BattleInst/BattleInst.cpp
prog/Field/FieldStatic/source/BattleInst/BattleInstTool.cpp
prog/Field/FieldStatic/include/BattleInst/BattleInstData.h
prog/Savedata/include/BattleInstSave.h
prog/Savedata/source/BattleInstSave.cpp
```

The relevant source functions are `GetPowerRndNormal`, `MakeTrainerPokemon`, `MakePartnerPokemon`, `ScoutLilie`, `CreatePokemon`, `MakeAiPartner`, and `SetVsPokemon`.

## Optional local helper

The repository includes `scripts/inspect-offsets.sh`, which prints the target offsets and, when given a raw `.code` file, invokes radare2 for a compact inspection.
