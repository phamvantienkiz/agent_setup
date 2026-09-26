# Task input — <short title>

> Copy this file to `tasks/<task-id>/input.md` and fill it in. Only section 1 is
> mandatory; leave anything you do not know blank and the agent will either derive it or
> list it as an assumption. Writing "I don't know" is more useful than guessing — it tells
> the agent to explain that part rather than assume you already understand it.

---

## 1. The assignment, verbatim

<!-- Paste the original wording exactly, in whatever language it was given. Do not
     paraphrase — ambiguities in the original are information the agent needs. -->

```
<paste here>
```

## 2. My understanding of it, in my own words

<!-- One or two sentences. If your restatement turns out to differ from the agent's,
     that gap is exactly what is worth discussing before any code is written. -->

## 3. Hardware

- Board: `STM32F429I-DISC1`
- External components attached (module, how it connects, any wiring already decided):
  - <e.g. "MPU6050 on a breakout, I2C, not yet wired">
  - <e.g. "none — on-board LED and button only">
- Anything I must NOT use (pin reserved, peripheral used by another exercise):

## 4. Constraints from the assignment

- [ ] Specific timing stated: <e.g. "exactly 500 ms", "response within 10 ms">
- [ ] A required technique: <e.g. "must use a timer interrupt", "must use DMA",
      "must not use HAL_Delay", "register-level, no HAL">
- [ ] A required peripheral: <e.g. "must use TIM3">
- [ ] Output must be observable as: <LED / terminal / LCD / scope>
- [ ] Deadline or scope limit:

## 5. What I already have working

<!-- Helps the agent skip ground you have covered and start from your actual state. -->

- <e.g. "blink with HAL_Delay works; EXTI I have never used">
- Existing project I want to extend: <path, or "starting fresh">

## 6. What I want out of this

<!-- Tick what applies; the agent adjusts depth accordingly. -->

- [ ] Full design dossier + reference `main.c`  (default)
- [ ] Extra explanation of <peripheral/concept> — I have not used it before
- [ ] Register-level explanation alongside the HAL calls
- [ ] Just the CubeMX configuration, I will write the code myself
- [ ] Review of code I already wrote (attach it)

## 7. Open questions I have

<!-- Anything you are confused about. These get answered explicitly in the dossier
     rather than being buried in the design. -->

1.
2.
