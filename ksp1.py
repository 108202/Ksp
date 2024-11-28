import krpc
import time
import math

# Подключаемся к kRPC серверу
conn = krpc.connect(name="Sputnik-1 Launch")
vessel = conn.space_center.active_vessel

# Основные параметры для запуска
target_altitude = 500000  # Наша цель — высота орбиты в метрах (500 км над Землей)
g0 = 9.80665  # Ускорение свободного падения на Земле, м/с^2
p0 = 101325  # Давление на уровне моря, Па
H = 8500  # Характерная высота атмосферы, м

# Включаем автопилот и устанавливаем начальные параметры
vessel.auto_pilot.engage()
vessel.control.throttle = 1.0  # Газ на максимум
vessel.auto_pilot.target_pitch_and_heading(90, 90)  # Взлетаем строго вверх

# Формула для расчета давления в зависимости от высоты
def pressure_at_height(height):
    if height < 0:
        return p0  # На всякий случай, если высота вдруг отрицательная
    return p0 * math.exp(-height / H)  # Экспоненциальное снижение давления

# Формула для расчета тяги с учетом атмосферного давления
def current_thrust(stage_thrust, height):
    pressure = pressure_at_height(height)
    vacuum_thrust = stage_thrust  # Тяга в вакууме
    sea_level_thrust = stage_thrust * 0.7  # Примерное значение тяги на земле
    thrust = sea_level_thrust + (vacuum_thrust - sea_level_thrust) * (1 - pressure / p0)
    return thrust

# Рассчитываем угол наклона ракеты
def calculate_pitch(current_altitude, target_altitude):
    pitch = 90 - (current_altitude / target_altitude) * 90  # Постепенный переход к горизонтальному полету
    return max(0, min(pitch, 90))  # Угол всегда в пределах от 0 до 90 градусов

# Первый этап полета — первая ступень
def stage_1_launch():
    print("Взлет!")
    while True:
        height = vessel.flight().mean_altitude  # Текущая высота
        pitch = calculate_pitch(height, target_altitude)  # Считаем угол
        vessel.auto_pilot.target_pitch_and_heading(pitch, 90)  # Устанавливаем угол
        
        # Проверяем, когда нужно отделить первую ступень
        if vessel.mass <= (vessel.mass * 0.5):  # Это просто пример, здесь может быть любая логика
            vessel.control.activate_next_stage()  # Отделяем ступень
            print("Первая ступень отделена!")
            break
        time.sleep(0.1)

# Второй этап полета — вторая ступень
def stage_2_launch():
    while True:
        height = vessel.flight().mean_altitude  # Текущая высота
        pitch = calculate_pitch(height, target_altitude)  # Считаем угол
        vessel.auto_pilot.target_pitch_and_heading(pitch, 90)  # Устанавливаем угол
        
        # Проверяем, достигли ли нужной орбиты
        if vessel.orbit.apoapsis_altitude >= target_altitude:
            vessel.control.throttle = 0  # Останавливаем двигатели
            print("Целевая орбита достигнута!")
            break
        time.sleep(0.1)

# Выполняем этапы полета
stage_1_launch()  # Первая ступень
stage_2_launch()  # Вторая ступень
print("Успех! Спутник выведен на орбиту!")

