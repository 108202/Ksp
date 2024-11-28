import krpc
import time
import math

# Подключаемся к kRPC серверу
conn = krpc.connect(name="Sputnik-1 Launch")
vessel = conn.space_center.active_vessel

# Основные параметры орбиты Спутника-1
target_periapsis = 215000  # Перигей в метрах
target_apoapsis = 939000  # Апогей в метрах
target_inclination = 65.1  # Наклонение орбиты в градусах
g0 = 9.80665  # Ускорение свободного падения на Земле, м/с^2
p0 = 101325  # Давление на уровне моря, Па
H = 8500  # Характерная высота атмосферы, м

# Настраиваем автопилот
vessel.auto_pilot.engage()
vessel.control.throttle = 1.0  # Максимальная тяга
vessel.auto_pilot.target_pitch_and_heading(90, 90)  # Стартуем вертикально

# Формула для расчета атмосферного давления
def pressure_at_height(height):
    if height < 0:
        return p0
    return p0 * math.exp(-height / H)

# Формула для расчета тяги с учетом давления
def current_thrust(stage_thrust, height):
    pressure = pressure_at_height(height)
    vacuum_thrust = stage_thrust
    sea_level_thrust = stage_thrust * 0.7  # Примерное значение тяги на уровне моря
    return sea_level_thrust + (vacuum_thrust - sea_level_thrust) * (1 - pressure / p0)

# Рассчитываем угол наклона ракеты
def calculate_pitch(current_altitude, target_altitude):
    pitch = 90 - (current_altitude / target_altitude) * 90
    return max(0, min(pitch, 90))

# Первый этап — работа первой ступени
def stage_1_launch():
    print("Старт!")
    while True:
        height = vessel.flight().mean_altitude
        pitch = calculate_pitch(height, target_apoapsis)  # Меняем угол наклона
        vessel.auto_pilot.target_pitch_and_heading(pitch, 90)
        
        # Проверяем, когда нужно отделить первую ступень
        if vessel.resources.amount("LiquidFuel") <= 0.1:  # Топливо первой ступени израсходовано
            vessel.control.activate_next_stage()
            print("Первая ступень отделена!")
            break
        time.sleep(0.1)

# Второй этап — выход на орбиту
def stage_2_launch():
    print("Работа второй ступени")
    while True:
        height = vessel.flight().mean_altitude
        pitch = calculate_pitch(height, target_apoapsis)
        vessel.auto_pilot.target_pitch_and_heading(pitch, 90)
        
        # Проверяем параметры орбиты
        apoapsis = vessel.orbit.apoapsis_altitude
        periapsis = vessel.orbit.periapsis_altitude
        
        # Когда апогей достигнут, отключаем двигатели
        if apoapsis >= target_apoapsis:
            vessel.control.throttle = 0
            print("Апогей достигнут. Корректируем перигей.")
            break
        time.sleep(0.1)

    # Коррекция орбиты до перигея
    while True:
        periapsis = vessel.orbit.periapsis_altitude
        if periapsis >= target_periapsis:
            vessel.control.throttle = 0
            print("Орбита достигнута!")
            break
        vessel.control.throttle = 0.5
        time.sleep(0.1)

# Установка целевого наклонения
def set_inclination():
    print("Коррекция наклонения")
    vessel.auto_pilot.target_pitch_and_heading(0, target_inclination)  # Устанавливаем наклонение
    time.sleep(5)

# Запуск
stage_1_launch()  # Первая ступень
stage_2_launch()  # Вторая ступень
set_inclination()  # Установка наклонения
print("Спутник-1 на орбите!")
