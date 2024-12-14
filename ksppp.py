import krpc
import time
import math
import matplotlib.pyplot as plt

# Подключение к kRPC и выбор активного аппарата
conn = krpc.connect(name="Sputnik-1 Launch")
vessel = conn.space_center.active_vessel

# Задаем параметры орбиты и другие константы
target_periapsis = 215000  # Перигей, м
target_apoapsis = 939000   # Апогей, м
target_inclination = 65.1  # Угол наклона, градусы

# Словарь для телеметрии
telemetry = {
    "time": [],
    "altitude": [],
    "velocity": [],
    "pitch": [],
    "apoapsis": [],
    "periapsis": []
}

# Функция сохранения данных телеметрии
def save_telemetry():
    telemetry["time"].append(conn.space_center.ut)
    telemetry["altitude"].append(vessel.flight().mean_altitude)
    telemetry["velocity"].append(vessel.flight().speed)
    telemetry["pitch"].append(vessel.flight().pitch)
    telemetry["apoapsis"].append(vessel.orbit.apoapsis_altitude)
    telemetry["periapsis"].append(vessel.orbit.periapsis_altitude)

# Функция вычисления угла наклона (тангажа) для плавного подъема
def pitch_angle(current_altitude, target_altitude):
    angle = 90 - (current_altitude / target_altitude) * 90
    return max(0, min(angle, 90))

# Функция проверки уровня топлива и активации следующей ступени
def activate_next_stage_if_needed():
    """
    Проверяет уровень топлива на текущей ступени и активирует следующую, если топлива больше нет.
    """
    liquid_fuel = vessel.resources_in_decouple_stage(
        vessel.control.current_stage, cumulative=False
    ).amount("LiquidFuel")

    solid_fuel = vessel.resources_in_decouple_stage(
        vessel.control.current_stage, cumulative=False
    ).amount("SolidFuel")

    if liquid_fuel < 0.1 and solid_fuel < 0.1:  # Проверяем, осталось ли топливо
        print(f"Ступень {vessel.control.current_stage} отделена.")
        vessel.control.activate_next_stage()
        time.sleep(1)  # Небольшая пауза для стабилизации после отделения

# Первая ступень: взлет
def stage_1():
    vessel.auto_pilot.engage()
    vessel.auto_pilot.target_roll = 0  # Удержание нулевого ролла
    vessel.control.throttle = 1.0
    print("Старт!")

    while True:
        height = vessel.flight().mean_altitude
        pitch = pitch_angle(height, target_apoapsis)
        vessel.auto_pilot.target_pitch_and_heading(pitch, 90)
        save_telemetry()

        activate_next_stage_if_needed()  # Проверяем, нужно ли отделить ступень

        # Завершение первой ступени при достижении определенной скорости и высоты
        if height > 30000 and vessel.flight().speed > 1000:
            print("Переход ко второй стадии")
            vessel.control.throttle = 0.5  # Снижаем тягу перед переходом
            time.sleep(0.5)
            vessel.control.activate_next_stage()
            time.sleep(1)
            break
        time.sleep(0.1)

# Вторая ступень: достижение апогея и завершение орбиты
def stage_2():
    print("Вторая ступень")
    vessel.auto_pilot.target_roll = 0  # Удержание ориентации
    vessel.control.throttle = 1.0  # Возвращаем тягу

    # Увеличение апогея
    while True:
        height = vessel.flight().mean_altitude
        pitch = pitch_angle(height, target_apoapsis)
        vessel.auto_pilot.target_pitch_and_heading(pitch, 90)
        save_telemetry()

        activate_next_stage_if_needed()  # Проверяем, нужно ли отделить ступень

        if vessel.orbit.apoapsis_altitude >= target_apoapsis:
            vessel.control.throttle = 0
            print("Апогей достигнут")
            break
        time.sleep(0.1)

    # Выход на орбиту: достижение целевого перигея
    vessel.control.throttle = 0.5
    while True:
        save_telemetry()
        vessel.auto_pilot.target_pitch_and_heading(0, 90)  # Гравитационный разворот

        activate_next_stage_if_needed()  # Проверяем, нужно ли отделить ступень

        if vessel.orbit.periapsis_altitude >= target_periapsis:
            vessel.control.throttle = 0
            print("Орбита установлена")
            break
        time.sleep(0.1)

# Этап работы спутника
def satellite_operation():
    print("Работа спутника")
    start = conn.space_center.ut
    while conn.space_center.ut - start < 300:  # Работает в течение 5 минут
        save_telemetry()
        vessel.auto_pilot.target_pitch_and_heading(0, 90)  # Удержание ориентации
        time.sleep(1)

# Функция построения графиков телеметрии
def plot_telemetry():
    plt.figure(figsize=(10, 8))

    plt.subplot(2, 2, 1)
    plt.plot(telemetry["time"], telemetry["altitude"])
    plt.title("Высота")
    plt.xlabel("Время")
    plt.ylabel("Высота, м")

    plt.subplot(2, 2, 2)
    plt.plot(telemetry["time"], telemetry["velocity"])
    plt.title("Скорость")
    plt.xlabel("Время")
    plt.ylabel("Скорость, м/с")

    plt.subplot(2, 2, 3)
    plt.plot(telemetry["time"], telemetry["apoapsis"], label="Апогей")
    plt.plot(telemetry["time"], telemetry["periapsis"], label="Перигей")
    plt.title("Орбита")
    plt.xlabel("Время")
    plt.ylabel("Высота, м")
    plt.legend()

    plt.subplot(2, 2, 4)
    plt.plot(telemetry["time"], telemetry["pitch"])
    plt.title("Угол наклона")
    plt.xlabel("Время")
    plt.ylabel("Угол, градусы")

    plt.tight_layout()
    plt.show()

# Выполнение этапов миссии
stage_1()
stage_2()
satellite_operation()
plot_telemetry()
