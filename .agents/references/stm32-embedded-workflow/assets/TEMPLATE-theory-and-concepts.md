# Theory & Concepts — <task title>

> Required structure for the secondary deliverable. This file isolates theoretical explanations, documentation facts, register details, and specific conceptual questions raised by the user. Keep every section heading.

| | |
|---|---|
| Task ID | `<task-id>` |
| Documents consulted | `<UM1670 rev X, RM0090 rev Y, datasheet rev Z>` |

---

## 1. Facts established from the documentation

For each peripheral used, document the underlying hardware mechanisms. This provides the rationale behind the CubeMX settings and code structure.

### `<PERIPHERAL>`

| Question | Answer | Source |
|---|---|---|
| Which bus and clock feeds it? | | `[RM0090 §X.Y]` |
| What starts it, where does data flow, which flag says done? | | `[RM0090 §X.Y]` |
| Which events raise an interrupt / DMA request? | | `[RM0090 §X.Y]` |
| Relevant registers and bits (for understanding, not for hand-coding) | | `[RM0090 §X.Y]` |

## 2. Explanation of concepts

Address any specific conceptual questions or requests for explanation from the user's input.

### `<Concept 1: e.g. Active High vs Active Low>`
`<Explanation...>`

### `<Concept 2: e.g. SysTick Non-blocking delays>`
`<Explanation...>`

## 3. Design rationale

Explain the deeper reasoning behind specific choices made in the design.

### Why `<this choice>` instead of `<that choice>`?
`<Explanation...>`

## 4. What to learn from this task

`<Two or three sentences: the transferable idea. "The reason the timer needed PSC=8999 rather than 44999 is the APB doubling rule — you will meet it on every F4 timer task." This is what makes the next assignment faster.>`

## 5. Possible extensions

`<Optional. Small variations the user could try to consolidate the concept — "switch the UART transmit to DMA and compare the jitter", etc.>`
