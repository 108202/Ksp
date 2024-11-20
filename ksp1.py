import krpc
import time
import math

# Подключение к серверу kRPC
conn = krpc.connect(name="Sputnik-1 Launch")
vessel = conn.space_center.active_vessel

# Основные параметры
target_altitude = 500000  # Высота целевой орбиты в метрах (500 км над поверхностью)
g0 = 9.8  # Ускорение свободного падения на поверхности Земли, м/с^2

# Настройка автопилота
vessel.auto_pilot.engage()
vessel.control.throttle = 1.0  # Устанавливаем начальную тягу на максимум
vessel.auto_pilot.target_pitch_and_heading(90, 90)  # Начальный вертикальный взлет

# Формула для атмосферного давления (вставь сюда свою формулу)
def pressure_at_height(height):
    # Здесь рассчитай давление в зависимости от высоты.
    # Например, если используется формула p(h) = p0 * exp(-h/H) для Земли, замени "1" на формулу.
    return 1  # Подставь сюда свой расчет давления

# Расчет текущей тяги (вставь свою формулу)
def current_thrust(stage_thrust, height):
    pressure = pressure_at_height(height)
    # Используй формулу для расчета тяги с учетом давления
    return stage_thrust  # Замени на формулу, которая учитывает атмосферное давление

# Расчет угла наклона ракеты по отношению к горизонту
def calculate_pitch(current_altitude, target_altitude):
    # Линейно меняем угол наклона в зависимости от высоты, чтобы ракета постепенно
    # переходила от вертикального старта к полету параллельно поверхности.
    pitch = 90 - (current_altitude / target_altitude) * 90
    return max(0, min(pitch, 90))  # Ограничиваем угол от 0 до 90 градусов

# Первый этап полета - работа первой ступени
def stage_1_launch():
    print("Старт!")
    while True:
        height = vessel.flight().mean_altitude
        pitch = calculate_pitch(height, target_altitude)
        vessel.auto_pilot.target_pitch_and_heading(pitch, 90)
        
        # Условие для отделения первой ступени (по массе или другой метрике)
        if vessel.mass <= (вставь сюда свою формулу для определения массы после использования топлива первой ступени):  
            vessel.control.activate_next_stage()
            print("Первая ступень отделена.")
            break
        time.sleep(0.1)

# Второй этап полета - работа второй ступени
def stage_2_launch():
    while True:
        height = vessel.flight().mean_altitude
        pitch = calculate_pitch(height, target_altitude)
        vessel.auto_pilot.target_pitch_and_heading(pitch, 90)
        
        # Условие для выхода на орбиту
        if vessel.orbit.apoapsis_altitude >= target_altitude:
            vessel.control.throttle = 0
            print("Достигнута целевая орбита")
            break
        time.sleep(0.1)

# Запуск и выполнение этапов
stage_1_launch()  # Выполняем первый этап полета
stage_2_launch()  # Переходим ко второму этапу полета
print("Запуск первого спутника на орбиту завершен!")