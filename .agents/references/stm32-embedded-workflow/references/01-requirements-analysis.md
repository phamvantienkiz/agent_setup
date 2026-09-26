# Phase 1–2 — From prose to peripherals

## Step 1: Restate the problem in one sentence

Write the assignment back in your own words, in one sentence, before anything else. If
you cannot, the problem statement is ambiguous — note the ambiguity in the assumptions
table rather than guessing silently.

## Step 2: Fill the I/O table

Every embedded problem decomposes into: what comes in, what goes out, how often, and
what state must be remembered between events.

| Field | Questions to answer |
|---|---|
| **Inputs** | What does the system sense? Digital or analog? Event-driven or sampled? At what rate? What is the electrical nature (switch, open-drain sensor, 0–3.3 V, differential)? |
| **Outputs** | What does the system actuate or report? Digital, analog, PWM, serial stream? At what rate? What current does it need? |
| **Timing constraints** | Any stated period, deadline, or latency? Words like "every", "after", "within", "immediately", "simultaneously" are constraints. |
| **State** | What must persist between events? Mode flags, counters, last-sample buffers, calibration. |
| **Done criteria** | What observable behaviour proves the assignment is complete? Write this before designing — it becomes the verification checklist in Phase 8. |

## Step 3: Translate verbs to peripherals

Read the statement, underline the verbs and nouns of action, and map them:

| Phrase in the problem | Peripheral | Notes |
|---|---|---|
| turn on/off an LED, drive a relay | GPIO Output (push-pull) | Check current limit if not an on-board LED |
| read a button, switch, limit sensor | GPIO Input + pull-up/down | Needs debouncing |
| "immediately when pressed", "as soon as" | GPIO + EXTI | A polled loop can miss or lag the event |
| "every N ms", "after N seconds", "periodically" | TIM with update interrupt, or `HAL_GetTick()` scheduler | Timer when accuracy matters or the main loop is busy |
| "measure the time between", "pulse width", "frequency of" | TIM Input Capture | |
| "dim", "vary brightness", "motor speed", "servo angle", "buzzer tone" | TIM PWM output channel | |
| "count pulses", "rotary encoder", "tachometer" | TIM in counter or encoder mode | |
| read a potentiometer, LDR, thermistor, analog sensor | ADC | 12-bit; result scales against VREF+ |
| "output an analog voltage", "generate a waveform" | DAC | |
| talk to a PC, `printf`, GPS/Bluetooth module, modem | USART/UART | Check whether the board has a virtual COM port; many Discovery boards do not |
| digital sensor with two wires labelled SCL/SDA, OLED, EEPROM | I2C | 7-bit address must be shifted left by 1 for HAL |
| sensor/display with SCK/MOSI/MISO/CS, SD card, on-board MEMS | SPI | |
| "without loading the CPU", continuous sampling, large transfers | DMA | Pair with the peripheral's own interrupt |
| on-board graphical LCD | LTDC + external RAM controller + an SPI control channel | Use the vendor BSP rather than driving it by hand |
| date/time, wake from low power at a set time | RTC | Needs a low-speed clock source |
| "recover if the program hangs" | IWDG/WWDG | |
| "sleep", "low power", battery | Low-power modes + wake sources | |

Anything you cannot map goes into the open-questions list. Do not silently drop a
requirement.

## Step 4: Choose the processing model per signal

For each input/output pair, choose exactly one and record *why*:

| Model | Use when | Cost |
|---|---|---|
| **Polling** | Simple, no hard deadline, single activity, learning a new peripheral | Burns CPU, can miss short events, poor composability |
| **Interrupt** | Asynchronous events, deadlines in the microsecond–millisecond range, several concurrent activities | Needs `volatile`, priority planning, ISR discipline |
| **DMA** | Continuous or bulk data, sample rates the CPU should not babysit, low jitter needed | More configuration, buffer lifetime and cache/coherency care |

Escalation rule: start at the left, move right only when the requirement forces it, and
name the forcing requirement in the dossier. "We use a timer interrupt because the log
transmission would otherwise delay the LED period by up to 8 ms" is a good justification.
"We use DMA because it is better" is not.

## Step 5: Sketch the state machine if there is one

If the problem mentions modes, sequences, or "when X then Y until Z", draw the states and
transitions before writing code. Three or more modes almost always means an explicit
`enum` state variable plus a `switch` in the main loop — far easier to debug than nested
boolean flags.

## Output of this phase

A table of the form:

| Requirement | Peripheral | Model | Parameters to compute later |
|---|---|---|---|
| LED blinks at 500 ms | GPIO output + tick scheduler | non-blocking poll | period constant |
| Button changes mode | GPIO input + EXTI | interrupt | edge, pull direction, debounce window |
| Log once per second | USART | polling transmit | baud rate |

Pin numbers do **not** appear yet. That is Phase 3, and mixing the two is what makes
beginners open CubeMX too early.
