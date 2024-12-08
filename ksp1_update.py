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

# Настраиваем автопилот
vessel.auto_pilot.engage()
vessel.auto_pilot.target_roll = 0  # Удерживаем стабилизацию по крену
vessel.auto_pilot.stopping_time = (2, 2, 2)  # Сглаживание маневров
vessel.control.throttle = 1.0  # Максимальная тяга

# Формула для расчета угла наклона ракеты
def calculate_pitch(current_altitude, target_altitude):
    pitch = 90 - (current_altitude / target_altitude) * 70  # Уменьшаем угол с ростом высоты
    return max(0, min(pitch, 90))

# Первый этап — работа первой ступени
def stage_1_launch():
    print("Старт!")
    vessel.auto_pilot.target_pitch_and_heading(90, 90)  # Вертикальный старт
    time.sleep(1)  # Ждем стабилизации ракеты
    vessel.control.activate_next_stage()  # Запускаем двигатель

    while True:
        flight_info = vessel.flight()
        height = flight_info.mean_altitude
        pitch = calculate_pitch(height, target_apoapsis)  # Меняем угол наклона
        vessel.auto_pilot.target_pitch_and_heading(pitch, 90)  # Контроль тангажа
        
        # Проверяем, когда нужно отделить первую ступень
        if vessel.resources.amount("LiquidFuel") <= 0.1:  # Топливо первой ступени израсходовано
            vessel.control.activate_next_stage()
            print("Первая ступень отделена!")
            break
        time.sleep(0.1)

# Второй этап — выход на орбиту
def stage_2_launch():
    print("Работа второй ступени")
    vessel.control.throttle = 1.0  # Устанавливаем полную тягу

    while True:
        flight_info = vessel.flight()
        height = flight_info.mean_altitude
        pitch = calculate_pitch(height, target_apoapsis)  # Меняем угол наклона
        vessel.auto_pilot.target_pitch_and_heading(pitch, 90)

        apoapsis = vessel.orbit.apoapsis_altitude
        if apoapsis >= target_apoapsis:  # Достигаем апогей
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
    vessel.auto_pilot.disengage()  # Отключаем автопилот для маневра
    time.sleep(5)
    vessel.auto_pilot.engage()
    vessel.auto_pilot.target_pitch_and_heading(0, target_inclination)
    time.sleep(5)

# Запуск
stage_1_launch()  # Первая ступень
stage_2_launch()  # Вторая ступень
set_inclination()  # Установка наклонения
print("Спутник-1 на орбите!")
