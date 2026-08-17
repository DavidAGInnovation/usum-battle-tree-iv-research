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
| The existing branch-opcode audit is a value-complete symbolic execution of every condition, score, and threshold branch. | **Disproved as a characterization of the audit; the stronger all-state theorem remains unproved.** | The recovered native dispatcher makes branch results depend on live state: `CMDFUNC_IF_RND_UNDER` draws a fresh random byte, `CMDFUNC_IF_HP_UNDER` reads the active HP ratio, and `CMDFUNC_GET_MAX_WAZA_POWER_INCLUDE_AFFINITY` computes a state-dependent value. The host reads `p_Score` and `p_PokeChangeEnable` only after the Pawn program returns. The exact retail VM now executes the extracted members and validates both score counterexamples (runtime identities are in [`recovered/ai-score-witnesses.json`](../recovered/ai-score-witnesses.json)), but concrete traces do not quantify over every native-state valuation. Opcode reachability and selected concrete paths are proven; a value-complete all-state symbolic theorem is not. |
| Strong or Expert is monotonically more capable than Basic. | **Disproved for score dominance over legal retail states; strict structural dominance is also disproved.** | Let `Q(s)` be the native-command IDs used by script `s`. The structural claim `Q(Basic) ⊆ Q(Strong)` or `Q(Basic) ⊆ Q(Expert)` is false in both cases. Define `F_s(σ,c,r)` as the returned script score and switch-enable result for legal live state `σ`, candidate `c`, and random trace `r`; the universal score theorem would require `∀σ,c,r: F_Strong ≥ F_Basic` (and analogously for Expert). The ROM-derived Ninjask records and exact AMX VM runs in [`recovered/ai-score-witnesses.json`](../recovered/ai-score-witnesses.json) provide legal witnesses with Basic `0` and Strong `−1`, and Basic `0` and Expert `−1`. Therefore both universal score-dominance claims are false. An action-dominance claim remains a separate relation because it additionally requires a utility function and the judge's tie/randomness policy. |
| The original generated `BattleAi.gaix` bytes can be recovered from the supplied source and ROM. | **Disproved for these inputs; equivalent reconstruction proved.** | The complete archived Git object database has zero `BattleAi.gaix` objects, the source archive has no path with that name, and the retail RomFS has no generated `.gaix` file. The retail GARC, archived project ordering, archiver sort rule, and C++ index switch force the numeric map. The source-compatible header is reconstructed at [`recovered/BattleAi.gaix`](../recovered/BattleAi.gaix). It is logically equivalent, not byte-identical. A runtime `datIdx` trace would be corroboration only, not a remaining numeric-map proof obligation. |
| Every special trainer uses one AI mask in every mode and phase. | **Disproved at source scope.** | The source has explicit alternatives: ordinary `0x107`, Royal setup `0x127` with an effective Royal selector `0x125`, special-wild `0x007`, wild Double `0x008`, intrusion `0x040`, reinforcement `0x00f`, and Battle Festival Basic-only reductions. Therefore the universal same-mask statement is false. |
| The source-level mask-writer inventory is complete for every direct, indirect, aliased, and copied writer in the retail binary. | **Direct source-mapped writers are now confirmed; complete aliased/copied coverage remains unproved.** | The section-aware scanner uses the retail ExHeader text boundary `0x4ba000` and recognizes scalar, double-word, and register-list stores while tracking immediate constants. It finds 67,645 total executable-region candidates: 25,604 ARM and 19,703 Thumb `.code` candidates plus 22,338 ARM candidates across the 132 CRO code segments. It identifies three high-confidence direct writers in the retail `.code`: `0x58260` (`stm r5,{r4,r7}`) and `0x582d4` (`str r7,[r5,#4]`) write `0x107`/`0x10f` at `+0x4` on the two `BattleInst::SetVsTrainer`/`SetAiBit` branches; `0x59370` (`str r1,[r2,#4]`) writes literal `0x127`, matching `SetVsTrainerRoyal`. The scan has 325 mask-valued candidates in total (321 immediate, 2 literal-pool, and 2 computed); those values are dominated by same-offset `0x7/0x8/0xf` collisions, so only the three `0x10f`/`0x127` stores are source-mapped. The CRO tables contain 101,802 `R_ARM_ABS32` records, 58,255 executable targets, and zero malformed entries. The expanded pass still leaves 42,193 candidates with unknown base provenance; the other non-mapped rows have only local register/constant classifications, not C++ object identity. It cannot resolve interprocedural aliases, copied structs, or stripped-main-code relocations (full summary: [`recovered/retail-ai-mask-provenance.json`](../recovered/retail-ai-mask-provenance.json)); complete writer coverage therefore remains unproved. |

After applying the ExHeader text boundary, only two Thumb-sweep mask constants
remain. One (`0x3d3600`) lies inside an ARM function reached by ARM
branches/calls, so its Thumb decode is not a Thumb writer. The remaining
`0x688` instruction is real Thumb code, but its surrounding sequence ORs `0x20`
into offset `0`, writes `8` at `+0x1c`, and then consumes a separate `+0x24`
payload. This is incompatible with both source layouts: `TRAINER_DATA` has a
pointer at `+0x0`, while `CORE_DATA` has `tr_id` at `+0x0` and `ai_bit` at
`+0x4`. Thus `0x688` is disproved as either source-defined `ai_bit` writer.
The remaining ARM mask-valued candidate is a stack temporary. These are
source-layout disproofs, not a universal retail type proof: an unrelated
retail object can still use the same displacement until object provenance is
recovered.

The source inventory also identifies three `MainModule` writers at `+0x1c`:
aggregate initialization in `trainerParam_Init`, zeroing in
`trainerParam_StoreCore`, and the `BSP_TRAINER_DATA::GetAIBit()` copy in
`trainerParam_StoreNPCTrainer`. Their retail instructions are not uniquely
mapped yet because the same displacement occurs throughout unrelated object
layouts; they are recorded explicitly in the provenance artifact rather than
silently treated as absent.

## What is closed, and what is not being claimed

The original four-item list is now fully classified: two behavior claims are
disproved, the byte-recovery request is impossible from the supplied artifacts
but has an exact logical reconstruction, and the remaining retail-binary
completeness question is explicitly scoped as unestablished rather than
mistakenly inferred from source or observations. The former “undefined”
behavioral comparison is no longer undefined: it is a quantified score/action
relation with a stated state space and tie policy. It is simply not proved by
the present artifacts.

### Constructive separation of the residual obligations

The two residual caveats are not merely missing documentation. They have
reproducible separating examples in
[`recovered/proof-boundary-separation.json`](../recovered/proof-boundary-separation.json).
The same Strong AMX bytes execute successfully under two native models that
obey the documented callback interface: an all-zero model returns score `0`,
while the legal Ninjask witness returns `−1`. Thus the program and VM do not
determine a score until the native battle-state model is supplied; observing a
finite set of paths cannot quantify over the missing state space.

The binary ambiguity is equally concrete. The expanded pass now confirms the
three direct source-mapped writers at `.code:0x58260`, `.code:0x582d4`, and
`.code:0x59370`, but in
the same image `0x45ec` is `str r0, [r4, #4]` after `r4` receives a function
return. In `Battle.cro`, code offset `0x1e80` is `str r1, [r0, #4]` with an
incoming argument. Neither ambiguous store is a relocation patch site. Each
is compatible with an `ai_bit` write and with an unrelated field at the same
displacement. Without object/type provenance, the confirmed direct subset
cannot be promoted to a complete writer set.

Two stronger results would require new proof work if they are desired as
separate theorems:

1. A value-complete VM/native symbolic execution would still be needed to
   enumerate every score/threshold branch and prove a positive theorem about
   all states. The exact retail VM now validates the ROM-derived legal
   Basic/Strong and Basic/Expert paths (each gives `0` versus `−1`), so it is
   no longer needed to classify the two monotonicity claims. The witness
   disproves each universal score-dominance theorem, while the broader
   branch-complete execution audit remains a separate descriptive task.
2. Retail writer completeness would need a whole-program ARM/CRO lift with
   relocation and alias analysis, followed by an exhaustive read/write proof
   for the AI-mask field. The scanner now records local register provenance
   and parses CRO relocations, but the stripped main `.code` has no CRO/CRS
   relocation table. The missing interprocedural register/object data flow is
   not directly present as metadata; it can still be reconstructed by a
   complete binary lift, source-to-binary matching, or runtime instrumentation.

The ROM and source are therefore sufficient inputs in principle, but they are
not a shortcut to the theorem. The ROM supplies code bytes and some runtime
type-name strings; the source supplies the candidate layouts and writer
semantics. Closing the theorem still requires recovering function boundaries,
following ARM/Thumb calls and aliases across the whole image, mapping every
candidate pointer to an object type, and validating the result against the
retail runtime or a reproducible unstripped build.

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
bytes, and the standard Pawn VM now runs the extracted members. The legal
witnesses below settle the sign of the two score relations, but the source
still does not provide a finite, executable definition of every legal `σ`
(including every object graph and cross-command correlation). That broader
value-complete execution theorem, and the independent writer-completeness
theorem, remain outside the evidence.

The positive all-state branch theorem and the retail write-set completeness
theorem remain unproved. They are distinct from the now-disproved score
dominance claims and from the relocation inventory: a counterexample closes a
universal ordering claim, but it does not symbolically enumerate every other
reachable path or prove that no aliased writer exists.

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
cannot be ordered from the dispatcher contracts alone. The stronger legal-state
result is recorded next.

### Legal retail-state score counterexamples

The contract result is no longer the strongest evidence. The ROM itself gives
species 291 (Ninjask), its type pair and ability 3, the level-up record that
contains moves 210, 14, and 404, and the move records that supply their AI
sequence and damage-type values. The item archive contains item record 287.
Those records let one instantiate the queried native values with a legal
object graph rather than independent synthetic answers. The complete vectors
and the exact VM output are preserved in
[`recovered/ai-score-witnesses.json`](../recovered/ai-score-witnesses.json).

For Strong, use two Ninjask, a single battle, Fury Cutter (move 210, sequence
119) as the current usable move, and X-Scissor (move 404) as the stronger
available move. Give the active Pokémon no item, full HP, neutral/no status
state, and no stat boosts. The exact retail members return Basic `0` and
Strong `−1`.

For Expert, use two Ninjask in a single battle with Swords Dance (move 14,
sequence 50) as the current usable move, item 287 on the AI Pokémon, full HP,
no status/side effect, and zero stat ranks. Choose the legal random trace whose
draw is `0`; Expert's first `IF_RND_UNDER(220)` is true. The exact members
return Basic `0` and Expert `−1`.

Each listed native result is either read directly from the ROM record or is a
legal predicate outcome of that state (for example, full HP makes the 40/70 HP
tests false, no item makes the Strong item comparison false, and item 287 makes
the Expert comparison true). These are reachable-state counterexamples to
`F_Strong >=score F_Basic` and `F_Expert >=score F_Basic`; a positive
all-state score theorem is therefore disproved, not merely left untested.
