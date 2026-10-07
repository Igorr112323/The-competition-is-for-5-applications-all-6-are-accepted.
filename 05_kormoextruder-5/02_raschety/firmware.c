#include <stdint.h>
#include <math.h>

#define TEMP_TARGET 130
#define TEMP_HYSTERESIS 5
#define SCREW_RPM_MAX 400
#define PRESSURE_MAX 30.0f
#define CYCLE_MS 500

typedef struct {
    float barrel_temp;
    float die_pressure;
    float screw_rpm;
    float motor_current;
    uint8_t heater_on;
    uint8_t motor_on;
    uint8_t alarm;
    uint32_t total_kg;
    uint32_t runtime_s;
} ExtruderState;

static ExtruderState ext;

void temp_control(float target) {
    if (ext.barrel_temp < target - TEMP_HYSTERESIS) {
        ext.heater_on = 1;
    } else if (ext.barrel_temp > target + TEMP_HYSTERESIS) {
        ext.heater_on = 0;
    }
}

void pressure_monitor(void) {
    if (ext.die_pressure > PRESSURE_MAX) {
        ext.alarm = 1;
        ext.motor_on = 0;
        ext.screw_rpm = 0;
    }
}

void motor_control(float target_rpm) {
    if (ext.alarm) {
        ext.screw_rpm = 0;
        return;
    }
    if (target_rpm > SCREW_RPM_MAX) target_rpm = SCREW_RPM_MAX;
    ext.screw_rpm = target_rpm;
    ext.motor_on = (target_rpm > 10) ? 1 : 0;
}

void ble_send(void) {
    uint8_t buf[20];
    buf[0] = (uint8_t)ext.barrel_temp;
    buf[1] = (uint8_t)(ext.die_pressure * 10);
    buf[2] = (uint8_t)(ext.screw_rpm / 2);
    buf[3] = (ext.heater_on << 1) | ext.motor_on;
    buf[4] = ext.alarm;
    buf[5] = (ext.total_kg >> 24) & 0xFF;
    buf[6] = (ext.total_kg >> 16) & 0xFF;
    buf[7] = (ext.total_kg >> 8) & 0xFF;
    buf[8] = ext.total_kg & 0xFF;
    buf[9] = (ext.runtime_s >> 24) & 0xFF;
    buf[10] = (ext.runtime_s >> 16) & 0xFF;
    buf[11] = (ext.runtime_s >> 8) & 0xFF;
    buf[12] = ext.runtime_s & 0xFF;
}

void control_loop(void) {
    temp_control(TEMP_TARGET);
    pressure_monitor();
    if (!ext.alarm) {
        motor_control(300.0f);
    }
    ext.runtime_s++;
    ble_send();
}

int main(void) {
    ext.barrel_temp = 25.0f;
    ext.screw_rpm = 0;
    ext.alarm = 0;
    while (1) {
        control_loop();
        delay_ms(CYCLE_MS);
    }
    return 0;
}