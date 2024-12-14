import numpy as np
import krpc
import time
import matplotlib.pyplot as plt

# Подключение к kRPC и выбор активного аппарата
conn = krpc.connect(name="Rocket Autopilot")
vessel = conn.space_center.active_vessel

# Задаем параметры ракеты
g = 9.8  # ускорение свободного падения, м/с^2
R = 6371000  # радиус Земли, м
h_start = 0  # высота старта, м
h_target = 500000  # целевая высота (около 500 км), м
mass_payload = 5400  # масса полезной нагрузки, кг
fuel_mass_1 = 125000  # масса топлива 1-й ступени, кг
fuel_mass_2 = 125000  # масса топлива 2-й ступени, кг
total_mass = 267000  # общая масса ракеты, кг
thrust_1 = 3253600  # тяга 1-й ступени, Н
thrust_2 = 744800  # тяга 2-й ступени, Н
I_sp_1 = 300  # удельный импульс 1-й ступени, с
I_sp_2 = 330  # удельный импульс 2-й ступени, с
h_crit_1 = 30000  # критическая высота для отделения 1-й ступени, м
h_crit_2 = 80000  # критическая высота для отделения 2-й ступени, м
h_atm = 5000  # характеристическая высота атмосферы, м

# Создание контейнера для телеметрии
telemetry = {
    "time": [],
    "altitude": [],
    "velocity": [],
    "pitch": [],
    "thrust": [],
    "mass": []
}

# Функция для сохранения телеметрии
def save_telemetry():
    telemetry["time"].append(conn.space_center.ut)
    telemetry["altitude"].append(vessel.flight().mean_altitude)
    telemetry["velocity"].append(vessel.flight().speed)
    telemetry["pitch"].append(vessel.flight().pitch)
    telemetry["thrust"].append(vessel.control.throttle)
    telemetry["mass"].append(vessel.mass)

# Функция для вычисления давления
def pressure(h):
    p_0 = 1  # давление на поверхности (атм)
    h_scale = h_atm  # характеристическая высота
    return p_0 * np.exp(-h / h_scale)

# Функция для вычисления тяги в зависимости от давления
def thrust_at_altitude(thrust_vacuum, p):
    delta_thrust = (thrust_1 - thrust_2) / 1  # разница тяг на уровне поверхности и в вакууме
    return thrust_vacuum * (1 + delta_thrust * p)

# Функция для вычисления ускорения ракеты
def acceleration(mass, thrust, gravity):
    return (thrust / mass) - gravity

# Функция для расчета угла наклона ракеты
def pitch_angle(current_altitude, target_altitude, k=0.00001):
    # Пример линейного изменения угла наклона
    angle = k * (current_altitude - h_start)
    return max(0, min(angle, 90))

# Основной цикл полета
def flight():
    vessel.auto_pilot.engage()
    vessel.auto_pilot.target_roll = 0
    vessel.control.throttle = 1.0

    current_mass = total_mass
    stage = 1
    while vessel.flight().mean_altitude < h_target:
        current_altitude = vessel.flight().mean_altitude
        p = pressure(current_altitude)
        
        # Тяга на основе высоты и давления
        if stage == 1:
            thrust = thrust_at_altitude(thrust_1, p)
        elif stage == 2:
            thrust = thrust_at_altitude(thrust_2, p)

        # Изменение угла наклона
        pitch = pitch_angle(current_altitude, h_target)
        vessel.auto_pilot.target_pitch_and_heading(pitch, 90)

        # Масса ракеты (с учетом расхода топлива)
        if stage == 1:
            fuel_consumption = thrust / (I_sp_1 * g)  # расход топлива 1-й ступени
            current_mass -= fuel_consumption
            if current_altitude > h_crit_1:  # отделение 1-й ступени
                print("Отделение 1-й ступени")
                vessel.control.activate_next_stage()
                stage = 2
        elif stage == 2:
            fuel_consumption = thrust / (I_sp_2 * g)  # расход топлива 2-й ступени
            current_mass -= fuel_consumption
            if current_altitude > h_crit_2:  # отделение 2-й ступени
                print("Отделение 2-й ступени")
                vessel.control.activate_next_stage()
                break  # Завершаем полет

        # Сохраняем телеметрию
        save_telemetry()

        # Пауза между итерациями
        time.sleep(0.1)

    print("Полет завершен")

# Функция для построения графиков
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
    plt.plot(telemetry["time"], telemetry["thrust"], label="Тяга")
    plt.title("Тяга")
    plt.xlabel("Время")
    plt.ylabel("Тяга")

    plt.subplot(2, 2, 4)
    plt.plot(telemetry["time"], telemetry["mass"], label="Масса ракеты")
    plt.title("Масса ракеты")
    plt.xlabel("Время")
    plt.ylabel("Масса (кг)")

    plt.tight_layout()
    plt.show()

# Главная функция, которая запускает полет и построение графиков
if __name__ == "__main__":
    flight()
    plot_telemetry()
