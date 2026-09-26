# Configuration & Implementation — <task title>

> Required structure for the primary configuration deliverable. Keep every section heading; delete a section's placeholder rows only. Replace every `<...>`. Every hardware fact carries a citation such as `[UM1670 p.23]`.

| | |
|---|---|
| Task ID | `<task-id>` |
| Board | `<board>` |
| MCU | `<part number>` |
| Date | `<date>` |

---

## 0. Open items — confirm before building

| # | Item | Why it matters | How to confirm |
|---|---|---|---|
| 1 | `<e.g. LD3 pin assignment>` | `<wrong pin = nothing lights up>` | `<UM1670, "LEDs" section>` |

## 1. Problem analysis

**Restated in one sentence:** `<...>`

### Assumptions made

| Assumption | Why | Impact if wrong |
|---|---|---|
| `<blink "fast" = 100 ms>` | `<not specified>` | `<cosmetic only>` |

### Requirements (Inputs, Outputs, Timing, State)

| Signal / Constraint / State | Details |
|---|---|
| **Inputs** | `<...>` |
| **Outputs** | `<...>` |
| **Timing constraints** | `<...>` |
| **State to maintain** | `<...>` |

### Acceptance criteria

- [ ] `<observable behaviour>` — expected `<what you should see>`

## 2. Peripheral selection

| Requirement | Peripheral | Processing model | Why this, not the alternative |
|---|---|---|---|

**Escalation justification:** `<why anything beyond simple polling was necessary>`

## 3. Pin map

| Signal | Pin | Mode | Pull | Speed / AF | Active level | Source |
|---|---|---|---|---|---|---|
| `<LED_GREEN>` | `<PG13>` | `<Output push-pull>` | `<No pull>` | `<Low>` | `<High = on>` | `[UM1670 p.23]` |

### Pin availability & Conflicts
`<Statement that each chosen pin was checked against the board's on-board peripheral allocation.>` `[citation]`
Pins avoided: `<e.g. PA13/PA14 SWD debug>`

## 4. Clock and timing calculations

### System clock

```
<source> → M=<> → N=<> → P=<> → SYSCLK = <> MHz
AHB /<> → HCLK  = <> MHz
APB1 /<> → PCLK1 = <> MHz   → APB1 timer clock = <> MHz
APB2 /<> → PCLK2 = <> MHz   → APB2 timer clock = <> MHz
```

### Derived values

| Value | Derivation | Result |
|---|---|---|
| `<TIM3 ARR>` | `<500 ms × 10 kHz = 5000 ticks → ARR = 4999>` | `4999` |
| verification | `<(4999+1)/(90e6/9000) = 0.5 s ✓>` | ✓ |

## 5. STM32CubeMX configuration

Numbered click path, in tool order, every field filled with a concrete value.

```
□ 1. New project
     File → New → STM32 Project → "Board Selector" tab → <board name> → Next
     "Initialize all peripherals with their default Mode?" → No/Yes (explain why)
     Project name: <task-id>

□ 2. System Core → RCC
     High Speed Clock (HSE): <Crystal/Ceramic Resonator | BYPASS Clock Source | Disable>

□ 3. System Core → SYS
     Debug: Serial Wire
     Timebase Source: SysTick

□ 4. Clock Configuration tab
     <Detailed steps and target HCLK>

□ 5. GPIO pins
     <Detailed pin settings matching Pin Map>

□ 6. Communication peripherals (UART / I2C / SPI)
     <Detailed settings>

□ 7. Timers & Analog
     <Detailed settings>

□ 8. NVIC & DMA Settings
     <Detailed settings>

□ 9. Project Manager → Code Generator
     ☑ Generate peripheral initialization as a pair of .c/.h files per peripheral

□ 10. GENERATE CODE (Alt+K)
```

### Configuration traps relevant to this task

| Trap | Symptom if you hit it | Correct setting |
|---|---|---|

## 6. Implementation plan

### Program structure

```
<one-screen sketch: what happens in init, what happens in the loop, what happens in each ISR>
```

### Where each fragment goes

| CubeMX marker | What you add |
|---|---|
| `/* USER CODE BEGIN Includes */` | |
| `/* USER CODE BEGIN 2 */` | |
| `/* USER CODE BEGIN WHILE */` | |

Key API calls: `<e.g. HAL_TIM_Base_Start_IT() - why this variant>`

## 7. Bring-up and verification

### Incremental stages

| Stage | What to build | What you should observe | If it fails, suspect |
|---|---|---|---|
| 1 | `<empty project>` | `<debugger halts at main()>` | `<probe, clock config>` |

### Failure decision tree for this task

`<Trimmed decision tree relevant to the components used>`
