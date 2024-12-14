import krpc
import time
import math

# Подключение к серверу KSP
conn = krpc.connect(name='KSP Autopilot')
vessel = conn.space_center.active_vessel

# Ускорение свободного падения и другие параметры
G = 6.67430e-11  # гравитационная постоянная
M_kerbin = 5.2915158e22  # масса Кербина (в кг)
R_kerbin = 600000  # радиус Кербина (в м)

# Параметры ступеней ракеты
stages = [
    {"thrust": 2150000, "burn_time": 60},  # Первая ступень
    {"thrust": 1000000, "burn_time": 50},  # Вторая ступень
    {"thrust": 500000, "burn_time": 40}   # Третья ступень
]

def calculate_orbital_speed(altitude):
    """Рассчитывает орбитальную скорость на заданной высоте."""
    r = R_kerbin + altitude
    return math.sqrt(G * M_kerbin / r)

def set_pitch(vessel, pitch):
    """Устанавливает тангаж."""
    ap = vessel.auto_pilot
    ap.target_pitch_and_heading(pitch, 90)
    ap.engage()

def stage():
    """Активирует следующую ступень ракеты."""
    vessel.control.activate_next_stage()

def log_telemetry(telemetry, elapsed_time, altitude, speed, thrust, mass):
    """Записывает телеметрию."""
    telemetry.append({
        "time": elapsed_time,
        "altitude": altitude,
        "speed": speed,
        "thrust": thrust,
        "mass": mass
    })

# Исходные параметры
telemetry = []
target_altitude = 80000  # целевая высота орбиты (в м)
turn_start_altitude = 250  # высота начала поворота (в м)
turn_end_altitude = 45000  # высота окончания поворота (в м)

# Предварительная настройка автопилота
vessel.auto_pilot.engage()
vessel.auto_pilot.target_pitch_and_heading(90, 90)
vessel.auto_pilot.stopping_time = (0.5, 0.5, 0.5)  # Ускорение стабилизации
vessel.auto_pilot.max_rotation_rate = (1, 1, 1)  # Ограничение скоростей вращения
vessel.control.rcs = True  # Включение реактивной системы стабилизации
vessel.control.throttle = 1.0

# Старт
print("Запуск...")
vessel.control.activate_next_stage()
start_time = time.time()

# Основной цикл
current_stage = 0
stage_burn_start = time.time()

while True:
    elapsed_time = time.time() - start_time
    altitude = vessel.flight().mean_altitude
    velocity = vessel.flight().speed
    thrust = vessel.available_thrust
    mass = vessel.mass

    # Телеметрия
    log_telemetry(telemetry, elapsed_time, altitude, velocity, thrust, mass)
    print(f"Время: {elapsed_time:.1f} с, Высота: {altitude:.1f} м, Скорость: {velocity:.1f} м/с")

    # Поворот к горизонту
    if altitude > turn_start_altitude and altitude < turn_end_altitude:
        frac = (altitude - turn_start_altitude) / (turn_end_altitude - turn_start_altitude)
        target_pitch = 90 - frac * 90
        set_pitch(vessel, target_pitch)

    # Смена ступеней
    if elapsed_time - stage_burn_start > stages[current_stage]["burn_time"]:
        current_stage += 1
        if current_stage < len(stages):
            stage()
            stage_burn_start = time.time()
        else:
            print("Все ступени использованы.")
            vessel.control.throttle = 0.0
            break

    # Выход на орбиту
    if altitude >= target_altitude:
        orbital_speed = calculate_orbital_speed(target_altitude)
        current_speed = vessel.flight(vessel.orbit.body.reference_frame).speed
        if current_speed >= orbital_speed:
            print("Орбита достигнута!")
            vessel.control.throttle = 0.0
            break

    time.sleep(0.1)

# Завершение
vessel.auto_pilot.disengage()  # Отключение автопилота
vessel.control.sas = True  # Включение SAS для стабилизации после выхода на орбиту
print("Программа завершена.")
