# Why three models, not two?

A natural question: if multi-model review is better than single,
why exactly three? Why not two? Why not five?

## The 2-model collapse

With two models, the consolidation step has only two outputs:

- **Both agree** — call this consensus
- **Exactly one finds it** — call this unique

That's a binary signal. There's no middle ground. And when the two
disagree on something specific, you've got no third opinion to
break the tie. You're back to flipping a coin.

Two models is also where the value of "unique" findings is most
ambiguous. When 1 of 2 catches something, it could equally well be
that model's insight or its hallucination. With three, the same
1-of-3 finding is still uncertain, but you've got two other
reviews on the same artifact that didn't flag it as a problem —
making it easier to interpret.

## What three models add

With three, the gradient becomes useful:

- **All 3 agree** (3-way consensus) — strongest signal; this is
  almost certainly worth fixing
- **2 of 3 agree** (2-way consensus) — strong signal; still likely
  real, with one model offering a different lens
- **1 of 3 finds it** (unique) — the most interesting case. Could
  be that model's insight; could be the other two's blind spot

That 3-way / 2-way / 1-way gradient is the whole point. The
"1-of-3" findings — the ones only one model caught — are where you
catch what single-model review would have missed entirely.

## Why not four or more?

Two reasons.

**Cost.** Each model adds API spend roughly proportional to its
share of the total. Going from 3 to 4 is a 33% cost bump per run,
and you'll run this many times. The marginal value drops fast.

**Echo chamber.** This is the bigger reason. Today's frontier LLMs
are all transformers trained on overlapping public corpora. They
share blind spots — and when they all miss something, they tend to
miss the *same* something. Adding a fourth model from the same
architectural family (another GPT, another fine-tuned open
release) adds vote weight without adding meaningful diversity. If
you really want a fourth opinion, the better move is to pick one
with a meaningfully different base architecture or training
corpus, not just a different vendor logo.

In practice, three models — Claude / Codex (GPT-family) / Gemini —
gives you three different teams' training data, three different
RLHF preferences, and three different sets of blind spots. That's
enough to surface meaningful disagreement. Beyond three the
returns get small fast.

## When three isn't enough

If you find that all three of your models keep missing the same
type of bug, the fix isn't a fourth model. It's a feedback loop:
keep a regression list of human-found bugs and feed them back into
your consolidation prompt, so the system learns from the misses
you catch by hand. [Chapter 06](../06-going-further/) covers this
in the pitfalls section (look for the "echo chamber" warning).

[← Back to README](../README.md)
