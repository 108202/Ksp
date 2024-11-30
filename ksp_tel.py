import krpc
import time
import math
import matplotlib.pyplot as plt

conn = krpc.connect(name="Sputnik-1 Launch")
vessel = conn.space_center.active_vessel

# Задаем параметры
target_periapsis = 215000
target_apoapsis = 939000
target_inclination = 65.1

telemetry = {
    "time": [],
    "altitude": [],
    "velocity": [],
    "pitch": [],
    "apoapsis": [],
    "periapsis": []
}

def save_telemetry():
    telemetry["time"].append(conn.space_center.ut)
    telemetry["altitude"].append(vessel.flight().mean_altitude)
    telemetry["velocity"].append(vessel.flight().speed)
    telemetry["pitch"].append(vessel.flight().pitch)
    telemetry["apoapsis"].append(vessel.orbit.apoapsis_altitude)
    telemetry["periapsis"].append(vessel.orbit.periapsis_altitude)

def pressure(height):
    p0 = 101325
    H = 8500
    return p0 * math.exp(-height / H)

def thrust(stage_thrust, height):
    vacuum_thrust = stage_thrust
    sea_level_thrust = stage_thrust * 0.7
    return sea_level_thrust + (vacuum_thrust - sea_level_thrust) * (1 - pressure(height) / 101325)

def pitch_angle(current_altitude, target_altitude):
    angle = 90 - (current_altitude / target_altitude) * 90
    return max(0, min(angle, 90))

def stage_1():
    vessel.auto_pilot.engage()
    vessel.control.throttle = 1.0
    print("Старт!")
    while True:
        height = vessel.flight().mean_altitude
        pitch = pitch_angle(height, target_apoapsis)
        vessel.auto_pilot.target_pitch_and_heading(pitch, 90)
        save_telemetry()
        if vessel.resources.amount("LiquidFuel") < 0.1:
            vessel.control.activate_next_stage()
            print("Первая ступень отделена")
            break
        time.sleep(0.1)

def stage_2():
    print("Вторая ступень")
    while True:
        height = vessel.flight().mean_altitude
        pitch = pitch_angle(height, target_apoapsis)
        vessel.auto_pilot.target_pitch_and_heading(pitch, 90)
        save_telemetry()
        if vessel.orbit.apoapsis_altitude >= target_apoapsis:
            vessel.control.throttle = 0
            print("Апогей достигнут")
            break
        time.sleep(0.1)
    vessel.control.throttle = 0.5
    while True:
        save_telemetry()
        if vessel.orbit.periapsis_altitude >= target_periapsis:
            vessel.control.throttle = 0
            print("Орбита установлена")
            break
        time.sleep(0.1)

def satellite_operation():
    print("Работа спутника")
    start = conn.space_center.ut
    while conn.space_center.ut - start < 300:
        save_telemetry()
        vessel.auto_pilot.target_pitch_and_heading(0, 90)
        time.sleep(1)

def plot_telemetry():
    plt.figure(figsize=(10, 8))

    plt.subplot(2, 2, 1)
    plt.plot(telemetry["time"], telemetry["altitude"])
    plt.title("Высота")
    plt.xlabel("Время")
    plt.ylabel("Высота")

    plt.subplot(2, 2, 2)
    plt.plot(telemetry["time"], telemetry["velocity"])
    plt.title("Скорость")
    plt.xlabel("Время")
    plt.ylabel("Скорость")

    plt.subplot(2, 2, 3)
    plt.plot(telemetry["time"], telemetry["apoapsis"], label="Апогей")
    plt.plot(telemetry["time"], telemetry["periapsis"], label="Перигей")
    plt.title("Орбита")
    plt.xlabel("Время")
    plt.ylabel("Высота")
    plt.legend()

    plt.subplot(2, 2, 4)
    plt.plot(telemetry["time"], telemetry["pitch"])
    plt.title("Угол наклона")
    plt.xlabel("Время")
    plt.ylabel("Угол")

    plt.tight_layout()
    plt.show()

stage_1()
stage_2()
satellite_operation()
plot_telemetry()
