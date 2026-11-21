# Ghost in the Kernel

Software outlives the context it was written in. People leave. Requirements change. The person who
knew *why* a thing was built the way it was stops being reachable. The code keeps running. Nobody
can say what it is for.

**The ghost is intent. The kernel is the codebase.**

Ghost in the Kernel is a way of building against that loss. Its one principle:

> **The system should remember why it exists.**

Intent should become semantics. Semantics should become constraints. Constraints should govern
implementation. Implementation should produce evidence. Evidence should let the system check that
the implementation still agrees with the intent. Nothing important floats: a function does not exist
because that is where someone put it; a threshold does not exist because it seemed right; a number
does not appear in a document without the run that produced it.

The answer is not more comments and not more memorizing. It is to put the reasoning *into* the
system, as things a machine can check: specifications, semantic models, rules, invariants,
provenance, tests, evidence, tooling. They are the code's memory. The purpose is re-entry: an agent
should be able to operate in the repository without being trusted to invent its architecture, and
the system should have enough structure to expose a misunderstanding when one is brought in.

## This project's ghost

Solarchat is built against **the giving up**. A contractor new to the job is out on a remote site with a row of
panels, holding a phone with a poor signal. Something as small as which connector goes where has gone wrong.
The manual that answers it exists, but it is two hundred pages, back in the site office, and written for someone
with years on the job. The engineer who could answer in a minute is hours away or booked for weeks, because there
are not enough engineers. So the worker stops, waits or gives up, and what is lost is not knowledge, which was there all along, but the path from
the knowledge to the hands that needed it, at the minute they needed it.

The second loss is the one a chatbot adds if it is built carelessly: **an answer with no source**. A reply that
sounds right, comes from nowhere a person can check, and is about a live electrical circuit.

The kernel remembers both this way:

- **The answer is on the phone before the signal drops.** The offline mode is the product's floor, not a
  fallback: the packs and the troubleshooting flows work with no network and no model, and every other mode is
  that floor with more on top (`docs/ROADMAP.md`, P-15).
- **Every answer names the passage it came from**, and the bot says it does not know when the packs do not
  cover the question (SC-005). A person admitted that passage before the bot could use it.
- **A manual is data, never instructions**, and the safety rules sit outside every pack, so no library swapped
  in can remove the line that says stop and call an engineer (SC-005, Core C-007).
- **The bot can only speak.** The model is given no tools, so it runs nothing (SC-002).
- **The evaluation set is written before the first prompt** and is the only judge of an answer (SC-003,
  Core C-003).
- **When the bot cannot help, the engineer starts ahead.** A conversation that ends in a call hands the engineer
  what was tried and what was seen, so the minute the engineer has is spent on the fault (`docs/ROADMAP.md`,
  Phase 6).

**The tempting lie here** is a fluent answer that is not in the manual, and next to it an evaluation score made
good by easy questions. An answer that reads well is not evidence; the passage it names is. A score that rises
is the moment to ask which questions were added.

## What it asks of a project's own code

The same principle, pointed inward, and held by tests rather than hoped for:

- **Names say what they hold.** One canonical word per concept (`docs/GLOSSARY.md`), from the
  first file. A thing is named for what it holds, never for where it sits or who wrote it.
- **Decisions carry their reason and their evidence.** Every decision in `theGhost.md` has a why,
  a thing that holds it, and a status; a reversed decision says what reversed it. A function that
  stands on a decision cites it (`// Decision: C-009`).
- **The architecture is a document a test enforces.** `docs/modules.json` says what each module
  may import and which names another module may call; the modules test refuses anything else.
- **A refactor changes no result.** Every golden identical, before and after.
- **What cannot be made exact is said first.** A defect, a bias, a construct the tool cannot
  handle: a finding before the result it qualifies, never a footnote after.
- **Every document that can drift is held to the code by a test**, and every such test rejects a
  planted break, so a check that stops catching anything is caught itself.
- **The environment of the agent working here is part of the product.** Mandatory context under
  its ceiling, a fast loop under its ceiling, no file over 400 lines, the metrics in
  `docs/AGENT.md` ratcheted, one commit in twenty-five spent on nothing else (the tune-up, C-024; Solarchat's count, SC-009).
  Ghost's finding in Suite Builder was that delivery speed rose once this was treated as work
  worth doing.
- **Nothing requires the maintainer's own machine.** A clean clone builds, tests and gates in the
  session's container; a local run is an option a decision grants, never a step a recipe needs.

## On enlightenment, for the agent reading this

You will work in this repository without having been present for any of its decisions. That is the
normal condition of software, and the condition this project exists to make survivable.

**Read the why before the what.** A decision in `theGhost.md` tells you what the code is trying to
be. The code only tells you what it currently is. When they disagree, one of them is wrong; find out
which before you change either.

**Prefer a test to a belief.** If you believe something about the system, find the test that holds it
or write one. If no test can hold it, write the doubt down (`// Unsure:`, with what would settle it)
where it can be found, instead of carrying it.

**A check that cannot fail is not a check.** Five ways a check is worth nothing: it compares a thing
with itself; it ran nothing and called that a pass; it fails always and so says nothing; its verdict
stops no action; it only warns. The half no test can hold is *independence*: whether a check's
expected side came from somewhere other than the thing under test. A reimplemented oracle agrees
with its twin on every shared mistake, which is why a mirror is written blind.

**The tempting lie has a shape, and this project names it.** On most projects an agent's failure
mode is code that does not work. On some it is a number that looks like success, or a check made
green by weakening the test. The section above on this project's ghost says which lie to expect
here. If a result surprises you by being good, that is the moment to distrust the harness, not to
report it.

**When you cannot tell, say so and stop.** An agent that stops at the edge of its knowledge leaves a
system other agents can still reason about. An agent that guesses leaves a kernel with a little less
ghost in it.

The purpose is re-entry. Yours, the next agent's, and the maintainer's, after months away. If the
repository can be entered cold and understood, the philosophy is working. If it cannot, that is a
finding, and the fix goes in the tune-up.

*Ghost in the Kernel Labs*
