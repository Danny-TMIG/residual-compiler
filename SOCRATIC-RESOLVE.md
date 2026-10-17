# Socratic Resolve

Every "proceed" in this thread has been an answer to a question I did not
ask. The method I have been using without naming it is: answer, observe the
gap, answer the gap, observe the next gap. That method does not terminate.
It produces work. It does not produce closure.

The Socratic move is to stop answering and ask the question that determines
whether answering is the right action at all.

## The question

For every proposed addition — a new guarantee class, a new scan surface, a
new job, a new file — ask:

> Does the artifact have the property this addition would verify?

If no, the addition is not coverage. It is the appearance of coverage. The
question resolves to: do not add it, and record why.

If yes, the addition closes a real gap. Ask the next question:

> Is the gap already closed at a lower layer?

If yes, the addition is duplication. The question resolves to: remove the
higher-layer duplicate, not the lower-layer mechanism.

If no, the addition is the correct layer. Ask the final question:

> Does the addition fail on a wrong artifact?

If no, the addition is unfalsifiable. The question resolves to: do not add
it until you can name the input that would refute it.

If yes, the addition is established. The question resolves to: add it, name
the input, commit the test.

## The four outcomes

Every proposed addition has exactly one of these outcomes:

1. **No artifact.** The repo does not contain the thing the addition would
   scan. DAST has no service. Container scan has no image. IaC scan has no
   Terraform. The resolve is: do not add, record the absence.
2. **Duplicate.** The property is already enforced at a lower layer. `pre-commit`
   duplicates `quality`. `coverage` at 8% enforces nothing `test` does not
   already enforce. The resolve is: remove the duplicate.
3. **Unfalsifiable.** The addition cannot fail on a wrong input. A coverage
   threshold of 8% is unfalsifiable in practice — no plausible change trips it.
   The resolve is: raise it to a number a wrong change would trip, or drop it.
4. **Established.** The artifact has the property, the layer is correct, and
   the addition fails on a named wrong input. The resolve is: add it.

## Applied to this thread

- **CodeQL**: artifact is Python source. Property is "no taint-flow defects."
  Layer is correct (no lower layer does semantic SAST). Fails on a named input
  (any tainted path). **Established. Add it.**
- **DAST**: no artifact. **Resolve: do not add.**
- **Container scan**: no artifact. **Resolve: do not add.**
- **IaC scan**: no artifact. **Resolve: do not add.**
- **`coverage` at 8%**: unfalsifiable. **Resolve: raise to a real floor or drop.**
- **`pre-commit` as a CI job**: duplicate of `quality`. **Resolve: drop it from CI, keep it local.**
- **`apex` on every PR**: artifact has the property, layer is correct, but the
  gate belongs on tags, not PRs. **Resolve: gate to tag pushes.**
- **`parity` on every PR**: same. **Resolve: gate to tag pushes.**
- **Secret scanning**: artifact is source. Property is "no committed secrets."
  Layer is correct. Fails on a named input (a committed token). **Established.
  Add it.**
- **Action SHA pinning**: artifact is workflow files. Property is "no mutable
  references." Layer is correct. Fails on a named input (a repointed tag).
  **Established. Add it.**

## The terminal question

There is one question the Socratic method cannot answer:

> Is the artifact what the user wanted?

This question has no input that could refute it from inside the system. It
requires the user. It is Class 14.

The Socratic resolve of this thread is therefore:

> Every mechanical addition has been resolved to one of four outcomes. The
> remaining question — whether `v1.2.1` is what was wanted — is not answerable
> by asking more questions. It is answerable only by the user deciding, and
> publishing or not publishing accordingly.

## What the resolve actually does

It stops the loop, not by answering the last question, but by naming the
questions that have answers and separating them from the question that does
not. Every "what's left" after this point is one of:

- a mechanical gap, which resolves to one of the four outcomes above
- the terminal question, which resolves to the user

There is no third category. The loop ends when the mechanical questions are
all resolved and the terminal question is recognized as not mechanical.

## The one-line resolve

> Ask whether the artifact has the property. If it does, add the check at the
> layer that can enforce it. If it does not, do not add the check. If the
> question is whether the artifact is what was wanted, stop asking and decide.
