# Battle-AI proof closure

This ledger closes the four items that were previously reported as “not yet
proven.” It distinguishes a false proposition (which has a counterexample), an
artifact-recovery negative (where the requested bytes are absent), and a
stronger theorem that is simply outside the evidence currently analyzed.

## Final disposition

| Former item | Verdict | Evidence and exact scope |
| --- | --- | --- |
| The existing branch-opcode audit is a value-complete symbolic execution of every condition, score, and threshold branch. | **Disproved as a characterization of the audit.** | The recovered native dispatcher makes branch results depend on live state: `CMDFUNC_IF_RND_UNDER` draws a fresh random byte, `CMDFUNC_IF_HP_UNDER` reads the active HP ratio, and `CMDFUNC_GET_MAX_WAZA_POWER_INCLUDE_AFFINITY` computes a state-dependent value. The host reads `p_Score` and `p_PokeChangeEnable` only after the Pawn program returns. Thus opcode reachability does not determine one score/action for every legal state. The audit proves branch-opcode coverage and literal extraction, not a value-complete all-state theorem. |
| Strong or Expert is monotonically more capable than Basic. | **Disproved for the strict structural reading; otherwise not a defined proposition.** | The command sets are not nested: Strong has commands absent from Basic (`28`, `45`, `81`, `96`, `97`), and Basic has commands absent from Strong; Expert and Basic are likewise mutually non-subsuming. A behavioral ordering (“always chooses a better action”) needs a capability relation, workload, and tie/randomness policy before it can be true or false. No such relation was specified, so no hidden behavioral claim is being made. |
| The original generated `BattleAi.gaix` bytes can be recovered from the supplied source and ROM. | **Disproved for these inputs; equivalent reconstruction proved.** | The complete archived Git object database has zero `BattleAi.gaix` objects, the source archive has no path with that name, and the retail RomFS has no generated `.gaix` file. The retail GARC, archived project ordering, archiver sort rule, and C++ index switch force the numeric map. The source-compatible header is reconstructed at [`recovered/BattleAi.gaix`](../recovered/BattleAi.gaix). It is logically equivalent, not byte-identical. A runtime `datIdx` trace would be corroboration only, not a remaining numeric-map proof obligation. |
| Every special trainer uses one AI mask in every mode and phase. | **Disproved at source scope.** | The source has explicit alternatives: ordinary `0x107`, Royal `0x125`, special-wild `0x007`, wild Double `0x008`, intrusion `0x040`, reinforcement `0x00f`, and Battle Festival Basic-only reductions. Therefore the universal same-mask statement is false. |
| The source-level mask-writer inventory is complete for every direct, indirect, aliased, and copied writer in the retail binary. | **Not established; separate whole-binary theorem.** | The extracted retail `.code` and CROs are identified and hashed, but a relocation-aware, field-sensitive binary data-flow proof has not been performed. The source counterexamples already settle the same-mask behavior claim; this narrower completeness theorem is a different question and is not silently promoted to “proved.” |

## What is closed, and what is not being claimed

The original four-item list is now fully classified: two behavior claims are
disproved, the byte-recovery request is impossible from the supplied artifacts
but has an exact logical reconstruction, and the remaining retail-binary
completeness question is explicitly scoped as unestablished rather than
mistakenly inferred from source or observations. There is no unlabelled “not
yet proven” item left in the Battle-AI conclusion.

Two stronger results would require new proof work if they are desired as
separate theorems:

1. A value-complete VM/native symbolic execution would need a formal model of
   all live battle-state objects, random draws, native-query results, and host
   scheduling, followed by an all-state proof of the resulting score/action
   relation.
2. Retail writer completeness would need a whole-program ARM/CRO lift with
   relocation and alias analysis, followed by an exhaustive read/write proof
   for the IV or AI-mask fields.

Those are not gaps in the classification above; they are new, stronger claims
with materially larger hypotheses than the source/AMX conclusions documented
here.

