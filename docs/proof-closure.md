# Battle-AI proof closure

This ledger closes the four items that were previously reported as “not yet
proven.” It distinguishes a false proposition (which has a counterexample), an
artifact-recovery negative (where the requested bytes are absent), and a
stronger theorem that is outside the evidence currently analyzed. This
iteration also gives the two stronger claims precise definitions, runs the
retail-ROM candidate writer sweep, and executes the retail AMX bodies through
the recovered Pawn VM interface. Those additions narrow the boundary; they do
not turn an over-approximate binary scan or a synthetic native callback into a
universal proof.

## Final disposition

| Former item | Verdict | Evidence and exact scope |
| --- | --- | --- |
| The existing branch-opcode audit is a value-complete symbolic execution of every condition, score, and threshold branch. | **Disproved as a characterization of the audit.** | The recovered native dispatcher makes branch results depend on live state: `CMDFUNC_IF_RND_UNDER` draws a fresh random byte, `CMDFUNC_IF_HP_UNDER` reads the active HP ratio, and `CMDFUNC_GET_MAX_WAZA_POWER_INCLUDE_AFFINITY` computes a state-dependent value. The host reads `p_Score` and `p_PokeChangeEnable` only after the Pawn program returns. Thus opcode reachability does not determine one score/action for every legal state. The audit proves branch-opcode coverage and literal extraction, not a value-complete all-state theorem. |
| Strong or Expert is monotonically more capable than Basic. | **Strict structural dominance is disproved; behavioral score/action dominance is now defined but not established.** | Let `Q(s)` be the native-command IDs used by script `s`. The structural claim `Q(Basic) ⊆ Q(Strong)` or `Q(Basic) ⊆ Q(Expert)` is false in both cases, with witnesses in each direction. For a behavioral theorem, define `F_s(σ,c,r)` as the returned script score and switch-enable result for live state `σ`, candidate `c`, and random trace `r`; score dominance is `∀σ,c,r: F_Strong ≥ F_Basic` (and analogously for Expert). The recovered VM and dispatcher execute the real AMX bodies, but the native callback must still be modeled over all legal `σ`; a synthetic callback is a sanity check, not a behavioral witness. |
| The original generated `BattleAi.gaix` bytes can be recovered from the supplied source and ROM. | **Disproved for these inputs; equivalent reconstruction proved.** | The complete archived Git object database has zero `BattleAi.gaix` objects, the source archive has no path with that name, and the retail RomFS has no generated `.gaix` file. The retail GARC, archived project ordering, archiver sort rule, and C++ index switch force the numeric map. The source-compatible header is reconstructed at [`recovered/BattleAi.gaix`](../recovered/BattleAi.gaix). It is logically equivalent, not byte-identical. A runtime `datIdx` trace would be corroboration only, not a remaining numeric-map proof obligation. |
| Every special trainer uses one AI mask in every mode and phase. | **Disproved at source scope.** | The source has explicit alternatives: ordinary `0x107`, Royal `0x125`, special-wild `0x007`, wild Double `0x008`, intrusion `0x040`, reinforcement `0x00f`, and Battle Festival Basic-only reductions. Therefore the universal same-mask statement is false. |
| The source-level mask-writer inventory is complete for every direct, indirect, aliased, and copied writer in the retail binary. | **Not established; the candidate sweep is complete but the alias/data-flow proof is not.** | The exact retail `.code` and all 132 CROs were extracted and hashed. `scripts/audit-retail-ai-mask-writers.py` enumerates every literal ARM store with displacement `0x1c` in the CRO code segments and both linear ARM/Thumb over-approximations of `.code`: 2,286 ARM and 1,125 Thumb `.code` candidates, plus 2,265 CRO ARM candidates. Most are stack slots or unrelated structures; the Battle CRO alone has ten. Relocations, function boundaries, aliases, and copied-structure destinations are not resolved by a displacement scan, so no candidate can be promoted to (or excluded from) `ai_bit` without a whole-binary data-flow proof. |

## What is closed, and what is not being claimed

The original four-item list is now fully classified: two behavior claims are
disproved, the byte-recovery request is impossible from the supplied artifacts
but has an exact logical reconstruction, and the remaining retail-binary
completeness question is explicitly scoped as unestablished rather than
mistakenly inferred from source or observations. The former “undefined”
behavioral comparison is no longer undefined: it is a quantified score/action
relation with a stated state space and tie policy. It is simply not proved by
the present artifacts.

Two stronger results would require new proof work if they are desired as
separate theorems:

1. A value-complete VM/native symbolic execution would need a formal model of
   all live battle-state objects, random draws, native-query results, and host
   scheduling, followed by an all-state proof of the resulting score/action
   relation. The recovered VM was exercised directly: Basic member `02`,
   Strong `10`, and Expert `04` all execute successfully, and changing the
   synthetic native-return model changes their scores. This validates the
   execution path, but it is not a legal-state counterexample or an all-state
   proof.
2. Retail writer completeness would need a whole-program ARM/CRO lift with
   relocation and alias analysis, followed by an exhaustive read/write proof
   for the AI-mask field. The new displacement scan is deliberately recorded
   as a candidate inventory, not as that proof.

## Formal behavioral relation and the remaining evidence boundary

The word “capable” is not a machine-level predicate, so the proof must name
the relation being claimed. The structural relation is:

```text
s1 >=struct s0  iff  Q(s0) is a subset of Q(s1)
```

where `Q(s)` is the set of native `AI_CMD` IDs called by script `s`. This is
decidable from the extracted AMX programs and is false for both Strong versus
Basic and Expert versus Basic because the sets are mutually non-subsuming.

For a behavioral statement, let `σ` range over legal live battle states, `c`
over legal move/target or reserve candidates, and `r` over legal random
traces. Let `F_s(σ,c,r)` return the script's score and switch-enable output.
The corresponding score-dominance theorem is:

```text
s1 >=score s0  iff  for every (σ,c,r), F_s1(σ,c,r) >= F_s0(σ,c,r)
```

An action-dominance theorem additionally needs a utility function over actions
and the engine's tie/randomness policy. The C++ judges show that each enabled
script score is accumulated and that equal best candidates are randomized, so
“always chooses a better action” cannot be evaluated without those hypotheses.

The supplied source gives the native command semantics and the retail AMX
bytes, and the standard Pawn VM now runs the extracted members. It does not
provide a finite, executable definition of every legal `σ` (including object
graphs and cross-command correlations), nor has a relocation-aware writer
proof been completed. Those are the only remaining obligations for the two
stronger, explicitly quantified theorems; they are not silently claimed by
the source-level conclusions.

Those are not gaps in the classification above; they are new, stronger claims
with materially larger hypotheses than the source/AMX conclusions documented
here.
