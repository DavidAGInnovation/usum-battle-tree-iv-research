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
| Strong or Expert is monotonically more capable than Basic. | **Strict structural dominance is disproved. Strong score dominance is disproved over the native-contract abstraction; Expert score dominance and both legal-retail-state theorems remain unestablished.** | Let `Q(s)` be the native-command IDs used by script `s`. The structural claim `Q(Basic) ⊆ Q(Strong)` or `Q(Basic) ⊆ Q(Expert)` is false in both cases, with witnesses in each direction. Define `F_s(σ,c,r)` as the returned script score and switch-enable result for legal live state `σ`, candidate `c`, and random trace `r`; the retail theorem would require `∀σ,c,r: F_Strong ≥ F_Basic` (and analogously for Expert). A direct VM run over a native-contract return vector gives Strong `−1` versus Basic `0`, so command contracts alone do not imply Strong dominance. Because the vector has not been realized by one fully instantiated retail object graph, this is a counterexample to the contract abstraction, not yet a counterexample to the narrower `∀`-over-legal-retail-states theorem. No analogous Expert contract witness has been established. |
| The original generated `BattleAi.gaix` bytes can be recovered from the supplied source and ROM. | **Disproved for these inputs; equivalent reconstruction proved.** | The complete archived Git object database has zero `BattleAi.gaix` objects, the source archive has no path with that name, and the retail RomFS has no generated `.gaix` file. The retail GARC, archived project ordering, archiver sort rule, and C++ index switch force the numeric map. The source-compatible header is reconstructed at [`recovered/BattleAi.gaix`](../recovered/BattleAi.gaix). It is logically equivalent, not byte-identical. A runtime `datIdx` trace would be corroboration only, not a remaining numeric-map proof obligation. |
| Every special trainer uses one AI mask in every mode and phase. | **Disproved at source scope.** | The source has explicit alternatives: ordinary `0x107`, Royal `0x125`, special-wild `0x007`, wild Double `0x008`, intrusion `0x040`, reinforcement `0x00f`, and Battle Festival Basic-only reductions. Therefore the universal same-mask statement is false. |
| The source-level mask-writer inventory is complete for every direct, indirect, aliased, and copied writer in the retail binary. | **Not established; the candidate sweep is complete but the alias/data-flow proof is not.** | The source has two layouts: `BSP_TRAINER_DATA::CORE_DATA::ai_bit` at `+0x4` and `MainModule::TRAINER_DATA::ai_bit` at `+0x1c`. On the exact extracted build, `scripts/audit-retail-ai-mask-writers.py` finds 12,498 ARM / 4,336 Thumb `.code` candidates at `+0x4`, 2,286 ARM / 1,125 Thumb `.code` candidates at `+0x1c`, and 7,313 `+0x4` / 2,265 `+0x1c` candidates across the 132 CRO code segments. These are literal-displacement candidates, mostly stack slots or unrelated structures; relocations, function boundaries, aliases, and copied-structure destinations are not resolved, so no candidate can be promoted to (or excluded from) `ai_bit` without a whole-binary data-flow proof. |

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

### Contract-level score counterexample

To separate a real result from an arbitrary callback experiment, define
`F_s^contract` over native return vectors that obey each dispatcher function's
documented return contract, without yet requiring that one retail battle object
graph realize every component simultaneously. The following vector is within
those contracts on the Strong member `10` path:

```text
CHECK_WAZASEQNO=0       GET_CURRENT_WAZANO=1  CHECK_DAMAGE_WAZA=1
COMP_POWER=1            CHECK_MONSNO=1       CHECK_TOKUSEI=1
CHECK_BTL_RULE=0        IF_WAZA_HINSHI=0     CHECK_WAZA_USABLE=0
CHECK_WAZA_AISYOU=0     IF_HAVE_ITEM=0       all other calls on path=0
```

The values have the native meanings `COMP_POWER_NOTOP`, a move/species ID of
`1`, true/false predicates, and otherwise valid zero-valued flags. They satisfy
the individual native return contracts; the tuple is deliberately not claimed
to be a fully correlated retail object graph. Running the exact retail AMX
bodies through the recovered VM with that callback produces:

```text
member 02 (Basic):  score  0
member 10 (Strong): score -1
member 04 (Expert): score  0
```

Therefore `F_Strong^contract >= F_Basic^contract` is false. This closes the
previously unclassified *contract-level* question and proves that the labels
cannot be ordered from the dispatcher contracts alone. It does not silently
promote the result to a retail-state witness: proving or disproving the
narrower theorem still requires either a concrete state construction showing
that this correlated vector is reachable, or a value-complete symbolic model
of the native object graph and random/host semantics.
