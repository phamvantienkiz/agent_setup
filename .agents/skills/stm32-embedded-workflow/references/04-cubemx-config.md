# Phase 6 — STM32CubeMX configuration checklist

The dossier's CubeMX section must be a literal click path with the values filled in, in
this order. The order matters: later steps depend on earlier ones, and CubeMX will
silently accept an inconsistent configuration.

## The ordered checklist template

```
□  1. New project
      File → New → STM32 Project → "Board Selector" tab → <board name> → Next
      "Initialize all peripherals with their default Mode?"
        → No   (recommended while learning; you configure only what the task needs)
        → Yes  (only when the task needs the on-board LCD/SDRAM/sensor stack)
      Project name: <task-id>   Language: C   Toolchain: STM32CubeIDE

□  2. System Core → RCC
      High Speed Clock (HSE): <Crystal/Ceramic Resonator | BYPASS Clock Source | Disable>
        → value for this board: <from board reference file, cited>
      Low Speed Clock (LSE):  <Disable unless RTC is used>

□  3. System Core → SYS
      Debug: Serial Wire        ← omitting this locks out the debugger after the first flash
      Timebase Source: SysTick  (change only if a timer is needed for HAL timebase)

□  4. Clock Configuration tab
      Type <target HCLK> into the HCLK field and press Enter; let the solver fill PLL.
      Record: SYSCLK = ___  HCLK = ___  PCLK1 = ___  PCLK2 = ___
              APB1 Timer clocks = ___   APB2 Timer clocks = ___
      No field may be red.

□  5. GPIO pins   (one row per pin from the dossier pin map)
      Click pin <PXn> in the chip view → select <GPIO_Output | GPIO_Input | GPIO_EXTIn>
      System Core → GPIO → select the pin → set:
        GPIO output level: <Low|High>
        GPIO mode: <Output Push Pull | Output Open Drain | External Interrupt Mode with ...>
        GPIO Pull-up/Pull-down: <No pull | Pull-up | Pull-down>
        Maximum output speed: <Low|Medium|High|Very High>
        User Label: <NAME>        ← generates NAME_GPIO_Port / NAME_Pin in main.h

□  6. Communication peripherals (UART / I2C / SPI)
      <PERIPH> → Mode: <mode>
      Parameter Settings: <field> = <value>  (baud rate, word length, parity, stop bits,
                                              clock speed, prescaler, CPOL/CPHA, ...)
      Verify the auto-assigned pins match the dossier pin map; if not, click the pin and
      reassign manually.

□  7. Timers
      TIMx → Clock Source: Internal Clock      ← without this the timer never counts
      Prescaler (PSC − 1 in the field): <value>
      Counter Period (ARR − 1 in the field): <value>
      auto-reload preload: <Enable|Disable>
      For PWM: Channel<n> → PWM Generation CH<n>, then Pulse (CCR) = <value>

□  8. Analog
      ADCx → IN<k> checked; Resolution, Scan/Continuous mode, Sampling Time = <value>
      Regular Conversion Rank list matches the channel order in the dossier

□  9. NVIC Settings (per peripheral tab, or System Core → NVIC)
      Enable: <EXTI line n interrupt | TIMx global interrupt | USARTx global interrupt | DMAx Streamy>
      Preemption priority: <n>   Sub priority: <n>
      Keep user interrupts numerically above (lower priority than) SysTick unless there
      is a stated reason, so HAL_Delay and timeouts keep working.

□ 10. DMA Settings (if used)
      Add → Request: <request>  Stream: <auto>  Direction: <...>
      Mode: <Normal | Circular>   Data width: <Byte|Half Word|Word>  Increment: <...>
      Enabling DMA also requires the peripheral's own global interrupt enabled in NVIC.

□ 11. Project Manager → Code Generator
      ☑ Generate peripheral initialization as a pair of .c/.h files per peripheral
      ☑ Keep User Code when re-generating
      ☐ Delete previously generated files when not re-generated

□ 12. GENERATE CODE (Alt+K) → Open Project
```

## Reading the generated project

Point the user at these, in order, so the structure stops being a black box:

| File | Role | User edits? |
|---|---|---|
| `Core/Src/main.c` | `main()`, `SystemClock_Config()`, all `MX_*_Init()` | Yes — only inside USER CODE blocks |
| `Core/Inc/main.h` | Pin labels from step 5 become `NAME_Pin` / `NAME_GPIO_Port` | Rarely |
| `Core/Src/stm32xxxx_it.c` | Interrupt service routines that call HAL handlers | Yes — but prefer HAL callbacks in main.c |
| `Core/Src/stm32xxxx_hal_msp.c` | Low-level init: peripheral clock enables, AF pin setup, DMA linkage | No — regenerate instead |
| `Core/Startup/startup_*.s` | Vector table; useful for looking up exact IRQ handler names | No |
| `Drivers/` | HAL and CMSIS | Never |

`main()` calls, in this fixed order: `HAL_Init()` → `SystemClock_Config()` →
`MX_GPIO_Init()` → other `MX_*_Init()` → `while(1)`. If `SystemClock_Config()` fails, the
program lands in `Error_Handler()` before any user code runs — which looks identical to
"nothing works".

## Configuration traps worth warning about every time

1. **Wrong HSE source type.** Boards that feed the MCU from the debugger's clock output
   need *BYPASS*, not *Crystal*. Choosing wrong makes `HAL_RCC_OscConfig()` fail and the
   program die in `Error_Handler()`.
2. **SYS → Debug not set to Serial Wire.** The debug pins are reassigned as plain GPIO
   and the probe cannot reconnect. Recovery: "Connect under reset" in the debug
   configuration, or hold the reset button while starting the flash.
3. **Timer clock source left as "Disable"/internal not selected** — the timer is
   configured but never counts.
4. **PSC/ARR entered as the period instead of period − 1.** The CubeMX field is the
   register value; the register counts from zero.
5. **Interrupt enabled in the peripheral but not in NVIC** (or the reverse) — callbacks
   never fire, or the flag is set but nothing services it.
6. **Editing outside USER CODE blocks**, then regenerating, then losing everything.
7. **Reassigned pins after enabling a peripheral**: CubeMX picks a default pin set that
   may collide with something already wired on the board. Always compare against the
   dossier pin map before generating.
8. **Forgetting that a second peripheral needs the pin you just took.** CubeMX shows
   conflicts, but only for peripherals it knows about — it knows nothing about the
   board-level wiring in the user manual.

## What to write in the dossier

Reproduce the checklist above with every `<...>` replaced by a concrete value for this
task, and delete the steps that do not apply. A step that says "configure the UART" is
useless; a step that says "USART1 → Mode: Asynchronous; Baud Rate: 115200; Word Length:
8 Bits; Parity: None; Stop Bits: 1; check PA9/PA10 assignment" is what makes the user
independent.
