# Phase 5 — Clock tree and timing math

Do this on paper (in the dossier) before touching CubeMX. Every number the user types
into CubeMX should already exist here, with the derivation beside it.

## The clock chain (STM32F4 family shape)

```
clock source  ──►  PLL  ──►  SYSCLK  ──►  AHB prescaler ──► HCLK ──► CPU, SysTick, DMA, GPIO
 HSE / HSI                                 ├─ APB1 prescaler ──► PCLK1 ──► low-speed peripherals
                                           └─ APB2 prescaler ──► PCLK2 ──► high-speed peripherals
```

PLL on F4:

```
f_VCO_in  = f_HSE / M          (keep in the range the RM specifies, typically 1–2 MHz)
f_VCO_out = f_VCO_in × N       (must stay inside the RM's VCO range)
SYSCLK    = f_VCO_out / P
f_USB/SDIO/RNG = f_VCO_out / Q (48 MHz needed for USB full-speed)
```

Verify the legal ranges for M/N/P/Q and the maximum HCLK/PCLK1/PCLK2 for the specific
part in the reference manual RCC chapter and the datasheet — they differ between
families and even between lines in the same family.

### The timer clock doubling rule

This single rule causes more wrong blink rates than anything else:

> If an APB prescaler is **1**, the timers on that bus run at PCLKx.
> If it is **anything other than 1**, the timers on that bus run at **PCLKx × 2**.

So a system with `APB1 = /4` giving PCLK1 = 45 MHz feeds its APB1 timers at **90 MHz**,
not 45 MHz. Always state the timer input clock explicitly in the dossier, derived, before
computing PSC/ARR. CubeMX shows this value in the Clock Configuration view as
"APBx Timer clocks" — quote it.

## Timer period

```
f_tick   = f_timer_clk / (PSC + 1)
T_period = (ARR + 1) / f_tick
```

Choosing values: pick PSC so that `f_tick` is a round number (1 MHz, 100 kHz or 10 kHz
are convenient), then solve ARR. Check ARR fits the counter width (16-bit timers cap at
65535; some timers are 32-bit — confirm in the RM).

**Worked example.** Target 500 ms on a timer clocked at 90 MHz.

```
choose f_tick = 10 kHz  →  PSC + 1 = 90 000 000 / 10 000 = 9000  →  PSC = 8999
500 ms = 5000 ticks      →  ARR + 1 = 5000                      →  ARR = 4999
check: ARR = 4999 ≤ 65535 ✓
verify: (4999+1) / (90e6 / 9000) = 5000 / 10000 = 0.5 s ✓
```

Always include the verification line. It catches off-by-one errors in the `+1`s.

## PWM

```
f_PWM = f_timer_clk / ((PSC + 1) × (ARR + 1))
duty  = CCR / (ARR + 1)
```

Resolution is `ARR + 1` steps, so trade frequency against resolution deliberately: a
higher ARR gives finer duty control but lower maximum frequency. For LED dimming, 500 Hz
to 2 kHz with ARR = 999 (0.1 % steps) is comfortable. For servos, the convention is a
20 ms period with a 1–2 ms pulse, so aim for `f_tick = 1 MHz`, `ARR = 19999`,
`CCR = 1000..2000`.

## UART

The HAL computes the divisor; what matters is checking feasibility:

```
divisor = f_PCLKx / (8 × (2 − OVER8) × baud)
```

Practical checks:
- Error should stay under ~2 % for reliable framing. CubeMX flags bad combinations.
- The peripheral's clock is PCLK1 or PCLK2 depending on which USART — confirm on the bus
  table, since USART1/6 usually sit on the faster bus while USART2/3 and UART4/5 sit on
  the slower one.
- If the system clock is later changed, the baud divisor changes too. This is why "it
  worked, then I changed the PLL and got garbage on the terminal" happens.

## ADC

```
T_conversion = (T_sampling + T_resolution) × (1 / f_ADC)
```

where `T_sampling` is the programmed sample time in ADC clock cycles and `T_resolution`
is the conversion time in cycles for the chosen resolution (12 cycles at 12-bit on F4).
`f_ADC = PCLK2 / ADC_prescaler`, capped at the datasheet maximum — exceeding it silently
degrades accuracy rather than failing loudly.

Converting a reading:

```
V_in = raw × VREF+ / (2^resolution − 1)
```

Source impedance matters: a high-impedance source needs a longer sampling time so the
internal sample capacitor can charge. The datasheet gives the maximum source impedance
per sampling time — cite it when the task involves anything other than a low-impedance
divider.

## SysTick

HAL configures SysTick for a 1 ms tick by default, which is what `HAL_Delay()` and
`HAL_GetTick()` use. Two consequences worth stating in the dossier:

- `HAL_Delay()` inside an interrupt with priority higher than SysTick will hang forever,
  because the tick can no longer increment.
- `HAL_GetTick()` returns a `uint32_t` of milliseconds and wraps after ~49.7 days. The
  comparison `(now - last) >= period` with unsigned arithmetic is wrap-safe; the
  comparison `now >= last + period` is not. Always use the first form.

## Timing budget sanity check

Before finishing this phase, sum up the worst-case work in the main loop and in every
ISR, and compare it against the tightest deadline in the requirements. A 1 ms timer
interrupt plus a blocking 115200-baud transmission of 40 characters (~3.5 ms) is a
design error that will show up as jitter — catch it here, not in the lab.
