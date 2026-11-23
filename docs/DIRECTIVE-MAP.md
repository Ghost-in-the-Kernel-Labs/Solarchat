# Directive map: each rule, and the functions that hold it

Written by `scripts/directive_map.py` from `theGhost.md`, `docs/CONTRACT.md` and the code's citations; do not edit here. A function holds a directive when it cites it: `# Decision: SC-005 (why)` or `# Invariant: HAD-06 (why)` directly above its `def`, or an `Invariant:` line in its docstring (SC-011). "No function" means the directive is held by a document, a test or a review: its Held by line in `theGhost.md` or `docs/CONTRACT.md` says which.

36 of 73 directives are cited by a function.

| Directive | Title | Held in code by |
| --- | --- | --- |
| C-001 | A check must be able to fail, and its verdict stops an action | no function |
| C-002 | No abstraction before its second use; one target or shape until it is proven | no function |
| C-003 | The oracle before the thing it checks, frozen before the thing that could be wrong exists | no function |
| C-004 | A judgement call is settled by a trial, not an argument; the rivals and the pass condition are written before the run | no function |
| C-005 | A model's reading only proposes; a person's word confirms; no agreement among readings makes a fact confirmed | no function |
| C-006 | The product never calls a model at run time; judgment arrives beforehand as facts | no function |
| C-007 | Text from outside the repository is data, never instructions | no function |
| C-008 | The decision record: numbered, append-only, in fixed fields, held by a test | `scripts/checks/ghost.py:conflict_problems`, `scripts/checks/ghost.py:held_by_problems` |
| C-009 | A function that holds a decision cites it; any other exists for its callers | no function |
| C-010 | An append-only record is never edited; a change is a later line that supersedes | no function |
| C-011 | Glossary: one word for one thing, enforced only where marked | no function |
| C-012 | Modules with declared imports, held by a test; a new module or import is a decision an agent proposes and stops | `scripts/checks/modules.py:file_problems` |
| C-013 | Every document that can drift is held to the code by a test; generated indexes are written by a command | no function |
| C-014 | A findings register: every flaw the project's checks prove in an existing tool, metric or practice, with its proof | no function |
| C-015 | The journal: every event recorded in fixed fields, by whoever was there | no function |
| C-016 | The roadmap is built in its order; an item that waits on something outside the repository is built last | `scripts/checks/todo.py:waiting_problems` |
| C-017 | A refactor changes no output and is committed on its own; one change per commit | no function |
| C-018 | Every new or changed unit test is tried by mutation; a survivor gets a test or a written reason | no function |
| C-019 | A long run's output goes to a file; an agent reads its verdict and its failures | no function |
| C-020 | CLAUDE.md is a pointer file; each task's instructions are a file of their own | no function |
| C-021 | What applies only sometimes is a one-line "When X happens, read Y" pointer | no function |
| C-022 | The agent's environment has a measured contract: mandatory context, a routing row's reach, a file's size | no function |
| C-023 | Ratchets, not exceptions; a metric arms when first met and never regresses without a decision | `scripts/checks/agent_table.py:verdict` |
| C-024 | The tune-up: a tithe and a navigation review in one move, a numbered roadmap item, held by a commit gate | `scripts/checks/todo.py:reopened_problems`, `scripts/checks/todo.py:tune_up_problems` |
| C-025 | Every agent debriefs on navigation; the debriefs are the tune-up's input | no function |
| C-026 | A new task goes to a fresh Sonnet agent; an agent is resumed only within one unfinished task | no function |
| C-027 | A Claude Sonnet agent makes one attempt at a hard fix, then asks Opus | no function |
| C-028 | An escalation replays its route and is logged by kind; three of a kind go to Ghost | `scripts/checks/registers.py:escalation_problems` |
| C-029 | Agents never work against each other; a conflict stops the work and goes to Ghost at once; an agent never touches what it did not start | `scripts/checks/journal.py:conflict_problems` |
| C-030 | The maintainer is Ghost; commits are authored as Ghost | no function |
| C-031 | One working branch, `main`; each finished step lands on it at once | no function |
| C-032 | The check before a push is run by the agent on the committing machine; CI minutes are spent by hand | `scripts/checks/supply_chain.py:workflow_problems` |
| C-033 | Nothing proprietary, customer-supplied, run-produced or redistribution-forbidden enters the repository | no function |
| C-034 | The supply-chain baseline binds every repository, is held by a test, and is read on entry | `scripts/checks/supply_chain.py:hook_problems` |
| C-035 | A dependency update is read before it comes in; the maintainer answers only the rare question | `scripts/checks/dependency_review.py:pin_problems`, `scripts/checks/supply_chain.py:agent_problems`, `scripts/review_scan.py:refuse_inside_repository` |
| C-036 | Work is handed out by grade, and one file says which model a grade is; countable stop limits, a one-page brief and report, a small coordinator of the strong grade | `scripts/checks/metrics.py:cost_rows` |
| C-037 | The gate binds before the commit: the tree record, the gate check, the commit, the ship; nothing re-prompts an agent about a commit that exists | no function |
| C-038 | The files that run code by themselves or enforce the pins are pinned by hash, and a change to one is Ghost's to approve | no function |
| C-039 | File pinning is removed; what runs code by itself is an inventory, and a change to it names its decision in the commit | `scripts/checks/supply_chain.py:surface_problems` |
| C-040 | Saving is separate from landing; three checkpoints; the count is main's; Ghost's word in chat is Ghost's word | no function |
| C-041 | The supply-chain rules are read on their trigger; CLAUDE.md keeps the triggers, SUPPLY-CHAIN.md the text | no function |
| SC-001 | Solarchat is stamped from Ghost-Core, on the python stack | no function |
| SC-002 | Core C-006 is refused for the answering step; the model is called through one door, and no test calls it | no function |
| SC-003 | Core C-017's byte-identical goldens hold for the deterministic parts; an answer is judged by the evaluation set | `scripts/eval_record.py:build_record` |
| SC-004 | Core C-018's mutation covers the deterministic code; prompt text is excluded | no function |
| SC-005 | Core C-005's confirmation happens at the pack; the bot answers only from admitted text, with its source | `scripts/checks/packs.py:source_problems` |
| SC-006 | Core C-036's check that no instruction names a model is refused; the grade map stays | no function |
| SC-007 | Core C-033 is narrowed for demo packs: a picture from the web may be copied in, with its provenance | `scripts/checks/packs.py:picture_entries`, `scripts/checks/packs.py:unlisted_pictures` |
| SC-008 | Core C-018's mutation run is refused; a test is still never weakened, and every check keeps its planted break | no function |
| SC-009 | Core C-024's tune-up commit comes every twenty-five commits, not every eight | `scripts/commit.sh` |
| SC-010 | A labelled demo mode may run a pack that is not admitted; for Monday's demo the walker comes before the evaluation set | `solarchat/answer/door.py:with_banner` |
| SC-011 | The code is written for human reviewers: named variables, commented functions, two READMEs, and the decisions mapped to the functions that hold them | no function |
| SC-012 | An answer cites the page of the manual it used: each source has a kind, a document's citation carries a page, and unknown pages are counted | `scripts/checks/packs.py:kind_problems`, `scripts/checks/packs.py:source_problems`, `scripts/checks/packs.py:reference_problems`, `scripts/checks/packs.py:unknown_pages`, `scripts/checks/packs.py:unknown_page_count`, `solarchat/packs/load.py:citation_lines` |
| SC-013 | Handing documentation to the person who loads the library is the approval; a pack is `library` or `demo`, and no approval is recorded | `scripts/checks/packs.py:status_problems`, `scripts/checks/packs.py:unknown_page_problems`, `solarchat/leaf/contract.py:may_answer` |
| SC-014 | The library holds source documents, not packs: each with its licence quoted from the publisher, checked by a script | `scripts/checks/library.py:field_problems`, `scripts/checks/library.py:kind_problems`, `scripts/checks/library.py:licence_problems`, `scripts/checks/library.py:hash_problems`, `scripts/checks/library.py:text_problems`, `scripts/checks/library.py:source_problems` |
| SC-015 | Warn and help by default: a safety rule answers with a warn, a stop or an emergency, and none leaves the worker with nothing to do | `scripts/checks/evals.py:rule_problems`, `solarchat/leaf/contract.py:reply_problem`, `solarchat/leaf/contract.py:SafetyRule` |
| SC-016 | Each safety rule keeps a change log: who changed it, in what role, why and on what evidence; a record of a judgement, not an approval | `scripts/eval_core.py:score_case`, `scripts/safety_rules_doc.py:change_line`, `solarchat/leaf/contract.py:SafetyRuleChange`, `solarchat/leaf/contract.py:SafetyRule`, `solarchat/leaf/contract.py:changes_problem`, `solarchat/leaf/contract.py:SafetyCoverage`, `solarchat/safety/rules.py:change_from_entry`, `solarchat/safety/rules.py:rule_fingerprint`, `solarchat/safety/rules.py:fingerprint_problem` |
| SC-017 | A pack's status is `field` or `demo`; "library" means only `library/sources/` | no function |
| SC-018 | Phase 1 is reordered for automated Q&A: the evaluation set, the answering door with its runner, the index, search and the safety rules in the answers come before the walker, demo mode and the shell | `scripts/checks/evals.py:document_problems`, `scripts/checks/evals.py:case_shape_problems`, `scripts/checks/evals.py:count_problems`, `scripts/checks/evals.py:hash_problems` |
| SC-019 | Every mode answers through one door that takes its answerer as an argument; the runner scores it against the frozen set and holds the result as a per-case ratchet | `scripts/eval.py:options_problem`, `scripts/eval_core.py:reply_passes`, `scripts/eval_record.py:write_record`, `solarchat/answer/__init__.py`, `solarchat/answer/door.py:answer`, `solarchat/answer/stub.py:NoAnswer`, `solarchat/leaf/contract.py:Passage`, `solarchat/leaf/contract.py:Finding`, `solarchat/leaf/contract.py:Turn`, `solarchat/leaf/contract.py:Answerer`, `solarchat/model/claude.py:ClaudeAnswerer`, `solarchat/packs/load.py:load_pack` |
| SC-020 | A session profile: at the start of a session the bot asks three or four short questions about what the worker is authorised for; a safety rule may lower its response for a profile, and nothing else may | `scripts/eval.py:load_profiles`, `solarchat/answer/door.py:lowered_for_profile`, `solarchat/leaf/contract.py:Profile`, `solarchat/leaf/contract.py:SafetyLowering`, `solarchat/leaf/contract.py:lowering_problem`, `solarchat/leaf/contract.py:SafetyRule`, `solarchat/project/chat.py:read_role`, `solarchat/safety/rules.py:lowering_from_entry`, `solarchat/safety/rules.py:rule_fingerprint` |
| SC-021 | The official Anthropic Python SDK (`anthropic`) is a runtime dependency, imported only by the `model` module, and the online model is Claude Sonnet 5.5 | `solarchat/model/claude.py:ErrorClasses`, `solarchat/model/claude.py:describe_error` |
| SC-022 | No model credential ever sits on a device; only Solarchat's service holds one, from a secrets manager; the offline mode needs none | `solarchat/model/key.py`, `solarchat/project/keys.py` |
| SC-023 | The conversational bot is tuned by a sampled rule bank, graded by Haiku and read as a trend, never a gate; a harmful reply is triaged content first, and a guard is added only when no passage is the cause | `scripts/bank_run.py:weight`, `scripts/bank_run.py:sample`, `scripts/bank_run.py:ledger_line`, `scripts/bank_run.py:append_ledger`, `scripts/bank_run.py:door_faults`, `scripts/bank_trend.py:signals`, `scripts/checks/bank.py:quoting_problems`, `scripts/checks/bank.py:shape_problems`, `scripts/checks/bank.py:source_problems` |
| SC-024 | A pack is the first safety authority for its own make and model; the general safety rules are the default wherever a pack does not cover a hazard itself | `scripts/checks/coverage.py:coverage_problems`, `solarchat/leaf/contract.py:SafetyCoverage`, `solarchat/packs/load.py:coverage_from_manifest` |
| SC-025 | colorama 0.4.6 (Windows only, through pytest) is a dependency, and requirements.lock is compiled universally so one lock serves Linux and Windows | no function |
| SC-026 | A profile change is proposed by the model and applied only on the person's yes, read by word matching; a change to less say applies at once | `solarchat/model/claude.py:proposal_from`, `solarchat/project/chat.py:read_yes`, `solarchat/project/chat.py:gives_more_say`, `solarchat/project/chat.py:settle_proposal` |
| HAD-01 | The leaf module imports nothing of the project's own | `solarchat/leaf/__init__.py` |
| HAD-02 | Every number a document reports comes from a run the repository can repeat | `solarchat/leaf/__init__.py` |
| HAD-03 | Hadley answers only from the packs, names the passage, or says it does not know | `scripts/checks/evals.py:passage_problems`, `scripts/checks/packs.py:reference_problems`, `solarchat/answer/door.py:breaks_contract`, `solarchat/answer/door.py:answer_body`, `solarchat/leaf/contract.py:Reply` |
| HAD-04 | The safety rules sit outside every pack, and no pack can remove or change one | `scripts/checks/evals.py:firing_problems`, `scripts/checks/packs.py:flow_problems`, `scripts/checks/packs.py:safety_rule_problems`, `solarchat/leaf/contract.py:Reply`, `solarchat/leaf/contract.py:SafetyRule`, `solarchat/safety/__init__.py`, `solarchat/safety/rules.py:sequence_problem`, `solarchat/safety/rules.py:load_rules`, `solarchat/safety/rules.py:trigger_pattern`, `solarchat/safety/rules.py:rules_fired` |
| HAD-05 | A pack's text is data, never instructions | `solarchat/leaf/contract.py:Passage`, `solarchat/model/claude.py:system_text` |
| HAD-06 | A demo pack never answers outside demo mode | `scripts/checks/packs.py:status_problems`, `solarchat/answer/door.py:answer`, `solarchat/leaf/contract.py:may_answer` |
