# USUM Battle AI score-rule index

> This is a derived condition-to-score index for the active USUM Battle Tree programs. It is generated from the normalized source-level specification; the retail-only Intrude and Royal bytecode listings remain in [battle-ai-full-spec.md](battle-ai-full-spec.md).

## How to read this document

For a move/target candidate, the C++ judge starts at `100`. Each enabled Pawn program starts its own `p_Score` at `0`, evaluates native `AI_CMD` predicates, and applies the `SCORE +=` writes shown below. The returned script scores are added together. A condition that is not met contributes nothing; multiple writes can accumulate unless the function returns first.
Names such as `BaciAI_Seq_011()` are AI/move-sequence identifiers selected by the dispatcher; they are not move names. The complete specification shows which dispatcher cases call each sequence function and preserves the native enum names when their exact semantic expansion is not established.

The table's `What it does` column is a plain-language translation of each reachable rule: it names the trigger, the battle conditions, the score adjustment, and any immediate return or branch-order behavior. The entries also show complete normalized function bodies, not only the final score line. Therefore the `if`, `else`, `switch`, random threshold, and early-return conditions surrounding every source-level score write remain available as authoritative evidence. Helper functions called by a dispatcher are listed separately, so the caller's move-sequence selection must also be followed.

## Influence-closure definition

For each active script, this index starts at `main` and follows every recovered local function call. It therefore includes every entry point, dispatcher, caller, and predicate/helper reachable during that script's evaluation. Functions are classified as direct score writers, indirect callers/helpers on a score path, or reachable dispatcher/predicate support. Pokechange predicates are included even when they do not call the score helper themselves, because their boolean return values gate the call to `PokeChangeOK(20)`.

The local-call graph is conservative: it records which functions are referenced, while the exact bodies below determine which branch and return value actually controls a score write. Expert has 17 source functions that are not reachable from `main`; they remain documented in the full specification but are not presented as active score-influence functions here.

## Retail adjustment inventory

| Program | Retail score-delta constants observed |
|---|---|
| Basic | −20, −12, −10, −8, −6, −5, −1 |
| Strong | −3, −1, +2, +3, +4, +5 |
| Expert | −12, −10, −8, −7, −5, −4, −3, −2, −1, +1, +2, +3, +4 |
| Double | −30, −20, −12, −11, −10, −8, −7, −5, −4, −3, −2, −1, +1, +2, +3, +4, +5, +8, +20 |
| Pokechange | computed reserve score; see the exact formula below |

The retail inventory is the set of constants observed in the extracted US AMX members. The source listings below provide the conditions for the recovered source programs. A few retail members contain inlined or computed score expressions whose bytecode constants are broader than the direct source-literal inventory; those exact retail listings are retained in the full specification rather than silently re-labelled as source rules.

## Pokechange score formula

Switching is different from move scoring. One of seven switch reasons can call `PokeChangeOK(20)`, which enables switching and adds:

```text
SwitchScriptScore = 20
                    − 10  if the trainer is a scenario trainer and the bench can Mega Evolve
                    + 2   if maximum effective bench power is at least 160
                    + 3   if maximum effective bench power is at least 200
                    + 4   if maximum effective bench power is at least 240
```

The seven enabling reasons are: the last turn of Perish Song; a reserve that can break Wonder Guard; a reserve that improves a zero-effect matchup; escaping a bad Choice-locked matchup; exploiting an ability that nullifies the previous damage move; curing sleep or freeze through Natural Cure; and improving the matchup after the previous damage move. The exact guards are included in the Pokechange functions below. Only the first successful reason is used because the main procedure returns immediately.

## Basic: exact guarded score rules

| Function | Source lines | Influence role | What it does | Direct score writes | Calls |
|---|---:|---|---|---|---|
| `main()` | 7–16 | indirect caller/helper on a score path | Trigger: every Basic evaluation. It records the current move's AI sequence identifier and then enters the Basic decision procedure. | indirect/dynamic | main_proc |
| `main_proc()` | 18–61 | indirect caller/helper on a score path | Trigger: every move candidate reaching Basic. In Double or Triple Battles, the procedure skips a candidate when its selected target is an ally. It then checks powder immunities first; if one handles the move, the procedure stops. Otherwise it classifies the move as damaging, including the two one-hit-KO moves Fissure and Horn Drill, runs the damaging-move immunity checks when appropriate, and finally runs the selected general move-sequence rules. | indirect/dynamic | Basic_ConaHoushi, Calc_BasicAll, Calc_BasicDamage |
| `Basic_ConaHoushi()` | 63–94 | direct score writer | Trigger: called before the other Basic checks for the current move. If the move is Stun Spore, Sleep Powder, Poison Powder, Rage Powder, Spore, or Powder and the defender has Overcoat, the move is penalized by 10 points unless the attacker has Mold Breaker, Teravolt, or Turboblaze. If that first penalty is applied, the helper returns immediately. Otherwise, if the defender is Grass-type, it subtracts 10 points and returns. If neither condition applies, it returns without changing the score. | -10 | — |
| `Calc_BasicDamage()` | 99–153 | direct score writer | Trigger: called for a damaging move before the general Basic sequence checks. If the move has no effect against the defender, it subtracts 10 points and stops this damage evaluation. The exception is a Ground-type move against Levitate when the attacker has Mold Breaker, Teravolt, or Turboblaze; that immunity is treated as bypassed, so the initial penalty is skipped. If the attacker has any of those three ability-bypassing abilities, the helper then skips the listed defensive-ability checks. Otherwise it dispatches to the matching ability helper: Volt Absorb, Motor Drive, or Lightning Rod checks Electric moves; Water Absorb, Storm Drain, or Dry Skin checks Water moves; Flash Fire checks Fire moves; Wonder Guard checks whether the move is at least super-effective; Levitate checks Ground moves unless Gravity is active; and Sap Sipper checks Grass moves. If a helper handles the move, this function returns immediately; otherwise the caller continues to the general Basic rules. | -10 | BasicDmg_00_1, BasicDmg_00_2, BasicDmg_00_3, BasicDmg_00_4, BasicDmg_00_5, BasicDmg_00_7 |
| `BasicDmg_00_1()` | 156–164 | direct score writer | Trigger: called when the defender's ability is Volt Absorb, Motor Drive, or Lightning Rod. Condition: the current move is Electric-type. Effect: subtracts 12 points and reports the move as handled; for any other move type it makes no score change and reports that it did not handle it. | -12 | — |
| `BasicDmg_00_2()` | 166–175 | direct score writer | Trigger: called when the defender's ability is Water Absorb, Storm Drain, or Dry Skin. Condition: the current move is Water-type. Effect: subtracts 12 points and reports the move as handled; for any other move type it makes no score change and reports that it did not handle it. | -12 | — |
| `BasicDmg_00_3()` | 177–185 | direct score writer | Trigger: called when the defender has Flash Fire. Condition: the current move is Fire-type. Effect: subtracts 12 points and reports the move as handled; for any other move type it makes no score change and reports that it did not handle it. | -12 | — |
| `BasicDmg_00_4()` | 187–198 | direct score writer | Trigger: called when the defender has Wonder Guard. If the current move is 2× effective or 4× effective, it makes no score change and reports that it did not handle the move. Otherwise it subtracts 10 points and reports the move as handled. | -10 | — |
| `BasicDmg_00_5()` | 200–211 | direct score writer | Trigger: called when the defender has Levitate. Condition: the current move is Ground-type and Gravity is not active. Effect: subtracts 10 points and reports the move as handled. Ground moves are not penalized when Gravity is active, and other move types are not handled. | -10 | — |
| `BasicDmg_00_7()` | 213–221 | direct score writer | Trigger: called when the defender has Sap Sipper. Condition: the current move is Grass-type. Effect: subtracts 12 points and reports the move as handled; other move types are not handled. | -12 | — |
| `Calc_BasicAll()` | 227–423 | indirect caller/helper on a score path | Trigger: the damaging-move checks did not terminate Basic evaluation. It checks Soundproof first and stops if that helper handles the move; then it checks Bulletproof and stops if that helper handles the move. If neither applies, it selects the general rule set associated with the current move's AI sequence identifier. | indirect/dynamic | BaciAI_Seq_001, BaciAI_Seq_007, BaciAI_Seq_008, BaciAI_Seq_010, BaciAI_Seq_011, BaciAI_Seq_012, BaciAI_Seq_013, BaciAI_Seq_014, BaciAI_Seq_015, BaciAI_Seq_016, BaciAI_Seq_018, BaciAI_Seq_019, BaciAI_Seq_020, BaciAI_Seq_021, BaciAI_Seq_022, BaciAI_Seq_023, BaciAI_Seq_024, BaciAI_Seq_025, BaciAI_Seq_028, BaciAI_Seq_032, BaciAI_Seq_033, BaciAI_Seq_035, BaciAI_Seq_037, BaciAI_Seq_038, BaciAI_Seq_046, BaciAI_Seq_047, BaciAI_Seq_049, BaciAI_Seq_065, BaciAI_Seq_067, BaciAI_Seq_079, BaciAI_Seq_084, BaciAI_Seq_086, BaciAI_Seq_090, BaciAI_Seq_092, BaciAI_Seq_094, BaciAI_Seq_102, BaciAI_Seq_106, BaciAI_Seq_107, BaciAI_Seq_109, BaciAI_Seq_112, BaciAI_Seq_113, BaciAI_Seq_114, BaciAI_Seq_115, BaciAI_Seq_120, BaciAI_Seq_124, BaciAI_Seq_127, BaciAI_Seq_132, BaciAI_Seq_136, BaciAI_Seq_137, BaciAI_Seq_142, BaciAI_Seq_148, BaciAI_Seq_158, BaciAI_Seq_160, BaciAI_Seq_161, BaciAI_Seq_164, BaciAI_Seq_165, BaciAI_Seq_167, BaciAI_Seq_168, BaciAI_Seq_172, BaciAI_Seq_175, BaciAI_Seq_176, BaciAI_Seq_177, BaciAI_Seq_178, BaciAI_Seq_179, BaciAI_Seq_181, BaciAI_Seq_184, BaciAI_Seq_188, BaciAI_Seq_191, BaciAI_Seq_192, BaciAI_Seq_193, BaciAI_Seq_201, BaciAI_Seq_205, BaciAI_Seq_206, BaciAI_Seq_208, BaciAI_Seq_210, BaciAI_Seq_211, BaciAI_Seq_212, BaciAI_Seq_215, BaciAI_Seq_216, BaciAI_Seq_220, BaciAI_Seq_222, BaciAI_Seq_225, BaciAI_Seq_226, BaciAI_Seq_227, BaciAI_Seq_232, BaciAI_Seq_233, BaciAI_Seq_234, BaciAI_Seq_236, BaciAI_Seq_238, BaciAI_Seq_239, BaciAI_Seq_240, BaciAI_Seq_241, BaciAI_Seq_242, BaciAI_Seq_243, BaciAI_Seq_244, BaciAI_Seq_246, BaciAI_Seq_247, BaciAI_Seq_249, BaciAI_Seq_251, BaciAI_Seq_252, BaciAI_Seq_258, BaciAI_Seq_259, BaciAI_Seq_265, BaciAI_Seq_266, BaciAI_Seq_270, BaciAI_Seq_278, BaciAI_Seq_281, BaciAI_Seq_285, BaciAI_Seq_286, BaciAI_Seq_292, BaciAI_Seq_294, BaciAI_Seq_298, BaciAI_Seq_299, BaciAI_Seq_300, BaciAI_Seq_301, BaciAI_Seq_307, BaciAI_Seq_309, BaciAI_Seq_311, BaciAI_Seq_315, BaciAI_Seq_318, BaciAI_Seq_320, BaciAI_Seq_323, BaciAI_Seq_338, BaciAI_Seq_339, BaciAI_Seq_340, BaciAI_Seq_342, BaciAI_Seq_349, BaciAI_Seq_350, BaciAI_Seq_351, BaciAI_Seq_352, BaciAI_Seq_354, BaciAI_Seq_362, BaciAI_Seq_363, BaciAI_Seq_366, BaciAI_Seq_368, BaciAI_Seq_370, BaciAI_Seq_375, Boudan_Check, Bouon_Check |
| `Bouon_Check()` | 426–462 | direct score writer | Trigger: checked before the selected Basic move-sequence evaluator. If the defender has Soundproof, the attacker does not have Mold Breaker, Teravolt, or Turboblaze, and the current move is one of the sound-based moves in the source list, subtracts 10 points and reports the move as handled. Otherwise it leaves the score unchanged. | -10 | — |
| `Boudan_Check()` | 465–502 | direct score writer | Trigger: checked after the sound-move check and before the selected Basic move-sequence evaluator. If the defender has Bulletproof, the attacker does not have Mold Breaker, Teravolt, or Turboblaze, and the current move is one of the ball- or bomb-based moves in the source list, subtracts 10 points and reports the move as handled. Otherwise it leaves the score unchanged. | -10 | — |
| `BaciAI_Seq_001()` | 505–593 | direct score writer | Trigger: the Basic dispatcher selects move sequence 001. Rule 1: when the defending Pokémon has a status condition, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: when the side belonging to the defending Pokémon has Safeguard, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 4: when the field has Electric Terrain and all of the following are true: the defending Pokémon's ability is not Levitate; the defending Pokémon's first type is not Flying; the defending Pokémon's second type is not Flying, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 5: when the field has Misty Terrain and all of the following are true: the defending Pokémon's ability is not Levitate; the defending Pokémon's first type is not Flying; the defending Pokémon's second type is not Flying, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 6: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the defending Pokémon's ability is Insomnia; the defending Pokémon's ability is Vital Spirit; the defending Pokémon's ability is Magic Bounce, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 7: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and the defending Pokémon's ability is Flower Veil, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 8: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Flower Veil, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 9: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and the defending Pokémon's ability is Sweet Veil, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 10: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Sweet Veil, the AI subtracts 10 points from the move's score. The function then returns immediately. Within an if/else chain, only the first matching branch is reached. | -10 | — |
| `BaciAI_Seq_007()` | 596–626 | direct score writer | Trigger: the Basic dispatcher selects move sequence 007. Rule 1: when the current move has no effect against the target, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: when the attacking Pokémon's ability is not Mold Breaker and the defending Pokémon's ability is Damp, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when the battle format is Single Battles and the attacking Pokémon's usable reserve count is zero and the defending Pokémon's usable reserve count is not zero, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 4: when the battle format is Single Battles and the attacking Pokémon's usable reserve count is zero and the preceding branch in this if/else chain did not match, the AI subtracts 1 point from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -1 | — |
| `BaciAI_Seq_008()` | 629–644 | direct score writer | Trigger: the Basic dispatcher selects move sequence 008. Rule 1: when the defending Pokémon is not affected by Sleep, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: when the defending Pokémon's ability is Magic Guard, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_010()` | 647–661 | direct score writer | Trigger: the Basic dispatcher selects move sequence 010. Rule 1: when the attacking Pokémon's ability is Contrary, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 2: when the attacking Pokémon's Attack parameter is exactly 12 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -12, -10 | — |
| `BaciAI_Seq_011()` | 663–677 | direct score writer | Trigger: the Basic dispatcher selects move sequence 011. Rule 1: when the attacking Pokémon's ability is Contrary, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 2: when the attacking Pokémon's Defense parameter is exactly 12 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -12, -10 | — |
| `BaciAI_Seq_012()` | 679–700 | direct score writer | Trigger: the Basic dispatcher selects move sequence 012. Rule 1: when the attacking Pokémon's ability is Contrary, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 2: when the attacking Pokémon's Speed parameter is exactly 12 in the native AI value scale, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when the field has Trick Room, the AI subtracts 5 points from the move's score. Evaluation continues after this adjustment. | -12, -10, -5 | — |
| `BaciAI_Seq_013()` | 702–716 | direct score writer | Trigger: the Basic dispatcher selects move sequence 013. Rule 1: when the attacking Pokémon's ability is Contrary, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 2: when the attacking Pokémon's Special Attack parameter is exactly 12 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -12, -10 | — |
| `BaciAI_Seq_014()` | 718–732 | direct score writer | Trigger: the Basic dispatcher selects move sequence 014. Rule 1: when the attacking Pokémon's ability is Contrary, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 2: when the attacking Pokémon's Special Defense parameter is exactly 12 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -12, -10 | — |
| `BaciAI_Seq_015()` | 734–762 | direct score writer | Trigger: the Basic dispatcher selects move sequence 015. Rule 1: when the attacking Pokémon's ability is Contrary, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 2: when the defending Pokémon's ability is No Guard, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when the attacking Pokémon's ability is No Guard, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 4: when the attacking Pokémon's accuracy parameter is exactly 12 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -12, -10 | — |
| `BaciAI_Seq_016()` | 764–792 | direct score writer | Trigger: the Basic dispatcher selects move sequence 016. Rule 1: when the attacking Pokémon's ability is Contrary, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 2: when the defending Pokémon's ability is No Guard, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when the attacking Pokémon's ability is No Guard, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 4: when the attacking Pokémon's evasion parameter is exactly 12 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -12, -10 | — |
| `BaciAI_Seq_018()` | 794–856 | direct score writer | Trigger: the Basic dispatcher selects move sequence 018. Rule 1: when the defending Pokémon's Attack parameter is exactly 0 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when at least one of the following is true: the attacking Pokémon's ability is Defiant; the attacking Pokémon's ability is Competitive, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 4: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the defending Pokémon's ability is Hyper Cutter; the defending Pokémon's ability is Clear Body; the defending Pokémon's ability is White Smoke, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 5: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's ability is Contrary; the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 6: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and the defending Pokémon's ability is Flower Veil, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 7: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Flower Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -12 | — |
| `BaciAI_Seq_019()` | 858–920 | direct score writer | Trigger: the Basic dispatcher selects move sequence 019. Rule 1: when the attacking Pokémon's Defense parameter is exactly 0 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when at least one of the following is true: the attacking Pokémon's ability is Defiant; the attacking Pokémon's ability is Competitive, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 4: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the defending Pokémon's ability is Big Pecks; the defending Pokémon's ability is Clear Body; the defending Pokémon's ability is White Smoke, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 5: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's ability is Contrary; the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 6: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and the defending Pokémon's ability is Flower Veil, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 7: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Flower Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -12 | — |
| `BaciAI_Seq_020()` | 922–983 | direct score writer | Trigger: the Basic dispatcher selects move sequence 020. Rule 1: when the attacking Pokémon's Speed parameter is exactly 0 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when at least one of the following is true: the attacking Pokémon's ability is Defiant; the attacking Pokémon's ability is Competitive, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 4: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the defending Pokémon's ability is Clear Body; the defending Pokémon's ability is White Smoke, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 5: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's ability is Contrary; the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 6: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and the defending Pokémon's ability is Flower Veil, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 7: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Flower Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -8, -12 | — |
| `BaciAI_Seq_021()` | 985–1046 | direct score writer | Trigger: the Basic dispatcher selects move sequence 021. Rule 1: when the attacking Pokémon's Special Attack parameter is exactly 0 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when at least one of the following is true: the attacking Pokémon's ability is Defiant; the attacking Pokémon's ability is Competitive, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 4: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the defending Pokémon's ability is Clear Body; the defending Pokémon's ability is White Smoke, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 5: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's ability is Contrary; the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 6: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and the defending Pokémon's ability is Flower Veil, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 7: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Flower Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -8, -12 | — |
| `BaciAI_Seq_022()` | 1048–1109 | direct score writer | Trigger: the Basic dispatcher selects move sequence 022. Rule 1: when the attacking Pokémon's Special Defense parameter is exactly 0 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when at least one of the following is true: the attacking Pokémon's ability is Defiant; the attacking Pokémon's ability is Competitive, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 4: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the defending Pokémon's ability is Clear Body; the defending Pokémon's ability is White Smoke, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 5: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's ability is Contrary; the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 6: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and the defending Pokémon's ability is Flower Veil, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 7: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Flower Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -8, -12 | — |
| `BaciAI_Seq_023()` | 1111–1178 | direct score writer | Trigger: the Basic dispatcher selects move sequence 023. Rule 1: when the attacking Pokémon's accuracy parameter is exactly 0 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when at least one of the following is true: the defending Pokémon's ability is Defiant; the defending Pokémon's ability is Competitive, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's ability is No Guard; the attacking Pokémon's ability is No Guard, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 4: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 5: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the defending Pokémon's ability is Clear Body; the defending Pokémon's ability is White Smoke; the defending Pokémon's ability is Shield Dust, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 6: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's ability is Contrary; the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 7: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and the defending Pokémon's ability is Flower Veil, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 8: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Flower Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -8, -12 | — |
| `BaciAI_Seq_024()` | 1180–1246 | direct score writer | Trigger: the Basic dispatcher selects move sequence 024. Rule 1: when the defending Pokémon's evasion parameter is exactly 0 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when at least one of the following is true: the defending Pokémon's ability is Defiant; the defending Pokémon's ability is Competitive, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's ability is No Guard; the attacking Pokémon's ability is No Guard, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 4: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 5: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the defending Pokémon's ability is Clear Body; the defending Pokémon's ability is White Smoke, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 6: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's ability is Contrary; the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 7: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and the defending Pokémon's ability is Flower Veil, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 8: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Flower Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -8, -12 | — |
| `BaciAI_Seq_025()` | 1248–1308 | direct score writer | Trigger: the Basic dispatcher selects move sequence 025. Rule 1: when the attacking Pokémon's Attack parameter is above 6 in the native AI value scale, the AI subtracts 6 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and the attacking Pokémon's Defense parameter is above 6 in the native AI value scale, the AI subtracts 6 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and the attacking Pokémon's Special Attack parameter is above 6 in the native AI value scale, the AI subtracts 6 points from the move's score. Evaluation continues after this adjustment. Rule 4: when the preceding branch in this if/else chain did not match, and the attacking Pokémon's Special Defense parameter is above 6 in the native AI value scale, the AI subtracts 6 points from the move's score. Evaluation continues after this adjustment. Rule 5: when the preceding branch in this if/else chain did not match, and the attacking Pokémon's Speed parameter is above 6 in the native AI value scale, the AI subtracts 6 points from the move's score. Evaluation continues after this adjustment. Rule 6: when the preceding branch in this if/else chain did not match, and the attacking Pokémon's accuracy parameter is above 6 in the native AI value scale, the AI subtracts 6 points from the move's score. Evaluation continues after this adjustment. Rule 7: when the preceding branch in this if/else chain did not match, and the attacking Pokémon's evasion parameter is above 6 in the native AI value scale, the AI subtracts 6 points from the move's score. Evaluation continues after this adjustment. Rule 8: when the preceding branch in this if/else chain did not match, and the defending Pokémon's Attack parameter is below 6 in the native AI value scale, the AI subtracts 6 points from the move's score. Evaluation continues after this adjustment. Rule 9: when the preceding branch in this if/else chain did not match, and the defending Pokémon's Defense parameter is below 6 in the native AI value scale, the AI subtracts 6 points from the move's score. Evaluation continues after this adjustment. Rule 10: when the preceding branch in this if/else chain did not match, and the defending Pokémon's Special Attack parameter is below 6 in the native AI value scale, the AI subtracts 6 points from the move's score. Evaluation continues after this adjustment. Rule 11: when the preceding branch in this if/else chain did not match, and the defending Pokémon's Special Defense parameter is below 6 in the native AI value scale, the AI subtracts 6 points from the move's score. Evaluation continues after this adjustment. Rule 12: when the preceding branch in this if/else chain did not match, and the defending Pokémon's Speed parameter is below 6 in the native AI value scale, the AI subtracts 6 points from the move's score. Evaluation continues after this adjustment. Rule 13: when the preceding branch in this if/else chain did not match, and the defending Pokémon's accuracy parameter is below 6 in the native AI value scale, the AI subtracts 6 points from the move's score. Evaluation continues after this adjustment. Rule 14: when the preceding branch in this if/else chain did not match, and the defending Pokémon's evasion parameter is below 6 in the native AI value scale, the AI subtracts 6 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -6 | — |
| `BaciAI_Seq_028()` | 1310–1332 | direct score writer | Trigger: the Basic dispatcher selects move sequence 028. Rule 1: when the defending Pokémon's usable reserve count is zero, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the defending Pokémon's ability is Suction Cups; the defending Pokémon's ability is Magic Bounce, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_037()` | 1334–1356 | direct score writer | Trigger: the Basic dispatcher selects move sequence 037. Rule 1: when the attacking Pokémon is affected by Heal Block, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: when at least one of the following is true: the field has Electric Terrain; the field has Misty Terrain and all of the following are true: the attacking Pokémon's ability is not Levitate; the attacking Pokémon's first type is not Flying; the attacking Pokémon's second type is not Flying, the AI subtracts 10 points from the move's score. The function then returns immediately. | -10 | BaciAI_Seq_032 |
| `BaciAI_Seq_032()` | 1358–1366 | direct score writer | Trigger: the Basic dispatcher selects move sequence 032. Rule 1: when the attacking Pokémon's HP is exactly 100%, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. | -8 | — |
| `BaciAI_Seq_033()` | 1368–1469 | direct score writer | Trigger: the Basic dispatcher selects move sequence 033. Rule 1: when the defending Pokémon's ability is Poison Heal, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 2: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 4: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Immunity, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 5: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the current weather is Weather hare and the defending Pokémon's ability is Leaf Guard, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 6: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and the defending Pokémon's ability is Flower Veil, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 7: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Flower Veil, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 8: when at least one of the following is true: the defending Pokémon's first type is Steel; the defending Pokémon's first type is Poison; the defending Pokémon's second type is Steel; the defending Pokémon's second type is Poison, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 9: when the defending Pokémon's ability is Magic Guard, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 10: when the defending Pokémon has a status condition, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 11: when the field has Misty Terrain and all of the following are true: the defending Pokémon's ability is not Levitate; the defending Pokémon's first type is not Flying; the defending Pokémon's second type is not Flying, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 12: when the side belonging to the defending Pokémon has Safeguard, the AI subtracts 10 points from the move's score. The function then returns immediately. | -12, -10 | — |
| `BaciAI_Seq_035()` | 1471–1479 | direct score writer | Trigger: the Basic dispatcher selects move sequence 035. Rule 1: when the side belonging to the attacking Pokémon has Light Screen, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_038()` | 1481–1503 | direct score writer | Trigger: the Basic dispatcher selects move sequence 038. Rule 1: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Sturdy, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when higher defender level, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_046()` | 1505–1513 | direct score writer | Trigger: the Basic dispatcher selects move sequence 046. Rule 1: when the side belonging to the attacking Pokémon has Mist, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_047()` | 1515–1523 | direct score writer | Trigger: the Basic dispatcher selects move sequence 047. Rule 1: when the attacking Pokémon has the checked continuous-effect flag, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_049()` | 1525–1564 | direct score writer | Trigger: the Basic dispatcher selects move sequence 049. Rule 1: when the side belonging to the defending Pokémon has Safeguard, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and the defending Pokémon is affected by Confusion, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 4: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Own Tempo, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 5: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -8, -12 | — |
| `BaciAI_Seq_065()` | 1566–1574 | direct score writer | Trigger: the Basic dispatcher selects move sequence 065. Rule 1: when the side belonging to the attacking Pokémon has Reflect, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_067()` | 1576–1672 | direct score writer | Trigger: the Basic dispatcher selects move sequence 067. Rule 1: when the side belonging to the defending Pokémon has Safeguard, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and the defending Pokémon has a status condition, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Electric; the defending Pokémon's second type is Electric, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 4: when the preceding branch in this if/else chain did not match, and the current move has no effect against the target, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 5: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Limber, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 6: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 7: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the current move is Thunder Wave and at least one of the following is true: the defending Pokémon's ability is Motor Drive; the defending Pokémon's ability is Lightning Rod; the defending Pokémon's ability is Volt Absorb, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 8: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the current weather is Weather hare and the defending Pokémon's ability is Leaf Guard, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 9: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and the defending Pokémon's ability is Flower Veil, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 10: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Flower Veil, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 11: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 12: when the field has Misty Terrain and all of the following are true: the defending Pokémon's ability is not Levitate; the defending Pokémon's first type is not Flying; the defending Pokémon's second type is not Flying, the AI subtracts 10 points from the move's score. The function then returns immediately. Within an if/else chain, only the first matching branch is reached. | -10, -12 | — |
| `BaciAI_Seq_079()` | 1674–1687 | direct score writer | Trigger: the Basic dispatcher selects move sequence 079. Rule 1: when the attacking Pokémon has a Substitute, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the attacking Pokémon's HP is below 26%, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -8, -10 | — |
| `BaciAI_Seq_084()` | 1689–1730 | direct score writer | Trigger: the Basic dispatcher selects move sequence 084. Rule 1: when the defending Pokémon is affected by Leech Seed, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 4: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and the defending Pokémon's ability is Magic Guard, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 5: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Within an if/else chain, only the first matching branch is reached. | -8, -10, -12 | — |
| `BaciAI_Seq_086()` | 1732–1773 | direct score writer | Trigger: the Basic dispatcher selects move sequence 086. Rule 1: when the defending Pokémon is affected by Disable, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when at least one of the following is true: the attacker moves first; the attacking Pokémon's ability is Prankster and the last move used by the defending Pokémon is 0, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 4: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and the defending Pokémon's ability is Aroma Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 5: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Aroma Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -12 | — |
| `BaciAI_Seq_090()` | 1775–1816 | direct score writer | Trigger: the Basic dispatcher selects move sequence 090. Rule 1: when the defending Pokémon is affected by Encore, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when at least one of the following is true: the attacker moves first; the attacking Pokémon's ability is Prankster and the last move used by the defending Pokémon is 0, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 4: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and the defending Pokémon's ability is Aroma Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 5: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Aroma Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -12 | — |
| `BaciAI_Seq_092()` | 1818–1827 | direct score writer | Trigger: the Basic dispatcher selects move sequence 092. Rule 1: when the attacking Pokémon is not affected by Sleep, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_094()` | 1829–1852 | direct score writer | Trigger: the Basic dispatcher selects move sequence 094. Rule 1: when the attacking Pokémon is affected by the sure-hit target state, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and at least one of the following is true: the attacking Pokémon's ability is No Guard; the defending Pokémon's ability is No Guard, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Within an if/else chain, only the first matching branch is reached. | -10, -8 | — |
| `BaciAI_Seq_102()` | 1854–1873 | direct score writer | Trigger: the Basic dispatcher selects move sequence 102. Rule 1: when the attacking Pokémon has no status condition and the attacking Pokémon has no reserve Pokémon with the checked condition, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_106()` | 1875–1909 | direct score writer | Trigger: the Basic dispatcher selects move sequence 106. Rule 1: when the defending Pokémon is affected by Soak, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when at least one of the following is true: the defending Pokémon's first type is Ghost; the defending Pokémon's second type is Ghost, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 4: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Within an if/else chain, only the first matching branch is reached. | -10, -12 | — |
| `BaciAI_Seq_107()` | 1911–1932 | direct score writer | Trigger: the Basic dispatcher selects move sequence 107. Rule 1: when the defending Pokémon is affected by Nightmare, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and the defending Pokémon is not affected by Sleep, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Within an if/else chain, only the first matching branch is reached. | -10, -8 | — |
| `BaciAI_Seq_109()` | 1934–1965 | direct score writer | Trigger: the Basic dispatcher selects move sequence 109. Rule 1: when at least one of the following is true: the attacking Pokémon's first type is Ghost; the attacking Pokémon's second type is Ghost and the defending Pokémon is affected by Curse, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and the attacking Pokémon's ability is Contrary, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 3: when the preceding branch in this if/else chain did not match, and the attacking Pokémon's Attack parameter is exactly 12 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 4: when the preceding branch in this if/else chain did not match, and the attacking Pokémon's Defense parameter is exactly 12 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -12 | — |
| `BaciAI_Seq_112()` | 1967–1995 | direct score writer | Trigger: the Basic dispatcher selects move sequence 112. Rule 1: when the number of Spikes layers is 3, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and the number of usable reserves is 0, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -12 | — |
| `BaciAI_Seq_113()` | 1997–2018 | direct score writer | Trigger: the Basic dispatcher selects move sequence 113. Rule 1: when the defending Pokémon is affected by Miracle Eye, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -12 | — |
| `BaciAI_Seq_114()` | 2020–2029 | direct score writer | Trigger: the Basic dispatcher selects move sequence 114. Rule 1: when the defending Pokémon is affected by Perish Song, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_115()` | 2031–2040 | direct score writer | Trigger: the Basic dispatcher selects move sequence 115. Rule 1: when the current weather is Weather sunaarashi, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. | -8 | — |
| `BaciAI_Seq_120()` | 2042–2099 | direct score writer | Trigger: the Basic dispatcher selects move sequence 120. Rule 1: when the defending Pokémon is affected by Infatuation, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and the attacking Pokémon's sex is male and the defending Pokémon's sex is not female, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and the attacking Pokémon's sex is female and the defending Pokémon's sex is not male, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 4: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Oblivious, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 5: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and the defending Pokémon's ability is Aroma Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 6: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 7: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Aroma Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -12 | — |
| `BaciAI_Seq_124()` | 2101–2109 | direct score writer | Trigger: the Basic dispatcher selects move sequence 124. Rule 1: when the side belonging to the attacking Pokémon has Safeguard, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_127()` | 2111–2120 | direct score writer | Trigger: the Basic dispatcher selects move sequence 127. Rule 1: when the number of usable reserves is 0, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_132()` | 2122–2130 | direct score writer | Trigger: the Basic dispatcher selects move sequence 132. Rule 1: when the attacking Pokémon's HP is exactly 100%, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. | -8 | — |
| `BaciAI_Seq_136()` | 2132–2141 | direct score writer | Trigger: the Basic dispatcher selects move sequence 136. Rule 1: when the current weather is Weather ame, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. | -8 | — |
| `BaciAI_Seq_137()` | 2143–2152 | direct score writer | Trigger: the Basic dispatcher selects move sequence 137. Rule 1: when the current weather is Weather hare, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. | -8 | — |
| `BaciAI_Seq_142()` | 2154–2172 | direct score writer | Trigger: the Basic dispatcher selects move sequence 142. Rule 1: when the attacking Pokémon's ability is Contrary, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 2: when the attacking Pokémon's Attack parameter is exactly 12 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and the attacking Pokémon's HP is below 51%, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -12, -10 | — |
| `BaciAI_Seq_148()` | 2174–2182 | direct score writer | Trigger: the Basic dispatcher selects move sequence 148. Rule 1: when the defending Pokémon is under a delayed-action effect, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_158()` | 2184–2193 | direct score writer | Trigger: the Basic dispatcher selects move sequence 158. Rule 1: when the attacking Pokémon's Fake Out/action-used flag is not 0, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_160()` | 2195–2209 | direct score writer | Trigger: the Basic dispatcher selects move sequence 160. Rule 1: when the attacking Pokémon's ability is Contrary, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 2: when the attacking Pokémon's Stockpile count is 3, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -12, -10 | — |
| `BaciAI_Seq_161()` | 2211–2220 | direct score writer | Trigger: the Basic dispatcher selects move sequence 161. Rule 1: when the attacking Pokémon's Stockpile count is zero, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_164()` | 2222–2231 | direct score writer | Trigger: the Basic dispatcher selects move sequence 164. Rule 1: when the current weather is Weather arare, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. | -8 | — |
| `BaciAI_Seq_165()` | 2233–2267 | direct score writer | Trigger: the Basic dispatcher selects move sequence 165. Rule 1: when the defending Pokémon is affected by Torment, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Aroma Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 4: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Aroma Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -12 | — |
| `BaciAI_Seq_167()` | 2269–2360 | direct score writer | Trigger: the Basic dispatcher selects move sequence 167. Rule 1: when at least one of the following is true: the defending Pokémon's first type is Fire; the defending Pokémon's second type is Fire, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and the defending Pokémon's ability is Magic Guard, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and the defending Pokémon has a status condition, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 4: when the preceding branch in this if/else chain did not match, and the side belonging to the defending Pokémon has Safeguard, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 5: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 6: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and the defending Pokémon's ability is Flash Fire, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 7: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and the defending Pokémon's ability is Water Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 8: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and the current weather is Weather hare and the defending Pokémon's ability is Leaf Guard, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 9: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and the defending Pokémon's ability is Flower Veil, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 10: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Flower Veil, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 11: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 12: when the field has Misty Terrain and all of the following are true: the defending Pokémon's ability is not Levitate; the defending Pokémon's first type is not Flying; the defending Pokémon's second type is not Flying, the AI subtracts 10 points from the move's score. The function then returns immediately. Within an if/else chain, only the first matching branch is reached. | -10, -12 | — |
| `BaciAI_Seq_168()` | 2362–2424 | direct score writer | Trigger: the Basic dispatcher selects move sequence 168. Rule 1: when the number of usable reserves is 0, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and the defending Pokémon's Attack parameter is exactly 0 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and the defending Pokémon's Special Attack parameter is exactly 0 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 4: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Contrary, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 5: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's ability is Magic Bounce; the defending Pokémon's ability is Clear Body; the defending Pokémon's ability is White Smoke, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 6: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and the defending Pokémon's ability is Flower Veil, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 7: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Flower Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 8: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Within an if/else chain, only the first matching branch is reached. | -10, -12 | — |
| `BaciAI_Seq_172()` | 2426–2435 | direct score writer | Trigger: the Basic dispatcher selects move sequence 172. Rule 1: when at least one of the following is true: the battle format is Single Battles; the battle format is Rotation Battles, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_175()` | 2437–2472 | direct score writer | Trigger: the Basic dispatcher selects move sequence 175. Rule 1: when the defending Pokémon is affected by Taunt, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the defending Pokémon's ability is Aroma Veil; the defending Pokémon's ability is Oblivious, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 4: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Aroma Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -12 | — |
| `BaciAI_Seq_176()` | 2474–2483 | direct score writer | Trigger: the Basic dispatcher selects move sequence 176. Rule 1: when at least one of the following is true: the battle format is Single Battles; the battle format is Rotation Battles, the AI subtracts 20 points from the move's score. Evaluation continues after this adjustment. | -20 | — |
| `BaciAI_Seq_177()` | 2485–2524 | direct score writer | Trigger: the Basic dispatcher selects move sequence 177. Rule 1: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Sticky Hold, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when at least one of the following is true: the defending Pokémon's species is Arceus; the defending Pokémon's species is Genesect, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 4: when the defending Pokémon's species is Giratina and the defending Pokémon holds the held item associated with Giratina's Origin Forme, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 5: when the defending Pokémon is Mega-Evolved, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_178()` | 2526–2551 | direct score writer | Trigger: the Basic dispatcher selects move sequence 178. Rule 1: when at least one of the following is true: the defending Pokémon's ability is Trace; the defending Pokémon's ability is Zen Mode, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: when at least one of the following is true: the defending Pokémon's species is Castform; the defending Pokémon's species is Arceus; the defending Pokémon's species is Cherrim; the defending Pokémon's species is Zoroark; the defending Pokémon's species is Ditto; the defending Pokémon's species is Shedinja; the defending Pokémon's species is Aegislash; the defending Pokémon's species is Slaking; the defending Pokémon's species is Archeops; the defending Pokémon's species is Regigigas, the AI subtracts 10 points from the move's score. The function then returns immediately. | -10 | — |
| `BaciAI_Seq_179()` | 2553–2560 | direct score writer | Trigger: the Basic dispatcher selects move sequence 179. Rule 1: when the last move used by the attacking Pokémon is Wish, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_181()` | 2562–2570 | direct score writer | Trigger: the Basic dispatcher selects move sequence 181. Rule 1: when the attacking Pokémon is affected by the internal move-state flag NEWOHARU, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_184()` | 2572–2581 | direct score writer | Trigger: the Basic dispatcher selects move sequence 184. Rule 1: when the attacking Pokémon's Recycle state is zero, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. | -8 | — |
| `BaciAI_Seq_188()` | 2583–2612 | direct score writer | Trigger: the Basic dispatcher selects move sequence 188. Rule 1: when the attacking Pokémon's held-item state is zero, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Sticky Hold, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Within an if/else chain, only the first matching branch is reached. | -10 | — |
| `BaciAI_Seq_191()` | 2614–2651 | direct score writer | Trigger: the Basic dispatcher selects move sequence 191. Rule 1: when at least one of the following is true: the defending Pokémon's ability is Wonder Guard; the defending Pokémon's ability is Multitype; the defending Pokémon's ability is Illusion; the defending Pokémon's ability is Stance Change, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when at least one of the following is true: the defending Pokémon's species is Castform; the defending Pokémon's species is Arceus; the defending Pokémon's species is Cherrim; the defending Pokémon's species is Zoroark; the defending Pokémon's species is Ditto; the defending Pokémon's species is Shedinja; the defending Pokémon's species is Aegislash, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when at least one of the following is true: the defending Pokémon's species is Slaking; the defending Pokémon's species is Archeops; the defending Pokémon's species is Regigigas, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 4: when at least one of the following is true: the defending Pokémon's ability is Truant; the defending Pokémon's ability is Defeatist; the defending Pokémon's ability is Slow Start, the AI subtracts 12 points from the move's score. The function then returns immediately. | -10, -12 | — |
| `BaciAI_Seq_192()` | 2653–2661 | direct score writer | Trigger: the Basic dispatcher selects move sequence 192. Rule 1: when the field has Imprison, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_193()` | 2663–2671 | direct score writer | Trigger: the Basic dispatcher selects move sequence 193. Rule 1: when the attacking Pokémon has no status condition, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_201()` | 2673–2681 | direct score writer | Trigger: the Basic dispatcher selects move sequence 201. Rule 1: when the field has Mud Sport, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_205()` | 2683–2750 | direct score writer | Trigger: the Basic dispatcher selects move sequence 205. Rule 1: when at least one of the following is true: the defending Pokémon's ability is Defiant; the defending Pokémon's ability is Competitive, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and the defending Pokémon's Attack parameter is exactly 0 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and the defending Pokémon's Defense parameter is exactly 0 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 4: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the defending Pokémon's ability is Hyper Cutter; the defending Pokémon's ability is Big Pecks; the defending Pokémon's ability is Clear Body; the defending Pokémon's ability is White Smoke, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 5: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's ability is Contrary; the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 6: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and the defending Pokémon's ability is Flower Veil, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 7: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Flower Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 8: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Within an if/else chain, only the first matching branch is reached. | -12, -10 | — |
| `BaciAI_Seq_206()` | 2752–2771 | direct score writer | Trigger: the Basic dispatcher selects move sequence 206. Rule 1: when the attacking Pokémon's ability is Contrary, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 2: when the attacking Pokémon's Defense parameter is exactly 12 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and the attacking Pokémon's Special Defense parameter is exactly 12 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -12, -10 | — |
| `BaciAI_Seq_208()` | 2773–2792 | direct score writer | Trigger: the Basic dispatcher selects move sequence 208. Rule 1: when the attacking Pokémon's ability is Contrary, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 2: when the attacking Pokémon's Attack parameter is exactly 12 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and the attacking Pokémon's Defense parameter is exactly 12 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -12, -10 | — |
| `BaciAI_Seq_210()` | 2794–2802 | direct score writer | Trigger: the Basic dispatcher selects move sequence 210. Rule 1: when the field has Water Sport, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_211()` | 2804–2823 | direct score writer | Trigger: the Basic dispatcher selects move sequence 211. Rule 1: when the attacking Pokémon's ability is Contrary, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 2: when the attacking Pokémon's Special Attack parameter is exactly 12 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and the attacking Pokémon's Special Defense parameter is exactly 12 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -12, -10 | — |
| `BaciAI_Seq_212()` | 2825–2839 | direct score writer | Trigger: the Basic dispatcher selects move sequence 212. Rule 1: when the attacking Pokémon's ability is Contrary, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 2: when the attacking Pokémon's Attack parameter is exactly 12 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -12, -10 | — |
| `BaciAI_Seq_215()` | 2841–2849 | direct score writer | Trigger: the Basic dispatcher selects move sequence 215. Rule 1: when the field has Gravity, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_216()` | 2851–2872 | direct score writer | Trigger: the Basic dispatcher selects move sequence 216. Rule 1: when the defending Pokémon is affected by Miracle Eye, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -12 | — |
| `BaciAI_Seq_220()` | 2874–2889 | direct score writer | Trigger: the Basic dispatcher selects move sequence 220. Rule 1: when the number of usable reserves is 0, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: unconditionally, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_222()` | 2891–2898 | direct score writer | Trigger: the Basic dispatcher selects move sequence 222. Rule 1: when the attacking Pokémon's held item is 0, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_225()` | 2900–2913 | direct score writer | Trigger: the Basic dispatcher selects move sequence 225. Rule 1: when the side belonging to the attacking Pokémon has Tailwind, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and the field has Trick Room, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -8 | — |
| `BaciAI_Seq_226()` | 2915–2919 | reachable dispatcher/predicate support | Basic AI sequence 226 has an empty body: it performs no checks, calls, or direct score writes. | indirect/dynamic | — |
| `BaciAI_Seq_227()` | 2921–2951 | direct score writer | Trigger: the Basic dispatcher selects move sequence 227. Rule 1: when the defending Pokémon's ability is Aftermath, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and the attacker moves first, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10 | — |
| `BaciAI_Seq_232()` | 2953–2981 | direct score writer | Trigger: the Basic dispatcher selects move sequence 232. Rule 1: when the defending Pokémon is affected by the internal move-state flag SASIOSAE, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Within an if/else chain, only the first matching branch is reached. | -10, -12 | — |
| `BaciAI_Seq_233()` | 2983–3019 | direct score writer | Trigger: the Basic dispatcher selects move sequence 233. Rule 1: when the attacking Pokémon's held-item effect is 0, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the attacking Pokémon's held-item effect is a flinch-causing held-item effect and the defender moves first, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when the attacking Pokémon's held-item effect is a flinch-causing held-item effect and all of the following are true: the defending Pokémon's ability is Inner Focus; the defending Pokémon's ability is Prankster, the AI subtracts 10 points from the move's score. The function then returns immediately. | -10 | BaciAI_Seq_033, BaciAI_Seq_067, BaciAI_Seq_167 |
| `BaciAI_Seq_234()` | 3021–3055 | direct score writer | Trigger: the Basic dispatcher selects move sequence 234. Rule 1: when the defending Pokémon has a status condition, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and the attacking Pokémon has no status condition, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and the side belonging to the defending Pokémon has Safeguard, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -8 | BaciAI_Seq_033, BaciAI_Seq_067, BaciAI_Seq_167 |
| `BaciAI_Seq_236()` | 3057–3090 | direct score writer | Trigger: the Basic dispatcher selects move sequence 236. Rule 1: when the defending Pokémon is affected by Heal Block, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the preceding branch in this if/else chain did not match, and the defending Pokémon's ability is Aroma Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 4: when the preceding branch in this if/else chain did not match, and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the defending Pokémon's ally's ability is Aroma Veil, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -12 | — |
| `BaciAI_Seq_238()` | 3092–3104 | direct score writer | Trigger: the Basic dispatcher selects move sequence 238. Rule 1: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. | -10 | — |
| `BaciAI_Seq_239()` | 3106–3166 | direct score writer | Trigger: the Basic dispatcher selects move sequence 239. Rule 1: when the defending Pokémon is affected by Gastro Acid, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: when at least one of the following is true: the defending Pokémon's ability is Multitype; the defending Pokémon's ability is Run Away; the defending Pokémon's ability is Keen Eye, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 4: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 5: when at least one of the following is true: the defending Pokémon's species is Arceus; the defending Pokémon's species is Aegislash, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 6: when at least one of the following is true: the defending Pokémon's species is Slaking; the defending Pokémon's species is Archeops; the defending Pokémon's species is Regigigas, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 7: when at least one of the following is true: the defending Pokémon's ability is Truant; the defending Pokémon's ability is Defeatist; the defending Pokémon's ability is Slow Start, the AI subtracts 12 points from the move's score. The function then returns immediately. | -10, -12 | — |
| `BaciAI_Seq_240()` | 3168–3176 | reachable dispatcher/predicate support | Basic AI sequence 240 has an empty body: it performs no checks, calls, or direct score writes. | indirect/dynamic | — |
| `BaciAI_Seq_241()` | 3178–3187 | direct score writer | Trigger: the Basic dispatcher selects move sequence 241. Rule 1: when the defender moves first and the attacking Pokémon's ability is not Prankster, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_242()` | 3189–3201 | direct score writer | Trigger: the Basic dispatcher selects move sequence 242. Rule 1: when the current battle turn is 0 and the defender moves first, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_243()` | 3203–3215 | direct score writer | Trigger: the Basic dispatcher selects move sequence 243. Rule 1: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. | -10 | — |
| `BaciAI_Seq_244()` | 3217–3229 | direct score writer | Trigger: the Basic dispatcher selects move sequence 244. Rule 1: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. | -10 | — |
| `BaciAI_Seq_246()` | 3231–3240 | direct score writer | Trigger: the Basic dispatcher selects move sequence 246. Rule 1: unconditionally, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_247()` | 3242–3294 | direct score writer | Trigger: the Basic dispatcher selects move sequence 247. Rule 1: when the defending Pokémon's ability is Insomnia, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 3: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 4: when at least one of the following is true: the defending Pokémon's species is Arceus; the defending Pokémon's species is Aegislash, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 5: when at least one of the following is true: the defending Pokémon's species is Slaking; the defending Pokémon's species is Archeops; the defending Pokémon's species is Regigigas, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 6: when at least one of the following is true: the defending Pokémon's ability is Truant; the defending Pokémon's ability is Defeatist; the defending Pokémon's ability is Slow Start, the AI subtracts 12 points from the move's score. The function then returns immediately. | -10, -12 | — |
| `BaciAI_Seq_249()` | 3296–3326 | direct score writer | Trigger: the Basic dispatcher selects move sequence 249. Rule 1: when the number of Toxic Spikes layers is 2, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: when the number of usable reserves is 0, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. | -10, -12 | — |
| `BaciAI_Seq_251()` | 3328–3336 | direct score writer | Trigger: the Basic dispatcher selects move sequence 251. Rule 1: when the attacking Pokémon is affected by Aqua Ring, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_252()` | 3338–3368 | direct score writer | Trigger: the Basic dispatcher selects move sequence 252. Rule 1: when the attacking Pokémon is affected by the semi-invulnerable Flying state, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: when the attacking Pokémon's ability is Levitate, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when at least one of the following is true: the attacking Pokémon's first type is Flying; the attacking Pokémon's second type is Flying, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 4: when the field has Gravity, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_258()` | 3370–3400 | direct score writer | Trigger: the Basic dispatcher selects move sequence 258. Rule 1: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 2: when the defending Pokémon's evasion parameter is exactly 0 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -12, -10 | — |
| `BaciAI_Seq_259()` | 3402–3415 | reachable dispatcher/predicate support | Basic AI sequence 259 has an empty body: it performs no checks, calls, or direct score writes. | indirect/dynamic | — |
| `BaciAI_Seq_265()` | 3417–3441 | direct score writer | Trigger: the Basic dispatcher selects move sequence 265. Rule 1: when the attacking Pokémon's sex is male and the defending Pokémon's sex is not female, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: when the preceding branch in this if/else chain did not match, and the attacking Pokémon's sex is female and the defending Pokémon's sex is not male, the AI subtracts 10 points from the move's score. The function then returns immediately. Within an if/else chain, only the first matching branch is reached. | -10 | BaciAI_Seq_021 |
| `BaciAI_Seq_266()` | 3443–3472 | direct score writer | Trigger: the Basic dispatcher selects move sequence 266. Rule 1: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 2: when the side belonging to the defending Pokémon has Stealth Rock, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when the number of usable reserves is 0, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -12, -10 | — |
| `BaciAI_Seq_270()` | 3474–3498 | direct score writer | Trigger: the Basic dispatcher selects move sequence 270. Rule 1: when the number of usable reserves is 0, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: unconditionally, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_278()` | 3500–3509 | direct score writer | Trigger: the Basic dispatcher selects move sequence 278. Rule 1: when at least one of the following is true: the battle format is Single Battles; the battle format is Rotation Battles, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_281()` | 3511–3519 | direct score writer | Trigger: the Basic dispatcher selects move sequence 281. Rule 1: when the field has Wonder Room, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_285()` | 3521–3550 | direct score writer | Trigger: the Basic dispatcher selects move sequence 285. Rule 1: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 2: when the defending Pokémon is affected by Telekinesis, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. | -12, -10 | — |
| `BaciAI_Seq_286()` | 3552–3560 | direct score writer | Trigger: the Basic dispatcher selects move sequence 286. Rule 1: when the field has Magic Room, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_292()` | 3563–3590 | direct score writer | Trigger: the Basic dispatcher selects move sequence 292. Rule 1: when all of the following are true: the attacking Pokémon's first type is not Def type1; the attacking Pokémon's first type is not Def type2; the attacking Pokémon's second type is not Def type1; the attacking Pokémon's second type is not Def type2, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_294()` | 3592–3620 | direct score writer | Trigger: the Basic dispatcher selects move sequence 294. Rule 1: when the defending Pokémon's ability is Storm Drain and all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 2: when at least one of the following is true: the defending Pokémon's first type is Water; the defending Pokémon's second type is Water, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. | -12, -10 | — |
| `BaciAI_Seq_298()` | 3622–3686 | direct score writer | Trigger: the Basic dispatcher selects move sequence 298. Rule 1: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: when at least one of the following is true: the defending Pokémon's ability is Trace; the defending Pokémon's ability is Zen Mode, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when at least one of the following is true: the defending Pokémon's species is Castform; the defending Pokémon's species is Arceus; the defending Pokémon's species is Cherrim; the defending Pokémon's species is Zoroark; the defending Pokémon's species is Ditto; the defending Pokémon's species is Shedinja; the defending Pokémon's species is Aegislash, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 4: when the defending Pokémon's ability is Simple, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 5: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 6: when at least one of the following is true: the defending Pokémon's species is Slaking; the defending Pokémon's species is Archeops; the defending Pokémon's species is Regigigas, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 7: when at least one of the following is true: the defending Pokémon's ability is Truant; the defending Pokémon's ability is Defeatist; the defending Pokémon's ability is Slow Start, the AI subtracts 12 points from the move's score. The function then returns immediately. | -10, -12 | — |
| `BaciAI_Seq_299()` | 3688–3750 | direct score writer | Trigger: the Basic dispatcher selects move sequence 299. Rule 1: when the attacking Pokémon's ability is Def tokusei, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 3: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 4: when at least one of the following is true: the defending Pokémon's ability is Trace; the defending Pokémon's ability is Zen Mode, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 5: when at least one of the following is true: the defending Pokémon's species is Castform; the defending Pokémon's species is Arceus; the defending Pokémon's species is Cherrim; the defending Pokémon's species is Zoroark; the defending Pokémon's species is Ditto; the defending Pokémon's species is Shedinja; the defending Pokémon's species is Aegislash, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 6: when at least one of the following is true: the defending Pokémon's species is Slaking; the defending Pokémon's species is Archeops; the defending Pokémon's species is Regigigas, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 7: when at least one of the following is true: the defending Pokémon's ability is Truant; the defending Pokémon's ability is Defeatist; the defending Pokémon's ability is Slow Start, the AI subtracts 12 points from the move's score. The function then returns immediately. | -10, -12 | — |
| `BaciAI_Seq_300()` | 3752–3761 | direct score writer | Trigger: the Basic dispatcher selects move sequence 300. Rule 1: when at least one of the following is true: the battle format is Single Battles; the battle format is Rotation Battles, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_301()` | 3763–3772 | reachable dispatcher/predicate support | Basic AI sequence 301 has an empty body: it performs no checks, calls, or direct score writes. | indirect/dynamic | — |
| `BaciAI_Seq_307()` | 3774–3797 | direct score writer | Trigger: the Basic dispatcher selects move sequence 307. Rule 1: when at least one of the following is true: the battle format is Single Battles; the battle format is Rotation Battles, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: when the battle is in Multi mode, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the attacking Pokémon's ally's HP is exactly 0%, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_309()` | 3799–3808 | direct score writer | Trigger: the Basic dispatcher selects move sequence 309. Rule 1: when at least one of the following is true: the battle format is Single Battles; the battle format is Rotation Battles, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_311()` | 3810–3834 | direct score writer | Trigger: the Basic dispatcher selects move sequence 311. Rule 1: when the attacking Pokémon's weight is at least 2000, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: when the defending Pokémon's ability is Heavy Metal and the attacking Pokémon's weight is at least 1000, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. | -10 | — |
| `BaciAI_Seq_315()` | 3836–3853 | direct score writer | Trigger: the Basic dispatcher selects move sequence 315. Rule 1: when at least one of the following is true: the battle format is Single Battles; the battle format is Rotation Battles, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. | -10 | — |
| `BaciAI_Seq_318()` | 3855–3879 | direct score writer | Trigger: the Basic dispatcher selects move sequence 318. Rule 1: when the defending Pokémon's first type is Atk type1 and the defending Pokémon's second type is Atk type2, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: when the defending Pokémon's first type is Atk type2 and the defending Pokémon's second type is Atk type1, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_320()` | 3881–3891 | direct score writer | Trigger: the Basic dispatcher selects move sequence 320. Rule 1: when the number of usable reserves is 0, the AI subtracts 10 points from the move's score. The function then returns immediately. | -10 | — |
| `BaciAI_Seq_323()` | 3893–3926 | direct score writer | Trigger: the Basic dispatcher selects move sequence 323. Rule 1: when the attacking Pokémon's held-item state is zero, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when at least one of the following is true: the defending Pokémon's species is Arceus; the defending Pokémon's species is Genesect, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 4: when the defending Pokémon's species is Giratina and the defending Pokémon holds the held item associated with Giratina's Origin Forme, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 5: when the defending Pokémon is Mega-Evolved, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -10 | — |
| `BaciAI_Seq_338()` | 3928–3936 | direct score writer | Trigger: the Basic dispatcher selects move sequence 338. Rule 1: unconditionally, the AI subtracts 8 points from the move's score. Evaluation continues after this adjustment. | -8 | — |
| `BaciAI_Seq_339()` | 3938–4021 | direct score writer | Trigger: the Basic dispatcher selects move sequence 339. Rule 1: when all of the following are true: the attacking Pokémon's first type is not Grass; the attacking Pokémon's second type is not Grass and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and all of the following are true: the defending Pokémon's ally's first type is not Grass; the defending Pokémon's ally's second type is not Grass, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: when all of the following are true: the attacking Pokémon's first type is not Grass; the attacking Pokémon's second type is not Grass and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the preceding branch in this if/else chain did not match and the defending Pokémon's ally's ability is Contrary, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 3: when all of the following are true: the attacking Pokémon's first type is not Grass; the attacking Pokémon's second type is not Grass and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and the preceding branch in this if/else chain did not match and at least one of the following is true: the defending Pokémon's ally's first type is Flying; the defending Pokémon's ally's second type is Flying; the defending Pokémon's ally's ability is Levitate, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 4: when all of the following are true: the attacking Pokémon's first type is not Grass; the attacking Pokémon's second type is not Grass and the preceding branch in this if/else chain did not match, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 5: when the preceding branch in this if/else chain did not match and the attacking Pokémon's ability is Contrary, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 6: when the preceding branch in this if/else chain did not match and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and at least one of the following is true: the defending Pokémon's ally's first type is Grass; the defending Pokémon's ally's second type is Grass and the defending Pokémon's ally's ability is Contrary, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 7: when the preceding branch in this if/else chain did not match and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and at least one of the following is true: the attacking Pokémon's first type is Flying; the attacking Pokémon's second type is Flying; the attacking Pokémon's ability is Levitate and all of the following are true: the defending Pokémon's ally's first type is not Grass; the defending Pokémon's ally's second type is not Grass, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 8: when the preceding branch in this if/else chain did not match and at least one of the following is true: the battle format is Double Battles; the battle format is Triple Battles and at least one of the following is true: the attacking Pokémon's first type is Flying; the attacking Pokémon's second type is Flying; the attacking Pokémon's ability is Levitate and at least one of the following is true: the defending Pokémon's ally's first type is Flying; the defending Pokémon's ally's second type is Flying; the defending Pokémon's ally's ability is Levitate, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 9: when the preceding branch in this if/else chain did not match and the preceding branch in this if/else chain did not match, and at least one of the following is true: the attacking Pokémon's first type is Flying; the attacking Pokémon's second type is Flying; the attacking Pokémon's ability is Levitate, the AI subtracts 10 points from the move's score. The function then returns immediately. Within an if/else chain, only the first matching branch is reached. | -10, -12 | — |
| `BaciAI_Seq_340()` | 4023–4052 | direct score writer | Trigger: the Basic dispatcher selects move sequence 340. Rule 1: when all of the following are true: the attacking Pokémon's ability is not Mold Breaker; the attacking Pokémon's ability is not Teravolt; the attacking Pokémon's ability is not Turboblaze and the defending Pokémon's ability is Magic Bounce, the AI subtracts 12 points from the move's score. The function then returns immediately. Rule 2: when the side belonging to the defending Pokémon has Sticky Web, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when the number of usable reserves is 0, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -12, -10 | — |
| `BaciAI_Seq_342()` | 4054–4079 | direct score writer | Trigger: the Basic dispatcher selects move sequence 342. Rule 1: when at least one of the following is true: the defending Pokémon's first type is Ghost; the defending Pokémon's second type is Ghost, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: when the defending Pokémon has Ghost as its special/ex type, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. | -10 | — |
| `BaciAI_Seq_375()` | 4081–4106 | direct score writer | Trigger: the Basic dispatcher selects move sequence 375. Rule 1: when at least one of the following is true: the defending Pokémon's first type is Grass; the defending Pokémon's second type is Grass, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: when the defending Pokémon has Grass as its special/ex type, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 3: when the defending Pokémon has a Substitute and the attacking Pokémon's ability is not Infiltrator, the AI subtracts 10 points from the move's score. The function then returns immediately. | -10 | — |
| `BaciAI_Seq_349()` | 4108–4117 | direct score writer | Trigger: the Basic dispatcher selects move sequence 349. Rule 1: when at least one of the following is true: the battle format is Single Battles; the battle format is Rotation Battles, the AI subtracts 5 points from the move's score. Evaluation continues after this adjustment. | -5 | — |
| `BaciAI_Seq_350()` | 4119–4164 | direct score writer | Trigger: the Basic dispatcher selects move sequence 350. Rule 1: when at least one of the following is true: the battle format is Single Battles; the battle format is Rotation Battles and all of the following are true: the attacking Pokémon's first type is not Grass; the attacking Pokémon's second type is not Grass, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Rule 2: when at least one of the following is true: the battle format is Single Battles; the battle format is Rotation Battles and the preceding branch in this if/else chain did not match and the attacking Pokémon's ability is Contrary, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 3: when at least one of the following is true: the attacking Pokémon's first type is Grass; the attacking Pokémon's second type is Grass and the attacking Pokémon's ability is Contrary, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 4: when at least one of the following is true: the defending Pokémon's ally's first type is Grass; the defending Pokémon's ally's second type is Grass and the attacking Pokémon's ally's ability is Contrary, the AI subtracts 12 points from the move's score. Evaluation continues after this adjustment. Rule 5: when all of the following are true: the attacking Pokémon's first type is not Grass; the attacking Pokémon's second type is not Grass; the defending Pokémon's ally's first type is not Grass; the defending Pokémon's ally's second type is not Grass, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. Within an if/else chain, only the first matching branch is reached. | -10, -12 | — |
| `BaciAI_Seq_351()` | 4166–4174 | direct score writer | Trigger: the Basic dispatcher selects move sequence 351. Rule 1: when the field has Grassy Terrain, the AI subtracts 10 points from the move's score. The function then returns immediately. | -10 | — |
| `BaciAI_Seq_352()` | 4176–4184 | direct score writer | Trigger: the Basic dispatcher selects move sequence 352. Rule 1: when the field has Misty Terrain, the AI subtracts 10 points from the move's score. The function then returns immediately. | -10 | — |
| `BaciAI_Seq_354()` | 4186–4203 | direct score writer | Trigger: the Basic dispatcher selects move sequence 354. Rule 1: when the attacking Pokémon's ability is Shadow Tag, the AI subtracts 10 points from the move's score. The function then returns immediately. Rule 2: when the number of usable reserves is 0, the AI subtracts 10 points from the move's score. The function then returns immediately. | -10 | — |
| `BaciAI_Seq_362()` | 4205–4221 | direct score writer | Trigger: the Basic dispatcher selects move sequence 362. Rule 1: when at least one of the following is true: the battle format is Single Battles; the battle format is Rotation Battles, the AI subtracts 20 points from the move's score. The function then returns immediately. Rule 2: when the attacking Pokémon's ally's Special Defense parameter is exactly 12 in the native AI value scale, the AI subtracts 10 points from the move's score. Evaluation continues after this adjustment. | -20, -10 | — |
| `BaciAI_Seq_363()` | 4223–4235 | direct score writer | Trigger: the Basic dispatcher selects move sequence 363. Rule 1: when at least one of the following is true: the defending Pokémon is not affected by the poison move-state; the defending Pokémon is not badly poisoned, the AI subtracts 10 points from the move's score. The function then returns immediately. | -10 | BaciAI_Seq_018, BaciAI_Seq_021 |
| `BaciAI_Seq_366()` | 4237–4251 | direct score writer | Trigger: the Basic dispatcher selects move sequence 366. Rule 1: when all of the following are true: the attacking Pokémon's ability is not Plus; the attacking Pokémon's ability is not Minus; the defending Pokémon's ally's ability is not Plus; the defending Pokémon's ally's ability is not Minus, the AI subtracts 10 points from the move's score. The function then returns immediately. | -10 | — |
| `BaciAI_Seq_368()` | 4253–4261 | direct score writer | Trigger: the Basic dispatcher selects move sequence 368. Rule 1: when the field has Electric Terrain, the AI subtracts 10 points from the move's score. The function then returns immediately. | -10 | — |
| `BaciAI_Seq_370()` | 4263–4273 | direct score writer | Trigger: the Basic dispatcher selects move sequence 370. Rule 1: when at least one of the following is true: the battle format is Single Battles; the battle format is Rotation Battles, the AI subtracts 20 points from the move's score. The function then returns immediately. | -20 | — |

The complete guarded bodies follow:

### `main()` (source lines 7–16)

```text
    7 | main()
    8 | {
    9 | waza_seq_no = AI_CMD(CMD_CHECK_WORKWAZA_SEQNO);
   13 | main_proc();
   16 | }
```

### `main_proc()` (source lines 18–61)

```text
   18 | main_proc()
   19 | {
   21 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
   22 | if( CHK_rule == BTL_RULE_DOUBLE
   23 | || CHK_rule == BTL_RULE_TRIPLE ){
   24 | if( AI_CMD(CMD_IF_MIKATA_ATTACK)){
   25 | return;
   26 | }
   27 | }
   29 | if ( Basic_ConaHoushi( ) == 1 ){
   30 | return;
   31 | }
   33 | bBasicAll = 1;
   36 | {
   37 | bBasicDamage = false;
   40 | wazaNo = CURRENT_MOVE();
   41 | if( (wazaNo == WAZANO_ZIWARE) || (wazaNo == WAZANO_TUNODORIRU) )
   42 | {
   43 | bBasicDamage = true;
   44 | }
   46 | else if( AI_CMD(CMD_CHECK_DAMAGE_WAZA, CURRENT_MOVE())){
   47 | bBasicDamage = true;
   48 | }
   51 | if( bBasicDamage ){
   52 | bBasicAll = Calc_BasicDamage();
   53 | }
   54 | }
   57 | if( bBasicAll == 1){
   58 | Calc_BasicAll();
   59 | }
   61 | }
```

### `Basic_ConaHoushi()` (source lines 63–94)

```text
   63 | Basic_ConaHoushi( )
   64 | {
   65 | wazaNo = CURRENT_MOVE();
   66 | if( wazaNo == WAZANO_SIBIREGONA || wazaNo == WAZANO_NEMURIGONA
   67 | || wazaNo == WAZANO_DOKUNOKONA || wazaNo == WAZANO_IKARINOKONA
   68 | || wazaNo == WAZANO_KINOKONOHOUSI || wazaNo == WAZANO_HUNZIN){
   70 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_BOUZIN ){
   71 | atk_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
   72 | if( atk_tokusei != TOKUSEI_KATAYABURI
   73 | && atk_tokusei != TOKUSEI_TAABOBUREIZU
   74 | && atk_tokusei != TOKUSEI_TERABORUTEEZI){
   76 | SCORE += -10;
   77 | return 1;
   78 | }
   79 | }
   80 | if(AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) == POKETYPE_KUSA
   81 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) == POKETYPE_KUSA ){
   83 | SCORE += -10;
   84 | return 1;
   85 | }
   92 | }
   93 | return 0;
   94 | }
```

### `Calc_BasicDamage()` (source lines 99–153)

```text
   99 | Calc_BasicDamage( )
  100 | {
  102 | atk_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
  103 | def_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
  105 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI) )
  106 | {
  107 | if( AI_CMD(CMD_CHECK_TYPE, CHECK_WAZA) == POKETYPE_JIMEN ){
  108 | if( def_tokusei == TOKUSEI_HUYUU){
  109 | if( atk_tokusei == TOKUSEI_KATAYABURI
  110 | || atk_tokusei == TOKUSEI_TAABOBUREIZU
  111 | || atk_tokusei == TOKUSEI_TERABORUTEEZI){
  113 | return 1;
  114 | }
  115 | }
  116 | }
  118 | SCORE += -10;
  119 | return 0;
  120 | }
  123 | if( atk_tokusei == TOKUSEI_KATAYABURI
  124 | || atk_tokusei == TOKUSEI_TAABOBUREIZU
  125 | || atk_tokusei == TOKUSEI_TERABORUTEEZI){
  127 | return 1;
  128 | }
  131 | bQuit = 0;
  133 | switch( def_tokusei )
  134 | {
  135 | case TOKUSEI_TIKUDEN: bQuit = BasicDmg_00_1();
  136 | case TOKUSEI_DENKIENZIN: bQuit = BasicDmg_00_1();
  137 | case TOKUSEI_HIRAISIN: bQuit = BasicDmg_00_1();
  138 | case TOKUSEI_TYOSUI: bQuit = BasicDmg_00_2();
  139 | case TOKUSEI_YOBIMIZU: bQuit = BasicDmg_00_2();
  140 | case TOKUSEI_MORAIBI: bQuit = BasicDmg_00_3();
  141 | case TOKUSEI_HUSIGINAMAMORI: bQuit = BasicDmg_00_4();
  142 | case TOKUSEI_HUYUU: bQuit = BasicDmg_00_5();
  143 | case TOKUSEI_KANSOUHADA: bQuit = BasicDmg_00_2();
  144 | case TOKUSEI_SOUSYOKU: bQuit = BasicDmg_00_7();
  145 | }
  149 | if( bQuit ){
  150 | return 0;
  151 | }
  152 | return 1;
  153 | }
```

### `BasicDmg_00_1()` (source lines 156–164)

```text
  156 | BasicDmg_00_1()
  157 | {
  158 | if( AI_CMD(CMD_CHECK_TYPE, CHECK_WAZA) == POKETYPE_DENKI ){
  160 | SCORE += -12;
  161 | return 1;
  162 | }
  163 | return 0;
  164 | }
```

### `BasicDmg_00_2()` (source lines 166–175)

```text
  166 | BasicDmg_00_2()
  167 | {
  169 | if( AI_CMD(CMD_CHECK_TYPE, CHECK_WAZA) == POKETYPE_MIZU ){
  171 | SCORE += -12;
  172 | return 1;
  173 | }
  174 | return 0;
  175 | }
```

### `BasicDmg_00_3()` (source lines 177–185)

```text
  177 | BasicDmg_00_3()
  178 | {
  179 | if( AI_CMD(CMD_CHECK_TYPE, CHECK_WAZA) == POKETYPE_HONOO ){
  181 | SCORE += -12;
  182 | return 1;
  183 | }
  184 | return 0;
  185 | }
```

### `BasicDmg_00_4()` (source lines 187–198)

```text
  187 | BasicDmg_00_4()
  188 | {
  189 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_2BAI)){
  190 | return 0;
  191 | }
  192 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_4BAI)){
  193 | return 0;
  194 | }
  196 | SCORE += -10;
  197 | return 1;
  198 | }
```

### `BasicDmg_00_5()` (source lines 200–211)

```text
  200 | BasicDmg_00_5()
  201 | {
  202 | if( AI_CMD(CMD_CHECK_TYPE, CHECK_WAZA) == POKETYPE_JIMEN ){
  203 | if( AI_CMD(CMD_FLDEFF_CHECK, EFF_JURYOKU)){
  204 | return 0;
  205 | }
  207 | SCORE += -10;
  208 | return 1;
  209 | }
  210 | return 0;
  211 | }
```

### `BasicDmg_00_7()` (source lines 213–221)

```text
  213 | BasicDmg_00_7()
  214 | {
  215 | if( AI_CMD(CMD_CHECK_TYPE, CHECK_WAZA) == POKETYPE_KUSA ){
  217 | SCORE += -12;
  218 | return 1;
  219 | }
  220 | return 0;
  221 | }
```

### `Calc_BasicAll()` (source lines 227–423)

```text
  227 | Calc_BasicAll( )
  228 | {
  230 | if( Bouon_Check() == 1 ){
  231 | return ;
  232 | }
  234 | if( Boudan_Check() == 1 ){
  235 | return ;
  236 | }
  238 | waza_seq_no = AI_CMD(CMD_CHECK_WORKWAZA_SEQNO);
  240 | switch( waza_seq_no )
  241 | {
  242 | case 1: BaciAI_Seq_001();
  243 | case 7: BaciAI_Seq_007();
  244 | case 8: BaciAI_Seq_008();
  245 | case 10: BaciAI_Seq_010();
  246 | case 11: BaciAI_Seq_011();
  247 | case 12: BaciAI_Seq_012();
  248 | case 13: BaciAI_Seq_013();
  249 | case 14: BaciAI_Seq_014();
  250 | case 15: BaciAI_Seq_015();
  251 | case 16: BaciAI_Seq_016();
  252 | case 18: BaciAI_Seq_018();
  253 | case 19: BaciAI_Seq_019();
  254 | case 20: BaciAI_Seq_020();
  255 | case 21: BaciAI_Seq_021();
  256 | case 22: BaciAI_Seq_022();
  257 | case 23: BaciAI_Seq_023();
  258 | case 24: BaciAI_Seq_024();
  259 | case 25: BaciAI_Seq_025();
  260 | case 28: BaciAI_Seq_028();
  261 | case 32: BaciAI_Seq_032();
  262 | case 33: BaciAI_Seq_033();
  263 | case 35: BaciAI_Seq_035();
  264 | case 37: BaciAI_Seq_037();
  265 | case 38: BaciAI_Seq_038();
  266 | case 46: BaciAI_Seq_046();
  267 | case 47: BaciAI_Seq_047();
  268 | case 49: BaciAI_Seq_049();
  269 | case 50: BaciAI_Seq_010();
  270 | case 51: BaciAI_Seq_011();
  271 | case 52: BaciAI_Seq_012();
  272 | case 53: BaciAI_Seq_013();
  273 | case 54: BaciAI_Seq_014();
  274 | case 55: BaciAI_Seq_015();
  275 | case 56: BaciAI_Seq_016();
  276 | case 58: BaciAI_Seq_018();
  277 | case 59: BaciAI_Seq_019();
  278 | case 60: BaciAI_Seq_020();
  279 | case 61: BaciAI_Seq_021();
  280 | case 62: BaciAI_Seq_022();
  281 | case 63: BaciAI_Seq_023();
  282 | case 64: BaciAI_Seq_024();
  283 | case 65: BaciAI_Seq_065();
  284 | case 66: BaciAI_Seq_033();
  285 | case 67: BaciAI_Seq_067();
  286 | case 79: BaciAI_Seq_079();
  287 | case 84: BaciAI_Seq_084();
  288 | case 86: BaciAI_Seq_086();
  289 | case 90: BaciAI_Seq_090();
  290 | case 92: BaciAI_Seq_092();
  291 | case 94: BaciAI_Seq_094();
  292 | case 97: BaciAI_Seq_092();
  293 | case 102: BaciAI_Seq_102();
  294 | case 106: BaciAI_Seq_106();
  295 | case 107: BaciAI_Seq_107();
  296 | case 108: BaciAI_Seq_016();
  297 | case 109: BaciAI_Seq_109();
  298 | case 112: BaciAI_Seq_112();
  299 | case 113: BaciAI_Seq_113();
  300 | case 114: BaciAI_Seq_114();
  301 | case 115: BaciAI_Seq_115();
  302 | case 118: BaciAI_Seq_049();
  303 | case 120: BaciAI_Seq_120();
  304 | case 124: BaciAI_Seq_124();
  305 | case 127: BaciAI_Seq_127();
  306 | case 132: BaciAI_Seq_132();
  307 | case 133: BaciAI_Seq_132();
  308 | case 134: BaciAI_Seq_132();
  309 | case 136: BaciAI_Seq_136();
  310 | case 137: BaciAI_Seq_137();
  311 | case 142: BaciAI_Seq_142();
  312 | case 143: BaciAI_Seq_025();
  313 | case 148: BaciAI_Seq_148();
  314 | case 156: BaciAI_Seq_011();
  315 | case 157: BaciAI_Seq_132();
  316 | case 158: BaciAI_Seq_158();
  317 | case 160: BaciAI_Seq_160();
  318 | case 161: BaciAI_Seq_161();
  319 | case 162: BaciAI_Seq_161();
  320 | case 164: BaciAI_Seq_164();
  321 | case 165: BaciAI_Seq_165();
  322 | case 166: BaciAI_Seq_049();
  323 | case 167: BaciAI_Seq_167();
  324 | case 168: BaciAI_Seq_168();
  325 | case 172: BaciAI_Seq_172();
  326 | case 175: BaciAI_Seq_175();
  327 | case 176: BaciAI_Seq_176();
  328 | case 177: BaciAI_Seq_177();
  329 | case 178: BaciAI_Seq_178();
  330 | case 179: BaciAI_Seq_179();
  331 | case 181: BaciAI_Seq_181();
  332 | case 184: BaciAI_Seq_184();
  333 | case 187: BaciAI_Seq_001();
  334 | case 188: BaciAI_Seq_188();
  335 | case 191: BaciAI_Seq_191();
  336 | case 192: BaciAI_Seq_192();
  337 | case 193: BaciAI_Seq_193();
  338 | case 201: BaciAI_Seq_201();
  339 | case 205: BaciAI_Seq_205();
  340 | case 206: BaciAI_Seq_206();
  341 | case 208: BaciAI_Seq_208();
  342 | case 210: BaciAI_Seq_210();
  343 | case 211: BaciAI_Seq_211();
  344 | case 212: BaciAI_Seq_212();
  345 | case 215: BaciAI_Seq_215();
  346 | case 216: BaciAI_Seq_216();
  347 | case 220: BaciAI_Seq_220();
  348 | case 222: BaciAI_Seq_222();
  349 | case 225: BaciAI_Seq_225();
  350 | case 226: BaciAI_Seq_226();
  351 | case 227: BaciAI_Seq_227();
  352 | case 232: BaciAI_Seq_232();
  353 | case 233: BaciAI_Seq_233();
  354 | case 234: BaciAI_Seq_234();
  355 | case 236: BaciAI_Seq_236();
  356 | case 238: BaciAI_Seq_238();
  357 | case 239: BaciAI_Seq_239();
  358 | case 240: BaciAI_Seq_240();
  359 | case 241: BaciAI_Seq_241();
  360 | case 242: BaciAI_Seq_242();
  361 | case 243: BaciAI_Seq_243();
  362 | case 244: BaciAI_Seq_244();
  363 | case 246: BaciAI_Seq_246();
  364 | case 247: BaciAI_Seq_247();
  365 | case 249: BaciAI_Seq_249();
  366 | case 251: BaciAI_Seq_251();
  367 | case 252: BaciAI_Seq_252();
  368 | case 258: BaciAI_Seq_258();
  369 | case 259: BaciAI_Seq_259();
  370 | case 265: BaciAI_Seq_265();
  371 | case 266: BaciAI_Seq_266();
  372 | case 270: BaciAI_Seq_270();
  373 | case 277: BaciAI_Seq_010();
  374 | case 278: BaciAI_Seq_278();
  375 | case 281: BaciAI_Seq_281();
  376 | case 284: BaciAI_Seq_012();
  377 | case 285: BaciAI_Seq_285();
  378 | case 286: BaciAI_Seq_286();
  379 | case 290: BaciAI_Seq_013();
  380 | case 292: BaciAI_Seq_292();
  381 | case 294: BaciAI_Seq_294();
  382 | case 298: BaciAI_Seq_298();
  383 | case 299: BaciAI_Seq_299();
  384 | case 300: BaciAI_Seq_300();
  385 | case 301: BaciAI_Seq_301();
  386 | case 307: BaciAI_Seq_307();
  387 | case 308: BaciAI_Seq_010();
  388 | case 309: BaciAI_Seq_309();
  389 | case 311: BaciAI_Seq_311();
  390 | case 312: BaciAI_Seq_010();
  391 | case 315: BaciAI_Seq_315();
  392 | case 316: BaciAI_Seq_010();
  393 | case 318: BaciAI_Seq_318();
  394 | case 320: BaciAI_Seq_320();
  395 | case 321: BaciAI_Seq_013();
  396 | case 322: BaciAI_Seq_010();
  397 | case 323: BaciAI_Seq_323();
  398 | case 327: BaciAI_Seq_010();
  399 | case 328: BaciAI_Seq_011();
  400 | case 338: BaciAI_Seq_338();
  401 | case 339: BaciAI_Seq_339();
  402 | case 340: BaciAI_Seq_340();
  403 | case 342: BaciAI_Seq_342();
  404 | case 343: BaciAI_Seq_018();
  405 | case 346: BaciAI_Seq_018();
  406 | case 349: BaciAI_Seq_349();
  407 | case 350: BaciAI_Seq_350();
  408 | case 351: BaciAI_Seq_351();
  409 | case 352: BaciAI_Seq_352();
  410 | case 354: BaciAI_Seq_354();
  411 | case 356: BaciAI_Seq_018();
  412 | case 357: BaciAI_Seq_021();
  413 | case 362: BaciAI_Seq_362();
  414 | case 363: BaciAI_Seq_363();
  415 | case 364: BaciAI_Seq_018();
  416 | case 365: BaciAI_Seq_013();
  417 | case 366: BaciAI_Seq_366();
  418 | case 368: BaciAI_Seq_368();
  419 | case 370: BaciAI_Seq_370();
  420 | case 375: BaciAI_Seq_375();
  421 | case 376: BaciAI_Seq_158();
  422 | }
  423 | }
```

### `Bouon_Check()` (source lines 426–462)

```text
  426 | Bouon_Check()
  427 | {
  428 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_BOUON )
  429 | {
  431 | tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
  432 | if(tokusei != TOKUSEI_KATAYABURI
  433 | && tokusei != TOKUSEI_TAABOBUREIZU
  434 | && tokusei != TOKUSEI_TERABORUTEEZI)
  435 | {
  437 | MyWazaNo = CURRENT_MOVE();
  439 | if( MyWazaNo == WAZANO_NAKIGOE
  440 | || MyWazaNo == WAZANO_HOERU
  441 | || MyWazaNo == WAZANO_UTAU
  442 | || MyWazaNo == WAZANO_TYOUONPA
  443 | || MyWazaNo == WAZANO_IYANAOTO
  444 | || MyWazaNo == WAZANO_IBIKI
  445 | || MyWazaNo == WAZANO_SAWAGU
  446 | || MyWazaNo == WAZANO_KINZOKUON
  447 | || MyWazaNo == WAZANO_KUSABUE
  448 | || MyWazaNo == WAZANO_MUSINOSAZAMEKI
  449 | || MyWazaNo == WAZANO_OSYABERI
  450 | || MyWazaNo == WAZANO_RINSYOU
  451 | || MyWazaNo == WAZANO_EKOOBOISU
  452 | || MyWazaNo == WAZANO_INISIENOUTA
  453 | || MyWazaNo == WAZANO_BAAKUAUTO
  454 | ){
  456 | SCORE += -10;
  457 | return 1
  458 | }
  459 | }
  460 | }
  461 | return 0
  462 | }
```

### `Boudan_Check()` (source lines 465–502)

```text
  465 | Boudan_Check()
  466 | {
  467 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_BOUDAN )
  468 | {
  470 | tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
  471 | if(tokusei != TOKUSEI_KATAYABURI
  472 | && tokusei != TOKUSEI_TAABOBUREIZU
  473 | && tokusei != TOKUSEI_TERABORUTEEZI)
  474 | {
  476 | MyWazaNo = CURRENT_MOVE();
  478 | if( MyWazaNo == WAZANO_TAMANAGE
  479 | || MyWazaNo == WAZANO_KIAIDAMA
  480 | || MyWazaNo == WAZANO_SYADOOBOORU
  481 | || MyWazaNo == WAZANO_MISUTOBOORU
  482 | || MyWazaNo == WAZANO_AISUBOORU
  483 | || MyWazaNo == WAZANO_WHEZAABOORU
  484 | || MyWazaNo == WAZANO_ZYAIROBOORU
  485 | || MyWazaNo == WAZANO_ENAZIIBOORU
  486 | || MyWazaNo == WAZANO_EREKIBOORU
  487 | || MyWazaNo == WAZANO_TAMAGOBAKUDAN
  488 | || MyWazaNo == WAZANO_HEDOROBAKUDAN
  489 | || MyWazaNo == WAZANO_TANEBAKUDAN
  490 | || MyWazaNo == WAZANO_DOROBAKUDAN
  491 | || MyWazaNo == WAZANO_AKUUSETUDAN
  492 | || MyWazaNo == WAZANO_KAENDAN
  493 | || MyWazaNo == WAZANO_HADOUDAN
  494 | ){
  496 | SCORE += -10;
  497 | return 1
  498 | }
  499 | }
  500 | }
  501 | return 0
  502 | }
```

### `BaciAI_Seq_001()` (source lines 505–593)

```text
  505 | BaciAI_Seq_001()
  506 | {
  509 | if( AI_CMD(CMD_IF_POKESICK, CHECK_DEFENCE) ){
  511 | SCORE += -10;
  512 | return;
  513 | }
  515 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_DEFENCE) == BTL_SIDEEFF_SINPINOMAMORI ){
  517 | SCORE += -10;
  518 | return;
  519 | }
  520 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
  521 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
  522 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
  524 | SCORE += -10;
  525 | return;
  526 | }
  527 | }
  528 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
  529 | DEF_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1);
  530 | DEF_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2);
  531 | if( AI_CMD(CMD_IF_EXIST_GROUND, BTL_GROUND_ELEKI) ){
  532 | if( DEF_tokusei != TOKUSEI_HUYUU
  533 | && DEF_type1 != POKETYPE_HIKOU
  534 | && DEF_type2 != POKETYPE_HIKOU){
  536 | SCORE += -10;
  537 | return;
  538 | }
  539 | }
  540 | if( AI_CMD(CMD_IF_EXIST_GROUND, BTL_GROUND_MIST) ){
  541 | if( DEF_tokusei != TOKUSEI_HUYUU
  542 | && DEF_type1 != POKETYPE_HIKOU
  543 | && DEF_type2 != POKETYPE_HIKOU){
  545 | SCORE += -10;
  546 | return;
  547 | }
  548 | }
  549 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
  550 | if(ATK_tokusei != TOKUSEI_KATAYABURI
  551 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
  552 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
  553 | {
  555 | if( DEF_tokusei == TOKUSEI_HUMIN
  556 | || DEF_tokusei == TOKUSEI_YARUKI
  557 | || DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
  558 | ){
  560 | SCORE += -10;
  561 | return;
  562 | }
  563 | else if(DEF_type1 == POKETYPE_KUSA
  564 | || DEF_type2 == POKETYPE_KUSA ){
  565 | if( DEF_tokusei == TOKUSEI_HURAWAABEERU){
  567 | SCORE += -10;
  568 | return;
  569 | }
  570 | if( CHK_rule == BTL_RULE_DOUBLE
  571 | || CHK_rule == BTL_RULE_TRIPLE){
  572 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_HURAWAABEERU){
  574 | SCORE += -10;
  575 | return;
  576 | }
  577 | }
  578 | }
  579 | else if( DEF_tokusei == TOKUSEI_SUIITOBEERU){
  581 | SCORE += -10;
  582 | return;
  583 | }
  584 | else if( CHK_rule == BTL_RULE_DOUBLE
  585 | || CHK_rule == BTL_RULE_TRIPLE){
  586 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_SUIITOBEERU){
  588 | SCORE += -10;
  589 | return;
  590 | }
  591 | }
  592 | }
  593 | }
```

### `BaciAI_Seq_007()` (source lines 596–626)

```text
  596 | BaciAI_Seq_007()
  597 | {
  600 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)){
  602 | SCORE += -10;
  603 | return;
  604 | }
  606 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) != TOKUSEI_KATAYABURI )
  607 | {
  608 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_SIMERIKE )
  609 | {
  611 | SCORE += -10;
  612 | return;
  613 | }
  614 | }
  616 | if( AI_CMD(CMD_CHECK_BTL_RULE) == BTL_RULE_SINGLE ){
  617 | if( AI_CMD(CMD_CHECK_BENCH_COUNT, CHECK_ATTACK) == 0 ){
  618 | if( AI_CMD(CMD_CHECK_BENCH_COUNT, CHECK_DEFENCE) != 0 ){
  620 | SCORE += -10;
  621 | }else{
  622 | SCORE += -1;
  623 | }
  624 | }
  625 | }
  626 | }
```

### `BaciAI_Seq_008()` (source lines 629–644)

```text
  629 | BaciAI_Seq_008()
  630 | {
  633 | if( AI_CMD(CMD_IFN_WAZASICK, CHECK_DEFENCE, WAZASICK_NEMURI) ){
  635 | SCORE += -10;
  636 | return;
  637 | }
  639 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_MAZIKKUGAADO )
  640 | {
  642 | SCORE += -10;
  643 | }
  644 | }
```

### `BaciAI_Seq_010()` (source lines 647–661)

```text
  647 | BaciAI_Seq_010()
  648 | {
  650 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_AMANOZYAKU){
  652 | SCORE += -12;
  653 | return;
  654 | }
  656 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_POW, 12) )
  657 | {
  659 | SCORE += -10;
  660 | }
  661 | }
```

### `BaciAI_Seq_011()` (source lines 663–677)

```text
  663 | BaciAI_Seq_011()
  664 | {
  666 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_AMANOZYAKU){
  668 | SCORE += -12;
  669 | return;
  670 | }
  672 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_DEF, 12) )
  673 | {
  675 | SCORE += -10;
  676 | }
  677 | }
```

### `BaciAI_Seq_012()` (source lines 679–700)

```text
  679 | BaciAI_Seq_012()
  680 | {
  682 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_AMANOZYAKU){
  684 | SCORE += -12;
  685 | return;
  686 | }
  688 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_AGI, 12) )
  689 | {
  691 | SCORE += -10;
  692 | return;
  693 | }
  695 | if( AI_CMD(CMD_FLDEFF_CHECK) == EFF_TRICKROOM)
  696 | {
  698 | SCORE += -5;
  699 | }
  700 | }
```

### `BaciAI_Seq_013()` (source lines 702–716)

```text
  702 | BaciAI_Seq_013()
  703 | {
  705 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_AMANOZYAKU){
  707 | SCORE += -12;
  708 | return;
  709 | }
  711 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_SPEPOW, 12) )
  712 | {
  714 | SCORE += -10;
  715 | }
  716 | }
```

### `BaciAI_Seq_014()` (source lines 718–732)

```text
  718 | BaciAI_Seq_014()
  719 | {
  721 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_AMANOZYAKU){
  723 | SCORE += -12;
  724 | return;
  725 | }
  727 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_SPEDEF, 12) )
  728 | {
  730 | SCORE += -10;
  731 | }
  732 | }
```

### `BaciAI_Seq_015()` (source lines 734–762)

```text
  734 | BaciAI_Seq_015()
  735 | {
  737 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_AMANOZYAKU){
  739 | SCORE += -12;
  740 | return;
  741 | }
  743 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_NOOGAADO)
  744 | {
  746 | SCORE += -10;
  747 | return;
  748 | }
  750 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_NOOGAADO)
  751 | {
  753 | SCORE += -10;
  754 | return;
  755 | }
  757 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_HIT, 12) )
  758 | {
  760 | SCORE += -10;
  761 | }
  762 | }
```

### `BaciAI_Seq_016()` (source lines 764–792)

```text
  764 | BaciAI_Seq_016()
  765 | {
  767 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_AMANOZYAKU){
  769 | SCORE += -12;
  770 | return;
  771 | }
  773 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_NOOGAADO)
  774 | {
  776 | SCORE += -10;
  777 | return;
  778 | }
  780 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_NOOGAADO)
  781 | {
  783 | SCORE += -10;
  784 | return;
  785 | }
  787 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_AVOID, 12) )
  788 | {
  790 | SCORE += -10;
  791 | }
  792 | }
```

### `BaciAI_Seq_018()` (source lines 794–856)

```text
  794 | BaciAI_Seq_018()
  795 | {
  798 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_DEFENCE, PARA_POW, 0) )
  799 | {
  801 | SCORE += -10;
  802 | }
  804 | tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
  805 | if( tokusei == TOKUSEI_MAKENKI
  806 | || tokusei == TOKUSEI_KATIKI
  807 | ){
  809 | SCORE += -12;
  810 | }
  811 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
  812 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
  813 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
  815 | SCORE += -10;
  816 | return;
  817 | }
  818 | }
  821 | if(ATK_tokusei != TOKUSEI_KATAYABURI
  822 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
  823 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
  824 | {
  825 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
  826 | if( DEF_tokusei == TOKUSEI_KAIRIKIBASAMI
  827 | || DEF_tokusei == TOKUSEI_KURIABODHI
  828 | || DEF_tokusei == TOKUSEI_SIROIKEMURI
  829 | ){
  831 | SCORE += -10;
  832 | }
  833 | else if( DEF_tokusei == TOKUSEI_AMANOZYAKU
  834 | || DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
  835 | ){
  837 | SCORE += -12;
  838 | }
  839 | else if(AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) == POKETYPE_KUSA
  840 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) == POKETYPE_KUSA ){
  841 | if( DEF_tokusei == TOKUSEI_HURAWAABEERU){
  843 | SCORE += -10;
  844 | return;
  845 | }
  846 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
  847 | if( CHK_rule == BTL_RULE_DOUBLE
  848 | || CHK_rule == BTL_RULE_TRIPLE){
  849 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_HURAWAABEERU){
  851 | SCORE += -10;
  852 | }
  853 | }
  854 | }
  855 | }
  856 | }
```

### `BaciAI_Seq_019()` (source lines 858–920)

```text
  858 | BaciAI_Seq_019()
  859 | {
  862 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_DEF, 0) )
  863 | {
  865 | SCORE += -10;
  866 | }
  868 | tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
  869 | if( tokusei == TOKUSEI_MAKENKI
  870 | || tokusei == TOKUSEI_KATIKI
  871 | ){
  873 | SCORE += -12;
  874 | }
  875 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
  876 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
  877 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
  879 | SCORE += -10;
  880 | return;
  881 | }
  882 | }
  885 | if(ATK_tokusei != TOKUSEI_KATAYABURI
  886 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
  887 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
  888 | {
  889 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
  890 | if( DEF_tokusei == TOKUSEI_HATOMUNE
  891 | || DEF_tokusei == TOKUSEI_KURIABODHI
  892 | || DEF_tokusei == TOKUSEI_SIROIKEMURI
  893 | ){
  895 | SCORE += -10;
  896 | }
  897 | else if( DEF_tokusei == TOKUSEI_AMANOZYAKU
  898 | || DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
  899 | ){
  901 | SCORE += -12;
  902 | }
  903 | else if(AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) == POKETYPE_KUSA
  904 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) == POKETYPE_KUSA ){
  905 | if( DEF_tokusei == TOKUSEI_HURAWAABEERU){
  907 | SCORE += -10;
  908 | return;
  909 | }
  910 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
  911 | if( CHK_rule == BTL_RULE_DOUBLE
  912 | || CHK_rule == BTL_RULE_TRIPLE){
  913 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_HURAWAABEERU){
  915 | SCORE += -10;
  916 | }
  917 | }
  918 | }
  919 | }
  920 | }
```

### `BaciAI_Seq_020()` (source lines 922–983)

```text
  922 | BaciAI_Seq_020()
  923 | {
  926 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_AGI, 0) )
  927 | {
  929 | SCORE += -10;
  930 | }
  932 | tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
  933 | if( tokusei == TOKUSEI_MAKENKI
  934 | || tokusei == TOKUSEI_KATIKI
  935 | ){
  937 | SCORE += -8;
  938 | }
  939 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
  940 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
  941 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
  943 | SCORE += -10;
  944 | return;
  945 | }
  946 | }
  949 | if(ATK_tokusei != TOKUSEI_KATAYABURI
  950 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
  951 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
  952 | {
  953 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
  954 | if( DEF_tokusei == TOKUSEI_KURIABODHI
  955 | || DEF_tokusei == TOKUSEI_SIROIKEMURI
  956 | ){
  958 | SCORE += -10;
  959 | }
  960 | else if( DEF_tokusei == TOKUSEI_AMANOZYAKU
  961 | || DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
  962 | ){
  964 | SCORE += -12;
  965 | }
  966 | else if(AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) == POKETYPE_KUSA
  967 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) == POKETYPE_KUSA ){
  968 | if( DEF_tokusei == TOKUSEI_HURAWAABEERU){
  970 | SCORE += -10;
  971 | return;
  972 | }
  973 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
  974 | if( CHK_rule == BTL_RULE_DOUBLE
  975 | || CHK_rule == BTL_RULE_TRIPLE){
  976 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_HURAWAABEERU){
  978 | SCORE += -10;
  979 | }
  980 | }
  981 | }
  982 | }
  983 | }
```

### `BaciAI_Seq_021()` (source lines 985–1046)

```text
  985 | BaciAI_Seq_021()
  986 | {
  989 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_SPEPOW, 0) )
  990 | {
  992 | SCORE += -10;
  993 | }
  995 | tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
  996 | if( tokusei == TOKUSEI_MAKENKI
  997 | || tokusei == TOKUSEI_KATIKI
  998 | ){
 1000 | SCORE += -8;
 1001 | }
 1002 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1003 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 1004 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 1006 | SCORE += -10;
 1007 | return;
 1008 | }
 1009 | }
 1012 | if(ATK_tokusei != TOKUSEI_KATAYABURI
 1013 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 1014 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 1015 | {
 1016 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 1017 | if( DEF_tokusei == TOKUSEI_KURIABODHI
 1018 | || DEF_tokusei == TOKUSEI_SIROIKEMURI
 1019 | ){
 1021 | SCORE += -10;
 1022 | }
 1023 | else if( DEF_tokusei == TOKUSEI_AMANOZYAKU
 1024 | || DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 1025 | ){
 1027 | SCORE += -12;
 1028 | }
 1029 | else if(AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) == POKETYPE_KUSA
 1030 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) == POKETYPE_KUSA ){
 1031 | if( DEF_tokusei == TOKUSEI_HURAWAABEERU){
 1033 | SCORE += -10;
 1034 | return;
 1035 | }
 1036 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 1037 | if( CHK_rule == BTL_RULE_DOUBLE
 1038 | || CHK_rule == BTL_RULE_TRIPLE){
 1039 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_HURAWAABEERU){
 1041 | SCORE += -10;
 1042 | }
 1043 | }
 1044 | }
 1045 | }
 1046 | }
```

### `BaciAI_Seq_022()` (source lines 1048–1109)

```text
 1048 | BaciAI_Seq_022()
 1049 | {
 1052 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_SPEDEF, 0) )
 1053 | {
 1055 | SCORE += -10;
 1056 | }
 1058 | tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 1059 | if( tokusei == TOKUSEI_MAKENKI
 1060 | || tokusei == TOKUSEI_KATIKI
 1061 | ){
 1063 | SCORE += -8;
 1064 | }
 1065 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1066 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 1067 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 1069 | SCORE += -10;
 1070 | return;
 1071 | }
 1072 | }
 1075 | if(ATK_tokusei != TOKUSEI_KATAYABURI
 1076 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 1077 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 1078 | {
 1079 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 1080 | if( DEF_tokusei == TOKUSEI_KURIABODHI
 1081 | || DEF_tokusei == TOKUSEI_SIROIKEMURI
 1082 | ){
 1084 | SCORE += -10;
 1085 | }
 1086 | else if( DEF_tokusei == TOKUSEI_AMANOZYAKU
 1087 | || DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 1088 | ){
 1090 | SCORE += -12;
 1091 | }
 1092 | else if(AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) == POKETYPE_KUSA
 1093 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) == POKETYPE_KUSA ){
 1094 | if( DEF_tokusei == TOKUSEI_HURAWAABEERU){
 1096 | SCORE += -10;
 1097 | return;
 1098 | }
 1099 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 1100 | if( CHK_rule == BTL_RULE_DOUBLE
 1101 | || CHK_rule == BTL_RULE_TRIPLE){
 1102 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_HURAWAABEERU){
 1104 | SCORE += -10;
 1105 | }
 1106 | }
 1107 | }
 1108 | }
 1109 | }
```

### `BaciAI_Seq_023()` (source lines 1111–1178)

```text
 1111 | BaciAI_Seq_023()
 1112 | {
 1115 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_HIT, 0) )
 1116 | {
 1118 | SCORE += -10;
 1119 | }
 1121 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 1122 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1123 | if( DEF_tokusei == TOKUSEI_MAKENKI
 1124 | || DEF_tokusei == TOKUSEI_KATIKI
 1125 | ){
 1127 | SCORE += -8;
 1128 | }
 1129 | else if( DEF_tokusei == TOKUSEI_NOOGAADO
 1130 | || ATK_tokusei == TOKUSEI_NOOGAADO
 1131 | ){
 1133 | SCORE += -10;
 1134 | }
 1135 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 1136 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 1138 | SCORE += -10;
 1139 | return;
 1140 | }
 1141 | }
 1144 | if(ATK_tokusei != TOKUSEI_KATAYABURI
 1145 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 1146 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 1147 | {
 1148 | if( DEF_tokusei == TOKUSEI_KURIABODHI
 1149 | || DEF_tokusei == TOKUSEI_SIROIKEMURI
 1150 | || DEF_tokusei == TOKUSEI_SURUDOIME
 1151 | ){
 1153 | SCORE += -10;
 1154 | }
 1155 | else if( DEF_tokusei == TOKUSEI_AMANOZYAKU
 1156 | || DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 1157 | ){
 1159 | SCORE += -12;
 1160 | }
 1161 | else if(AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) == POKETYPE_KUSA
 1162 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) == POKETYPE_KUSA ){
 1163 | if( DEF_tokusei == TOKUSEI_HURAWAABEERU){
 1165 | SCORE += -10;
 1166 | return;
 1167 | }
 1168 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 1169 | if( CHK_rule == BTL_RULE_DOUBLE
 1170 | || CHK_rule == BTL_RULE_TRIPLE){
 1171 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_HURAWAABEERU){
 1173 | SCORE += -10;
 1174 | }
 1175 | }
 1176 | }
 1177 | }
 1178 | }
```

### `BaciAI_Seq_024()` (source lines 1180–1246)

```text
 1180 | BaciAI_Seq_024()
 1181 | {
 1184 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_DEFENCE, PARA_AVOID, 0) )
 1185 | {
 1187 | SCORE += -10;
 1188 | }
 1190 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 1191 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1192 | if( DEF_tokusei == TOKUSEI_MAKENKI
 1193 | || DEF_tokusei == TOKUSEI_KATIKI
 1194 | ){
 1196 | SCORE += -8;
 1197 | }
 1198 | else if( DEF_tokusei == TOKUSEI_NOOGAADO
 1199 | || ATK_tokusei == TOKUSEI_NOOGAADO
 1200 | ){
 1202 | SCORE += -10;
 1203 | }
 1204 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 1205 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 1207 | SCORE += -10;
 1208 | return;
 1209 | }
 1210 | }
 1213 | if(ATK_tokusei != TOKUSEI_KATAYABURI
 1214 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 1215 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 1216 | {
 1217 | if( DEF_tokusei == TOKUSEI_KURIABODHI
 1218 | || DEF_tokusei == TOKUSEI_SIROIKEMURI
 1219 | ){
 1221 | SCORE += -10;
 1222 | }
 1223 | else if( DEF_tokusei == TOKUSEI_AMANOZYAKU
 1224 | || DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 1225 | ){
 1227 | SCORE += -12;
 1228 | }
 1229 | else if(AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) == POKETYPE_KUSA
 1230 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) == POKETYPE_KUSA ){
 1231 | if( DEF_tokusei == TOKUSEI_HURAWAABEERU){
 1233 | SCORE += -10;
 1234 | return;
 1235 | }
 1236 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 1237 | if( CHK_rule == BTL_RULE_DOUBLE
 1238 | || CHK_rule == BTL_RULE_TRIPLE){
 1239 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_HURAWAABEERU){
 1241 | SCORE += -10;
 1242 | }
 1243 | }
 1244 | }
 1245 | }
 1246 | }
```

### `BaciAI_Seq_025()` (source lines 1248–1308)

```text
 1248 | BaciAI_Seq_025()
 1249 | {
 1252 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_POW, 6)
 1253 | ){
 1254 | SCORE += -6;
 1255 | }
 1256 | else if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_DEF, 6)
 1257 | ){
 1258 | SCORE += -6;
 1259 | }
 1260 | else if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEPOW, 6)
 1261 | ){
 1262 | SCORE += -6;
 1263 | }
 1264 | else if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEDEF, 6)
 1265 | ){
 1266 | SCORE += -6;
 1267 | }
 1268 | else if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_AGI, 6)
 1269 | ){
 1270 | SCORE += -6;
 1271 | }
 1272 | else if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_HIT, 6)
 1273 | ){
 1274 | SCORE += -6;
 1275 | }
 1276 | else if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_AVOID, 6)
 1277 | ){
 1278 | SCORE += -6;
 1279 | }
 1280 | else if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_POW, 6)
 1281 | ){
 1282 | SCORE += -6;
 1283 | }
 1284 | else if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_DEF, 6)
 1285 | ){
 1286 | SCORE += -6;
 1287 | }
 1288 | else if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_SPEPOW, 6)
 1289 | ){
 1290 | SCORE += -6;
 1291 | }
 1292 | else if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_SPEDEF, 6)
 1293 | ){
 1294 | SCORE += -6;
 1295 | }
 1296 | else if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_AGI, 6)
 1297 | ){
 1298 | SCORE += -6;
 1299 | }
 1300 | else if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_HIT, 6)
 1301 | ){
 1302 | SCORE += -6;
 1303 | }
 1304 | else if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_AVOID, 6)
 1305 | ){
 1306 | SCORE += -6;
 1307 | }
 1308 | }
```

### `BaciAI_Seq_028()` (source lines 1310–1332)

```text
 1310 | BaciAI_Seq_028()
 1311 | {
 1313 | if( AI_CMD(CMD_CHECK_BENCH_COUNT, CHECK_DEFENCE) == 0){
 1315 | SCORE += -10;
 1316 | }
 1317 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 1318 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1321 | if(ATK_tokusei != TOKUSEI_KATAYABURI
 1322 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 1323 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 1324 | {
 1325 | if( DEF_tokusei == TOKUSEI_KYUUBAN
 1326 | || DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 1327 | ){
 1329 | SCORE += -10;
 1330 | }
 1331 | }
 1332 | }
```

### `BaciAI_Seq_037()` (source lines 1334–1356)

```text
 1334 | BaciAI_Seq_037()
 1335 | {
 1337 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_KAIHUKUHUUJI)){
 1339 | SCORE += -10;
 1340 | return;
 1341 | }
 1342 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1343 | ATK_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE1);
 1344 | ATK_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE2);
 1345 | if( AI_CMD(CMD_IF_EXIST_GROUND, BTL_GROUND_ELEKI)
 1346 | || AI_CMD(CMD_IF_EXIST_GROUND, BTL_GROUND_MIST) ){
 1347 | if( ATK_tokusei != TOKUSEI_HUYUU
 1348 | && ATK_type1 != POKETYPE_HIKOU
 1349 | && ATK_type2 != POKETYPE_HIKOU){
 1351 | SCORE += -10;
 1352 | return;
 1353 | }
 1354 | }
 1355 | BaciAI_Seq_032()
 1356 | }
```

### `BaciAI_Seq_032()` (source lines 1358–1366)

```text
 1358 | BaciAI_Seq_032()
 1359 | {
 1361 | if( AI_CMD(CMD_IF_HP_EQUAL, CHECK_ATTACK, 100)
 1362 | ){
 1364 | SCORE += -8;
 1365 | }
 1366 | }
```

### `BaciAI_Seq_033()` (source lines 1368–1469)

```text
 1368 | BaciAI_Seq_033()
 1369 | {
 1371 | DEF_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1);
 1372 | DEF_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2);
 1373 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 1374 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1375 | CHK_weather = AI_CMD(CMD_CHECK_WEATHER);
 1376 | if( DEF_tokusei == TOKUSEI_POIZUNHIIRU
 1377 | ){
 1379 | SCORE += -12;
 1380 | return;
 1381 | }
 1382 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 1383 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 1385 | SCORE += -10;
 1386 | return;
 1387 | }
 1388 | }
 1390 | if(ATK_tokusei != TOKUSEI_KATAYABURI
 1391 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 1392 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 1393 | {
 1394 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 1395 | ){
 1397 | SCORE += -12;
 1398 | return;
 1399 | }
 1400 | if( DEF_tokusei == TOKUSEI_MENEKI
 1401 | ){
 1403 | SCORE += -10;
 1404 | return;
 1405 | }
 1406 | if( CHK_weather == WEATHER_HARE
 1407 | ){
 1408 | if( DEF_tokusei == TOKUSEI_RIIHUGAADO
 1409 | ){
 1411 | SCORE += -10;
 1412 | return;
 1413 | }
 1414 | }
 1415 | if(AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) == POKETYPE_KUSA
 1416 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) == POKETYPE_KUSA ){
 1417 | if( DEF_tokusei == TOKUSEI_HURAWAABEERU){
 1419 | SCORE += -10;
 1420 | return;
 1421 | }
 1422 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 1423 | if( CHK_rule == BTL_RULE_DOUBLE
 1424 | || CHK_rule == BTL_RULE_TRIPLE){
 1425 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_HURAWAABEERU){
 1427 | SCORE += -10;
 1428 | return;
 1429 | }
 1430 | }
 1431 | }
 1432 | }
 1433 | if(DEF_type1 == POKETYPE_HAGANE
 1434 | || DEF_type1 == POKETYPE_DOKU
 1435 | || DEF_type2 == POKETYPE_HAGANE
 1436 | || DEF_type2 == POKETYPE_DOKU
 1437 | ){
 1439 | SCORE += -10;
 1440 | return;
 1441 | }
 1442 | if( DEF_tokusei == TOKUSEI_MAZIKKUGAADO
 1443 | ){
 1445 | SCORE += -10;
 1446 | return;
 1447 | }
 1448 | if( AI_CMD(CMD_IF_POKESICK, CHECK_DEFENCE)
 1449 | ){
 1451 | SCORE += -10;
 1452 | return;
 1453 | }
 1454 | if( AI_CMD(CMD_IF_EXIST_GROUND, BTL_GROUND_MIST) ){
 1455 | if( DEF_tokusei != TOKUSEI_HUYUU
 1456 | && DEF_type1 != POKETYPE_HIKOU
 1457 | && DEF_type2 != POKETYPE_HIKOU){
 1459 | SCORE += -10;
 1460 | return;
 1461 | }
 1462 | }
 1463 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_DEFENCE, BTL_SIDEEFF_SINPINOMAMORI)
 1464 | ){
 1466 | SCORE += -10;
 1467 | return;
 1468 | }
 1469 | }
```

### `BaciAI_Seq_035()` (source lines 1471–1479)

```text
 1471 | BaciAI_Seq_035()
 1472 | {
 1474 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_ATTACK, BTL_SIDEEFF_HIKARINOKABE)
 1475 | ){
 1477 | SCORE += -10;
 1478 | }
 1479 | }
```

### `BaciAI_Seq_038()` (source lines 1481–1503)

```text
 1481 | BaciAI_Seq_038()
 1482 | {
 1486 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1487 | if(ATK_tokusei != TOKUSEI_KATAYABURI
 1488 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 1489 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 1490 | {
 1491 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 1492 | if( DEF_tokusei == TOKUSEI_GANZYOU
 1493 | ){
 1495 | SCORE += -10;
 1496 | }
 1497 | }
 1498 | if( AI_CMD(CMD_IF_LEVEL, LEVEL_DEFENCE)
 1499 | ){
 1501 | SCORE += -10;
 1502 | }
 1503 | }
```

### `BaciAI_Seq_046()` (source lines 1505–1513)

```text
 1505 | BaciAI_Seq_046()
 1506 | {
 1508 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_ATTACK, BTL_SIDEEFF_SIROIKIRI)
 1509 | ){
 1511 | SCORE += -10;
 1512 | }
 1513 | }
```

### `BaciAI_Seq_047()` (source lines 1515–1523)

```text
 1515 | BaciAI_Seq_047()
 1516 | {
 1518 | if( AI_CMD(CMD_IF_CONTFLG, CHECK_ATTACK, CONTFLG_KIAIDAME)
 1519 | ){
 1521 | SCORE += -10;
 1522 | }
 1523 | }
```

### `BaciAI_Seq_049()` (source lines 1525–1564)

```text
 1525 | BaciAI_Seq_049()
 1526 | {
 1527 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1528 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 1530 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_DEFENCE, BTL_SIDEEFF_SINPINOMAMORI)
 1531 | ){
 1533 | SCORE += -10;
 1534 | }
 1535 | else if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_KONRAN)
 1536 | ){
 1538 | SCORE += -8;
 1539 | }
 1540 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 1541 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 1543 | SCORE += -10;
 1544 | return;
 1545 | }
 1546 | }
 1549 | else if(ATK_tokusei != TOKUSEI_KATAYABURI
 1550 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 1551 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI
 1552 | ){
 1553 | if( DEF_tokusei == TOKUSEI_MAIPEESU
 1554 | ){
 1556 | SCORE += -10;
 1557 | }
 1558 | else if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 1559 | ){
 1561 | SCORE += -12;
 1562 | }
 1563 | }
 1564 | }
```

### `BaciAI_Seq_065()` (source lines 1566–1574)

```text
 1566 | BaciAI_Seq_065()
 1567 | {
 1569 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_ATTACK, BTL_SIDEEFF_REFRECTOR)
 1570 | ){
 1572 | SCORE += -10;
 1573 | }
 1574 | }
```

### `BaciAI_Seq_067()` (source lines 1576–1672)

```text
 1576 | BaciAI_Seq_067()
 1577 | {
 1579 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1580 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 1581 | wazaNo = CURRENT_MOVE();
 1582 | DEF_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1);
 1583 | DEF_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2);
 1584 | CHK_weather = AI_CMD(CMD_CHECK_WEATHER);
 1585 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_DEFENCE, BTL_SIDEEFF_SINPINOMAMORI)
 1586 | ){
 1588 | SCORE += -10;
 1589 | }
 1590 | else if( AI_CMD(CMD_IF_POKESICK, CHECK_DEFENCE)
 1591 | ){
 1593 | SCORE += -10;
 1594 | }
 1595 | else if(DEF_type1 == POKETYPE_DENKI
 1596 | || DEF_type2 == POKETYPE_DENKI
 1597 | ){
 1599 | SCORE += -10;
 1600 | }
 1601 | else if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 1602 | ){
 1604 | SCORE += -10;
 1605 | }
 1607 | else if(ATK_tokusei != TOKUSEI_KATAYABURI
 1608 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 1609 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 1610 | {
 1611 | if( DEF_tokusei == TOKUSEI_ZYUUNAN
 1612 | ){
 1614 | SCORE += -10;
 1615 | return;
 1616 | }
 1617 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 1618 | ){
 1620 | SCORE += -12;
 1621 | return;
 1622 | }
 1623 | if(wazaNo == WAZANO_DENZIHA){
 1624 | if( DEF_tokusei == TOKUSEI_DENKIENZIN
 1625 | || DEF_tokusei == TOKUSEI_HIRAISIN
 1626 | || DEF_tokusei == TOKUSEI_TIKUDEN){
 1628 | SCORE += -10;
 1629 | return;
 1630 | }
 1631 | }
 1632 | if( CHK_weather == WEATHER_HARE){
 1633 | if( DEF_tokusei == TOKUSEI_RIIHUGAADO){
 1635 | SCORE += -10;
 1636 | }
 1637 | }
 1638 | if(AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) == POKETYPE_KUSA
 1639 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) == POKETYPE_KUSA ){
 1640 | if( DEF_tokusei == TOKUSEI_HURAWAABEERU){
 1642 | SCORE += -10;
 1643 | return;
 1644 | }
 1645 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 1646 | if( CHK_rule == BTL_RULE_DOUBLE
 1647 | || CHK_rule == BTL_RULE_TRIPLE){
 1648 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_HURAWAABEERU){
 1650 | SCORE += -10;
 1651 | return;
 1652 | }
 1653 | }
 1654 | }
 1655 | }
 1656 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 1657 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 1659 | SCORE += -10;
 1660 | return;
 1661 | }
 1662 | }
 1663 | if( AI_CMD(CMD_IF_EXIST_GROUND, BTL_GROUND_MIST) ){
 1664 | if( DEF_tokusei != TOKUSEI_HUYUU
 1665 | && DEF_type1 != POKETYPE_HIKOU
 1666 | && DEF_type2 != POKETYPE_HIKOU){
 1668 | SCORE += -10;
 1669 | return;
 1670 | }
 1671 | }
 1672 | }
```

### `BaciAI_Seq_079()` (source lines 1674–1687)

```text
 1674 | BaciAI_Seq_079()
 1675 | {
 1677 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_ATTACK)
 1678 | ){
 1680 | SCORE += -8;
 1681 | }
 1682 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 26)
 1683 | ){
 1685 | SCORE += -10;
 1686 | }
 1687 | }
```

### `BaciAI_Seq_084()` (source lines 1689–1730)

```text
 1689 | BaciAI_Seq_084()
 1690 | {
 1692 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1693 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 1694 | DEF_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1);
 1695 | DEF_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2);
 1696 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_YADORIGI)
 1697 | ){
 1699 | SCORE += -8;
 1700 | }
 1701 | else if(DEF_type1 == POKETYPE_KUSA
 1702 | || DEF_type2 == POKETYPE_KUSA
 1703 | ){
 1705 | SCORE += -10;
 1706 | }
 1708 | else if(ATK_tokusei != TOKUSEI_KATAYABURI
 1709 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 1710 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 1711 | {
 1712 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 1713 | ){
 1715 | SCORE += -12;
 1716 | }
 1717 | else if( DEF_tokusei == TOKUSEI_MAZIKKUGAADO
 1718 | ){
 1720 | SCORE += -10;
 1721 | }
 1722 | }
 1723 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 1724 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 1726 | SCORE += -10;
 1727 | return;
 1728 | }
 1729 | }
 1730 | }
```

### `BaciAI_Seq_086()` (source lines 1732–1773)

```text
 1732 | BaciAI_Seq_086()
 1733 | {
 1735 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1736 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 1737 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_KANASIBARI)
 1738 | ){
 1740 | SCORE += -10;
 1741 | }
 1742 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)
 1743 | || ATK_tokusei == TOKUSEI_ITAZURAGOKORO ){
 1744 | if( AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_DEFENCE) == 0 ){
 1746 | SCORE += -10;
 1747 | }
 1748 | }
 1750 | else if(ATK_tokusei != TOKUSEI_KATAYABURI
 1751 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 1752 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 1753 | {
 1754 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 1755 | ){
 1757 | SCORE += -12;
 1758 | }
 1759 | else if( DEF_tokusei == TOKUSEI_AROMABEERU
 1760 | ){
 1762 | SCORE += -10;
 1763 | }
 1764 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 1765 | if( CHK_rule == BTL_RULE_DOUBLE
 1766 | || CHK_rule == BTL_RULE_TRIPLE){
 1767 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_AROMABEERU){
 1769 | SCORE += -10;
 1770 | }
 1771 | }
 1772 | }
 1773 | }
```

### `BaciAI_Seq_090()` (source lines 1775–1816)

```text
 1775 | BaciAI_Seq_090()
 1776 | {
 1778 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1779 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 1780 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_ENCORE)
 1781 | ){
 1783 | SCORE += -10;
 1784 | }
 1785 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)
 1786 | || ATK_tokusei == TOKUSEI_ITAZURAGOKORO ){
 1787 | if( AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_DEFENCE) == 0 ){
 1789 | SCORE += -10;
 1790 | }
 1791 | }
 1793 | else if(ATK_tokusei != TOKUSEI_KATAYABURI
 1794 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 1795 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 1796 | {
 1797 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 1798 | ){
 1800 | SCORE += -12;
 1801 | }
 1802 | else if( DEF_tokusei == TOKUSEI_AROMABEERU
 1803 | ){
 1805 | SCORE += -10;
 1806 | }
 1807 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 1808 | if( CHK_rule == BTL_RULE_DOUBLE
 1809 | || CHK_rule == BTL_RULE_TRIPLE){
 1810 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_AROMABEERU){
 1812 | SCORE += -10;
 1813 | }
 1814 | }
 1815 | }
 1816 | }
```

### `BaciAI_Seq_092()` (source lines 1818–1827)

```text
 1818 | BaciAI_Seq_092()
 1819 | {
 1821 | if( AI_CMD(CMD_IFN_WAZASICK, CHECK_ATTACK, WAZASICK_NEMURI)
 1822 | ){
 1824 | SCORE += -10;
 1825 | }
 1827 | }
```

### `BaciAI_Seq_094()` (source lines 1829–1852)

```text
 1829 | BaciAI_Seq_094()
 1830 | {
 1832 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1833 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 1834 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_MUSTHIT_TARGET)
 1835 | ){
 1837 | SCORE += -10;
 1838 | }
 1839 | else if(ATK_tokusei == TOKUSEI_NOOGAADO
 1840 | || DEF_tokusei == TOKUSEI_NOOGAADO
 1841 | ){
 1843 | SCORE += -8;
 1844 | }
 1845 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 1846 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 1848 | SCORE += -10;
 1849 | return;
 1850 | }
 1851 | }
 1852 | }
```

### `BaciAI_Seq_102()` (source lines 1854–1873)

```text
 1854 | BaciAI_Seq_102()
 1855 | {
 1857 | if( AI_CMD(CMD_IFN_POKESICK, CHECK_ATTACK)){
 1859 | if( AI_CMD(CMD_IFN_BENCH_COND, CHECK_ATTACK)){
 1861 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 1862 | if( CHK_rule == BTL_RULE_DOUBLE
 1863 | || CHK_rule == BTL_RULE_TRIPLE){
 1864 | if( AI_CMD(CMD_IF_POKESICK, CHECK_ATTACK_FRIEND)){
 1865 | return;
 1866 | }
 1868 | }
 1870 | SCORE += -10;
 1871 | }
 1872 | }
 1873 | }
```

### `BaciAI_Seq_106()` (source lines 1875–1909)

```text
 1875 | BaciAI_Seq_106()
 1876 | {
 1878 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1879 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 1880 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_TOOSENBOU)
 1881 | ){
 1883 | SCORE += -10;
 1884 | }
 1885 | if(AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) == POKETYPE_GHOST
 1886 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) == POKETYPE_GHOST ){
 1888 | SCORE += -10;
 1889 | }
 1891 | else if(ATK_tokusei != TOKUSEI_KATAYABURI
 1892 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 1893 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 1894 | {
 1895 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 1896 | ){
 1898 | SCORE += -12;
 1899 | return;
 1900 | }
 1901 | }
 1902 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 1903 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 1905 | SCORE += -10;
 1906 | return;
 1907 | }
 1908 | }
 1909 | }
```

### `BaciAI_Seq_107()` (source lines 1911–1932)

```text
 1911 | BaciAI_Seq_107()
 1912 | {
 1914 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_AKUMU)
 1915 | ){
 1917 | SCORE += -10;
 1918 | }
 1919 | else if( AI_CMD(CMD_IFN_WAZASICK, CHECK_DEFENCE, WAZASICK_NEMURI)
 1920 | ){
 1922 | SCORE += -8;
 1923 | }
 1924 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1925 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 1926 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 1928 | SCORE += -10;
 1929 | return;
 1930 | }
 1931 | }
 1932 | }
```

### `BaciAI_Seq_109()` (source lines 1934–1965)

```text
 1934 | BaciAI_Seq_109()
 1935 | {
 1937 | ATK_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE1);
 1938 | ATK_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE2);
 1940 | if(ATK_type1 == POKETYPE_GHOST
 1941 | || ATK_type2 == POKETYPE_GHOST
 1942 | ){
 1943 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_NOROI)
 1944 | ){
 1946 | SCORE += -10;
 1947 | }
 1948 | }
 1950 | else if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_AMANOZYAKU){
 1952 | SCORE += -12;
 1953 | return;
 1954 | }
 1955 | else if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_POW, 12) )
 1956 | {
 1958 | SCORE += -10;
 1959 | }
 1960 | else if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_DEF, 12) )
 1961 | {
 1963 | SCORE += -10;
 1964 | }
 1965 | }
```

### `BaciAI_Seq_112()` (source lines 1967–1995)

```text
 1967 | BaciAI_Seq_112()
 1968 | {
 1970 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1971 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 1972 | MAKIBISHI_count = AI_CMD(CMD_CHECK_SIDEEFF_COUNT, CHECK_DEFENCE, BTL_SIDEEFF_MAKIBISI);
 1973 | HIKAE_count = AI_CMD(CMD_CHECK_BENCH_COUNT, CHECK_DEFENCE);
 1974 | if(MAKIBISHI_count == 3
 1975 | ){
 1977 | SCORE += -10;
 1978 | }
 1979 | else if(HIKAE_count == 0
 1980 | ){
 1982 | SCORE += -10;
 1983 | }
 1985 | else if(ATK_tokusei != TOKUSEI_KATAYABURI
 1986 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 1987 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 1988 | {
 1989 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 1990 | ){
 1992 | SCORE += -12;
 1993 | }
 1994 | }
 1995 | }
```

### `BaciAI_Seq_113()` (source lines 1997–2018)

```text
 1997 | BaciAI_Seq_113()
 1998 | {
 2000 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 2001 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 2002 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_MIYABURU)
 2003 | ){
 2005 | SCORE += -10;
 2006 | }
 2008 | else if(ATK_tokusei != TOKUSEI_KATAYABURI
 2009 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 2010 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 2011 | {
 2012 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 2013 | ){
 2015 | SCORE += -12;
 2016 | }
 2017 | }
 2018 | }
```

### `BaciAI_Seq_114()` (source lines 2020–2029)

```text
 2020 | BaciAI_Seq_114()
 2021 | {
 2023 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_HOROBINOUTA)
 2024 | ){
 2026 | SCORE += -10;
 2027 | }
 2029 | }
```

### `BaciAI_Seq_115()` (source lines 2031–2040)

```text
 2031 | BaciAI_Seq_115()
 2032 | {
 2034 | CHK_weather = AI_CMD(CMD_CHECK_WEATHER);
 2035 | if( CHK_weather == WEATHER_SUNAARASHI
 2036 | ){
 2038 | SCORE += -8;
 2039 | }
 2040 | }
```

### `BaciAI_Seq_120()` (source lines 2042–2099)

```text
 2042 | BaciAI_Seq_120()
 2043 | {
 2045 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 2046 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 2047 | ATK_sex = AI_CMD(CMD_CHECK_POKESEX, CHECK_ATTACK);
 2048 | DEF_sex = AI_CMD(CMD_CHECK_POKESEX, CHECK_DEFENCE);
 2049 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_MEROMERO)
 2050 | ){
 2052 | SCORE += -10;
 2053 | }
 2054 | else if( ATK_sex == PTL_SEX_MALE
 2055 | ){
 2056 | if( DEF_sex != PTL_SEX_FEMALE
 2057 | ){
 2059 | SCORE += -10;
 2060 | }
 2061 | }
 2062 | else if( ATK_sex == PTL_SEX_FEMALE
 2063 | ){
 2064 | if( DEF_sex != PTL_SEX_MALE
 2065 | ){
 2067 | SCORE += -10;
 2068 | }
 2069 | }
 2071 | else if(ATK_tokusei != TOKUSEI_KATAYABURI
 2072 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 2073 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 2074 | {
 2075 | if( DEF_tokusei == TOKUSEI_DONKAN
 2076 | ){
 2078 | SCORE += -10;
 2079 | }
 2080 | else if( DEF_tokusei == TOKUSEI_AROMABEERU
 2081 | ){
 2083 | SCORE += -10;
 2084 | }
 2085 | else if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 2086 | ){
 2088 | SCORE += -12;
 2089 | }
 2090 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 2091 | if( CHK_rule == BTL_RULE_DOUBLE
 2092 | || CHK_rule == BTL_RULE_TRIPLE){
 2093 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_AROMABEERU){
 2095 | SCORE += -10;
 2096 | }
 2097 | }
 2098 | }
 2099 | }
```

### `BaciAI_Seq_124()` (source lines 2101–2109)

```text
 2101 | BaciAI_Seq_124()
 2102 | {
 2104 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_ATTACK, BTL_SIDEEFF_SINPINOMAMORI)
 2105 | ){
 2107 | SCORE += -10;
 2108 | }
 2109 | }
```

### `BaciAI_Seq_127()` (source lines 2111–2120)

```text
 2111 | BaciAI_Seq_127()
 2112 | {
 2114 | HIKAE_count = AI_CMD(CMD_CHECK_BENCH_COUNT, CHECK_ATTACK);
 2115 | if(HIKAE_count == 0
 2116 | ){
 2118 | SCORE += -10;
 2119 | }
 2120 | }
```

### `BaciAI_Seq_132()` (source lines 2122–2130)

```text
 2122 | BaciAI_Seq_132()
 2123 | {
 2125 | if( AI_CMD(CMD_IF_HP_EQUAL, CHECK_ATTACK, 100)
 2126 | ){
 2128 | SCORE += -8;
 2129 | }
 2130 | }
```

### `BaciAI_Seq_136()` (source lines 2132–2141)

```text
 2132 | BaciAI_Seq_136()
 2133 | {
 2135 | CHK_weather = AI_CMD(CMD_CHECK_WEATHER);
 2136 | if( CHK_weather == WEATHER_AME
 2137 | ){
 2139 | SCORE += -8;
 2140 | }
 2141 | }
```

### `BaciAI_Seq_137()` (source lines 2143–2152)

```text
 2143 | BaciAI_Seq_137()
 2144 | {
 2146 | CHK_weather = AI_CMD(CMD_CHECK_WEATHER);
 2147 | if( CHK_weather == WEATHER_HARE
 2148 | ){
 2150 | SCORE += -8;
 2151 | }
 2152 | }
```

### `BaciAI_Seq_142()` (source lines 2154–2172)

```text
 2154 | BaciAI_Seq_142()
 2155 | {
 2157 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_AMANOZYAKU){
 2159 | SCORE += -12;
 2160 | return;
 2161 | }
 2162 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_POW, 12)
 2163 | ){
 2165 | SCORE += -10;
 2166 | }
 2167 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 51)
 2168 | ){
 2170 | SCORE += -10;
 2171 | }
 2172 | }
```

### `BaciAI_Seq_148()` (source lines 2174–2182)

```text
 2174 | BaciAI_Seq_148()
 2175 | {
 2177 | if( AI_CMD(CMD_IF_MIRAIYOCHI, CHECK_DEFENCE)
 2178 | ){
 2180 | SCORE += -10;
 2181 | }
 2182 | }
```

### `BaciAI_Seq_158()` (source lines 2184–2193)

```text
 2184 | BaciAI_Seq_158()
 2185 | {
 2187 | CHK_nekodamashi = AI_CMD(CMD_CHECK_NEKODAMASI, CHECK_ATTACK);
 2188 | if( CHK_nekodamashi != 0
 2189 | ){
 2191 | SCORE += -10;
 2192 | }
 2193 | }
```

### `BaciAI_Seq_160()` (source lines 2195–2209)

```text
 2195 | BaciAI_Seq_160()
 2196 | {
 2198 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_AMANOZYAKU){
 2200 | SCORE += -12;
 2201 | return;
 2202 | }
 2203 | CHK_takuwaeru = AI_CMD(CMD_CHECK_TAKUWAERU, CHECK_ATTACK);
 2204 | if( CHK_takuwaeru == 3
 2205 | ){
 2207 | SCORE += -10;
 2208 | }
 2209 | }
```

### `BaciAI_Seq_161()` (source lines 2211–2220)

```text
 2211 | BaciAI_Seq_161()
 2212 | {
 2214 | CHK_takuwaeru = AI_CMD(CMD_CHECK_TAKUWAERU, CHECK_ATTACK);
 2215 | if( CHK_takuwaeru == 0
 2216 | ){
 2218 | SCORE += -10;
 2219 | }
 2220 | }
```

### `BaciAI_Seq_164()` (source lines 2222–2231)

```text
 2222 | BaciAI_Seq_164()
 2223 | {
 2225 | CHK_weather = AI_CMD(CMD_CHECK_WEATHER);
 2226 | if( CHK_weather == WEATHER_ARARE
 2227 | ){
 2229 | SCORE += -8;
 2230 | }
 2231 | }
```

### `BaciAI_Seq_165()` (source lines 2233–2267)

```text
 2233 | BaciAI_Seq_165()
 2234 | {
 2236 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 2237 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 2238 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_ICHAMON)
 2239 | ){
 2241 | SCORE += -10;
 2242 | }
 2244 | else if(ATK_tokusei != TOKUSEI_KATAYABURI
 2245 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 2246 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 2247 | {
 2248 | if( DEF_tokusei == TOKUSEI_AROMABEERU
 2249 | ){
 2251 | SCORE += -10;
 2252 | }
 2253 | else if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 2254 | ){
 2256 | SCORE += -12;
 2257 | }
 2258 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 2259 | if( CHK_rule == BTL_RULE_DOUBLE
 2260 | || CHK_rule == BTL_RULE_TRIPLE){
 2261 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_AROMABEERU){
 2263 | SCORE += -10;
 2264 | }
 2265 | }
 2266 | }
 2267 | }
```

### `BaciAI_Seq_167()` (source lines 2269–2360)

```text
 2269 | BaciAI_Seq_167()
 2270 | {
 2272 | DEF_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1);
 2273 | DEF_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2);
 2274 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 2275 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 2276 | CHK_weather = AI_CMD(CMD_CHECK_WEATHER);
 2278 | if(DEF_type1 == POKETYPE_HONOO
 2279 | || DEF_type2 == POKETYPE_HONOO
 2280 | ){
 2282 | SCORE += -10;
 2283 | }
 2284 | else if( DEF_tokusei == TOKUSEI_MAZIKKUGAADO
 2285 | ){
 2287 | SCORE += -10;
 2288 | }
 2289 | else if( AI_CMD(CMD_IF_POKESICK, CHECK_DEFENCE)
 2290 | ){
 2292 | SCORE += -10;
 2293 | }
 2294 | else if( AI_CMD(CMD_IF_SIDEEFF, CHECK_DEFENCE, BTL_SIDEEFF_SINPINOMAMORI)
 2295 | ){
 2297 | SCORE += -10;
 2298 | }
 2300 | else if(ATK_tokusei != TOKUSEI_KATAYABURI
 2301 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 2302 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 2303 | {
 2304 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 2305 | ){
 2307 | SCORE += -12;
 2308 | }
 2309 | else if( DEF_tokusei == TOKUSEI_MORAIBI
 2310 | ){
 2312 | SCORE += -12;
 2313 | }
 2314 | else if( DEF_tokusei == TOKUSEI_MIZUNOBEERU
 2315 | ){
 2317 | SCORE += -10;
 2318 | }
 2319 | else if( CHK_weather == WEATHER_HARE
 2320 | ){ if( DEF_tokusei == TOKUSEI_RIIHUGAADO
 2321 | ){
 2323 | SCORE += -10;
 2324 | }
 2325 | }
 2326 | if(AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) == POKETYPE_KUSA
 2327 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) == POKETYPE_KUSA ){
 2328 | if( DEF_tokusei == TOKUSEI_HURAWAABEERU){
 2330 | SCORE += -10;
 2331 | return;
 2332 | }
 2333 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 2334 | if( CHK_rule == BTL_RULE_DOUBLE
 2335 | || CHK_rule == BTL_RULE_TRIPLE){
 2336 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_HURAWAABEERU){
 2338 | SCORE += -10;
 2339 | return;
 2340 | }
 2341 | }
 2342 | }
 2343 | }
 2344 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 2345 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 2347 | SCORE += -10;
 2348 | return;
 2349 | }
 2350 | }
 2351 | if( AI_CMD(CMD_IF_EXIST_GROUND, BTL_GROUND_MIST) ){
 2352 | if( DEF_tokusei != TOKUSEI_HUYUU
 2353 | && DEF_type1 != POKETYPE_HIKOU
 2354 | && DEF_type2 != POKETYPE_HIKOU){
 2356 | SCORE += -10;
 2357 | return;
 2358 | }
 2359 | }
 2360 | }
```

### `BaciAI_Seq_168()` (source lines 2362–2424)

```text
 2362 | BaciAI_Seq_168()
 2363 | {
 2365 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 2366 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 2367 | HIKAE_count = AI_CMD(CMD_CHECK_BENCH_COUNT, CHECK_ATTACK);
 2368 | if(HIKAE_count == 0
 2369 | ){
 2371 | SCORE += -10;
 2372 | }
 2373 | else if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_DEFENCE, PARA_POW, 0)
 2374 | ){
 2376 | SCORE += -10;
 2377 | }
 2378 | else if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_DEFENCE, PARA_SPEPOW, 0)
 2379 | ){
 2381 | SCORE += -10;
 2382 | }
 2384 | else if(ATK_tokusei != TOKUSEI_KATAYABURI
 2385 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 2386 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI
 2387 | ){
 2388 | if( DEF_tokusei == TOKUSEI_AMANOZYAKU
 2389 | ){
 2391 | SCORE += -12;
 2392 | }
 2393 | else if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 2394 | || DEF_tokusei == TOKUSEI_KURIABODHI
 2395 | || DEF_tokusei == TOKUSEI_SIROIKEMURI
 2396 | ){
 2398 | SCORE += -10;
 2399 | }
 2400 | else if(AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) == POKETYPE_KUSA
 2401 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) == POKETYPE_KUSA ){
 2402 | if( DEF_tokusei == TOKUSEI_HURAWAABEERU){
 2404 | SCORE += -10;
 2405 | return;
 2406 | }
 2407 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 2408 | if( CHK_rule == BTL_RULE_DOUBLE
 2409 | || CHK_rule == BTL_RULE_TRIPLE){
 2410 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_HURAWAABEERU){
 2412 | SCORE += -10;
 2413 | }
 2414 | }
 2415 | }
 2416 | }
 2417 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 2418 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 2420 | SCORE += -10;
 2421 | return;
 2422 | }
 2423 | }
 2424 | }
```

### `BaciAI_Seq_172()` (source lines 2426–2435)

```text
 2426 | BaciAI_Seq_172()
 2427 | {
 2429 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 2430 | if( CHK_rule == BTL_RULE_SINGLE
 2431 | || CHK_rule == BTL_RULE_ROTATION ){
 2433 | SCORE += -10;
 2434 | }
 2435 | }
```

### `BaciAI_Seq_175()` (source lines 2437–2472)

```text
 2437 | BaciAI_Seq_175()
 2438 | {
 2440 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 2441 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 2442 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_TYOUHATSU)
 2443 | ){
 2445 | SCORE += -10;
 2446 | }
 2448 | else if(ATK_tokusei != TOKUSEI_KATAYABURI
 2449 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 2450 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 2451 | {
 2452 | if( DEF_tokusei == TOKUSEI_AROMABEERU
 2453 | || DEF_tokusei == TOKUSEI_DONKAN
 2454 | ){
 2456 | SCORE += -10;
 2457 | }
 2458 | else if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 2459 | ){
 2461 | SCORE += -12;
 2462 | }
 2463 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 2464 | if( CHK_rule == BTL_RULE_DOUBLE
 2465 | || CHK_rule == BTL_RULE_TRIPLE){
 2466 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_AROMABEERU){
 2468 | SCORE += -10;
 2469 | }
 2470 | }
 2471 | }
 2472 | }
```

### `BaciAI_Seq_176()` (source lines 2474–2483)

```text
 2474 | BaciAI_Seq_176()
 2475 | {
 2477 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 2478 | if( CHK_rule == BTL_RULE_SINGLE
 2479 | || CHK_rule == BTL_RULE_ROTATION ){
 2481 | SCORE += -20;
 2482 | }
 2483 | }
```

### `BaciAI_Seq_177()` (source lines 2485–2524)

```text
 2485 | BaciAI_Seq_177()
 2486 | {
 2488 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 2489 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 2491 | if(ATK_tokusei != TOKUSEI_KATAYABURI
 2492 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 2493 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 2494 | {
 2495 | if( DEF_tokusei == TOKUSEI_NENTYAKU
 2496 | ){
 2498 | SCORE += -10;
 2499 | }
 2500 | }
 2501 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 2502 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 2504 | SCORE += -10;
 2505 | return;
 2506 | }
 2507 | }
 2508 | DefMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
 2509 | if( DefMonsNo == MONSNO_ARUSEUSU
 2510 | || DefMonsNo == MONSNO_GENOSEKUTO){
 2512 | SCORE += -10;
 2513 | }
 2514 | if( DefMonsNo == MONSNO_GIRATHINA){
 2515 | if(AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_HAKKINDAMA)){
 2517 | SCORE += -10;
 2518 | }
 2519 | }
 2520 | if( AI_CMD(CMD_IF_MEGAEVOLVED, CHECK_DEFENCE) ){
 2522 | SCORE += -10;
 2523 | }
 2524 | }
```

### `BaciAI_Seq_178()` (source lines 2526–2551)

```text
 2526 | BaciAI_Seq_178()
 2527 | {
 2528 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 2529 | if( DEF_tokusei == TOKUSEI_TOREESU
 2530 | || DEF_tokusei == TOKUSEI_DARUMAMOODO){
 2532 | SCORE += -10;
 2533 | return;
 2534 | }
 2535 | DefMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
 2536 | if( DefMonsNo == MONSNO_POWARUN
 2537 | || DefMonsNo == MONSNO_ARUSEUSU
 2538 | || DefMonsNo == MONSNO_THERIMU
 2539 | || DefMonsNo == MONSNO_ZOROAAKU
 2540 | || DefMonsNo == MONSNO_METAMON
 2541 | || DefMonsNo == MONSNO_NUKENIN
 2542 | || DefMonsNo == MONSNO_GIRUGARUDO
 2543 | || DefMonsNo == MONSNO_KEKKINGU
 2544 | || DefMonsNo == MONSNO_AAKEOSU
 2545 | || DefMonsNo == MONSNO_REZIGIGASU
 2546 | ){
 2548 | SCORE += -10;
 2549 | return;
 2550 | }
 2551 | }
```

### `BaciAI_Seq_179()` (source lines 2553–2560)

```text
 2553 | BaciAI_Seq_179()
 2554 | {
 2556 | if( AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_ATTACK) == WAZANO_NEGAIGOTO ){
 2558 | SCORE += -10;
 2559 | }
 2560 | }
```

### `BaciAI_Seq_181()` (source lines 2562–2570)

```text
 2562 | BaciAI_Seq_181()
 2563 | {
 2565 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_NEWOHARU)
 2566 | ){
 2568 | SCORE += -10;
 2569 | }
 2570 | }
```

### `BaciAI_Seq_184()` (source lines 2572–2581)

```text
 2572 | BaciAI_Seq_184()
 2573 | {
 2575 | CHK_recycle = AI_CMD(CMD_CHECK_RECYCLE_ITEM, CHECK_ATTACK);
 2576 | if( CHK_recycle == 0
 2577 | ){
 2579 | SCORE += -8;
 2580 | }
 2581 | }
```

### `BaciAI_Seq_188()` (source lines 2583–2612)

```text
 2583 | BaciAI_Seq_188()
 2584 | {
 2586 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 2587 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 2588 | CHK_soubi = AI_CMD(CMD_CHECK_SOUBI_ITEM, CHECK_DEFENCE);
 2589 | if( CHK_soubi == 0
 2590 | ){
 2592 | SCORE += -10;
 2593 | }
 2595 | else if(ATK_tokusei != TOKUSEI_KATAYABURI
 2596 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 2597 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 2598 | {
 2599 | if( DEF_tokusei == TOKUSEI_NENTYAKU
 2600 | ){
 2602 | SCORE += -10;
 2603 | }
 2604 | }
 2605 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 2606 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 2608 | SCORE += -10;
 2609 | return;
 2610 | }
 2611 | }
 2612 | }
```

### `BaciAI_Seq_191()` (source lines 2614–2651)

```text
 2614 | BaciAI_Seq_191()
 2615 | {
 2616 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 2617 | if(DEF_tokusei == TOKUSEI_HUSIGINAMAMORI
 2618 | || DEF_tokusei == TOKUSEI_MARUTITAIPU
 2619 | || DEF_tokusei == TOKUSEI_IRYUUZYON
 2620 | || DEF_tokusei == TOKUSEI_BATORUSUITTI){
 2622 | SCORE += -10;
 2623 | }
 2624 | DefMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
 2625 | if( DefMonsNo == MONSNO_POWARUN
 2626 | || DefMonsNo == MONSNO_ARUSEUSU
 2627 | || DefMonsNo == MONSNO_THERIMU
 2628 | || DefMonsNo == MONSNO_ZOROAAKU
 2629 | || DefMonsNo == MONSNO_METAMON
 2630 | || DefMonsNo == MONSNO_NUKENIN
 2631 | || DefMonsNo == MONSNO_GIRUGARUDO){
 2633 | SCORE += -10;
 2634 | return;
 2635 | }
 2637 | if( DefMonsNo == MONSNO_KEKKINGU
 2638 | || DefMonsNo == MONSNO_AAKEOSU
 2639 | || DefMonsNo == MONSNO_REZIGIGASU){
 2641 | SCORE += -12;
 2642 | return;
 2643 | }
 2644 | if(DEF_tokusei == TOKUSEI_NAMAKE
 2645 | || DEF_tokusei == TOKUSEI_YOWAKI
 2646 | || DEF_tokusei == TOKUSEI_SUROOSUTAATO){
 2648 | SCORE += -12;
 2649 | return;
 2650 | }
 2651 | }
```

### `BaciAI_Seq_192()` (source lines 2653–2661)

```text
 2653 | BaciAI_Seq_192()
 2654 | {
 2656 | if( AI_CMD(CMD_FLDEFF_CHECK, EFF_FUIN)
 2657 | ){
 2659 | SCORE += -10;
 2660 | }
 2661 | }
```

### `BaciAI_Seq_193()` (source lines 2663–2671)

```text
 2663 | BaciAI_Seq_193()
 2664 | {
 2666 | if( AI_CMD(CMD_IFN_POKESICK, CHECK_ATTACK)
 2667 | ){
 2669 | SCORE += -10;
 2670 | }
 2671 | }
```

### `BaciAI_Seq_201()` (source lines 2673–2681)

```text
 2673 | BaciAI_Seq_201()
 2674 | {
 2676 | if( AI_CMD(CMD_FLDEFF_CHECK, EFF_DOROASOBI)
 2677 | ){
 2679 | SCORE += -10;
 2680 | }
 2681 | }
```

### `BaciAI_Seq_205()` (source lines 2683–2750)

```text
 2683 | BaciAI_Seq_205()
 2684 | {
 2687 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 2688 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 2689 | if( DEF_tokusei == TOKUSEI_MAKENKI
 2690 | || DEF_tokusei == TOKUSEI_KATIKI
 2691 | ){
 2693 | SCORE += -12;
 2694 | }
 2696 | else if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_DEFENCE, PARA_POW, 0) )
 2697 | {
 2699 | SCORE += -10;
 2700 | }
 2701 | else if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_DEFENCE, PARA_DEF, 0) )
 2702 | {
 2704 | SCORE += -10;
 2705 | }
 2708 | else if(ATK_tokusei != TOKUSEI_KATAYABURI
 2709 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 2710 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 2711 | {
 2712 | if( DEF_tokusei == TOKUSEI_KAIRIKIBASAMI
 2713 | || DEF_tokusei == TOKUSEI_HATOMUNE
 2714 | || DEF_tokusei == TOKUSEI_KURIABODHI
 2715 | || DEF_tokusei == TOKUSEI_SIROIKEMURI
 2716 | ){
 2718 | SCORE += -10;
 2719 | }
 2720 | else if( DEF_tokusei == TOKUSEI_AMANOZYAKU
 2721 | || DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 2722 | ){
 2724 | SCORE += -12;
 2725 | }
 2726 | else if(AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) == POKETYPE_KUSA
 2727 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) == POKETYPE_KUSA ){
 2728 | if( DEF_tokusei == TOKUSEI_HURAWAABEERU){
 2730 | SCORE += -10;
 2731 | return;
 2732 | }
 2733 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 2734 | if( CHK_rule == BTL_RULE_DOUBLE
 2735 | || CHK_rule == BTL_RULE_TRIPLE){
 2736 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_HURAWAABEERU){
 2738 | SCORE += -10;
 2739 | }
 2740 | }
 2741 | }
 2742 | }
 2743 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 2744 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 2746 | SCORE += -10;
 2747 | return;
 2748 | }
 2749 | }
 2750 | }
```

### `BaciAI_Seq_206()` (source lines 2752–2771)

```text
 2752 | BaciAI_Seq_206()
 2753 | {
 2755 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_AMANOZYAKU){
 2757 | SCORE += -12;
 2758 | return;
 2759 | }
 2761 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_DEF, 12) )
 2762 | {
 2764 | SCORE += -10;
 2765 | }
 2766 | else if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_SPEDEF, 12) )
 2767 | {
 2769 | SCORE += -10;
 2770 | }
 2771 | }
```

### `BaciAI_Seq_208()` (source lines 2773–2792)

```text
 2773 | BaciAI_Seq_208()
 2774 | {
 2776 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_AMANOZYAKU){
 2778 | SCORE += -12;
 2779 | return;
 2780 | }
 2782 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_POW, 12) )
 2783 | {
 2785 | SCORE += -10;
 2786 | }
 2787 | else if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_DEF, 12) )
 2788 | {
 2790 | SCORE += -10;
 2791 | }
 2792 | }
```

### `BaciAI_Seq_210()` (source lines 2794–2802)

```text
 2794 | BaciAI_Seq_210()
 2795 | {
 2797 | if( AI_CMD(CMD_FLDEFF_CHECK, EFF_MIZUASOBI)
 2798 | ){
 2800 | SCORE += -10;
 2801 | }
 2802 | }
```

### `BaciAI_Seq_211()` (source lines 2804–2823)

```text
 2804 | BaciAI_Seq_211()
 2805 | {
 2807 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_AMANOZYAKU){
 2809 | SCORE += -12;
 2810 | return;
 2811 | }
 2813 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_SPEPOW, 12) )
 2814 | {
 2816 | SCORE += -10;
 2817 | }
 2818 | else if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_SPEDEF, 12) )
 2819 | {
 2821 | SCORE += -10;
 2822 | }
 2823 | }
```

### `BaciAI_Seq_212()` (source lines 2825–2839)

```text
 2825 | BaciAI_Seq_212()
 2826 | {
 2828 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_AMANOZYAKU){
 2830 | SCORE += -12;
 2831 | return;
 2832 | }
 2834 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_POW, 12) )
 2835 | {
 2837 | SCORE += -10;
 2838 | }
 2839 | }
```

### `BaciAI_Seq_215()` (source lines 2841–2849)

```text
 2841 | BaciAI_Seq_215()
 2842 | {
 2844 | if( AI_CMD(CMD_FLDEFF_CHECK, EFF_JURYOKU)
 2845 | ){
 2847 | SCORE += -10;
 2848 | }
 2849 | }
```

### `BaciAI_Seq_216()` (source lines 2851–2872)

```text
 2851 | BaciAI_Seq_216()
 2852 | {
 2854 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 2855 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 2856 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_MIYABURU)
 2857 | ){
 2859 | SCORE += -10;
 2860 | }
 2862 | else if(ATK_tokusei != TOKUSEI_KATAYABURI
 2863 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 2864 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 2865 | {
 2866 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 2867 | ){
 2869 | SCORE += -12;
 2870 | }
 2871 | }
 2872 | }
```

### `BaciAI_Seq_220()` (source lines 2874–2889)

```text
 2874 | BaciAI_Seq_220()
 2875 | {
 2877 | HIKAE_count = AI_CMD(CMD_CHECK_BENCH_COUNT, CHECK_ATTACK);
 2878 | if(HIKAE_count == 0
 2879 | ){
 2881 | SCORE += -10;
 2882 | return;
 2883 | }
 2884 | if( AI_CMD(CMD_IF_BENCH_HPDEC, CHECK_ATTACK)){
 2885 | return;
 2886 | }
 2888 | SCORE += -10;
 2889 | }
```

### `BaciAI_Seq_222()` (source lines 2891–2898)

```text
 2891 | BaciAI_Seq_222()
 2892 | {
 2894 | if( AI_CMD(CMD_CHECK_SOUBI_ITEM, CHECK_ATTACK) == 0){
 2896 | SCORE += -10;
 2897 | }
 2898 | }
```

### `BaciAI_Seq_225()` (source lines 2900–2913)

```text
 2900 | BaciAI_Seq_225()
 2901 | {
 2903 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_ATTACK, BTL_SIDEEFF_OIKAZE)
 2904 | ){
 2906 | SCORE += -10;
 2907 | }
 2908 | else if( AI_CMD(CMD_FLDEFF_CHECK, EFF_TRICKROOM)
 2909 | ){
 2911 | SCORE += -8;
 2912 | }
 2913 | }
```

### `BaciAI_Seq_226()` (source lines 2915–2919)

```text
 2915 | BaciAI_Seq_226()
 2916 | {
 2919 | }
```

### `BaciAI_Seq_227()` (source lines 2921–2951)

```text
 2921 | BaciAI_Seq_227()
 2922 | {
 2924 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 2925 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 2928 | if( DEF_tokusei == TOKUSEI_ATODASI
 2929 | ){
 2931 | SCORE += -10;
 2932 | }
 2938 | else if( ATK_tokusei == TOKUSEI_ATODASI
 2939 | ){
 2940 | return;
 2941 | }
 2946 | else if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)
 2947 | ){
 2949 | SCORE += -10;
 2950 | }
 2951 | }
```

### `BaciAI_Seq_232()` (source lines 2953–2981)

```text
 2953 | BaciAI_Seq_232()
 2954 | {
 2956 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 2957 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 2958 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_SASIOSAE)
 2959 | ){
 2961 | SCORE += -10;
 2962 | }
 2964 | else if(ATK_tokusei != TOKUSEI_KATAYABURI
 2965 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 2966 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 2967 | {
 2968 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 2969 | ){
 2971 | SCORE += -12;
 2972 | }
 2973 | }
 2974 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 2975 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 2977 | SCORE += -10;
 2978 | return;
 2979 | }
 2980 | }
 2981 | }
```

### `BaciAI_Seq_233()` (source lines 2983–3019)

```text
 2983 | BaciAI_Seq_233()
 2984 | {
 2986 | Atk_SoubiEquip = AI_CMD(CMD_CHECK_SOUBI_EQUIP, CHECK_ATTACK)
 2987 | Def_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 2988 | Atk_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 2989 | if( Atk_SoubiEquip == 0){
 2991 | SCORE += -10;
 2992 | }
 2993 | if( Atk_SoubiEquip == SOUBI_HIRUMASERU ){
 2994 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_DEFENCE)){
 2996 | SCORE += -10;
 2997 | return;
 2998 | }
 2999 | if( Def_Tokusei == TOKUSEI_SEISINRYOKU
 3000 | && Def_Tokusei == TOKUSEI_ITAZURAGOKORO ){
 3002 | SCORE += -10;
 3003 | return;
 3004 | }
 3005 | }
 3006 | if( Atk_SoubiEquip == SOUBI_DOKUBARIUP
 3007 | || Atk_SoubiEquip == SOUBI_TEKINIMOTASERUTOMOUDOKU ){
 3008 | Call BaciAI_Seq_033()
 3009 | return;
 3010 | }
 3011 | if( Atk_SoubiEquip == SOUBI_TTEKINIMOTASERUTOYAKEDO ){
 3012 | Call BaciAI_Seq_167()
 3013 | return;
 3014 | }
 3015 | if( Atk_SoubiEquip == SOUBI_PIKATYUUTOKUKOUNIBAI){
 3016 | Call BaciAI_Seq_067()
 3017 | return;
 3018 | }
 3019 | }
```

### `BaciAI_Seq_234()` (source lines 3021–3055)

```text
 3021 | BaciAI_Seq_234()
 3022 | {
 3024 | if( AI_CMD(CMD_IF_POKESICK, CHECK_DEFENCE)
 3025 | ){
 3027 | SCORE += -10;
 3028 | }
 3029 | else if( AI_CMD(CMD_IFN_POKESICK, CHECK_ATTACK)
 3030 | ){
 3032 | SCORE += -8;
 3033 | }
 3034 | else if( AI_CMD(CMD_IF_SIDEEFF, CHECK_DEFENCE, BTL_SIDEEFF_SINPINOMAMORI)
 3035 | ){
 3037 | SCORE += -10;
 3038 | }
 3039 | else if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_DOKU)
 3040 | ){
 3041 | Call BaciAI_Seq_033()
 3042 | }
 3043 | else if( AI_CMD(CMD_IF_DOKUDOKU, CHECK_ATTACK)
 3044 | ){
 3045 | Call BaciAI_Seq_033()
 3046 | }
 3047 | else if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_YAKEDO)
 3048 | ){
 3049 | Call BaciAI_Seq_167()
 3050 | }
 3051 | else if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_MAHI)
 3052 | ){
 3053 | Call BaciAI_Seq_067()
 3054 | }
 3055 | }
```

### `BaciAI_Seq_236()` (source lines 3057–3090)

```text
 3057 | BaciAI_Seq_236()
 3058 | {
 3060 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 3061 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 3062 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_KAIHUKUHUUJI)
 3063 | ){
 3065 | SCORE += -10;
 3066 | }
 3068 | else if(ATK_tokusei != TOKUSEI_KATAYABURI
 3069 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 3070 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 3071 | {
 3072 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 3073 | ){
 3075 | SCORE += -12;
 3076 | }
 3077 | else if( DEF_tokusei == TOKUSEI_AROMABEERU){
 3079 | SCORE += -10;
 3080 | }
 3081 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 3082 | if( CHK_rule == BTL_RULE_DOUBLE
 3083 | || CHK_rule == BTL_RULE_TRIPLE){
 3084 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) == TOKUSEI_AROMABEERU){
 3086 | SCORE += -10;
 3087 | }
 3088 | }
 3089 | }
 3090 | }
```

### `BaciAI_Seq_238()` (source lines 3092–3104)

```text
 3092 | BaciAI_Seq_238()
 3093 | {
 3095 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 3096 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 3097 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 3099 | SCORE += -10;
 3100 | return;
 3101 | }
 3102 | }
 3104 | }
```

### `BaciAI_Seq_239()` (source lines 3106–3166)

```text
 3106 | BaciAI_Seq_239()
 3107 | {
 3109 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 3110 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 3111 | DefMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
 3112 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_IEKI)
 3113 | ){
 3115 | SCORE += -10;
 3116 | return;
 3117 | }
 3118 | if( DEF_tokusei == TOKUSEI_MARUTITAIPU
 3119 | || DEF_tokusei == TOKUSEI_NIGEASI
 3120 | || DEF_tokusei == TOKUSEI_MITUATUME
 3121 | ){
 3123 | SCORE += -10;
 3124 | return;
 3125 | }
 3127 | if(ATK_tokusei != TOKUSEI_KATAYABURI
 3128 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 3129 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 3130 | {
 3131 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 3132 | ){
 3134 | SCORE += -12;
 3135 | return;
 3136 | }
 3137 | }
 3138 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 3139 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 3141 | SCORE += -10;
 3142 | return;
 3143 | }
 3144 | }
 3145 | if( DefMonsNo == MONSNO_ARUSEUSU
 3146 | || DefMonsNo == MONSNO_GIRUGARUDO ){
 3148 | SCORE += -10;
 3149 | return;
 3150 | }
 3152 | if( DefMonsNo == MONSNO_KEKKINGU
 3153 | || DefMonsNo == MONSNO_AAKEOSU
 3154 | || DefMonsNo == MONSNO_REZIGIGASU){
 3156 | SCORE += -12;
 3157 | return;
 3158 | }
 3159 | if(DEF_tokusei == TOKUSEI_NAMAKE
 3160 | || DEF_tokusei == TOKUSEI_YOWAKI
 3161 | || DEF_tokusei == TOKUSEI_SUROOSUTAATO){
 3163 | SCORE += -12;
 3164 | return;
 3165 | }
 3166 | }
```

### `BaciAI_Seq_240()` (source lines 3168–3176)

```text
 3168 | BaciAI_Seq_240()
 3169 | {
 3176 | }
```

### `BaciAI_Seq_241()` (source lines 3178–3187)

```text
 3178 | BaciAI_Seq_241()
 3179 | {
 3181 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_DEFENCE)){
 3182 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) != TOKUSEI_ITAZURAGOKORO ){
 3184 | SCORE += -10;
 3185 | }
 3186 | }
 3187 | }
```

### `BaciAI_Seq_242()` (source lines 3189–3201)

```text
 3189 | BaciAI_Seq_242()
 3190 | {
 3192 | CHK_turn = AI_CMD(CMD_CHECK_TURN);
 3193 | if( CHK_turn == 0
 3194 | ){
 3195 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_DEFENCE)
 3196 | ){
 3198 | SCORE += -10;
 3199 | }
 3200 | }
 3201 | }
```

### `BaciAI_Seq_243()` (source lines 3203–3215)

```text
 3203 | BaciAI_Seq_243()
 3204 | {
 3206 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 3207 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 3208 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 3210 | SCORE += -10;
 3211 | return;
 3212 | }
 3213 | }
 3215 | }
```

### `BaciAI_Seq_244()` (source lines 3217–3229)

```text
 3217 | BaciAI_Seq_244()
 3218 | {
 3220 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 3221 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 3222 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 3224 | SCORE += -10;
 3225 | return;
 3226 | }
 3227 | }
 3229 | }
```

### `BaciAI_Seq_246()` (source lines 3231–3240)

```text
 3231 | BaciAI_Seq_246()
 3232 | {
 3234 | if( AI_CMD(CMD_IF_TOTTEOKI, CHECK_ATTACK)
 3235 | ){
 3236 | return;
 3237 | }
 3239 | SCORE += -10;
 3240 | }
```

### `BaciAI_Seq_247()` (source lines 3242–3294)

```text
 3242 | BaciAI_Seq_247()
 3243 | {
 3245 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 3246 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 3247 | DefMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
 3248 | if( DEF_tokusei == TOKUSEI_HUMIN
 3249 | ){
 3251 | SCORE += -10;
 3252 | return;
 3253 | }
 3255 | if(ATK_tokusei != TOKUSEI_KATAYABURI
 3256 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 3257 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 3258 | {
 3259 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 3260 | ){
 3262 | SCORE += -12;
 3263 | return;
 3264 | }
 3265 | }
 3266 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 3267 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 3269 | SCORE += -10;
 3270 | return;
 3271 | }
 3272 | }
 3273 | if( DefMonsNo == MONSNO_ARUSEUSU
 3274 | || DefMonsNo == MONSNO_GIRUGARUDO ){
 3276 | SCORE += -10;
 3277 | return;
 3278 | }
 3280 | if( DefMonsNo == MONSNO_KEKKINGU
 3281 | || DefMonsNo == MONSNO_AAKEOSU
 3282 | || DefMonsNo == MONSNO_REZIGIGASU){
 3284 | SCORE += -12;
 3285 | return;
 3286 | }
 3287 | if(DEF_tokusei == TOKUSEI_NAMAKE
 3288 | || DEF_tokusei == TOKUSEI_YOWAKI
 3289 | || DEF_tokusei == TOKUSEI_SUROOSUTAATO){
 3291 | SCORE += -12;
 3292 | return;
 3293 | }
 3294 | }
```

### `BaciAI_Seq_249()` (source lines 3296–3326)

```text
 3296 | BaciAI_Seq_249()
 3297 | {
 3299 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 3300 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 3301 | DOKUBISHI_count = AI_CMD(CMD_CHECK_SIDEEFF_COUNT, CHECK_DEFENCE, BTL_SIDEEFF_DOKUBISI);
 3302 | HIKAE_count = AI_CMD(CMD_CHECK_BENCH_COUNT, CHECK_DEFENCE);
 3303 | if(DOKUBISHI_count == 2
 3304 | ){
 3306 | SCORE += -10;
 3307 | return;
 3308 | }
 3309 | if(HIKAE_count == 0
 3310 | ){
 3312 | SCORE += -10;
 3313 | return;
 3314 | }
 3316 | if(ATK_tokusei != TOKUSEI_KATAYABURI
 3317 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 3318 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 3319 | {
 3320 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 3321 | ){
 3323 | SCORE += -12;
 3324 | }
 3325 | }
 3326 | }
```

### `BaciAI_Seq_251()` (source lines 3328–3336)

```text
 3328 | BaciAI_Seq_251()
 3329 | {
 3331 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_AQUARING)
 3332 | ){
 3334 | SCORE += -10;
 3335 | }
 3336 | }
```

### `BaciAI_Seq_252()` (source lines 3338–3368)

```text
 3338 | BaciAI_Seq_252()
 3339 | {
 3340 | ATK_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE1);
 3341 | ATK_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE2);
 3342 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 3344 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_FLYING)
 3345 | ){
 3347 | SCORE += -10;
 3348 | return;
 3349 | }
 3350 | if( ATK_tokusei == TOKUSEI_HUYUU
 3351 | ){
 3353 | SCORE += -10;
 3354 | return;
 3355 | }
 3356 | if(ATK_type1 == POKETYPE_HIKOU
 3357 | || ATK_type2 == POKETYPE_HIKOU
 3358 | ){
 3360 | SCORE += -10;
 3361 | return;
 3362 | }
 3363 | if( AI_CMD(CMD_FLDEFF_CHECK, EFF_JURYOKU)
 3364 | ){
 3366 | SCORE += -10;
 3367 | }
 3368 | }
```

### `BaciAI_Seq_258()` (source lines 3370–3400)

```text
 3370 | BaciAI_Seq_258()
 3371 | {
 3373 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 3374 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 3376 | if(ATK_tokusei != TOKUSEI_KATAYABURI
 3377 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 3378 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 3379 | {
 3380 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 3381 | ){
 3383 | SCORE += -12;
 3384 | return;
 3385 | }
 3386 | }
 3387 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_DEFENCE, BTL_SIDEEFF_HIKARINOKABE)
 3388 | ){
 3389 | return;
 3390 | }
 3391 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_DEFENCE, BTL_SIDEEFF_REFRECTOR)
 3392 | ){
 3393 | return;
 3394 | }
 3395 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_DEFENCE, PARA_AVOID, 0)
 3396 | ){
 3398 | SCORE += -10;
 3399 | }
 3400 | }
```

### `BaciAI_Seq_259()` (source lines 3402–3415)

```text
 3402 | BaciAI_Seq_259()
 3403 | {
 3415 | }
```

### `BaciAI_Seq_265()` (source lines 3417–3441)

```text
 3417 | BaciAI_Seq_265()
 3418 | {
 3420 | ATK_sex = AI_CMD(CMD_CHECK_POKESEX, CHECK_ATTACK);
 3421 | DEF_sex = AI_CMD(CMD_CHECK_POKESEX, CHECK_DEFENCE);
 3422 | if( ATK_sex == PTL_SEX_MALE
 3423 | ){
 3424 | if( DEF_sex != PTL_SEX_FEMALE
 3425 | ){
 3427 | SCORE += -10;
 3428 | return;
 3429 | }
 3430 | }
 3431 | else if( ATK_sex == PTL_SEX_FEMALE
 3432 | ){
 3433 | if( DEF_sex != PTL_SEX_MALE
 3434 | ){
 3436 | SCORE += -10;
 3437 | return;
 3438 | }
 3439 | }
 3440 | Call BaciAI_Seq_021()
 3441 | }
```

### `BaciAI_Seq_266()` (source lines 3443–3472)

```text
 3443 | BaciAI_Seq_266()
 3444 | {
 3446 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 3447 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 3448 | HIKAE_count = AI_CMD(CMD_CHECK_BENCH_COUNT, CHECK_DEFENCE);
 3450 | if(ATK_tokusei != TOKUSEI_KATAYABURI
 3451 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 3452 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 3453 | {
 3454 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 3455 | ){
 3457 | SCORE += -12;
 3458 | return;
 3459 | }
 3460 | }
 3461 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_DEFENCE, BTL_SIDEEFF_STEALTHROCK)
 3462 | ){
 3464 | SCORE += -10;
 3465 | return;
 3466 | }
 3467 | if(HIKAE_count == 0
 3468 | ){
 3470 | SCORE += -10;
 3471 | }
 3472 | }
```

### `BaciAI_Seq_270()` (source lines 3474–3498)

```text
 3474 | BaciAI_Seq_270()
 3475 | {
 3477 | HIKAE_count = AI_CMD(CMD_CHECK_BENCH_COUNT, CHECK_ATTACK);
 3478 | if(HIKAE_count == 0
 3479 | ){
 3481 | SCORE += -10;
 3482 | return;
 3483 | }
 3484 | if( AI_CMD(CMD_IF_BENCH_HPDEC, CHECK_ATTACK)){
 3486 | return;
 3487 | }
 3488 | if( AI_CMD(CMD_IF_BENCH_COND, CHECK_ATTACK)){
 3490 | return;
 3491 | }
 3492 | if( AI_CMD(CMD_IF_BENCH_PPDEC, CHECK_ATTACK)){
 3494 | return;
 3495 | }
 3497 | SCORE += -10;
 3498 | }
```

### `BaciAI_Seq_278()` (source lines 3500–3509)

```text
 3500 | BaciAI_Seq_278()
 3501 | {
 3503 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 3504 | if( CHK_rule == BTL_RULE_SINGLE
 3505 | || CHK_rule == BTL_RULE_ROTATION ){
 3507 | SCORE += -10;
 3508 | }
 3509 | }
```

### `BaciAI_Seq_281()` (source lines 3511–3519)

```text
 3511 | BaciAI_Seq_281()
 3512 | {
 3514 | if( AI_CMD(CMD_FLDEFF_CHECK, EFF_WONDERROOM)
 3515 | ){
 3517 | SCORE += -10;
 3518 | }
 3519 | }
```

### `BaciAI_Seq_285()` (source lines 3521–3550)

```text
 3521 | BaciAI_Seq_285()
 3522 | {
 3524 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 3525 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 3527 | if(ATK_tokusei != TOKUSEI_KATAYABURI
 3528 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 3529 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 3530 | {
 3531 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 3532 | ){
 3534 | SCORE += -12;
 3535 | return;
 3536 | }
 3537 | }
 3538 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_TELEKINESIS)
 3539 | ){
 3541 | SCORE += -10;
 3542 | }
 3543 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 3544 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 3546 | SCORE += -10;
 3547 | return;
 3548 | }
 3549 | }
 3550 | }
```

### `BaciAI_Seq_286()` (source lines 3552–3560)

```text
 3552 | BaciAI_Seq_286()
 3553 | {
 3555 | if( AI_CMD(CMD_FLDEFF_CHECK, EFF_MAGICROOM)
 3556 | ){
 3558 | SCORE += -10;
 3559 | }
 3560 | }
```

### `BaciAI_Seq_292()` (source lines 3563–3590)

```text
 3563 | BaciAI_Seq_292()
 3564 | {
 3566 | ATK_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE1);
 3567 | ATK_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE2);
 3568 | DEF_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1);
 3569 | DEF_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2);
 3570 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 3571 | if( CHK_rule == BTL_RULE_DOUBLE
 3572 | || CHK_rule == BTL_RULE_TRIPLE){
 3573 | DEFFRD_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_FRIEND_TYPE1);
 3574 | DEFFRD_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_FRIEND_TYPE2);
 3575 | if(ATK_type1 == DEFFRD_type1
 3576 | || ATK_type1 == DEFFRD_type2
 3577 | || ATK_type2 == DEFFRD_type1
 3578 | || ATK_type2 == DEFFRD_type2){
 3580 | return;
 3581 | }
 3582 | }
 3583 | if(ATK_type1 != DEF_type1
 3584 | && ATK_type1 != DEF_type2
 3585 | && ATK_type2 != DEF_type1
 3586 | && ATK_type2 != DEF_type2){
 3588 | SCORE += -10;
 3589 | }
 3590 | }
```

### `BaciAI_Seq_294()` (source lines 3592–3620)

```text
 3592 | BaciAI_Seq_294()
 3593 | {
 3595 | DEF_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1);
 3596 | DEF_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2);
 3597 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 3598 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_YOBIMIZU){
 3599 | if( ATK_tokusei != TOKUSEI_KATAYABURI
 3600 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 3601 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI){
 3603 | SCORE += -12;
 3604 | return;
 3605 | }
 3606 | }
 3607 | if(DEF_type1 == POKETYPE_MIZU
 3608 | || DEF_type2 == POKETYPE_MIZU
 3609 | ){
 3611 | SCORE += -10;
 3612 | }
 3613 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 3614 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 3616 | SCORE += -10;
 3617 | return;
 3618 | }
 3619 | }
 3620 | }
```

### `BaciAI_Seq_298()` (source lines 3622–3686)

```text
 3622 | BaciAI_Seq_298()
 3623 | {
 3625 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 3626 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 3628 | if(ATK_tokusei != TOKUSEI_KATAYABURI
 3629 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 3630 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 3631 | {
 3632 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 3633 | ){
 3635 | SCORE += -10;
 3636 | return;
 3637 | }
 3638 | }
 3639 | if( DEF_tokusei == TOKUSEI_TOREESU
 3640 | || DEF_tokusei == TOKUSEI_DARUMAMOODO){
 3642 | SCORE += -10;
 3643 | return;
 3644 | }
 3645 | DefMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
 3646 | if( DefMonsNo == MONSNO_POWARUN
 3647 | || DefMonsNo == MONSNO_ARUSEUSU
 3648 | || DefMonsNo == MONSNO_THERIMU
 3649 | || DefMonsNo == MONSNO_ZOROAAKU
 3650 | || DefMonsNo == MONSNO_METAMON
 3651 | || DefMonsNo == MONSNO_NUKENIN
 3652 | || DefMonsNo == MONSNO_GIRUGARUDO
 3653 | ){
 3655 | SCORE += -10;
 3656 | return;
 3657 | }
 3659 | if(DEF_tokusei == TOKUSEI_TANZYUN){
 3661 | SCORE += -10;
 3662 | return;
 3663 | }
 3664 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 3665 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 3667 | SCORE += -10;
 3668 | return;
 3669 | }
 3670 | }
 3672 | if( DefMonsNo == MONSNO_KEKKINGU
 3673 | || DefMonsNo == MONSNO_AAKEOSU
 3674 | || DefMonsNo == MONSNO_REZIGIGASU){
 3676 | SCORE += -12;
 3677 | return;
 3678 | }
 3679 | if(DEF_tokusei == TOKUSEI_NAMAKE
 3680 | || DEF_tokusei == TOKUSEI_YOWAKI
 3681 | || DEF_tokusei == TOKUSEI_SUROOSUTAATO){
 3683 | SCORE += -12;
 3684 | return;
 3685 | }
 3686 | }
```

### `BaciAI_Seq_299()` (source lines 3688–3750)

```text
 3688 | BaciAI_Seq_299()
 3689 | {
 3691 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 3692 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 3693 | if( ATK_tokusei == DEF_tokusei){
 3695 | SCORE += -10;
 3696 | return;
 3697 | }
 3699 | if(ATK_tokusei != TOKUSEI_KATAYABURI
 3700 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 3701 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 3702 | {
 3703 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 3704 | ){
 3706 | SCORE += -10;
 3707 | }
 3708 | }
 3709 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 3710 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 3712 | SCORE += -10;
 3713 | return;
 3714 | }
 3715 | }
 3716 | if( DEF_tokusei == TOKUSEI_TOREESU
 3717 | || DEF_tokusei == TOKUSEI_DARUMAMOODO){
 3719 | SCORE += -10;
 3720 | return;
 3721 | }
 3722 | DefMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
 3723 | if( DefMonsNo == MONSNO_POWARUN
 3724 | || DefMonsNo == MONSNO_ARUSEUSU
 3725 | || DefMonsNo == MONSNO_THERIMU
 3726 | || DefMonsNo == MONSNO_ZOROAAKU
 3727 | || DefMonsNo == MONSNO_METAMON
 3728 | || DefMonsNo == MONSNO_NUKENIN
 3729 | || DefMonsNo == MONSNO_GIRUGARUDO
 3730 | ){
 3732 | SCORE += -10;
 3733 | return;
 3734 | }
 3736 | if( DefMonsNo == MONSNO_KEKKINGU
 3737 | || DefMonsNo == MONSNO_AAKEOSU
 3738 | || DefMonsNo == MONSNO_REZIGIGASU){
 3740 | SCORE += -12;
 3741 | return;
 3742 | }
 3743 | if(DEF_tokusei == TOKUSEI_NAMAKE
 3744 | || DEF_tokusei == TOKUSEI_YOWAKI
 3745 | || DEF_tokusei == TOKUSEI_SUROOSUTAATO){
 3747 | SCORE += -12;
 3748 | return;
 3749 | }
 3750 | }
```

### `BaciAI_Seq_300()` (source lines 3752–3761)

```text
 3752 | BaciAI_Seq_300()
 3753 | {
 3755 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 3756 | if( CHK_rule == BTL_RULE_SINGLE
 3757 | || CHK_rule == BTL_RULE_ROTATION ){
 3759 | SCORE += -10;
 3760 | }
 3761 | }
```

### `BaciAI_Seq_301()` (source lines 3763–3772)

```text
 3763 | BaciAI_Seq_301()
 3764 | {
 3772 | }
```

### `BaciAI_Seq_307()` (source lines 3774–3797)

```text
 3774 | BaciAI_Seq_307()
 3775 | {
 3777 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 3778 | if( CHK_rule == BTL_RULE_SINGLE
 3779 | || CHK_rule == BTL_RULE_ROTATION ){
 3781 | SCORE += -10;
 3782 | return;
 3783 | }
 3784 | if( AI_CMD(CMD_IF_MULTI) ){
 3786 | SCORE += -10;
 3787 | return;
 3788 | }
 3789 | if( CHK_rule == BTL_RULE_DOUBLE
 3790 | || CHK_rule == BTL_RULE_TRIPLE
 3791 | ){
 3792 | if( AI_CMD(CMD_IF_HP_EQUAL, CHECK_ATTACK_FRIEND, 0)){
 3794 | SCORE += -10;
 3795 | }
 3796 | }
 3797 | }
```

### `BaciAI_Seq_309()` (source lines 3799–3808)

```text
 3799 | BaciAI_Seq_309()
 3800 | {
 3802 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 3803 | if( CHK_rule == BTL_RULE_SINGLE
 3804 | || CHK_rule == BTL_RULE_ROTATION ){
 3806 | SCORE += -10;
 3807 | }
 3808 | }
```

### `BaciAI_Seq_311()` (source lines 3810–3834)

```text
 3810 | BaciAI_Seq_311()
 3811 | {
 3813 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 3814 | Weight = AI_CMD(CMD_GET_WEIGHT, CHECK_DEFENCE);
 3815 | if( Weight >= 2000 ){
 3817 | SCORE += -10;
 3818 | return;
 3819 | }
 3820 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_HEVHIMETARU ){
 3821 | if( Weight >= 1000 ){
 3823 | SCORE += -10;
 3824 | return;
 3825 | }
 3826 | }
 3827 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 3828 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 3830 | SCORE += -10;
 3831 | return;
 3832 | }
 3833 | }
 3834 | }
```

### `BaciAI_Seq_315()` (source lines 3836–3853)

```text
 3836 | BaciAI_Seq_315()
 3837 | {
 3839 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 3840 | if( CHK_rule == BTL_RULE_SINGLE
 3841 | || CHK_rule == BTL_RULE_ROTATION ){
 3843 | SCORE += -10;
 3844 | }
 3845 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 3846 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 3847 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 3849 | SCORE += -10;
 3850 | return;
 3851 | }
 3852 | }
 3853 | }
```

### `BaciAI_Seq_318()` (source lines 3855–3879)

```text
 3855 | BaciAI_Seq_318()
 3856 | {
 3858 | DEF_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1);
 3859 | DEF_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2);
 3860 | ATK_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE1);
 3861 | ATK_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE2);
 3862 | if(DEF_type1 == ATK_type1
 3863 | ){
 3864 | if(DEF_type2 == ATK_type2
 3865 | ){
 3867 | SCORE += -10;
 3868 | return;
 3869 | }
 3870 | }
 3871 | if(DEF_type1 == ATK_type2
 3872 | ){
 3873 | if(DEF_type2 == ATK_type1
 3874 | ){
 3876 | SCORE += -10;
 3877 | }
 3878 | }
 3879 | }
```

### `BaciAI_Seq_320()` (source lines 3881–3891)

```text
 3881 | BaciAI_Seq_320()
 3882 | {
 3884 | HIKAE_count = AI_CMD(CMD_CHECK_BENCH_COUNT, CHECK_ATTACK);
 3885 | if(HIKAE_count == 0
 3886 | ){
 3888 | SCORE += -10;
 3889 | return;
 3890 | }
 3891 | }
```

### `BaciAI_Seq_323()` (source lines 3893–3926)

```text
 3893 | BaciAI_Seq_323()
 3894 | {
 3896 | CHK_soubi = AI_CMD(CMD_CHECK_SOUBI_ITEM, CHECK_ATTACK);
 3897 | if( CHK_soubi == 0
 3898 | ){
 3900 | SCORE += -10;
 3901 | }
 3902 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 3903 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 3904 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 3906 | SCORE += -10;
 3907 | return;
 3908 | }
 3909 | }
 3910 | DefMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
 3911 | if( DefMonsNo == MONSNO_ARUSEUSU
 3912 | || DefMonsNo == MONSNO_GENOSEKUTO){
 3914 | SCORE += -10;
 3915 | }
 3916 | if( DefMonsNo == MONSNO_GIRATHINA){
 3917 | if(AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_HAKKINDAMA)){
 3919 | SCORE += -10;
 3920 | }
 3921 | }
 3922 | if( AI_CMD(CMD_IF_MEGAEVOLVED, CHECK_DEFENCE) ){
 3924 | SCORE += -10;
 3925 | }
 3926 | }
```

### `BaciAI_Seq_338()` (source lines 3928–3936)

```text
 3928 | BaciAI_Seq_338()
 3929 | {
 3931 | if( AI_CMD(CMD_IF_ATE_KINOMI, CHECK_ATTACK) ){
 3932 | return;
 3933 | }
 3935 | SCORE += -8;
 3936 | }
```

### `BaciAI_Seq_339()` (source lines 3938–4021)

```text
 3938 | BaciAI_Seq_339()
 3939 | {
 3941 | ATK_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE1);
 3942 | ATK_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE2);
 3943 | FRD_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE1);
 3944 | FRD_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE2);
 3945 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 3946 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK)
 3947 | FRD_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK_FRIEND)
 3948 | if(ATK_type1 != POKETYPE_KUSA
 3949 | && ATK_type2 != POKETYPE_KUSA){
 3950 | if( CHK_rule == BTL_RULE_DOUBLE
 3951 | || CHK_rule == BTL_RULE_TRIPLE){
 3952 | if( FRD_type1 != POKETYPE_KUSA
 3953 | && FRD_type2 != POKETYPE_KUSA){
 3955 | SCORE += -10;
 3956 | return;
 3957 | }
 3958 | else{
 3959 | if( FRD_tokusei == TOKUSEI_AMANOZYAKU){
 3961 | SCORE += -12;
 3962 | return;
 3963 | }
 3964 | if( FRD_type1 == POKETYPE_HIKOU
 3965 | || FRD_type2 == POKETYPE_HIKOU
 3966 | || FRD_tokusei == TOKUSEI_HUYUU){
 3968 | SCORE += -10;
 3969 | return;
 3970 | }
 3971 | }
 3972 | }
 3973 | else{
 3975 | SCORE += -10;
 3976 | return;
 3977 | }
 3978 | }
 3979 | else{
 3980 | if( ATK_tokusei == TOKUSEI_AMANOZYAKU){
 3982 | SCORE += -12;
 3983 | return;
 3984 | }
 3985 | if( CHK_rule == BTL_RULE_DOUBLE
 3986 | || CHK_rule == BTL_RULE_TRIPLE){
 3987 | if( FRD_type1 == POKETYPE_KUSA
 3988 | || FRD_type2 == POKETYPE_KUSA){
 3989 | if( FRD_tokusei == TOKUSEI_AMANOZYAKU){
 3991 | SCORE += -12;
 3992 | return;
 3993 | }
 3994 | }
 3995 | if( ATK_type1 == POKETYPE_HIKOU
 3996 | || ATK_type2 == POKETYPE_HIKOU
 3997 | || ATK_tokusei == TOKUSEI_HUYUU){
 3998 | if( FRD_type1 != POKETYPE_KUSA
 3999 | && FRD_type2 != POKETYPE_KUSA){
 4001 | SCORE += -10;
 4002 | return;
 4003 | }
 4004 | if( FRD_type1 == POKETYPE_HIKOU
 4005 | || FRD_type2 == POKETYPE_HIKOU
 4006 | || FRD_tokusei == TOKUSEI_HUYUU){
 4008 | SCORE += -10;
 4009 | return;
 4010 | }
 4011 | }
 4012 | }
 4013 | else if( ATK_type1 == POKETYPE_HIKOU
 4014 | || ATK_type2 == POKETYPE_HIKOU
 4015 | || ATK_tokusei == TOKUSEI_HUYUU){
 4017 | SCORE += -10;
 4018 | return;
 4019 | }
 4020 | }
 4021 | }
```

### `BaciAI_Seq_340()` (source lines 4023–4052)

```text
 4023 | BaciAI_Seq_340()
 4024 | {
 4026 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 4027 | DEF_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 4028 | HIKAE_count = AI_CMD(CMD_CHECK_BENCH_COUNT, CHECK_DEFENCE);
 4030 | if(ATK_tokusei != TOKUSEI_KATAYABURI
 4031 | && ATK_tokusei != TOKUSEI_TAABOBUREIZU
 4032 | && ATK_tokusei != TOKUSEI_TERABORUTEEZI)
 4033 | {
 4034 | if( DEF_tokusei == TOKUSEI_MAZIKKUMIRAA
 4035 | ){
 4037 | SCORE += -12;
 4038 | return;
 4039 | }
 4040 | }
 4041 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_DEFENCE, BTL_SIDEEFF_NEBANEBANET)
 4042 | ){
 4044 | SCORE += -10;
 4045 | return;
 4046 | }
 4047 | if(HIKAE_count == 0
 4048 | ){
 4050 | SCORE += -10;
 4051 | }
 4052 | }
```

### `BaciAI_Seq_342()` (source lines 4054–4079)

```text
 4054 | BaciAI_Seq_342()
 4055 | {
 4057 | DEF_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1);
 4058 | DEF_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2);
 4059 | if(DEF_type1 == POKETYPE_GHOST
 4060 | || DEF_type2 == POKETYPE_GHOST
 4061 | ){
 4063 | SCORE += -10;
 4064 | return;
 4065 | }
 4066 | if( AI_CMD(CMD_IF_TYPE_EX, CHECK_DEFENCE, POKETYPE_GHOST) ){
 4068 | SCORE += -10;
 4069 | return;
 4070 | }
 4071 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 4072 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 4073 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 4075 | SCORE += -10;
 4076 | return;
 4077 | }
 4078 | }
 4079 | }
```

### `BaciAI_Seq_375()` (source lines 4081–4106)

```text
 4081 | BaciAI_Seq_375()
 4082 | {
 4084 | DEF_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1);
 4085 | DEF_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2);
 4086 | if(DEF_type1 == POKETYPE_KUSA
 4087 | || DEF_type2 == POKETYPE_KUSA
 4088 | ){
 4090 | SCORE += -10;
 4091 | return;
 4092 | }
 4093 | if( AI_CMD(CMD_IF_TYPE_EX, CHECK_DEFENCE, POKETYPE_KUSA) ){
 4095 | SCORE += -10;
 4096 | return;
 4097 | }
 4098 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 4099 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 4100 | if( ATK_tokusei != TOKUSEI_SURINUKE ){
 4102 | SCORE += -10;
 4103 | return;
 4104 | }
 4105 | }
 4106 | }
```

### `BaciAI_Seq_349()` (source lines 4108–4117)

```text
 4108 | BaciAI_Seq_349()
 4109 | {
 4111 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 4112 | if( CHK_rule == BTL_RULE_SINGLE
 4113 | || CHK_rule == BTL_RULE_ROTATION ){
 4115 | SCORE += -5;
 4116 | }
 4117 | }
```

### `BaciAI_Seq_350()` (source lines 4119–4164)

```text
 4119 | BaciAI_Seq_350()
 4120 | {
 4122 | ATK_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE1);
 4123 | ATK_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE2);
 4124 | FRD_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE1);
 4125 | FRD_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE2);
 4126 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 4127 | if( CHK_rule == BTL_RULE_SINGLE
 4128 | || CHK_rule == BTL_RULE_ROTATION ){
 4129 | if(ATK_type1 != POKETYPE_KUSA
 4130 | && ATK_type2 != POKETYPE_KUSA){
 4132 | SCORE += -10;
 4133 | }
 4134 | else{
 4135 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_AMANOZYAKU){
 4137 | SCORE += -12;
 4138 | }
 4139 | }
 4140 | return;
 4141 | }
 4142 | if(ATK_type1 == POKETYPE_KUSA
 4143 | || ATK_type2 == POKETYPE_KUSA){
 4144 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_AMANOZYAKU){
 4146 | SCORE += -12;
 4147 | }
 4149 | }
 4150 | if( FRD_type1 == POKETYPE_KUSA
 4151 | || FRD_type2 == POKETYPE_KUSA){
 4152 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK_FRIEND) == TOKUSEI_AMANOZYAKU){
 4154 | SCORE += -12;
 4155 | }
 4156 | }
 4157 | if(ATK_type1 != POKETYPE_KUSA
 4158 | && ATK_type2 != POKETYPE_KUSA
 4159 | && FRD_type1 != POKETYPE_KUSA
 4160 | && FRD_type2 != POKETYPE_KUSA){
 4162 | SCORE += -10;
 4163 | }
 4164 | }
```

### `BaciAI_Seq_351()` (source lines 4166–4174)

```text
 4166 | BaciAI_Seq_351()
 4167 | {
 4169 | if( AI_CMD(CMD_IF_EXIST_GROUND, BTL_GROUND_GRASS) ){
 4171 | SCORE += -10;
 4172 | return;
 4173 | }
 4174 | }
```

### `BaciAI_Seq_352()` (source lines 4176–4184)

```text
 4176 | BaciAI_Seq_352()
 4177 | {
 4179 | if( AI_CMD(CMD_IF_EXIST_GROUND, BTL_GROUND_MIST) ){
 4181 | SCORE += -10;
 4182 | return;
 4183 | }
 4184 | }
```

### `BaciAI_Seq_354()` (source lines 4186–4203)

```text
 4186 | BaciAI_Seq_354()
 4187 | {
 4189 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 4190 | HIKAE_count = AI_CMD(CMD_CHECK_BENCH_COUNT, CHECK_DEFENCE);
 4191 | if(ATK_tokusei == TOKUSEI_KAGEHUMI
 4192 | ){
 4194 | SCORE += -10;
 4195 | return;
 4196 | }
 4197 | if(HIKAE_count == 0
 4198 | ){
 4200 | SCORE += -10;
 4201 | return;
 4202 | }
 4203 | }
```

### `BaciAI_Seq_362()` (source lines 4205–4221)

```text
 4205 | BaciAI_Seq_362()
 4206 | {
 4208 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 4209 | if( CHK_rule == BTL_RULE_SINGLE
 4210 | || CHK_rule == BTL_RULE_ROTATION ){
 4212 | SCORE += -20;
 4213 | return;
 4214 | }
 4216 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK_FRIEND, PARA_SPEDEF, 12) )
 4217 | {
 4219 | SCORE += -10;
 4220 | }
 4221 | }
```

### `BaciAI_Seq_363()` (source lines 4223–4235)

```text
 4223 | BaciAI_Seq_363()
 4224 | {
 4226 | if( AI_CMD(CMD_IFN_WAZASICK, CHECK_DEFENCE, WAZASICK_DOKU)
 4227 | || AI_CMD(CMD_IFN_DOKUDOKU, CHECK_DEFENCE)
 4228 | ){
 4230 | SCORE += -10;
 4231 | return;
 4232 | }
 4233 | Call BaciAI_Seq_018()
 4234 | Call BaciAI_Seq_021()
 4235 | }
```

### `BaciAI_Seq_366()` (source lines 4237–4251)

```text
 4237 | BaciAI_Seq_366()
 4238 | {
 4240 | ATK_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 4241 | FRD_tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK_FRIEND);
 4242 | if(ATK_tokusei != TOKUSEI_PURASU
 4243 | && ATK_tokusei != TOKUSEI_MAINASU
 4244 | && FRD_tokusei != TOKUSEI_PURASU
 4245 | && FRD_tokusei != TOKUSEI_MAINASU
 4246 | ){
 4248 | SCORE += -10;
 4249 | return;
 4250 | }
 4251 | }
```

### `BaciAI_Seq_368()` (source lines 4253–4261)

```text
 4253 | BaciAI_Seq_368()
 4254 | {
 4256 | if( AI_CMD(CMD_IF_EXIST_GROUND, BTL_GROUND_ELEKI) ){
 4258 | SCORE += -10;
 4259 | return;
 4260 | }
 4261 | }
```

### `BaciAI_Seq_370()` (source lines 4263–4273)

```text
 4263 | BaciAI_Seq_370()
 4264 | {
 4266 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 4267 | if( CHK_rule == BTL_RULE_SINGLE
 4268 | || CHK_rule == BTL_RULE_ROTATION ){
 4270 | SCORE += -20;
 4271 | return;
 4272 | }
 4273 | }
```

## Strong: exact guarded score rules

| Function | Source lines | Influence role | What it does | Direct score writes | Calls |
|---|---:|---|---|---|---|
| `main()` | 7–13 | indirect caller/helper on a score path | Entry point: reads the current move sequence and calls the attack-oriented evaluator. | indirect/dynamic | main_proc |
| `main_proc()` | 15–80 | direct score writer | Rewards selected finishing moves, avoids moves that compare poorly in power, and gives a randomized bonus to strongly favorable matchups; skips ally attacks in multi battles. | 3, 5, 4, -1, 2 | Strong_KinomiCheck, Strong_exception |
| `Strong_exception()` | 82–121 | reachable dispatcher/predicate support | Suppresses normal power scoring for special species/ability combinations where the generic comparison would be misleading. | indirect/dynamic | — |
| `Strong_KinomiCheck()` | 123–215 | direct score writer | Detects type-resist Berries and selected Ground-immunity cases so the normal attack-power evaluation can be bypassed or penalized. | -3 | — |

The complete guarded bodies follow:

### `main()` (source lines 7–13)

```text
    7 | main()
    8 | {
    9 | waza_seq_no = AI_CMD(CMD_CHECK_WORKWAZA_SEQNO);
   11 | main_proc();
   13 | }
```

### `main_proc()` (source lines 15–80)

```text
   15 | main_proc()
   16 | {
   17 | waza_seq_no = AI_CMD(CMD_CHECK_WORKWAZA_SEQNO);
   20 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
   21 | if( CHK_rule == BTL_RULE_DOUBLE
   22 | || CHK_rule == BTL_RULE_TRIPLE ){
   23 | if( AI_CMD(CMD_IF_MIKATA_ATTACK)){
   24 | return;
   25 | }
   26 | }
   27 | if( AI_CMD(CMD_IF_WAZA_HINSHI, LOSS_CALC_OFF) ){
   28 | if( waza_seq_no == 7
   29 | || waza_seq_no == 170
   30 | || waza_seq_no == 248
   31 | || waza_seq_no == 148){
   32 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
   34 | SCORE += 3;
   35 | }
   36 | }
   37 | else {
   38 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
   40 | SCORE += 3;
   41 | }
   42 | }
   43 | if( waza_seq_no == 103
   44 | || waza_seq_no == 360){
   45 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
   47 | SCORE += 5;
   48 | }
   49 | }
   50 | if( waza_seq_no == 341 ){
   51 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
   53 | SCORE += 4;
   54 | }
   55 | }
   56 | }
   57 | if ( Strong_exception() == 0 ){
   58 | if ( Strong_KinomiCheck() == 0 ){
   59 | PowerCheck = AI_CMD(CMD_COMP_POWER, LOSS_CALC_OFF);
   60 | if( PowerCheck == COMP_POWER_NOTOP ){
   62 | SCORE += -1;
   63 | }
   64 | }
   65 | }
   74 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_4BAI) ){
   75 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
   77 | SCORE += 2;
   78 | }
   79 | }
   80 | }
```

### `Strong_exception()` (source lines 82–121)

```text
   82 | Strong_exception()
   83 | {
   84 | WazaType = AI_CMD(CMD_CHECK_TYPE, CHECK_WAZA);
   85 | DefMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
   86 | DefTokusei1 = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
   87 | DefTokusei2 = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
   88 | DefTokusei3 = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
   89 | DefTokusei4 = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
   90 | if( AI_CMD(CMD_CHECK_DAMAGE_WAZA, CURRENT_MOVE())){
   91 | if( DefTokusei1 != DefTokusei2
   92 | || DefTokusei2 != DefTokusei3
   93 | || DefTokusei3 != DefTokusei4 ){
   94 | if( WazaType == POKETYPE_HONOO
   95 | || WazaType == POKETYPE_KOORI){
   96 | if( DefMonsNo == MONSNO_PAUWAU || DefMonsNo == MONSNO_ZYUGON
   97 | || DefMonsNo == MONSNO_MARIRU || DefMonsNo == MONSNO_MARIRURI
   98 | || DefMonsNo == MONSNO_MIRUTANKU || DefMonsNo == MONSNO_MAKUNOSITA
   99 | || DefMonsNo == MONSNO_HARITEYAMA || DefMonsNo == MONSNO_RURIRI
  100 | || DefMonsNo == MONSNO_BANEBUU || DefMonsNo == MONSNO_BUUPIGGU
  101 | || DefMonsNo == MONSNO_TAMAZARASI || DefMonsNo == MONSNO_TODOGURAA
  102 | || DefMonsNo == MONSNO_TODOZERUGA || DefMonsNo == MONSNO_BUNYATTO
  103 | || DefMonsNo == MONSNO_KABIGON || DefMonsNo == MONSNO_GONBE
  104 | || DefMonsNo == MONSNO_URIMUU || DefMonsNo == MONSNO_INOMUU
  105 | || DefMonsNo == MONSNO_MANMUU || DefMonsNo == MONSNO_POKABU
  106 | || DefMonsNo == MONSNO_TYAOBUU ){
  108 | return 1;
  109 | }
  110 | }
  111 | if( WazaType == POKETYPE_JIMEN
  112 | || WazaType == POKETYPE_HONOO){
  113 | if( DefMonsNo == MONSNO_DOOTAKUN){
  115 | return 1;
  116 | }
  117 | }
  118 | }
  119 | }
  120 | return 0;
  121 | }
```

### `Strong_KinomiCheck()` (source lines 123–215)

```text
  123 | Strong_KinomiCheck()
  124 | {
  125 | WazaType = AI_CMD(CMD_CHECK_TYPE, CHECK_WAZA);
  126 | if( WazaType == POKETYPE_AKU
  127 | && AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_NAMONOMI)){
  128 | return 1;
  129 | }
  130 | if( WazaType == POKETYPE_IWA
  131 | && AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_YOROGINOMI)){
  132 | return 1;
  133 | }
  134 | if( WazaType == POKETYPE_ESPER
  135 | && AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_UTANNOMI)){
  136 | return 1;
  137 | }
  138 | if( WazaType == POKETYPE_KAKUTOU
  139 | && AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_YOPUNOMI)){
  140 | return 1;
  141 | }
  142 | if( WazaType == POKETYPE_KUSA
  143 | && AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_RINDONOMI)){
  144 | return 1;
  145 | }
  146 | if( WazaType == POKETYPE_GHOST
  147 | && AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_KASIBUNOMI)){
  148 | return 1;
  149 | }
  150 | if( WazaType == POKETYPE_KOORI
  151 | && AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_YATHENOMI)){
  152 | return 1;
  153 | }
  154 | if( WazaType == POKETYPE_JIMEN
  155 | && AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_SYUKANOMI)){
  156 | return 1;
  157 | }
  158 | if( WazaType == POKETYPE_DENKI
  159 | && AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_SOKUNONOMI)){
  160 | return 1;
  161 | }
  162 | if( WazaType == POKETYPE_DOKU
  163 | && AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_BIAANOMI)){
  164 | return 1;
  165 | }
  166 | if( WazaType == POKETYPE_DRAGON
  167 | && AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_HABANNOMI)){
  168 | return 1;
  169 | }
  170 | if( WazaType == POKETYPE_NORMAL
  171 | && AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_HOZUNOMI)){
  172 | return 1;
  173 | }
  174 | if( WazaType == POKETYPE_HAGANE
  175 | && AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_RIRIBANOMI)){
  176 | return 1;
  177 | }
  178 | if( WazaType == POKETYPE_HIKOU
  179 | && AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_BAKOUNOMI)){
  180 | return 1;
  181 | }
  182 | if( WazaType == POKETYPE_FAIRY
  183 | && AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_ROZERUNOMI)){
  184 | return 1;
  185 | }
  186 | if( WazaType == POKETYPE_HONOO
  187 | && AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_OKKANOMI)){
  188 | return 1;
  189 | }
  190 | if( WazaType == POKETYPE_MIZU
  191 | && AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_ITOKENOMI)){
  192 | return 1;
  193 | }
  194 | if( WazaType == POKETYPE_MUSHI
  195 | && AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_TANGANOMI)){
  196 | return 1;
  197 | }
  198 | if( WazaType == POKETYPE_JIMEN ){
  199 | if (AI_CMD(CMD_FLDEFF_CHECK, EFF_JURYOKU)){
  200 | return 0;
  201 | }
  202 | ATK_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
  203 | if( ATK_Tokusei != TOKUSEI_KATAYABURI
  204 | && ATK_Tokusei != TOKUSEI_TAABOBUREIZU
  205 | && ATK_Tokusei != TOKUSEI_TERABORUTEEZI){
  206 | if (AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_HUYUU
  207 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) == POKETYPE_HIKOU
  208 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) == POKETYPE_HIKOU ){
  209 | SCORE += -3;
  210 | return 1;
  211 | }
  212 | }
  213 | }
  214 | return 0;
  215 | }
```

## Expert: exact guarded score rules

| Function | Source lines | Influence role | What it does | Direct score writes | Calls |
|---|---:|---|---|---|---|
| `main()` | 7–14 | indirect caller/helper on a score path | Evaluates a expert rule using the native battle-state interface; applies no direct score write under the guarded conditions below. | indirect/dynamic | main_proc |
| `main_proc()` | 16–326 | direct score writer | Evaluates a expert rule using battle-rule state, ally attack state, held items, move category, random gates; applies -1, 2 under the guarded conditions below. | -1, 2 | ExpertAI_Seq_001, ExpertAI_Seq_003, ExpertAI_Seq_007, ExpertAI_Seq_008, ExpertAI_Seq_009, ExpertAI_Seq_010, ExpertAI_Seq_011, ExpertAI_Seq_012, ExpertAI_Seq_013, ExpertAI_Seq_014, ExpertAI_Seq_015, ExpertAI_Seq_016, ExpertAI_Seq_017, ExpertAI_Seq_018, ExpertAI_Seq_019, ExpertAI_Seq_020, ExpertAI_Seq_021, ExpertAI_Seq_022, ExpertAI_Seq_023, ExpertAI_Seq_024, ExpertAI_Seq_025, ExpertAI_Seq_026, ExpertAI_Seq_028, ExpertAI_Seq_030, ExpertAI_Seq_032, ExpertAI_Seq_033, ExpertAI_Seq_035, ExpertAI_Seq_037, ExpertAI_Seq_038, ExpertAI_Seq_039, ExpertAI_Seq_040, ExpertAI_Seq_042, ExpertAI_Seq_043, ExpertAI_Seq_048, ExpertAI_Seq_049, ExpertAI_Seq_065, ExpertAI_Seq_067, ExpertAI_Seq_070, ExpertAI_Seq_078, ExpertAI_Seq_079, ExpertAI_Seq_080, ExpertAI_Seq_086, ExpertAI_Seq_087, ExpertAI_Seq_089, ExpertAI_Seq_090, ExpertAI_Seq_091, ExpertAI_Seq_092, ExpertAI_Seq_094, ExpertAI_Seq_098, ExpertAI_Seq_099, ExpertAI_Seq_102, ExpertAI_Seq_105, ExpertAI_Seq_108, ExpertAI_Seq_109, ExpertAI_Seq_111, ExpertAI_Seq_112, ExpertAI_Seq_113, ExpertAI_Seq_116, ExpertAI_Seq_118, ExpertAI_Seq_120, ExpertAI_Seq_121, ExpertAI_Seq_123, ExpertAI_Seq_127, ExpertAI_Seq_128, ExpertAI_Seq_132, ExpertAI_Seq_135, ExpertAI_Seq_136, ExpertAI_Seq_137, ExpertAI_Seq_142, ExpertAI_Seq_143, ExpertAI_Seq_152, ExpertAI_Seq_155, ExpertAI_Seq_158, ExpertAI_Seq_160, ExpertAI_Seq_161, ExpertAI_Seq_164, ExpertAI_Seq_165, ExpertAI_Seq_166, ExpertAI_Seq_167, ExpertAI_Seq_169, ExpertAI_Seq_170, ExpertAI_Seq_171, ExpertAI_Seq_173, ExpertAI_Seq_175, ExpertAI_Seq_177, ExpertAI_Seq_178, ExpertAI_Seq_183, ExpertAI_Seq_184, ExpertAI_Seq_185, ExpertAI_Seq_186, ExpertAI_Seq_187, ExpertAI_Seq_188, ExpertAI_Seq_190, ExpertAI_Seq_191, ExpertAI_Seq_192, ExpertAI_Seq_196, ExpertAI_Seq_203, ExpertAI_Seq_210, ExpertAI_Seq_212, ExpertAI_Seq_215, ExpertAI_Seq_218, ExpertAI_Seq_219, ExpertAI_Seq_220, ExpertAI_Seq_221, ExpertAI_Seq_222, ExpertAI_Seq_227, ExpertAI_Seq_228, ExpertAI_Seq_229, ExpertAI_Seq_230, ExpertAI_Seq_233, ExpertAI_Seq_237, ExpertAI_Seq_239, ExpertAI_Seq_240, ExpertAI_Seq_241, ExpertAI_Seq_242, ExpertAI_Seq_243, ExpertAI_Seq_244, ExpertAI_Seq_245, ExpertAI_Seq_246, ExpertAI_Seq_247, ExpertAI_Seq_248, ExpertAI_Seq_249, ExpertAI_Seq_250, ExpertAI_Seq_251, ExpertAI_Seq_252, ExpertAI_Seq_258, ExpertAI_Seq_259, ExpertAI_Seq_265, ExpertAI_Seq_266, ExpertAI_Seq_268, ExpertAI_Seq_270, ExpertAI_Seq_272, ExpertAI_Seq_278, ExpertAI_Seq_279, ExpertAI_Seq_280, ExpertAI_Seq_283, ExpertAI_Seq_284, ExpertAI_Seq_285, ExpertAI_Seq_286, ExpertAI_Seq_287, ExpertAI_Seq_288, ExpertAI_Seq_289, ExpertAI_Seq_290, ExpertAI_Seq_291, ExpertAI_Seq_292, ExpertAI_Seq_293, ExpertAI_Seq_294, ExpertAI_Seq_295, ExpertAI_Seq_296, ExpertAI_Seq_297, ExpertAI_Seq_298, ExpertAI_Seq_299, ExpertAI_Seq_300, ExpertAI_Seq_301, ExpertAI_Seq_302, ExpertAI_Seq_303, ExpertAI_Seq_304, ExpertAI_Seq_305, ExpertAI_Seq_306, ExpertAI_Seq_308, ExpertAI_Seq_310, ExpertAI_Seq_314, ExpertAI_Seq_316, ExpertAI_Seq_317, ExpertAI_Seq_318, ExpertAI_Seq_319, ExpertAI_Seq_320, ExpertAI_Seq_323, ExpertAI_Seq_329, ExpertAI_Seq_334, ExpertAI_Seq_335, ExpertAI_Seq_336, ExpertAI_Seq_337, ExpertAI_Seq_338, ExpertAI_Seq_340, ExpertAI_Seq_342, ExpertAI_Seq_344, ExpertAI_Seq_346, ExpertAI_Seq_347, ExpertAI_Seq_349, ExpertAI_Seq_350, ExpertAI_Seq_351, ExpertAI_Seq_352, ExpertAI_Seq_353, ExpertAI_Seq_354, ExpertAI_Seq_359, ExpertAI_Seq_363, ExpertAI_Seq_365, ExpertAI_Seq_366, ExpertAI_Seq_368, ExpertAI_Seq_372, ExpertAI_Seq_373, ExpertAI_Seq_374, ExpertAI_Seq_377, ExpertAI_Seq_379 |
| `ExpertAI_Seq_001()` | 330–383 | direct score writer | Evaluates Expert move sequence 001; uses random gates, abilities and applies 1, -2, -1, 2 when the guarded conditions below succeed. | 1, -2, -1, 2 | — |
| `ExpertAI_Seq_003()` | 385–396 | direct score writer | Evaluates Expert move sequence 003; uses abilities, random gates and applies -2 when the guarded conditions below succeed. | -2 | — |
| `ExpertAI_Seq_007()` | 398–457 | direct score writer | Evaluates Expert move sequence 007; uses random gates, HP thresholds, speed/order state and applies -1, -2, 3, 2 when the guarded conditions below succeed. | -1, -2, 3, 2 | — |
| `ExpertAI_Seq_008()` | 459–491 | direct score writer | Evaluates Expert move sequence 008; uses type effectiveness, random gates, abilities and applies -2, -1, 3 when the guarded conditions below succeed. | -2, -1, 3 | — |
| `ExpertAI_Seq_009()` | 493–510 | direct score writer | Evaluates Expert move sequence 009; uses speed/order state, random gates and applies -1, 2 when the guarded conditions below succeed. | -1, 2 | ExpertAI_Seq_009_sub |
| `ExpertAI_Seq_009_sub()` | 511–544 | reachable dispatcher/predicate support | Evaluates Expert move sequence 009 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_010()` | 546–583 | direct score writer | Evaluates Expert move sequence 010; uses random gates, HP thresholds and applies -1, 2, -2 when the guarded conditions below succeed. | -1, 2, -2 | — |
| `ExpertAI_Seq_011()` | 585–636 | direct score writer | Evaluates Expert move sequence 011; uses HP thresholds, random gates and applies -2, -1, 2 when the guarded conditions below succeed. | -2, -1, 2 | — |
| `ExpertAI_Seq_012()` | 638–706 | direct score writer | Evaluates Expert move sequence 012; uses speed/order state, random gates and applies -5, 1 when the guarded conditions below succeed. | -5, 1 | — |
| `ExpertAI_Seq_013()` | 708–745 | direct score writer | Evaluates Expert move sequence 013; uses random gates, HP thresholds and applies -1, 2, -2 when the guarded conditions below succeed. | -1, 2, -2 | — |
| `ExpertAI_Seq_014()` | 747–798 | direct score writer | Evaluates Expert move sequence 014; uses HP thresholds, random gates, move category and applies -2, -1, 2 when the guarded conditions below succeed. | -2, -1, 2 | — |
| `ExpertAI_Seq_015()` | 800–815 | direct score writer | Evaluates Expert move sequence 015; uses random gates, HP thresholds and applies -2 when the guarded conditions below succeed. | -2 | — |
| `ExpertAI_Seq_016()` | 818–978 | direct score writer | Evaluates Expert move sequence 016; uses abilities, weather, available moves, random gates, held items and applies -2, 1, 2, -1 when the guarded conditions below succeed. | -2, 1, 2, -1 | ExpertAI_Seq_016_sub1, ExpertAI_Seq_016_sub2, ExpertAI_Seq_016_sub3, ExpertAI_Seq_016_sub4 |
| `ExpertAI_Seq_016_sub1()` | 981–999 | reachable dispatcher/predicate support | Evaluates Expert move sequence 016 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_016_sub2()` | 1000–1018 | reachable dispatcher/predicate support | Evaluates Expert move sequence 016 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_016_sub3()` | 1019–1052 | reachable dispatcher/predicate support | Evaluates Expert move sequence 016; uses abilities, weather and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_016_sub4()` | 1053–1086 | reachable dispatcher/predicate support | Evaluates Expert move sequence 016; uses abilities, weather and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_017()` | 1088–1115 | direct score writer | Evaluates Expert move sequence 017; uses type effectiveness, random gates and applies 2 when the guarded conditions below succeed. | 2 | — |
| `ExpertAI_Seq_018()` | 1117–1144 | direct score writer | Evaluates Expert move sequence 018; uses random gates, HP thresholds and applies -1, -2 when the guarded conditions below succeed. | -1, -2 | — |
| `ExpertAI_Seq_019()` | 1146–1167 | direct score writer | Evaluates Expert move sequence 019; uses random gates, HP thresholds and applies -1, -2 when the guarded conditions below succeed. | -1, -2 | — |
| `ExpertAI_Seq_020()` | 1170–1183 | direct score writer | Evaluates Expert move sequence 020; uses speed/order state, random gates and applies -3, 2 when the guarded conditions below succeed. | -3, 2 | — |
| `ExpertAI_Seq_021()` | 1185–1212 | direct score writer | Evaluates Expert move sequence 021; uses random gates, HP thresholds and applies -1, -2 when the guarded conditions below succeed. | -1, -2 | — |
| `ExpertAI_Seq_022()` | 1214–1235 | direct score writer | Evaluates Expert move sequence 022; uses random gates, HP thresholds and applies -1, -2 when the guarded conditions below succeed. | -1, -2 | — |
| `ExpertAI_Seq_023()` | 1237–1391 | direct score writer | Evaluates Expert move sequence 023; uses abilities, weather, available moves, random gates, held items and applies -3, -2, 1, 2, -1 when the guarded conditions below succeed. | -3, -2, 1, 2, -1 | ExpertAI_Seq_016_sub1, ExpertAI_Seq_016_sub2, ExpertAI_Seq_016_sub3, ExpertAI_Seq_016_sub4 |
| `ExpertAI_Seq_024()` | 1393–1414 | direct score writer | Evaluates Expert move sequence 024; uses random gates, HP thresholds and applies -1, -2 when the guarded conditions below succeed. | -1, -2 | — |
| `ExpertAI_Seq_025()` | 1416–1462 | direct score writer | Evaluates Expert move sequence 025; uses random gates and applies -3, 2 when the guarded conditions below succeed. | -3, 2 | — |
| `ExpertAI_Seq_026()` | 1464–1473 | direct score writer | Evaluates Expert move sequence 026; uses HP thresholds, random gates and applies -2 when the guarded conditions below succeed. | -2 | — |
| `ExpertAI_Seq_028()` | 1475–1532 | direct score writer | Evaluates Expert move sequence 028; uses random gates and applies 2, 1 when the guarded conditions below succeed. | 2, 1 | — |
| `ExpertAI_Seq_030()` | 1534–1543 | direct score writer | Evaluates Expert move sequence 030; uses HP thresholds, random gates and applies -2 when the guarded conditions below succeed. | -2 | — |
| `ExpertAI_Seq_032()` | 1546–1597 | direct score writer | Evaluates Expert move sequence 032; uses HP thresholds, random gates, abilities, speed/order state, available moves and applies 2, -5, -4, -2 when the guarded conditions below succeed. | 2, -5, -4, -2 | — |
| `ExpertAI_Seq_033()` | 1599–1633 | direct score writer | Evaluates Expert move sequence 033; uses available damaging moves, random gates, HP thresholds and applies 2, -1, 1 when the guarded conditions below succeed. | 2, -1, 1 | — |
| `ExpertAI_Seq_035()` | 1635–1661 | direct score writer | Evaluates Expert move sequence 035; uses HP thresholds, random gates, physical/special damage type and applies 2, -2, -3, 1 when the guarded conditions below succeed. | 2, -2, -3, 1 | — |
| `ExpertAI_Seq_037()` | 1663–1714 | direct score writer | Evaluates Expert move sequence 037; uses HP thresholds, abilities, speed/order state, random gates, available moves, and other state and applies -5, -4, 2, -2 when the guarded conditions below succeed. | -5, -4, 2, -2 | — |
| `ExpertAI_Seq_038()` | 1716–1729 | direct score writer | Evaluates Expert move sequence 038; uses random gates and applies 2, 1 when the guarded conditions below succeed. | 2, 1 | — |
| `ExpertAI_Seq_039()` | 1731–1795 | direct score writer | Evaluates Expert move sequence 039; uses type effectiveness, random gates, weather, held items, HP thresholds, and other state and applies -2, 2, -1 when the guarded conditions below succeed. | -2, 2, -1 | — |
| `ExpertAI_Seq_040()` | 1797–1836 | direct score writer | Evaluates Expert move sequence 040; uses HP thresholds, random gates and applies -1, 1 when the guarded conditions below succeed. | -1, 1 | — |
| `ExpertAI_Seq_042()` | 1838–1864 | direct score writer | Evaluates Expert move sequence 042; uses abilities, random gates and applies 1, 2 when the guarded conditions below succeed. | 1, 2 | ExpertAI_Seq_016_sub2, ExpertAI_Seq_016_sub4 |
| `ExpertAI_Seq_043()` | 1866–1897 | direct score writer | Evaluates Expert move sequence 043; uses type effectiveness, random gates, move category and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_048()` | 1899–1912 | direct score writer | Evaluates Expert move sequence 048; uses abilities, HP thresholds, random gates and applies -1 when the guarded conditions below succeed. | -1 | — |
| `ExpertAI_Seq_049()` | 1915–1930 | direct score writer | Evaluates Expert move sequence 049; uses HP thresholds, random gates and applies 1, -1 when the guarded conditions below succeed. | 1, -1 | — |
| `ExpertAI_Seq_065()` | 1933–1959 | direct score writer | Evaluates Expert move sequence 065; uses HP thresholds, random gates, physical/special damage type and applies 2, -2, -3, 1 when the guarded conditions below succeed. | 2, -2, -3, 1 | — |
| `ExpertAI_Seq_067()` | 1961–1979 | direct score writer | Evaluates Expert move sequence 067; uses speed/order state, HP thresholds, random gates and applies 3, -1 when the guarded conditions below succeed. | 3, -1 | — |
| `ExpertAI_Seq_070()` | 1981–1998 | indirect caller/helper on a score path | Evaluates Expert move sequence 070; uses type effectiveness and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | ExpertAI_Seq_020 |
| `ExpertAI_Seq_078()` | 2000–2014 | direct score writer | Evaluates Expert move sequence 078; uses speed/order state, random gates, HP thresholds and applies -1, -2 when the guarded conditions below succeed. | -1, -2 | ExpertAI_Seq_017 |
| `ExpertAI_Seq_079()` | 2016–2122 | direct score writer | Evaluates Expert move sequence 079; uses types, available moves, random gates, HP thresholds, abilities, and other state and applies 1, 2, -1 when the guarded conditions below succeed. | 1, 2, -1 | — |
| `ExpertAI_Seq_080()` | 2124–2156 | direct score writer | Evaluates Expert move sequence 080; uses type effectiveness, abilities, random gates, speed/order state, HP thresholds and applies 1, -1 when the guarded conditions below succeed. | 1, -1 | — |
| `ExpertAI_Seq_086()` | 2158–2265 | direct score writer | Evaluates Expert move sequence 086; uses abilities, speed/order state, random gates, move lock/status state, types and applies -1, 2 when the guarded conditions below succeed. | -1, 2 | — |
| `ExpertAI_Seq_087()` | 2267–2280 | direct score writer | Evaluates Expert move sequence 087; uses HP thresholds, random gates and applies 3, 1 when the guarded conditions below succeed. | 3, 1 | — |
| `ExpertAI_Seq_089()` | 2282–2329 | direct score writer | Evaluates Expert move sequence 089; uses random gates, HP thresholds and applies -3, -1, -2, 2 when the guarded conditions below succeed. | -3, -1, -2, 2 | — |
| `ExpertAI_Seq_090()` | 2331–2344 | direct score writer | Evaluates Expert move sequence 090; uses abilities, speed/order state, random gates and applies 1 when the guarded conditions below succeed. | 1 | ExpertAI_Seq_090_sub |
| `ExpertAI_Seq_090_sub()` | 2345–2364 | reachable dispatcher/predicate support | Evaluates Expert move sequence 090 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_091()` | 2366–2409 | direct score writer | Evaluates Expert move sequence 091; uses HP thresholds, random gates, abilities, speed/order state and applies -2, -1, 3, 1 when the guarded conditions below succeed. | -2, -1, 3, 1 | — |
| `ExpertAI_Seq_092()` | 2411–2418 | direct score writer | Evaluates Expert move sequence 092; uses random gates and applies 2 when the guarded conditions below succeed. | 2 | — |
| `ExpertAI_Seq_094()` | 2420–2436 | direct score writer | Evaluates Expert move sequence 094; uses available moves, random gates and applies -2, 2 when the guarded conditions below succeed. | -2, 2 | — |
| `ExpertAI_Seq_098()` | 2438–2481 | direct score writer | Evaluates Expert move sequence 098; uses abilities, speed/order state, HP thresholds, random gates and applies -2, 1, -1 when the guarded conditions below succeed. | -2, 1, -1 | — |
| `ExpertAI_Seq_099()` | 2483–2514 | direct score writer | Evaluates Expert move sequence 099; uses speed/order state, HP thresholds, random gates and applies -2, 1, -1 when the guarded conditions below succeed. | -2, 1, -1 | — |
| `ExpertAI_Seq_102()` | 2516–2557 | direct score writer | Evaluates Expert move sequence 102; uses random gates, HP thresholds, battle-rule state and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_105()` | 2559–2611 | direct score writer | Evaluates Expert move sequence 105; uses abilities, random gates, species, held items and applies 1, -1, -5 when the guarded conditions below succeed. | 1, -1, -5 | ExpertAI_Seq_GoodItemPokemon, ExpertAI_Seq_MegaShinkaPokemon |
| `ExpertAI_Seq_GoodItemPokemon()` | 2614–2623 | reachable dispatcher/predicate support | Evaluates a expert rule using species; applies no direct score write under the guarded conditions below. | indirect/dynamic | — |
| `ExpertAI_Seq_108()` | 2627–2661 | direct score writer | Evaluates Expert move sequence 108; uses available moves, random gates and applies -2 when the guarded conditions below succeed. | -2 | ExpertAI_Seq_016 |
| `ExpertAI_Seq_109()` | 2663–2700 | direct score writer | Evaluates Expert move sequence 109; uses types, HP thresholds, random gates, available moves, field effects and applies -1, 1 when the guarded conditions below succeed. | -1, 1 | — |
| `ExpertAI_Seq_111()` | 2702–2772 | direct score writer | Evaluates Expert move sequence 111; uses held items, HP thresholds, random gates, available moves, abilities, and other state and applies -3, -1, -2, 1, 2 when the guarded conditions below succeed. | -3, -1, -2, 1, 2 | ExpertAI_Seq_016_sub3, ExpertAI_Seq_016_sub4 |
| `ExpertAI_Seq_112()` | 2774–2788 | direct score writer | Evaluates Expert move sequence 112; uses random gates and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_113()` | 2790–2808 | direct score writer | Evaluates Expert move sequence 113; uses types, random gates and applies 2 when the guarded conditions below succeed. | 2 | — |
| `ExpertAI_Seq_116()` | 2810–2835 | direct score writer | Evaluates Expert move sequence 116; uses random gates, HP thresholds, abilities, shared partner randomness and applies -4, -3, -5, 2 when the guarded conditions below succeed. | -4, -3, -5, 2 | ExpertAI_Seq_016_sub3 |
| `ExpertAI_Seq_118()` | 2837–2848 | direct score writer | Evaluates Expert move sequence 118; uses random gates and applies -2 when the guarded conditions below succeed. | -2 | ExpertAI_Seq_049 |
| `ExpertAI_Seq_120()` | 2850–2858 | direct score writer | Evaluates Expert move sequence 120; uses random gates and applies 1 when the guarded conditions below succeed. | 1 | ExpertAI_Seq_049 |
| `ExpertAI_Seq_121()` | 2860–2881 | direct score writer | Evaluates Expert move sequence 121; uses type effectiveness, random gates and applies -1, 1, 2 when the guarded conditions below succeed. | -1, 1, 2 | — |
| `ExpertAI_Seq_123()` | 2883–2904 | direct score writer | Evaluates Expert move sequence 123; uses type effectiveness, random gates and applies -1, 1, 2 when the guarded conditions below succeed. | -1, 1, 2 | — |
| `ExpertAI_Seq_127()` | 2906–2952 | direct score writer | Evaluates Expert move sequence 127; uses speed/order state, HP thresholds, random gates and applies 1, 3 when the guarded conditions below succeed. | 1, 3 | — |
| `ExpertAI_Seq_128()` | 2954–2981 | direct score writer | Evaluates Expert move sequence 128; uses types, random gates and applies 2, 1 when the guarded conditions below succeed. | 2, 1 | — |
| `ExpertAI_Seq_132()` | 2983–2997 | direct score writer | Evaluates Expert move sequence 132; uses weather, random gates and applies -2 when the guarded conditions below succeed. | -2 | ExpertAI_Seq_032 |
| `ExpertAI_Seq_135()` | 2999–3004 | indirect caller/helper on a score path | Evaluates Expert move sequence 135 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | ExpertAI_TypeCheck |
| `ExpertAI_TypeCheck(WazaType)` | 3006–3639 | direct score writer | Evaluates a expert rule using types, abilities; applies -10, -1, 1 under the guarded conditions below. | -10, -1, 1 | — |
| `ExpertAI_Seq_136()` | 3641–3657 | direct score writer | Evaluates Expert move sequence 136; uses weather, random gates and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_137()` | 3659–3675 | direct score writer | Evaluates Expert move sequence 137; uses weather, random gates and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_142()` | 3677–3686 | direct score writer | Evaluates Expert move sequence 142; uses HP thresholds, random gates and applies -2 when the guarded conditions below succeed. | -2 | — |
| `ExpertAI_Seq_143()` | 3688–3713 | direct score writer | Evaluates Expert move sequence 143; uses random gates and applies -2, 1 when the guarded conditions below succeed. | -2, 1 | — |
| `ExpertAI_Seq_152()` | 3764–3773 | direct score writer | Evaluates Expert move sequence 152; uses random gates and applies 2 when the guarded conditions below succeed. | 2 | — |
| `ExpertAI_Seq_155()` | 3775–3804 | direct score writer | Evaluates Expert move sequence 155; uses held items, random gates and applies -1 when the guarded conditions below succeed. | -1 | ExpertAI_Seq_272 |
| `ExpertAI_Seq_158()` | 3806–3813 | direct score writer | Evaluates Expert move sequence 158; uses random gates and applies 2 when the guarded conditions below succeed. | 2 | — |
| `ExpertAI_Seq_160()` | 3815–3840 | direct score writer | Evaluates Expert move sequence 160; uses HP thresholds, random gates and applies 2, -2, -1 when the guarded conditions below succeed. | 2, -2, -1 | — |
| `ExpertAI_Seq_161()` | 3842–3851 | direct score writer | Evaluates Expert move sequence 161; uses random gates and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_164()` | 3853–3869 | direct score writer | Evaluates Expert move sequence 164; uses weather, random gates and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_165()` | 3871–3881 | direct score writer | Evaluates Expert move sequence 165; uses HP thresholds, random gates and applies -1 when the guarded conditions below succeed. | -1 | — |
| `ExpertAI_Seq_166()` | 3883–3894 | direct score writer | Evaluates Expert move sequence 166; uses random gates and applies -2 when the guarded conditions below succeed. | -2 | ExpertAI_Seq_049 |
| `ExpertAI_Seq_167()` | 3896–3936 | direct score writer | Evaluates Expert move sequence 167; uses available damaging moves, random gates, abilities, species, HP thresholds and applies 2, -12, -5, -1, 1 when the guarded conditions below succeed. | 2, -12, -5, -1, 1 | — |
| `ExpertAI_Seq_169()` | 3938–3963 | direct score writer | Evaluates Expert move sequence 169; uses type effectiveness, random gates and applies 2 when the guarded conditions below succeed. | 2 | — |
| `ExpertAI_Seq_170()` | 3965–4014 | direct score writer | Evaluates Expert move sequence 170; uses type effectiveness, random gates and applies 2, 1, -1 when the guarded conditions below succeed. | 2, 1, -1 | — |
| `ExpertAI_Seq_171()` | 4016–4030 | direct score writer | Evaluates Expert move sequence 171; uses type effectiveness, random gates and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_173()` | 4032–4046 | indirect caller/helper on a score path | Evaluates Expert move sequence 173 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | ExpertAI_TypeCheck |
| `ExpertAI_Seq_175()` | 4048–4074 | direct score writer | Evaluates Expert move sequence 175; uses species, random gates, HP thresholds and applies 1, -2, -1 when the guarded conditions below succeed. | 1, -2, -1 | ExpertAI_Seq_HenkaWazaPokemon |
| `ExpertAI_Seq_HenkaWazaPokemon()` | 4076–4119 | reachable dispatcher/predicate support | Evaluates a expert rule using species; applies no direct score write under the guarded conditions below. | indirect/dynamic | — |
| `ExpertAI_Seq_177()` | 4121–4212 | direct score writer | Evaluates Expert move sequence 177; uses held items, random gates, available moves, abilities, types and applies -2, -5, -1, 2 when the guarded conditions below succeed. | -2, -5, -1, 2 | ExpertAI_Seq_HenkaWazaPokemon, ExpertAI_Seq_MegaShinkaPokemon |
| `ExpertAI_Seq_MegaShinkaPokemon()` | 4214–4235 | reachable dispatcher/predicate support | Evaluates a expert rule using species; applies no direct score write under the guarded conditions below. | indirect/dynamic | — |
| `ExpertAI_Seq_178()` | 4238–4255 | direct score writer | Evaluates Expert move sequence 178; uses random gates, abilities and applies 1 when the guarded conditions below succeed. | 1 | ExpertAI_Seq_CopyPokemonTokusei |
| `ExpertAI_Seq_CopyPokemonTokusei()` | 4257–4293 | reachable dispatcher/predicate support | Evaluates a expert rule using species; applies no direct score write under the guarded conditions below. | indirect/dynamic | — |
| `ExpertAI_Seq_183()` | 4295–4305 | direct score writer | Evaluates Expert move sequence 183; uses species, random gates and applies 1 when the guarded conditions below succeed. | 1 | ExpertAI_Seq_ReturnWazaPokemon |
| `ExpertAI_Seq_ReturnWazaPokemon()` | 4308–4333 | reachable dispatcher/predicate support | Evaluates a expert rule using species; applies no direct score write under the guarded conditions below. | indirect/dynamic | — |
| `ExpertAI_Seq_184()` | 4335–4342 | direct score writer | Evaluates Expert move sequence 184; uses random gates and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_185()` | 4344–4369 | direct score writer | Evaluates Expert move sequence 185; uses random gates and applies -2, -1, 1 when the guarded conditions below succeed. | -2, -1, 1 | — |
| `ExpertAI_Seq_186()` | 4371–4386 | direct score writer | Evaluates Expert move sequence 186; uses random gates and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_187()` | 4388–4396 | direct score writer | Evaluates Expert move sequence 187; uses random gates and applies 1 when the guarded conditions below succeed. | 1 | ExpertAI_Seq_001 |
| `ExpertAI_Seq_188()` | 4398–4434 | direct score writer | Evaluates Expert move sequence 188; uses abilities, random gates, held items and applies -1, 1 when the guarded conditions below succeed. | -1, 1 | ExpertAI_Seq_GoodItemPokemon |
| `ExpertAI_Seq_190()` | 4436–4478 | direct score writer | Evaluates Expert move sequence 190; uses type effectiveness, speed/order state, HP thresholds, random gates and applies 2, 1, -2, -3 when the guarded conditions below succeed. | 2, 1, -2, -3 | — |
| `ExpertAI_Seq_191()` | 4480–4514 | direct score writer | Evaluates Expert move sequence 191; uses battle-rule state, random gates, HP thresholds and applies -2, -1, 1 when the guarded conditions below succeed. | -2, -1, 1 | ExpertAI_Seq_CopyPokemonTokusei, ExpertAI_Seq_ErasePokemonTokusei |
| `ExpertAI_Seq_ErasePokemonTokusei()` | 4516–4537 | reachable dispatcher/predicate support | Evaluates a expert rule using species; applies no direct score write under the guarded conditions below. | indirect/dynamic | — |
| `ExpertAI_Seq_192()` | 4539–4549 | direct score writer | Evaluates Expert move sequence 192; uses random gates and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_196()` | 4559–4614 | direct score writer | Evaluates Expert move sequence 196; uses type effectiveness, random gates and applies 2, 1, -1 when the guarded conditions below succeed. | 2, 1, -1 | — |
| `ExpertAI_Seq_203()` | 4644–4661 | indirect caller/helper on a score path | Evaluates Expert move sequence 203; uses weather and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | ExpertAI_TypeCheck |
| `ExpertAI_Seq_210()` | 4675–4693 | direct score writer | Evaluates Expert move sequence 210; uses types, random gates, HP thresholds and applies 2, -1 when the guarded conditions below succeed. | 2, -1 | — |
| `ExpertAI_Seq_212()` | 4695–4716 | direct score writer | Evaluates Expert move sequence 212; uses speed/order state, random gates, HP thresholds and applies 2, -1, 1 when the guarded conditions below succeed. | 2, -1, 1 | — |
| `ExpertAI_Seq_215()` | 4718–4735 | direct score writer | Evaluates Expert move sequence 215; uses random gates, abilities, types and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_218()` | 4747–4767 | direct score writer | Evaluates Expert move sequence 218; uses field effects, speed/order state, random gates, type effectiveness and applies 2, 1 when the guarded conditions below succeed. | 2, 1 | — |
| `ExpertAI_Seq_219()` | 4769–4796 | direct score writer | Evaluates Expert move sequence 219; uses type effectiveness, speed/order state, random gates and applies -1, -2, 2, 1 when the guarded conditions below succeed. | -1, -2, 2, 1 | — |
| `ExpertAI_Seq_220()` | 4798–4815 | direct score writer | Evaluates Expert move sequence 220; uses HP thresholds, random gates and applies 2 when the guarded conditions below succeed. | 2 | — |
| `ExpertAI_Seq_221()` | 4817–4840 | direct score writer | Evaluates Expert move sequence 221; uses type effectiveness, HP thresholds, random gates and applies -1, 2 when the guarded conditions below succeed. | -1, 2 | — |
| `ExpertAI_Seq_222()` | 4842–4950 | indirect caller/helper on a score path | Evaluates Expert move sequence 222; uses held items and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | ExpertAI_TypeCheck |
| `ExpertAI_Seq_227()` | 5012–5051 | direct score writer | Evaluates Expert move sequence 227; uses random gates, HP thresholds and applies -3, -1, -2, 2 when the guarded conditions below succeed. | -3, -1, -2, 2 | — |
| `ExpertAI_Seq_228()` | 5053–5073 | direct score writer | Evaluates Expert move sequence 228; uses random gates, reserve damage potential and applies -3, -1, 1 when the guarded conditions below succeed. | -3, -1, 1 | ExpertAI_Seq_228_sub |
| `ExpertAI_Seq_228_sub()` | 5075–5097 | direct score writer | Evaluates Expert move sequence 228; uses type effectiveness, available super-effective attacks, random gates and applies -1 when the guarded conditions below succeed. | -1 | — |
| `ExpertAI_Seq_229()` | 5099–5110 | direct score writer | Evaluates Expert move sequence 229; uses HP thresholds, random gates and applies -1 when the guarded conditions below succeed. | -1 | — |
| `ExpertAI_Seq_230()` | 5112–5137 | direct score writer | Evaluates Expert move sequence 230; uses type effectiveness, speed/order state, abilities, random gates and applies 3, 2 when the guarded conditions below succeed. | 3, 2 | — |
| `ExpertAI_Seq_233()` | 5139–5187 | direct score writer | Evaluates Expert move sequence 233; uses abilities, speed/order state, random gates, type effectiveness and applies 2, -2 when the guarded conditions below succeed. | 2, -2 | ExpertAI_Seq_033, ExpertAI_Seq_067, ExpertAI_Seq_167 |
| `ExpertAI_Seq_237()` | 5189–5225 | direct score writer | Evaluates Expert move sequence 237; uses type effectiveness, HP thresholds, random gates and applies -1, 2, 1, -2 when the guarded conditions below succeed. | -1, 2, 1, -2 | — |
| `ExpertAI_Seq_239()` | 5227–5288 | direct score writer | Evaluates Expert move sequence 239; uses HP thresholds, random gates, abilities and applies -3, -1, 2, 1 when the guarded conditions below succeed. | -3, -1, 2, 1 | ExpertAI_Seq_ErasePokemonTokusei |
| `ExpertAI_Seq_240()` | 5290–5293 | reachable dispatcher/predicate support | Evaluates Expert move sequence 240 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_241()` | 5295–5377 | direct score writer | Evaluates Expert move sequence 241; uses types, random gates and applies 2, 1 when the guarded conditions below succeed. | 2, 1 | — |
| `ExpertAI_Seq_242()` | 5379–5382 | reachable dispatcher/predicate support | Evaluates Expert move sequence 242 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_243()` | 5384–5387 | reachable dispatcher/predicate support | Evaluates Expert move sequence 243 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_244()` | 5389–5392 | reachable dispatcher/predicate support | Evaluates Expert move sequence 244 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_245()` | 5394–5450 | direct score writer | Evaluates Expert move sequence 245; uses type effectiveness, status conditions, random gates and applies -1, 3, 2 when the guarded conditions below succeed. | -1, 3, 2 | — |
| `ExpertAI_Seq_246()` | 5452–5455 | reachable dispatcher/predicate support | Evaluates Expert move sequence 246 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_247()` | 5457–5460 | reachable dispatcher/predicate support | Evaluates Expert move sequence 247 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_248()` | 5462–5478 | direct score writer | Evaluates Expert move sequence 248; uses type effectiveness, speed/order state, HP thresholds, random gates and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_249()` | 5480–5487 | direct score writer | Evaluates Expert move sequence 249; uses random gates and applies 2 when the guarded conditions below succeed. | 2 | — |
| `ExpertAI_Seq_250()` | 5489–5492 | reachable dispatcher/predicate support | Evaluates Expert move sequence 250 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_251()` | 5494–5497 | reachable dispatcher/predicate support | Evaluates Expert move sequence 251 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_252()` | 5499–5502 | reachable dispatcher/predicate support | Evaluates Expert move sequence 252 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_258()` | 5504–5507 | reachable dispatcher/predicate support | Evaluates Expert move sequence 258 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_259()` | 5509–5526 | direct score writer | Evaluates Expert move sequence 259; uses battle-rule state, speed/order state, random gates and applies 2, -5 when the guarded conditions below succeed. | 2, -5 | — |
| `ExpertAI_Seq_265()` | 5528–5531 | reachable dispatcher/predicate support | Evaluates Expert move sequence 265 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_266()` | 5533–5540 | direct score writer | Evaluates Expert move sequence 266; uses random gates and applies 2 when the guarded conditions below succeed. | 2 | — |
| `ExpertAI_Seq_268()` | 5542–5615 | indirect caller/helper on a score path | Evaluates Expert move sequence 268; uses species, held items and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | ExpertAI_TypeCheck |
| `ExpertAI_Seq_270()` | 5617–5634 | direct score writer | Evaluates Expert move sequence 270; uses HP thresholds, random gates and applies 2 when the guarded conditions below succeed. | 2 | — |
| `ExpertAI_Seq_272()` | 5636–5678 | direct score writer | Evaluates Expert move sequence 272; uses abilities, random gates, speed/order state, type effectiveness, held items and applies 1 when the guarded conditions below succeed. | 1 | ExpertAI_Seq_016_sub2, ExpertAI_Seq_016_sub4 |
| `ExpertAI_Seq_278()` | 5680–5684 | reachable dispatcher/predicate support | Evaluates Expert move sequence 278 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_279()` | 5686–5690 | reachable dispatcher/predicate support | Evaluates Expert move sequence 279 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_280()` | 5692–5696 | reachable dispatcher/predicate support | Evaluates Expert move sequence 280 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_283()` | 5707–5720 | direct score writer | Evaluates Expert move sequence 283; uses type effectiveness and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_284()` | 5722–5732 | direct score writer | Evaluates Expert move sequence 284; uses random gates and applies 1 when the guarded conditions below succeed. | 1 | ExpertAI_Seq_012 |
| `ExpertAI_Seq_285()` | 5734–5737 | reachable dispatcher/predicate support | Evaluates Expert move sequence 285 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_286()` | 5739–5746 | direct score writer | Evaluates Expert move sequence 286; uses random gates and applies 2 when the guarded conditions below succeed. | 2 | — |
| `ExpertAI_Seq_287()` | 5748–5751 | reachable dispatcher/predicate support | Evaluates Expert move sequence 287 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_288()` | 5753–5779 | direct score writer | Evaluates Expert move sequence 288; uses type effectiveness, random gates and applies 2 when the guarded conditions below succeed. | 2 | — |
| `ExpertAI_Seq_289()` | 5781–5784 | reachable dispatcher/predicate support | Evaluates Expert move sequence 289 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_290()` | 5786–5807 | direct score writer | Evaluates Expert move sequence 290; uses speed/order state, random gates, HP thresholds and applies 2, -1, 1 when the guarded conditions below succeed. | 2, -1, 1 | — |
| `ExpertAI_Seq_291()` | 5809–5855 | direct score writer | Evaluates Expert move sequence 291; uses type effectiveness, abilities, random gates and applies 2, 1, -1 when the guarded conditions below succeed. | 2, 1, -1 | — |
| `ExpertAI_Seq_292()` | 5857–5860 | reachable dispatcher/predicate support | Evaluates Expert move sequence 292 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_293()` | 5862–5897 | direct score writer | Evaluates Expert move sequence 293; uses type effectiveness, speed/order state, random gates and applies -1, -3, -2, 2 when the guarded conditions below succeed. | -1, -3, -2, 2 | — |
| `ExpertAI_Seq_294()` | 5899–5902 | reachable dispatcher/predicate support | Evaluates Expert move sequence 294 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_295()` | 5904–5915 | direct score writer | Evaluates Expert move sequence 295; uses speed/order state, random gates and applies 2 when the guarded conditions below succeed. | 2 | — |
| `ExpertAI_Seq_296()` | 5917–5932 | direct score writer | Evaluates Expert move sequence 296; uses random gates and applies -2, -1 when the guarded conditions below succeed. | -2, -1 | — |
| `ExpertAI_Seq_297()` | 5934–5975 | direct score writer | Evaluates Expert move sequence 297; uses type effectiveness, random gates and applies -1, 2 when the guarded conditions below succeed. | -1, 2 | — |
| `ExpertAI_Seq_298()` | 5977–5980 | reachable dispatcher/predicate support | Evaluates Expert move sequence 298 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_299()` | 5982–5985 | reachable dispatcher/predicate support | Evaluates Expert move sequence 299 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_300()` | 5987–5990 | reachable dispatcher/predicate support | Evaluates Expert move sequence 300 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_301()` | 5992–5995 | reachable dispatcher/predicate support | Evaluates Expert move sequence 301 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_302()` | 5997–6000 | reachable dispatcher/predicate support | Evaluates Expert move sequence 302 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_303()` | 6002–6029 | direct score writer | Evaluates Expert move sequence 303; uses type effectiveness, random gates and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_304()` | 6031–6058 | direct score writer | Evaluates Expert move sequence 304; uses random gates and applies -1, 2 when the guarded conditions below succeed. | -1, 2 | — |
| `ExpertAI_Seq_305()` | 6061–6124 | direct score writer | Evaluates Expert move sequence 305; uses type effectiveness, status conditions, random gates and applies 4, 3, 2, -1 when the guarded conditions below succeed. | 4, 3, 2, -1 | — |
| `ExpertAI_Seq_306()` | 6126–6135 | direct score writer | Evaluates Expert move sequence 306; uses battle-rule state and applies -5 when the guarded conditions below succeed. | -5 | — |
| `ExpertAI_Seq_308()` | 6137–6154 | direct score writer | Evaluates Expert move sequence 308; uses random gates, speed/order state and applies -2, 2 when the guarded conditions below succeed. | -2, 2 | — |
| `ExpertAI_Seq_310()` | 6156–6183 | direct score writer | Evaluates Expert move sequence 310; uses type effectiveness, random gates and applies 2 when the guarded conditions below succeed. | 2 | — |
| `ExpertAI_Seq_314()` | 6196–6205 | direct score writer | Evaluates Expert move sequence 314; uses random gates and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_316()` | 6207–6219 | direct score writer | Evaluates Expert move sequence 316; uses weather, random gates and applies -1 when the guarded conditions below succeed. | -1 | ExpertAI_Seq_010 |
| `ExpertAI_Seq_317()` | 6221–6241 | direct score writer | Evaluates Expert move sequence 317; uses type effectiveness, held items, random gates and applies 2, 1 when the guarded conditions below succeed. | 2, 1 | — |
| `ExpertAI_Seq_318()` | 6243–6246 | reachable dispatcher/predicate support | Evaluates Expert move sequence 318 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_319()` | 6248–6251 | reachable dispatcher/predicate support | Evaluates Expert move sequence 319 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_320()` | 6253–6294 | direct score writer | Evaluates Expert move sequence 320; uses HP thresholds, available super-effective attacks, random gates and applies -2 when the guarded conditions below succeed. | -2 | — |
| `ExpertAI_Seq_323()` | 6296–6308 | direct score writer | Evaluates Expert move sequence 323; uses random gates and applies -5, -1 when the guarded conditions below succeed. | -5, -1 | ExpertAI_Seq_MegaShinkaPokemon |
| `ExpertAI_Seq_329()` | 6310–6313 | reachable dispatcher/predicate support | Evaluates Expert move sequence 329 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_334()` | 6315–6318 | reachable dispatcher/predicate support | Evaluates Expert move sequence 334 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_335()` | 6320–6323 | reachable dispatcher/predicate support | Evaluates Expert move sequence 335 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_336()` | 6325–6328 | reachable dispatcher/predicate support | Evaluates Expert move sequence 336 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_337()` | 6330–6362 | direct score writer | Evaluates Expert move sequence 337; uses type effectiveness, types, random gates and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_338()` | 6364–6376 | direct score writer | Evaluates Expert move sequence 338; uses type effectiveness, random gates and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_340()` | 6378–6398 | direct score writer | Evaluates Expert move sequence 340; uses field effects, random gates and applies -2, -1, 1 when the guarded conditions below succeed. | -2, -1, 1 | — |
| `ExpertAI_Seq_342()` | 6400–6414 | direct score writer | Evaluates Expert move sequence 342; uses HP thresholds, random gates and applies -1, 1 when the guarded conditions below succeed. | -1, 1 | — |
| `ExpertAI_Seq_344()` | 6441–6457 | direct score writer | Evaluates Expert move sequence 344; uses types, abilities, random gates and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_346()` | 6464–6480 | direct score writer | Evaluates Expert move sequence 346; uses available super-effective attacks, random gates, reserve damage potential and applies -2, 1 when the guarded conditions below succeed. | -2, 1 | — |
| `ExpertAI_Seq_347()` | 6482–6514 | direct score writer | Evaluates Expert move sequence 347; uses random gates and applies -3, 2 when the guarded conditions below succeed. | -3, 2 | — |
| `ExpertAI_Seq_349()` | 6516–6519 | reachable dispatcher/predicate support | Evaluates Expert move sequence 349 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_350()` | 6521–6530 | direct score writer | Evaluates Expert move sequence 350; uses battle-rule state and applies -5 when the guarded conditions below succeed. | -5 | — |
| `ExpertAI_Seq_351()` | 6532–6551 | direct score writer | Evaluates Expert move sequence 351; uses random gates and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_352()` | 6553–6596 | direct score writer | Evaluates Expert move sequence 352; uses random gates and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_353()` | 6598–6623 | direct score writer | Evaluates Expert move sequence 353; uses abilities, random gates and applies -2, 1 when the guarded conditions below succeed. | -2, 1 | — |
| `ExpertAI_Seq_354()` | 6625–6628 | reachable dispatcher/predicate support | Evaluates Expert move sequence 354 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_359()` | 6630–6633 | reachable dispatcher/predicate support | Evaluates Expert move sequence 359 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_363()` | 6635–6649 | direct score writer | Evaluates Expert move sequence 363; uses speed/order state, random gates and applies -3, 2 when the guarded conditions below succeed. | -3, 2 | — |
| `ExpertAI_Seq_365()` | 6651–6689 | direct score writer | Evaluates Expert move sequence 365; uses random gates, HP thresholds and applies -1, 2, -2 when the guarded conditions below succeed. | -1, 2, -2 | — |
| `ExpertAI_Seq_366()` | 6691–6722 | direct score writer | Evaluates Expert move sequence 366; uses battle-rule state, random gates, HP thresholds and applies -1, -2 when the guarded conditions below succeed. | -1, -2 | — |
| `ExpertAI_Seq_368()` | 6724–6749 | direct score writer | Evaluates Expert move sequence 368; uses random gates and applies 1 when the guarded conditions below succeed. | 1 | — |
| `ExpertAI_Seq_372()` | 6751–6754 | reachable dispatcher/predicate support | Evaluates Expert move sequence 372 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_373()` | 6756–6759 | reachable dispatcher/predicate support | Evaluates Expert move sequence 373 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `ExpertAI_Seq_374()` | 6762–6772 | direct score writer | Evaluates Expert move sequence 374; uses random gates and applies 1 when the guarded conditions below succeed. | 1 | ExpertAI_Seq_010 |
| `ExpertAI_Seq_377()` | 6774–6784 | direct score writer | Evaluates Expert move sequence 377; uses types, random gates and applies 2 when the guarded conditions below succeed. | 2 | — |
| `ExpertAI_Seq_379()` | 6786–6804 | direct score writer | Evaluates Expert move sequence 379; uses type effectiveness, types, random gates and applies 1 when the guarded conditions below succeed. | 1 | — |

The complete guarded bodies follow:

### `main()` (source lines 7–14)

```text
    7 | main()
    8 | {
    9 | waza_seq_no = AI_CMD(CMD_CHECK_WORKWAZA_SEQNO);
   11 | main_proc();
   14 | }
```

### `main_proc()` (source lines 16–326)

```text
   16 | main_proc()
   17 | {
   18 | waza_seq_no = AI_CMD(CMD_CHECK_WORKWAZA_SEQNO);
   20 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
   21 | if( CHK_rule == BTL_RULE_DOUBLE
   22 | || CHK_rule == BTL_RULE_TRIPLE ){
   23 | if( AI_CMD(CMD_IF_MIKATA_ATTACK)){
   24 | return;
   25 | }
   26 | }
   27 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KODAWARISUKAAHU)
   28 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KODAWARIHATIMAKI)
   29 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KODAWARIMEGANE)){
   30 | WazaKind = AI_CMD(CMD_CHECK_WAZA_KIND);
   31 | if( WazaKind != WAZADATA_DMG_SPECIAL
   32 | && WazaKind != WAZADATA_DMG_PHYSIC ){
   33 | if( waza_seq_no != 177 ){
   35 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
   36 | SCORE += -1;
   37 | }
   38 | }
   39 | }
   40 | }
   41 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_MUSTHIT_TARGET)){
   42 | wazaNo = CURRENT_MOVE();
   43 | if( wazaNo == WAZANO_DENZIHOU
   44 | || wazaNo == WAZANO_BAKURETUPANTI
   45 | || wazaNo == WAZANO_RENGOKU
   46 | || wazaNo == WAZANO_UTAU
   47 | || wazaNo == WAZANO_TYOUONPA
   48 | || wazaNo == WAZANO_KUSABUE
   49 | || wazaNo == WAZANO_SAIMINZYUTU
   50 | || wazaNo == WAZANO_HUBUKI
   51 | || wazaNo == WAZANO_KAMINARI
   52 | || wazaNo == WAZANO_SUMOGGU
   53 | || wazaNo == WAZANO_KIAIDAMA
   54 | || wazaNo == WAZANO_BOUHUU){
   56 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
   57 | SCORE += 2;
   58 | }
   59 | }
   60 | }
   64 | switch( waza_seq_no )
   65 | {
   66 | case 1: ExpertAI_Seq_001();
   67 | case 3: ExpertAI_Seq_003();
   68 | case 7: ExpertAI_Seq_007();
   69 | case 8: ExpertAI_Seq_008();
   70 | case 9: ExpertAI_Seq_009();
   71 | case 10: ExpertAI_Seq_010();
   72 | case 11: ExpertAI_Seq_011();
   73 | case 12: ExpertAI_Seq_012();
   74 | case 13: ExpertAI_Seq_013();
   75 | case 14: ExpertAI_Seq_014();
   76 | case 15: ExpertAI_Seq_015();
   77 | case 16: ExpertAI_Seq_016();
   78 | case 17: ExpertAI_Seq_017();
   79 | case 18: ExpertAI_Seq_018();
   80 | case 19: ExpertAI_Seq_019();
   81 | case 20: ExpertAI_Seq_020();
   82 | case 21: ExpertAI_Seq_021();
   83 | case 22: ExpertAI_Seq_022();
   84 | case 23: ExpertAI_Seq_023();
   85 | case 24: ExpertAI_Seq_024();
   86 | case 25: ExpertAI_Seq_025();
   87 | case 26: ExpertAI_Seq_026();
   88 | case 28: ExpertAI_Seq_028();
   89 | case 30: ExpertAI_Seq_030();
   90 | case 32: ExpertAI_Seq_032();
   91 | case 33: ExpertAI_Seq_033();
   92 | case 35: ExpertAI_Seq_035();
   93 | case 37: ExpertAI_Seq_037();
   94 | case 38: ExpertAI_Seq_038();
   95 | case 39: ExpertAI_Seq_039();
   96 | case 40: ExpertAI_Seq_040();
   97 | case 42: ExpertAI_Seq_042();
   98 | case 43: ExpertAI_Seq_043();
   99 | case 48: ExpertAI_Seq_048();
  100 | case 49: ExpertAI_Seq_049();
  101 | case 50: ExpertAI_Seq_010();
  102 | case 51: ExpertAI_Seq_011();
  103 | case 52: ExpertAI_Seq_012();
  104 | case 53: ExpertAI_Seq_013();
  105 | case 54: ExpertAI_Seq_014();
  106 | case 55: ExpertAI_Seq_015();
  107 | case 56: ExpertAI_Seq_016();
  108 | case 58: ExpertAI_Seq_018();
  109 | case 59: ExpertAI_Seq_019();
  110 | case 60: ExpertAI_Seq_020();
  111 | case 61: ExpertAI_Seq_021();
  112 | case 62: ExpertAI_Seq_022();
  113 | case 63: ExpertAI_Seq_023();
  114 | case 64: ExpertAI_Seq_024();
  115 | case 65: ExpertAI_Seq_065();
  116 | case 66: ExpertAI_Seq_033();
  117 | case 67: ExpertAI_Seq_067();
  118 | case 70: ExpertAI_Seq_070();
  119 | case 75: ExpertAI_Seq_039();
  120 | case 78: ExpertAI_Seq_078();
  121 | case 79: ExpertAI_Seq_079();
  122 | case 80: ExpertAI_Seq_080();
  123 | case 84: ExpertAI_Seq_033();
  124 | case 86: ExpertAI_Seq_086();
  125 | case 87: ExpertAI_Seq_087();
  126 | case 88: ExpertAI_Seq_087();
  127 | case 89: ExpertAI_Seq_089();
  128 | case 90: ExpertAI_Seq_090();
  129 | case 91: ExpertAI_Seq_091();
  130 | case 92: ExpertAI_Seq_092();
  131 | case 94: ExpertAI_Seq_094();
  132 | case 97: ExpertAI_Seq_092();
  133 | case 98: ExpertAI_Seq_098();
  134 | case 99: ExpertAI_Seq_099();
  135 | case 102: ExpertAI_Seq_102();
  136 | case 105: ExpertAI_Seq_105();
  137 | case 106: ExpertAI_Seq_042();
  138 | case 108: ExpertAI_Seq_108();
  139 | case 109: ExpertAI_Seq_109();
  140 | case 111: ExpertAI_Seq_111();
  141 | case 112: ExpertAI_Seq_112();
  142 | case 113: ExpertAI_Seq_113();
  143 | case 116: ExpertAI_Seq_116();
  144 | case 118: ExpertAI_Seq_118();
  145 | case 120: ExpertAI_Seq_120();
  146 | case 121: ExpertAI_Seq_121();
  147 | case 123: ExpertAI_Seq_123();
  148 | case 127: ExpertAI_Seq_127();
  149 | case 128: ExpertAI_Seq_128();
  150 | case 132: ExpertAI_Seq_132();
  151 | case 133: ExpertAI_Seq_132();
  152 | case 134: ExpertAI_Seq_132();
  153 | case 135: ExpertAI_Seq_135();
  154 | case 136: ExpertAI_Seq_136();
  155 | case 137: ExpertAI_Seq_137();
  156 | case 142: ExpertAI_Seq_142();
  157 | case 143: ExpertAI_Seq_143();
  158 | case 145: ExpertAI_Seq_039();
  159 | case 151: ExpertAI_Seq_039();
  160 | case 152: ExpertAI_Seq_152();
  161 | case 155: ExpertAI_Seq_155();
  162 | case 157: ExpertAI_Seq_032();
  163 | case 158: ExpertAI_Seq_158();
  164 | case 160: ExpertAI_Seq_160();
  165 | case 161: ExpertAI_Seq_161();
  166 | case 162: ExpertAI_Seq_032();
  167 | case 164: ExpertAI_Seq_164();
  168 | case 165: ExpertAI_Seq_165();
  169 | case 167: ExpertAI_Seq_167();
  170 | case 166: ExpertAI_Seq_166();
  171 | case 168: ExpertAI_Seq_007();
  172 | case 169: ExpertAI_Seq_169();
  173 | case 170: ExpertAI_Seq_170();
  174 | case 171: ExpertAI_Seq_171();
  175 | case 173: ExpertAI_Seq_173();
  176 | case 175: ExpertAI_Seq_175();
  177 | case 177: ExpertAI_Seq_177();
  178 | case 178: ExpertAI_Seq_178();
  179 | case 183: ExpertAI_Seq_183();
  180 | case 184: ExpertAI_Seq_184();
  181 | case 185: ExpertAI_Seq_185();
  182 | case 186: ExpertAI_Seq_186();
  183 | case 187: ExpertAI_Seq_187();
  184 | case 188: ExpertAI_Seq_188();
  185 | case 189: ExpertAI_Seq_091();
  186 | case 190: ExpertAI_Seq_190();
  187 | case 191: ExpertAI_Seq_191();
  188 | case 192: ExpertAI_Seq_192();
  189 | case 196: ExpertAI_Seq_196();
  190 | case 198: ExpertAI_Seq_048();
  191 | case 200: ExpertAI_Seq_043();
  192 | case 203: ExpertAI_Seq_203();
  193 | case 205: ExpertAI_Seq_019();
  194 | case 206: ExpertAI_Seq_014();
  195 | case 208: ExpertAI_Seq_010();
  196 | case 209: ExpertAI_Seq_043();
  197 | case 210: ExpertAI_Seq_210();
  198 | case 211: ExpertAI_Seq_013();
  199 | case 212: ExpertAI_Seq_212();
  200 | case 214: ExpertAI_Seq_032();
  201 | case 215: ExpertAI_Seq_215();
  202 | case 218: ExpertAI_Seq_218();
  203 | case 219: ExpertAI_Seq_219();
  204 | case 220: ExpertAI_Seq_220();
  205 | case 221: ExpertAI_Seq_221();
  206 | case 222: ExpertAI_Seq_222();
  207 | case 227: ExpertAI_Seq_227();
  208 | case 228: ExpertAI_Seq_228();
  209 | case 229: ExpertAI_Seq_229();
  210 | case 230: ExpertAI_Seq_230();
  211 | case 233: ExpertAI_Seq_233();
  212 | case 237: ExpertAI_Seq_237();
  213 | case 239: ExpertAI_Seq_239();
  214 | case 240: ExpertAI_Seq_240();
  215 | case 241: ExpertAI_Seq_241();
  216 | case 242: ExpertAI_Seq_242();
  217 | case 243: ExpertAI_Seq_243();
  218 | case 244: ExpertAI_Seq_244();
  219 | case 245: ExpertAI_Seq_245();
  220 | case 246: ExpertAI_Seq_246();
  221 | case 247: ExpertAI_Seq_247();
  222 | case 248: ExpertAI_Seq_248();
  223 | case 249: ExpertAI_Seq_249();
  224 | case 250: ExpertAI_Seq_250();
  225 | case 251: ExpertAI_Seq_251();
  226 | case 252: ExpertAI_Seq_252();
  227 | case 253: ExpertAI_Seq_048();
  228 | case 255: ExpertAI_Seq_155();
  229 | case 256: ExpertAI_Seq_155();
  230 | case 258: ExpertAI_Seq_258();
  231 | case 259: ExpertAI_Seq_259();
  232 | case 262: ExpertAI_Seq_048();
  233 | case 263: ExpertAI_Seq_155();
  234 | case 265: ExpertAI_Seq_265();
  235 | case 266: ExpertAI_Seq_266();
  236 | case 268: ExpertAI_Seq_268();
  237 | case 269: ExpertAI_Seq_048();
  238 | case 270: ExpertAI_Seq_270();
  239 | case 272: ExpertAI_Seq_272();
  240 | case 277: ExpertAI_Seq_010();
  241 | case 278: ExpertAI_Seq_278();
  242 | case 279: ExpertAI_Seq_279();
  243 | case 280: ExpertAI_Seq_280();
  244 | case 283: ExpertAI_Seq_283();
  245 | case 284: ExpertAI_Seq_284();
  246 | case 285: ExpertAI_Seq_285();
  247 | case 286: ExpertAI_Seq_286();
  248 | case 287: ExpertAI_Seq_287();
  249 | case 288: ExpertAI_Seq_288();
  250 | case 289: ExpertAI_Seq_289();
  251 | case 290: ExpertAI_Seq_290();
  252 | case 291: ExpertAI_Seq_291();
  253 | case 292: ExpertAI_Seq_292();
  254 | case 293: ExpertAI_Seq_293();
  255 | case 294: ExpertAI_Seq_294();
  256 | case 295: ExpertAI_Seq_295();
  257 | case 296: ExpertAI_Seq_296();
  258 | case 297: ExpertAI_Seq_297();
  259 | case 298: ExpertAI_Seq_298();
  260 | case 299: ExpertAI_Seq_299();
  261 | case 300: ExpertAI_Seq_300();
  262 | case 301: ExpertAI_Seq_301();
  263 | case 302: ExpertAI_Seq_302();
  264 | case 303: ExpertAI_Seq_303();
  265 | case 304: ExpertAI_Seq_304();
  266 | case 305: ExpertAI_Seq_305();
  267 | case 306: ExpertAI_Seq_306();
  268 | case 308: ExpertAI_Seq_308();
  269 | case 310: ExpertAI_Seq_310();
  270 | case 312: ExpertAI_Seq_012();
  271 | case 313: ExpertAI_Seq_028();
  272 | case 314: ExpertAI_Seq_314();
  273 | case 316: ExpertAI_Seq_316();
  274 | case 317: ExpertAI_Seq_317();
  275 | case 318: ExpertAI_Seq_318();
  276 | case 319: ExpertAI_Seq_319();
  277 | case 320: ExpertAI_Seq_320();
  278 | case 321: ExpertAI_Seq_013();
  279 | case 322: ExpertAI_Seq_010();
  280 | case 323: ExpertAI_Seq_323();
  281 | case 327: ExpertAI_Seq_010();
  282 | case 328: ExpertAI_Seq_011();
  283 | case 329: ExpertAI_Seq_329();
  284 | case 330: ExpertAI_Seq_070();
  285 | case 331: ExpertAI_Seq_039();
  286 | case 332: ExpertAI_Seq_039();
  287 | case 333: ExpertAI_Seq_152();
  288 | case 334: ExpertAI_Seq_334();
  289 | case 335: ExpertAI_Seq_335();
  290 | case 336: ExpertAI_Seq_336();
  291 | case 337: ExpertAI_Seq_337();
  292 | case 338: ExpertAI_Seq_338();
  293 | case 340: ExpertAI_Seq_340();
  294 | case 342: ExpertAI_Seq_342();
  295 | case 343: ExpertAI_Seq_021();
  296 | case 344: ExpertAI_Seq_344();
  297 | case 345: ExpertAI_Seq_003();
  298 | case 346: ExpertAI_Seq_346();
  299 | case 347: ExpertAI_Seq_347();
  300 | case 348: ExpertAI_Seq_003();
  301 | case 349: ExpertAI_Seq_349();
  302 | case 350: ExpertAI_Seq_350();
  303 | case 351: ExpertAI_Seq_351();
  304 | case 352: ExpertAI_Seq_352();
  305 | case 353: ExpertAI_Seq_353();
  306 | case 354: ExpertAI_Seq_354();
  307 | case 355: ExpertAI_Seq_111();
  308 | case 356: ExpertAI_Seq_018();
  309 | case 357: ExpertAI_Seq_021();
  310 | case 359: ExpertAI_Seq_359();
  311 | case 361: ExpertAI_Seq_111();
  312 | case 363: ExpertAI_Seq_363();
  313 | case 364: ExpertAI_Seq_018();
  314 | case 365: ExpertAI_Seq_365();
  315 | case 366: ExpertAI_Seq_366();
  316 | case 368: ExpertAI_Seq_368();
  317 | case 371: ExpertAI_Seq_067();
  318 | case 372: ExpertAI_Seq_372();
  319 | case 373: ExpertAI_Seq_373();
  320 | case 374: ExpertAI_Seq_374();
  321 | case 375: ExpertAI_Seq_342();
  322 | case 376: ExpertAI_Seq_111();
  323 | case 377: ExpertAI_Seq_377();
  324 | case 379: ExpertAI_Seq_379();
  325 | }
  326 | }
```

### `ExpertAI_Seq_001()` (source lines 330–383)

```text
  330 | ExpertAI_Seq_001()
  331 | {
  334 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 8) ){
  336 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  337 | SCORE += 1;
  338 | }
  339 | }
  341 | else if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 107) ){
  343 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  344 | SCORE += 1;
  345 | }
  346 | }
  348 | else if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 97) ){
  350 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
  351 | SCORE += -2;
  352 | }
  353 | }
  355 | else if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 183) ){
  357 | if( AI_CMD(CMD_IF_RND_UNDER, 150) ){
  358 | SCORE += -1;
  359 | }
  360 | }
  362 | else if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 92) ){
  364 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  365 | SCORE += -1;
  366 | }
  367 | }
  369 | DefTokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
  370 | if( DefTokusei == TOKUSEI_NOOGAADO ){
  372 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  373 | SCORE += 2;
  374 | }
  375 | }
  377 | else if( DefTokusei == TOKUSEI_NOOGAADO ){
  379 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
  380 | SCORE += -2;
  381 | }
  382 | }
  383 | }
```

### `ExpertAI_Seq_003()` (source lines 385–396)

```text
  385 | ExpertAI_Seq_003()
  386 | {
  389 | DefTokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
  390 | if( DefTokusei == TOKUSEI_NOOGAADO ){
  392 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  393 | SCORE += -2;
  394 | }
  395 | }
  396 | }
```

### `ExpertAI_Seq_007()` (source lines 398–457)

```text
  398 | ExpertAI_Seq_007()
  399 | {
  401 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 111) ){
  403 | if( AI_CMD(CMD_IF_RND_UNDER, 50) ){
  404 | SCORE += -1;
  405 | }
  406 | }
  407 | else if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 355) ){
  409 | if( AI_CMD(CMD_IF_RND_UNDER, 50) ){
  410 | SCORE += -1;
  411 | }
  412 | }
  413 | else if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 361) ){
  415 | if( AI_CMD(CMD_IF_RND_UNDER, 50) ){
  416 | SCORE += -1;
  417 | }
  418 | }
  419 | else if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 278) ){
  421 | if( AI_CMD(CMD_IF_RND_UNDER, 50) ){
  422 | SCORE += -1;
  423 | }
  424 | }
  425 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_AVOID, 9) ){
  427 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
  428 | SCORE += -2;
  429 | }
  430 | }
  431 | else if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_AVOID, 6) ){
  433 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
  434 | SCORE += -1;
  435 | }
  436 | }
  437 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 80) ){
  438 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_DEFENCE) ){
  440 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
  441 | SCORE += -2;
  442 | }
  443 | }
  444 | }
  445 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 30) ){
  447 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
  448 | SCORE += 3
  449 | }
  450 | }
  451 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 50) ){
  453 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
  454 | SCORE += 2
  455 | }
  456 | }
  457 | }
```

### `ExpertAI_Seq_008()` (source lines 459–491)

```text
  459 | ExpertAI_Seq_008()
  460 | {
  462 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI) ){
  464 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
  465 | SCORE += -2;
  466 | return;
  467 | }
  468 | }
  469 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI) ){
  471 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
  472 | SCORE += -1;
  473 | return;
  474 | }
  475 | }
  476 | DefTokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
  477 | if( DefTokusei == TOKUSEI_NOOGAADO ){
  479 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  480 | SCORE += -2;
  481 | return;
  482 | }
  483 | }
  484 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_NEMURI) ){
  486 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
  487 | SCORE += 3;
  488 | return;
  489 | }
  490 | }
  491 | }
```

### `ExpertAI_Seq_009()` (source lines 493–510)

```text
  493 | ExpertAI_Seq_009()
  494 | {
  496 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_DEFENCE)){
  497 | if( ExpertAI_Seq_009_sub() == 0 ){
  499 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
  500 | SCORE += -1;
  501 | }
  502 | }
  503 | }
  504 | if( ExpertAI_Seq_009_sub() == 1 ){
  506 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  507 | SCORE += 2;
  508 | }
  509 | }
  510 | }
```

### `ExpertAI_Seq_009_sub()` (source lines 511–544)

```text
  511 | ExpertAI_Seq_009_sub()
  512 | {
  513 | DefLastWaza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_DEFENCE);
  514 | if( DefLastWaza == WAZANO_HASAMIGIROTIN || DefLastWaza == WAZANO_TUNODORIRU
  515 | || DefLastWaza == WAZANO_DENZIHA || DefLastWaza == WAZANO_ZIWARE
  516 | || DefLastWaza == WAZANO_DOKUDOKU || DefLastWaza == WAZANO_NAITOHEDDO
  517 | || DefLastWaza == WAZANO_AYASIIHIKARI || DefLastWaza == WAZANO_TOBIHIZAGERI
  518 | || DefLastWaza == WAZANO_HEBINIRAMI || DefLastWaza == WAZANO_AKUMANOKISSU
  519 | || DefLastWaza == WAZANO_IKARINOMAEBA || DefLastWaza == WAZANO_URAMI
  520 | || DefLastWaza == WAZANO_KOGOERUKAZE || DefLastWaza == WAZANO_GEKIRIN
  521 | || DefLastWaza == WAZANO_MEROMERO || DefLastWaza == WAZANO_BAKURETUPANTI
  522 | || DefLastWaza == WAZANO_SYADOOBOORU || DefLastWaza == WAZANO_ITYAMON
  523 | || DefLastWaza == WAZANO_ONIBI || DefLastWaza == WAZANO_ITYAMON
  524 | || DefLastWaza == WAZANO_TORIKKU || DefLastWaza == WAZANO_BAKADIKARA
  525 | || DefLastWaza == WAZANO_SUKIRUSUWAPPU || DefLastWaza == WAZANO_ZETTAIREIDO
  526 | || DefLastWaza == WAZANO_DORAGONKUROO || DefLastWaza == WAZANO_INFAITO
  527 | || DefLastWaza == WAZANO_SAIKOSIHUTO || DefLastWaza == WAZANO_RYUUNOHADOU
  528 | || DefLastWaza == WAZANO_DORAGONDAIBU || DefLastWaza == WAZANO_SURIKAE
  529 | || DefLastWaza == WAZANO_GIGAINPAKUTO || DefLastWaza == WAZANO_SYADOOKUROO
  530 | || DefLastWaza == WAZANO_KAGEUTI || DefLastWaza == WAZANO_RYUUSEIGUN
  531 | || DefLastWaza == WAZANO_OSYABERI || DefLastWaza == WAZANO_TOKINOHOUKOU
  532 | || DefLastWaza == WAZANO_AKUUSETUDAN || DefLastWaza == WAZANO_DAAKUHOORU
  533 | || DefLastWaza == WAZANO_SYADOODAIBU || DefLastWaza == WAZANO_ROOKIKKU
  534 | || DefLastWaza == WAZANO_RINSYOU || DefLastWaza == WAZANO_EKOOBOISU
  535 | || DefLastWaza == WAZANO_MUSINOTEIKOU || DefLastWaza == WAZANO_ZINARASI
  536 | || DefLastWaza == WAZANO_DABURUTYOPPU || DefLastWaza == WAZANO_SEINARUTURUGI
  537 | || DefLastWaza == WAZANO_AHUROBUREIKU || DefLastWaza == WAZANO_KOGOERUSEKAI
  538 | || DefLastWaza == WAZANO_BAAKUAUTO || DefLastWaza == WAZANO_vJENEREETO
  539 | || DefLastWaza == WAZANO_HURAINGUPURESU || DefLastWaza == WAZANO_GOOSUTODAIBU
  540 | || DefLastWaza == WAZANO_OTAKEBI || DefLastWaza == WAZANO_BAKUONPA ){
  541 | return 1;
  542 | }
  543 | return 0;
  544 | }
```

### `ExpertAI_Seq_010()` (source lines 546–583)

```text
  546 | ExpertAI_Seq_010()
  547 | {
  549 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_POW, 8)){
  551 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  552 | SCORE += -1;
  553 | }
  554 | }
  555 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_POW, 7)){
  557 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  558 | SCORE += -1;
  559 | }
  560 | }
  561 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_POW, 6)){
  562 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 70)){
  563 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 127)){
  565 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  566 | SCORE += 2;
  567 | }
  568 | }
  569 | }
  570 | }
  571 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 40)){
  573 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
  574 | SCORE += -2;
  575 | }
  576 | }
  577 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 70)){
  579 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
  580 | SCORE += -2;
  581 | }
  582 | }
  583 | }
```

### `ExpertAI_Seq_011()` (source lines 585–636)

```text
  585 | ExpertAI_Seq_011()
  586 | {
  588 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 70)){
  589 | if( AI_CMD(CMD_CHECK_LAST_WAZA_KIND) == WAZADATA_DMG_SPECIAL) {
  591 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
  592 | SCORE += -2;
  593 | }
  594 | }
  595 | }
  596 | if( AI_CMD(CMD_CHECK_LAST_WAZA_KIND) == WAZADATA_DMG_SPECIAL) {
  598 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  599 | SCORE += -2;
  600 | }
  601 | }
  602 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_DEF, 8)){
  604 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  605 | SCORE += -1;
  606 | }
  607 | }
  608 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_DEF, 7)){
  610 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  611 | SCORE += -1;
  612 | }
  613 | }
  614 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_DEF, 6)){
  615 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 70)){
  616 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 127)){
  618 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  619 | SCORE += 2;
  620 | }
  621 | }
  622 | }
  623 | }
  624 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 40)){
  626 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
  627 | SCORE += -2;
  628 | }
  629 | }
  630 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 70)){
  632 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
  633 | SCORE += -2;
  634 | }
  635 | }
  636 | }
```

### `ExpertAI_Seq_012()` (source lines 638–706)

```text
  638 | ExpertAI_Seq_012()
  639 | {
  641 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)){
  643 | SCORE += -5;
  644 | return;
  645 | }
  646 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 31)){
  648 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
  649 | SCORE += 1;
  650 | }
  651 | }
  652 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 32)){
  654 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
  655 | SCORE += 1;
  656 | }
  657 | }
  658 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 37)){
  660 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
  661 | SCORE += 1;
  662 | }
  663 | }
  664 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 132)){
  666 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
  667 | SCORE += 1;
  668 | }
  669 | }
  670 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 214)){
  672 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
  673 | SCORE += 1;
  674 | }
  675 | }
  676 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 79)){
  678 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
  679 | SCORE += 1;
  680 | }
  681 | }
  682 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 91)){
  684 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
  685 | SCORE += 1;
  686 | }
  687 | }
  688 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 150)){
  690 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
  691 | SCORE += 1;
  692 | }
  693 | }
  694 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 98)){
  696 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
  697 | SCORE += 1;
  698 | }
  699 | }
  700 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 127)){
  702 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
  703 | SCORE += 1;
  704 | }
  705 | }
  706 | }
```

### `ExpertAI_Seq_013()` (source lines 708–745)

```text
  708 | ExpertAI_Seq_013()
  709 | {
  711 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEPOW, 8)){
  713 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  714 | SCORE += -1;
  715 | }
  716 | }
  717 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEPOW, 7)){
  719 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  720 | SCORE += -1;
  721 | }
  722 | }
  723 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_SPEPOW, 6)){
  724 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 70)){
  725 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 127)){
  727 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  728 | SCORE += 2;
  729 | }
  730 | }
  731 | }
  732 | }
  733 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 40)){
  735 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
  736 | SCORE += -2;
  737 | }
  738 | }
  739 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 70)){
  741 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
  742 | SCORE += -2;
  743 | }
  744 | }
  745 | }
```

### `ExpertAI_Seq_014()` (source lines 747–798)

```text
  747 | ExpertAI_Seq_014()
  748 | {
  750 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 70)){
  751 | if( AI_CMD(CMD_CHECK_LAST_WAZA_KIND) == WAZADATA_DMG_PHYSIC) {
  753 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
  754 | SCORE += -2;
  755 | }
  756 | }
  757 | }
  758 | if( AI_CMD(CMD_CHECK_WAZA_KIND) == WAZADATA_DMG_PHYSIC) {
  760 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  761 | SCORE += -2;
  762 | }
  763 | }
  764 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEDEF, 8)){
  766 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  767 | SCORE += -1;
  768 | }
  769 | }
  770 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEDEF, 7)){
  772 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  773 | SCORE += -1;
  774 | }
  775 | }
  776 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_SPEDEF, 6)){
  777 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 70)){
  778 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 127)){
  780 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  781 | SCORE += 2;
  782 | }
  783 | }
  784 | }
  785 | }
  786 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 40)){
  788 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
  789 | SCORE += -2;
  790 | }
  791 | }
  792 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 70)){
  794 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
  795 | SCORE += -2;
  796 | }
  797 | }
  798 | }
```

### `ExpertAI_Seq_015()` (source lines 800–815)

```text
  800 | ExpertAI_Seq_015()
  801 | {
  803 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEDEF, 7)){
  805 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
  806 | SCORE += -2;
  807 | }
  808 | }
  809 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 70)){
  811 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
  812 | SCORE += -2;
  813 | }
  814 | }
  815 | }
```

### `ExpertAI_Seq_016()` (source lines 818–978)

```text
  818 | ExpertAI_Seq_016()
  819 | {
  821 | ChkAtkTokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
  822 | ChkDefTokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
  823 | if( ChkAtkTokusei == TOKUSEI_NOOGAADO
  824 | || ChkDefTokusei == TOKUSEI_NOOGAADO ){
  826 | SCORE += -2;
  827 | return;
  828 | }
  829 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_MIYABURU)){
  831 | SCORE += -2;
  832 | return;
  833 | }
  834 | CHK_weather = AI_CMD(CMD_CHECK_WEATHER);
  835 | if( CHK_weather == WEATHER_AME ){
  836 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_KAMINARI)){
  838 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
  839 | SCORE += -2;
  840 | }
  841 | }
  842 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_BOUHUU)){
  844 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
  845 | SCORE += -2;
  846 | }
  847 | }
  848 | }
  849 | if( CHK_weather == WEATHER_ARARE ){
  850 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_HUBUKI)){
  852 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
  853 | SCORE += -2;
  854 | }
  855 | }
  856 | }
  857 | ChkAtkDoku = ExpertAI_Seq_016_sub3();
  858 | if( ChkAtkDoku == 1 ){
  859 | if( ExpertAI_Seq_016_sub1() == 0 ){
  860 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) != TOKUSEI_MAZIKKUGAADO ){
  862 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
  863 | SCORE += -2;
  864 | }
  865 | }
  866 | }
  867 | }
  868 | else if( ChkAtkDoku == 2 ){
  870 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  871 | SCORE += 1;
  872 | }
  873 | }
  874 | if( CHK_weather == WEATHER_AME ){
  875 | if( ChkAtkTokusei == TOKUSEI_AMEUKEZARA
  876 | || ChkAtkTokusei == TOKUSEI_KANSOUHADA ){
  878 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  879 | SCORE += 2;
  880 | }
  881 | }
  882 | }
  883 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_NEWOHARU)){
  885 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  886 | SCORE += 1;
  887 | }
  888 | }
  889 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_AQUARING)){
  891 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  892 | SCORE += 1;
  893 | }
  894 | }
  895 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_TABENOKOSI)){
  897 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  898 | SCORE += 1;
  899 | }
  900 | }
  901 | ChkDefDoku = ExpertAI_Seq_016_sub4();
  902 | if( ChkDefDoku == 1 ){
  903 | if( ExpertAI_Seq_016_sub2() == 0 ){
  904 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) != TOKUSEI_MAZIKKUGAADO ){
  906 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
  907 | SCORE += 2;
  908 | }
  909 | }
  910 | }
  911 | }
  912 | else if( ChkDefDoku == 2 ){
  914 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  915 | SCORE += -1;
  916 | }
  917 | }
  918 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_AVOID, 7)){
  920 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  921 | SCORE += -1;
  922 | }
  923 | }
  924 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_AVOID, 7)){
  926 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  927 | SCORE += -1;
  928 | }
  929 | }
  930 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 127)){
  932 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  933 | SCORE += 1;
  934 | }
  935 | }
  936 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 17)){
  938 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  939 | SCORE += -2;
  940 | }
  941 | }
  942 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 235)){
  944 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  945 | SCORE += -2;
  946 | }
  947 | }
  948 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 272)){
  950 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  951 | SCORE += -2;
  952 | }
  953 | }
  954 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 25)){
  956 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  957 | SCORE += -2;
  958 | }
  959 | }
  960 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 114)){
  962 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  963 | SCORE += -2;
  964 | }
  965 | }
  966 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 78)){
  968 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  969 | SCORE += -2;
  970 | }
  971 | }
  972 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 359)){
  974 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  975 | SCORE += -2;
  976 | }
  977 | }
  978 | }
```

### `ExpertAI_Seq_016_sub1()` (source lines 981–999)

```text
  981 | ExpertAI_Seq_016_sub1()
  982 | {
  983 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 32)){
  984 | return 1;
  985 | }
  986 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 132)){
  987 | return 1;
  988 | }
  989 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 156)){
  990 | return 1;
  991 | }
  992 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 162)){
  993 | return 1;
  994 | }
  995 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 214)){
  996 | return 1;
  997 | }
  998 | return 0;
  999 | }
```

### `ExpertAI_Seq_016_sub2()` (source lines 1000–1018)

```text
 1000 | ExpertAI_Seq_016_sub2()
 1001 | {
 1002 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 32)){
 1003 | return 1;
 1004 | }
 1005 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 132)){
 1006 | return 1;
 1007 | }
 1008 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 156)){
 1009 | return 1;
 1010 | }
 1011 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 162)){
 1012 | return 1;
 1013 | }
 1014 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 214)){
 1015 | return 1;
 1016 | }
 1017 | return 0;
 1018 | }
```

### `ExpertAI_Seq_016_sub3()` (source lines 1019–1052)

```text
 1019 | ExpertAI_Seq_016_sub3()
 1020 | {
 1021 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_YADORIGI)){
 1022 | return 1;
 1023 | }
 1024 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_NOROI)){
 1025 | return 1;
 1026 | }
 1027 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_DOKU)){
 1028 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) != TOKUSEI_POIZUNHIIRU ){
 1029 | return 1;
 1030 | }
 1031 | else {
 1032 | return 2;
 1033 | }
 1034 | }
 1035 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_YAKEDO)){
 1036 | return 1;
 1037 | }
 1038 | if( AI_CMD(CMD_IF_DOKUDOKU, CHECK_ATTACK)){
 1039 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) != TOKUSEI_POIZUNHIIRU ){
 1040 | return 1;
 1041 | }
 1042 | else {
 1043 | return 2;
 1044 | }
 1045 | }
 1046 | if( AI_CMD(CMD_CHECK_WEATHER) == WEATHER_HARE ){
 1047 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_KANSOUHADA ){
 1048 | return 1;
 1049 | }
 1050 | }
 1051 | return 0;
 1052 | }
```

### `ExpertAI_Seq_016_sub4()` (source lines 1053–1086)

```text
 1053 | ExpertAI_Seq_016_sub4()
 1054 | {
 1055 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_YADORIGI)){
 1056 | return 1;
 1057 | }
 1058 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_NOROI)){
 1059 | return 1;
 1060 | }
 1061 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_DOKU)){
 1062 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) != TOKUSEI_POIZUNHIIRU ){
 1063 | return 1;
 1064 | }
 1065 | else {
 1066 | return 2;
 1067 | }
 1068 | }
 1069 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_YAKEDO)){
 1070 | return 1;
 1071 | }
 1072 | if( AI_CMD(CMD_IF_DOKUDOKU, CHECK_DEFENCE)){
 1073 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) != TOKUSEI_POIZUNHIIRU ){
 1074 | return 1;
 1075 | }
 1076 | else {
 1077 | return 2;
 1078 | }
 1079 | }
 1080 | if( AI_CMD(CMD_CHECK_WEATHER) == WEATHER_HARE ){
 1081 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_KANSOUHADA ){
 1082 | return 1;
 1083 | }
 1084 | }
 1085 | return 0;
 1086 | }
```

### `ExpertAI_Seq_017()` (source lines 1088–1115)

```text
 1088 | ExpertAI_Seq_017()
 1089 | {
 1091 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI) ){
 1092 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 1094 | return;
 1095 | }
 1096 | }
 1097 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI) ){
 1098 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1100 | return;
 1101 | }
 1102 | }
 1103 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_AVOID, 10)){
 1105 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1106 | SCORE += 2;
 1107 | }
 1108 | }
 1109 | if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_ATTACK, PARA_HIT, 5)){
 1111 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1112 | SCORE += 2;
 1113 | }
 1114 | }
 1115 | }
```

### `ExpertAI_Seq_018()` (source lines 1117–1144)

```text
 1117 | ExpertAI_Seq_018()
 1118 | {
 1120 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_POW, 7)){
 1122 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1123 | SCORE += -1;
 1124 | }
 1125 | }
 1126 | if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_POW, 5)){
 1128 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1129 | SCORE += -2;
 1130 | }
 1131 | }
 1132 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 50)){
 1134 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1135 | SCORE += -1;
 1136 | }
 1137 | }
 1138 | if( AI_CMD(CMD_CHECK_LAST_WAZA_KIND) == WAZADATA_DMG_SPECIAL){
 1140 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 1141 | SCORE += -2;
 1142 | }
 1143 | }
 1144 | }
```

### `ExpertAI_Seq_019()` (source lines 1146–1167)

```text
 1146 | ExpertAI_Seq_019()
 1147 | {
 1149 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_DEF, 7)){
 1151 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1152 | SCORE += -1;
 1153 | }
 1154 | }
 1155 | if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_DEF, 5)){
 1157 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1158 | SCORE += -2;
 1159 | }
 1160 | }
 1161 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 50)){
 1163 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1164 | SCORE += -1;
 1165 | }
 1166 | }
 1167 | }
```

### `ExpertAI_Seq_020()` (source lines 1170–1183)

```text
 1170 | ExpertAI_Seq_020()
 1171 | {
 1173 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)
 1174 | ){
 1176 | SCORE += -3;
 1177 | return;
 1178 | }
 1179 | if( AI_CMD(CMD_IF_RND_UNDER, 220)
 1180 | ){
 1181 | SCORE += 2;
 1182 | }
 1183 | }
```

### `ExpertAI_Seq_021()` (source lines 1185–1212)

```text
 1185 | ExpertAI_Seq_021()
 1186 | {
 1188 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_SPEPOW, 7)){
 1190 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1191 | SCORE += -1;
 1192 | }
 1193 | }
 1194 | if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_SPEPOW, 5)){
 1196 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1197 | SCORE += -2;
 1198 | }
 1199 | }
 1200 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 50)){
 1202 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1203 | SCORE += -1;
 1204 | }
 1205 | }
 1206 | if( AI_CMD(CMD_CHECK_LAST_WAZA_KIND) == WAZADATA_DMG_PHYSIC){
 1208 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 1209 | SCORE += -2;
 1210 | }
 1211 | }
 1212 | }
```

### `ExpertAI_Seq_022()` (source lines 1214–1235)

```text
 1214 | ExpertAI_Seq_022()
 1215 | {
 1217 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_SPEDEF, 7)){
 1219 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1220 | SCORE += -1;
 1221 | }
 1222 | }
 1223 | if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_SPEDEF, 5)){
 1225 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1226 | SCORE += -2;
 1227 | }
 1228 | }
 1229 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 50)){
 1231 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1232 | SCORE += -1;
 1233 | }
 1234 | }
 1235 | }
```

### `ExpertAI_Seq_023()` (source lines 1237–1391)

```text
 1237 | ExpertAI_Seq_023()
 1238 | {
 1240 | ChkAtkTokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1241 | ChkDefTokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 1242 | if( ChkAtkTokusei == TOKUSEI_NOOGAADO
 1243 | || ChkDefTokusei == TOKUSEI_NOOGAADO ){
 1245 | SCORE += -3;
 1246 | return;
 1247 | }
 1248 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_MIYABURU)){
 1250 | SCORE += -2;
 1251 | return;
 1252 | }
 1253 | CHK_weather = AI_CMD(CMD_CHECK_WEATHER);
 1254 | if( CHK_weather == WEATHER_AME ){
 1255 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_KAMINARI)){
 1257 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 1258 | SCORE += -2;
 1259 | }
 1260 | }
 1261 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_BOUHUU)){
 1263 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 1264 | SCORE += -2;
 1265 | }
 1266 | }
 1267 | }
 1268 | if( CHK_weather == WEATHER_ARARE ){
 1269 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_HUBUKI)){
 1271 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 1272 | SCORE += -2;
 1273 | }
 1274 | }
 1275 | }
 1276 | ChkAtkDoku = ExpertAI_Seq_016_sub3();
 1277 | if( ChkAtkDoku == 1 ){
 1278 | if( ExpertAI_Seq_016_sub1() == 0 ){
 1279 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) != TOKUSEI_MAZIKKUGAADO ){
 1281 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 1282 | SCORE += -2;
 1283 | }
 1284 | }
 1285 | }
 1286 | }
 1287 | else if( ChkAtkDoku == 2 ){
 1289 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1290 | SCORE += 1;
 1291 | }
 1292 | }
 1293 | if( CHK_weather == WEATHER_AME ){
 1294 | if( ChkAtkTokusei == TOKUSEI_AMEUKEZARA
 1295 | || ChkAtkTokusei == TOKUSEI_KANSOUHADA ){
 1297 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1298 | SCORE += 2;
 1299 | }
 1300 | }
 1301 | }
 1302 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_NEWOHARU)){
 1304 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1305 | SCORE += 1;
 1306 | }
 1307 | }
 1308 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_AQUARING)){
 1310 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1311 | SCORE += 1;
 1312 | }
 1313 | }
 1314 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_TABENOKOSI)){
 1316 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1317 | SCORE += 1;
 1318 | }
 1319 | }
 1320 | ChkDefDoku = ExpertAI_Seq_016_sub4();
 1321 | if( ChkDefDoku == 1 ){
 1322 | if( ExpertAI_Seq_016_sub2() == 0 ){
 1323 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) != TOKUSEI_MAZIKKUGAADO ){
 1325 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 1326 | SCORE += 2;
 1327 | }
 1328 | }
 1329 | }
 1330 | }
 1331 | else if( ChkDefDoku == 2 ){
 1333 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1334 | SCORE += -1;
 1335 | }
 1336 | }
 1337 | if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_HIT, 5)){
 1339 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1340 | SCORE += -1;
 1341 | }
 1342 | }
 1343 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_HIT, 7)){
 1345 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1346 | SCORE += -1;
 1347 | }
 1348 | }
 1349 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 17)){
 1351 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1352 | SCORE += -2;
 1353 | }
 1354 | }
 1355 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 235)){
 1357 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1358 | SCORE += -2;
 1359 | }
 1360 | }
 1361 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 272)){
 1363 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1364 | SCORE += -2;
 1365 | }
 1366 | }
 1367 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 25)){
 1369 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1370 | SCORE += -2;
 1371 | }
 1372 | }
 1373 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 114)){
 1375 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1376 | SCORE += -2;
 1377 | }
 1378 | }
 1379 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 78)){
 1381 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1382 | SCORE += -2;
 1383 | }
 1384 | }
 1385 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 359)){
 1387 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1388 | SCORE += -2;
 1389 | }
 1390 | }
 1391 | }
```

### `ExpertAI_Seq_024()` (source lines 1393–1414)

```text
 1393 | ExpertAI_Seq_024()
 1394 | {
 1396 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_AVOID, 7)){
 1398 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1399 | SCORE += -1;
 1400 | }
 1401 | }
 1402 | if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_AVOID, 5)){
 1404 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1405 | SCORE += -2;
 1406 | }
 1407 | }
 1408 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 50)){
 1410 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1411 | SCORE += -1;
 1412 | }
 1413 | }
 1414 | }
```

### `ExpertAI_Seq_025()` (source lines 1416–1462)

```text
 1416 | ExpertAI_Seq_025()
 1417 | {
 1419 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_POW, 7)
 1420 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_DEF, 7)
 1421 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEPOW, 7)
 1422 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEDEF, 7)
 1423 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_AGI, 6)
 1424 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_HIT, 7)
 1425 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_AVOID, 7)
 1426 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_POW, 5)
 1427 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_DEF, 5)
 1428 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_SPEPOW, 5)
 1429 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_SPEDEF, 5)
 1430 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_AGI, 6)
 1431 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_HIT, 5)
 1432 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_AVOID, 5)){
 1434 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 1435 | SCORE += -3;
 1436 | }
 1437 | }
 1438 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_POW, 7)
 1439 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_DEF, 7)
 1440 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_SPEPOW, 7)
 1441 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_SPEDEF, 7)
 1442 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_AGI, 6)
 1443 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_HIT, 7)
 1444 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_AVOID, 7)
 1445 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_ATTACK, PARA_POW, 5)
 1446 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_ATTACK, PARA_DEF, 5)
 1447 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_ATTACK, PARA_SPEPOW, 5)
 1448 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_ATTACK, PARA_SPEDEF, 5)
 1449 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_ATTACK, PARA_AGI, 6)
 1450 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_ATTACK, PARA_HIT, 5)
 1451 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_ATTACK, PARA_AVOID, 5)){
 1453 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 1454 | SCORE += 2;
 1455 | }
 1456 | return;
 1457 | }
 1459 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 1460 | SCORE += -3;
 1461 | }
 1462 | }
```

### `ExpertAI_Seq_026()` (source lines 1464–1473)

```text
 1464 | ExpertAI_Seq_026()
 1465 | {
 1467 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 80)){
 1469 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 1470 | SCORE += -2;
 1471 | }
 1472 | }
 1473 | }
```

### `ExpertAI_Seq_028()` (source lines 1475–1532)

```text
 1475 | ExpertAI_Seq_028()
 1476 | {
 1478 | if( AI_CMD(CMD_CHECK_SLOWSTART_TURN, CHECK_DEFENCE) == 4){
 1480 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1481 | SCORE += 2;
 1482 | }
 1483 | }
 1484 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_DEFENCE, BTL_SIDEEFF_MAKIBISI)){
 1486 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1487 | SCORE += 1;
 1488 | }
 1489 | }
 1490 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_DEFENCE, BTL_SIDEEFF_STEALTHROCK)){
 1492 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1493 | SCORE += 1;
 1494 | }
 1495 | }
 1496 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_DEFENCE, BTL_SIDEEFF_DOKUBISI)){
 1498 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1499 | SCORE += 1;
 1500 | }
 1501 | }
 1502 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_POW, 7)){
 1504 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 1505 | SCORE += 1;
 1506 | }
 1507 | }
 1508 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_DEF, 7)){
 1510 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 1511 | SCORE += 1;
 1512 | }
 1513 | }
 1514 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_SPEPOW, 7)){
 1516 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 1517 | SCORE += 1;
 1518 | }
 1519 | }
 1520 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_SPEDEF, 7)){
 1522 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 1523 | SCORE += 1;
 1524 | }
 1525 | }
 1526 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_AVOID, 7)){
 1528 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 1529 | SCORE += 1;
 1530 | }
 1531 | }
 1532 | }
```

### `ExpertAI_Seq_030()` (source lines 1534–1543)

```text
 1534 | ExpertAI_Seq_030()
 1535 | {
 1537 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 80)){
 1539 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 1540 | SCORE += -2;
 1541 | }
 1542 | }
 1543 | }
```

### `ExpertAI_Seq_032()` (source lines 1546–1597)

```text
 1546 | ExpertAI_Seq_032()
 1547 | {
 1549 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_MAHI)
 1550 | || AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_KONRAN)
 1551 | || AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_MEROMERO)
 1552 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_HIT, 6)
 1553 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_AVOID, 6)){
 1554 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 70)){
 1556 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 1557 | SCORE += 2;
 1558 | return;
 1559 | }
 1560 | }
 1561 | }
 1562 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 80)){
 1564 | SCORE += -5;
 1565 | return;
 1566 | }
 1567 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 60)){
 1568 | AtkTokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1569 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)
 1570 | || AtkTokusei == TOKUSEI_ITAZURAGOKORO ){
 1572 | SCORE += -4;
 1573 | return;
 1574 | }
 1575 | }
 1576 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 50)){
 1578 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 1579 | SCORE += 2;
 1580 | }
 1581 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_AVOID, 7)
 1582 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_DEF, 7)
 1583 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEDEF, 7)){
 1585 | if( AI_CMD(CMD_IF_RND_UNDER, 200)){
 1586 | SCORE += 2;
 1587 | }
 1588 | }
 1589 | }
 1591 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_YOKODORI)){
 1593 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 1594 | SCORE += -2;
 1595 | }
 1596 | }
 1597 | }
```

### `ExpertAI_Seq_033()` (source lines 1599–1633)

```text
 1599 | ExpertAI_Seq_033()
 1600 | {
 1602 | if( AI_CMD(CMD_IFN_HAVE_DAMAGE_WAZA)){
 1604 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1605 | SCORE += 2;
 1606 | return;
 1607 | }
 1608 | }
 1609 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 30)){
 1611 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1612 | SCORE += -1;
 1613 | }
 1614 | }
 1615 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_AVOID, 7)){
 1617 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 1618 | SCORE += 1;
 1619 | }
 1620 | }
 1621 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_DEF, 7)){
 1623 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1624 | SCORE += 1;
 1625 | }
 1626 | }
 1627 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_SPEDEF, 7)){
 1629 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1630 | SCORE += 1;
 1631 | }
 1632 | }
 1633 | }
```

### `ExpertAI_Seq_035()` (source lines 1635–1661)

```text
 1635 | ExpertAI_Seq_035()
 1636 | {
 1638 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 80)){
 1640 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1641 | SCORE += 2;
 1642 | }
 1643 | }
 1644 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 50)){
 1646 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1647 | SCORE += -2;
 1648 | }
 1649 | }
 1650 | if( AI_CMD(CMD_IF_DMG_PHYSIC_OVER, CHECK_DEFENCE)){
 1652 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1653 | SCORE += -3;
 1654 | }
 1655 | return;
 1656 | }
 1658 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 1659 | SCORE += 1;
 1660 | }
 1661 | }
```

### `ExpertAI_Seq_037()` (source lines 1663–1714)

```text
 1663 | ExpertAI_Seq_037()
 1664 | {
 1666 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 80)){
 1668 | SCORE += -5;
 1669 | return;
 1670 | }
 1671 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 60)){
 1672 | AtkTokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1673 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)
 1674 | || AtkTokusei == TOKUSEI_ITAZURAGOKORO ){
 1676 | SCORE += -4;
 1677 | return;
 1678 | }
 1679 | }
 1680 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 50)){
 1682 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 1683 | SCORE += 2;
 1684 | }
 1685 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_AVOID, 7)
 1686 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_DEF, 7)
 1687 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEDEF, 7)){
 1689 | if( AI_CMD(CMD_IF_RND_UNDER, 200)){
 1690 | SCORE += 2;
 1691 | }
 1692 | }
 1693 | }
 1694 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_YOKODORI)){
 1696 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 1697 | SCORE += -2;
 1698 | }
 1699 | }
 1700 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_RAMUNOMI)
 1701 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KAGONOMI)
 1702 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_NEGOTO)
 1703 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_IBIKI)){
 1704 | return;
 1705 | }
 1706 | else if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_AVOID, 8)
 1707 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_DEF, 8)
 1708 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_SPEDEF, 8)){
 1710 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 1711 | SCORE += -2;
 1712 | }
 1713 | }
 1714 | }
```

### `ExpertAI_Seq_038()` (source lines 1716–1729)

```text
 1716 | ExpertAI_Seq_038()
 1717 | {
 1719 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_MUSTHIT_TARGET)){
 1721 | if( AI_CMD(CMD_IF_RND_UNDER, 230)){
 1722 | SCORE += 2;
 1723 | }
 1724 | }
 1726 | if( AI_CMD(CMD_IF_RND_UNDER, 150)){
 1727 | SCORE += 1;
 1728 | }
 1729 | }
```

### `ExpertAI_Seq_039()` (source lines 1731–1795)

```text
 1731 | ExpertAI_Seq_039()
 1732 | {
 1734 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 1735 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 1736 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 1738 | if( AI_CMD(CMD_IF_RND_UNDER, 250) ){
 1739 | SCORE += -2;
 1740 | return;
 1741 | }
 1742 | }
 1743 | waza_seq_no = AI_CMD(CMD_CHECK_WORKWAZA_SEQNO);
 1744 | if( waza_seq_no == 151 ){
 1745 | CHK_weather = AI_CMD(CMD_CHECK_WEATHER);
 1746 | if( CHK_weather == WEATHER_HARE ){
 1748 | if( AI_CMD(CMD_IF_RND_UNDER, 200)){
 1749 | SCORE += 2;
 1750 | return;
 1751 | }
 1752 | }
 1753 | else if( CHK_weather == WEATHER_AME
 1754 | || CHK_weather == WEATHER_SUNAARASHI
 1755 | || CHK_weather == WEATHER_ARARE ){
 1757 | if( AI_CMD(CMD_IF_RND_UNDER, 240)){
 1758 | SCORE += -2;
 1759 | return;
 1760 | }
 1761 | }
 1762 | }
 1763 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_PAWAHURUHAABU)){
 1765 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1766 | SCORE += 2;
 1767 | return;
 1768 | }
 1769 | }
 1770 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 111)
 1771 | || AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 376)
 1772 | || AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 355)
 1773 | || AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 361)){
 1775 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 1776 | SCORE += -2;
 1777 | return;
 1778 | }
 1779 | }
 1780 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 65)){
 1781 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_DEFENCE)){
 1783 | if( AI_CMD(CMD_IF_RND_UNDER, 200)){
 1784 | SCORE += -2;
 1785 | return;
 1786 | }
 1787 | }
 1788 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_DEFENCE)){
 1790 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 1791 | SCORE += -1;
 1792 | }
 1793 | }
 1794 | }
 1795 | }
```

### `ExpertAI_Seq_040()` (source lines 1797–1836)

```text
 1797 | ExpertAI_Seq_040()
 1798 | {
 1800 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 60)){
 1802 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 1803 | SCORE += -1;
 1804 | }
 1805 | }
 1806 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_DEFENCE, 80)){
 1808 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1809 | SCORE += 1;
 1810 | }
 1811 | }
 1812 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_KONRAN)){
 1814 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 1815 | SCORE += 1;
 1816 | }
 1817 | }
 1818 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_MEROMERO)){
 1820 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 1821 | SCORE += 1;
 1822 | }
 1823 | }
 1824 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_NOROI)){
 1826 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 1827 | SCORE += 1;
 1828 | }
 1829 | }
 1830 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_AKUBI)){
 1832 | if( AI_CMD(CMD_IF_RND_UNDER, 150) ){
 1833 | SCORE += 1;
 1834 | }
 1835 | }
 1836 | }
```

### `ExpertAI_Seq_042()` (source lines 1838–1864)

```text
 1838 | ExpertAI_Seq_042()
 1839 | {
 1841 | ChkDefDoku = ExpertAI_Seq_016_sub4();
 1842 | if( ChkDefDoku == 1 ){
 1843 | if( ExpertAI_Seq_016_sub2() == 0 ){
 1844 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) != TOKUSEI_MAZIKKUGAADO ){
 1846 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 1847 | SCORE += 1;
 1848 | }
 1849 | }
 1850 | }
 1851 | }
 1852 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_HOROBINOUTA)){
 1854 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 1855 | SCORE += 2;
 1856 | }
 1857 | }
 1858 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_MEROMERO)){
 1860 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 1861 | SCORE += 1;
 1862 | }
 1863 | }
 1864 | }
```

### `ExpertAI_Seq_043()` (source lines 1866–1897)

```text
 1866 | ExpertAI_Seq_043()
 1867 | {
 1869 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 1870 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 1871 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 1872 | return;
 1873 | }
 1874 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_2BAI)
 1875 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_4BAI)){
 1877 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1878 | SCORE += 1;
 1879 | }
 1880 | }
 1881 | if( AI_CMD(CMD_CHECK_WAZA_KIND) == WAZADATA_DMG_PHYSIC){
 1882 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_DEF, 7)){
 1884 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1885 | SCORE += 1;
 1886 | }
 1887 | }
 1888 | }
 1889 | if( AI_CMD(CMD_CHECK_WAZA_KIND) == WAZADATA_DMG_SPECIAL){
 1890 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_SPEDEF, 7)){
 1892 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1893 | SCORE += 1;
 1894 | }
 1895 | }
 1896 | }
 1897 | }
```

### `ExpertAI_Seq_048()` (source lines 1899–1912)

```text
 1899 | ExpertAI_Seq_048()
 1900 | {
 1902 | ChkAtkTokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1903 | if( ChkAtkTokusei != TOKUSEI_ISIATAMA
 1904 | && ChkAtkTokusei != TOKUSEI_MAZIKKUGAADO ){
 1905 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 10)){
 1907 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1908 | SCORE += -1;
 1909 | }
 1910 | }
 1911 | }
 1912 | }
```

### `ExpertAI_Seq_049()` (source lines 1915–1930)

```text
 1915 | ExpertAI_Seq_049()
 1916 | {
 1918 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_DEFENCE, 50)){
 1920 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 1921 | SCORE += 1;
 1922 | }
 1923 | }
 1924 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 30)){
 1926 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1927 | SCORE += -1;
 1928 | }
 1929 | }
 1930 | }
```

### `ExpertAI_Seq_065()` (source lines 1933–1959)

```text
 1933 | ExpertAI_Seq_065()
 1934 | {
 1936 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 80)){
 1938 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1939 | SCORE += 2;
 1940 | }
 1941 | }
 1942 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 50)){
 1944 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1945 | SCORE += -2;
 1946 | }
 1947 | }
 1948 | if( AI_CMD(CMD_IF_DMG_PHYSIC_UNDER, CHECK_DEFENCE)){
 1950 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1951 | SCORE += -3;
 1952 | }
 1953 | return;
 1954 | }
 1956 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 1957 | SCORE += 1;
 1958 | }
 1959 | }
```

### `ExpertAI_Seq_067()` (source lines 1961–1979)

```text
 1961 | ExpertAI_Seq_067()
 1962 | {
 1964 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_DEFENCE)){
 1965 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_DEFENCE, 20)){
 1967 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 1968 | SCORE += 3;
 1969 | }
 1970 | }
 1971 | return;
 1972 | }
 1973 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 70)){
 1975 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 1976 | SCORE += -1;
 1977 | }
 1978 | }
 1979 | }
```

### `ExpertAI_Seq_070()` (source lines 1981–1998)

```text
 1981 | ExpertAI_Seq_070()
 1982 | {
 1984 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)){
 1985 | return;
 1986 | }
 1987 | wazaNo = CURRENT_MOVE();
 1988 | if( wazaNo == WAZANO_KOGOERUKAZE
 1989 | || wazaNo == WAZANO_GANSEKIHUUZI
 1990 | || wazaNo == WAZANO_MADDOSYOTTO
 1991 | || wazaNo == WAZANO_ROOKIKKU
 1992 | || wazaNo == WAZANO_EREKINETTO
 1993 | || wazaNo == WAZANO_ZINARASI
 1994 | || wazaNo == WAZANO_KOGOERUSEKAI
 1995 | ){
 1996 | Call ExpertAI_Seq_020()
 1997 | }
 1998 | }
```

### `ExpertAI_Seq_078()` (source lines 2000–2014)

```text
 2000 | ExpertAI_Seq_078()
 2001 | {
 2003 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)){
 2005 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 2006 | SCORE += -1;
 2007 | }
 2008 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 30)){
 2010 | SCORE += -2;
 2011 | }
 2012 | }
 2013 | ExpertAI_Seq_017()
 2014 | }
```

### `ExpertAI_Seq_079()` (source lines 2016–2122)

```text
 2016 | ExpertAI_Seq_079()
 2017 | {
 2019 | ATK_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE1);
 2020 | ATK_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE2);
 2021 | DefLastWazaKind = AI_CMD(CMD_CHECK_LAST_WAZA_KIND);
 2022 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK, WAZANO_KIAIPANTI)){
 2024 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 2025 | SCORE += 1;
 2026 | }
 2027 | }
 2028 | if( DefLastWazaKind == 38){
 2030 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 2031 | SCORE += 2;
 2032 | }
 2033 | }
 2034 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 50)){
 2036 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 2037 | SCORE += -1;
 2038 | }
 2039 | }
 2040 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 50)){
 2042 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 2043 | SCORE += -1;
 2044 | }
 2045 | }
 2046 | AtkTokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 2047 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)
 2048 | || AtkTokusei == TOKUSEI_ITAZURAGOKORO ){
 2049 | if( DefLastWazaKind == 1
 2050 | || DefLastWazaKind == 33
 2051 | || DefLastWazaKind == 66
 2052 | || DefLastWazaKind == 67
 2053 | || DefLastWazaKind == 167
 2054 | || DefLastWazaKind == 187){
 2055 | if( AI_CMD(CMD_IFN_POKESICK, CHECK_ATTACK)){
 2057 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 2058 | SCORE += 1;
 2059 | }
 2060 | }
 2061 | }
 2062 | if( DefLastWazaKind == 49
 2063 | || DefLastWazaKind == 118
 2064 | || DefLastWazaKind == 166){
 2065 | if( AI_CMD(CMD_IFN_WAZASICK, CHECK_ATTACK, WAZASICK_KONRAN)){
 2067 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 2068 | SCORE += 1;
 2069 | }
 2070 | }
 2071 | }
 2072 | if( DefLastWazaKind == 84){
 2073 | if( AI_CMD(CMD_IFN_WAZASICK, CHECK_ATTACK, WAZASICK_YADORIGI)){
 2075 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 2076 | SCORE += 1;
 2077 | }
 2078 | }
 2079 | }
 2080 | if( DefLastWazaKind == 38){
 2082 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 2083 | SCORE += 1;
 2084 | }
 2085 | }
 2086 | if( DefLastWazaKind == 294){
 2087 | if( ATK_type1 == POKETYPE_MIZU
 2088 | || ATK_type2 == POKETYPE_MIZU ){
 2090 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 2091 | SCORE += 1;
 2092 | }
 2093 | }
 2094 | }
 2095 | if( DefLastWazaKind == 342){
 2096 | if( AI_CMD(CMD_IF_TYPE_EX, CHECK_ATTACK, POKETYPE_GHOST)
 2097 | || ATK_type1 == POKETYPE_GHOST
 2098 | || ATK_type2 == POKETYPE_GHOST ){
 2099 | return;
 2100 | }
 2101 | else{
 2103 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 2104 | SCORE += 1;
 2105 | }
 2106 | }
 2107 | }
 2108 | if( DefLastWazaKind == 375){
 2109 | if( AI_CMD(CMD_IF_TYPE_EX, CHECK_ATTACK, POKETYPE_KUSA)
 2110 | || ATK_type1 == POKETYPE_KUSA
 2111 | || ATK_type2 == POKETYPE_KUSA ){
 2112 | return;
 2113 | }
 2114 | else{
 2116 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 2117 | SCORE += 1;
 2118 | }
 2119 | }
 2120 | }
 2121 | }
 2122 | }
```

### `ExpertAI_Seq_080()` (source lines 2124–2156)

```text
 2124 | ExpertAI_Seq_080()
 2125 | {
 2127 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 2128 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 2129 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 2130 | return;
 2131 | }
 2132 | ChkAtkTokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 2133 | if( ChkAtkTokusei == TOKUSEI_NAMAKE ){
 2135 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 2136 | SCORE += 1;
 2137 | }
 2138 | return;
 2139 | }
 2140 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)){
 2141 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 55)){
 2143 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 2144 | SCORE += -1;
 2145 | }
 2146 | }
 2147 | }
 2148 | else{
 2149 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 70)){
 2151 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 2152 | SCORE += -1;
 2153 | }
 2154 | }
 2155 | }
 2156 | }
```

### `ExpertAI_Seq_086()` (source lines 2158–2265)

```text
 2158 | ExpertAI_Seq_086()
 2159 | {
 2161 | AtkTokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 2162 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)
 2163 | || AtkTokusei == TOKUSEI_ITAZURAGOKORO ){
 2164 | DefLastWazaKind = AI_CMD(CMD_CHECK_LAST_WAZA_KIND);
 2165 | if( DefLastWazaKind != WAZADATA_DMG_SPECIAL
 2166 | && DefLastWazaKind != WAZADATA_DMG_PHYSIC){
 2168 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 2169 | SCORE += -1;
 2170 | }
 2171 | }
 2172 | ChkDefLastWaza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_DEFENCE);
 2173 | if( ChkDefLastWaza == WAZANO_KINOKONOHOUSI
 2174 | || ChkDefLastWaza == WAZANO_NEMURIGONA
 2175 | || ChkDefLastWaza == WAZANO_DOKUDOKU
 2176 | || ChkDefLastWaza == WAZANO_ONIBI
 2177 | || ChkDefLastWaza == WAZANO_DENZIHA
 2178 | || ChkDefLastWaza == WAZANO_AKUMANOKISSU
 2179 | || ChkDefLastWaza == WAZANO_DAAKUHOORU
 2180 | || ChkDefLastWaza == WAZANO_DOKUNOKONA
 2181 | || ChkDefLastWaza == WAZANO_SIBIREGONA
 2182 | || ChkDefLastWaza == WAZANO_HEBINIRAMI ){
 2183 | if( AI_CMD(CMD_IFN_WAZASICK, CHECK_ATTACK, WAZASICK_MAHI)
 2184 | && AI_CMD(CMD_IFN_WAZASICK, CHECK_ATTACK, WAZASICK_YAKEDO)
 2185 | && AI_CMD(CMD_IFN_WAZASICK, CHECK_ATTACK, WAZASICK_DOKU)
 2186 | && AI_CMD(CMD_IFN_DOKUDOKU, CHECK_ATTACK)){
 2188 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 2189 | SCORE += 2;
 2190 | }
 2191 | }
 2192 | }
 2193 | else if( ChkDefLastWaza == WAZANO_AYASIIHIKARI
 2194 | || ChkDefLastWaza == WAZANO_IBARU
 2195 | || ChkDefLastWaza == WAZANO_ODATERU
 2196 | || ChkDefLastWaza == WAZANO_HURAHURADANSU
 2197 | || ChkDefLastWaza == WAZANO_DENZIHA
 2198 | || ChkDefLastWaza == WAZANO_OSYABERI ){
 2199 | if( AI_CMD(CMD_IFN_WAZASICK, CHECK_ATTACK, WAZASICK_KONRAN)){
 2201 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 2202 | SCORE += 2;
 2203 | }
 2204 | }
 2205 | }
 2206 | else if( ChkDefLastWaza == WAZANO_MEROMERO ){
 2207 | if( AI_CMD(CMD_IFN_WAZASICK, CHECK_ATTACK, WAZASICK_MEROMERO)){
 2209 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 2210 | SCORE += 2;
 2211 | }
 2212 | }
 2213 | }
 2214 | else if( ChkDefLastWaza == WAZANO_TYOUHATU ){
 2215 | if( AI_CMD(CMD_IFN_WAZASICK, CHECK_ATTACK, WAZASICK_TYOUHATSU)){
 2217 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 2218 | SCORE += 2;
 2219 | }
 2220 | }
 2221 | }
 2222 | else if( ChkDefLastWaza == WAZANO_ITYAMON ){
 2223 | if( AI_CMD(CMD_IFN_WAZASICK, CHECK_ATTACK, WAZASICK_ICHAMON)){
 2225 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 2226 | SCORE += 2;
 2227 | }
 2228 | }
 2229 | }
 2230 | else if( ChkDefLastWaza == WAZANO_KANASIBARI ){
 2231 | if( AI_CMD(CMD_IFN_WAZASICK, CHECK_ATTACK, WAZASICK_KANASIBARI)){
 2233 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 2234 | SCORE += 2;
 2235 | }
 2236 | }
 2237 | }
 2238 | else if( ChkDefLastWaza == WAZANO_ANKOORU ){
 2239 | if( AI_CMD(CMD_IFN_WAZASICK, CHECK_ATTACK, WAZASICK_ENCORE)){
 2241 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 2242 | SCORE += 2;
 2243 | }
 2244 | }
 2245 | }
 2246 | else if( ChkDefLastWaza == WAZANO_YADORIGINOTANE ){
 2247 | ATK_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE1);
 2248 | ATK_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE2);
 2249 | if( AI_CMD(CMD_IF_TYPE_EX, CHECK_ATTACK, POKETYPE_KUSA)
 2250 | || ATK_type1 == POKETYPE_KUSA
 2251 | || ATK_type2 == POKETYPE_KUSA ){
 2252 | return;
 2253 | }
 2254 | if(AtkTokusei == TOKUSEI_HEDOROEKI ){
 2255 | return;
 2256 | }
 2257 | if( AI_CMD(CMD_IFN_WAZASICK, CHECK_ATTACK, WAZASICK_YADORIGI)){
 2259 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 2260 | SCORE += 2;
 2261 | }
 2262 | }
 2263 | }
 2264 | }
 2265 | }
```

### `ExpertAI_Seq_087()` (source lines 2267–2280)

```text
 2267 | ExpertAI_Seq_087()
 2268 | {
 2270 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 20)){
 2272 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 2273 | SCORE += 3;
 2274 | }
 2275 | }
 2277 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 2278 | SCORE += 1;
 2279 | }
 2280 | }
```

### `ExpertAI_Seq_089()` (source lines 2282–2329)

```text
 2282 | ExpertAI_Seq_089()
 2283 | {
 2285 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_NEMURI)
 2286 | || AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_KOORI)){
 2288 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 2289 | SCORE += -3;
 2290 | }
 2291 | }
 2292 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_MEROMERO)
 2293 | || AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_KONRAN)){
 2295 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 2296 | SCORE += -1;
 2297 | }
 2298 | }
 2299 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_MAHI)){
 2301 | if( AI_CMD(CMD_IF_RND_UNDER, 50) ){
 2302 | SCORE += -1;
 2303 | }
 2304 | }
 2305 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 30)){
 2307 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 2308 | SCORE += -2;
 2309 | }
 2310 | }
 2311 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 50)){
 2313 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 2314 | SCORE += -1;
 2315 | }
 2316 | }
 2317 | if( AI_CMD(CMD_CHECK_LAST_WAZA_KIND) == WAZADATA_DMG_SPECIAL){
 2319 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 2320 | SCORE += -3;
 2321 | }
 2322 | }
 2323 | if( AI_CMD(CMD_CHECK_LAST_WAZA_KIND) == WAZADATA_DMG_PHYSIC){
 2325 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 2326 | SCORE += 2;
 2327 | }
 2328 | }
 2329 | }
```

### `ExpertAI_Seq_090()` (source lines 2331–2344)

```text
 2331 | ExpertAI_Seq_090()
 2332 | {
 2334 | AtkTokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 2335 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)
 2336 | || AtkTokusei == TOKUSEI_ITAZURAGOKORO ){
 2337 | if( ExpertAI_Seq_090_sub() == 1 ){
 2339 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 2340 | SCORE += 1;
 2341 | }
 2342 | }
 2343 | }
 2344 | }
```

### `ExpertAI_Seq_090_sub()` (source lines 2345–2364)

```text
 2345 | ExpertAI_Seq_090_sub()
 2346 | {
 2347 | ChkDefLastWaza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_DEFENCE);
 2348 | if( ChkDefLastWaza == 0
 2349 | || ChkDefLastWaza == WAZANO_KINOKONOHOUSI
 2350 | || ChkDefLastWaza == WAZANO_NEMURIGONA
 2351 | || ChkDefLastWaza == WAZANO_KAGEBUNSIN
 2352 | || ChkDefLastWaza == WAZANO_MIGAWARI
 2353 | || ChkDefLastWaza == WAZANO_ANKOORU
 2354 | || ChkDefLastWaza == WAZANO_NEKONOTE
 2355 | || ChkDefLastWaza == WAZANO_DAAKUHOORU ){
 2356 | return 0;
 2357 | }
 2358 | DefLastWazaKind = AI_CMD(CMD_CHECK_LAST_WAZA_KIND);
 2359 | if( DefLastWazaKind != WAZADATA_DMG_SPECIAL
 2360 | && DefLastWazaKind != WAZADATA_DMG_PHYSIC){
 2361 | return 1;
 2362 | }
 2363 | return 0;
 2364 | }
```

### `ExpertAI_Seq_091()` (source lines 2366–2409)

```text
 2366 | ExpertAI_Seq_091()
 2367 | {
 2369 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 50)){
 2371 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 2372 | SCORE += -2;
 2373 | }
 2374 | }
 2375 | AtkTokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 2376 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK) == true
 2377 | || AtkTokusei == TOKUSEI_ITAZURAGOKORO ){
 2378 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 50)){
 2380 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 2381 | SCORE += -1;
 2382 | }
 2383 | }
 2384 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 30)){
 2385 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_DEFENCE, 80)){
 2387 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 2388 | SCORE += 3;
 2389 | }
 2390 | }
 2391 | }
 2392 | }
 2393 | else{
 2394 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 70)){
 2396 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 2397 | SCORE += -1;
 2398 | }
 2399 | }
 2400 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 50)){
 2401 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_DEFENCE, 80)){
 2403 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 2404 | SCORE += 1;
 2405 | }
 2406 | }
 2407 | }
 2408 | }
 2409 | }
```

### `ExpertAI_Seq_092()` (source lines 2411–2418)

```text
 2411 | ExpertAI_Seq_092()
 2412 | {
 2415 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 2416 | SCORE += 2;
 2417 | }
 2418 | }
```

### `ExpertAI_Seq_094()` (source lines 2420–2436)

```text
 2420 | ExpertAI_Seq_094()
 2421 | {
 2423 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_MAMORU)
 2424 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_MIKIRI)
 2425 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_KINGUSIIRUDO)
 2426 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_NIIDORUGAADO)
 2427 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_WAIDOGAADO)){
 2429 | SCORE += -2;
 2430 | return;
 2431 | }
 2433 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 2434 | SCORE += 2;
 2435 | }
 2436 | }
```

### `ExpertAI_Seq_098()` (source lines 2438–2481)

```text
 2438 | ExpertAI_Seq_098()
 2439 | {
 2441 | AtkTokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 2442 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)
 2443 | || AtkTokusei == TOKUSEI_ITAZURAGOKORO ){
 2444 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 60)){
 2446 | if( AI_CMD(CMD_IF_RND_UNDER, 200)){
 2447 | SCORE += -2;
 2448 | }
 2449 | }
 2450 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 20)){
 2452 | if( AI_CMD(CMD_IF_RND_UNDER, 200)){
 2453 | SCORE += 1;
 2454 | }
 2455 | }
 2456 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 50)){
 2458 | if( AI_CMD(CMD_IF_RND_UNDER, 100)){
 2459 | SCORE += 1;
 2460 | }
 2461 | }
 2462 | }
 2463 | else{
 2465 | if( AI_CMD(CMD_IF_RND_UNDER, 100)){
 2466 | SCORE += -1;
 2467 | }
 2468 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 80)){
 2470 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 2471 | SCORE += -1;
 2472 | }
 2473 | }
 2474 | else if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 40)){
 2476 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 2477 | SCORE += -1;
 2478 | }
 2479 | }
 2480 | }
 2481 | }
```

### `ExpertAI_Seq_099()` (source lines 2483–2514)

```text
 2483 | ExpertAI_Seq_099()
 2484 | {
 2486 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)){
 2487 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 33)){
 2489 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 2490 | SCORE += -2;
 2491 | }
 2492 | }
 2493 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 8)){
 2495 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 2496 | SCORE += 1;
 2497 | }
 2498 | }
 2499 | }
 2500 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_DEFENCE)){
 2501 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 60)){
 2503 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 2504 | SCORE += -1;
 2505 | }
 2506 | }
 2507 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 40)){
 2509 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 2510 | SCORE += 1;
 2511 | }
 2512 | }
 2513 | }
 2514 | }
```

### `ExpertAI_Seq_102()` (source lines 2516–2557)

```text
 2516 | ExpertAI_Seq_102()
 2517 | {
 2519 | if( AI_CMD(CMD_IF_BENCH_COND, CHECK_ATTACK)){
 2521 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 2522 | SCORE += 1;
 2523 | }
 2524 | }
 2525 | else if( AI_CMD(CMD_IF_POKESICK, CHECK_ATTACK)){
 2526 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 70)){
 2528 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 2529 | SCORE += 1;
 2530 | }
 2531 | }
 2532 | }
 2533 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_MAHI)){
 2535 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 2536 | SCORE += 1;
 2537 | }
 2538 | }
 2539 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 2540 | if( CHK_rule == BTL_RULE_DOUBLE
 2541 | || CHK_rule == BTL_RULE_TRIPLE ){
 2542 | if( AI_CMD(CMD_IF_POKESICK, CHECK_ATTACK_FRIEND)){
 2543 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK_FRIEND, 70)){
 2545 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 2546 | SCORE += 1;
 2547 | }
 2548 | }
 2549 | }
 2550 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK_FRIEND, WAZASICK_MAHI)){
 2552 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 2553 | SCORE += 1;
 2554 | }
 2555 | }
 2556 | }
 2557 | }
```

### `ExpertAI_Seq_105()` (source lines 2559–2611)

```text
 2559 | ExpertAI_Seq_105()
 2560 | {
 2562 | if( AI_CMD(CMD_CHECK_SOUBI_ITEM, CHECK_DEFENCE) == 0
 2563 | || AI_CMD(CMD_CHECK_SOUBI_ITEM, CHECK_ATTACK) != 0){
 2565 | return;
 2566 | }
 2567 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_NENTYAKU ){
 2569 | return;
 2570 | }
 2571 | else if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_GANZYOU ){
 2572 | if( AI_CMD(CMD_IF_LEVEL, LEVEL_ATTACK)){
 2575 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 2576 | SCORE += 1;
 2577 | }
 2578 | }
 2579 | }
 2580 | if( ExpertAI_Seq_GoodItemPokemon() == 1 ){
 2582 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 2583 | SCORE += 1;
 2584 | }
 2585 | }
 2586 | DefMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
 2587 | if( DefMonsNo == MONSNO_ARUSEUSU
 2588 | || DefMonsNo == MONSNO_GENOSEKUTO){
 2590 | SCORE += -1;
 2591 | }
 2592 | if( DefMonsNo == MONSNO_GIRATHINA){
 2593 | if(AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_HAKKINDAMA)){
 2595 | SCORE += -1;
 2596 | }
 2597 | }
 2598 | if( AI_CMD(CMD_IF_MEGAEVOLVED, CHECK_DEFENCE) ){
 2600 | SCORE += -1;
 2601 | }
 2602 | if( ExpertAI_Seq_MegaShinkaPokemon() == 1 ){
 2604 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 2605 | SCORE += -5;
 2606 | return;
 2607 | }
 2608 | SCORE += -1;
 2609 | return;
 2610 | }
 2611 | }
```

### `ExpertAI_Seq_GoodItemPokemon()` (source lines 2614–2623)

```text
 2614 | ExpertAI_Seq_GoodItemPokemon()
 2615 | {
 2616 | DefMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
 2617 | if( DefMonsNo == MONSNO_PIKATYUU || DefMonsNo == MONSNO_GARAGARA
 2618 | || DefMonsNo == MONSNO_RAKKII || DefMonsNo == MONSNO_PORIGON2
 2619 | || DefMonsNo == MONSNO_SAMAYOORU ){
 2620 | return 1;
 2621 | }
 2622 | return 0;
 2623 | }
```

### `ExpertAI_Seq_108()` (source lines 2627–2661)

```text
 2627 | ExpertAI_Seq_108()
 2628 | {
 2630 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_HUMITUKE)){
 2632 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 2633 | SCORE += -2;
 2634 | }
 2635 | }
 2636 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_NOSIKAKARI)){
 2638 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 2639 | SCORE += -2;
 2640 | }
 2641 | }
 2642 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_HIITOSUTANPU)){
 2644 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 2645 | SCORE += -2;
 2646 | }
 2647 | }
 2648 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_HURAINGUPURESU)){
 2650 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 2651 | SCORE += -2;
 2652 | }
 2653 | }
 2654 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_DORAGONDAIBU)){
 2656 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 2657 | SCORE += -2;
 2658 | }
 2659 | }
 2660 | ExpertAI_Seq_016()
 2661 | }
```

### `ExpertAI_Seq_109()` (source lines 2663–2700)

```text
 2663 | ExpertAI_Seq_109()
 2664 | {
 2666 | ATK_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE1);
 2667 | ATK_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE2);
 2668 | if( ATK_type1 == POKETYPE_GHOST
 2669 | || ATK_type2 == POKETYPE_GHOST ){
 2671 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 70)){
 2673 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 2674 | SCORE += -1;
 2675 | }
 2676 | }
 2677 | if( AI_CMD(CMD_CHECK_BENCH_COUNT, CHECK_ATTACK) == 0 ){
 2679 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 2680 | SCORE += -1;
 2681 | }
 2682 | }
 2684 | if( AI_CMD(CMD_IF_RND_UNDER, 100)){
 2685 | SCORE += 1;
 2686 | }
 2687 | }
 2688 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK, WAZANO_ZYAIROBOORU)){
 2690 | if( AI_CMD(CMD_IF_RND_UNDER, 100)){
 2691 | SCORE += 1;
 2692 | }
 2693 | }
 2694 | if( AI_CMD(CMD_FLDEFF_CHECK, EFF_TRICKROOM)){
 2696 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 2697 | SCORE += 1;
 2698 | }
 2699 | }
 2700 | }
```

### `ExpertAI_Seq_111()` (source lines 2702–2772)

```text
 2702 | ExpertAI_Seq_111()
 2703 | {
 2705 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_IBANNOMI)){
 2706 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 25)){
 2708 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 2709 | SCORE += -3;
 2710 | }
 2711 | }
 2712 | }
 2713 | AtkLastWaza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_ATTACK);
 2714 | if( AtkLastWaza == WAZANO_MAMORU || AtkLastWaza == WAZANO_MIKIRI
 2715 | || AtkLastWaza == WAZANO_KORAERU || AtkLastWaza == WAZANO_WAIDOGAADO
 2716 | || AtkLastWaza == WAZANO_FASUTOGAADO || AtkLastWaza == WAZANO_KINGUSIIRUDO
 2717 | || AtkLastWaza == WAZANO_TATAMIGAESI || AtkLastWaza == WAZANO_NIIDORUGAADO ){
 2719 | if( AI_CMD(CMD_IF_RND_UNDER, 240)){
 2720 | SCORE += -3;
 2721 | }
 2722 | }
 2723 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_FEINTO)){
 2725 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 2726 | SCORE += -1;
 2727 | }
 2728 | }
 2729 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_DEFENCE, WAZANO_IZIGENHOORU)){
 2731 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 2732 | SCORE += -1;
 2733 | }
 2734 | }
 2735 | ChkDefLastWaza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_DEFENCE);
 2736 | if( ChkDefLastWaza == WAZANO_SYADOODAIBU
 2737 | || ChkDefLastWaza == WAZANO_GOOSUTODAIBU ){
 2739 | if( AI_CMD(CMD_IF_RND_UNDER, 240)){
 2740 | SCORE += -3;
 2741 | }
 2742 | return;
 2743 | }
 2744 | ChkAtkDoku = ExpertAI_Seq_016_sub3();
 2745 | if( ChkAtkDoku == 1 ){
 2746 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) != TOKUSEI_MAZIKKUGAADO ){
 2748 | if( AI_CMD(CMD_IF_RND_UNDER, 220)){
 2749 | SCORE += -2;
 2750 | }
 2751 | }
 2752 | }
 2753 | ChkDefDoku = ExpertAI_Seq_016_sub4();
 2754 | if( ChkDefDoku == 1 ){
 2755 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) != TOKUSEI_MAZIKKUGAADO ){
 2757 | if( AI_CMD(CMD_IF_COMMONRND_OVER, 125) ){
 2758 | SCORE += 1;
 2759 | }
 2760 | }
 2761 | }
 2762 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_MUSTHIT_TARGET)){
 2764 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 2765 | SCORE += 2;
 2766 | }
 2767 | }
 2769 | if( AI_CMD(CMD_IF_COMMONRND_OVER, 180)){
 2770 | SCORE += 1;
 2771 | }
 2772 | }
```

### `ExpertAI_Seq_112()` (source lines 2774–2788)

```text
 2774 | ExpertAI_Seq_112()
 2775 | {
 2777 | MAKIBISHI_count = AI_CMD(CMD_CHECK_SIDEEFF_COUNT, CHECK_DEFENCE, BTL_SIDEEFF_MAKIBISI);
 2778 | HIKAE_count = AI_CMD(CMD_CHECK_BENCH_COUNT, CHECK_DEFENCE);
 2779 | if(MAKIBISHI_count != 0
 2780 | ){
 2782 | return;
 2783 | }
 2785 | if( AI_CMD(CMD_IF_RND_UNDER, 100)){
 2786 | SCORE += 1;
 2787 | }
 2788 | }
```

### `ExpertAI_Seq_113()` (source lines 2790–2808)

```text
 2790 | ExpertAI_Seq_113()
 2791 | {
 2793 | DEF_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1);
 2794 | DEF_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2);
 2795 | if( DEF_type1 == POKETYPE_GHOST
 2796 | || DEF_type2 == POKETYPE_GHOST ){
 2798 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 2799 | SCORE += 2;
 2800 | }
 2801 | }
 2802 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_AVOID, 7)){
 2804 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 2805 | SCORE += 2;
 2806 | }
 2807 | }
 2808 | }
```

### `ExpertAI_Seq_116()` (source lines 2810–2835)

```text
 2810 | ExpertAI_Seq_116()
 2811 | {
 2813 | if( AI_CMD(CMD_CHECK_MAMORU_COUNT, CHECK_ATTACK) != 0 ){
 2815 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 2816 | SCORE += -4;
 2817 | }
 2818 | }
 2819 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 50)){
 2821 | if( AI_CMD(CMD_IF_RND_UNDER, 160) ){
 2822 | SCORE += -3;
 2823 | }
 2824 | }
 2825 | ChkAtkDoku = ExpertAI_Seq_016_sub3();
 2826 | if( ChkAtkDoku == 1 ){
 2827 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) != TOKUSEI_MAZIKKUGAADO ){
 2829 | SCORE += -5;
 2830 | }
 2831 | }
 2832 | if( AI_CMD(CMD_IF_COMMONRND_UNDER, 128)){
 2833 | SCORE += 2;
 2834 | }
 2835 | }
```

### `ExpertAI_Seq_118()` (source lines 2837–2848)

```text
 2837 | ExpertAI_Seq_118()
 2838 | {
 2840 | DefLastWazaKind = AI_CMD(CMD_CHECK_LAST_WAZA_KIND);
 2841 | if( DefLastWazaKind == WAZADATA_DMG_PHYSIC){
 2843 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 2844 | SCORE += -2;
 2845 | }
 2846 | }
 2847 | ExpertAI_Seq_049()
 2848 | }
```

### `ExpertAI_Seq_120()` (source lines 2850–2858)

```text
 2850 | ExpertAI_Seq_120()
 2851 | {
 2854 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 2855 | SCORE += 1;
 2856 | }
 2857 | ExpertAI_Seq_049()
 2858 | }
```

### `ExpertAI_Seq_121()` (source lines 2860–2881)

```text
 2860 | ExpertAI_Seq_121()
 2861 | {
 2863 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 2864 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 2865 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 2866 | SCORE += -1;
 2867 | return;
 2868 | }
 2869 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_2BAI)){
 2871 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 2872 | SCORE += 1;
 2873 | }
 2874 | }
 2875 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_4BAI)){
 2877 | if( AI_CMD(CMD_IF_RND_UNDER, 150)){
 2878 | SCORE += 2;
 2879 | }
 2880 | }
 2881 | }
```

### `ExpertAI_Seq_123()` (source lines 2883–2904)

```text
 2883 | ExpertAI_Seq_123()
 2884 | {
 2886 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 2887 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 2888 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 2889 | SCORE += -1;
 2890 | return;
 2891 | }
 2892 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_2BAI)){
 2894 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 2895 | SCORE += 1;
 2896 | }
 2897 | }
 2898 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_4BAI)){
 2900 | if( AI_CMD(CMD_IF_RND_UNDER, 150)){
 2901 | SCORE += 2;
 2902 | }
 2903 | }
 2904 | }
```

### `ExpertAI_Seq_127()` (source lines 2906–2952)

```text
 2906 | ExpertAI_Seq_127()
 2907 | {
 2909 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_POW, 7)
 2910 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_DEF, 7)
 2911 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEPOW, 7)
 2912 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEDEF, 7)
 2913 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_AVOID, 7)
 2914 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_HIT, 7)){
 2915 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)){
 2916 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 60)){
 2918 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 2919 | return;
 2920 | }
 2921 | }
 2923 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 2924 | SCORE += 1;
 2925 | }
 2926 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 40)){
 2928 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 2929 | SCORE += 3;
 2930 | }
 2931 | }
 2932 | }
 2933 | else if( AI_CMD(CMD_IF_FIRST, IF_FIRST_DEFENCE)){
 2934 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 70)){
 2936 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 2937 | return;
 2938 | }
 2939 | }
 2941 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 2942 | SCORE += 1;
 2943 | }
 2944 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 50)){
 2946 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 2947 | SCORE += 3;
 2948 | }
 2949 | }
 2950 | }
 2951 | }
 2952 | }
```

### `ExpertAI_Seq_128()` (source lines 2954–2981)

```text
 2954 | ExpertAI_Seq_128()
 2955 | {
 2957 | DEF_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1);
 2958 | DEF_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2);
 2959 | if( AI_CMD(CMD_CHECK_NEKODAMASI, CHECK_ATTACK) == 0 ){
 2960 | if( DEF_type1 == POKETYPE_GHOST
 2961 | || DEF_type2 == POKETYPE_GHOST
 2962 | || DEF_type1 == POKETYPE_ESPER
 2963 | || DEF_type2 == POKETYPE_ESPER ){
 2965 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 2966 | SCORE += 2;
 2967 | }
 2968 | }
 2969 | }
 2970 | else{
 2971 | if( DEF_type1 == POKETYPE_GHOST
 2972 | || DEF_type2 == POKETYPE_GHOST
 2973 | || DEF_type1 == POKETYPE_ESPER
 2974 | || DEF_type2 == POKETYPE_ESPER ){
 2976 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 2977 | SCORE += 1;
 2978 | }
 2979 | }
 2980 | }
 2981 | }
```

### `ExpertAI_Seq_132()` (source lines 2983–2997)

```text
 2983 | ExpertAI_Seq_132()
 2984 | {
 2986 | CHK_weather = AI_CMD(CMD_CHECK_WEATHER);
 2987 | if( CHK_weather == WEATHER_AME
 2988 | || CHK_weather == WEATHER_ARARE
 2989 | || CHK_weather == WEATHER_SUNAARASHI ){
 2991 | if( AI_CMD(CMD_IF_RND_UNDER, 240)){
 2992 | SCORE += -2;
 2993 | }
 2994 | return;
 2995 | }
 2996 | ExpertAI_Seq_032()
 2997 | }
```

### `ExpertAI_Seq_135()` (source lines 2999–3004)

```text
 2999 | ExpertAI_Seq_135()
 3000 | {
 3002 | WazaType = AI_CMD(CMD_GET_MEZAME_TYPE, CHECK_ATTACK);
 3003 | ExpertAI_TypeCheck( WazaType )
 3004 | }
```

### `ExpertAI_TypeCheck(WazaType)` (source lines 3006–3639)

```text
 3006 | ExpertAI_TypeCheck( WazaType )
 3007 | {
 3008 | DEF_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1);
 3009 | DEF_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2);
 3010 | ATK_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 3011 | DEF_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 3012 | if( WazaType == POKETYPE_NORMAL ){
 3014 | if( DEF_type1 == POKETYPE_GHOST
 3015 | || DEF_type2 == POKETYPE_GHOST ){
 3016 | SCORE += -10;
 3017 | return;
 3018 | }
 3019 | if( AI_CMD(CMD_IF_TYPE_EX, CHECK_DEFENCE, POKETYPE_GHOST) ){
 3020 | SCORE += -10;
 3021 | return;
 3022 | }
 3023 | if( DEF_type1 == POKETYPE_IWA
 3024 | || DEF_type1 == POKETYPE_HAGANE ){
 3025 | SCORE += -1;
 3026 | }
 3027 | if( DEF_type1 == DEF_type2 ){
 3028 | return;
 3029 | }
 3030 | if( DEF_type2 == POKETYPE_IWA
 3031 | || DEF_type2 == POKETYPE_HAGANE){
 3032 | SCORE += -1;
 3033 | }
 3034 | return;
 3035 | }
 3036 | if( WazaType == POKETYPE_HONOO ){
 3038 | if( DEF_Tokusei == TOKUSEI_MORAIBI ){
 3039 | if( ATK_Tokusei != TOKUSEI_KATAYABURI
 3040 | && ATK_Tokusei != TOKUSEI_TAABOBUREIZU
 3041 | && ATK_Tokusei != TOKUSEI_TERABORUTEEZI){
 3042 | SCORE += -10;
 3043 | return;
 3044 | }
 3045 | }
 3046 | if( DEF_Tokusei == TOKUSEI_TAINETU
 3047 | || DEF_Tokusei == TOKUSEI_ATUISIBOU ){
 3048 | SCORE += -1;
 3049 | }
 3050 | if( DEF_type1 == POKETYPE_HONOO
 3051 | || DEF_type1 == POKETYPE_MIZU
 3052 | || DEF_type1 == POKETYPE_IWA
 3053 | || DEF_type1 == POKETYPE_DRAGON ){
 3054 | SCORE += -1;
 3055 | }
 3056 | else if( DEF_type1 == POKETYPE_KUSA
 3057 | || DEF_type1 == POKETYPE_KOORI
 3058 | || DEF_type1 == POKETYPE_MUSHI
 3059 | || DEF_type1 == POKETYPE_HAGANE ){
 3060 | SCORE += 1;
 3061 | }
 3062 | if( AI_CMD(CMD_IF_TYPE_EX, CHECK_DEFENCE, POKETYPE_KUSA)){
 3063 | SCORE += 1;
 3064 | }
 3065 | if( DEF_type1 == DEF_type2 ){
 3066 | return;
 3067 | }
 3068 | if( DEF_type2 == POKETYPE_HONOO
 3069 | || DEF_type2 == POKETYPE_MIZU
 3070 | || DEF_type2 == POKETYPE_IWA
 3071 | || DEF_type2 == POKETYPE_DRAGON ){
 3072 | SCORE += -1;
 3073 | }
 3074 | else if( DEF_type2 == POKETYPE_KUSA
 3075 | || DEF_type2 == POKETYPE_KOORI
 3076 | || DEF_type2 == POKETYPE_MUSHI
 3077 | || DEF_type2 == POKETYPE_HAGANE ){
 3078 | SCORE += 1;
 3079 | }
 3080 | return;
 3081 | }
 3082 | if( WazaType == POKETYPE_MIZU ){
 3084 | if( DEF_Tokusei == TOKUSEI_TYOSUI
 3085 | || DEF_Tokusei == TOKUSEI_YOBIMIZU
 3086 | || DEF_Tokusei == TOKUSEI_KANSOUHADA ){
 3087 | if( ATK_Tokusei != TOKUSEI_KATAYABURI
 3088 | && ATK_Tokusei != TOKUSEI_TAABOBUREIZU
 3089 | && ATK_Tokusei != TOKUSEI_TERABORUTEEZI){
 3090 | SCORE += -10;
 3091 | return;
 3092 | }
 3093 | }
 3094 | if( DEF_type1 == POKETYPE_MIZU
 3095 | || DEF_type1 == POKETYPE_KUSA
 3096 | || DEF_type1 == POKETYPE_DRAGON ){
 3097 | SCORE += -1;
 3098 | }
 3099 | else if( DEF_type1 == POKETYPE_HONOO
 3100 | || DEF_type1 == POKETYPE_JIMEN
 3101 | || DEF_type1 == POKETYPE_IWA ){
 3102 | SCORE += 1;
 3103 | }
 3104 | if( AI_CMD(CMD_IF_TYPE_EX, CHECK_DEFENCE, POKETYPE_KUSA)){
 3105 | SCORE += -1;
 3106 | }
 3107 | if( DEF_type1 == DEF_type2 ){
 3108 | return;
 3109 | }
 3110 | if( DEF_type2 == POKETYPE_MIZU
 3111 | || DEF_type2 == POKETYPE_KUSA
 3112 | || DEF_type2 == POKETYPE_DRAGON ){
 3113 | SCORE += -1;
 3114 | }
 3115 | else if( DEF_type2 == POKETYPE_HONOO
 3116 | || DEF_type2 == POKETYPE_JIMEN
 3117 | || DEF_type2 == POKETYPE_IWA ){
 3118 | SCORE += 1;
 3119 | }
 3120 | return;
 3121 | }
 3122 | if( WazaType == POKETYPE_KUSA ){
 3124 | if( DEF_Tokusei == TOKUSEI_SOUSYOKU ){
 3125 | if( ATK_Tokusei != TOKUSEI_KATAYABURI
 3126 | && ATK_Tokusei != TOKUSEI_TAABOBUREIZU
 3127 | && ATK_Tokusei != TOKUSEI_TERABORUTEEZI){
 3128 | SCORE += -10;
 3129 | return;
 3130 | }
 3131 | }
 3132 | if( DEF_type1 == POKETYPE_HONOO
 3133 | || DEF_type1 == POKETYPE_KUSA
 3134 | || DEF_type1 == POKETYPE_DOKU
 3135 | || DEF_type1 == POKETYPE_HIKOU
 3136 | || DEF_type1 == POKETYPE_MUSHI
 3137 | || DEF_type1 == POKETYPE_DRAGON
 3138 | || DEF_type1 == POKETYPE_HAGANE ){
 3139 | SCORE += -1;
 3140 | }
 3141 | else if( DEF_type1 == POKETYPE_MIZU
 3142 | || DEF_type1 == POKETYPE_JIMEN
 3143 | || DEF_type1 == POKETYPE_IWA ){
 3144 | SCORE += 1;
 3145 | }
 3146 | if( AI_CMD(CMD_IF_TYPE_EX, CHECK_DEFENCE, POKETYPE_KUSA)){
 3147 | SCORE += -1;
 3148 | }
 3149 | if( DEF_type1 == DEF_type2 ){
 3150 | return;
 3151 | }
 3152 | if( DEF_type2 == POKETYPE_HONOO
 3153 | || DEF_type2 == POKETYPE_KUSA
 3154 | || DEF_type2 == POKETYPE_DOKU
 3155 | || DEF_type2 == POKETYPE_HIKOU
 3156 | || DEF_type2 == POKETYPE_MUSHI
 3157 | || DEF_type2 == POKETYPE_DRAGON
 3158 | || DEF_type2 == POKETYPE_HAGANE ){
 3159 | SCORE += -1;
 3160 | }
 3161 | else if( DEF_type2 == POKETYPE_MIZU
 3162 | || DEF_type2 == POKETYPE_JIMEN
 3163 | || DEF_type2 == POKETYPE_IWA ){
 3164 | SCORE += 1;
 3165 | }
 3166 | return;
 3167 | }
 3168 | if( WazaType == POKETYPE_DENKI ){
 3170 | if( DEF_type1 == POKETYPE_JIMEN
 3171 | || DEF_type2 == POKETYPE_JIMEN ){
 3172 | SCORE += -10;
 3173 | return;
 3174 | }
 3175 | if( DEF_Tokusei == TOKUSEI_TIKUDEN
 3176 | || DEF_Tokusei == TOKUSEI_DENKIENZIN
 3177 | || DEF_Tokusei == TOKUSEI_HIRAISIN ){
 3178 | if( ATK_Tokusei != TOKUSEI_KATAYABURI
 3179 | && ATK_Tokusei != TOKUSEI_TAABOBUREIZU
 3180 | && ATK_Tokusei != TOKUSEI_TERABORUTEEZI){
 3181 | SCORE += -10;
 3182 | return;
 3183 | }
 3184 | }
 3185 | if( DEF_type1 == POKETYPE_KUSA
 3186 | || DEF_type1 == POKETYPE_DENKI
 3187 | || DEF_type1 == POKETYPE_DRAGON ){
 3188 | SCORE += -1;
 3189 | }
 3190 | else if( DEF_type1 == POKETYPE_MIZU
 3191 | || DEF_type1 == POKETYPE_HIKOU ){
 3192 | SCORE += 1;
 3193 | }
 3194 | if( AI_CMD(CMD_IF_TYPE_EX, CHECK_DEFENCE, POKETYPE_KUSA)){
 3195 | SCORE += -1;
 3196 | }
 3197 | if( DEF_type1 == DEF_type2 ){
 3198 | return;
 3199 | }
 3200 | if( DEF_type2 == POKETYPE_KUSA
 3201 | || DEF_type2 == POKETYPE_DENKI
 3202 | || DEF_type2 == POKETYPE_DRAGON ){
 3203 | SCORE += -1;
 3204 | }
 3205 | else if( DEF_type2 == POKETYPE_MIZU
 3206 | || DEF_type2 == POKETYPE_HIKOU ){
 3207 | SCORE += 1;
 3208 | }
 3209 | return;
 3210 | }
 3211 | if( WazaType == POKETYPE_KOORI ){
 3213 | if( DEF_Tokusei == TOKUSEI_ATUISIBOU ){
 3214 | SCORE += -1;
 3215 | }
 3216 | if( DEF_type1 == POKETYPE_HONOO
 3217 | || DEF_type1 == POKETYPE_MIZU
 3218 | || DEF_type1 == POKETYPE_KOORI
 3219 | || DEF_type1 == POKETYPE_HAGANE ){
 3220 | SCORE += -1;
 3221 | }
 3222 | else if( DEF_type1 == POKETYPE_KUSA
 3223 | || DEF_type1 == POKETYPE_JIMEN
 3224 | || DEF_type1 == POKETYPE_HIKOU
 3225 | || DEF_type1 == POKETYPE_DRAGON ){
 3226 | SCORE += 1;
 3227 | }
 3228 | if( AI_CMD(CMD_IF_TYPE_EX, CHECK_DEFENCE, POKETYPE_KUSA)){
 3229 | SCORE += 1;
 3230 | }
 3231 | if( DEF_type1 == DEF_type2 ){
 3232 | return;
 3233 | }
 3234 | if( DEF_type2 == POKETYPE_HONOO
 3235 | || DEF_type2 == POKETYPE_MIZU
 3236 | || DEF_type2 == POKETYPE_KOORI
 3237 | || DEF_type2 == POKETYPE_HAGANE ){
 3238 | SCORE += -1;
 3239 | }
 3240 | else if( DEF_type2 == POKETYPE_KUSA
 3241 | || DEF_type2 == POKETYPE_JIMEN
 3242 | || DEF_type2 == POKETYPE_HIKOU
 3243 | || DEF_type2 == POKETYPE_DRAGON ){
 3244 | SCORE += 1;
 3245 | }
 3246 | return;
 3247 | }
 3248 | if( WazaType == POKETYPE_KAKUTOU ){
 3250 | if( DEF_type1 == POKETYPE_GHOST
 3251 | || DEF_type2 == POKETYPE_GHOST ){
 3252 | SCORE += -10;
 3253 | return;
 3254 | }
 3255 | if( AI_CMD(CMD_IF_TYPE_EX, CHECK_DEFENCE, POKETYPE_GHOST)){
 3256 | SCORE += -10;
 3257 | return;
 3258 | }
 3259 | if( DEF_type1 == POKETYPE_DOKU
 3260 | || DEF_type1 == POKETYPE_HIKOU
 3261 | || DEF_type1 == POKETYPE_ESPER
 3262 | || DEF_type1 == POKETYPE_MUSHI
 3263 | || DEF_type1 == POKETYPE_FAIRY ){
 3264 | SCORE += -1;
 3265 | }
 3266 | else if( DEF_type1 == POKETYPE_NORMAL
 3267 | || DEF_type1 == POKETYPE_KOORI
 3268 | || DEF_type1 == POKETYPE_IWA
 3269 | || DEF_type1 == POKETYPE_AKU
 3270 | || DEF_type1 == POKETYPE_HAGANE ){
 3271 | SCORE += 1;
 3272 | }
 3273 | if( DEF_type1 == DEF_type2 ){
 3274 | return;
 3275 | }
 3276 | if( DEF_type2 == POKETYPE_DOKU
 3277 | || DEF_type2 == POKETYPE_HIKOU
 3278 | || DEF_type2 == POKETYPE_ESPER
 3279 | || DEF_type2 == POKETYPE_MUSHI
 3280 | || DEF_type2 == POKETYPE_FAIRY ){
 3281 | SCORE += -1;
 3282 | }
 3283 | else if( DEF_type2 == POKETYPE_NORMAL
 3284 | || DEF_type2 == POKETYPE_KOORI
 3285 | || DEF_type2 == POKETYPE_IWA
 3286 | || DEF_type2 == POKETYPE_AKU
 3287 | || DEF_type2 == POKETYPE_HAGANE ){
 3288 | SCORE += 1;
 3289 | }
 3290 | return;
 3291 | }
 3292 | if( WazaType == POKETYPE_DOKU ){
 3294 | if( DEF_type1 == POKETYPE_HAGANE
 3295 | || DEF_type2 == POKETYPE_HAGANE ){
 3296 | SCORE += -10;
 3297 | return;
 3298 | }
 3299 | if( DEF_type1 == POKETYPE_DOKU
 3300 | || DEF_type1 == POKETYPE_JIMEN
 3301 | || DEF_type1 == POKETYPE_IWA
 3302 | || DEF_type1 == POKETYPE_GHOST ){
 3303 | SCORE += -1;
 3304 | }
 3305 | else if( DEF_type1 == POKETYPE_KUSA
 3306 | || DEF_type1 == POKETYPE_FAIRY ){
 3307 | SCORE += 1;
 3308 | }
 3309 | if( AI_CMD(CMD_IF_TYPE_EX, CHECK_DEFENCE, POKETYPE_KUSA)){
 3310 | SCORE += 1;
 3311 | }
 3312 | else if( AI_CMD(CMD_IF_TYPE_EX, CHECK_DEFENCE, POKETYPE_GHOST)){
 3313 | SCORE += -1;
 3314 | }
 3315 | if( DEF_type1 == DEF_type2 ){
 3316 | return;
 3317 | }
 3318 | if( DEF_type2 == POKETYPE_DOKU
 3319 | || DEF_type2 == POKETYPE_JIMEN
 3320 | || DEF_type2 == POKETYPE_IWA
 3321 | || DEF_type2 == POKETYPE_GHOST ){
 3322 | SCORE += -1;
 3323 | }
 3324 | else if( DEF_type2 == POKETYPE_KUSA
 3325 | || DEF_type2 == POKETYPE_FAIRY ){
 3326 | SCORE += 1;
 3327 | }
 3328 | return;
 3329 | }
 3330 | if( WazaType == POKETYPE_JIMEN ){
 3332 | if( DEF_type1 == POKETYPE_HIKOU
 3333 | || DEF_type2 == POKETYPE_HIKOU ){
 3334 | SCORE += -10;
 3335 | return;
 3336 | }
 3337 | if( DEF_Tokusei == TOKUSEI_HUYUU ){
 3338 | if( ATK_Tokusei != TOKUSEI_KATAYABURI
 3339 | && ATK_Tokusei != TOKUSEI_TAABOBUREIZU
 3340 | && ATK_Tokusei != TOKUSEI_TERABORUTEEZI){
 3341 | SCORE += -10;
 3342 | return;
 3343 | }
 3344 | }
 3345 | if( DEF_type1 == POKETYPE_KUSA
 3346 | || DEF_type1 == POKETYPE_MUSHI ){
 3347 | SCORE += -1;
 3348 | }
 3349 | else if( DEF_type1 == POKETYPE_HONOO
 3350 | || DEF_type1 == POKETYPE_DENKI
 3351 | || DEF_type1 == POKETYPE_DOKU
 3352 | || DEF_type1 == POKETYPE_IWA
 3353 | || DEF_type1 == POKETYPE_HAGANE ){
 3354 | SCORE += 1;
 3355 | }
 3356 | if( AI_CMD(CMD_IF_TYPE_EX, CHECK_DEFENCE, POKETYPE_KUSA)){
 3357 | SCORE += -1;
 3358 | }
 3359 | if( DEF_type1 == DEF_type2 ){
 3360 | return;
 3361 | }
 3362 | if( DEF_type2 == POKETYPE_KUSA
 3363 | || DEF_type2 == POKETYPE_MUSHI ){
 3364 | SCORE += -1;
 3365 | }
 3366 | else if( DEF_type2 == POKETYPE_HONOO
 3367 | || DEF_type2 == POKETYPE_DENKI
 3368 | || DEF_type2 == POKETYPE_DOKU
 3369 | || DEF_type2 == POKETYPE_IWA
 3370 | || DEF_type2 == POKETYPE_HAGANE ){
 3371 | SCORE += 1;
 3372 | }
 3373 | return;
 3374 | }
 3375 | if( WazaType == POKETYPE_HIKOU ){
 3377 | if( DEF_type1 == POKETYPE_DENKI
 3378 | || DEF_type1 == POKETYPE_IWA
 3379 | || DEF_type1 == POKETYPE_HAGANE ){
 3380 | SCORE += -1;
 3381 | }
 3382 | else if( DEF_type1 == POKETYPE_KUSA
 3383 | || DEF_type1 == POKETYPE_KAKUTOU
 3384 | || DEF_type1 == POKETYPE_MUSHI ){
 3385 | SCORE += 1;
 3386 | }
 3387 | if( AI_CMD(CMD_IF_TYPE_EX, CHECK_DEFENCE, POKETYPE_KUSA)){
 3388 | SCORE += 1;
 3389 | }
 3390 | if( DEF_type1 == DEF_type2 ){
 3391 | return;
 3392 | }
 3393 | if( DEF_type2 == POKETYPE_DENKI
 3394 | || DEF_type2 == POKETYPE_IWA
 3395 | || DEF_type2 == POKETYPE_HAGANE ){
 3396 | SCORE += -1;
 3397 | }
 3398 | else if( DEF_type2 == POKETYPE_KUSA
 3399 | || DEF_type2 == POKETYPE_KAKUTOU
 3400 | || DEF_type2 == POKETYPE_MUSHI ){
 3401 | SCORE += 1;
 3402 | }
 3403 | return;
 3404 | }
 3405 | if( WazaType == POKETYPE_ESPER ){
 3407 | if( DEF_type1 == POKETYPE_AKU
 3408 | || DEF_type2 == POKETYPE_AKU ){
 3409 | SCORE += -10;
 3410 | return;
 3411 | }
 3412 | if( DEF_type1 == POKETYPE_ESPER
 3413 | || DEF_type1 == POKETYPE_HAGANE ){
 3414 | SCORE += -1;
 3415 | }
 3416 | else if( DEF_type1 == POKETYPE_KAKUTOU
 3417 | || DEF_type1 == POKETYPE_DOKU ){
 3418 | SCORE += 1;
 3419 | }
 3420 | if( DEF_type1 == DEF_type2 ){
 3421 | return;
 3422 | }
 3423 | if( DEF_type2 == POKETYPE_ESPER
 3424 | || DEF_type2 == POKETYPE_HAGANE ){
 3425 | SCORE += -1;
 3426 | }
 3427 | else if( DEF_type2 == POKETYPE_KAKUTOU
 3428 | || DEF_type2 == POKETYPE_DOKU ){
 3429 | SCORE += 1;
 3430 | }
 3431 | return;
 3432 | }
 3433 | if( WazaType == POKETYPE_MUSHI ){
 3435 | if( DEF_type1 == POKETYPE_HONOO
 3436 | || DEF_type1 == POKETYPE_KAKUTOU
 3437 | || DEF_type1 == POKETYPE_DOKU
 3438 | || DEF_type1 == POKETYPE_HIKOU
 3439 | || DEF_type1 == POKETYPE_GHOST
 3440 | || DEF_type1 == POKETYPE_HAGANE
 3441 | || DEF_type1 == POKETYPE_FAIRY ){
 3442 | SCORE += -1;
 3443 | }
 3444 | else if( DEF_type1 == POKETYPE_KUSA
 3445 | || DEF_type1 == POKETYPE_ESPER
 3446 | || DEF_type1 == POKETYPE_AKU ){
 3447 | SCORE += 1;
 3448 | }
 3449 | if( AI_CMD(CMD_IF_TYPE_EX, CHECK_DEFENCE, POKETYPE_GHOST)){
 3450 | SCORE += -1;
 3451 | }
 3452 | else if( AI_CMD(CMD_IF_TYPE_EX, CHECK_DEFENCE, POKETYPE_KUSA)){
 3453 | SCORE += 1;
 3454 | }
 3455 | if( DEF_type1 == DEF_type2 ){
 3456 | return;
 3457 | }
 3458 | if( DEF_type2 == POKETYPE_HONOO
 3459 | || DEF_type2 == POKETYPE_KAKUTOU
 3460 | || DEF_type2 == POKETYPE_DOKU
 3461 | || DEF_type2 == POKETYPE_HIKOU
 3462 | || DEF_type2 == POKETYPE_GHOST
 3463 | || DEF_type2 == POKETYPE_HAGANE
 3464 | || DEF_type2 == POKETYPE_FAIRY ){
 3465 | SCORE += -1;
 3466 | }
 3467 | else if( DEF_type2 == POKETYPE_KUSA
 3468 | || DEF_type2 == POKETYPE_ESPER
 3469 | || DEF_type2 == POKETYPE_AKU ){
 3470 | SCORE += 1;
 3471 | }
 3472 | return;
 3473 | }
 3474 | if( WazaType == POKETYPE_IWA ){
 3476 | if( DEF_type1 == POKETYPE_KAKUTOU
 3477 | || DEF_type1 == POKETYPE_JIMEN
 3478 | || DEF_type1 == POKETYPE_HAGANE ){
 3479 | SCORE += -1;
 3480 | }
 3481 | else if( DEF_type1 == POKETYPE_HONOO
 3482 | || DEF_type1 == POKETYPE_KOORI
 3483 | || DEF_type1 == POKETYPE_HIKOU
 3484 | || DEF_type1 == POKETYPE_MUSHI ){
 3485 | SCORE += 1;
 3486 | }
 3487 | if( DEF_type1 == DEF_type2 ){
 3488 | return;
 3489 | }
 3490 | if( DEF_type2 == POKETYPE_KAKUTOU
 3491 | || DEF_type2 == POKETYPE_JIMEN
 3492 | || DEF_type2 == POKETYPE_HAGANE ){
 3493 | SCORE += -1;
 3494 | }
 3495 | else if( DEF_type2 == POKETYPE_HONOO
 3496 | || DEF_type2 == POKETYPE_KOORI
 3497 | || DEF_type2 == POKETYPE_HIKOU
 3498 | || DEF_type2 == POKETYPE_MUSHI ){
 3499 | SCORE += 1;
 3500 | }
 3501 | return;
 3502 | }
 3503 | if( WazaType == POKETYPE_GHOST ){
 3505 | if( DEF_type1 == POKETYPE_NORMAL
 3506 | || DEF_type2 == POKETYPE_NORMAL ){
 3507 | SCORE += -10;
 3508 | return;
 3509 | }
 3510 | if( DEF_type1 == POKETYPE_AKU ){
 3511 | SCORE += -1;
 3512 | }
 3513 | else if( DEF_type1 == POKETYPE_GHOST
 3514 | || DEF_type1 == POKETYPE_ESPER ){
 3515 | SCORE += 1;
 3516 | }
 3517 | if( AI_CMD(CMD_IF_TYPE_EX, CHECK_DEFENCE, POKETYPE_GHOST)){
 3518 | SCORE += 1;
 3519 | }
 3520 | if( DEF_type1 == DEF_type2 ){
 3521 | return;
 3522 | }
 3523 | if( DEF_type2 == POKETYPE_AKU ){
 3524 | SCORE += -1;
 3525 | }
 3526 | else if( DEF_type2 == POKETYPE_GHOST
 3527 | || DEF_type2 == POKETYPE_ESPER ){
 3528 | SCORE += 1;
 3529 | }
 3530 | return;
 3531 | }
 3532 | if( WazaType == POKETYPE_DRAGON ){
 3534 | if( DEF_type1 == POKETYPE_FAIRY
 3535 | || DEF_type2 == POKETYPE_FAIRY ){
 3536 | SCORE += -10;
 3537 | return;
 3538 | }
 3539 | if( DEF_type1 == POKETYPE_HAGANE ){
 3540 | SCORE += -1;
 3541 | }
 3542 | else if( DEF_type1 == POKETYPE_DRAGON ){
 3543 | SCORE += 1;
 3544 | }
 3545 | if( DEF_type1 == DEF_type2 ){
 3546 | return;
 3547 | }
 3548 | if( DEF_type2 == POKETYPE_HAGANE ){
 3549 | SCORE += -1;
 3550 | }
 3551 | else if( DEF_type2 == POKETYPE_DRAGON ){
 3552 | SCORE += 1;
 3553 | }
 3554 | return;
 3555 | }
 3556 | if( WazaType == POKETYPE_AKU ){
 3558 | if( DEF_type1 == POKETYPE_KAKUTOU
 3559 | || DEF_type1 == POKETYPE_AKU
 3560 | || DEF_type1 == POKETYPE_FAIRY ){
 3561 | SCORE += -1;
 3562 | }
 3563 | else if( DEF_type1 == POKETYPE_ESPER
 3564 | || DEF_type1 == POKETYPE_GHOST ){
 3565 | SCORE += 1;
 3566 | }
 3567 | if( AI_CMD(CMD_IF_TYPE_EX, CHECK_DEFENCE, POKETYPE_GHOST)){
 3568 | SCORE += 1;
 3569 | }
 3570 | if( DEF_type1 == DEF_type2 ){
 3571 | return;
 3572 | }
 3573 | if( DEF_type2 == POKETYPE_KAKUTOU
 3574 | || DEF_type2 == POKETYPE_AKU
 3575 | || DEF_type2 == POKETYPE_FAIRY ){
 3576 | SCORE += -1;
 3577 | }
 3578 | else if( DEF_type2 == POKETYPE_ESPER
 3579 | || DEF_type2 == POKETYPE_GHOST ){
 3580 | SCORE += 1;
 3581 | }
 3582 | return;
 3583 | }
 3584 | if( WazaType == POKETYPE_HAGANE ){
 3586 | if( DEF_type1 == POKETYPE_HONOO
 3587 | || DEF_type1 == POKETYPE_MIZU
 3588 | || DEF_type1 == POKETYPE_DENKI
 3589 | || DEF_type1 == POKETYPE_HAGANE ){
 3590 | SCORE += -1;
 3591 | }
 3592 | else if( DEF_type1 == POKETYPE_KOORI
 3593 | || DEF_type1 == POKETYPE_IWA
 3594 | || DEF_type1 == POKETYPE_FAIRY ){
 3595 | SCORE += 1;
 3596 | }
 3597 | if( DEF_type1 == DEF_type2 ){
 3598 | return;
 3599 | }
 3600 | if( DEF_type2 == POKETYPE_HONOO
 3601 | || DEF_type2 == POKETYPE_MIZU
 3602 | || DEF_type2 == POKETYPE_DENKI
 3603 | || DEF_type2 == POKETYPE_HAGANE ){
 3604 | SCORE += -1;
 3605 | }
 3606 | else if( DEF_type2 == POKETYPE_KOORI
 3607 | || DEF_type2 == POKETYPE_IWA
 3608 | || DEF_type2 == POKETYPE_FAIRY ){
 3609 | SCORE += 1;
 3610 | }
 3611 | return;
 3612 | }
 3613 | if( WazaType == POKETYPE_FAIRY ){
 3615 | if( DEF_type1 == POKETYPE_HONOO
 3616 | || DEF_type1 == POKETYPE_DOKU
 3617 | || DEF_type1 == POKETYPE_HAGANE ){
 3618 | SCORE += -1;
 3619 | }
 3620 | else if( DEF_type1 == POKETYPE_KAKUTOU
 3621 | || DEF_type1 == POKETYPE_DRAGON
 3622 | || DEF_type1 == POKETYPE_AKU ){
 3623 | SCORE += 1;
 3624 | }
 3625 | if( DEF_type1 == DEF_type2 ){
 3626 | return;
 3627 | }
 3628 | if( DEF_type2 == POKETYPE_HONOO
 3629 | || DEF_type2 == POKETYPE_DOKU
 3630 | || DEF_type2 == POKETYPE_HAGANE ){
 3631 | SCORE += -1;
 3632 | }
 3633 | else if( DEF_type2 == POKETYPE_KAKUTOU
 3634 | || DEF_type2 == POKETYPE_DRAGON
 3635 | || DEF_type2 == POKETYPE_AKU ){
 3636 | SCORE += 1;
 3637 | }
 3638 | }
 3639 | }
```

### `ExpertAI_Seq_136()` (source lines 3641–3657)

```text
 3641 | ExpertAI_Seq_136()
 3642 | {
 3644 | CHK_weather = AI_CMD(CMD_CHECK_WEATHER);
 3645 | if( CHK_weather == WEATHER_HARE
 3646 | || CHK_weather == WEATHER_ARARE
 3647 | || CHK_weather == WEATHER_SUNAARASHI ){
 3649 | if( AI_CMD(CMD_IF_RND_UNDER, 200)){
 3650 | SCORE += 1;
 3651 | }
 3652 | }
 3654 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 3655 | SCORE += 1;
 3656 | }
 3657 | }
```

### `ExpertAI_Seq_137()` (source lines 3659–3675)

```text
 3659 | ExpertAI_Seq_137()
 3660 | {
 3662 | CHK_weather = AI_CMD(CMD_CHECK_WEATHER);
 3663 | if( CHK_weather == WEATHER_AME
 3664 | || CHK_weather == WEATHER_ARARE
 3665 | || CHK_weather == WEATHER_SUNAARASHI ){
 3667 | if( AI_CMD(CMD_IF_RND_UNDER, 200)){
 3668 | SCORE += 1;
 3669 | }
 3670 | }
 3672 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 3673 | SCORE += 1;
 3674 | }
 3675 | }
```

### `ExpertAI_Seq_142()` (source lines 3677–3686)

```text
 3677 | ExpertAI_Seq_142()
 3678 | {
 3680 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 90)){
 3682 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 3683 | SCORE += -2;
 3684 | }
 3685 | }
 3686 | }
```

### `ExpertAI_Seq_143()` (source lines 3688–3713)

```text
 3688 | ExpertAI_Seq_143()
 3689 | {
 3691 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_POW, 6)
 3692 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_DEF, 6)
 3693 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEPOW, 6)
 3694 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEDEF, 6)
 3695 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_AVOID, 6)
 3696 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_HIT, 6)){
 3698 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 3699 | SCORE += -2;
 3700 | }
 3701 | }
 3702 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_POW, 7)
 3703 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_DEF, 7)
 3704 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_SPEPOW, 7)
 3705 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_SPEDEF, 7)
 3706 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_AVOID, 7)
 3707 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_HIT, 7)){
 3709 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 3710 | SCORE += 1;
 3711 | }
 3712 | }
 3713 | }
```

### `ExpertAI_Seq_152()` (source lines 3764–3773)

```text
 3764 | ExpertAI_Seq_152()
 3765 | {
 3767 | if( AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_DEFENCE) == WAZANO_SORAWOTOBU ){
 3769 | if( AI_CMD(CMD_IF_RND_UNDER, 200)){
 3770 | SCORE += 2;
 3771 | }
 3772 | }
 3773 | }
```

### `ExpertAI_Seq_155()` (source lines 3775–3804)

```text
 3775 | ExpertAI_Seq_155()
 3776 | {
 3777 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_PAWAHURUHAABU)){
 3778 | ExpertAI_Seq_272()
 3779 | }
 3780 | else{
 3781 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 111)){
 3783 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 3784 | SCORE += -1;
 3785 | return;
 3786 | }
 3787 | }
 3788 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 361)){
 3790 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 3791 | SCORE += -1;
 3792 | return;
 3793 | }
 3794 | }
 3795 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 355)){
 3797 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 3798 | SCORE += -1;
 3799 | return;
 3800 | }
 3801 | }
 3802 | ExpertAI_Seq_272()
 3803 | }
 3804 | }
```

### `ExpertAI_Seq_158()` (source lines 3806–3813)

```text
 3806 | ExpertAI_Seq_158()
 3807 | {
 3810 | if( AI_CMD(CMD_IF_RND_UNDER, 230)){
 3811 | SCORE += 2;
 3812 | }
 3813 | }
```

### `ExpertAI_Seq_160()` (source lines 3815–3840)

```text
 3815 | ExpertAI_Seq_160()
 3816 | {
 3818 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 90)){
 3820 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 3821 | SCORE += 2;
 3822 | }
 3823 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 127)){
 3825 | SCORE += 2;
 3826 | }
 3827 | }
 3828 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 40)){
 3830 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 3831 | SCORE += -2;
 3832 | }
 3833 | }
 3834 | else{
 3836 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 3837 | SCORE += -1;
 3838 | }
 3839 | }
 3840 | }
```

### `ExpertAI_Seq_161()` (source lines 3842–3851)

```text
 3842 | ExpertAI_Seq_161()
 3843 | {
 3845 | if( AI_CMD(CMD_CHECK_TAKUWAERU, CHECK_ATTACK) == 3 ){
 3847 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 3848 | SCORE += 1;
 3849 | }
 3850 | }
 3851 | }
```

### `ExpertAI_Seq_164()` (source lines 3853–3869)

```text
 3853 | ExpertAI_Seq_164()
 3854 | {
 3856 | CHK_weather = AI_CMD(CMD_CHECK_WEATHER);
 3857 | if( CHK_weather == WEATHER_AME
 3858 | || CHK_weather == WEATHER_HARE
 3859 | || CHK_weather == WEATHER_SUNAARASHI ){
 3861 | if( AI_CMD(CMD_IF_RND_UNDER, 200)){
 3862 | SCORE += 1;
 3863 | }
 3864 | }
 3866 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 3867 | SCORE += 1;
 3868 | }
 3869 | }
```

### `ExpertAI_Seq_165()` (source lines 3871–3881)

```text
 3871 | ExpertAI_Seq_165()
 3872 | {
 3874 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 50)){
 3876 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 3877 | SCORE += -1;
 3878 | return;
 3879 | }
 3880 | }
 3881 | }
```

### `ExpertAI_Seq_166()` (source lines 3883–3894)

```text
 3883 | ExpertAI_Seq_166()
 3884 | {
 3886 | DefLastWazaKind = AI_CMD(CMD_CHECK_LAST_WAZA_KIND);
 3887 | if( DefLastWazaKind == WAZADATA_DMG_SPECIAL){
 3889 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 3890 | SCORE += -2;
 3891 | }
 3892 | }
 3893 | ExpertAI_Seq_049()
 3894 | }
```

### `ExpertAI_Seq_167()` (source lines 3896–3936)

```text
 3896 | ExpertAI_Seq_167()
 3897 | {
 3899 | if( AI_CMD(CMD_IFN_HAVE_DAMAGE_WAZA)){
 3901 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 3902 | SCORE += 2;
 3903 | return;
 3904 | }
 3905 | }
 3906 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_KONZYOU ){
 3908 | SCORE += -12;
 3909 | return;
 3910 | }
 3911 | Def_MonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
 3912 | if( Def_MonsNo == MONSNO_GOORIKII || Def_MonsNo == MONSNO_KAIRIKII
 3913 | || Def_MonsNo == MONSNO_RINGUMA || Def_MonsNo == MONSNO_OOSUBAME
 3914 | || Def_MonsNo == MONSNO_NAGEKI || Def_MonsNo == MONSNO_DOTEKKOTU
 3915 | || Def_MonsNo == MONSNO_ROOBUSIN || Def_MonsNo == MONSNO_RATTA
 3916 | || Def_MonsNo == MONSNO_HERAKUROSU || Def_MonsNo == MONSNO_MAKUNOSITA
 3917 | || Def_MonsNo == MONSNO_HARITEYAMA || Def_MonsNo == MONSNO_RUKUSIO
 3918 | || Def_MonsNo == MONSNO_RENTORAA){
 3920 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 3921 | SCORE += -5;
 3922 | }
 3923 | }
 3924 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 30)){
 3926 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 3927 | SCORE += -1;
 3928 | }
 3929 | }
 3930 | if( AI_CMD(CMD_CHECK_LAST_WAZA_KIND) == WAZADATA_DMG_PHYSIC ){
 3932 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 3933 | SCORE += 1;
 3934 | }
 3935 | }
 3936 | }
```

### `ExpertAI_Seq_169()` (source lines 3938–3963)

```text
 3938 | ExpertAI_Seq_169()
 3939 | {
 3941 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 3942 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 3943 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 3944 | return;
 3945 | }
 3946 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_DOKU)
 3947 | || AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_MAHI)
 3948 | || AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK, WAZASICK_YAKEDO)
 3949 | || AI_CMD(CMD_IF_DOKUDOKU, CHECK_ATTACK)){
 3950 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_2BAI)
 3951 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_4BAI)){
 3953 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 3954 | SCORE += 2;
 3955 | return;
 3956 | }
 3957 | }
 3959 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 3960 | SCORE += 2;
 3961 | }
 3962 | }
 3963 | }
```

### `ExpertAI_Seq_170()` (source lines 3965–4014)

```text
 3965 | ExpertAI_Seq_170()
 3966 | {
 3968 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 3969 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 3970 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 3971 | return;
 3972 | }
 3973 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_ATTACK)){
 3975 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 3976 | SCORE += 2;
 3977 | return;
 3978 | }
 3979 | }
 3980 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_NEMURI)
 3981 | || AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_KOORI)){
 3983 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 3984 | SCORE += 2;
 3985 | return;
 3986 | }
 3987 | }
 3988 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_MEROMERO)
 3989 | || AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_KONRAN)){
 3991 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 3992 | SCORE += 1;
 3993 | return;
 3994 | }
 3995 | }
 3996 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_MAHI)){
 3998 | if( AI_CMD(CMD_IF_RND_UNDER, 50) ){
 3999 | SCORE += 1;
 4000 | return;
 4001 | }
 4002 | }
 4003 | if( AI_CMD(CMD_CHECK_NEKODAMASI, CHECK_ATTACK) == 0 ){
 4005 | if( AI_CMD(CMD_IF_RND_UNDER, 50) ){
 4006 | SCORE += 1;
 4007 | return;
 4008 | }
 4009 | }
 4011 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 4012 | SCORE += -1;
 4013 | }
 4014 | }
```

### `ExpertAI_Seq_171()` (source lines 4016–4030)

```text
 4016 | ExpertAI_Seq_171()
 4017 | {
 4019 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 4020 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 4021 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 4022 | return;
 4023 | }
 4024 | if( AI_CMD(CMD_IF_WAZASICK, WAZASICK_MAHI)){
 4026 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 4027 | SCORE += 1;
 4028 | }
 4029 | }
 4030 | }
```

### `ExpertAI_Seq_173()` (source lines 4032–4046)

```text
 4032 | ExpertAI_Seq_173()
 4033 | {
 4035 | WazaType = POKETYPE_NORMAL
 4036 | if( AI_CMD(CMD_IF_EXIST_GROUND, BTL_GROUND_MIST)){
 4037 | WazaType = POKETYPE_FAIRY
 4038 | }
 4039 | if( AI_CMD(CMD_IF_EXIST_GROUND, BTL_GROUND_GRASS)){
 4040 | WazaType = POKETYPE_KUSA
 4041 | }
 4042 | if( AI_CMD(CMD_IF_EXIST_GROUND, BTL_GROUND_ELEKI)){
 4043 | WazaType = POKETYPE_DENKI
 4044 | }
 4045 | ExpertAI_TypeCheck( WazaType )
 4046 | }
```

### `ExpertAI_Seq_175()` (source lines 4048–4074)

```text
 4048 | ExpertAI_Seq_175()
 4049 | {
 4051 | DefMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
 4052 | if( ExpertAI_Seq_HenkaWazaPokemon() == 1 ){
 4054 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 4055 | SCORE += 1;
 4056 | }
 4057 | }
 4058 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 30)){
 4060 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 4061 | SCORE += -2;
 4062 | }
 4063 | }
 4064 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 50)){
 4066 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 4067 | SCORE += -1;
 4068 | }
 4069 | }
 4071 | if( AI_CMD(CMD_IF_RND_UNDER, 100)){
 4072 | SCORE += 1;
 4073 | }
 4074 | }
```

### `ExpertAI_Seq_HenkaWazaPokemon()` (source lines 4076–4119)

```text
 4076 | ExpertAI_Seq_HenkaWazaPokemon()
 4077 | {
 4078 | DefMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
 4079 | if( DefMonsNo == MONSNO_PARASEKUTO || DefMonsNo == MONSNO_RAHURESIA
 4080 | || DefMonsNo == MONSNO_KIREIHANA || DefMonsNo == MONSNO_PERUSIAN
 4081 | || DefMonsNo == MONSNO_UTUBOTTO || DefMonsNo == MONSNO_YADORAN
 4082 | || DefMonsNo == MONSNO_YADOKINGU || DefMonsNo == MONSNO_ZYUGON
 4083 | || DefMonsNo == MONSNO_SURIIPAA || DefMonsNo == MONSNO_RAKKII
 4084 | || DefMonsNo == MONSNO_HAPINASU || DefMonsNo == MONSNO_BARIYAADO
 4085 | || DefMonsNo == MONSNO_BURAKKII || DefMonsNo == MONSNO_TOGETIKKU
 4086 | || DefMonsNo == MONSNO_TOGEKISSU || DefMonsNo == MONSNO_WATAKKO
 4087 | || DefMonsNo == MONSNO_NUOO || DefMonsNo == MONSNO_YAMIKARASU
 4088 | || DefMonsNo == MONSNO_MUUMA || DefMonsNo == MONSNO_MUUMAAZI
 4089 | || DefMonsNo == MONSNO_SOONANSU || DefMonsNo == MONSNO_FORETOSU
 4090 | || DefMonsNo == MONSNO_TUBOTUBO || DefMonsNo == MONSNO_DOOBURU
 4091 | || DefMonsNo == MONSNO_KINOGASSA || DefMonsNo == MONSNO_YAMIRAMI
 4092 | || DefMonsNo == MONSNO_KOKODORA || DefMonsNo == MONSNO_KODORA
 4093 | || DefMonsNo == MONSNO_BUUPIGGU || DefMonsNo == MONSNO_PATTIIRU
 4094 | || DefMonsNo == MONSNO_YUREIDORU || DefMonsNo == MONSNO_KAKUREON
 4095 | || DefMonsNo == MONSNO_ZYUPETTA || DefMonsNo == MONSNO_SAMAYOORU
 4096 | || DefMonsNo == MONSNO_YONOWAARU || DefMonsNo == MONSNO_HUWARAIDO
 4097 | || DefMonsNo == MONSNO_DOOTAKUN || DefMonsNo == MONSNO_MIKARUGE
 4098 | || DefMonsNo == MONSNO_KURESERIA || DefMonsNo == MONSNO_DAAKURAI
 4099 | || DefMonsNo == MONSNO_REPARUDASU || DefMonsNo == MONSNO_MUSYAANA
 4100 | || DefMonsNo == MONSNO_ERUHUUN || DefMonsNo == MONSNO_DOREDHIA
 4101 | || DefMonsNo == MONSNO_DESUKAAN || DefMonsNo == MONSNO_GOTIRUZERU
 4102 | || DefMonsNo == MONSNO_RANKURUSU || DefMonsNo == MONSNO_MOROBARERU
 4103 | || DefMonsNo == MONSNO_BURUNGERU || DefMonsNo == MONSNO_MAMANBOU
 4104 | || DefMonsNo == MONSNO_NATTOREI || DefMonsNo == MONSNO_OOBEMU
 4105 | || DefMonsNo == MONSNO_BORUTOROSU || DefMonsNo == MONSNO_TORUNEROSU
 4106 | || DefMonsNo == MONSNO_TORIMIAN || DefMonsNo == MONSNO_OOROTTO
 4107 | || DefMonsNo == MONSNO_BIBIYON || DefMonsNo == MONSNO_DORAMIDORO
 4108 | || DefMonsNo == MONSNO_HURAETTE || DefMonsNo == MONSNO_HURAAJESU
 4109 | || DefMonsNo == MONSNO_GEKKOUGA || DefMonsNo == MONSNO_KARAMANERO
 4110 | || DefMonsNo == MONSNO_NYAONIKUSU || DefMonsNo == MONSNO_PANPUZIN
 4111 | || DefMonsNo == MONSNO_BORUTOROSU || DefMonsNo == MONSNO_AMARURUGA
 4112 | || DefMonsNo == MONSNO_PERORIIMU || DefMonsNo == MONSNO_GIRUGARUDO
 4113 | || DefMonsNo == MONSNO_GAMENODESU || DefMonsNo == MONSNO_KUREHFI
 4114 | || DefMonsNo == MONSNO_HUREHUWAN || DefMonsNo == MONSNO_TORUNEROSU
 4115 | || DefMonsNo == MONSNO_DHIANSII || DefMonsNo == MONSNO_TORUNEROSU ){
 4116 | return 1;
 4117 | }
 4118 | return 0;
 4119 | }
```

### `ExpertAI_Seq_177()` (source lines 4121–4212)

```text
 4121 | ExpertAI_Seq_177()
 4122 | {
 4124 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_KODAWARISUKAAHU)
 4125 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_KODAWARIHATIMAKI)
 4126 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_KODAWARIMEGANE)
 4127 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_KAENDAMA)
 4128 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_DOKUDOKUDAMA)
 4129 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, ITEM_KOUKOUNOSIPPO)){
 4131 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 4132 | SCORE += -2;
 4133 | return;
 4134 | }
 4135 | }
 4136 | if( ExpertAI_Seq_MegaShinkaPokemon() == 1 ){
 4138 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 4139 | SCORE += -5;
 4140 | return;
 4141 | }
 4142 | SCORE += -1;
 4143 | return;
 4144 | }
 4145 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KODAWARISUKAAHU)
 4146 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KODAWARIHATIMAKI)
 4147 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KODAWARIMEGANE)){
 4148 | if( ExpertAI_Seq_HenkaWazaPokemon() == 1 ){
 4150 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 4151 | SCORE += 2;
 4152 | return;
 4153 | }
 4154 | }
 4155 | if ( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK, WAZANO_KANASIBARI)){
 4157 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 4158 | SCORE += 2;
 4159 | return;
 4160 | }
 4161 | }
 4162 | }
 4163 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KAENDAMA)){
 4164 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) != TOKUSEI_KONZYOU ){
 4165 | if( AI_CMD(CMD_CHECK_LAST_WAZA_KIND) == WAZADATA_DMG_PHYSIC){
 4167 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 4168 | SCORE += 2;
 4169 | return;
 4170 | }
 4171 | }
 4172 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) != TOKUSEI_MAZIKKUGAADO ){
 4174 | if( AI_CMD(CMD_IF_RND_UNDER, 160) ){
 4175 | SCORE += 2;
 4176 | return;
 4177 | }
 4178 | }
 4179 | }
 4180 | }
 4181 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KOUKOUNOSIPPO)){
 4183 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 4184 | SCORE += 2;
 4185 | return;
 4186 | }
 4187 | }
 4188 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_DOKUDOKUDAMA)){
 4189 | if( AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) != POKETYPE_DOKU
 4190 | && AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) != POKETYPE_DOKU
 4191 | && AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) != TOKUSEI_MAZIKKUGAADO
 4192 | && AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) != TOKUSEI_KONZYOU
 4193 | && AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) != TOKUSEI_POIZUNHIIRU ){
 4195 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 4196 | SCORE += 2;
 4197 | return;
 4198 | }
 4199 | }
 4200 | }
 4201 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KOUKOUNOSIPPO)){
 4203 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 4204 | SCORE += 2;
 4205 | return;
 4206 | }
 4207 | }
 4209 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 4210 | SCORE += -1;
 4211 | }
 4212 | }
```

### `ExpertAI_Seq_MegaShinkaPokemon()` (source lines 4214–4235)

```text
 4214 | ExpertAI_Seq_MegaShinkaPokemon()
 4215 | {
 4216 | DefMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
 4217 | if( DefMonsNo == MONSNO_GENGAA || DefMonsNo == MONSNO_SAANAITO
 4218 | || DefMonsNo == MONSNO_DENRYUU || DefMonsNo == MONSNO_HUSIGIBANA
 4219 | || DefMonsNo == MONSNO_RIZAADON || DefMonsNo == MONSNO_KAMEKKUSU
 4220 | || DefMonsNo == MONSNO_MYUUTUU || DefMonsNo == MONSNO_BASYAAMO
 4221 | || DefMonsNo == MONSNO_TYAAREMU || DefMonsNo == MONSNO_HERUGAA
 4222 | || DefMonsNo == MONSNO_BOSUGODORA || DefMonsNo == MONSNO_ZYUPETTA
 4223 | || DefMonsNo == MONSNO_BANGIRASU || DefMonsNo == MONSNO_HASSAMU
 4224 | || DefMonsNo == MONSNO_KAIROSU || DefMonsNo == MONSNO_PUTERA
 4225 | || DefMonsNo == MONSNO_RUKARIO || DefMonsNo == MONSNO_YUKINOOO
 4226 | || DefMonsNo == MONSNO_RIZAADON || DefMonsNo == MONSNO_GARUURA
 4227 | || DefMonsNo == MONSNO_GYARADOSU || DefMonsNo == MONSNO_ABUSORU
 4228 | || DefMonsNo == MONSNO_HUUDHIN || DefMonsNo == MONSNO_HERAKUROSU
 4229 | || DefMonsNo == MONSNO_KUTIITO || DefMonsNo == MONSNO_RAIBORUTO
 4230 | || DefMonsNo == MONSNO_GABURIASU || DefMonsNo == MONSNO_RATHIOSU
 4231 | || DefMonsNo == MONSNO_RATHIASU ){
 4232 | return 1;
 4233 | }
 4234 | return 0;
 4235 | }
```

### `ExpertAI_Seq_178()` (source lines 4238–4255)

```text
 4238 | ExpertAI_Seq_178()
 4239 | {
 4241 | if( ExpertAI_Seq_CopyPokemonTokusei() == 1){
 4243 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 4244 | SCORE += 1;
 4245 | return;
 4246 | }
 4247 | }
 4248 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) != TOKUSEI_IKAKU ){
 4250 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 4251 | SCORE += 1;
 4252 | return;
 4253 | }
 4254 | }
 4255 | }
```

### `ExpertAI_Seq_CopyPokemonTokusei()` (source lines 4257–4293)

```text
 4257 | ExpertAI_Seq_CopyPokemonTokusei()
 4258 | {
 4259 | DefMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
 4260 | if( DefMonsNo == MONSNO_DAGUTORIO || DefMonsNo == MONSNO_PERUSIAN
 4261 | || DefMonsNo == MONSNO_GORUDAKKU || DefMonsNo == MONSNO_KINGUDORA
 4262 | || DefMonsNo == MONSNO_EREKIBURU || DefMonsNo == MONSNO_RAPURASU
 4263 | || DefMonsNo == MONSNO_SYAWAAZU || DefMonsNo == MONSNO_SANDAASU
 4264 | || DefMonsNo == MONSNO_OMUSUTAA || DefMonsNo == MONSNO_KABUTOPUSU
 4265 | || DefMonsNo == MONSNO_RANTAAN || DefMonsNo == MONSNO_MARIRURI
 4266 | || DefMonsNo == MONSNO_KIMAWARI || DefMonsNo == MONSNO_NUOO
 4267 | || DefMonsNo == MONSNO_YAMIKARASU || DefMonsNo == MONSNO_SOONANSU
 4268 | || DefMonsNo == MONSNO_HARIISEN || DefMonsNo == MONSNO_MANTAIN
 4269 | || DefMonsNo == MONSNO_HERUGAA || DefMonsNo == MONSNO_ENTEI
 4270 | || DefMonsNo == MONSNO_RAIKOU || DefMonsNo == MONSNO_SUIKUN
 4271 | || DefMonsNo == MONSNO_RUNPAPPA || DefMonsNo == MONSNO_DAATENGU
 4272 | || DefMonsNo == MONSNO_BAKUONGU || DefMonsNo == MONSNO_YAMIRAMI
 4273 | || DefMonsNo == MONSNO_RAIBORUTO || DefMonsNo == MONSNO_PURASURU
 4274 | || DefMonsNo == MONSNO_MAINAN || DefMonsNo == MONSNO_HURAIGON
 4275 | || DefMonsNo == MONSNO_HANTEERU || DefMonsNo == MONSNO_SAKURABISU
 4276 | || DefMonsNo == MONSNO_ZIIRANSU || DefMonsNo == MONSNO_HUROOZERU
 4277 | || DefMonsNo == MONSNO_THERIMU || DefMonsNo == MONSNO_TORITODON
 4278 | || DefMonsNo == MONSNO_GUREGGURU || DefMonsNo == MONSNO_HIIDORAN
 4279 | || DefMonsNo == MONSNO_REPARUDASU || DefMonsNo == MONSNO_KOKOROMORI
 4280 | || DefMonsNo == MONSNO_DORYUUZU || DefMonsNo == MONSNO_MUURANDO
 4281 | || DefMonsNo == MONSNO_GAMAGEROGE || DefMonsNo == MONSNO_DOREDHIA
 4282 | || DefMonsNo == MONSNO_ERUHUUN || DefMonsNo == MONSNO_GOTIRUZERU
 4283 | || DefMonsNo == MONSNO_RANKURUSU || DefMonsNo == MONSNO_MEBUKIZIKA
 4284 | || DefMonsNo == MONSNO_BURUNGERU || DefMonsNo == MONSNO_GIGIGIARU
 4285 | || DefMonsNo == MONSNO_SYANDERA || DefMonsNo == MONSNO_URUGAMOSU
 4286 | || DefMonsNo == MONSNO_BORUTOROSU || DefMonsNo == MONSNO_TORUNEROSU
 4287 | || DefMonsNo == MONSNO_MAFOKUSII || DefMonsNo == MONSNO_GOOGOOTO
 4288 | || DefMonsNo == MONSNO_EREZAADO || DefMonsNo == MONSNO_NYAONIKUSU
 4289 | || DefMonsNo == MONSNO_TORIMIAN || DefMonsNo == MONSNO_BORUKENION ){
 4290 | return 1;
 4291 | }
 4292 | return 0;
 4293 | }
```

### `ExpertAI_Seq_183()` (source lines 4295–4305)

```text
 4295 | ExpertAI_Seq_183()
 4296 | {
 4298 | DefMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
 4299 | if( ExpertAI_Seq_ReturnWazaPokemon() == 1 ){
 4301 | if( AI_CMD(CMD_IF_RND_UNDER, 50) ){
 4302 | SCORE += 1;
 4303 | }
 4304 | }
 4305 | }
```

### `ExpertAI_Seq_ReturnWazaPokemon()` (source lines 4308–4333)

```text
 4308 | ExpertAI_Seq_ReturnWazaPokemon()
 4309 | {
 4310 | DefMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
 4311 | if( DefMonsNo == MONSNO_PERUSIAN || DefMonsNo == MONSNO_BURAKKII
 4312 | || DefMonsNo == MONSNO_NUOO || DefMonsNo == MONSNO_YAMIKARASU
 4313 | || DefMonsNo == MONSNO_MUUMA || DefMonsNo == MONSNO_MUUMAAZI
 4314 | || DefMonsNo == MONSNO_FORETOSU || DefMonsNo == MONSNO_TUBOTUBO
 4315 | || DefMonsNo == MONSNO_DOOBURU || DefMonsNo == MONSNO_YAMIRAMI
 4316 | || DefMonsNo == MONSNO_SAMAYOORU || DefMonsNo == MONSNO_YONOWAARU
 4317 | || DefMonsNo == MONSNO_DOOTAKUN || DefMonsNo == MONSNO_MIKARUGE
 4318 | || DefMonsNo == MONSNO_KURESERIA || DefMonsNo == MONSNO_DAAKURAI
 4319 | || DefMonsNo == MONSNO_REPARUDASU || DefMonsNo == MONSNO_MUSYAANA
 4320 | || DefMonsNo == MONSNO_ERUHUUN || DefMonsNo == MONSNO_DESUKAAN
 4321 | || DefMonsNo == MONSNO_GOTIRUZERU || DefMonsNo == MONSNO_RANKURUSU
 4322 | || DefMonsNo == MONSNO_MAMANBOU || DefMonsNo == MONSNO_OOBEMU
 4323 | || DefMonsNo == MONSNO_BORUTOROSU || DefMonsNo == MONSNO_TORUNEROSU
 4324 | || DefMonsNo == MONSNO_TORIMIAN || DefMonsNo == MONSNO_OOROTTO
 4325 | || DefMonsNo == MONSNO_KARAMANERO || DefMonsNo == MONSNO_NYAONIKUSU
 4326 | || DefMonsNo == MONSNO_PANPUZIN || DefMonsNo == MONSNO_PERORIIMU
 4327 | || DefMonsNo == MONSNO_GAMENODESU || DefMonsNo == MONSNO_KUREHFI
 4328 | || DefMonsNo == MONSNO_HUREHUWAN || DefMonsNo == MONSNO_DHIANSII
 4329 | || DefMonsNo == MONSNO_MERESII ){
 4330 | return 1;
 4331 | }
 4332 | return 0;
 4333 | }
```

### `ExpertAI_Seq_184()` (source lines 4335–4342)

```text
 4335 | ExpertAI_Seq_184()
 4336 | {
 4339 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 4340 | SCORE += 1;
 4341 | }
 4342 | }
```

### `ExpertAI_Seq_185()` (source lines 4344–4369)

```text
 4344 | ExpertAI_Seq_185()
 4345 | {
 4347 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_NEMURI)){
 4349 | if( AI_CMD(CMD_IF_RND_UNDER, 200)){
 4350 | SCORE += -2;
 4351 | }
 4352 | }
 4353 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_MEROMERO)){
 4355 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 4356 | SCORE += -1;
 4357 | }
 4358 | }
 4359 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_KONRAN)){
 4361 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 4362 | SCORE += -1;
 4363 | }
 4364 | }
 4366 | if( AI_CMD(CMD_IF_RND_UNDER, 80)){
 4367 | SCORE += 1;
 4368 | }
 4369 | }
```

### `ExpertAI_Seq_186()` (source lines 4371–4386)

```text
 4371 | ExpertAI_Seq_186()
 4372 | {
 4374 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_DEFENCE, BTL_SIDEEFF_REFRECTOR)){
 4376 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 4377 | SCORE += 1;
 4378 | }
 4379 | }
 4380 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_DEFENCE, BTL_SIDEEFF_HIKARINOKABE)){
 4382 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 4383 | SCORE += 1;
 4384 | }
 4385 | }
 4386 | }
```

### `ExpertAI_Seq_187()` (source lines 4388–4396)

```text
 4388 | ExpertAI_Seq_187()
 4389 | {
 4392 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 4393 | SCORE += 1;
 4394 | }
 4395 | ExpertAI_Seq_001();
 4396 | }
```

### `ExpertAI_Seq_188()` (source lines 4398–4434)

```text
 4398 | ExpertAI_Seq_188()
 4399 | {
 4401 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_SYUUKAKU ){
 4403 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 4404 | return;
 4405 | }
 4406 | }
 4407 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_DEFENCE, 0)){
 4409 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 4410 | SCORE += -1;
 4411 | return;
 4412 | }
 4413 | }
 4414 | else{
 4416 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 4417 | SCORE += 1;
 4418 | return;
 4419 | }
 4420 | }
 4421 | if( ExpertAI_Seq_GoodItemPokemon() == 1 ){
 4423 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 4424 | SCORE += 1;
 4425 | }
 4426 | }
 4427 | if( AI_CMD(CMD_CHECK_NEKODAMASI, CHECK_ATTACK) == 0 ){
 4429 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 4430 | SCORE += 1;
 4431 | return;
 4432 | }
 4433 | }
 4434 | }
```

### `ExpertAI_Seq_190()` (source lines 4436–4478)

```text
 4436 | ExpertAI_Seq_190()
 4437 | {
 4439 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 4440 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 4441 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 4442 | return;
 4443 | }
 4444 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)){
 4445 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 90)){
 4447 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 4448 | SCORE += 2;
 4449 | }
 4450 | }
 4451 | else if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 60)){
 4453 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 4454 | SCORE += 1;
 4455 | }
 4456 | }
 4457 | else{
 4459 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 4460 | SCORE += -2;
 4461 | }
 4462 | }
 4463 | }
 4464 | else if( AI_CMD(CMD_IF_FIRST, IF_FIRST_DEFENCE)){
 4465 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 80)){
 4467 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 4468 | SCORE += -2;
 4469 | }
 4470 | }
 4471 | else{
 4473 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 4474 | SCORE += -3;
 4475 | }
 4476 | }
 4477 | }
 4478 | }
```

### `ExpertAI_Seq_191()` (source lines 4480–4514)

```text
 4480 | ExpertAI_Seq_191()
 4481 | {
 4483 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 4484 | if( CHK_rule == BTL_RULE_SINGLE
 4485 | || CHK_rule == BTL_RULE_ROTATION ){
 4486 | if( AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_ATTACK) == WAZANO_SUKIRUSUWAPPU ){
 4488 | SCORE += -2;
 4489 | }
 4490 | }
 4491 | if( AI_CMD(CMD_CHECK_NEKODAMASI, CHECK_ATTACK) != 0 ){
 4493 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 4494 | SCORE += -1;
 4495 | return;
 4496 | }
 4497 | }
 4498 | if( ExpertAI_Seq_ErasePokemonTokusei() == 1){
 4499 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_DEFENCE, 50)){
 4501 | if( AI_CMD(CMD_IF_RND_UNDER, CHECK_DEFENCE, 180)){
 4502 | SCORE += 1;
 4503 | return;
 4504 | }
 4505 | }
 4506 | }
 4507 | if( ExpertAI_Seq_CopyPokemonTokusei() == 1){
 4509 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 4510 | SCORE += 1;
 4511 | return;
 4512 | }
 4513 | }
 4514 | }
```

### `ExpertAI_Seq_ErasePokemonTokusei()` (source lines 4516–4537)

```text
 4516 | ExpertAI_Seq_ErasePokemonTokusei()
 4517 | {
 4518 | DefMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
 4519 | if( DefMonsNo == MONSNO_DAGUTORIO || DefMonsNo == MONSNO_KAIRIKII
 4520 | || DefMonsNo == MONSNO_HASSAMU || DefMonsNo == MONSNO_KABUTOPUSU
 4521 | || DefMonsNo == MONSNO_MARIRURI || DefMonsNo == MONSNO_SOONANSU
 4522 | || DefMonsNo == MONSNO_HERAKUROSU || DefMonsNo == MONSNO_RINGUMA
 4523 | || DefMonsNo == MONSNO_KINOGASSA || DefMonsNo == MONSNO_NUKENIN
 4524 | || DefMonsNo == MONSNO_HARITEYAMA || DefMonsNo == MONSNO_YAMIRAMI
 4525 | || DefMonsNo == MONSNO_TYAAREMU || DefMonsNo == MONSNO_DOOTAKUN
 4526 | || DefMonsNo == MONSNO_ROOBUSIN || DefMonsNo == MONSNO_NAGEKI
 4527 | || DefMonsNo == MONSNO_ERUHUUN || DefMonsNo == MONSNO_GOTIRUZERU
 4528 | || DefMonsNo == MONSNO_RANKURUSU || DefMonsNo == MONSNO_BORUTOROSU
 4529 | || DefMonsNo == MONSNO_TORUNEROSU || DefMonsNo == MONSNO_HORUUDO
 4530 | || DefMonsNo == MONSNO_GOOGOOTO || DefMonsNo == MONSNO_NYAONIKUSU
 4531 | || DefMonsNo == MONSNO_KAMEKKUSU || DefMonsNo == MONSNO_ZYUPETTA
 4532 | || DefMonsNo == MONSNO_KUREHFI || DefMonsNo == MONSNO_GARUURA
 4533 | || DefMonsNo == MONSNO_KUTIITO || DefMonsNo == MONSNO_GARUURA ){
 4534 | return 1;
 4535 | }
 4536 | return 0;
 4537 | }
```

### `ExpertAI_Seq_192()` (source lines 4539–4549)

```text
 4539 | ExpertAI_Seq_192()
 4540 | {
 4542 | if( AI_CMD(CMD_CHECK_NEKODAMASI, CHECK_ATTACK) == 0 ){
 4544 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 4545 | SCORE += 1;
 4546 | return;
 4547 | }
 4548 | }
 4549 | }
```

### `ExpertAI_Seq_196()` (source lines 4559–4614)

```text
 4559 | ExpertAI_Seq_196()
 4560 | {
 4562 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 4563 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 4564 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 4565 | return;
 4566 | }
 4567 | Weight = AI_CMD(CMD_GET_WEIGHT, CHECK_DEFENCE);
 4568 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_2BAI)
 4569 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_4BAI)){
 4570 | if( Weight >= 800 ){
 4572 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 4573 | SCORE += 2;
 4574 | }
 4575 | return;
 4576 | }
 4577 | }
 4578 | if( Weight >= 2000 ){
 4580 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 4581 | SCORE += 2;
 4582 | }
 4583 | return;
 4584 | }
 4585 | if( Weight >= 1000 ){
 4587 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 4588 | SCORE += 2;
 4589 | }
 4590 | return;
 4591 | }
 4592 | if( Weight >= 800 ){
 4594 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 4595 | SCORE += 1;
 4596 | return;
 4597 | }
 4598 | return;
 4599 | }
 4600 | if( Weight < 250 ){
 4602 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 4603 | SCORE += -1;
 4604 | return;
 4605 | }
 4606 | }
 4607 | if( Weight < 100 ){
 4609 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 4610 | SCORE += -1;
 4611 | return;
 4612 | }
 4613 | }
 4614 | }
```

### `ExpertAI_Seq_203()` (source lines 4644–4661)

```text
 4644 | ExpertAI_Seq_203()
 4645 | {
 4646 | CHK_weather = AI_CMD(CMD_CHECK_WEATHER);
 4647 | WazaType = POKETYPE_NORMAL
 4648 | if( CHK_weather == WEATHER_HARE ){
 4649 | WazaType = POKETYPE_HONOO
 4650 | }
 4651 | else if( CHK_weather == WEATHER_AME ){
 4652 | WazaType = POKETYPE_MIZU
 4653 | }
 4654 | else if( CHK_weather == WEATHER_SUNAARASHI ){
 4655 | WazaType = POKETYPE_IWA
 4656 | }
 4657 | else if( CHK_weather == WEATHER_ARARE ){
 4658 | WazaType = POKETYPE_KOORI
 4659 | }
 4660 | ExpertAI_TypeCheck( WazaType )
 4661 | }
```

### `ExpertAI_Seq_210()` (source lines 4675–4693)

```text
 4675 | ExpertAI_Seq_210()
 4676 | {
 4678 | DEF_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1);
 4679 | DEF_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2);
 4680 | if( DEF_type1 == POKETYPE_HONOO
 4681 | || DEF_type2 == POKETYPE_HONOO ){
 4683 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 4684 | SCORE += 2;
 4685 | }
 4686 | }
 4687 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 50)){
 4689 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 4690 | SCORE += -1;
 4691 | }
 4692 | }
 4693 | }
```

### `ExpertAI_Seq_212()` (source lines 4695–4716)

```text
 4695 | ExpertAI_Seq_212()
 4696 | {
 4698 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_DEFENCE)){
 4700 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 4701 | SCORE += 2;
 4702 | }
 4703 | return;
 4704 | }
 4705 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 50)){
 4707 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 4708 | SCORE += -1;
 4709 | return;
 4710 | }
 4711 | }
 4713 | if( AI_CMD(CMD_IF_RND_UNDER, 80)){
 4714 | SCORE += 1;
 4715 | }
 4716 | }
```

### `ExpertAI_Seq_215()` (source lines 4718–4735)

```text
 4718 | ExpertAI_Seq_215()
 4719 | {
 4721 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 4722 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_HUYUU
 4723 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) == POKETYPE_HIKOU
 4724 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) == POKETYPE_HIKOU ){
 4726 | if( AI_CMD(CMD_IF_RND_UNDER, 180)){
 4727 | SCORE += 1;
 4728 | }
 4729 | }
 4730 | }
 4732 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 4733 | SCORE += 1;
 4734 | }
 4735 | }
```

### `ExpertAI_Seq_218()` (source lines 4747–4767)

```text
 4747 | ExpertAI_Seq_218()
 4748 | {
 4750 | if( AI_CMD(CMD_FLDEFF_CHECK, EFF_TRICKROOM)){
 4751 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)){
 4753 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 4754 | SCORE += 2;
 4755 | }
 4756 | }
 4757 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 4758 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 4759 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 4760 | return;
 4761 | }
 4763 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 4764 | SCORE += 1;
 4765 | }
 4766 | }
 4767 | }
```

### `ExpertAI_Seq_219()` (source lines 4769–4796)

```text
 4769 | ExpertAI_Seq_219()
 4770 | {
 4772 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 4773 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 4774 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 4775 | SCORE += -1;
 4776 | return;
 4777 | }
 4778 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)){
 4780 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 4781 | SCORE += -2;
 4782 | }
 4783 | return;
 4784 | }
 4785 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_AGI, 6)){
 4787 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 4788 | SCORE += 2;
 4789 | return;
 4790 | }
 4791 | }
 4793 | if( AI_CMD(CMD_IF_RND_UNDER, 80) ){
 4794 | SCORE += 1;
 4795 | }
 4796 | }
```

### `ExpertAI_Seq_220()` (source lines 4798–4815)

```text
 4798 | ExpertAI_Seq_220()
 4799 | {
 4801 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 30)){
 4803 | if( AI_CMD(CMD_IF_RND_UNDER, 100)){
 4804 | SCORE += 2;
 4805 | return;
 4806 | }
 4807 | }
 4808 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 50)){
 4810 | if( AI_CMD(CMD_IF_RND_UNDER, 50)){
 4811 | SCORE += 2;
 4812 | return;
 4813 | }
 4814 | }
 4815 | }
```

### `ExpertAI_Seq_221()` (source lines 4817–4840)

```text
 4817 | ExpertAI_Seq_221()
 4818 | {
 4820 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 4821 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 4822 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 4823 | SCORE += -1;
 4824 | return;
 4825 | }
 4826 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 50)){
 4828 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 4829 | SCORE += 2;
 4830 | return;
 4831 | }
 4832 | }
 4833 | else{
 4835 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 4836 | SCORE += -1;
 4837 | return;
 4838 | }
 4839 | }
 4840 | }
```

### `ExpertAI_Seq_222()` (source lines 4842–4950)

```text
 4842 | ExpertAI_Seq_222()
 4843 | {
 4845 | WazaType = POKETYPE_NORMAL
 4846 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_IANOMI)
 4847 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_NOWAKINOMI)
 4848 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_NAMONOMI)
 4849 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_RENBUNOMI)
 4850 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_TARAPUNOMI)){
 4851 | WazaType = POKETYPE_AKU
 4852 | }
 4853 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_UINOMI)
 4854 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_GOSUNOMI)
 4855 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_YOROGINOMI)
 4856 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_MIKURUNOMI)){
 4857 | WazaType = POKETYPE_IWA
 4858 | }
 4859 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_SUTAANOMI)
 4860 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_OBONNOMI)
 4861 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_UTANNOMI)
 4862 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_MATOMANOMI)){
 4863 | WazaType = POKETYPE_ESPER
 4864 | }
 4865 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KAMURANOMI)
 4866 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_HIMERINOMI)
 4867 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_NEKOBUNOMI)
 4868 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_YOPUNOMI)){
 4869 | WazaType = POKETYPE_KAKUTOU
 4870 | }
 4871 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_TIIRANOMI)
 4872 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_TIIGONOMI)
 4873 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_PAIRUNOMI)
 4874 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_RINDONOMI)){
 4875 | WazaType = POKETYPE_KUSA
 4876 | }
 4877 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_IBANNOMI)
 4878 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_MAGONOMI)
 4879 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_RABUTANOMI)
 4880 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KASIBUNOMI)){
 4881 | WazaType = POKETYPE_GHOST
 4882 | }
 4883 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_RYUGANOMI)
 4884 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_NANASINOMI)
 4885 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_ZAROKUNOMI)
 4886 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_YATHENOMI) ){
 4887 | WazaType = POKETYPE_KOORI
 4888 | }
 4889 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_ZUANOMI)
 4890 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KIINOMI)
 4891 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_ROMENOMI)
 4892 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_SYUKANOMI)){
 4893 | WazaType = POKETYPE_JIMEN
 4894 | }
 4895 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_MOMONNOMI)
 4896 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_SESINANOMI)
 4897 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_BERIBUNOMI)
 4898 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_SOKUNONOMI)){
 4899 | WazaType = POKETYPE_DENKI
 4900 | }
 4901 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_ORENNOMI)
 4902 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_TAPORUNOMI)
 4903 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_BIAANOMI)
 4904 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_YATAPINOMI)){
 4905 | WazaType = POKETYPE_DOKU
 4906 | }
 4907 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_BANZINOMI)
 4908 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_NOMERUNOMI)
 4909 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_HABANNOMI)
 4910 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_ZYAPONOMI)){
 4911 | WazaType = POKETYPE_DRAGON
 4912 | }
 4913 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_HOZUNOMI)){
 4914 | WazaType = POKETYPE_NORMAL
 4915 | }
 4916 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_ZURINOMI)
 4917 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_SIIYANOMI)
 4918 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_RIRIBANOMI)){
 4919 | WazaType = POKETYPE_HAGANE
 4920 | }
 4921 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_RAMUNOMI)
 4922 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_UBUNOMI)
 4923 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_BAKOUNOMI)
 4924 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_SANNOMI)){
 4925 | WazaType = POKETYPE_HIKOU
 4926 | }
 4927 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KURABONOMI)
 4928 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_BURIINOMI)
 4929 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KAISUNOMI)
 4930 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_OKKANOMI)){
 4931 | WazaType = POKETYPE_HONOO
 4932 | }
 4933 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KAGONOMI)
 4934 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_NANANOMI)
 4935 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_DORINOMI)
 4936 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_ITOKENOMI)){
 4937 | WazaType = POKETYPE_MIZU
 4938 | }
 4939 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_FIRANOMI)
 4940 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_MOKOSINOMI)
 4941 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_TANGANOMI)
 4942 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_NAZONOMI)){
 4943 | WazaType = POKETYPE_MUSHI
 4944 | }
 4945 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_ROZERUNOMI)
 4946 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_AKKINOMI)){
 4947 | WazaType = POKETYPE_FAIRY
 4948 | }
 4949 | ExpertAI_TypeCheck( WazaType )
 4950 | }
```

### `ExpertAI_Seq_227()` (source lines 5012–5051)

```text
 5012 | ExpertAI_Seq_227()
 5013 | {
 5015 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_NEMURI)
 5016 | || AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_KOORI)){
 5018 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 5019 | SCORE += -3;
 5020 | }
 5021 | }
 5022 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_MEROMERO)
 5023 | || AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_KONRAN)){
 5025 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 5026 | SCORE += -1;
 5027 | }
 5028 | }
 5029 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_MAHI)){
 5031 | if( AI_CMD(CMD_IF_RND_UNDER, 50) ){
 5032 | SCORE += -1;
 5033 | }
 5034 | }
 5035 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 30)){
 5037 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 5038 | SCORE += -2;
 5039 | }
 5040 | }
 5041 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 50)){
 5043 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 5044 | SCORE += -1;
 5045 | }
 5046 | }
 5048 | if( AI_CMD(CMD_IF_RND_UNDER, 100)){
 5049 | SCORE += 2;
 5050 | }
 5051 | }
```

### `ExpertAI_Seq_228()` (source lines 5053–5073)

```text
 5053 | ExpertAI_Seq_228()
 5054 | {
 5056 | if( ExpertAI_Seq_228_sub() == 1 ){
 5058 | SCORE += -3;
 5059 | return;
 5060 | }
 5061 | if( AI_CMD(CMD_CHECK_BENCH_COUNT, CHECK_ATTACK) == 0 ){
 5063 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 5064 | SCORE += -1;
 5065 | }
 5066 | }
 5067 | else if( AI_CMD(CMD_IF_BENCH_DAMAGE_MAX, LOSS_CALC_OFF)){
 5069 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 5070 | SCORE += 1;
 5071 | }
 5072 | }
 5073 | }
```

### `ExpertAI_Seq_228_sub()` (source lines 5075–5097)

```text
 5075 | ExpertAI_Seq_228_sub()
 5076 | {
 5077 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1BAI)){
 5078 | return 0;
 5079 | }
 5080 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_2BAI)){
 5081 | return 0;
 5082 | }
 5083 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_4BAI)){
 5084 | return 0;
 5085 | }
 5086 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)){
 5087 | return 1;
 5088 | }
 5089 | if( AI_CMD(CMD_IF_HAVE_BATSUGUN, CHECK_ATTACK, CHECK_DEFENCE)){
 5090 | return 1;
 5091 | }
 5093 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 5094 | SCORE += -1;
 5095 | }
 5096 | return 0;
 5097 | }
```

### `ExpertAI_Seq_229()` (source lines 5099–5110)

```text
 5099 | ExpertAI_Seq_229()
 5100 | {
 5102 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 80)){
 5103 | if( AI_CMD(CMD_CHECK_BENCH_COUNT, CHECK_DEFENCE) == 0 ){
 5105 | if( AI_CMD(CMD_IF_RND_UNDER, CHECK_DEFENCE, 128)){
 5106 | SCORE += -1;
 5107 | }
 5108 | }
 5109 | }
 5110 | }
```

### `ExpertAI_Seq_230()` (source lines 5112–5137)

```text
 5112 | ExpertAI_Seq_230()
 5113 | {
 5115 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 5116 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 5117 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 5118 | return;
 5119 | }
 5120 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)){
 5121 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) != TOKUSEI_TEKUNISYAN ){
 5122 | return;
 5123 | }
 5124 | }
 5125 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_2BAI)
 5126 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_4BAI)){
 5128 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 5129 | SCORE += 3;
 5130 | return;
 5131 | }
 5132 | }
 5134 | if( AI_CMD(CMD_IF_RND_UNDER, 80) ){
 5135 | SCORE += 2;
 5136 | }
 5137 | }
```

### `ExpertAI_Seq_233()` (source lines 5139–5187)

```text
 5139 | ExpertAI_Seq_233()
 5140 | {
 5142 | Atk_SoubiEquip = AI_CMD(CMD_CHECK_SOUBI_EQUIP, CHECK_ATTACK)
 5143 | Def_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 5144 | Atk_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 5145 | if( Atk_SoubiEquip == SOUBI_HIRUMASERU ){
 5146 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)){
 5147 | if( Def_Tokusei != TOKUSEI_HUKUTUNOKOKORO
 5148 | && Def_Tokusei != TOKUSEI_SEISINRYOKU
 5149 | && Def_Tokusei != TOKUSEI_ITAZURAGOKORO ){
 5151 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 5152 | SCORE += 2;
 5153 | return;
 5154 | }
 5155 | }
 5156 | }
 5157 | }
 5158 | if( Atk_SoubiEquip == SOUBI_DOKUBARIUP
 5159 | || Atk_SoubiEquip == SOUBI_TEKINIMOTASERUTOMOUDOKU ){
 5160 | ExpertAI_Seq_033()
 5161 | return;
 5162 | }
 5163 | if( Atk_SoubiEquip == SOUBI_TTEKINIMOTASERUTOYAKEDO ){
 5164 | ExpertAI_Seq_167()
 5165 | return;
 5166 | }
 5167 | if( Atk_SoubiEquip == SOUBI_PIKATYUUTOKUKOUNIBAI){
 5168 | ExpertAI_Seq_067()
 5169 | return;
 5170 | }
 5171 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 5172 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 5173 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 5175 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 5176 | SCORE += -2;
 5177 | }
 5178 | return;
 5179 | }
 5180 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_2BAI)
 5181 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_4BAI)){
 5183 | if( AI_CMD(CMD_IF_RND_UNDER, 160) ){
 5184 | SCORE += 2;
 5185 | }
 5186 | }
 5187 | }
```

### `ExpertAI_Seq_237()` (source lines 5189–5225)

```text
 5189 | ExpertAI_Seq_237()
 5190 | {
 5192 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 5193 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 5194 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 5195 | SCORE += -1;
 5196 | return;
 5197 | }
 5198 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_DEFENCE, 80)){
 5199 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_2BAI)
 5200 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_4BAI)){
 5202 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 5203 | SCORE += 2;
 5204 | }
 5205 | return;
 5206 | }
 5208 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 5209 | SCORE += 1;
 5210 | }
 5211 | }
 5212 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 30)){
 5214 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 5215 | SCORE += -2;
 5216 | return;
 5217 | }
 5218 | }
 5219 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 50)){
 5221 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 5222 | SCORE += -1;
 5223 | }
 5224 | }
 5225 | }
```

### `ExpertAI_Seq_239()` (source lines 5227–5288)

```text
 5227 | ExpertAI_Seq_239()
 5228 | {
 5230 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 30)){
 5232 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 5233 | SCORE += -3;
 5234 | return;
 5235 | }
 5236 | }
 5237 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 50)){
 5239 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 5240 | SCORE += -1;
 5241 | }
 5242 | }
 5243 | DefTokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE);
 5244 | if(DefTokusei == TOKUSEI_KAGEHUMI
 5245 | || DefTokusei == TOKUSEI_HUSIGINAMAMORI
 5246 | || DefTokusei == TOKUSEI_TIKARAMOTI
 5247 | || DefTokusei == TOKUSEI_KONZYOU
 5248 | || DefTokusei == TOKUSEI_POIZUNHIIRU
 5249 | || DefTokusei == TOKUSEI_MAZIKKUGAADO
 5250 | || DefTokusei == TOKUSEI_NOOGAADO
 5251 | || DefTokusei == TOKUSEI_TEKUNISYAN ){
 5253 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 5254 | SCORE += 2;
 5255 | return;
 5256 | }
 5257 | }
 5258 | if( ExpertAI_Seq_ErasePokemonTokusei() == 1){
 5260 | if( AI_CMD(CMD_IF_RND_UNDER, CHECK_DEFENCE, 180)){
 5261 | SCORE += 1;
 5262 | return;
 5263 | }
 5264 | }
 5265 | if(DefTokusei == TOKUSEI_KASOKU
 5266 | || DefTokusei == TOKUSEI_TENNOMEGUMI
 5267 | || DefTokusei == TOKUSEI_SUISUI
 5268 | || DefTokusei == TOKUSEI_YOURYOKUSO
 5269 | || DefTokusei == TOKUSEI_HURAWAAGIHUTO
 5270 | || DefTokusei == TOKUSEI_MAZIKKUMIRAA
 5271 | || DefTokusei == TOKUSEI_ITAZURAGOKORO
 5272 | || DefTokusei == TOKUSEI_FAAKOOTO
 5273 | || DefTokusei == TOKUSEI_HAYATENOTUBASA
 5274 | || DefTokusei == TOKUSEI_MEGARANTYAA
 5275 | || DefTokusei == TOKUSEI_KATAITUME
 5276 | || DefTokusei == TOKUSEI_OYAKOAI
 5277 | || DefTokusei == TOKUSEI_DAAKUOORA
 5278 | || DefTokusei == TOKUSEI_FEARIIOORA ){
 5280 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 5281 | SCORE += 1;
 5282 | return;
 5283 | }
 5284 | }
 5285 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 5286 | SCORE += -1;
 5287 | }
 5288 | }
```

### `ExpertAI_Seq_240()` (source lines 5290–5293)

```text
 5290 | ExpertAI_Seq_240()
 5291 | {
 5293 | }
```

### `ExpertAI_Seq_241()` (source lines 5295–5377)

```text
 5295 | ExpertAI_Seq_241()
 5296 | {
 5298 | Atk_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE1);
 5299 | Atk_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE2);
 5300 | Def_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1);
 5301 | Def_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2);
 5302 | Def_LastWaza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_DEFENCE);
 5303 | if( Def_LastWaza == WAZANO_GEKIRIN ){
 5304 | if(Def_type1 != POKETYPE_HAGANE
 5305 | || Def_type2 != POKETYPE_HAGANE
 5306 | || Def_type1 != POKETYPE_FAIRY
 5307 | || Def_type2 != POKETYPE_FAIRY){
 5309 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 5310 | SCORE += 2;
 5311 | return;
 5312 | }
 5313 | }
 5314 | }
 5315 | if( Def_type1 == POKETYPE_DRAGON
 5316 | || Def_type2 == POKETYPE_DRAGON){
 5317 | if(Def_type1 != POKETYPE_HAGANE
 5318 | || Def_type2 != POKETYPE_HAGANE
 5319 | || Def_type1 != POKETYPE_FAIRY
 5320 | || Def_type2 != POKETYPE_FAIRY
 5321 | || Atk_type1 != POKETYPE_HAGANE
 5322 | || Atk_type2 != POKETYPE_HAGANE
 5323 | || Atk_type1 != POKETYPE_FAIRY
 5324 | || Atk_type2 != POKETYPE_FAIRY){
 5325 | if(Atk_type1 == POKETYPE_DRAGON
 5326 | || Atk_type2 == POKETYPE_DRAGON){
 5328 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 5329 | SCORE += 2;
 5330 | return;
 5331 | }
 5332 | }
 5334 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 5335 | SCORE += 2;
 5336 | return;
 5337 | }
 5338 | }
 5339 | }
 5340 | if( Def_type1 == POKETYPE_GHOST
 5341 | || Def_type2 == POKETYPE_GHOST){
 5342 | if(Def_type1 != POKETYPE_NORMAL
 5343 | || Def_type2 != POKETYPE_NORMAL
 5344 | || Def_type1 != POKETYPE_AKU
 5345 | || Def_type2 != POKETYPE_AKU
 5346 | || Atk_type1 != POKETYPE_NORMAL
 5347 | || Atk_type2 != POKETYPE_NORMAL
 5348 | || Atk_type1 != POKETYPE_AKU
 5349 | || Atk_type2 != POKETYPE_AKU){
 5350 | if(Atk_type1 == POKETYPE_GHOST
 5351 | || Atk_type2 == POKETYPE_GHOST
 5352 | || Atk_type1 != POKETYPE_ESPER
 5353 | || Atk_type2 != POKETYPE_ESPER){
 5355 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 5356 | SCORE += 2;
 5357 | return;
 5358 | }
 5359 | }
 5361 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 5362 | SCORE += 2;
 5363 | return;
 5364 | }
 5365 | }
 5366 | }
 5367 | if( Def_type1 != Atk_type1
 5368 | || Def_type2 != Atk_type2
 5369 | || Def_type2 != Atk_type1
 5370 | || Def_type1 != Atk_type2){
 5372 | if( AI_CMD(CMD_IF_RND_UNDER, 60) ){
 5373 | SCORE += 1;
 5374 | return;
 5375 | }
 5376 | }
 5377 | }
```

### `ExpertAI_Seq_242()` (source lines 5379–5382)

```text
 5379 | ExpertAI_Seq_242()
 5380 | {
 5382 | }
```

### `ExpertAI_Seq_243()` (source lines 5384–5387)

```text
 5384 | ExpertAI_Seq_243()
 5385 | {
 5387 | }
```

### `ExpertAI_Seq_244()` (source lines 5389–5392)

```text
 5389 | ExpertAI_Seq_244()
 5390 | {
 5392 | }
```

### `ExpertAI_Seq_245()` (source lines 5394–5450)

```text
 5394 | ExpertAI_Seq_245()
 5395 | {
 5397 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)){
 5398 | SCORE += -1;
 5399 | return;
 5400 | }
 5401 | AssistCount = 0 ;
 5402 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_POW, 6)){
 5403 | AssistCount = AssistCount + AI_CMD(CMD_CHECK_STATUS, CHECK_DEFENCE, PARA_POW) - 6;
 5404 | }
 5405 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_DEF, 6)){
 5406 | AssistCount = AssistCount + AI_CMD(CMD_CHECK_STATUS, CHECK_DEFENCE, PARA_DEF) - 6;
 5407 | }
 5408 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_SPEPOW, 6)){
 5409 | AssistCount = AssistCount + AI_CMD(CMD_CHECK_STATUS, CHECK_DEFENCE, PARA_SPEPOW) - 6;
 5410 | }
 5411 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_SPEDEF, 6)){
 5412 | AssistCount = AssistCount + AI_CMD(CMD_CHECK_STATUS, CHECK_DEFENCE, PARA_SPEDEF) - 6;
 5413 | }
 5414 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_AGI, 6)){
 5415 | AssistCount = AssistCount + AI_CMD(CMD_CHECK_STATUS, CHECK_DEFENCE, PARA_AGI) - 6;
 5416 | }
 5417 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_HIT, 6)){
 5418 | AssistCount = AssistCount + AI_CMD(CMD_CHECK_STATUS, CHECK_DEFENCE, PARA_HIT) - 6;
 5419 | }
 5420 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_AVOID, 6)){
 5421 | AssistCount = AssistCount + AI_CMD(CMD_CHECK_STATUS, CHECK_DEFENCE, PARA_AVOID) - 6;
 5422 | }
 5423 | if( AssistCount > 5 ){
 5424 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)){
 5425 | return;
 5426 | }
 5428 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 5429 | SCORE += 3;
 5430 | }
 5431 | return;
 5432 | }
 5433 | if( AssistCount > 1 ){
 5434 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)
 5435 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)){
 5436 | return;
 5437 | }
 5439 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 5440 | SCORE += 2;
 5441 | }
 5442 | return;
 5443 | }
 5444 | if( AssistCount < 1 ){
 5446 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 5447 | SCORE += -1;
 5448 | }
 5449 | }
 5450 | }
```

### `ExpertAI_Seq_246()` (source lines 5452–5455)

```text
 5452 | ExpertAI_Seq_246()
 5453 | {
 5455 | }
```

### `ExpertAI_Seq_247()` (source lines 5457–5460)

```text
 5457 | ExpertAI_Seq_247()
 5458 | {
 5460 | }
```

### `ExpertAI_Seq_248()` (source lines 5462–5478)

```text
 5462 | ExpertAI_Seq_248()
 5463 | {
 5465 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 5466 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 5467 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 5468 | return;
 5469 | }
 5470 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_DEFENCE)){
 5471 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 50)){
 5473 | if( AI_CMD(CMD_IF_RND_UNDER, 150) ){
 5474 | SCORE += 1;
 5475 | }
 5476 | }
 5477 | }
 5478 | }
```

### `ExpertAI_Seq_249()` (source lines 5480–5487)

```text
 5480 | ExpertAI_Seq_249()
 5481 | {
 5484 | if( AI_CMD(CMD_IF_RND_UNDER, 100)){
 5485 | SCORE += 2;
 5486 | }
 5487 | }
```

### `ExpertAI_Seq_250()` (source lines 5489–5492)

```text
 5489 | ExpertAI_Seq_250()
 5490 | {
 5492 | }
```

### `ExpertAI_Seq_251()` (source lines 5494–5497)

```text
 5494 | ExpertAI_Seq_251()
 5495 | {
 5497 | }
```

### `ExpertAI_Seq_252()` (source lines 5499–5502)

```text
 5499 | ExpertAI_Seq_252()
 5500 | {
 5502 | }
```

### `ExpertAI_Seq_258()` (source lines 5504–5507)

```text
 5504 | ExpertAI_Seq_258()
 5505 | {
 5507 | }
```

### `ExpertAI_Seq_259()` (source lines 5509–5526)

```text
 5509 | ExpertAI_Seq_259()
 5510 | {
 5512 | if( AI_CMD(CMD_CHECK_BTL_RULE) == BTL_RULE_DOUBLE
 5513 | || AI_CMD(CMD_CHECK_BTL_RULE) == BTL_RULE_TRIPLE ){
 5514 | return;
 5515 | }
 5516 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_DEFENCE)){
 5518 | if( AI_CMD(CMD_IF_RND_UNDER, 220)){
 5519 | SCORE += 2;
 5520 | }
 5521 | }
 5522 | else{
 5524 | SCORE += -5;
 5525 | }
 5526 | }
```

### `ExpertAI_Seq_265()` (source lines 5528–5531)

```text
 5528 | ExpertAI_Seq_265()
 5529 | {
 5531 | }
```

### `ExpertAI_Seq_266()` (source lines 5533–5540)

```text
 5533 | ExpertAI_Seq_266()
 5534 | {
 5537 | if( AI_CMD(CMD_IF_RND_UNDER, 100)){
 5538 | SCORE += 2;
 5539 | }
 5540 | }
```

### `ExpertAI_Seq_268()` (source lines 5542–5615)

```text
 5542 | ExpertAI_Seq_268()
 5543 | {
 5545 | WazaType = POKETYPE_NORMAL
 5546 | AtkMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_ATTACK);
 5547 | if( AtkMonsNo == MONSNO_ARUSEUSU ){
 5548 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KOWAMOTEPUREETO)){
 5549 | WazaType = POKETYPE_AKU
 5550 | }
 5551 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_GANSEKIPUREETO)){
 5552 | WazaType = POKETYPE_IWA
 5553 | }
 5554 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_HUSIGINOPUREETO)){
 5555 | WazaType = POKETYPE_ESPER
 5556 | }
 5557 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KOBUSINOPUREETO)){
 5558 | WazaType = POKETYPE_KAKUTOU
 5559 | }
 5560 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_MIDORINOPUREETO)){
 5561 | WazaType = POKETYPE_KUSA
 5562 | }
 5563 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_MONONOKEPUREETO)){
 5564 | WazaType = POKETYPE_GHOST
 5565 | }
 5566 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_TURARANOPUREETO)){
 5567 | WazaType = POKETYPE_KOORI
 5568 | }
 5569 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_DAITINOPUREETO)){
 5570 | WazaType = POKETYPE_JIMEN
 5571 | }
 5572 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_IKAZUTIPUREETO)){
 5573 | WazaType = POKETYPE_DENKI
 5574 | }
 5575 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_MOUDOKUPUREETO)){
 5576 | WazaType = POKETYPE_DOKU
 5577 | }
 5578 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_RYUUNOPUREETO)){
 5579 | WazaType = POKETYPE_DRAGON
 5580 | }
 5581 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KOUTETUPUREETO)){
 5582 | WazaType = POKETYPE_HAGANE
 5583 | }
 5584 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_AOZORAPUREETO)){
 5585 | WazaType = POKETYPE_HIKOU
 5586 | }
 5587 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_HINOTAMAPUREETO)){
 5588 | WazaType = POKETYPE_HONOO
 5589 | }
 5590 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_SIZUKUPUREETO)){
 5591 | WazaType = POKETYPE_MIZU
 5592 | }
 5593 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_TAMAMUSIPUREETO)){
 5594 | WazaType = POKETYPE_MUSHI
 5595 | }
 5596 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_SEIREIPUREETO)){
 5597 | WazaType = POKETYPE_FAIRY
 5598 | }
 5599 | }
 5600 | else if( AtkMonsNo == MONSNO_GENOSEKUTO ){
 5601 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_HURIIZUKASETTO)){
 5602 | WazaType = POKETYPE_KOORI
 5603 | }
 5604 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_INAZUMAKASETTO)){
 5605 | WazaType = POKETYPE_DENKI
 5606 | }
 5607 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_BUREIZUKASETTO)){
 5608 | WazaType = POKETYPE_HONOO
 5609 | }
 5610 | else if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_AKUAKASETTO)){
 5611 | WazaType = POKETYPE_MIZU
 5612 | }
 5613 | }
 5614 | ExpertAI_TypeCheck( WazaType )
 5615 | }
```

### `ExpertAI_Seq_270()` (source lines 5617–5634)

```text
 5617 | ExpertAI_Seq_270()
 5618 | {
 5620 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 30)){
 5622 | if( AI_CMD(CMD_IF_RND_UNDER, 100)){
 5623 | SCORE += 2;
 5624 | return;
 5625 | }
 5626 | }
 5627 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 50)){
 5629 | if( AI_CMD(CMD_IF_RND_UNDER, 50)){
 5630 | SCORE += 2;
 5631 | return;
 5632 | }
 5633 | }
 5634 | }
```

### `ExpertAI_Seq_272()` (source lines 5636–5678)

```text
 5636 | ExpertAI_Seq_272()
 5637 | {
 5639 | ChkDefDoku = ExpertAI_Seq_016_sub4();
 5640 | if( ChkDefDoku == 1 ){
 5641 | if( ExpertAI_Seq_016_sub2() == 0 ){
 5642 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) != TOKUSEI_MAZIKKUGAADO ){
 5644 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 5645 | SCORE += 1;
 5646 | }
 5647 | }
 5648 | }
 5649 | }
 5650 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)){
 5651 | ChkDefLastWaza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_DEFENCE);
 5652 | if( ChkDefLastWaza == WAZANO_ROKKUON
 5653 | || ChkDefLastWaza == WAZANO_KOKORONOME){
 5655 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 5656 | SCORE += 1;
 5657 | }
 5658 | }
 5659 | }
 5660 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)){
 5662 | return;
 5663 | }
 5664 | else if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)){
 5666 | return;
 5667 | }
 5668 | else if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 5670 | return;
 5671 | }
 5672 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_PAWAHURUHAABU)){
 5674 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 5675 | SCORE += 1;
 5676 | }
 5677 | }
 5678 | }
```

### `ExpertAI_Seq_278()` (source lines 5680–5684)

```text
 5680 | ExpertAI_Seq_278()
 5681 | {
 5684 | }
```

### `ExpertAI_Seq_279()` (source lines 5686–5690)

```text
 5686 | ExpertAI_Seq_279()
 5687 | {
 5690 | }
```

### `ExpertAI_Seq_280()` (source lines 5692–5696)

```text
 5692 | ExpertAI_Seq_280()
 5693 | {
 5696 | }
```

### `ExpertAI_Seq_283()` (source lines 5707–5720)

```text
 5707 | ExpertAI_Seq_283()
 5708 | {
 5710 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 5711 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 5712 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 5713 | return;
 5714 | }
 5715 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_DOKU)
 5716 | || AI_CMD(CMD_IF_DOKUDOKU, CHECK_DEFENCE)){
 5718 | SCORE += 1;
 5719 | }
 5720 | }
```

### `ExpertAI_Seq_284()` (source lines 5722–5732)

```text
 5722 | ExpertAI_Seq_284()
 5723 | {
 5725 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 196)){
 5727 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 5728 | SCORE += 1;
 5729 | }
 5730 | }
 5731 | ExpertAI_Seq_012()
 5732 | }
```

### `ExpertAI_Seq_285()` (source lines 5734–5737)

```text
 5734 | ExpertAI_Seq_285()
 5735 | {
 5737 | }
```

### `ExpertAI_Seq_286()` (source lines 5739–5746)

```text
 5739 | ExpertAI_Seq_286()
 5740 | {
 5743 | if( AI_CMD(CMD_IF_RND_UNDER, 150)){
 5744 | SCORE += 2;
 5745 | }
 5746 | }
```

### `ExpertAI_Seq_287()` (source lines 5748–5751)

```text
 5748 | ExpertAI_Seq_287()
 5749 | {
 5751 | }
```

### `ExpertAI_Seq_288()` (source lines 5753–5779)

```text
 5753 | ExpertAI_Seq_288()
 5754 | {
 5756 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 5757 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 5758 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 5759 | return;
 5760 | }
 5761 | if( CURRENT_MOVE() == WAZANO_YAMAARASI ){
 5762 | if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_ATTACK, PARA_POW, 6)
 5763 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_DEF, 6)){
 5765 | if( AI_CMD(CMD_IF_RND_UNDER, 200)){
 5766 | SCORE += 2;
 5767 | }
 5768 | }
 5769 | }
 5770 | else if( CURRENT_MOVE()== WAZANO_KOORINOIBUKI ){
 5771 | if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_ATTACK, PARA_SPEPOW, 6)
 5772 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_SPEDEF, 6)){
 5774 | if( AI_CMD(CMD_IF_RND_UNDER, 200)){
 5775 | SCORE += 2;
 5776 | }
 5777 | }
 5778 | }
 5779 | }
```

### `ExpertAI_Seq_289()` (source lines 5781–5784)

```text
 5781 | ExpertAI_Seq_289()
 5782 | {
 5784 | }
```

### `ExpertAI_Seq_290()` (source lines 5786–5807)

```text
 5786 | ExpertAI_Seq_290()
 5787 | {
 5789 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_DEFENCE)){
 5791 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 5792 | SCORE += 2;
 5793 | }
 5794 | return;
 5795 | }
 5796 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 50)){
 5798 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 5799 | SCORE += -1;
 5800 | return;
 5801 | }
 5802 | }
 5804 | if( AI_CMD(CMD_IF_RND_UNDER, 80)){
 5805 | SCORE += 1;
 5806 | }
 5807 | }
```

### `ExpertAI_Seq_291()` (source lines 5809–5855)

```text
 5809 | ExpertAI_Seq_291()
 5810 | {
 5812 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 5813 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 5814 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 5815 | return;
 5816 | }
 5817 | WeightDiff = AI_CMD(CMD_GET_WEIGHT, CHECK_ATTACK) / AI_CMD(CMD_GET_WEIGHT, CHECK_DEFENCE)
 5818 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_HEVHIMETARU ){
 5819 | WeightDiff = WeightDiff / 2
 5820 | }
 5821 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_HEVHIMETARU ){
 5822 | WeightDiff = WeightDiff * 2
 5823 | }
 5824 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_2BAI)
 5825 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_4BAI)){
 5826 | if( WeightDiff >= 3 ){
 5828 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 5829 | SCORE += 2;
 5830 | }
 5831 | }
 5832 | return;
 5833 | }
 5834 | if( WeightDiff >= 5 ){
 5836 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 5837 | SCORE += 1;
 5838 | }
 5839 | return;
 5840 | }
 5841 | if( WeightDiff >= 4 ){
 5843 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 5844 | SCORE += 1;
 5845 | }
 5846 | return;
 5847 | }
 5848 | if( WeightDiff < 2 ){
 5850 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 5851 | SCORE += -1;
 5852 | }
 5853 | return;
 5854 | }
 5855 | }
```

### `ExpertAI_Seq_292()` (source lines 5857–5860)

```text
 5857 | ExpertAI_Seq_292()
 5858 | {
 5860 | }
```

### `ExpertAI_Seq_293()` (source lines 5862–5897)

```text
 5862 | ExpertAI_Seq_293()
 5863 | {
 5865 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 5866 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 5867 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 5868 | SCORE += -1;
 5869 | return;
 5870 | }
 5871 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_DEFENCE)){
 5873 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 5874 | SCORE += -3;
 5875 | }
 5876 | return;
 5877 | }
 5878 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_AGI, 6)){
 5880 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 5881 | SCORE += -2;
 5882 | }
 5883 | return;
 5884 | }
 5885 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_AGI, 7)){
 5887 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 5888 | SCORE += 2;
 5889 | return;
 5890 | }
 5891 | }
 5893 | if( AI_CMD(CMD_IF_RND_UNDER, 80) ){
 5894 | SCORE += 2;
 5895 | return;
 5896 | }
 5897 | }
```

### `ExpertAI_Seq_294()` (source lines 5899–5902)

```text
 5899 | ExpertAI_Seq_294()
 5900 | {
 5902 | }
```

### `ExpertAI_Seq_295()` (source lines 5904–5915)

```text
 5904 | ExpertAI_Seq_295()
 5905 | {
 5907 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)){
 5909 | return;
 5910 | }
 5912 | if( AI_CMD(CMD_IF_RND_UNDER, 220)){
 5913 | SCORE += 2;
 5914 | }
 5915 | }
```

### `ExpertAI_Seq_296()` (source lines 5917–5932)

```text
 5917 | ExpertAI_Seq_296()
 5918 | {
 5920 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_SPEDEF, 3)){
 5922 | if( AI_CMD(CMD_IF_RND_UNDER, 240)){
 5923 | SCORE += -2;
 5924 | }
 5925 | }
 5926 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_SPEDEF, 5)){
 5928 | if( AI_CMD(CMD_IF_RND_UNDER, 180)){
 5929 | SCORE += -1;
 5930 | }
 5931 | }
 5932 | }
```

### `ExpertAI_Seq_297()` (source lines 5934–5975)

```text
 5934 | ExpertAI_Seq_297()
 5935 | {
 5937 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 5938 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 5939 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 5941 | if( AI_CMD(CMD_IF_RND_UNDER, 180)){
 5942 | SCORE += -1;
 5943 | }
 5944 | return;
 5945 | }
 5946 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_POW, 8)){
 5948 | if( AI_CMD(CMD_IF_RND_UNDER, 220)){
 5949 | SCORE += 2;
 5950 | return;
 5951 | }
 5952 | }
 5953 | else if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_POW, 6)){
 5954 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_2BAI)
 5955 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_4BAI)){
 5957 | if( AI_CMD(CMD_IF_RND_UNDER, 220)){
 5958 | SCORE += 2;
 5959 | return;
 5960 | }
 5961 | }
 5963 | if( AI_CMD(CMD_IF_RND_UNDER, 180)){
 5964 | SCORE += 2;
 5965 | return;
 5966 | }
 5967 | }
 5968 | if( AI_CMD(CMD_CHECK_LAST_WAZA_KIND) == WAZADATA_DMG_PHYSIC){
 5970 | if( AI_CMD(CMD_IF_RND_UNDER, 80)){
 5971 | SCORE += 2;
 5972 | return;
 5973 | }
 5974 | }
 5975 | }
```

### `ExpertAI_Seq_298()` (source lines 5977–5980)

```text
 5977 | ExpertAI_Seq_298()
 5978 | {
 5980 | }
```

### `ExpertAI_Seq_299()` (source lines 5982–5985)

```text
 5982 | ExpertAI_Seq_299()
 5983 | {
 5985 | }
```

### `ExpertAI_Seq_300()` (source lines 5987–5990)

```text
 5987 | ExpertAI_Seq_300()
 5988 | {
 5990 | }
```

### `ExpertAI_Seq_301()` (source lines 5992–5995)

```text
 5992 | ExpertAI_Seq_301()
 5993 | {
 5995 | }
```

### `ExpertAI_Seq_302()` (source lines 5997–6000)

```text
 5997 | ExpertAI_Seq_302()
 5998 | {
 6000 | }
```

### `ExpertAI_Seq_303()` (source lines 6002–6029)

```text
 6002 | ExpertAI_Seq_303()
 6003 | {
 6005 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)){
 6007 | return;
 6008 | }
 6009 | else if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)){
 6011 | return;
 6012 | }
 6013 | else if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 6015 | return;
 6016 | }
 6017 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_DEF, 7)){
 6019 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 6020 | SCORE += 1;
 6021 | }
 6022 | }
 6023 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_AVOID, 7)){
 6025 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 6026 | SCORE += 1;
 6027 | }
 6028 | }
 6029 | }
```

### `ExpertAI_Seq_304()` (source lines 6031–6058)

```text
 6031 | ExpertAI_Seq_304()
 6032 | {
 6034 | if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_POW, 6)
 6035 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_DEF, 6)
 6036 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_SPEPOW, 6)
 6037 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_SPEDEF, 6)
 6038 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_AGI, 6)
 6039 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_HIT, 6)
 6040 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_AVOID, 6)){
 6042 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 6043 | SCORE += -1;
 6044 | }
 6045 | }
 6046 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_POW, 7)
 6047 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_DEF, 7)
 6048 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_SPEPOW, 7)
 6049 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_SPEDEF, 7)
 6050 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_AGI, 6)
 6051 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_HIT, 7)
 6052 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_AVOID, 7)){
 6054 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 6055 | SCORE += 2;
 6056 | }
 6057 | }
 6058 | }
```

### `ExpertAI_Seq_305()` (source lines 6061–6124)

```text
 6061 | ExpertAI_Seq_305()
 6062 | {
 6064 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)){
 6065 | return;
 6066 | }
 6067 | AssistCount = 0 ;
 6068 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_POW, 6)){
 6069 | AssistCount = AssistCount + AI_CMD(CMD_CHECK_STATUS, CHECK_ATTACK, PARA_POW) - 6;
 6071 | }
 6072 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_DEF, 6)){
 6073 | AssistCount = AssistCount + AI_CMD(CMD_CHECK_STATUS, CHECK_ATTACK, PARA_DEF) - 6;
 6075 | }
 6076 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEPOW, 6)){
 6077 | AssistCount = AssistCount + AI_CMD(CMD_CHECK_STATUS, CHECK_ATTACK, PARA_SPEPOW) - 6;
 6078 | }
 6079 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEDEF, 6)){
 6080 | AssistCount = AssistCount + AI_CMD(CMD_CHECK_STATUS, CHECK_ATTACK, PARA_SPEDEF) - 6;
 6081 | }
 6082 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_AGI, 6)){
 6083 | AssistCount = AssistCount + AI_CMD(CMD_CHECK_STATUS, CHECK_ATTACK, PARA_AGI) - 6;
 6084 | }
 6085 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_HIT, 6)){
 6086 | AssistCount = AssistCount + AI_CMD(CMD_CHECK_STATUS, CHECK_ATTACK, PARA_HIT) - 6;
 6087 | }
 6088 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_AVOID, 6)){
 6089 | AssistCount = AssistCount + AI_CMD(CMD_CHECK_STATUS, CHECK_ATTACK, PARA_AVOID) - 6;
 6090 | }
 6091 | if( AssistCount > 16 ){
 6093 | if( AI_CMD(CMD_IF_RND_UNDER, 250) ){
 6094 | SCORE += 4;
 6095 | }
 6096 | return;
 6097 | }
 6098 | if( AssistCount > 8 ){
 6099 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)){
 6100 | return;
 6101 | }
 6103 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 6104 | SCORE += 3;
 6105 | }
 6106 | return;
 6107 | }
 6108 | if( AssistCount > 4 ){
 6109 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 6110 | return;
 6111 | }
 6113 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 6114 | SCORE += 2;
 6115 | }
 6116 | return;
 6117 | }
 6118 | if( AssistCount < 3 ){
 6120 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 6121 | SCORE += -1;
 6122 | }
 6123 | }
 6124 | }
```

### `ExpertAI_Seq_306()` (source lines 6126–6135)

```text
 6126 | ExpertAI_Seq_306()
 6127 | {
 6129 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 6130 | if( CHK_rule == BTL_RULE_SINGLE
 6131 | || CHK_rule == BTL_RULE_ROTATION ){
 6133 | SCORE += -5;
 6134 | }
 6135 | }
```

### `ExpertAI_Seq_308()` (source lines 6137–6154)

```text
 6137 | ExpertAI_Seq_308()
 6138 | {
 6140 | if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_ATTACK, PARA_DEF, 6)
 6141 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_ATTACK, PARA_SPEDEF, 6)){
 6143 | if( AI_CMD(CMD_IF_RND_UNDER, 250)){
 6144 | SCORE += -2;
 6145 | }
 6146 | return;
 6147 | }
 6148 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_DEFENCE)){
 6150 | if( AI_CMD(CMD_IF_RND_UNDER, 240)){
 6151 | SCORE += 2;
 6152 | }
 6153 | }
 6154 | }
```

### `ExpertAI_Seq_310()` (source lines 6156–6183)

```text
 6156 | ExpertAI_Seq_310()
 6157 | {
 6159 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 6160 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 6161 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 6162 | return;
 6163 | }
 6164 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_DOKU)
 6165 | || AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_NEMURI)
 6166 | || AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_KOORI)
 6167 | || AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_MAHI)
 6168 | || AI_CMD(CMD_IF_WAZASICK, CHECK_DEFENCE, WAZASICK_YAKEDO)
 6169 | || AI_CMD(CMD_IF_DOKUDOKU, CHECK_DEFENCE)){
 6170 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_2BAI)
 6171 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_4BAI)){
 6173 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 6174 | SCORE += 2;
 6175 | return;
 6176 | }
 6177 | }
 6179 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 6180 | SCORE += 2;
 6181 | }
 6182 | }
 6183 | }
```

### `ExpertAI_Seq_314()` (source lines 6196–6205)

```text
 6196 | ExpertAI_Seq_314()
 6197 | {
 6199 | if( AI_CMD(CMD_CHECK_TURN) == 0 ){
 6201 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 6202 | SCORE += 1;
 6203 | }
 6204 | }
 6205 | }
```

### `ExpertAI_Seq_316()` (source lines 6207–6219)

```text
 6207 | ExpertAI_Seq_316()
 6208 | {
 6210 | CHK_weather = AI_CMD(CMD_CHECK_WEATHER);
 6211 | if( AI_CMD(CMD_CHECK_WEATHER) == WEATHER_HARE ){
 6212 | ExpertAI_Seq_010()
 6213 | return
 6214 | }
 6216 | if( AI_CMD(CMD_IF_RND_UNDER, 200)){
 6217 | SCORE += -1;
 6218 | }
 6219 | }
```

### `ExpertAI_Seq_317()` (source lines 6221–6241)

```text
 6221 | ExpertAI_Seq_317()
 6222 | {
 6224 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 6225 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 6226 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 6227 | return;
 6228 | }
 6229 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_HIKOUNOZYUERU)){
 6231 | if( AI_CMD(CMD_IF_RND_UNDER, 140)){
 6232 | SCORE += 2;
 6233 | }
 6234 | }
 6235 | if( AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, 0)){
 6237 | if( AI_CMD(CMD_IF_RND_UNDER, 200)){
 6238 | SCORE += 1;
 6239 | }
 6240 | }
 6241 | }
```

### `ExpertAI_Seq_318()` (source lines 6243–6246)

```text
 6243 | ExpertAI_Seq_318()
 6244 | {
 6246 | }
```

### `ExpertAI_Seq_319()` (source lines 6248–6251)

```text
 6248 | ExpertAI_Seq_319()
 6249 | {
 6251 | }
```

### `ExpertAI_Seq_320()` (source lines 6253–6294)

```text
 6253 | ExpertAI_Seq_320()
 6254 | {
 6256 | if( AI_CMD(CMD_IF_MIGAWARI, CHECK_DEFENCE)){
 6258 | SCORE += -2;
 6259 | return;
 6260 | }
 6261 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 60)){
 6262 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_DEFENCE, 60)){
 6264 | SCORE += -2;
 6265 | return;
 6266 | }
 6267 | }
 6268 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 40)){
 6270 | SCORE += -2;
 6271 | return;
 6272 | }
 6273 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 50)){
 6274 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_DEFENCE, 50)){
 6276 | SCORE += -2;
 6277 | return;
 6278 | }
 6279 | }
 6280 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 60)){
 6281 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_DEFENCE, 60)){
 6283 | SCORE += -2;
 6284 | return;
 6285 | }
 6286 | }
 6287 | if( AI_CMD(CMD_IF_HAVE_BATSUGUN, CHECK_ATTACK, CHECK_DEFENCE)){
 6289 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 6290 | SCORE += -2;
 6291 | return;
 6292 | }
 6293 | }
 6294 | }
```

### `ExpertAI_Seq_323()` (source lines 6296–6308)

```text
 6296 | ExpertAI_Seq_323()
 6297 | {
 6299 | if( ExpertAI_Seq_MegaShinkaPokemon() == 1 ){
 6301 | if( AI_CMD(CMD_IF_RND_UNDER, 220) ){
 6302 | SCORE += -5;
 6303 | return;
 6304 | }
 6305 | SCORE += -1;
 6306 | return;
 6307 | }
 6308 | }
```

### `ExpertAI_Seq_329()` (source lines 6310–6313)

```text
 6310 | ExpertAI_Seq_329()
 6311 | {
 6313 | }
```

### `ExpertAI_Seq_334()` (source lines 6315–6318)

```text
 6315 | ExpertAI_Seq_334()
 6316 | {
 6318 | }
```

### `ExpertAI_Seq_335()` (source lines 6320–6323)

```text
 6320 | ExpertAI_Seq_335()
 6321 | {
 6323 | }
```

### `ExpertAI_Seq_336()` (source lines 6325–6328)

```text
 6325 | ExpertAI_Seq_336()
 6326 | {
 6328 | }
```

### `ExpertAI_Seq_337()` (source lines 6330–6362)

```text
 6330 | ExpertAI_Seq_337()
 6331 | {
 6333 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 6334 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 6335 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 6336 | return;
 6337 | }
 6338 | Def_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1);
 6339 | Def_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2);
 6340 | if( Def_type1 == POKETYPE_KUSA
 6341 | || Def_type2 == POKETYPE_KUSA
 6342 | || Def_type1 == POKETYPE_KAKUTOU
 6343 | || Def_type2 == POKETYPE_KAKUTOU
 6344 | || Def_type1 == POKETYPE_MUSHI
 6345 | || Def_type2 == POKETYPE_MUSHI ){
 6346 | if( Def_type1 != POKETYPE_DENKI
 6347 | && Def_type2 != POKETYPE_DENKI
 6348 | && Def_type1 != POKETYPE_IWA
 6349 | && Def_type2 != POKETYPE_IWA
 6350 | && Def_type1 != POKETYPE_HAGANE
 6351 | && Def_type2 != POKETYPE_HAGANE ){
 6353 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 6354 | SCORE += 1;
 6355 | }
 6357 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 6358 | SCORE += 1;
 6359 | }
 6360 | }
 6361 | }
 6362 | }
```

### `ExpertAI_Seq_338()` (source lines 6364–6376)

```text
 6364 | ExpertAI_Seq_338()
 6365 | {
 6367 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 6368 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 6369 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 6370 | return;
 6371 | }
 6373 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 6374 | SCORE += 1;
 6375 | }
 6376 | }
```

### `ExpertAI_Seq_340()` (source lines 6378–6398)

```text
 6378 | ExpertAI_Seq_340()
 6379 | {
 6381 | if( AI_CMD(CMD_FLDEFF_CHECK, EFF_TRICKROOM)){
 6383 | if( AI_CMD(CMD_IF_RND_UNDER, 240)){
 6384 | SCORE += -2;
 6385 | }
 6386 | }
 6387 | if( AI_CMD(CMD_CHECK_BENCH_COUNT, CHECK_ATTACK) == 0){
 6389 | if( AI_CMD(CMD_IF_RND_UNDER, 200)){
 6390 | SCORE += -1;
 6391 | }
 6392 | return;
 6393 | }
 6395 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 6396 | SCORE += 1;
 6397 | }
 6398 | }
```

### `ExpertAI_Seq_342()` (source lines 6400–6414)

```text
 6400 | ExpertAI_Seq_342()
 6401 | {
 6403 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_DEFENCE, 50)){
 6405 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 6406 | SCORE += -1;
 6407 | return;
 6408 | }
 6409 | }
 6411 | if( AI_CMD(CMD_IF_RND_UNDER, 128)){
 6412 | SCORE += 1;
 6413 | }
 6414 | }
```

### `ExpertAI_Seq_344()` (source lines 6441–6457)

```text
 6441 | ExpertAI_Seq_344()
 6442 | {
 6444 | if( AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_DEFENCE) == 0 ){
 6445 | if( AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) == POKETYPE_NORMAL
 6446 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) == POKETYPE_NORMAL ){
 6447 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_HIRAISIN
 6448 | || AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_TIKUDEN
 6449 | || AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_DENKIENZIN ){
 6451 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 6452 | SCORE += 1;
 6453 | }
 6454 | }
 6455 | }
 6456 | }
 6457 | }
```

### `ExpertAI_Seq_346()` (source lines 6464–6480)

```text
 6464 | ExpertAI_Seq_346()
 6465 | {
 6467 | if( AI_CMD(CMD_IF_HAVE_BATSUGUN, CHECK_ATTACK, CHECK_DEFENCE)){
 6469 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 6470 | SCORE += -2;
 6471 | return;
 6472 | }
 6473 | }
 6474 | if( AI_CMD(CMD_IF_BENCH_DAMAGE_MAX, LOSS_CALC_OFF)){
 6476 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 6477 | SCORE += 1;
 6478 | }
 6479 | }
 6480 | }
```

### `ExpertAI_Seq_347()` (source lines 6482–6514)

```text
 6482 | ExpertAI_Seq_347()
 6483 | {
 6485 | if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_POW, 6)
 6486 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_DEF, 6)
 6487 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_SPEPOW, 6)
 6488 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_SPEDEF, 6)
 6489 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_AGI, 6)
 6490 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_HIT, 6)
 6491 | || AI_CMD(CMD_IF_PARA_UNDER, CHECK_DEFENCE, PARA_AVOID, 6)){
 6493 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 6494 | SCORE += -3;
 6495 | }
 6496 | }
 6497 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_POW, 6)
 6498 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_DEF, 6)
 6499 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_SPEPOW, 6)
 6500 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_SPEDEF, 6)
 6501 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_AGI, 6)
 6502 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_HIT, 6)
 6503 | || AI_CMD(CMD_IF_PARA_OVER, CHECK_DEFENCE, PARA_AVOID, 6)){
 6505 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 6506 | SCORE += 2;
 6507 | }
 6508 | return;
 6509 | }
 6511 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 6512 | SCORE += -3;
 6513 | }
 6514 | }
```

### `ExpertAI_Seq_349()` (source lines 6516–6519)

```text
 6516 | ExpertAI_Seq_349()
 6517 | {
 6519 | }
```

### `ExpertAI_Seq_350()` (source lines 6521–6530)

```text
 6521 | ExpertAI_Seq_350()
 6522 | {
 6524 | CHK_rule = AI_CMD(CMD_CHECK_BTL_RULE);
 6525 | if( CHK_rule == BTL_RULE_SINGLE
 6526 | || CHK_rule == BTL_RULE_ROTATION ){
 6528 | SCORE += -5;
 6529 | }
 6530 | }
```

### `ExpertAI_Seq_351()` (source lines 6532–6551)

```text
 6532 | ExpertAI_Seq_351()
 6533 | {
 6535 | if( AI_CMD(CMD_IF_EXIST_GROUND, BTL_GROUND_MIST) ){
 6537 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 6538 | SCORE += 1;
 6539 | }
 6540 | }
 6541 | else if( AI_CMD(CMD_IF_EXIST_GROUND, BTL_GROUND_ELEKI) ){
 6543 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 6544 | SCORE += 1;
 6545 | }
 6546 | }
 6548 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 6549 | SCORE += 1;
 6550 | }
 6551 | }
```

### `ExpertAI_Seq_352()` (source lines 6553–6596)

```text
 6553 | ExpertAI_Seq_352()
 6554 | {
 6556 | if( AI_CMD(CMD_IF_EXIST_GROUND, BTL_GROUND_ELEKI) ){
 6558 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 6559 | SCORE += 1;
 6560 | }
 6561 | }
 6562 | else if( AI_CMD(CMD_IF_EXIST_GROUND, BTL_GROUND_GRASS) ){
 6564 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 6565 | SCORE += 1;
 6566 | }
 6567 | }
 6568 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 1)){
 6570 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 6571 | SCORE += 1;
 6572 | }
 6573 | }
 6574 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 33)){
 6576 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 6577 | SCORE += 1;
 6578 | }
 6579 | }
 6580 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 67)){
 6582 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 6583 | SCORE += 1;
 6584 | }
 6585 | }
 6586 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 167)){
 6588 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
 6589 | SCORE += 1;
 6590 | }
 6591 | }
 6593 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 6594 | SCORE += 1;
 6595 | }
 6596 | }
```

### `ExpertAI_Seq_353()` (source lines 6598–6623)

```text
 6598 | ExpertAI_Seq_353()
 6599 | {
 6601 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_HIRAISIN
 6602 | || AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_TIKUDEN
 6603 | || AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_DENKIENZIN ){
 6605 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 6606 | SCORE += -2;
 6607 | }
 6608 | }
 6609 | if( AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_DEFENCE) == 0 ){
 6610 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_HIRAISIN
 6611 | || AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_TIKUDEN
 6612 | || AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_DENKIENZIN ){
 6614 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 6615 | SCORE += 1;
 6616 | }
 6617 | }
 6618 | }
 6620 | if( AI_CMD(CMD_IF_RND_UNDER, 50) ){
 6621 | SCORE += 1;
 6622 | }
 6623 | }
```

### `ExpertAI_Seq_354()` (source lines 6625–6628)

```text
 6625 | ExpertAI_Seq_354()
 6626 | {
 6628 | }
```

### `ExpertAI_Seq_359()` (source lines 6630–6633)

```text
 6630 | ExpertAI_Seq_359()
 6631 | {
 6633 | }
```

### `ExpertAI_Seq_363()` (source lines 6635–6649)

```text
 6635 | ExpertAI_Seq_363()
 6636 | {
 6638 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)
 6639 | ){
 6641 | SCORE += -3;
 6642 | return;
 6643 | }
 6645 | if( AI_CMD(CMD_IF_RND_UNDER, 220)
 6646 | ){
 6647 | SCORE += 2;
 6648 | }
 6649 | }
```

### `ExpertAI_Seq_365()` (source lines 6651–6689)

```text
 6651 | ExpertAI_Seq_365()
 6652 | {
 6654 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_DEF, 8)
 6655 | && AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEDEF, 8)){
 6657 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 6658 | SCORE += -1;
 6659 | }
 6660 | }
 6661 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEDEF, 7)){
 6663 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 6664 | SCORE += -1;
 6665 | }
 6666 | }
 6667 | if( AI_CMD(CMD_IF_PARA_EQUAL, CHECK_ATTACK, PARA_SPEDEF, 6)){
 6668 | if( AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK, 70)){
 6669 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK, 127)){
 6671 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 6672 | SCORE += 2;
 6673 | }
 6674 | }
 6675 | }
 6676 | }
 6677 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 40)){
 6679 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 6680 | SCORE += -2;
 6681 | }
 6682 | }
 6683 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 70)){
 6685 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 6686 | SCORE += -2;
 6687 | }
 6688 | }
 6689 | }
```

### `ExpertAI_Seq_366()` (source lines 6691–6722)

```text
 6691 | ExpertAI_Seq_366()
 6692 | {
 6694 | if( AI_CMD(CMD_CHECK_BTL_RULE) == BTL_RULE_SINGLE){
 6695 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_DEF, 7)
 6696 | && AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEDEF, 7)){
 6698 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 6699 | SCORE += -1;
 6700 | }
 6701 | }
 6702 | if( AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_DEF, 9)
 6703 | && AI_CMD(CMD_IF_PARA_OVER, CHECK_ATTACK, PARA_SPEDEF, 9)){
 6705 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 6706 | SCORE += -2;
 6707 | }
 6708 | }
 6709 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 40)){
 6711 | if( AI_CMD(CMD_IF_RND_UNDER, 230) ){
 6712 | SCORE += -2;
 6713 | }
 6714 | }
 6715 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 70)){
 6717 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 6718 | SCORE += -2;
 6719 | }
 6720 | }
 6721 | }
 6722 | }
```

### `ExpertAI_Seq_368()` (source lines 6724–6749)

```text
 6724 | ExpertAI_Seq_368()
 6725 | {
 6727 | if( AI_CMD(CMD_IF_EXIST_GROUND, BTL_GROUND_MIST) ){
 6729 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 6730 | SCORE += 1;
 6731 | }
 6732 | }
 6733 | else if( AI_CMD(CMD_IF_EXIST_GROUND, BTL_GROUND_GRASS) ){
 6735 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 6736 | SCORE += 1;
 6737 | }
 6738 | }
 6739 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_DEFENCE, 1)){
 6741 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 6742 | SCORE += 1;
 6743 | }
 6744 | }
 6746 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 6747 | SCORE += 1;
 6748 | }
 6749 | }
```

### `ExpertAI_Seq_372()` (source lines 6751–6754)

```text
 6751 | ExpertAI_Seq_372()
 6752 | {
 6754 | }
```

### `ExpertAI_Seq_373()` (source lines 6756–6759)

```text
 6756 | ExpertAI_Seq_373()
 6757 | {
 6759 | }
```

### `ExpertAI_Seq_374()` (source lines 6762–6772)

```text
 6762 | ExpertAI_Seq_374()
 6763 | {
 6765 | if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_ATTACK, PARA_POW, 7)){
 6767 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
 6768 | SCORE += 1;
 6769 | }
 6770 | }
 6771 | ExpertAI_Seq_010()
 6772 | }
```

### `ExpertAI_Seq_377()` (source lines 6774–6784)

```text
 6774 | ExpertAI_Seq_377()
 6775 | {
 6777 | if( AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) == POKETYPE_HONOO
 6778 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) == POKETYPE_HONOO ){
 6780 | if( AI_CMD(CMD_IF_RND_UNDER, 80) ){
 6781 | SCORE += 2;
 6782 | }
 6783 | }
 6784 | }
```

### `ExpertAI_Seq_379()` (source lines 6786–6804)

```text
 6786 | ExpertAI_Seq_379()
 6787 | {
 6789 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 6790 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)){
 6791 | return;
 6792 | }
 6793 | if( AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) == POKETYPE_MIZU
 6794 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) == POKETYPE_MIZU ){
 6796 | if( AI_CMD(CMD_IF_RND_UNDER, 240) ){
 6797 | SCORE += 1;
 6798 | }
 6800 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 6801 | SCORE += 1;
 6802 | }
 6803 | }
 6804 | }
```

## Double: exact guarded score rules

| Function | Source lines | Influence role | What it does | Direct score writes | Calls |
|---|---:|---|---|---|---|
| `main()` | 7–20 | indirect caller/helper on a score path | Evaluates a double rule using ally attack state; applies no direct score write under the guarded conditions below. | indirect/dynamic | DoubleAI_Enemy_Main, DoubleAI_Friend_Main |
| `DoubleAI_Enemy_Main()` | 24–271 | direct score writer | Main double evaluator for the branch shown below; applies -12, -10, -2, -1, 1, 2, -5. | -12, -10, -2, -1, 1, 2, -5 | DoubleAI_Enemy_Seq_002, DoubleAI_Enemy_Seq_004, DoubleAI_Enemy_Seq_006, DoubleAI_Enemy_Seq_007, DoubleAI_Enemy_Seq_027, DoubleAI_Enemy_Seq_052, DoubleAI_Enemy_Seq_111, DoubleAI_Enemy_Seq_147, DoubleAI_Enemy_Seq_170, DoubleAI_Enemy_Seq_172, DoubleAI_Enemy_Seq_190, DoubleAI_Enemy_Seq_257, DoubleAI_Enemy_Seq_259, DoubleAI_Enemy_Seq_278, DoubleAI_Enemy_Seq_292, DoubleAI_Enemy_Seq_301, DoubleAI_Enemy_Seq_307, DoubleAI_Enemy_Seq_313, DoubleAI_Enemy_Seq_315, DoubleAI_Enemy_Seq_339, DoubleAI_Enemy_Seq_350, DoubleAI_Enemy_Seq_378, DoubleAI_Enemy_Seq_non |
| `DoubleAI_Enemy_Seq_002()` | 273–361 | direct score writer | Evaluates Double-battle sequence 002; uses types, abilities, type effectiveness, random gates, available moves, and other state and applies -3, -5, 3, 2, -1 when the guarded conditions below succeed. | -3, -5, 3, 2, -1 | — |
| `DoubleAI_Enemy_Seq_004()` | 363–464 | direct score writer | Evaluates Double-battle sequence 004; uses types, abilities, type effectiveness, random gates, available moves, and other state and applies -3, -5, 3, 2, -1 when the guarded conditions below succeed. | -3, -5, 3, 2, -1 | — |
| `DoubleAI_Enemy_Seq_006()` | 466–561 | direct score writer | Evaluates Double-battle sequence 006; uses types, abilities, type effectiveness, random gates, available moves, and other state and applies -3, -5, 3, 2, -1 when the guarded conditions below succeed. | -3, -5, 3, 2, -1 | — |
| `DoubleAI_Enemy_Seq_052()` | 562–572 | direct score writer | Evaluates Double-battle sequence 052; uses shared partner randomness and applies 3 when the guarded conditions below succeed. | 3 | — |
| `DoubleAI_Enemy_Seq_007()` | 574–613 | direct score writer | Evaluates Double-battle sequence 007; uses available moves, types, abilities, shared partner randomness and applies 3, -1 when the guarded conditions below succeed. | 3, -1 | — |
| `DoubleAI_Enemy_Seq_027()` | 615–679 | direct score writer | Evaluates Double-battle sequence 027; uses types, random gates and applies -4, -2 when the guarded conditions below succeed. | -4, -2 | — |
| `DoubleAI_Enemy_Seq_111()` | 681–928 | direct score writer | Evaluates Double-battle sequence 111; uses abilities, available moves, types, shared partner randomness, held items, and other state and applies 3, -1, -2 when the guarded conditions below succeed. | 3, -1, -2 | — |
| `DoubleAI_Enemy_Seq_147()` | 930–1043 | direct score writer | Evaluates Double-battle sequence 147; uses types, abilities, type effectiveness, move lock/status state, random gates, and other state and applies -3, -5, 3, 2, -1 when the guarded conditions below succeed. | -3, -5, 3, 2, -1 | — |
| `DoubleAI_Enemy_Seq_170()` | 1045–1065 | direct score writer | Evaluates Double-battle sequence 170; uses available moves, shared partner randomness and applies 3 when the guarded conditions below succeed. | 3 | — |
| `DoubleAI_Enemy_Seq_172()` | 1067–1144 | direct score writer | Evaluates Double-battle sequence 172; uses species, shared partner randomness, available moves, field effects, side effects, and other state and applies - 5, 3 when the guarded conditions below succeed. | - 5, 3 | — |
| `DoubleAI_Enemy_Seq_190()` | 1146–1174 | direct score writer | Evaluates Double-battle sequence 190; uses HP thresholds, available moves, shared partner randomness and applies -2, 3 when the guarded conditions below succeed. | -2, 3 | — |
| `DoubleAI_Enemy_Seq_257()` | 1176–1268 | direct score writer | Evaluates Double-battle sequence 257; uses types, abilities, type effectiveness, random gates, available moves, and other state and applies -3, -5, 3, 2, -1 when the guarded conditions below succeed. | -3, -5, 3, 2, -1 | — |
| `DoubleAI_Enemy_Seq_259()` | 1270–1348 | direct score writer | Evaluates Double-battle sequence 259 and applies -2, -1 when the guarded conditions below succeed. | -2, -1 | DoubleAI_Enemy_Seq_259_sub |
| `DoubleAI_Enemy_Seq_259_sub(value)` | 1349–1399 | direct score writer | Evaluates Double-battle sequence 259; uses available moves, shared partner randomness, species and applies value, - 5 when the guarded conditions below succeed. | value, - 5 | — |
| `DoubleAI_Enemy_Seq_278()` | 1401–1478 | direct score writer | Evaluates Double-battle sequence 278; uses species, shared partner randomness and applies 2 when the guarded conditions below succeed. | 2 | DoubleAI_Enemy_Seq_111 |
| `DoubleAI_Enemy_Seq_292()` | 1480–1509 | direct score writer | Evaluates Double-battle sequence 292; uses type effectiveness, types, shared partner randomness and applies 2 when the guarded conditions below succeed. | 2 | — |
| `DoubleAI_Enemy_Seq_301()` | 1511–1525 | direct score writer | Evaluates Double-battle sequence 301; uses type effectiveness, available moves, shared partner randomness and applies 3 when the guarded conditions below succeed. | 3 | — |
| `DoubleAI_Enemy_Seq_307()` | 1527–1636 | direct score writer | Evaluates Double-battle sequence 307; uses types, random gates and applies 2 when the guarded conditions below succeed. | 2 | — |
| `DoubleAI_Enemy_Seq_313()` | 1638–1641 | reachable dispatcher/predicate support | Evaluates Double-battle sequence 313 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `DoubleAI_Enemy_Seq_315()` | 1643–1676 | direct score writer | Evaluates Double-battle sequence 315; uses abilities, available moves, HP thresholds, shared partner randomness, random gates and applies 3, -8 when the guarded conditions below succeed. | 3, -8 | — |
| `DoubleAI_Enemy_Seq_339()` | 1678–1694 | direct score writer | Evaluates Double-battle sequence 339; uses types, shared partner randomness and applies 2 when the guarded conditions below succeed. | 2 | — |
| `DoubleAI_Enemy_Seq_350()` | 1696–1707 | direct score writer | Evaluates Double-battle sequence 350; uses types, shared partner randomness and applies 2 when the guarded conditions below succeed. | 2 | — |
| `DoubleAI_Enemy_Seq_non()` | 1708–1712 | direct score writer | Evaluates a double rule using the native battle-state interface; applies -12 under the guarded conditions below. | -12 | — |
| `DoubleAI_Enemy_Seq_378()` | 1714–1848 | direct score writer | Evaluates Double-battle sequence 378; uses types, abilities, type effectiveness, random gates, available moves, and other state and applies -3, -5, 3, 2, -1 when the guarded conditions below succeed. | -3, -5, 3, 2, -1 | — |
| `DoubleAI_Friend_Main()` | 1852–1879 | direct score writer | Main double evaluator for the branch shown below; applies -30, -20. | -30, -20 | DoubleAI_Friend_Seq_118, DoubleAI_Friend_Seq_154, DoubleAI_Friend_Seq_167, DoubleAI_Friend_Seq_176, DoubleAI_Friend_Seq_178, DoubleAI_Friend_Seq_191, DoubleAI_Friend_Seq_300, DoubleAI_Friend_Seq_309 |
| `DoubleAI_Friend_Seq_118()` | 1881–1902 | direct score writer | Evaluates Double-battle sequence 118; uses physical/special damage type, held items, abilities, HP thresholds, shared partner randomness and applies -12, 2, -10 when the guarded conditions below succeed. | -12, 2, -10 | — |
| `DoubleAI_Friend_Seq_154()` | 1904–1917 | direct score writer | Evaluates Double-battle sequence 154; uses abilities, shared partner randomness and applies 2, -10 when the guarded conditions below succeed. | 2, -10 | — |
| `DoubleAI_Friend_Seq_167()` | 1919–1939 | direct score writer | Evaluates Double-battle sequence 167; uses abilities, shared partner randomness, status conditions and applies 2 when the guarded conditions below succeed. | 2 | — |
| `DoubleAI_Friend_Seq_176()` | 1941–1959 | direct score writer | Evaluates Double-battle sequence 176; uses shared partner randomness and applies 2, -1 when the guarded conditions below succeed. | 2, -1 | — |
| `DoubleAI_Friend_Seq_178()` | 1963–1967 | reachable dispatcher/predicate support | Evaluates Double-battle sequence 178 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `DoubleAI_Friend_Seq_191()` | 1969–1973 | reachable dispatcher/predicate support | Evaluates Double-battle sequence 191 and applies no direct score write when the guarded conditions below succeed. | indirect/dynamic | — |
| `DoubleAI_Friend_Seq_300()` | 1975–2006 | direct score writer | Evaluates Double-battle sequence 300; uses abilities, available moves, HP thresholds, shared partner randomness, random gates and applies 3, -8 when the guarded conditions below succeed. | 3, -8 | — |
| `DoubleAI_Friend_Seq_309()` | 2008–2033 | direct score writer | Evaluates Double-battle sequence 309; uses HP thresholds, shared partner randomness and applies -1, 2 when the guarded conditions below succeed. | -1, 2 | — |

The complete guarded bodies follow:

### `main()` (source lines 7–20)

```text
    7 | main()
    8 | {
    9 | if( AI_CMD(CMD_IF_MIKATA_ATTACK) )
   10 | {
   12 | DoubleAI_Friend_Main()
   13 | }
   14 | else{
   16 | DoubleAI_Enemy_Main()
   17 | }
   20 | }
```

### `DoubleAI_Enemy_Main()` (source lines 24–271)

```text
   24 | DoubleAI_Enemy_Main()
   25 | {
   26 | wazaNo = CURRENT_MOVE();
   27 | waza_seq_no = AI_CMD(CMD_CHECK_WORKWAZA_SEQNO);
   28 | Waza_Type = AI_CMD(CMD_CHECK_TYPE, CHECK_WAZA);
   29 | DefFrd_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND);
   30 | Atk_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
   32 | if( DefFrd_Tokusei == TOKUSEI_MAZIKKUMIRAA){
   33 | if( wazaNo == WAZANO_SIPPOWOHURU || wazaNo == WAZANO_NIRAMITUKERU
   34 | || wazaNo == WAZANO_NAKIGOE || wazaNo == WAZANO_ITOWOHAKU
   35 | || wazaNo == WAZANO_DOKUGASU || wazaNo == WAZANO_WATAHOUSI
   36 | || wazaNo == WAZANO_AMAIKAORI || wazaNo == WAZANO_KAIHUKUHUUZI
   37 | || wazaNo == WAZANO_YUUWAKU || wazaNo == WAZANO_DAAKUHOORU
   38 | || wazaNo == WAZANO_BENOMUTORAPPU || wazaNo == WAZANO_NAKIGOE
   39 | || wazaNo == WAZANO_MAKIBISI || wazaNo == WAZANO_DOKUBISI
   40 | || wazaNo == WAZANO_SUTERUSUROKKU || wazaNo == WAZANO_NEBANEBANETTO ){
   41 | if( Atk_Tokusei != TOKUSEI_KATAYABURI
   42 | && Atk_Tokusei != TOKUSEI_TAABOBUREIZU
   43 | && Atk_Tokusei != TOKUSEI_TERABORUTEEZI){
   45 | SCORE += -12;
   46 | return;
   47 | }
   48 | }
   49 | }
   51 | if( DefFrd_Tokusei == TOKUSEI_HIRAISIN){
   52 | if( Waza_Type == POKETYPE_DENKI ){
   53 | if( Atk_Tokusei != TOKUSEI_KATAYABURI
   54 | && Atk_Tokusei != TOKUSEI_TAABOBUREIZU
   55 | && Atk_Tokusei != TOKUSEI_TERABORUTEEZI){
   56 | if( AI_CMD(CMD_CHECK_DAMAGE_WAZA, CURRENT_MOVE())){
   58 | SCORE += -12;
   59 | return;
   60 | }
   61 | if( wazaNo == WAZANO_DENZIHA
   62 | || wazaNo == WAZANO_KAIDENPA
   63 | || wazaNo == WAZANO_SOUDEN ){
   65 | SCORE += -12;
   66 | return;
   67 | }
   68 | }
   69 | }
   70 | }
   72 | if( DefFrd_Tokusei == TOKUSEI_YOBIMIZU){
   73 | if( Waza_Type == POKETYPE_MIZU ){
   74 | if( Atk_Tokusei != TOKUSEI_KATAYABURI
   75 | && Atk_Tokusei != TOKUSEI_TAABOBUREIZU
   76 | && Atk_Tokusei != TOKUSEI_TERABORUTEEZI){
   77 | if( AI_CMD(CMD_CHECK_DAMAGE_WAZA, CURRENT_MOVE())){
   79 | SCORE += -12;
   80 | return;
   81 | }
   82 | if( wazaNo == WAZANO_MIZUBITASI ){
   84 | SCORE += -12;
   85 | return;
   86 | }
   87 | }
   88 | }
   89 | }
   90 | if( AI_CMD(CMD_IF_WAZAHIDE, CHECK_DEFENCE) ){
   91 | if( AI_CMD(CMD_IF_FIRST, IF_FIRST_ATTACK)){
   92 | if( Atk_Tokusei != TOKUSEI_NOOGAADO){
   93 | Def_LastWaza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_DEFENCE);
   94 | if( Def_LastWaza != WAZANO_SORAWOTOBU
   95 | || Def_LastWaza != WAZANO_TOBIHANERU ){
   96 | if( wazaNo != WAZANO_KAMINARI
   97 | || wazaNo != WAZANO_SUKAIAPPAA
   98 | || wazaNo != WAZANO_UTIOTOSU
   99 | || wazaNo != WAZANO_KAZEOKOSI
  100 | || wazaNo != WAZANO_TATUMAKI){
  102 | SCORE += -10;
  103 | return;
  104 | }
  105 | }
  106 | else if( Def_LastWaza != WAZANO_ANAWOHORU ){
  107 | if( wazaNo != WAZANO_ZISIN
  108 | || wazaNo != WAZANO_MAGUNITYUUDO){
  110 | SCORE += -10;
  111 | return;
  112 | }
  113 | }
  114 | else if( Def_LastWaza != WAZANO_DAIBINGU ){
  115 | if( wazaNo != WAZANO_UZUSIO
  116 | || wazaNo != WAZANO_NAMINORI){
  118 | SCORE += -10;
  119 | return;
  120 | }
  121 | }
  122 | else{
  124 | SCORE += -10;
  125 | return;
  126 | }
  127 | }
  128 | }
  129 | }
  130 | if( AI_CMD(CMD_COMP_POWER, LOSS_CALC_OFF) != COMP_POWER_NONE ){
  133 | if( waza_seq_no != 026
  134 | && waza_seq_no != 038
  135 | && waza_seq_no != 040
  136 | && waza_seq_no != 041
  137 | && waza_seq_no != 087
  138 | && waza_seq_no != 088
  139 | && waza_seq_no != 088
  140 | && waza_seq_no != 130
  141 | && waza_seq_no != 144
  142 | && waza_seq_no != 189
  143 | && waza_seq_no != 190
  144 | && waza_seq_no != 227
  145 | && waza_seq_no != 320 ){
  146 | if( AI_CMD(CMD_IFN_WAZA_HINSHI, LOSS_CALC_OFF)){
  147 | if( AI_CMD(CMD_IFN_HP_EQUAL, CHECK_DEFENCE_FRIEND, 0)){
  148 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)){
  150 | if( AI_CMD(CMD_IF_RND_UNDER, 240)){
  151 | SCORE += -2;
  152 | }
  153 | }
  154 | else if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
  156 | if( AI_CMD(CMD_IF_RND_UNDER, 200)){
  157 | SCORE += -1;
  158 | }
  159 | }
  160 | }
  161 | }
  163 | if( AI_CMD(CMD_COMP_POWER_WITH_PARTNER, LOSS_CALC_OFF) == COMP_POWER_TOP ){
  165 | if( waza_seq_no != 007){
  167 | if( AI_CMD(CMD_IF_RND_UNDER, 100) ){
  168 | SCORE += 1;
  169 | }
  179 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_2BAI) ){
  181 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ){
  182 | SCORE += 1;
  183 | }
  184 | }
  185 | }
  186 | }
  187 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_TEDASUKE)){
  188 | if (AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK) == 0){
  189 | if (AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK_FRIEND) >= 2){
  191 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 100)){
  192 | SCORE += 2;
  193 | }
  194 | }
  195 | }
  196 | }
  197 | }
  198 | }
  199 | Frd_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK_FRIEND);
  200 | Atk_Type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE1);
  201 | Atk_Type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE2);
  202 | Frd_Type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE1);
  203 | Frd_Type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE2);
  204 | if ( Frd_Tokusei == TOKUSEI_HIRAISIN
  205 | && Waza_Type == POKETYPE_DENKI
  206 | && WazaNo != WAZANO_HOUDEN
  207 | && WazaNo != WAZANO_ZYUUDEN
  208 | && WazaNo != WAZANO_DENZIHUYUU
  209 | && WazaNo != WAZANO_PURAZUMASYAWAA
  210 | && WazaNo != WAZANO_ZIBASOUSA
  211 | && WazaNo != WAZANO_EREKIFIIRUDO ){
  212 | if ( Frd_Type1 == POKETYPE_JIMEN
  213 | || Frd_Type2 == POKETYPE_JIMEN ){
  215 | SCORE += -5;
  216 | }
  218 | if( AI_CMD(CMD_IF_COMMONRND_UNDER, 230) ){
  219 | SCORE += -5;
  220 | }
  221 | }
  222 | if ( Frd_Tokusei == TOKUSEI_YOBIMIZU
  223 | && Waza_Type == POKETYPE_MIZU
  224 | && WazaNo != WAZANO_NAMINORI
  225 | && WazaNo != WAZANO_KARANIKOMORU
  226 | && WazaNo != WAZANO_AMAGOI
  227 | && WazaNo != WAZANO_MIZUASOBI
  228 | && WazaNo != WAZANO_AKUARINGU ){
  230 | if( AI_CMD(CMD_IF_COMMONRND_UNDER, 230) ){
  231 | SCORE += -5;
  232 | }
  233 | }
  237 | switch( waza_seq_no )
  238 | {
  239 | case 002: DoubleAI_Enemy_Seq_002();
  240 | case 004: DoubleAI_Enemy_Seq_004();
  241 | case 006: DoubleAI_Enemy_Seq_006();
  242 | case 007: DoubleAI_Enemy_Seq_007();
  243 | case 027: DoubleAI_Enemy_Seq_027();
  244 | case 052: DoubleAI_Enemy_Seq_052();
  245 | case 111: DoubleAI_Enemy_Seq_111();
  246 | case 147: DoubleAI_Enemy_Seq_147();
  247 | case 170: DoubleAI_Enemy_Seq_170();
  248 | case 172: DoubleAI_Enemy_Seq_172();
  249 | case 190: DoubleAI_Enemy_Seq_190();
  250 | case 212: DoubleAI_Enemy_Seq_052();
  251 | case 257: DoubleAI_Enemy_Seq_257();
  252 | case 259: DoubleAI_Enemy_Seq_259();
  253 | case 278: DoubleAI_Enemy_Seq_278();
  254 | case 284: DoubleAI_Enemy_Seq_052();
  255 | case 290: DoubleAI_Enemy_Seq_052();
  256 | case 292: DoubleAI_Enemy_Seq_292();
  257 | case 301: DoubleAI_Enemy_Seq_301();
  258 | case 307: DoubleAI_Enemy_Seq_307();
  259 | case 312: DoubleAI_Enemy_Seq_052();
  260 | case 300: DoubleAI_Enemy_Seq_non();
  261 | case 309: DoubleAI_Enemy_Seq_non();
  262 | case 313: DoubleAI_Enemy_Seq_313();
  263 | case 315: DoubleAI_Enemy_Seq_315();
  264 | case 339: DoubleAI_Enemy_Seq_339();
  265 | case 350: DoubleAI_Enemy_Seq_350();
  266 | case 355: DoubleAI_Enemy_Seq_111();
  267 | case 361: DoubleAI_Enemy_Seq_111();
  268 | case 376: DoubleAI_Enemy_Seq_111();
  269 | case 378: DoubleAI_Enemy_Seq_378();
  270 | }
  271 | }
```

### `DoubleAI_Enemy_Seq_002()` (source lines 273–361)

```text
  273 | DoubleAI_Enemy_Seq_002()
  274 | {
  276 | wazaNo = CURRENT_MOVE();
  277 | if( wazaNo != WAZANO_HEDOROWHEEBU ){
  278 | return;
  279 | }
  280 | Frd_Type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE1);
  281 | Frd_Type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE2);
  282 | Frd_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK_FRIEND);
  283 | Atk_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
  284 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
  285 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
  286 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
  287 | if( Frd_Tokusei != TOKUSEI_TEREPASII){
  288 | if( Frd_Type1 == POKETYPE_KUSA
  289 | || Frd_Type2 == POKETYPE_KUSA){
  291 | SCORE += -3;
  292 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
  293 | SCORE += -5;
  294 | }
  295 | }
  296 | }
  297 | return;
  298 | }
  299 | if( Frd_Tokusei == TOKUSEI_TEREPASII){
  300 | if( Atk_Tokusei != TOKUSEI_KATAYABURI
  301 | && Atk_Tokusei != TOKUSEI_TERABORUTEEZI
  302 | && Atk_Tokusei != TOKUSEI_TAABOBUREIZU){
  304 | if (AI_CMD(CMD_IF_RND_UNDER, 160)){
  305 | SCORE += 3;
  306 | }
  307 | return;
  308 | }
  309 | }
  310 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_MAMORU)
  311 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_MIKIRI)
  312 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_KINGUSIIRUDO)
  313 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_NIIDORUGAADO)
  314 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_TATAMIGAESI)
  315 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_WAIDOGAADO)){
  316 | Last_Frend_Waza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_ATTACK_FRIEND);
  317 | if( Last_Frend_Waza != WAZANO_MAMORU
  318 | && Last_Frend_Waza != WAZANO_MIKIRI
  319 | && Last_Frend_Waza != WAZANO_KINGUSIIRUDO
  320 | && Last_Frend_Waza != WAZANO_NIIDORUGAADO
  321 | && Last_Frend_Waza != WAZANO_TATAMIGAESI
  322 | && Last_Frend_Waza != WAZANO_WAIDOGAADO
  323 | && Last_Frend_Waza != WAZANO_FASUTOGAADO){
  325 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  326 | SCORE += 2;
  327 | return;
  328 | }
  329 | }
  330 | }
  331 | if( Frd_Type1 == POKETYPE_KUSA
  332 | || Frd_Type2 == POKETYPE_KUSA){
  334 | SCORE += -3;
  335 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
  336 | SCORE += -5;
  337 | }
  338 | }
  339 | if( Frd_Type1 == POKETYPE_DOKU
  340 | || Frd_Type2 == POKETYPE_DOKU
  341 | || Frd_Type1 == POKETYPE_JIMEN
  342 | || Frd_Type2 == POKETYPE_JIMEN
  343 | || Frd_Type1 == POKETYPE_IWA
  344 | || Frd_Type2 == POKETYPE_IWA
  345 | || Frd_Type1 == POKETYPE_GHOST
  346 | || Frd_Type2 == POKETYPE_GHOST
  347 | || Frd_Type1 == POKETYPE_HAGANE
  348 | || Frd_Type2 == POKETYPE_HAGANE){
  350 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  351 | SCORE += 2;
  352 | return;
  353 | }
  354 | }
  355 | else{
  357 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
  358 | SCORE += -1;
  359 | }
  360 | }
  361 | }
```

### `DoubleAI_Enemy_Seq_004()` (source lines 363–464)

```text
  363 | DoubleAI_Enemy_Seq_004()
  364 | {
  366 | wazaNo = CURRENT_MOVE();
  367 | if( wazaNo != WAZANO_HUNEN
  368 | && wazaNo != WAZANO_KAENDAN ){
  369 | return;
  370 | }
  371 | Frd_Type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE1);
  372 | Frd_Type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE2);
  373 | Frd_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK_FRIEND);
  374 | Atk_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
  375 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
  376 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
  377 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
  378 | if( Frd_Tokusei != TOKUSEI_MORAIBI
  379 | && Frd_Tokusei != TOKUSEI_TEREPASII){
  380 | if( Frd_Type1 == POKETYPE_MUSHI
  381 | || Frd_Type2 == POKETYPE_MUSHI
  382 | || Frd_Type1 == POKETYPE_HAGANE
  383 | || Frd_Type2 == POKETYPE_HAGANE
  384 | || Frd_Type1 == POKETYPE_KOORI
  385 | || Frd_Type2 == POKETYPE_KOORI
  386 | || Frd_Type1 == POKETYPE_KUSA
  387 | || Frd_Type2 == POKETYPE_KUSA){
  389 | SCORE += -3;
  390 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
  391 | SCORE += -5;
  392 | }
  393 | }
  394 | }
  395 | return;
  396 | }
  397 | if( Frd_Tokusei == TOKUSEI_MORAIBI
  398 | || Frd_Tokusei == TOKUSEI_TEREPASII){
  399 | if( Atk_Tokusei != TOKUSEI_KATAYABURI
  400 | && Atk_Tokusei != TOKUSEI_TERABORUTEEZI
  401 | && Atk_Tokusei != TOKUSEI_TAABOBUREIZU){
  403 | if (AI_CMD(CMD_IF_RND_UNDER, 160)){
  404 | SCORE += 3;
  405 | }
  406 | return;
  407 | }
  408 | }
  409 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_MAMORU)
  410 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_MIKIRI)
  411 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_KINGUSIIRUDO)
  412 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_NIIDORUGAADO)
  413 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_TATAMIGAESI)
  414 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_WAIDOGAADO)){
  415 | Last_Frend_Waza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_ATTACK_FRIEND);
  416 | if( Last_Frend_Waza != WAZANO_MAMORU
  417 | && Last_Frend_Waza != WAZANO_MIKIRI
  418 | && Last_Frend_Waza != WAZANO_KINGUSIIRUDO
  419 | && Last_Frend_Waza != WAZANO_NIIDORUGAADO
  420 | && Last_Frend_Waza != WAZANO_TATAMIGAESI
  421 | && Last_Frend_Waza != WAZANO_WAIDOGAADO
  422 | && Last_Frend_Waza != WAZANO_FASUTOGAADO){
  424 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  425 | SCORE += 2;
  426 | return;
  427 | }
  428 | }
  429 | }
  430 | if( Frd_Type1 == POKETYPE_MUSHI
  431 | || Frd_Type2 == POKETYPE_MUSHI
  432 | || Frd_Type1 == POKETYPE_HAGANE
  433 | || Frd_Type2 == POKETYPE_HAGANE
  434 | || Frd_Type1 == POKETYPE_KOORI
  435 | || Frd_Type2 == POKETYPE_KOORI
  436 | || Frd_Type1 == POKETYPE_KUSA
  437 | || Frd_Type2 == POKETYPE_KUSA){
  439 | SCORE += -3;
  440 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
  441 | SCORE += -5;
  442 | }
  443 | }
  444 | if( Frd_Type1 == POKETYPE_HONOO
  445 | || Frd_Type2 == POKETYPE_HONOO
  446 | || Frd_Type1 == POKETYPE_MIZU
  447 | || Frd_Type2 == POKETYPE_MIZU
  448 | || Frd_Type1 == POKETYPE_IWA
  449 | || Frd_Type2 == POKETYPE_IWA
  450 | || Frd_Type1 == POKETYPE_DRAGON
  451 | || Frd_Type2 == POKETYPE_DRAGON){
  453 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  454 | SCORE += 2;
  455 | return;
  456 | }
  457 | }
  458 | else{
  460 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
  461 | SCORE += -1;
  462 | }
  463 | }
  464 | }
```

### `DoubleAI_Enemy_Seq_006()` (source lines 466–561)

```text
  466 | DoubleAI_Enemy_Seq_006()
  467 | {
  469 | wazaNo = CURRENT_MOVE();
  470 | if( wazaNo != WAZANO_HOUDEN
  471 | && wazaNo != WAZANO_PARABORATYAAZI ){
  472 | return;
  473 | }
  474 | Frd_Type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE1);
  475 | Frd_Type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE2);
  476 | Frd_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK_FRIEND);
  477 | Atk_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
  478 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
  479 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
  480 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
  481 | if( Frd_Tokusei != TOKUSEI_TIKUDEN
  482 | && Frd_Tokusei != TOKUSEI_DENKIENZIN
  483 | && Frd_Tokusei != TOKUSEI_TEREPASII){
  484 | if( Frd_Type1 == POKETYPE_MIZU
  485 | || Frd_Type2 == POKETYPE_MIZU
  486 | || Frd_Type1 == POKETYPE_HIKOU
  487 | || Frd_Type2 == POKETYPE_HIKOU){
  489 | SCORE += -3;
  490 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
  491 | SCORE += -5;
  492 | }
  493 | }
  494 | }
  495 | return;
  496 | }
  497 | if( Frd_Tokusei == TOKUSEI_TIKUDEN
  498 | || Frd_Tokusei == TOKUSEI_DENKIENZIN
  499 | || Frd_Tokusei == TOKUSEI_TEREPASII){
  500 | if( Atk_Tokusei != TOKUSEI_KATAYABURI
  501 | && Atk_Tokusei != TOKUSEI_TERABORUTEEZI
  502 | && Atk_Tokusei != TOKUSEI_TAABOBUREIZU){
  504 | if (AI_CMD(CMD_IF_RND_UNDER, 160)){
  505 | SCORE += 3;
  506 | }
  507 | return;
  508 | }
  509 | }
  510 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_MAMORU)
  511 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_MIKIRI)
  512 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_KINGUSIIRUDO)
  513 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_NIIDORUGAADO)
  514 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_TATAMIGAESI)
  515 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_WAIDOGAADO)){
  516 | Last_Frend_Waza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_ATTACK_FRIEND);
  517 | if( Last_Frend_Waza != WAZANO_MAMORU
  518 | && Last_Frend_Waza != WAZANO_MIKIRI
  519 | && Last_Frend_Waza != WAZANO_KINGUSIIRUDO
  520 | && Last_Frend_Waza != WAZANO_NIIDORUGAADO
  521 | && Last_Frend_Waza != WAZANO_TATAMIGAESI
  522 | && Last_Frend_Waza != WAZANO_WAIDOGAADO
  523 | && Last_Frend_Waza != WAZANO_FASUTOGAADO){
  525 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  526 | SCORE += 2;
  527 | return;
  528 | }
  529 | }
  530 | }
  531 | if( Frd_Type1 == POKETYPE_MIZU
  532 | || Frd_Type2 == POKETYPE_MIZU
  533 | || Frd_Type1 == POKETYPE_HIKOU
  534 | || Frd_Type2 == POKETYPE_HIKOU){
  536 | SCORE += -3;
  537 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
  538 | SCORE += -5;
  539 | }
  540 | }
  541 | if( Frd_Type1 == POKETYPE_KUSA
  542 | || Frd_Type2 == POKETYPE_KUSA
  543 | || Frd_Type1 == POKETYPE_DENKI
  544 | || Frd_Type2 == POKETYPE_DENKI
  545 | || Frd_Type1 == POKETYPE_JIMEN
  546 | || Frd_Type2 == POKETYPE_JIMEN
  547 | || Frd_Type1 == POKETYPE_DRAGON
  548 | || Frd_Type2 == POKETYPE_DRAGON){
  550 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  551 | SCORE += 2;
  552 | return;
  553 | }
  554 | }
  555 | else{
  557 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
  558 | SCORE += -1;
  559 | }
  560 | }
  561 | }
```

### `DoubleAI_Enemy_Seq_052()` (source lines 562–572)

```text
  562 | DoubleAI_Enemy_Seq_052()
  563 | {
  565 | if (AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK) != 0){
  567 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 180)){
  568 | SCORE += 3;
  569 | return;
  570 | }
  571 | }
  572 | }
```

### `DoubleAI_Enemy_Seq_007()` (source lines 574–613)

```text
  574 | DoubleAI_Enemy_Seq_007()
  575 | {
  577 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_MAMORU)
  578 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_MIKIRI)
  579 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_KINGUSIIRUDO)
  580 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_NIIDORUGAADO)
  581 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_TATAMIGAESI)
  582 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_WAIDOGAADO)){
  583 | if( AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) != POKETYPE_GHOST
  584 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) != POKETYPE_GHOST
  585 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_FRIEND_TYPE1) != POKETYPE_GHOST
  586 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_FRIEND_TYPE2) != POKETYPE_GHOST
  587 | || AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) != TOKUSEI_SIMERIKE
  588 | || AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) != TOKUSEI_SIMERIKE
  589 | || AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK_FRIEND) != TOKUSEI_SIMERIKE){
  590 | Last_Frend_Waza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_ATTACK_FRIEND);
  591 | if( Last_Frend_Waza != WAZANO_MAMORU
  592 | && Last_Frend_Waza != WAZANO_MIKIRI
  593 | && Last_Frend_Waza != WAZANO_KINGUSIIRUDO
  594 | && Last_Frend_Waza != WAZANO_NIIDORUGAADO
  595 | && Last_Frend_Waza != WAZANO_TATAMIGAESI
  596 | && Last_Frend_Waza != WAZANO_WAIDOGAADO
  597 | && Last_Frend_Waza != WAZANO_FASUTOGAADO){
  599 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  600 | SCORE += 3;
  601 | return;
  602 | }
  603 | }
  604 | else{
  605 | if( AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE1) != POKETYPE_GHOST
  606 | || AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE2) != POKETYPE_GHOST
  607 | || AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK_FRIEND) == TOKUSEI_TEREPASII){
  608 | SCORE += -1;
  609 | }
  610 | }
  611 | }
  612 | }
  613 | }
```

### `DoubleAI_Enemy_Seq_027()` (source lines 615–679)

```text
  615 | DoubleAI_Enemy_Seq_027()
  616 | {
  618 | wazaNo = CURRENT_MOVE();
  619 | Def_Frd_Type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_FRIEND_TYPE1);
  620 | Def_Frd_Type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_FRIEND_TYPE2);
  621 | if( wazaNo == WAZANO_ABARERU ){
  622 | if( Def_Frd_Type1 == POKETYPE_GHOST
  623 | || Def_Frd_Type2 == POKETYPE_GHOST ){
  625 | if (AI_CMD(CMD_IF_RND_UNDER, 230)){
  626 | SCORE += -4;
  627 | }
  628 | }
  629 | else if( Def_Frd_Type1 == POKETYPE_IWA
  630 | || Def_Frd_Type2 == POKETYPE_IWA
  631 | || Def_Frd_Type1 == POKETYPE_HAGANE
  632 | || Def_Frd_Type2 == POKETYPE_HAGANE ){
  634 | if (AI_CMD(CMD_IF_RND_UNDER, 200)){
  635 | SCORE += -2;
  636 | }
  637 | }
  638 | }
  639 | else if( wazaNo == WAZANO_HANABIRANOMAI ){
  640 | if( Def_Frd_Type1 == POKETYPE_HONOO
  641 | || Def_Frd_Type2 == POKETYPE_HONOO
  642 | || Def_Frd_Type1 == POKETYPE_KUSA
  643 | || Def_Frd_Type2 == POKETYPE_KUSA
  644 | || Def_Frd_Type1 == POKETYPE_DOKU
  645 | || Def_Frd_Type2 == POKETYPE_DOKU
  646 | || Def_Frd_Type1 == POKETYPE_HIKOU
  647 | || Def_Frd_Type2 == POKETYPE_HIKOU
  648 | || Def_Frd_Type1 == POKETYPE_MUSHI
  649 | || Def_Frd_Type2 == POKETYPE_MUSHI
  650 | || Def_Frd_Type1 == POKETYPE_DRAGON
  651 | || Def_Frd_Type2 == POKETYPE_DRAGON
  652 | || Def_Frd_Type1 == POKETYPE_HAGANE
  653 | || Def_Frd_Type2 == POKETYPE_HAGANE ){
  654 | if( Def_Frd_Type1 != POKETYPE_MIZU
  655 | && Def_Frd_Type2 != POKETYPE_MIZU
  656 | && Def_Frd_Type1 != POKETYPE_JIMEN
  657 | && Def_Frd_Type2 != POKETYPE_JIMEN
  658 | && Def_Frd_Type1 != POKETYPE_IWA
  659 | && Def_Frd_Type2 != POKETYPE_IWA ){
  661 | if (AI_CMD(CMD_IF_RND_UNDER, 200)){
  662 | SCORE += -2;
  663 | }
  664 | }
  665 | }
  666 | }
  667 | else if( wazaNo == WAZANO_GEKIRIN ){
  668 | if( Def_Frd_Type1 == POKETYPE_HAGANE
  669 | || Def_Frd_Type2 == POKETYPE_HAGANE ){
  670 | if( Def_Frd_Type1 != POKETYPE_DRAGON
  671 | && Def_Frd_Type2 != POKETYPE_DRAGON ){
  673 | if (AI_CMD(CMD_IF_RND_UNDER, 200)){
  674 | SCORE += -2;
  675 | }
  676 | }
  677 | }
  678 | }
  679 | }
```

### `DoubleAI_Enemy_Seq_111()` (source lines 681–928)

```text
  681 | DoubleAI_Enemy_Seq_111()
  682 | {
  684 | Last_Attack_Waza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_ATTACK);
  685 | Atk_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
  686 | Frd_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK_FRIEND);
  687 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_ZIBAKU)
  688 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_DAIBAKUHATU)){
  689 | if( AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) != POKETYPE_GHOST
  690 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) != POKETYPE_GHOST
  691 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_FRIEND_TYPE1) != POKETYPE_GHOST
  692 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_FRIEND_TYPE2) != POKETYPE_GHOST
  693 | || AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) != TOKUSEI_SIMERIKE
  694 | || AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE_FRIEND) != TOKUSEI_SIMERIKE
  695 | || AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK_FRIEND) != TOKUSEI_SIMERIKE){
  696 | if( Last_Attack_Waza != WAZANO_MAMORU
  697 | && Last_Attack_Waza != WAZANO_MIKIRI
  698 | && Last_Attack_Waza != WAZANO_KINGUSIIRUDO
  699 | && Last_Attack_Waza != WAZANO_NIIDORUGAADO
  700 | && Last_Attack_Waza != WAZANO_TATAMIGAESI
  701 | && Last_Attack_Waza != WAZANO_WAIDOGAADO
  702 | && Last_Attack_Waza != WAZANO_FASUTOGAADO){
  704 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  705 | SCORE += 3;
  706 | return;
  707 | }
  708 | else{
  709 | SCORE += -1;
  710 | }
  711 | }
  712 | }
  713 | }
  714 | else if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_ZISIN)){
  715 | if( Last_Attack_Waza != WAZANO_MAMORU
  716 | && Last_Attack_Waza != WAZANO_MIKIRI
  717 | && Last_Attack_Waza != WAZANO_KINGUSIIRUDO
  718 | && Last_Attack_Waza != WAZANO_NIIDORUGAADO
  719 | && Last_Attack_Waza != WAZANO_TATAMIGAESI
  720 | && Last_Attack_Waza != WAZANO_WAIDOGAADO
  721 | && Last_Attack_Waza != WAZANO_FASUTOGAADO){
  722 | if( Atk_Tokusei != TOKUSEI_HUYUU
  723 | || Atk_Tokusei != TOKUSEI_TEREPASII
  724 | || Atk_Tokusei , WAZASICK_FLYING
  725 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_FRIEND_TYPE1) != POKETYPE_HIKOU
  726 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_FRIEND_TYPE2) != POKETYPE_HIKOU){
  728 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  729 | SCORE += 3;
  730 | }
  731 | return;
  732 | }
  733 | if( Frd_Tokusei == TOKUSEI_KATAYABURI
  734 | || Frd_Tokusei == TOKUSEI_TERABORUTEEZI
  735 | || Frd_Tokusei == TOKUSEI_TAABOBUREIZU ){
  737 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  738 | SCORE += 3;
  739 | return;
  740 | }
  741 | }
  742 | }
  743 | }
  744 | else if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_NAMINORI)){
  745 | if( Last_Attack_Waza != WAZANO_MAMORU
  746 | && Last_Attack_Waza != WAZANO_MIKIRI
  747 | && Last_Attack_Waza != WAZANO_KINGUSIIRUDO
  748 | && Last_Attack_Waza != WAZANO_NIIDORUGAADO
  749 | && Last_Attack_Waza != WAZANO_TATAMIGAESI
  750 | && Last_Attack_Waza != WAZANO_WAIDOGAADO
  751 | && Last_Attack_Waza != WAZANO_FASUTOGAADO){
  752 | if( Atk_Tokusei != TOKUSEI_TYOSUI
  753 | || Atk_Tokusei != TOKUSEI_YOBIMIZU
  754 | || Atk_Tokusei != TOKUSEI_KANSOUHADA
  755 | || Atk_Tokusei != TOKUSEI_TEREPASII){
  757 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  758 | SCORE += 3;
  759 | }
  760 | return;
  761 | }
  762 | if( Frd_Tokusei == TOKUSEI_KATAYABURI
  763 | || Frd_Tokusei == TOKUSEI_TERABORUTEEZI
  764 | || Frd_Tokusei == TOKUSEI_TAABOBUREIZU ){
  766 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  767 | SCORE += 3;
  768 | return;
  769 | }
  770 | }
  771 | }
  772 | }
  773 | else if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_HOUDEN)
  774 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_PARABORATYAAZI)){
  775 | if( Last_Attack_Waza != WAZANO_MAMORU
  776 | && Last_Attack_Waza != WAZANO_MIKIRI
  777 | && Last_Attack_Waza != WAZANO_KINGUSIIRUDO
  778 | && Last_Attack_Waza != WAZANO_NIIDORUGAADO
  779 | && Last_Attack_Waza != WAZANO_TATAMIGAESI
  780 | && Last_Attack_Waza != WAZANO_WAIDOGAADO
  781 | && Last_Attack_Waza != WAZANO_FASUTOGAADO){
  782 | if( Atk_Tokusei != TOKUSEI_HIRAISIN
  783 | || Atk_Tokusei != TOKUSEI_TIKUDEN
  784 | || Atk_Tokusei != TOKUSEI_DENKIENZIN
  785 | || Atk_Tokusei != TOKUSEI_TEREPASII
  786 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_FRIEND_TYPE1) != POKETYPE_JIMEN
  787 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_FRIEND_TYPE2) != POKETYPE_JIMEN){
  789 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  790 | SCORE += 3;
  791 | }
  792 | return;
  793 | }
  794 | if( Frd_Tokusei == TOKUSEI_KATAYABURI
  795 | || Frd_Tokusei == TOKUSEI_TERABORUTEEZI
  796 | || Frd_Tokusei == TOKUSEI_TAABOBUREIZU ){
  798 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  799 | SCORE += 3;
  800 | return;
  801 | }
  802 | }
  803 | }
  804 | }
  805 | else if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_HUNEN)
  806 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_KAENDAN)){
  807 | if( Last_Attack_Waza != WAZANO_MAMORU
  808 | && Last_Attack_Waza != WAZANO_MIKIRI
  809 | && Last_Attack_Waza != WAZANO_KINGUSIIRUDO
  810 | && Last_Attack_Waza != WAZANO_NIIDORUGAADO
  811 | && Last_Attack_Waza != WAZANO_TATAMIGAESI
  812 | && Last_Attack_Waza != WAZANO_WAIDOGAADO
  813 | && Last_Attack_Waza != WAZANO_FASUTOGAADO){
  814 | if( Atk_Tokusei != TOKUSEI_MORAIBI
  815 | || Atk_Tokusei != TOKUSEI_TEREPASII){
  817 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  818 | SCORE += 3;
  819 | }
  820 | return;
  821 | }
  822 | if( Frd_Tokusei == TOKUSEI_KATAYABURI
  823 | || Frd_Tokusei == TOKUSEI_TERABORUTEEZI
  824 | || Frd_Tokusei == TOKUSEI_TAABOBUREIZU ){
  826 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  827 | SCORE += 3;
  828 | return;
  829 | }
  830 | }
  831 | }
  832 | }
  833 | else if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_HANAHUBUKI)){
  834 | if( Last_Attack_Waza != WAZANO_MAMORU
  835 | && Last_Attack_Waza != WAZANO_MIKIRI
  836 | && Last_Attack_Waza != WAZANO_KINGUSIIRUDO
  837 | && Last_Attack_Waza != WAZANO_NIIDORUGAADO
  838 | && Last_Attack_Waza != WAZANO_TATAMIGAESI
  839 | && Last_Attack_Waza != WAZANO_WAIDOGAADO
  840 | && Last_Attack_Waza != WAZANO_FASUTOGAADO){
  841 | if( Atk_Tokusei != TOKUSEI_SOUSYOKU
  842 | || Atk_Tokusei != TOKUSEI_TEREPASII){
  844 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  845 | SCORE += 3;
  846 | }
  847 | return;
  848 | }
  849 | if( Frd_Tokusei == TOKUSEI_KATAYABURI
  850 | || Frd_Tokusei == TOKUSEI_TERABORUTEEZI
  851 | || Frd_Tokusei == TOKUSEI_TAABOBUREIZU ){
  853 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  854 | SCORE += 3;
  855 | return;
  856 | }
  857 | }
  858 | }
  859 | }
  860 | else if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_HEDOROWHEEBU)){
  861 | if( Last_Attack_Waza != WAZANO_MAMORU
  862 | && Last_Attack_Waza != WAZANO_MIKIRI
  863 | && Last_Attack_Waza != WAZANO_KINGUSIIRUDO
  864 | && Last_Attack_Waza != WAZANO_NIIDORUGAADO
  865 | && Last_Attack_Waza != WAZANO_TATAMIGAESI
  866 | && Last_Attack_Waza != WAZANO_WAIDOGAADO
  867 | && Last_Attack_Waza != WAZANO_FASUTOGAADO){
  868 | if( Atk_Tokusei != TOKUSEI_TEREPASII){
  870 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  871 | SCORE += 3;
  872 | }
  873 | return;
  874 | }
  875 | if( Frd_Tokusei == TOKUSEI_KATAYABURI
  876 | || Frd_Tokusei == TOKUSEI_TERABORUTEEZI
  877 | || Frd_Tokusei == TOKUSEI_TAABOBUREIZU ){
  879 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  880 | SCORE += 3;
  881 | return;
  882 | }
  883 | }
  884 | }
  885 | }
  886 | else if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_BAKUONPA)){
  887 | if( Last_Attack_Waza != WAZANO_MAMORU
  888 | && Last_Attack_Waza != WAZANO_MIKIRI
  889 | && Last_Attack_Waza != WAZANO_KINGUSIIRUDO
  890 | && Last_Attack_Waza != WAZANO_NIIDORUGAADO
  891 | && Last_Attack_Waza != WAZANO_TATAMIGAESI
  892 | && Last_Attack_Waza != WAZANO_WAIDOGAADO
  893 | && Last_Attack_Waza != WAZANO_FASUTOGAADO){
  894 | if( Atk_Tokusei != TOKUSEI_TEREPASII){
  896 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  897 | SCORE += 3;
  898 | }
  899 | return;
  900 | }
  901 | if( Frd_Tokusei == TOKUSEI_KATAYABURI
  902 | || Frd_Tokusei == TOKUSEI_TERABORUTEEZI
  903 | || Frd_Tokusei == TOKUSEI_TAABOBUREIZU ){
  905 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
  906 | SCORE += 3;
  907 | return;
  908 | }
  909 | }
  910 | }
  911 | }
  912 | else if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_IBARU)){
  913 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_ATTACK) == BTL_SIDEEFF_SINPINOMAMORI
  914 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_KIINOMI)
  915 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK, ITEM_RAMUNOMI)
  916 | || AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_MAIPEESU){
  917 | if( AI_CMD(CMD_IF_DMG_PHYSIC_OVER, CHECK_ATTACK)){
  918 | if (AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK_FRIEND, 70)){
  920 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 100)){
  921 | SCORE += -2;
  922 | return;
  923 | }
  924 | }
  925 | }
  926 | }
  927 | }
  928 | }
```

### `DoubleAI_Enemy_Seq_147()` (source lines 930–1043)

```text
  930 | DoubleAI_Enemy_Seq_147()
  931 | {
  933 | Frd_Type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE1);
  934 | Frd_Type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE2);
  935 | Frd_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK_FRIEND);
  936 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
  937 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
  938 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
  939 | if( AI_CMD(CMD_IFN_WAZASICK, CHECK_ATTACK_FRIEND, WAZASICK_FLYING)
  940 | && Frd_Type1 != POKETYPE_HIKOU
  941 | && Frd_Type2 != POKETYPE_HIKOU
  942 | && Frd_Tokusei != TOKUSEI_HUYUU
  943 | && Frd_Tokusei != TOKUSEI_TEREPASII){
  944 | if( Frd_Type1 == POKETYPE_DENKI
  945 | || Frd_Type2 == POKETYPE_DENKI
  946 | || Frd_Type1 == POKETYPE_HAGANE
  947 | || Frd_Type2 == POKETYPE_HAGANE
  948 | || Frd_Type1 == POKETYPE_DOKU
  949 | || Frd_Type2 == POKETYPE_DOKU
  950 | || Frd_Type1 == POKETYPE_HONOO
  951 | || Frd_Type2 == POKETYPE_HONOO
  952 | || Frd_Type1 == POKETYPE_IWA
  953 | || Frd_Type2 == POKETYPE_IWA){
  955 | SCORE += -3;
  956 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
  957 | SCORE += -5;
  958 | }
  959 | }
  960 | }
  961 | return;
  962 | }
  963 | if( AI_CMD(CMD_IF_WAZASICK, CHECK_ATTACK_FRIEND, WAZASICK_FLYING)
  964 | || Frd_Type1 == POKETYPE_HIKOU
  965 | || Frd_Type2 == POKETYPE_HIKOU){
  966 | if( AI_CMD(CMD_FLDEFF_CHECK, EFF_JURYOKU)){
  968 | }
  969 | else{
  971 | if (AI_CMD(CMD_IF_RND_OVER, 160)){
  972 | SCORE += 3;
  973 | }
  974 | return;
  975 | }
  976 | }
  977 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK_FRIEND) == TOKUSEI_HUYUU
  978 | || AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK_FRIEND) == TOKUSEI_TEREPASII){
  979 | Atk_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
  980 | if( Atk_Tokusei != TOKUSEI_KATAYABURI
  981 | && Atk_Tokusei != TOKUSEI_TERABORUTEEZI
  982 | && Atk_Tokusei != TOKUSEI_TAABOBUREIZU){
  984 | if (AI_CMD(CMD_IF_RND_UNDER, 160)){
  985 | SCORE += 3;
  986 | }
  987 | return;
  988 | }
  989 | }
  990 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_MAMORU)
  991 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_MIKIRI)
  992 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_KINGUSIIRUDO)
  993 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_NIIDORUGAADO)
  994 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_TATAMIGAESI)
  995 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_WAIDOGAADO)){
  996 | Last_Frend_Waza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_ATTACK_FRIEND);
  997 | if( Last_Frend_Waza != WAZANO_MAMORU
  998 | && Last_Frend_Waza != WAZANO_MIKIRI
  999 | && Last_Frend_Waza != WAZANO_KINGUSIIRUDO
 1000 | && Last_Frend_Waza != WAZANO_NIIDORUGAADO
 1001 | && Last_Frend_Waza != WAZANO_TATAMIGAESI
 1002 | && Last_Frend_Waza != WAZANO_WAIDOGAADO
 1003 | && Last_Frend_Waza != WAZANO_FASUTOGAADO){
 1005 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
 1006 | SCORE += 2;
 1007 | return;
 1008 | }
 1009 | }
 1010 | }
 1011 | if( Frd_Type1 == POKETYPE_DENKI
 1012 | || Frd_Type2 == POKETYPE_DENKI
 1013 | || Frd_Type1 == POKETYPE_HAGANE
 1014 | || Frd_Type2 == POKETYPE_HAGANE
 1015 | || Frd_Type1 == POKETYPE_DOKU
 1016 | || Frd_Type2 == POKETYPE_DOKU
 1017 | || Frd_Type1 == POKETYPE_HONOO
 1018 | || Frd_Type2 == POKETYPE_HONOO
 1019 | || Frd_Type1 == POKETYPE_IWA
 1020 | || Frd_Type2 == POKETYPE_IWA){
 1022 | SCORE += -3;
 1023 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1024 | SCORE += -5;
 1025 | }
 1026 | }
 1027 | if( Frd_Type1 != POKETYPE_MUSHI
 1028 | || Frd_Type2 != POKETYPE_MUSHI
 1029 | || Frd_Type1 != POKETYPE_KUSA
 1030 | || Frd_Type2 != POKETYPE_KUSA){
 1032 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
 1033 | SCORE += 2;
 1034 | return;
 1035 | }
 1036 | }
 1037 | else{
 1039 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 1040 | SCORE += -1;
 1041 | }
 1042 | }
 1043 | }
```

### `DoubleAI_Enemy_Seq_170()` (source lines 1045–1065)

```text
 1045 | DoubleAI_Enemy_Seq_170()
 1046 | {
 1048 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_KONOYUBITOMARE)){
 1050 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 180)){
 1051 | SCORE += 3;
 1052 | return;
 1053 | }
 1054 | }
 1055 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_OSAKINIDOUZO)
 1056 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_SAKIOKURI)){
 1057 | if (AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK_FRIEND) == 0){
 1059 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 180)){
 1060 | SCORE += 3;
 1061 | return;
 1062 | }
 1063 | }
 1064 | }
 1065 | }
```

### `DoubleAI_Enemy_Seq_172()` (source lines 1067–1144)

```text
 1067 | DoubleAI_Enemy_Seq_172()
 1068 | {
 1070 | if( AI_CMD(CMD_IF_HAVE_WAZA_SEQNO, CHECK_ATTACK_FRIEND, 172)){
 1072 | if( AI_CMD(CMD_CHECK_MONSNO, CHECK_ATTACK) > AI_CMD(CMD_CHECK_MONSNO, CHECK_ATTACK_FRIEND)){
 1073 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 128)){
 1075 | SCORE += - 5;
 1076 | return;
 1077 | }
 1078 | }
 1079 | else{
 1080 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 127)){
 1082 | SCORE += - 5;
 1083 | return;
 1084 | }
 1085 | }
 1086 | }
 1087 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_TORIKKURUUMU)){
 1088 | if( AI_CMD(CMD_FLDEFF_CHECK, EFF_TRICKROOM)){
 1089 | }
 1090 | else{
 1092 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 240)){
 1093 | SCORE += 3;
 1094 | return;
 1095 | }
 1096 | }
 1097 | }
 1098 | else if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_OIKAZE)){
 1099 | if( AI_CMD(CMD_IFN_SIDEEFF, CHECK_ATTACK, BTL_SIDEEFF_OIKAZE)){
 1100 | if (AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK_FRIEND) != 0
 1101 | && AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) != TOKUSEI_ITAZURAGOKORO){
 1103 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 240)){
 1104 | SCORE += 3;
 1105 | return;
 1106 | }
 1107 | }
 1108 | }
 1109 | }
 1110 | else if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_HUNKA)
 1111 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_SIOHUKI)){
 1112 | if (AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK_FRIEND) != 0){
 1113 | if (AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK_FRIEND, 70)){
 1115 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 180)){
 1116 | SCORE += 3;
 1117 | return;
 1118 | }
 1119 | }
 1120 | }
 1121 | }
 1122 | else if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_KIAIPANTI)){
 1124 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 180)){
 1125 | SCORE += 3;
 1126 | return;
 1127 | }
 1128 | }
 1129 | else if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_KARAWOYABURU)
 1130 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_RYUUNOMAI)
 1131 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_TYOUNOMAI)
 1132 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_KOUSOKUIDOU)
 1133 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_ROKKUKATTO)
 1134 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_BODHIPAAZI)
 1135 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_GIATHENZI)){
 1136 | if (AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK_FRIEND) != 0){
 1138 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 180)){
 1139 | SCORE += 3;
 1140 | return;
 1141 | }
 1142 | }
 1143 | }
 1144 | }
```

### `DoubleAI_Enemy_Seq_190()` (source lines 1146–1174)

```text
 1146 | DoubleAI_Enemy_Seq_190()
 1147 | {
 1149 | if (AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 70)){
 1150 | SCORE += -2;
 1151 | return;
 1152 | }
 1153 | if (AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK) == 0){
 1154 | SCORE += 3;
 1155 | return;
 1156 | }
 1157 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_OSAKINIDOUZO)
 1158 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_SAKIOKURI)){
 1159 | if (AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK_FRIEND) == 0){
 1161 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 128)){
 1162 | SCORE += 3;
 1163 | return;
 1164 | }
 1165 | }
 1166 | }
 1167 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_KONOYUBITOMARE)){
 1169 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 180)){
 1170 | SCORE += 3;
 1171 | return;
 1172 | }
 1173 | }
 1174 | }
```

### `DoubleAI_Enemy_Seq_257()` (source lines 1176–1268)

```text
 1176 | DoubleAI_Enemy_Seq_257()
 1177 | {
 1179 | Frd_Type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE1);
 1180 | Frd_Type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE2);
 1181 | Frd_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK_FRIEND);
 1182 | Atk_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1183 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 1184 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 1185 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 1186 | if( Frd_Tokusei != TOKUSEI_TYOSUI
 1187 | && Frd_Tokusei != TOKUSEI_YOBIMIZU
 1188 | && Frd_Tokusei != TOKUSEI_KANSOUHADA
 1189 | && Frd_Tokusei != TOKUSEI_TEREPASII){
 1190 | if( Frd_Type1 == POKETYPE_JIMEN
 1191 | || Frd_Type2 == POKETYPE_JIMEN
 1192 | || Frd_Type1 == POKETYPE_HONOO
 1193 | || Frd_Type2 == POKETYPE_HONOO
 1194 | || Frd_Type1 == POKETYPE_IWA
 1195 | || Frd_Type2 == POKETYPE_IWA){
 1197 | SCORE += -3;
 1198 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1199 | SCORE += -5;
 1200 | }
 1201 | }
 1202 | }
 1203 | return;
 1204 | }
 1205 | if( Frd_Tokusei == TOKUSEI_TYOSUI
 1206 | || Frd_Tokusei == TOKUSEI_YOBIMIZU
 1207 | || Frd_Tokusei == TOKUSEI_KANSOUHADA
 1208 | || Frd_Tokusei == TOKUSEI_TEREPASII){
 1209 | if( Atk_Tokusei != TOKUSEI_KATAYABURI
 1210 | && Atk_Tokusei != TOKUSEI_TERABORUTEEZI
 1211 | && Atk_Tokusei != TOKUSEI_TAABOBUREIZU){
 1213 | if (AI_CMD(CMD_IF_RND_UNDER, 160)){
 1214 | SCORE += 3;
 1215 | }
 1216 | return;
 1217 | }
 1218 | }
 1219 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_MAMORU)
 1220 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_MIKIRI)
 1221 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_KINGUSIIRUDO)
 1222 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_NIIDORUGAADO)
 1223 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_TATAMIGAESI)
 1224 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_WAIDOGAADO)){
 1225 | Last_Frend_Waza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_ATTACK_FRIEND);
 1226 | if( Last_Frend_Waza != WAZANO_MAMORU
 1227 | && Last_Frend_Waza != WAZANO_MIKIRI
 1228 | && Last_Frend_Waza != WAZANO_KINGUSIIRUDO
 1229 | && Last_Frend_Waza != WAZANO_NIIDORUGAADO
 1230 | && Last_Frend_Waza != WAZANO_TATAMIGAESI
 1231 | && Last_Frend_Waza != WAZANO_WAIDOGAADO
 1232 | && Last_Frend_Waza != WAZANO_FASUTOGAADO){
 1234 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
 1235 | SCORE += 2;
 1236 | return;
 1237 | }
 1238 | }
 1239 | }
 1240 | if( Frd_Type1 == POKETYPE_JIMEN
 1241 | || Frd_Type2 == POKETYPE_JIMEN
 1242 | || Frd_Type1 == POKETYPE_HONOO
 1243 | || Frd_Type2 == POKETYPE_HONOO
 1244 | || Frd_Type1 == POKETYPE_IWA
 1245 | || Frd_Type2 == POKETYPE_IWA){
 1247 | SCORE += -3;
 1248 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1249 | SCORE += -5;
 1250 | }
 1251 | }
 1252 | if( Frd_Type1 != POKETYPE_MUSHI
 1253 | || Frd_Type2 != POKETYPE_MUSHI
 1254 | || Frd_Type1 != POKETYPE_KUSA
 1255 | || Frd_Type2 != POKETYPE_KUSA){
 1257 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
 1258 | SCORE += 2;
 1259 | return;
 1260 | }
 1261 | }
 1262 | else{
 1264 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 1265 | SCORE += -1;
 1266 | }
 1267 | }
 1268 | }
```

### `DoubleAI_Enemy_Seq_259()` (source lines 1270–1348)

```text
 1270 | DoubleAI_Enemy_Seq_259()
 1271 | {
 1273 | Atk_Agi_Rank = AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK);
 1274 | Frd_Agi_Rank = AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK_FRIEND);
 1276 | if (Atk_Agi_Rank == 0){
 1277 | if (Frd_Agi_Rank == 0){
 1278 | SCORE += -2;
 1279 | return;
 1280 | }
 1281 | if (Frd_Agi_Rank == 1){
 1282 | SCORE += -2;
 1283 | return;
 1284 | }
 1285 | if (Frd_Agi_Rank == 2){
 1286 | SCORE += -1;
 1287 | return;
 1288 | }
 1289 | if (Frd_Agi_Rank == 3){
 1290 | SCORE += -1;
 1291 | return;
 1292 | }
 1293 | }
 1294 | if (Atk_Agi_Rank == 1){
 1295 | if (Frd_Agi_Rank == 0){
 1296 | SCORE += -2;
 1297 | return;
 1298 | }
 1299 | if (Frd_Agi_Rank == 1){
 1300 | SCORE += -1;
 1301 | return;
 1302 | }
 1303 | if (Frd_Agi_Rank == 2){
 1304 | SCORE += -1;
 1305 | return;
 1306 | }
 1307 | if (Frd_Agi_Rank == 3){
 1308 | DoubleAI_Enemy_Seq_259_sub( 2 );
 1309 | return;
 1310 | }
 1311 | }
 1312 | if (Atk_Agi_Rank == 2){
 1313 | if (Frd_Agi_Rank == 0){
 1314 | SCORE += -2;
 1315 | return;
 1316 | }
 1317 | if (Frd_Agi_Rank == 1){
 1318 | SCORE += -1;
 1319 | return;
 1320 | }
 1321 | if (Frd_Agi_Rank == 2){
 1322 | DoubleAI_Enemy_Seq_259_sub( 3 );
 1323 | return;
 1324 | }
 1325 | if (Frd_Agi_Rank == 3){
 1326 | DoubleAI_Enemy_Seq_259_sub( 3 );
 1327 | return;
 1328 | }
 1329 | }
 1330 | if (Atk_Agi_Rank == 3){
 1331 | if (Frd_Agi_Rank == 0){
 1332 | SCORE += -1;
 1333 | return;
 1334 | }
 1335 | if (Frd_Agi_Rank == 1){
 1336 | DoubleAI_Enemy_Seq_259_sub( 2 );
 1337 | return;
 1338 | }
 1339 | if (Frd_Agi_Rank == 2){
 1340 | DoubleAI_Enemy_Seq_259_sub( 3 );
 1341 | return;
 1342 | }
 1343 | if (Frd_Agi_Rank == 3){
 1344 | DoubleAI_Enemy_Seq_259_sub( 3 );
 1345 | return;
 1346 | }
 1347 | }
 1348 | }
```

### `DoubleAI_Enemy_Seq_259_sub(value)` (source lines 1349–1399)

```text
 1349 | DoubleAI_Enemy_Seq_259_sub( value )
 1350 | {
 1351 | Atk_Agi_Rank = AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK);
 1352 | Frd_Agi_Rank = AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK_FRIEND);
 1354 | if(AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_TORIKKURUUMU)){
 1355 | if (Atk_Agi_Rank == 3){
 1356 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 150)){
 1357 | SCORE += value;
 1358 | return;
 1359 | }
 1360 | else{
 1361 | SCORE += - 5;
 1362 | return;
 1363 | }
 1364 | }
 1365 | else{
 1366 | if(Frd_Agi_Rank == Atk_Agi_Rank){
 1367 | if( AI_CMD(CMD_CHECK_MONSNO, CHECK_ATTACK) > AI_CMD(CMD_CHECK_MONSNO, CHECK_ATTACK_FRIEND)){
 1368 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 128)){
 1369 | SCORE += - 5;
 1370 | return;
 1371 | }
 1372 | else{
 1373 | SCORE += value;
 1374 | return;
 1375 | }
 1376 | }
 1377 | else{
 1378 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 128)){
 1379 | SCORE += value;
 1380 | return;
 1381 | }
 1382 | else{
 1383 | SCORE += - 5;
 1384 | return;
 1385 | }
 1386 | }
 1387 | }
 1388 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 150)){
 1389 | SCORE += - 5;
 1390 | return;
 1391 | }
 1392 | else{
 1393 | SCORE += value;
 1394 | return;
 1395 | }
 1396 | }
 1397 | }
 1398 | SCORE += value;
 1399 | }
```

### `DoubleAI_Enemy_Seq_278()` (source lines 1401–1478)

```text
 1401 | DoubleAI_Enemy_Seq_278()
 1402 | {
 1404 | DefMonsNo = AI_CMD(CMD_CHECK_MONSNO, CHECK_DEFENCE);
 1405 | if( DefMonsNo == MONSNO_BAKUHUUN || DefMonsNo == MONSNO_TORITODON
 1406 | || DefMonsNo == MONSNO_KAIOOGA || DefMonsNo == MONSNO_PUTERA
 1407 | || DefMonsNo == MONSNO_KINGUDORA || DefMonsNo == MONSNO_GABURIASU
 1408 | || DefMonsNo == MONSNO_TERAKION || DefMonsNo == MONSNO_YUKINOOO
 1409 | || DefMonsNo == MONSNO_GUREISIA || DefMonsNo == MONSNO_SYANDERA
 1411 | || DefMonsNo == MONSNO_BANGIRASU || DefMonsNo == MONSNO_HIIDORAN
 1412 | || DefMonsNo == MONSNO_DORYUUZU || DefMonsNo == MONSNO_BURUNGERU
 1413 | || DefMonsNo == MONSNO_ONONOKUSU || DefMonsNo == MONSNO_URUGAMOSU
 1414 | || DefMonsNo == MONSNO_KYUREMU ){
 1416 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 128)){
 1417 | SCORE += 2;
 1418 | return;
 1419 | }
 1420 | }
 1421 | Last_Def_Waza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_DEFENCE);
 1422 | Last_DefFrd_Waza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_DEFENCE_FRIEND);
 1423 | if( Last_Def_Waza == WAZANO_HUBUKI
 1424 | || Last_DefFrd_Waza == WAZANO_HUBUKI
 1425 | || Last_Def_Waza == WAZANO_NAMINORI
 1426 | || Last_DefFrd_Waza == WAZANO_NAMINORI
 1427 | || Last_Def_Waza == WAZANO_ZISIN
 1428 | || Last_DefFrd_Waza == WAZANO_ZISIN
 1429 | || Last_Def_Waza == WAZANO_IWANADARE
 1430 | || Last_DefFrd_Waza == WAZANO_IWANADARE
 1431 | || Last_Def_Waza == WAZANO_NEPPUU
 1432 | || Last_DefFrd_Waza == WAZANO_NEPPUU
 1433 | || Last_Def_Waza == WAZANO_HAIPAABOISU
 1434 | || Last_DefFrd_Waza == WAZANO_HAIPAABOISU
 1435 | || Last_Def_Waza == WAZANO_SIOHUKI
 1436 | || Last_DefFrd_Waza == WAZANO_SIOHUKI
 1437 | || Last_Def_Waza == WAZANO_DAKURYUU
 1438 | || Last_DefFrd_Waza == WAZANO_DAKURYUU
 1439 | || Last_Def_Waza == WAZANO_HOUDEN
 1440 | || Last_DefFrd_Waza == WAZANO_HOUDEN
 1441 | || Last_Def_Waza == WAZANO_HUNEN
 1442 | || Last_DefFrd_Waza == WAZANO_HUNEN
 1443 | || Last_Def_Waza == WAZANO_HEDOROWHEEBU
 1444 | || Last_DefFrd_Waza == WAZANO_HEDOROWHEEBU
 1445 | || Last_Def_Waza == WAZANO_SINKURONOIZU
 1446 | || Last_DefFrd_Waza == WAZANO_SINKURONOIZU
 1447 | || Last_Def_Waza == WAZANO_KAENDAN
 1448 | || Last_DefFrd_Waza == WAZANO_KAENDAN
 1449 | || Last_Def_Waza == WAZANO_INISIENOUTA
 1450 | || Last_DefFrd_Waza == WAZANO_INISIENOUTA
 1451 | || Last_Def_Waza == WAZANO_KOGOERUSEKAI
 1452 | || Last_DefFrd_Waza == WAZANO_KOGOERUSEKAI
 1453 | || Last_Def_Waza == WAZANO_BAAKUAUTO
 1454 | || Last_DefFrd_Waza == WAZANO_BAAKUAUTO
 1455 | || Last_Def_Waza == WAZANO_PARABORATYAAZI
 1456 | || Last_DefFrd_Waza == WAZANO_PARABORATYAAZI
 1457 | || Last_Def_Waza == WAZANO_HANAHUBUKI
 1458 | || Last_DefFrd_Waza == WAZANO_HANAHUBUKI
 1459 | || Last_Def_Waza == WAZANO_BAKUONPA
 1460 | || Last_DefFrd_Waza == WAZANO_BAKUONPA
 1461 | || Last_Def_Waza == WAZANO_DAIYASUTOOMU
 1462 | || Last_DefFrd_Waza == WAZANO_DAIYASUTOOMU
 1463 | || Last_Def_Waza == WAZANO_MAZIKARUSYAIN
 1464 | || Last_DefFrd_Waza == WAZANO_MAZIKARUSYAIN
 1465 | || Last_Def_Waza == WAZANO_SAUZANAROO
 1466 | || Last_DefFrd_Waza == WAZANO_SAUZANAROO
 1467 | || Last_Def_Waza == WAZANO_SAUZANWHEEBU
 1468 | || Last_DefFrd_Waza == WAZANO_SAUZANWHEEBU
 1469 | || Last_Def_Waza == WAZANO_GURANDOFOOSU
 1470 | || Last_DefFrd_Waza == WAZANO_GURANDOFOOSU){
 1472 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 128)){
 1473 | SCORE += 2;
 1474 | return;
 1475 | }
 1476 | }
 1477 | DoubleAI_Enemy_Seq_111()
 1478 | }
```

### `DoubleAI_Enemy_Seq_292()` (source lines 1480–1509)

```text
 1480 | DoubleAI_Enemy_Seq_292()
 1481 | {
 1483 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 1484 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 1485 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 1486 | return;
 1487 | }
 1488 | ATK_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE1);
 1489 | ATK_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE2);
 1490 | DEF_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1);
 1491 | DEF_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2);
 1492 | DEFFRD_type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_FRIEND_TYPE1);
 1493 | DEFFRD_type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_FRIEND_TYPE2);
 1494 | if(ATK_type1 == DEF_type1
 1495 | || ATK_type1 == DEF_type2
 1496 | || ATK_type2 == DEF_type1
 1497 | || ATK_type2 == DEF_type2){
 1498 | if(ATK_type1 == DEFFRD_type1
 1499 | || ATK_type1 == DEFFRD_type2
 1500 | || ATK_type2 == DEFFRD_type1
 1501 | || ATK_type2 == DEFFRD_type2){
 1503 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 128)){
 1504 | SCORE += 2;
 1505 | return;
 1506 | }
 1507 | }
 1508 | }
 1509 | }
```

### `DoubleAI_Enemy_Seq_301()` (source lines 1511–1525)

```text
 1511 | DoubleAI_Enemy_Seq_301()
 1512 | {
 1514 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 1515 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 1516 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 1517 | return;
 1518 | }
 1519 | if(AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_RINSYOU)){
 1520 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 128)){
 1521 | SCORE += 3;
 1522 | return;
 1523 | }
 1524 | }
 1525 | }
```

### `DoubleAI_Enemy_Seq_307()` (source lines 1527–1636)

```text
 1527 | DoubleAI_Enemy_Seq_307()
 1528 | {
 1530 | Atk_Type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE1);
 1531 | Atk_Type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_TYPE2);
 1532 | AtkFrd_Type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE1);
 1533 | AtkFrd_Type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE2);
 1534 | Def_Type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1);
 1535 | Def_Type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2);
 1536 | DefFrd_Type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_FRIEND_TYPE1);
 1537 | DefFrd_Type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_FRIEND_TYPE2);
 1540 | if( Atk_Type1 == POKETYPE_ESPER
 1541 | || Atk_Type2 == POKETYPE_ESPER ){
 1542 | if( AtkFrd_Type1 == POKETYPE_NORMAL
 1543 | || AtkFrd_Type2 == POKETYPE_NORMAL
 1544 | || AtkFrd_Type1 == POKETYPE_IWA
 1545 | || AtkFrd_Type2 == POKETYPE_IWA
 1546 | || AtkFrd_Type1 == POKETYPE_AKU
 1547 | || AtkFrd_Type2 == POKETYPE_AKU
 1548 | || AtkFrd_Type1 == POKETYPE_HAGANE
 1549 | || AtkFrd_Type2 == POKETYPE_HAGANE
 1550 | || AtkFrd_Type1 == POKETYPE_KOORI
 1551 | || AtkFrd_Type2 == POKETYPE_KOORI){
 1552 | if( Def_Type1 == POKETYPE_KAKUTOU
 1553 | || Def_Type2 == POKETYPE_KAKUTOU
 1554 | || DefFrd_Type1 == POKETYPE_KAKUTOU
 1555 | || DefFrd_Type2 == POKETYPE_KAKUTOU){
 1557 | if (AI_CMD(CMD_IF_RND_UNDER, 70)){
 1558 | SCORE += 2;
 1559 | return;
 1560 | }
 1561 | }
 1562 | }
 1563 | if( AtkFrd_Type1 == POKETYPE_DOKU
 1564 | || AtkFrd_Type2 == POKETYPE_DOKU
 1565 | || AtkFrd_Type1 == POKETYPE_KAKUTOU
 1566 | || AtkFrd_Type2 == POKETYPE_KAKUTOU ){
 1567 | if( Def_Type1 == POKETYPE_ESPER
 1568 | || Def_Type2 == POKETYPE_ESPER
 1569 | || DefFrd_Type1 == POKETYPE_ESPER
 1570 | || DefFrd_Type2 == POKETYPE_ESPER){
 1572 | if (AI_CMD(CMD_IF_RND_UNDER, 70)){
 1573 | SCORE += 2;
 1574 | return;
 1575 | }
 1576 | }
 1577 | }
 1578 | if( Def_Type1 == POKETYPE_AKU
 1579 | || Def_Type2 == POKETYPE_AKU
 1580 | || DefFrd_Type1 == POKETYPE_AKU
 1581 | || DefFrd_Type2 == POKETYPE_AKU ){
 1582 | if( AtkFrd_Type1 == POKETYPE_KAKUTOU
 1583 | || AtkFrd_Type2 == POKETYPE_KAKUTOU
 1584 | || AtkFrd_Type1 == POKETYPE_AKU
 1585 | || AtkFrd_Type2 == POKETYPE_AKU
 1586 | || AtkFrd_Type2 == POKETYPE_HAGANE
 1587 | || AtkFrd_Type2 == POKETYPE_HAGANE){
 1589 | if (AI_CMD(CMD_IF_RND_UNDER, 70)){
 1590 | SCORE += 2;
 1591 | return;
 1592 | }
 1593 | }
 1594 | }
 1595 | if( Def_Type1 == POKETYPE_MUSHI
 1596 | || Def_Type2 == POKETYPE_MUSHI
 1597 | || DefFrd_Type1 == POKETYPE_MUSHI
 1598 | || DefFrd_Type2 == POKETYPE_MUSHI ){
 1599 | if( AtkFrd_Type1 == POKETYPE_HONOO
 1600 | || AtkFrd_Type2 == POKETYPE_HONOO
 1601 | || AtkFrd_Type1 == POKETYPE_KAKUTOU
 1602 | || AtkFrd_Type2 == POKETYPE_KAKUTOU
 1603 | || AtkFrd_Type1 == POKETYPE_DOKU
 1604 | || AtkFrd_Type2 == POKETYPE_DOKU
 1605 | || AtkFrd_Type1 == POKETYPE_HIKOU
 1606 | || AtkFrd_Type2 == POKETYPE_HIKOU
 1607 | || AtkFrd_Type1 == POKETYPE_GHOST
 1608 | || AtkFrd_Type2 == POKETYPE_GHOST
 1609 | || AtkFrd_Type2 == POKETYPE_HAGANE
 1610 | || AtkFrd_Type2 == POKETYPE_HAGANE){
 1612 | if (AI_CMD(CMD_IF_RND_UNDER, 70)){
 1613 | SCORE += 2;
 1614 | return;
 1615 | }
 1616 | }
 1617 | }
 1618 | if( Def_Type1 == POKETYPE_GHOST
 1619 | || Def_Type2 == POKETYPE_GHOST
 1620 | || DefFrd_Type1 == POKETYPE_GHOST
 1621 | || DefFrd_Type2 == POKETYPE_GHOST ){
 1622 | if( AtkFrd_Type1 == POKETYPE_NORMAL
 1623 | || AtkFrd_Type2 == POKETYPE_NORMAL
 1624 | || AtkFrd_Type1 == POKETYPE_AKU
 1625 | || AtkFrd_Type2 == POKETYPE_AKU
 1626 | || AtkFrd_Type2 == POKETYPE_HAGANE
 1627 | || AtkFrd_Type2 == POKETYPE_HAGANE){
 1629 | if (AI_CMD(CMD_IF_RND_UNDER, 70)){
 1630 | SCORE += 2;
 1631 | return;
 1632 | }
 1633 | }
 1634 | }
 1635 | }
 1636 | }
```

### `DoubleAI_Enemy_Seq_313()` (source lines 1638–1641)

```text
 1638 | DoubleAI_Enemy_Seq_313()
 1639 | {
 1641 | }
```

### `DoubleAI_Enemy_Seq_315()` (source lines 1643–1676)

```text
 1643 | DoubleAI_Enemy_Seq_315()
 1644 | {
 1646 | if (AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK) == 0
 1647 | || AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_ITAZURAGOKORO){
 1648 | if (AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK_FRIEND) > 1){
 1649 | if (AI_CMD(CMD_CHECK_AGI_RANK, CHECK_DEFENCE) == 1){
 1650 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_HUNKA)
 1651 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_SIOHUKI)){
 1652 | if (AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK_FRIEND, 70)){
 1654 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 180)){
 1655 | SCORE += 3;
 1656 | return;
 1657 | }
 1658 | }
 1659 | }
 1661 | if (AI_CMD(CMD_IF_RND_UNDER, 180)){
 1662 | SCORE += 3;
 1663 | return;
 1664 | }
 1665 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_KIAIPANTI)){
 1667 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 180)){
 1668 | SCORE += 3;
 1669 | return;
 1670 | }
 1671 | }
 1672 | }
 1673 | }
 1674 | }
 1675 | SCORE += -8;
 1676 | }
```

### `DoubleAI_Enemy_Seq_339()` (source lines 1678–1694)

```text
 1678 | DoubleAI_Enemy_Seq_339()
 1679 | {
 1681 | if( AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE1) == POKETYPE_KUSA
 1682 | || AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE2) == POKETYPE_KUSA){
 1683 | if( AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE1) != POKETYPE_KUSA
 1684 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_TYPE2) != POKETYPE_KUSA
 1685 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_FRIEND_TYPE1) != POKETYPE_KUSA
 1686 | || AI_CMD(CMD_CHECK_TYPE, CHECK_DEFENCE_FRIEND_TYPE2) != POKETYPE_KUSA){
 1688 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 128)){
 1689 | SCORE += 2;
 1690 | return;
 1691 | }
 1692 | }
 1693 | }
 1694 | }
```

### `DoubleAI_Enemy_Seq_350()` (source lines 1696–1707)

```text
 1696 | DoubleAI_Enemy_Seq_350()
 1697 | {
 1699 | if( AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE1) == POKETYPE_KUSA
 1700 | || AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE2) == POKETYPE_KUSA){
 1702 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 128)){
 1703 | SCORE += 2;
 1704 | return;
 1705 | }
 1706 | }
 1707 | }
```

### `DoubleAI_Enemy_Seq_non()` (source lines 1708–1712)

```text
 1708 | DoubleAI_Enemy_Seq_non()
 1709 | {
 1711 | SCORE += -12;
 1712 | }
```

### `DoubleAI_Enemy_Seq_378()` (source lines 1714–1848)

```text
 1714 | DoubleAI_Enemy_Seq_378()
 1715 | {
 1717 | wazaNo = CURRENT_MOVE();
 1718 | if( wazaNo != WAZANO_HANAHUBUKI
 1719 | && wazaNo != WAZANO_BAKUONPA ){
 1720 | return;
 1721 | }
 1722 | Frd_Type1 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE1);
 1723 | Frd_Type2 = AI_CMD(CMD_CHECK_TYPE, CHECK_ATTACK_FRIEND_TYPE2);
 1724 | Frd_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK_FRIEND);
 1725 | Atk_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK);
 1726 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_0BAI)
 1727 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_4BAI)
 1728 | || AI_CMD(CMD_CHECK_WAZA_AISYOU, CHECK_ATTACK, CHECK_DEFENCE, CURRENT_MOVE(), AISYOU_1_2BAI)){
 1729 | if( wazaNo == WAZANO_HANAHUBUKI){
 1730 | if( Frd_Tokusei != TOKUSEI_SOUSYOKU
 1731 | && Frd_Tokusei != TOKUSEI_TEREPASII){
 1732 | if( Frd_Type1 == POKETYPE_MIZU
 1733 | || Frd_Type2 == POKETYPE_MIZU
 1734 | || Frd_Type1 == POKETYPE_JIMEN
 1735 | || Frd_Type2 == POKETYPE_JIMEN
 1736 | || Frd_Type1 == POKETYPE_IWA
 1737 | || Frd_Type2 == POKETYPE_IWA){
 1739 | SCORE += -3;
 1740 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1741 | SCORE += -5;
 1742 | }
 1743 | }
 1744 | }
 1745 | }
 1746 | return;
 1747 | }
 1748 | if( wazaNo == WAZANO_HANAHUBUKI){
 1749 | if( Frd_Tokusei == TOKUSEI_SOUSYOKU
 1750 | || Frd_Tokusei == TOKUSEI_TEREPASII){
 1751 | if( Atk_Tokusei != TOKUSEI_KATAYABURI
 1752 | && Atk_Tokusei != TOKUSEI_TERABORUTEEZI
 1753 | && Atk_Tokusei != TOKUSEI_TAABOBUREIZU){
 1755 | if (AI_CMD(CMD_IF_RND_UNDER, 160)){
 1756 | SCORE += 3;
 1757 | }
 1758 | return;
 1759 | }
 1760 | }
 1761 | }
 1762 | else if( wazaNo == WAZANO_BAKUONPA){
 1763 | if( Frd_Tokusei == TOKUSEI_TEREPASII){
 1764 | if( Atk_Tokusei != TOKUSEI_KATAYABURI
 1765 | && Atk_Tokusei != TOKUSEI_TERABORUTEEZI
 1766 | && Atk_Tokusei != TOKUSEI_TAABOBUREIZU){
 1768 | if (AI_CMD(CMD_IF_RND_UNDER, 160)){
 1769 | SCORE += 3;
 1770 | }
 1771 | return;
 1772 | }
 1773 | }
 1774 | }
 1775 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_MAMORU)
 1776 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_MIKIRI)
 1777 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_KINGUSIIRUDO)
 1778 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_NIIDORUGAADO)
 1779 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_TATAMIGAESI)
 1780 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_WAIDOGAADO)){
 1781 | Last_Frend_Waza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_ATTACK_FRIEND);
 1782 | if( Last_Frend_Waza != WAZANO_MAMORU
 1783 | && Last_Frend_Waza != WAZANO_MIKIRI
 1784 | && Last_Frend_Waza != WAZANO_KINGUSIIRUDO
 1785 | && Last_Frend_Waza != WAZANO_NIIDORUGAADO
 1786 | && Last_Frend_Waza != WAZANO_TATAMIGAESI
 1787 | && Last_Frend_Waza != WAZANO_WAIDOGAADO
 1788 | && Last_Frend_Waza != WAZANO_FASUTOGAADO){
 1790 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
 1791 | SCORE += 2;
 1792 | return;
 1793 | }
 1794 | }
 1795 | }
 1796 | if( wazaNo == WAZANO_HANAHUBUKI){
 1797 | if( Frd_Type1 == POKETYPE_MIZU
 1798 | || Frd_Type2 == POKETYPE_MIZU
 1799 | || Frd_Type1 == POKETYPE_JIMEN
 1800 | || Frd_Type2 == POKETYPE_JIMEN
 1801 | || Frd_Type1 == POKETYPE_IWA
 1802 | || Frd_Type2 == POKETYPE_IWA){
 1804 | SCORE += -3;
 1805 | if( AI_CMD(CMD_IF_RND_UNDER, 200) ){
 1806 | SCORE += -5;
 1807 | }
 1808 | }
 1809 | if( Frd_Type1 == POKETYPE_KUSA
 1810 | || Frd_Type2 == POKETYPE_KUSA
 1811 | || Frd_Type1 == POKETYPE_MIZU
 1812 | || Frd_Type2 == POKETYPE_MIZU
 1813 | || Frd_Type1 == POKETYPE_DRAGON
 1814 | || Frd_Type2 == POKETYPE_DRAGON){
 1816 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
 1817 | SCORE += 2;
 1818 | return;
 1819 | }
 1820 | }
 1821 | else{
 1823 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 1824 | SCORE += -1;
 1825 | }
 1826 | }
 1827 | }
 1828 | if( wazaNo == WAZANO_BAKUONPA){
 1829 | if( Frd_Type1 == POKETYPE_IWA
 1830 | || Frd_Type2 == POKETYPE_IWA
 1831 | || Frd_Type1 == POKETYPE_HAGANE
 1832 | || Frd_Type2 == POKETYPE_HAGANE
 1833 | || Frd_Type1 == POKETYPE_GHOST
 1834 | || Frd_Type2 == POKETYPE_GHOST){
 1836 | if (AI_CMD(CMD_IF_COMMONRND_OVER, 160)){
 1837 | SCORE += 2;
 1838 | return;
 1839 | }
 1840 | }
 1841 | else{
 1843 | if( AI_CMD(CMD_IF_RND_UNDER, 180) ){
 1844 | SCORE += -1;
 1845 | }
 1846 | }
 1847 | }
 1848 | }
```

### `DoubleAI_Friend_Main()` (source lines 1852–1879)

```text
 1852 | DoubleAI_Friend_Main()
 1853 | {
 1854 | if (AI_CMD(CMD_IF_HP_EQUAL, CHECK_ATTACK_FRIEND, 0)){
 1856 | SCORE += -30;
 1857 | }
 1863 | waza_seq_no = AI_CMD(CMD_CHECK_WORKWAZA_SEQNO);
 1864 | switch( waza_seq_no )
 1865 | {
 1866 | case 118: DoubleAI_Friend_Seq_118();
 1867 | case 154: DoubleAI_Friend_Seq_154();
 1868 | case 167: DoubleAI_Friend_Seq_167();
 1869 | case 176: DoubleAI_Friend_Seq_176();
 1870 | case 178: DoubleAI_Friend_Seq_178();
 1871 | case 191: DoubleAI_Friend_Seq_191();
 1872 | case 300: DoubleAI_Friend_Seq_300();
 1873 | case 309: DoubleAI_Friend_Seq_309();
 1874 | default:{
 1876 | SCORE += -20;
 1877 | }
 1878 | }
 1879 | }
```

### `DoubleAI_Friend_Seq_118()` (source lines 1881–1902)

```text
 1881 | DoubleAI_Friend_Seq_118()
 1882 | {
 1884 | if( AI_CMD(CMD_IF_DMG_PHYSIC_UNDER, CHECK_ATTACK_FRIEND)){
 1886 | SCORE += -12;
 1887 | return;
 1888 | }
 1889 | if( AI_CMD(CMD_IF_SIDEEFF, CHECK_DEFENCE) == BTL_SIDEEFF_SINPINOMAMORI
 1890 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK_FRIEND, ITEM_KIINOMI)
 1891 | || AI_CMD(CMD_IF_HAVE_ITEM, CHECK_ATTACK_FRIEND, ITEM_RAMUNOMI)
 1892 | || AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_MAIPEESU){
 1893 | if (AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK_FRIEND, 70)){
 1895 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 100)){
 1896 | SCORE += 2;
 1897 | return;
 1898 | }
 1899 | }
 1900 | }
 1901 | SCORE += -10;
 1902 | }
```

### `DoubleAI_Friend_Seq_154()` (source lines 1904–1917)

```text
 1904 | DoubleAI_Friend_Seq_154()
 1905 | {
 1907 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_DEFENCE) == TOKUSEI_SEIGINOKOKORO){
 1908 | if( AI_CMD(CMD_IF_PARA_UNDER, CHECK_ATTACK_FRIEND, 9)){
 1910 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 180)){
 1911 | SCORE += 2;
 1912 | return;
 1913 | }
 1914 | }
 1915 | }
 1916 | SCORE += -10;
 1917 | }
```

### `DoubleAI_Friend_Seq_167()` (source lines 1919–1939)

```text
 1919 | DoubleAI_Friend_Seq_167()
 1920 | {
 1922 | Frd_Tokusei = AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK_FRIEND);
 1923 | if( Frd_Tokusei == TOKUSEI_MORAIBI){
 1925 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 100)){
 1926 | SCORE += 2;
 1927 | return;
 1928 | }
 1929 | }
 1930 | if( Frd_Tokusei == TOKUSEI_KONZYOU){
 1931 | if( AI_CMD(CMD_IFN_POKESICK, CHECK_ATTACK_FRIEND)){
 1933 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 100)){
 1934 | SCORE += 2;
 1935 | return;
 1936 | }
 1937 | }
 1938 | }
 1939 | }
```

### `DoubleAI_Friend_Seq_176()` (source lines 1941–1959)

```text
 1941 | DoubleAI_Friend_Seq_176()
 1942 | {
 1944 | if (AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK_FRIEND) == 0){
 1945 | if (AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK) >= 2){
 1947 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 100)){
 1948 | SCORE += 2;
 1949 | return;
 1950 | }
 1951 | }
 1952 | }
 1953 | else{
 1954 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 180)){
 1955 | SCORE += -1;
 1956 | return;
 1957 | }
 1958 | }
 1959 | }
```

### `DoubleAI_Friend_Seq_178()` (source lines 1963–1967)

```text
 1963 | DoubleAI_Friend_Seq_178()
 1964 | {
 1967 | }
```

### `DoubleAI_Friend_Seq_191()` (source lines 1969–1973)

```text
 1969 | DoubleAI_Friend_Seq_191()
 1970 | {
 1973 | }
```

### `DoubleAI_Friend_Seq_300()` (source lines 1975–2006)

```text
 1975 | DoubleAI_Friend_Seq_300()
 1976 | {
 1978 | if (AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK) == 0
 1979 | || AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) == TOKUSEI_ITAZURAGOKORO){
 1980 | if (AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK_FRIEND) > 1){
 1981 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_HUNKA)
 1982 | || AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_SIOHUKI)){
 1983 | if (AI_CMD(CMD_IF_HP_OVER, CHECK_ATTACK_FRIEND, 70)){
 1985 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 180)){
 1986 | SCORE += 3;
 1987 | return;
 1988 | }
 1989 | }
 1990 | }
 1992 | if (AI_CMD(CMD_IF_RND_UNDER, 180)){
 1993 | SCORE += 3;
 1994 | return;
 1995 | }
 1996 | }
 1997 | if( AI_CMD(CMD_IF_HAVE_WAZA, CHECK_ATTACK_FRIEND, WAZANO_KIAIPANTI)){
 1999 | if (AI_CMD(CMD_IF_COMMONRND_UNDER, 180)){
 2000 | SCORE += 3;
 2001 | return;
 2002 | }
 2003 | }
 2004 | }
 2005 | SCORE += -8;
 2006 | }
```

### `DoubleAI_Friend_Seq_309()` (source lines 2008–2033)

```text
 2008 | DoubleAI_Friend_Seq_309()
 2009 | {
 2011 | if( AI_CMD(CMD_IF_HP_EQUAL, CHECK_ATTACK_FRIEND, 100)){
 2013 | if( AI_CMD(CMD_IF_COMMONRND_OVER, 50)){
 2014 | SCORE += -1;
 2015 | }
 2016 | return;
 2017 | }
 2018 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK_FRIEND, 50)){
 2020 | if( AI_CMD(CMD_IF_COMMONRND_UNDER, 128)){
 2021 | SCORE += 2;
 2022 | }
 2023 | return;
 2024 | }
 2025 | else if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK_FRIEND, 70)){
 2026 | if (AI_CMD(CMD_CHECK_AGI_RANK, CHECK_ATTACK) > 1){
 2028 | if( AI_CMD(CMD_IF_COMMONRND_UNDER, 128)){
 2029 | SCORE += 2;
 2030 | }
 2031 | }
 2032 | }
 2033 | }
```

## Pokechange: exact guarded score rules

| Function | Source lines | Influence role | What it does | Direct score writes | Calls |
|---|---:|---|---|---|---|
| `main()` | 3–46 | indirect caller/helper on a score path | Tests seven switch-enabling situations in priority order and stops after the first successful reason. | indirect/dynamic | CanAisyou0BaiBreak, CanAisyouMakeBetter, CanHusiginamamoriBreak, CanKodawariBadAisyouBreak, CanNoEffectPrevDamageByTokusei, CanRepairSickBySizenkaihuku, IsHorobinoutaLastTurn, PokeChangeOK |
| `PokeChangeOK(scoreOffset)` | 53–58 | direct score writer | Adds the computed reserve score plus the supplied offset and enables switching. | score | CalcBaseScore |
| `CalcBaseScore()` | 64–82 | indirect switch predicate/helper | Computes the reserve baseline from scenario-trainer Mega Evolution state and maximum effective bench move power. | indirect/dynamic | — |
| `IsHorobinoutaLastTurn()` | 88–96 | indirect switch predicate/helper | Detects whether the active Pokémon is on the final turn of Perish Song. | indirect/dynamic | — |
| `CanHusiginamamoriBreak()` | 102–118 | indirect switch predicate/helper | Randomly permits switching when a reserve can hit a Wonder Guard target that the active side cannot hit super-effectively. | indirect/dynamic | — |
| `CanAisyou0BaiBreak()` | 124–147 | indirect switch predicate/helper | Permits switching when a reserve improves a zero-effect matchup, using randomized thresholds for strictly better or equal matchups. | indirect/dynamic | — |
| `CanKodawariBadAisyouBreak()` | 153–187 | indirect switch predicate/helper | Permits escape from a bad Choice-locked matchup when the bench has a usable improvement, subject to randomized thresholds. | indirect/dynamic | IsAisyou0Bai |
| `IsAisyou0Bai(attacker, defender, wazano)` | 197–206 | indirect switch predicate/helper | Evaluates a switching condition using type effectiveness; its exact return path is shown below. | indirect/dynamic | — |
| `CanNoEffectPrevDamageByTokusei()` | 212–237 | indirect switch predicate/helper | Permits switching to exploit an ability that would nullify the opponent's previous damage move, with scenario-trainer and random exceptions. | indirect/dynamic | — |
| `CanRepairSickBySizenkaihuku()` | 243–280 | indirect switch predicate/helper | Permits switching to a Natural Cure Pokémon that can recover sleep or freeze and has a favorable matchup against the previous move. | indirect/dynamic | — |
| `CanAisyouMakeBetter()` | 286–330 | indirect switch predicate/helper | Permits switching when the active side was damaged by a poor matchup and a reserve offers a better matchup, with status, Mega, and random checks. | indirect/dynamic | — |

The complete guarded bodies follow:

### `main()` (source lines 3–46)

```text
    3 | main()
    4 | {
    6 | if( IsHorobinoutaLastTurn() ) {
    7 | PokeChangeOK( 20 );
    8 | return;
    9 | }
   12 | if( CanHusiginamamoriBreak() ) {
   13 | PokeChangeOK( 20 );
   14 | return;
   15 | }
   18 | if( CanAisyou0BaiBreak() ) {
   19 | PokeChangeOK( 20 );
   20 | return;
   21 | }
   24 | if( CanKodawariBadAisyouBreak() ) {
   25 | PokeChangeOK( 20 );
   26 | return;
   27 | }
   30 | if( CanNoEffectPrevDamageByTokusei() ) {
   31 | PokeChangeOK( 20 );
   32 | return;
   33 | }
   36 | if( CanRepairSickBySizenkaihuku() ) {
   37 | PokeChangeOK( 20 );
   38 | return;
   39 | }
   42 | if( CanAisyouMakeBetter() ) {
   43 | PokeChangeOK( 20 );
   44 | return;
   45 | }
   46 | }
```

### `PokeChangeOK(scoreOffset)` (source lines 53–58)

```text
   53 | PokeChangeOK( scoreOffset )
   54 | {
   55 | score = CalcBaseScore() + scoreOffset;
   56 | SCORE += score;
   57 | ENABLE_SWITCHING();
   58 | }
```

### `CalcBaseScore()` (source lines 64–82)

```text
   64 | CalcBaseScore()
   65 | {
   66 | score = 0;
   69 | if( AI_CMD(CMD_IF_I_AM_SENARIO_TRAINER) &&
   70 | AI_CMD(CMD_IF_CAN_MEGAEVOLVE, CHECK_BENCH) ) {
   71 | score += -10;
   72 | }
   76 | wazaPower = AI_CMD(CMD_GET_MAX_WAZA_POWER_INCLUDE_AFFINITY, CHECK_BENCH);
   77 | if( 240 <= wazaPower ){ score += 4; }
   78 | else if( 200 <= wazaPower ) { score += 3; }
   79 | else if( 160 <= wazaPower ) { score += 2; }
   81 | return score;
   82 | }
```

### `IsHorobinoutaLastTurn()` (source lines 88–96)

```text
   88 | IsHorobinoutaLastTurn()
   89 | {
   90 | if( AI_CMD(CMD_IFN_WAZASICK, CHECK_ATTACK, WAZASICK_HOROBINOUTA) ) {
   91 | return false;
   92 | }
   93 | maxTurn = AI_CMD(CMD_GET_HOROBINOUTA_TURN_MAX, CHECK_ATTACK);
   94 | nowTurn = AI_CMD(CMD_GET_HOROBINOUTA_TURN_NOW, CHECK_ATTACK);
   95 | return ( (nowTurn + 1) == maxTurn );
   96 | }
```

### `CanHusiginamamoriBreak()` (source lines 102–118)

```text
  102 | CanHusiginamamoriBreak()
  103 | {
  104 | defensePoke[] = { CHECK_DEFENCE, CHECK_DEFENCE_FRIEND };
  105 | defenseIndex;
  106 | for( defenseIndex=0; defenseIndex<sizeof(defensePoke); ++defenseIndex )
  107 | {
  108 | if( ( AI_CMD(CMD_CHECK_TOKUSEI, defensePoke[ defenseIndex ]) == TOKUSEI_HUSIGINAMAMORI ) &&
  109 | ( AI_CMD(CMD_IF_HAVE_BATSUGUN, CHECK_ATTACK, defensePoke[ defenseIndex ]) == false ) &&
  110 | ( AI_CMD(CMD_IF_HAVE_BATSUGUN, CHECK_BENCH, defensePoke[ defenseIndex ]) == true ) )
  111 | {
  112 | if( AI_CMD(CMD_IF_RND_UNDER, 170) ) {
  113 | return true;
  114 | }
  115 | }
  116 | }
  117 | return false;
  118 | }
```

### `CanAisyou0BaiBreak()` (source lines 124–147)

```text
  124 | CanAisyou0BaiBreak()
  125 | {
  127 | if( AI_CMD(CMD_IF_HAVE_WAZA_AISYOU_OVER, CHECK_ATTACK, CHECK_DEFENCE, AISYOU_0BAI) ||
  128 | AI_CMD(CMD_IF_HAVE_WAZA_AISYOU_OVER, CHECK_ATTACK, CHECK_DEFENCE_FRIEND, AISYOU_0BAI) ) {
  129 | return false;
  130 | }
  133 | if( AI_CMD(CMD_IF_HAVE_WAZA_AISYOU_OVER, CHECK_BENCH, CHECK_DEFENCE, AISYOU_1BAI) ||
  134 | AI_CMD(CMD_IF_HAVE_WAZA_AISYOU_OVER, CHECK_BENCH, CHECK_DEFENCE_FRIEND, AISYOU_1BAI) )
  135 | {
  136 | return AI_CMD(CMD_IF_RND_UNDER, 170);
  137 | }
  140 | if( AI_CMD(CMD_IF_HAVE_WAZA_AISYOU_EQUAL, CHECK_BENCH, CHECK_DEFENCE, AISYOU_1BAI) ||
  141 | AI_CMD(CMD_IF_HAVE_WAZA_AISYOU_EQUAL, CHECK_BENCH, CHECK_DEFENCE_FRIEND, AISYOU_1BAI) )
  142 | {
  143 | return AI_CMD(CMD_IF_RND_UNDER, 128);
  144 | }
  146 | return false;
  147 | }
```

### `CanKodawariBadAisyouBreak()` (source lines 153–187)

```text
  153 | CanKodawariBadAisyouBreak()
  154 | {
  156 | kodawariWaza = AI_CMD(CMD_GET_KODAWARI_WAZA, CHECK_ATTACK);
  157 | if( kodawariWaza == WAZANO_NULL ) {
  158 | return false;
  159 | }
  162 | if( AI_CMD(CMD_CHECK_DAMAGE_WAZA, kodawariWaza) == false )
  163 | {
  164 | return AI_CMD(CMD_IF_RND_UNDER, 170);
  165 | }
  170 | if( IsAisyou0Bai( CHECK_ATTACK, CHECK_DEFENCE, kodawariWaza ) &&
  171 | IsAisyou0Bai( CHECK_ATTACK, CHECK_DEFENCE_FRIEND, kodawariWaza ) )
  172 | {
  173 | randThreshold = 0;
  174 | if( AI_CMD(CMD_IF_HAVE_WAZA_AISYOU_OVER, CHECK_BENCH, CHECK_DEFENCE, AISYOU_1BAI) ||
  175 | AI_CMD(CMD_IF_HAVE_WAZA_AISYOU_OVER, CHECK_BENCH, CHECK_DEFENCE_FRIEND, AISYOU_1BAI) ) {
  176 | randThreshold = 170;
  177 | }
  178 | else if( AI_CMD(CMD_IF_HAVE_WAZA_AISYOU_EQUAL, CHECK_BENCH, CHECK_DEFENCE, AISYOU_1BAI) ||
  179 | AI_CMD(CMD_IF_HAVE_WAZA_AISYOU_EQUAL, CHECK_BENCH, CHECK_DEFENCE_FRIEND, AISYOU_1BAI) ) {
  180 | randThreshold = 128;
  181 | }
  183 | return AI_CMD(CMD_IF_RND_UNDER, randThreshold);
  184 | }
  186 | return false;
  187 | }
```

### `IsAisyou0Bai(attacker, defender, wazano)` (source lines 197–206)

```text
  197 | IsAisyou0Bai( attacker, defender, wazano )
  198 | {
  199 | if( AI_CMD(CMD_CHECK_WAZA_AISYOU, attacker, defender, wazano, AISYOU_0BAI) ) {
  200 | return true;
  201 | }
  202 | if( AI_CMD(CMD_CHECK_WAZA_NO_EFFECT_BY_TOKUSEI, defender, wazano) ) {
  203 | return true;
  204 | }
  205 | return false;
  206 | }
```

### `CanNoEffectPrevDamageByTokusei()` (source lines 212–237)

```text
  212 | CanNoEffectPrevDamageByTokusei()
  213 | {
  215 | if( AI_CMD(CMD_IF_I_AM_SENARIO_TRAINER) &&
  216 | AI_CMD(CMD_IF_CAN_MEGAEVOLVE, CHECK_BENCH) ) {
  217 | return false;
  218 | }
  221 | if( AI_CMD(CMD_IF_HAVE_BATSUGUN, CHECK_ATTACK, CHECK_DEFENCE) ||
  222 | AI_CMD(CMD_IF_HAVE_BATSUGUN, CHECK_ATTACK, CHECK_DEFENCE_FRIEND) ) {
  223 | if( AI_CMD(CMD_IF_RND_UNDER, 85) ) {
  224 | return false;
  225 | }
  226 | }
  229 | prevWaza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_DEFENCE);
  230 | if( AI_CMD(CMD_CHECK_WAZA_NO_EFFECT_BY_TOKUSEI, CHECK_BENCH, prevWaza) ) {
  231 | if( AI_CMD(CMD_IF_RND_UNDER, 128) ) {
  232 | return true;
  233 | }
  234 | }
  236 | return false;
  237 | }
```

### `CanRepairSickBySizenkaihuku()` (source lines 243–280)

```text
  243 | CanRepairSickBySizenkaihuku()
  244 | {
  246 | if( AI_CMD(CMD_IF_I_AM_SENARIO_TRAINER) &&
  247 | AI_CMD(CMD_IF_CAN_MEGAEVOLVE, CHECK_BENCH) ) {
  248 | return false;
  249 | }
  252 | if( AI_CMD(CMD_CHECK_TOKUSEI, CHECK_ATTACK) != TOKUSEI_SIZENKAIHUKU ) {
  253 | return false;
  254 | }
  257 | if( AI_CMD(CMD_IFN_WAZASICK, CHECK_ATTACK, WAZASICK_NEMURI) &&
  258 | AI_CMD(CMD_IFN_WAZASICK, CHECK_ATTACK, WAZASICK_KOORI) ) {
  259 | return false;
  260 | }
  263 | if( AI_CMD(CMD_IF_HP_UNDER, CHECK_ATTACK, 50) ) {
  264 | return false;
  265 | }
  268 | prevWaza = AI_CMD(CMD_CHECK_LAST_WAZA, CHECK_DEFENCE);
  269 | if( prevWaza == WAZANO_NULL ) {
  270 | return AI_CMD(CMD_IF_RND_UNDER, 128);
  271 | }
  274 | aisyou = AI_CMD(CMD_GET_WAZA_AISYOU, CHECK_DEFENCE, CHECK_ATTACK, prevWaza);
  275 | if( aisyou < AISYOU_1BAI ) {
  276 | return true;
  277 | }
  279 | return false;
  280 | }
```

### `CanAisyouMakeBetter()` (source lines 286–330)

```text
  286 | CanAisyouMakeBetter()
  287 | {
  289 | if( AI_CMD(CMD_IF_HAVE_BATSUGUN, CHECK_ATTACK, CHECK_DEFENCE) &&
  290 | AI_CMD(CMD_IF_RND_UNDER, 13) ) {
  291 | return false;
  292 | }
  295 | if( 4 <= AI_CMD(CMD_CHECK_STATUS_UP, CHECK_ATTACK) ) {
  296 | return false;
  297 | }
  300 | if( AI_CMD(CMD_IF_I_AM_SENARIO_TRAINER) &&
  301 | AI_CMD(CMD_IF_CAN_MEGAEVOLVE, CHECK_BENCH) ) {
  302 | return false;
  303 | }
  306 | if( AI_CMD(CMD_IF_HAVE_BATSUGUN, CHECK_BENCH, CHECK_DEFENCE) == false ) {
  307 | return false;
  308 | }
  311 | prevDamagedWaza = AI_CMD(CMD_GET_LAST_DAMAGED_WAZA_AT_PREV_TURN, CHECK_ATTACK);
  312 | if( prevDamagedWaza == WAZANO_NULL ) {
  313 | return false;
  314 | }
  317 | aisyou = AI_CMD(CMD_GET_WAZA_AISYOU, CHECK_DEFENCE, CHECK_BENCH, prevDamagedWaza);
  318 | if( aisyou == AISYOU_0BAI )
  319 | {
  320 | return AI_CMD(CMD_IF_RND_UNDER, 128);
  321 | }
  324 | if( aisyou <= AISYOU_1_2BAI )
  325 | {
  326 | return AI_CMD(CMD_IF_RND_UNDER, 85);
  327 | }
  329 | return false;
  330 | }
```

## What this does and does not establish

This index documents the exact source-level conditions and score writes represented in the recovered programs. It does not collapse native queries into universal weights: for example, `CHECK_WAZA_AISYOU`, `IF_HP_UNDER`, and damage queries return runtime values, and different scripts use those values in different branches. Random predicates can make the same candidate receive different contributions on different executions.

For the exact native return contracts, command IDs, retail AMX disassembly, and source line provenance, see [battle-ai-full-spec.md](battle-ai-full-spec.md).
