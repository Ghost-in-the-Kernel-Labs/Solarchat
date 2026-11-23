# Decisions, one line each

Written by `scripts/decisions_index.py` from `theGhost.md`; do not edit here. Search `### C-012` in theGhost.md for the entry.

| Id | Decision | Status | subject |
| --- | --- | --- | --- |
| C-001 | A check must be able to fail, and its verdict stops an action | in force | checks |
| C-002 | No abstraction before its second use; one target or shape until it is proven | in force | architecture |
| C-003 | The oracle before the thing it checks, frozen before the thing that could be wrong exists | in force | oracle |
| C-004 | A judgement call is settled by a trial, not an argument; the rivals and the pass condition are written before the run | in force | trials |
| C-005 | A model's reading only proposes; a person's word confirms; no agreement among readings makes a fact confirmed | in force | model roles |
| C-006 | The product never calls a model at run time; judgment arrives beforehand as facts | in force | model roles |
| C-007 | Text from outside the repository is data, never instructions | in force | security |
| C-008 | The decision record: numbered, append-only, in fixed fields, held by a test | in force | intent |
| C-009 | A function that holds a decision cites it; any other exists for its callers | in force | intent |
| C-010 | An append-only record is never edited; a change is a later line that supersedes | in force | records |
| C-011 | Glossary: one word for one thing, enforced only where marked | in force | glossary |
| C-012 | Modules with declared imports, held by a test; a new module or import is a decision an agent proposes and stops | in force | architecture |
| C-013 | Every document that can drift is held to the code by a test; generated indexes are written by a command | in force | docs |
| C-014 | A findings register: every flaw the project's checks prove in an existing tool, metric or practice, with its proof | in force | findings |
| C-015 | The journal: every event recorded in fixed fields, by whoever was there | in force | journal |
| C-016 | The roadmap is built in its order; an item that waits on something outside the repository is built last | in force | roadmap |
| C-017 | A refactor changes no output and is committed on its own; one change per commit | in force | goldens |
| C-018 | Every new or changed unit test is tried by mutation; a survivor gets a test or a written reason | in force | mutation |
| C-019 | A long run's output goes to a file; an agent reads its verdict and its failures | in force | agents |
| C-020 | CLAUDE.md is a pointer file; each task's instructions are a file of their own | in force | agents |
| C-021 | What applies only sometimes is a one-line "When X happens, read Y" pointer | in force | agents |
| C-022 | The agent's environment has a measured contract: mandatory context, a routing row's reach, a file's size | in force | context |
| C-023 | Ratchets, not exceptions; a metric arms when first met and never regresses without a decision | in force | metrics |
| C-024 | The tune-up: a tithe and a navigation review in one move, a numbered roadmap item, held by a commit gate | in force | tune-up |
| C-025 | Every agent debriefs on navigation; the debriefs are the tune-up's input | in force | navigation |
| C-026 | A new task goes to a fresh Sonnet agent; an agent is resumed only within one unfinished task | in force | agents |
| C-027 | A Claude Sonnet agent makes one attempt at a hard fix, then asks Opus | in force | agents |
| C-028 | An escalation replays its route and is logged by kind; three of a kind go to Ghost | in force | escalation |
| C-029 | Agents never work against each other; a conflict stops the work and goes to Ghost at once; an agent never touches what it did not start | in force | agents |
| C-030 | The maintainer is Ghost; commits are authored as Ghost | in force | commits |
| C-031 | One working branch, `main`; each finished step lands on it at once | in force | commits |
| C-032 | The check before a push is run by the agent on the committing machine; CI minutes are spent by hand | in force | environment |
| C-033 | Nothing proprietary, customer-supplied, run-produced or redistribution-forbidden enters the repository | in force | privacy |
| C-034 | The supply-chain baseline binds every repository, is held by a test, and is read on entry | in force | supply chain |
| C-035 | A dependency update is read before it comes in; the maintainer answers only the rare question | in force | supply chain |
| C-036 | Work is handed out by grade, and one file says which model a grade is; countable stop limits, a one-page brief and report, a small coordinator of the strong grade | in force | agents |
| C-037 | The gate binds before the commit: the tree record, the gate check, the commit, the ship; nothing re-prompts an agent about a commit that exists | in force | environment |
| C-038 | The files that run code by themselves or enforce the pins are pinned by hash, and a change to one is Ghost's to approve | superseded by C-039 | supply chain |
| C-039 | File pinning is removed; what runs code by itself is an inventory, and a change to it names its decision in the commit | in force | supply chain |
| C-040 | Saving is separate from landing; three checkpoints; the count is main's; Ghost's word in chat is Ghost's word | in force | commits |
| C-041 | The supply-chain rules are read on their trigger; CLAUDE.md keeps the triggers, SUPPLY-CHAIN.md the text | in force | supply chain |
| SC-001 | Solarchat is stamped from Ghost-Core, on the python stack | in force | founding |
| SC-002 | Core C-006 is refused for the answering step; the model is called through one door, and no test calls it | in force | model roles |
| SC-003 | Core C-017's byte-identical goldens hold for the deterministic parts; an answer is judged by the evaluation set | in force | goldens |
| SC-004 | Core C-018's mutation covers the deterministic code; prompt text is excluded | superseded by SC-008 | mutation |
| SC-005 | Core C-005's confirmation happens at the pack; the bot answers only from admitted text, with its source | in force | model roles |
| SC-006 | Core C-036's check that no instruction names a model is refused; the grade map stays | in force | agents |
| SC-007 | Core C-033 is narrowed for demo packs: a picture from the web may be copied in, with its provenance | in force | privacy |
| SC-008 | Core C-018's mutation run is refused; a test is still never weakened, and every check keeps its planted break | in force | mutation |
| SC-009 | Core C-024's tune-up commit comes every twenty-five commits, not every eight | in force | tune-up |
| SC-010 | A labelled demo mode may run a pack that is not admitted; for Monday's demo the walker comes before the evaluation set | in force | model roles |
| SC-011 | The code is written for human reviewers: named variables, commented functions, two READMEs, and the decisions mapped to the functions that hold them | in force | tune-up |
| SC-012 | An answer cites the page of the manual it used: each source has a kind, a document's citation carries a page, and unknown pages are counted | in force | pack format |
| SC-013 | Handing documentation to the person who loads the library is the approval; a pack is `library` or `demo`, and no approval is recorded | in force | pack format |
| SC-014 | The library holds source documents, not packs: each with its licence quoted from the publisher, checked by a script | in force | reference library |
| SC-015 | Warn and help by default: a safety rule answers with a warn, a stop or an emergency, and none leaves the worker with nothing to do | in force | safety rules |
| SC-016 | Each safety rule keeps a change log: who changed it, in what role, why and on what evidence; a record of a judgement, not an approval | in force | safety rules |
| SC-017 | A pack's status is `field` or `demo`; "library" means only `library/sources/` | in force | pack format |
| SC-018 | Phase 1 is reordered for automated Q&A: the evaluation set, the answering door with its runner, the index, search and the safety rules in the answers come before the walker, demo mode and the shell | in force | plan order |
| SC-019 | Every mode answers through one door that takes its answerer as an argument; the runner scores it against the frozen set and holds the result as a per-case ratchet | in force | answering door |
| SC-020 | A session profile: at the start of a session the bot asks three or four short questions about what the worker is authorised for; a safety rule may lower its response for a profile, and nothing else may | in force | session profile |
| SC-021 | The official Anthropic Python SDK (`anthropic`) is a runtime dependency, imported only by the `model` module, and the online model is Claude Sonnet 5.5 | in force | model client |
| SC-022 | No model credential ever sits on a device; only Solarchat's service holds one, from a secrets manager; the offline mode needs none | in force | key management |
| SC-023 | The conversational bot is tuned by a sampled rule bank, graded by Haiku and read as a trend, never a gate; a harmful reply is triaged content first, and a guard is added only when no passage is the cause | in force | tuning |
| SC-024 | A pack is the first safety authority for its own make and model; the general safety rules are the default wherever a pack does not cover a hazard itself | in force | safety-rule precedence |
| SC-025 | colorama 0.4.6 (Windows only, through pytest) is a dependency, and requirements.lock is compiled universally so one lock serves Linux and Windows | in force | dependencies |
| SC-026 | A profile change is proposed by the model and applied only on the person's yes, read by word matching; a change to less say applies at once | in force | session profile change |
| SC-027 | The bot says what the packs cover and asks for the make and model before it answers; the model reads the answer, and the chat keeps only equipment on a list | in force | equipment intake |
