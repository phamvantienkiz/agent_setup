# Board reference — STM32F429I-DISC1

> **Status of this file.** Entries marked `[VERIFIED …]` carry a document and page
> citation and can be used directly. Entries marked `UNVERIFIED` are strong priors that
> **must be confirmed against the PDFs before they appear in a dossier without a warning**.
> When you verify one, edit this file: replace the marker with the citation. The second
> task on this board should be much cheaper than the first.

## Documentation set

Place these in `docs/boards/STM32F429I-DISC1/`. All are free from st.com.

| Suggested filename              | Document                                                        | What it answers                                                                          |
| ------------------------------- | --------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `discovery-UM1670.pdf`          | UM1670 — Discovery kit with STM32F429ZI MCU                     | On-board LEDs, buttons, connectors, jumpers, pin allocation, clock source                |
| `schematic-MB1075.pdf`          | Board schematic (MB1075)                                        | Exact circuit: active levels, pull resistors, series resistors                           |
| `datasheet-STM32F429xx.pdf`     | STM32F427xx/429xx datasheet                                     | Pinout, **alternate function mapping**, memory map, electrical limits                    |
| `reference-manual-RM0090.pdf`   | RM0090 — STM32F405/415/407/417/427/437/429/439 reference manual | Every peripheral's behaviour and registers, clock tree                                   |
| `programming-manual-PM0214.pdf` | PM0214 — Cortex-M4 programming manual                           | NVIC, SysTick, priorities, faults, FPU                                                   |
| `user-manual_UM3461.pdf`        | UM3461 — STM32F4 series user manual                             | STM32F4 series UL/CSA/IEC 60730-1/60335-1 self-test library user guide                   |
| `hal-description-UM1725.pdf`    | UM1725 — Description of STM32F4 HAL and LL drivers              | HAL function signatures and callbacks (optional — grepping the local headers is cheaper) |

Also worth having locally, though not a PDF: the **STM32CubeF4 firmware package**. Its
`Projects/STM32F429I-Discovery/Examples/` folder contains working, vendor-authored
examples for most peripherals on this exact board, and is a better reference than any
tutorial. Grep it before writing anything non-trivial.

## MCU

`STM32F429ZIT6`, Arm Cortex-M4F, LQFP144. Confirm flash/RAM sizes and the maximum
system clock in the datasheet's feature table before quoting them in a dossier.

## On-board resources — verification targets

Fill the citation column as you verify each row. Until then, present these to the user as
items to confirm.

| Resource             | Prior (UNVERIFIED unless cited)                                                                                                     | Where to verify                            | Citation |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ | -------- |
| Green user LED (LD3) | PG13, **active high** (anode to PG13 via 510Ω R26, cathode to GND)                                                                   | UM1670 §7.5 p.20, Table 7 p.29; MB1075 sheet 6 | `[UM1670 §7.5 p.20; MB1075 sh.6]` |
| Red user LED (LD4)   | PG14, **active high** (anode to PG14 via 680Ω R27, cathode to GND)                                                                   | UM1670 §7.5 p.20, Table 7 p.29; MB1075 sheet 6 | `[UM1670 §7.5 p.20; MB1075 sh.6]` |
| User button B1       | PA0, **active high** (pull-down R22 220kΩ to GND, push-button switches to VDD)                                                     | UM1670 §7.6 p.20, Table 7 p.24; MB1075 sheet 6 | `[UM1670 §7.6 p.20; MB1075 sh.6]` |
| Reset button B2      | NRST                                                                                                                                | UM1670 §7.6 p.20, Table 7 p.24; MB1075 sheet 6 | `[UM1670 §7.6 p.20; MB1075 sh.6]` |
| Debugger             | ST-LINK/V2-B, SWD on PA13 (SWDIO) / PA14 (SWCLK) — never reassign                                                                   | UM1670 §7.3 p.16-19; MB1075 sheet 2        | `[UM1670 §7.3 p.16-19]` |
| HSE clock            | **8 MHz supplied by the ST-LINK MCU's clock output (MCO), i.e. HSE must be configured as BYPASS, not Crystal**                      | UM1670 §7.12.1 p.22, Table 6 p.23; MB1075 sh.5 | `[UM1670 §7.12.1 p.22]` |
| LSE clock            | 32.768 kHz crystal footprint X2 is not fitted by default (SB16/17 ON, R53/54 OFF)                                                   | UM1670 §7.12.2 p.22, Table 6 p.23; MB1075 sh.5 | `[UM1670 §7.12.2 p.22]` |
| TFT LCD              | 2.4" QVGA, controller driven over SPI5 for commands plus the parallel LCD-TFT controller for pixels; consumes a large block of pins | UM1670 §7.9 p.21, Table 7 p.24-30          | `[UM1670 §7.9 p.21]` |
| External SDRAM       | 64 Mbit, on the flexible memory controller; consumes many pins on ports D/E/F/G                                                     | UM1670 §7.10 p.21, Table 7 p.24-30         | `[UM1670 §7.10 p.21]` |
| MEMS gyroscope       | L3GD20 (or I3G4250D on rev E01), shares SPI5 with the LCD on a separate chip select (PC1)                                           | UM1670 §7.8 p.21, Table 7 p.26             | `[UM1670 §7.8 p.21]` |
| USB                  | OTG Micro-AB (CN6), internal FS PHY (PB12=ID, PB14=DM, PB15=DP, PB13=VBUS, PC4=PSO, PC5=OC)                                        | UM1670 §7.7 p.20-21, Table 7 p.25-26       | `[UM1670 §7.7 p.20-21]` |
| Expansion headers    | All LQFP144 I/O brought out on P1 and P2                                                                                            | UM1670 §7.14 p.24-30                       | `[UM1670 §7.14 p.24]` |
| Virtual COM port     | Supported on STM32F429I-DISC1 via USART1 (PA9=TX, PA10=RX) connected to ST-LINK/V2-B U2 with SB11 & SB15 ON by default             | UM1670 §7.3.3 p.17, Table 6 p.23; MB1075 sh.2 | `[UM1670 §7.3.3 p.17]` |

## Pin-availability warning

A large fraction of this board's I/O is already committed to the LCD, the SDRAM and the
gyroscope. Before assigning any pin for an external sensor:

1. Find the pin-allocation table in UM1670 and check the pin is free.
2. Check it is brought out to an expansion header if a wire must be attached.
3. Only then check the alternate-function mapping in the datasheet.

Doing this in the other order wastes time: a pin can be perfectly capable of I2C1_SCL and
still be soldered to the SDRAM.

## Board-specific traps

1. **HSE = BYPASS.** The most common first failure on this board. Selecting "Crystal/
   Ceramic Resonator" makes `HAL_RCC_OscConfig()` time out, `SystemClock_Config()` calls
   `Error_Handler()`, and the board appears completely dead before a single line of user
   code runs. Symptom: debugger halts in an infinite loop, no LED activity at all.
2. **No virtual COM port.** `printf` to a terminal needs an external USB–TTL adapter on a
   USART, or SWO trace, or the debugger's Live Expressions. Plan this in Phase 2, not
   after the code is written.
3. **Button polarity.** Verify the active level in the schematic. Assuming active-low and
   configuring a pull-up gives a button that appears permanently pressed.
4. **"Initialize all peripherals with their default Mode?" = Yes** in the CubeMX board
   selector generates the entire LCD/SDRAM/gyro stack. That is useful when the task needs
   the display, and overwhelming when the task is to blink an LED. Choose deliberately and
   say why in the dossier.
5. **The 8 MHz HSE is shared with the debug MCU.** If the ST-LINK firmware is very old or
   the board is powered from the user USB port only, the clock may not be present. If a
   board that worked yesterday now dies in `Error_Handler()`, check the power path.

## Useful cached extracts

Once extracted, keep these under `docs/boards/STM32F429I-DISC1/.cache/` and reuse them:

| Cache file                     | Source pages                                  | Used by                                                         |
| ------------------------------ | --------------------------------------------- | --------------------------------------------------------------- |
| `ds-alternate-function-map.md` | datasheet, "Alternate function mapping" table | every task that uses a communication peripheral or timer output |
| `um-leds-buttons.md`           | UM1670 LED and button sections                | every task                                                      |
| `um-pin-allocation.md`         | UM1670 pin allocation table                   | every task that adds an external device                         |
| `um-clock-source.md`           | UM1670 clock section                          | every task                                                      |
| `rm-clock-tree.md`             | RM0090 RCC clock tree figure and limits       | every task                                                      |
| `rm-exti.md`                   | RM0090 EXTI chapter                           | any task with a pin interrupt                                   |
