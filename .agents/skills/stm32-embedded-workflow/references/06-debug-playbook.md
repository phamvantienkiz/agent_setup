# Phase 8 — Bring-up and debug playbook

Every dossier ends with this phase, filled in for the specific task. The point is that
the user never faces a board that "does nothing" without a next move.

## Incremental bring-up order

Never write the whole application and then flash it. Build it in stages that each produce
an observable result, so a failure has only one possible new cause:

1. **Empty project flashes and the debugger halts at `main()`.** Proves toolchain, probe,
   power, and `SystemClock_Config()`.
2. **One GPIO output toggles** (blocking delay is fine here). Proves clock configuration
   is actually running at the expected speed and the pin map is right.
3. **One input reads correctly**, observed in Live Expressions. Proves pull configuration
   and active level.
4. **Each peripheral alone**: timer interrupt firing, UART sending a banner, ADC
   returning a plausible number. One at a time.
5. **Integration** — combine, then re-check timing.

State in the dossier what each stage should look like on the bench, e.g. "LED visibly
toggles about twice a second; if it is far faster or slower, the clock configuration is
wrong, not the delay constant."

## Tools, in the order to reach for them

| Tool | Best for | Notes |
|---|---|---|
| **Live Expressions** | Watching variables change while running | Lowest friction; start here |
| **Breakpoints + step** | Confirming control flow reaches a branch | Breaking inside an ISR distorts timing |
| **SFR / peripheral register view** | "Is the peripheral actually configured and running?" | Read `TIMx->CNT`, `GPIOx->ODR`, status registers |
| **SWV / ITM trace** | Low-overhead `printf` and event timing | Needs the correct core clock in trace settings |
| **UART terminal** | Long logs, running untethered | Baud must match; common ground required |
| **Logic analyser / oscilloscope** | Anything the MCU claims to be outputting but the peripheral does not receive | The only way to settle I2C/SPI disputes |

## Failure decision tree

```
Nothing happens after flashing
│
├─ Debugger will not connect
│    ├─ Correct USB port (debug port, not the device/user port)?
│    ├─ Debug Configuration → Debugger → "Connect under reset"
│    └─ SYS Debug was left disabled in CubeMX → hold RESET while starting the flash
│
├─ Halts inside Error_Handler()
│    └─ Breakpoint there, inspect the call stack. Almost always SystemClock_Config():
│       wrong HSE type (crystal vs bypass), PLL values out of range, or a missing
│       voltage-scaling/flash-latency step for the requested frequency.
│
├─ Lands in HardFault_Handler()
│    ├─ Using a peripheral whose clock was never enabled
│    ├─ Null or dangling pointer, array overrun, stack overflow
│    ├─ Unaligned access, or a DMA buffer that went out of scope
│    └─ Inspect the stacked PC/LR per the core programming manual's fault section
│
├─ Reaches while(1) but the output does nothing
│    ├─ Pin number matches the board user manual?
│    ├─ Active level correct (does driving it low turn the LED on)?
│    ├─ Port clock enabled — was MX_GPIO_Init() actually called?
│    └─ Watch GPIOx->ODR in the SFR view: if the bit toggles and the LED does not,
│       the fault is downstream (wrong pin, wiring, or hardware)
│
├─ Timer interrupt never fires
│    ├─ HAL_TIM_Base_Start_IT() used, not HAL_TIM_Base_Start()?
│    ├─ NVIC line enabled in CubeMX?
│    ├─ Clock source set to Internal Clock?
│    ├─ Callback name spelled exactly right?
│    └─ Check TIMx->CNT in the SFR view: not incrementing ⇒ the timer is not running;
│       incrementing but no callback ⇒ the interrupt path is the problem
│
├─ Timing is wrong by a constant factor
│    ├─ Factor of 2 → the APB timer-clock doubling rule
│    ├─ Off by one tick → PSC/ARR entered as period instead of period − 1
│    └─ Actual HCLK differs from the CubeMX assumption → verify with a scope on MCO,
│       or toggle a pin in a known loop and measure
│
├─ UART prints garbage
│    ├─ Baud mismatch, or the system clock changed after the UART was configured
│    ├─ TX/RX not crossed, or no common ground
│    ├─ 3.3 V vs 5 V logic level mismatch
│    └─ Sending from an ISR while another transmission is in progress
│
├─ I2C device never answers (HAL_BUSY / HAL_ERROR / AF flag)
│    ├─ 7-bit address must be shifted left by one for the HAL API
│    ├─ Pull-up resistors present on SDA and SCL?
│    ├─ Pins configured as open-drain with the correct alternate function?
│    └─ Scan the bus by probing every address with HAL_I2C_IsDeviceReady()
│
├─ SPI reads all 0x00 or all 0xFF
│    ├─ CPOL/CPHA mode mismatch with the device datasheet
│    ├─ Chip select not asserted, or asserted for the wrong duration
│    ├─ Clock too fast for the device
│    └─ MISO/MOSI swapped
│
└─ Works with the debugger attached, fails standalone
     ├─ Timing that depended on debugger-induced delays (race condition)
     ├─ An uninitialised variable that happened to be zero under the debugger
     └─ Power-supply or brown-out difference between the two setups
```

## Verification checklist

Close the dossier with the concrete, observable acceptance criteria written back in
Phase 1, each one phrased as something the user can look at:

- [ ] `<observable behaviour>` — expected: `<what it should look like>`
- [ ] `<measurement>` — expected: `<value ± tolerance>`, measured with `<tool>`

If a criterion cannot be observed without extra equipment, say so and offer a proxy
(e.g. toggle a spare pin at the same rate and watch it, instead of measuring an internal
period directly).
