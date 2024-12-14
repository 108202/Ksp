import krpc
import math
import time

# Подключение к KSP
conn = krpc.connect(name='KSP Autopilot')
vessel = conn.space_center.active_vessel

# Параметры ракеты
m0 = 267000  # начальная масса (кг)
m_payload = 5400  # масса полезной нагрузки (кг)
m_fuel = 250000  # масса топлива (кг)
thrust_stage_1 = 3253600  # тяга первой ступени (Н)
thrust_stage_2 = 744800  # тяга второй ступени (Н)
g = 9.81  # ускорение свободного падения (м/с^2)
v_exhaust = 2580  # скорость истечения газов (м/с)
h_char = 5000  # характеристическая высота для Кербина (м)
p0 = 1.0  # давление на уровне моря (атм)

def get_pressure(height):
    return p0 * math.exp(-height / h_char)

def get_thrust(height, stage):
    pressure = get_pressure(height)
    if stage == 1:
        return thrust_stage_1 + (pressure - p0) * 1000  # корректировка
    elif stage == 2:
        return thrust_stage_2 + (pressure - p0) * 500  # корректировка

def angle_control(time, burn_time):
    alpha_0 = math.pi / 2
    beta = math.pi / (2 * burn_time**2)
    return alpha_0 - beta * time**2

# Подготовка к запуску
vessel.control.sas = False
vessel.control.rcs = False
vessel.control.throttle = 1.0

print("Запуск")
vessel.control.activate_next_stage()

time.sleep(1)
start_time = conn.space_center.ut
burn_time_stage_1 = 60
burn_time_stage_2 = 90

telemetry = {'time': [], 'altitude': [], 'velocity': [], 'mass': [], 'thrust': [], 'angle': []}

while True:
    ut = conn.space_center.ut
    elapsed_time = ut - start_time

    altitude = vessel.flight().mean_altitude
    velocity = vessel.flight(vessel.orbit.body.reference_frame).speed
    mass = vessel.mass

    # Управление углом
    if elapsed_time <= burn_time_stage_1:
        angle = angle_control(elapsed_time, burn_time_stage_1)
    else:
        angle = angle_control(elapsed_time - burn_time_stage_1, burn_time_stage_2)

    vessel.auto_pilot.target_pitch_and_heading(math.degrees(angle), 90)
    vessel.auto_pilot.engage()

    # Вычисление текущей тяги
    stage = 1 if elapsed_time <= burn_time_stage_1 else 2
    thrust = get_thrust(altitude, stage)

    # Сохранение данных телеметрии
    telemetry['time'].append(elapsed_time)
    telemetry['altitude'].append(altitude)
    telemetry['velocity'].append(velocity)
    telemetry['mass'].append(mass)
    telemetry['thrust'].append(thrust)
    telemetry['angle'].append(math.degrees(angle))

    # Переход между ступенями
    if stage == 1 and elapsed_time > burn_time_stage_1:
        vessel.control.activate_next_stage()
        time.sleep(1)
    elif stage == 2 and elapsed_time > burn_time_stage_1 + burn_time_stage_2:
        print("Выход на орбиту завершен")
        break

    time.sleep(0.1)

# Построение графиков
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.subplot(2, 2, 1)
plt.plot(telemetry['time'], telemetry['altitude'])
plt.title('Altitude vs Time')
plt.xlabel('Time (s)')
plt.ylabel('Altitude (m)')

plt.subplot(2, 2, 2)
plt.plot(telemetry['time'], telemetry['velocity'])
plt.title('Velocity vs Time')
plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')

plt.subplot(2, 2, 3)
plt.plot(telemetry['time'], telemetry['thrust'])
plt.title('Thrust vs Time')
plt.xlabel('Time (s)')
plt.ylabel('Thrust (N)')

plt.subplot(2, 2, 4)
plt.plot(telemetry['time'], telemetry['angle'])
plt.title('Angle vs Time')
plt.xlabel('Time (s)')
plt.ylabel('Angle (degrees)')

plt.tight_layout()
plt.show()
