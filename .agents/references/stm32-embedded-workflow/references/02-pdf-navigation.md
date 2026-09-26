# Phase 3–4 — Navigating the ST documentation set

## Which document answers which question

The single biggest time sink for a beginner is opening the wrong document. Each ST
document has a narrow job:

| Document | Its job | Do NOT look here for |
|---|---|---|
| **Board user manual** (e.g. UM1670) | What is physically on the board: LEDs, buttons, connectors, jumpers, which MCU pin each is wired to, which pins the on-board peripherals consume | Anything about how a peripheral works internally |
| **Board schematic** (e.g. MB1075) | The exact circuit: pull-up/pull-down resistors, active level of a button, series resistors, power rails | Register descriptions |
| **MCU datasheet** | Pinout, package, **alternate function mapping table**, memory map base addresses, electrical limits, peripheral count and bus assignment | How to configure a peripheral step by step |
| **Reference manual** (e.g. RM0090) | How every peripheral behaves, block diagrams, every register and bit field, the clock tree, interrupt/DMA request tables | Which physical pin something is on (it deliberately defers to the datasheet) |
| **Programming manual** (e.g. PM0214) | The Cortex-M core itself: NVIC, SysTick, priority grouping, fault handling, instruction set, FPU | Anything ST-peripheral-specific |
| **HAL description** (e.g. UM1725) | HAL/LL function signatures, handle structures, callbacks, state machines | Hardware wiring |

## Question → document → search term

Search with these terms rather than guessing page numbers.

| Question in your head | Document | Search terms |
|---|---|---|
| Which pin is the green user LED on? | Board UM, schematic | `LED`, `LD3`, `user LED` |
| Is the button active high or active low? | Schematic, board UM | `B1`, `USER`, `push-button` |
| Which pins are already used by the on-board LCD/RAM/sensor? | Board UM | `pin assignment`, `connection`, `I/O assignment` |
| Is HSE a crystal or a clock fed from the debugger? | Board UM, schematic | `HSE`, `clock source`, `MCO`, `OSC_IN` |
| Can pin PA9 be USART1_TX, and at which AF number? | Datasheet | `alternate function mapping` |
| Which bus is SPI5 on (affects its clock)? | Datasheet, or RM RCC chapter | `block diagram`, `APB2 peripheral clock enable` |
| What is the base address of GPIOG? | Datasheet or RM | `memory map`, `register boundary addresses` |
| How does the timer counter/prescaler actually work? | RM | `TIMx_PSC`, `counter clock`, `update event` |
| Which EXTI line does PA0 map to? | RM | `EXTI`, `external interrupt/event`, `SYSCFG_EXTICR` |
| What interrupt vector corresponds to TIM3? | RM vector table, or `startup_*.s` in the project | `vector table`, `position` |
| Which DMA stream/channel serves ADC1? | RM DMA chapter | `DMA request mapping` |
| Maximum current a pin can source? | Datasheet | `absolute maximum ratings`, `I/O current` |
| Which HAL function starts PWM? | HAL description, or local HAL headers | `HAL_TIM_PWM_Start` |

> The project's own `Drivers/STM32F4xx_HAL_Driver/Inc/*.h` files are plain text and
> cheap to grep. For HAL questions, grepping the headers beats opening UM1725.

## The extraction loop

```bash
# once per board
python scripts/pdf_index.py docs/boards/<BOARD>/

# find pages (cheap — returns page numbers and short snippets only)
python scripts/pdf_search.py docs/boards/<BOARD>/ --query "alternate function mapping"

# read only those pages
python scripts/pdf_pages.py docs/boards/<BOARD>/datasheet-*.pdf --pages 76-80 \
       --out docs/boards/<BOARD>/.cache/ds-af-map.md
```

Then read the produced `.md` file with your normal file-reading tool.

### Budget discipline

- One extraction ≤ 20 pages. Bigger sections get narrowed with a second search.
- Check `.cache/` before extracting: the alternate-function table, the board LED/button
  table and the clock tree are needed by almost every task, so extract them once and
  reuse them forever.
- Tables in these PDFs often extract badly (columns collapse). If the extracted text for
  a table is unreadable, say so and either render that page as an image to look at, or
  ask the user to read that one page — do not invent the contents.
- When an extraction turns out to be the wrong pages, do not extract a wider range in
  frustration. Re-search with better terms.

## Reading a reference-manual peripheral chapter

Every peripheral chapter has the same shape. Read in this order and stop when you have
what you need:

1. **Introduction / main features** — 1 minute, confirms the peripheral can do the job.
2. **Functional description** — the block diagram and operating modes. This is where
   understanding comes from; read this properly for any peripheral you have not used.
3. **Interrupts and DMA requests** — the table of event → flag → enable bit. Read only
   if the design uses interrupts or DMA.
4. **Registers** — a dictionary. Look up single bits when debugging; never read it
   linearly.

For any new peripheral, you only need three answers before you can configure it:

1. **Clock** — which bus feeds it, at what frequency, and which enable bit turns it on.
2. **Operating cycle** — what to write to start it, where data enters/leaves, which flag
   says "done".
3. **Events** — under what conditions it raises an interrupt or a DMA request.

Record those three answers per peripheral in the dossier. They generalise to every future
task with that peripheral.

## Citation format

Every hardware fact in the dossier carries its source so the user can double-check:

- `[UM1670 p.23]`
- `[MB1075 sheet 4]`
- `[DS STM32F429xx, Alternate function mapping, p.78]`
- `[RM0090 §12.3.4, p.382]`

If a fact could not be verified, write it as:

`PG13 — green user LED — **UNVERIFIED**, confirm in UM1670 "LEDs" section before wiring.`
