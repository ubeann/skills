# The generation contract

What the generator receives and what it returns, whether the generator is you, a subagent, `impeccable`, or another tool the user pastes this into.

## Inputs, and nothing else

1. `PRODUCT.md`: who, the bet, the key moments.
2. `DESIGN.md`: the tokens and the rules.
3. One pattern reference per flow being built, labelled "structure only".
4. The screen list for the flow, in order, including its peak, its end, and its hard-moment states.

More references at this point make the output worse, not richer. If something is missing, add it to `DESIGN.md` first, then generate.

When a pattern library is connected (Mobbin's MCP is one), research how shipped products handle this flow first and cite the screens used. Research the patterns, then build with this product's own tokens; one-shotting the screens skips the research that makes them specific ([video at 2:49](https://www.youtube.com/watch?v=YbLF42BaoZs&t=169s)).

## The instruction

Adapt this to the flow and keep every line:

```text
Build <flow> for <product> as <screen list>.
Use only the tokens in DESIGN.md: every colour, size, weight, spacing value and radius
is a token or a token at reduced opacity. Use the signature element where DESIGN.md says.
Take structure from the pattern reference, never its colours, type or imagery.
Design the peak screen and the end screen as PRODUCT.md describes them.
Every hard moment answers: what happened, can I undo it, what do I do next.
Copy says each thing once, in the product's voice.
When you deviate from DESIGN.md or the pattern on purpose, keep going, and list each deviation.
```

Asking for deviations to be flagged keeps the generator from silently mixing systems, and turns a deviation into a decision the user makes ([video at 2:20](https://www.youtube.com/watch?v=YbLF42BaoZs&t=140s)).

## What comes back

The built screens, plus the deviation list:

| Screen | Element | Token or pattern it departs from | Value used | Why |
|---|---|---|---|---|

Each deviation is resolved in step 6: snapped to the token, or promoted to a token with its reason.
