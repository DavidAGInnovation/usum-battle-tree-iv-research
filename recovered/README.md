# Reconstructed retail-generated headers

`BattleAi.gaix` is a deterministic equivalent reconstruction of the missing
generated archive-index header. Its indices are fixed by three independent
inputs:

- the eleven valid AMX members in retail RomFS `/a/0/8/4`;
- the archived `btl_ai.pprj`/`btl_ai.files` name ordering; and
- the archived `GFArchiver.exe` `name_up` sort rule and version-4 header format.

The original generated file is not present in the supplied source Git object
database, source archive paths, or ROM filesystem, so byte identity cannot be
claimed. The reconstructed header is valid C++ and preserves the identifiers
and numeric values consumed by `btl_AiScript.cpp`.
