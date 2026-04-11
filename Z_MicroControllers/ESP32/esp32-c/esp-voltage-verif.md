# ESP32 Voltage Measurement — Explained

How to read supply or battery voltage on an ESP32 and why each design decision was made.

---

## Why you can't read VCC directly

The ESP32 ADC pins accept **0–3.3V maximum**. If you connect a LiPo battery (up to 4.2V) or a USB 5V rail directly to an ADC pin you will damage the ESP32.


You need to scale the voltage down first.

---

## The voltage divider

Two resistors in series between V_in and GND, with the ADC pin tapped in the middle:

```
V_in ──┬── R1 (100kΩ) ──┬── R2 (100kΩ) ── GND
                         │
                       GPIO35
                     (ADC reading)
```

The ADC sees a fraction of V_in:

```
V_measured = V_in × R2 / (R1 + R2)
```

With R1 = R2 = 100kΩ this divides by 2, so:

| V_in | V at GPIO35 |
|------|-------------|
| 3.3V (Pico/ESP regulated) | 1.65V ✅ |
| 4.2V (LiPo full) | 2.1V ✅ |
| 5.0V (USB) | 2.5V ✅ |
| 6.6V (max safe) | 3.3V ⚠️ limit |

To recover V_in in code:

```cpp
float voltage = v_measured * (R1 + R2) / R2;
// = v_measured * 2.0  (for equal resistors)
```

### Why 100kΩ and not smaller?

High-value resistors draw less current (50µA at 5V vs 5mA at 1kΩ), which matters when running on battery. The ESP32 ADC input impedance is high enough that 100kΩ source impedance doesn't affect accuracy.

---

## Why GPIO35

The ESP32 has two ADC units:

| Unit | Pins | WiFi safe? |
|------|------|-----------|
| ADC1 | GPIO32–GPIO39 | ✅ Yes |
| ADC2 | GPIO0, 2, 4, 12–15, 25–27 | ❌ No — disabled when WiFi is active |

**Always use ADC1 pins for anything that needs to work alongside WiFi.**

GPIO35 is also input-only (no internal pull-up/down), which makes it clean for analog reading.

---

## ADC accuracy and calibration

The ESP32 ADC is **not highly accurate out of the box**:

- Non-linear response, especially near 0V and 3.3V
- Typical error: ±5–10% uncalibrated
- Usable range with 11dB attenuation: ~0.15V to 3.1V (not the full 3.3V)

The script uses two techniques to improve this:

**1. `esp_adc_cal` — Espressif's built-in calibration:**
```cpp
esp_adc_cal_characterize(ADC_UNIT_1, ADC_ATTEN_DB_11,
                         ADC_WIDTH_BIT_12, ADC_REF_MV, &adcChars);
// then:
uint32_t mv = esp_adc_cal_raw_to_voltage(raw, &adcChars);
```
This corrects for the non-linear ADC curve using the internal 1100mV reference. Brings error down to ~±1–2%.

**2. Averaging 16 samples:**
```cpp
for (int i = 0; i < ADC_SAMPLES; i++) raw += analogRead(ADC_PIN);
raw /= ADC_SAMPLES;
```
Reduces random noise from the ADC. More samples = smoother reading.

---

## Attenuation settings

Attenuation controls the ADC's input voltage range:

| Setting | Input range | Use when |
|---------|-------------|----------|
| `ADC_0db` | 0–1.1V | Very low voltage signals |
| `ADC_2_5db` | 0–1.5V | |
| `ADC_6db` | 0–2.2V | |
| `ADC_11db` | 0–3.1V | **Most cases — use this** |

The script uses `ADC_11db` so it can read up to ~3.1V at the pin (which covers up to ~6.2V on V_in with the ÷2 divider).

---

## If you need higher accuracy

The ESP32 ADC is fine for battery monitoring (you don't need 0.01V precision to know a LiPo is at 3.7V). But if you need better accuracy, use an external ADC over I2C:

| Chip | Resolution | Range | Notes |
|------|-----------|-------|-------|
| **ADS1115** | 16-bit | ±6.144V | Best choice, I2C, very common |
| MCP3221 | 12-bit | 0–VCC | Simple, single channel |
| INA219 | 12-bit | 0–26V | Also measures current |

---

## MQTT topic

```
esp32/voltage/supply   →   4.132  (volts, 3 decimal places)
```

Subscribe to verify:
```sh
mosquitto_sub -h 192.168.1.2 -t "esp32/voltage/#" -v
```

---

## Full wiring summary

```
Battery/Supply (+) ──── R1 (100kΩ) ──── GPIO35 ──── R2 (100kΩ) ──── GND
                                            │
                                      ADC reads here
                                      (0 to 3.1V max)
```

| Connection | Detail |
|---|---|
| R1 | 100kΩ, between V_in and GPIO35 |
| R2 | 100kΩ, between GPIO35 and GND |
| ADC pin | GPIO35 (ADC1, input-only, WiFi-safe) |
| Max V_in | 6.6V (with equal resistors) |
| Publish interval | Every 10s (voltage changes slowly) |
