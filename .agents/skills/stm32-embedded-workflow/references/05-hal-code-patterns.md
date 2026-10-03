# Phase 7 — HAL code patterns

The code you emit is read by someone who will retype it into their own generated project.
Optimise for comprehension and for correct placement, not for cleverness.

## Placement rules

All user code lives between CubeMX's markers. Use the exact marker names so the user
knows where each fragment belongs:

| Marker | Contents |
|---|---|
| `/* USER CODE BEGIN Includes */` | `#include <stdio.h>`, `<string.h>`, project headers |
| `/* USER CODE BEGIN PTD */` | typedefs, enums (state machines) |
| `/* USER CODE BEGIN PD */` | `#define` constants |
| `/* USER CODE BEGIN PV */` | global/`volatile` variables |
| `/* USER CODE BEGIN PFP */` | private function prototypes |
| `/* USER CODE BEGIN 0 */` | helper function definitions |
| `/* USER CODE BEGIN 2 */` | one-time setup after all `MX_*_Init()`: start timers, arm interrupts, print banner |
| `/* USER CODE BEGIN WHILE */` … `/* USER CODE END WHILE */` | the body of the main loop |
| `/* USER CODE BEGIN 4 */` | HAL callbacks (`HAL_TIM_PeriodElapsedCallback`, `HAL_GPIO_EXTI_Callback`, …) |
| `/* USER CODE BEGIN Error_Handler_Debug */` | a visible failure indication instead of a silent hang |

Never reproduce the generated `MX_*_Init()` bodies in the output — reference the dossier's
CubeMX section instead. Reproducing them tempts the user to paste over generated code and
creates drift the next time they regenerate.

## Arming peripherals in USER CODE BEGIN 2

CubeMX initialises peripherals but does not start most of them. The common forgotten calls:

```c
HAL_TIM_Base_Start_IT(&htim3);                 /* periodic update interrupt */
HAL_TIM_PWM_Start(&htim4, TIM_CHANNEL_1);      /* PWM output               */
HAL_UART_Receive_IT(&huart1, &rx_byte, 1);     /* arm first RX; re-arm in callback */
HAL_ADC_Start_DMA(&hadc1, adc_buf, ADC_BUF_LEN);
```

## The non-blocking main loop

Prefer this over chains of `HAL_Delay()` as soon as there is more than one activity. It is
the natural stepping stone to an RTOS and it makes timing bugs visible instead of hidden.

```c
while (1)
{
    uint32_t now = HAL_GetTick();

    if (now - t_blink >= BLINK_PERIOD_MS) {     /* wrap-safe unsigned comparison */
        t_blink = now;
        HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
    }

    if (now - t_log >= LOG_PERIOD_MS) {
        t_log = now;
        /* ... */
    }

    if (flag_event) {                            /* set by an ISR */
        flag_event = 0;
        /* handle it here, in thread context, where blocking is allowed */
    }
}
```

Write `now - t >= period`, never `now >= t + period`: the first is correct across the
`uint32_t` wrap, the second is not.

## Interrupt discipline

Rules to state explicitly in the code comments, because they are the difference between
working firmware and an intermittent hang:

- An ISR sets a flag or moves one item of data. Everything else happens in the main loop.
- No `HAL_Delay()`, no blocking transmit, no `printf`, no long loops inside an ISR.
- Any variable shared between an ISR and the main loop is `volatile`. Anything wider than
  a machine word, or any multi-field structure, needs the read in the main loop protected
  (disable the interrupt briefly, or use a double-buffer / flag handshake).
- Keep user interrupt priorities numerically higher than SysTick's unless there is a
  reason, so HAL timeouts and `HAL_Delay()` keep working inside them.

## HAL callbacks

These are `__weak` in the driver; defining one in `main.c` overrides it. Always check
the instance, because one callback serves every instance of that peripheral.

```c
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    if (htim->Instance == TIM3) { /* ... */ }
}

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    if (GPIO_Pin == BTN_Pin) { /* ... */ }
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART1) {
        rx_ready = 1;
        HAL_UART_Receive_IT(huart, &rx_byte, 1);   /* re-arm, or reception stops */
    }
}

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc) { /* DMA full buffer  */ }
void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef *hadc) { /* first half   */ }
void HAL_UART_ErrorCallback(UART_HandleTypeDef *huart) { /* recover + re-arm */ }
```

A misspelled callback name compiles cleanly and is simply never called — if a callback
"does not fire", check the spelling before anything else.

## Debouncing

Time-based rejection is enough for assignments and is honest about what it does:

```c
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    static uint32_t last_edge = 0;
    uint32_t now = HAL_GetTick();
    if (GPIO_Pin == BTN_Pin && (now - last_edge) > DEBOUNCE_MS) {
        last_edge = now;
        flag_button = 1;
    }
}
```

`DEBOUNCE_MS` of 20–50 ms suits mechanical switches; 200 ms suits "one action per
deliberate press". Say which intent you chose.

## State machines

Three or more modes means an explicit state variable, not nested booleans:

```c
typedef enum { ST_IDLE, ST_MEASURING, ST_REPORTING } app_state_t;
static app_state_t state = ST_IDLE;

switch (state) {
    case ST_IDLE:      if (flag_start) { state = ST_MEASURING; } break;
    case ST_MEASURING: /* ... */                                  break;
    case ST_REPORTING: /* ... */ state = ST_IDLE;                 break;
}
```

## Error handling

`Error_Handler()` as generated is a silent infinite loop. Make failure observable:

```c
void Error_Handler(void)
{
  __disable_irq();
  /* USER CODE BEGIN Error_Handler_Debug */
  while (1) {
      /* fast blink of the error LED via direct register write, since HAL may be unusable */
  }
  /* USER CODE END Error_Handler_Debug */
}
```

Also check return codes on the calls that can genuinely fail at runtime — `HAL_I2C_*`,
`HAL_SPI_*`, `HAL_UART_Receive` with a timeout — rather than casting them to `void`.

## printf

Three options, in increasing order of setup cost. Pick one and say why:

1. **Debugger Live Expressions / watch window** — zero setup, no wiring, best while
   learning. Cannot log history.
2. **SWO / ITM trace** — one already-present debug pin, viewable in the IDE's trace
   console. Needs the correct core clock entered in the trace settings.
3. **UART to a terminal** — needs a physical port; retarget `_write()` so `printf` works:

```c
int _write(int file, char *ptr, int len)
{
    HAL_UART_Transmit(&huart1, (uint8_t *)ptr, len, HAL_MAX_DELAY);
    return len;
}
```

Note the cost: `printf` with float support pulls in a large library and a blocking
transmit at 115200 takes roughly 87 µs per character. In a tight control loop, buffer and
send outside the deadline, or use DMA.
