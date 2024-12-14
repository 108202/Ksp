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

# Исходные параметры
target_altitude = 80000  # целевая высота орбиты (в м)
turn_start_altitude = 250  # высота начала поворота (в м)
turn_end_altitude = 45000  # высота окончания поворота (в м)

# Предварительная настройка автопилота
vessel.auto_pilot.engage()
vessel.auto_pilot.target_pitch_and_heading(90, 90)
vessel.control.throttle = 1.0

# Старт
print("Запуск...")
vessel.control.activate_next_stage()

# Основной цикл
while True:
    altitude = vessel.flight().mean_altitude
    velocity = vessel.flight().velocity
    thrust = vessel.available_thrust
    mass = vessel.mass

    # Телеметрия
    print(f"Высота: {altitude:.1f} м, Скорость: {vessel.flight().speed:.1f} м/с")

    # Поворот к горизонту
    if altitude > turn_start_altitude and altitude < turn_end_altitude:
        frac = (altitude - turn_start_altitude) / (turn_end_altitude - turn_start_altitude)
        target_pitch = 90 - frac * 90
        set_pitch(vessel, target_pitch)

    # Выход на орбиту
    if altitude >= target_altitude:
        orbital_speed = calculate_orbital_speed(target_altitude)
        current_speed = vessel.flight(vessel.orbit.body.reference_frame).speed
        if current_speed >= orbital_speed:
            print("Орбита достигнута!")
            vessel.control.throttle = 0.0
            break

    # Сброс ступеней
    if vessel.resources.amount('SolidFuel') == 0:
        stage()

    time.sleep(0.1)

# Завершение
print("Программа завершена.")

