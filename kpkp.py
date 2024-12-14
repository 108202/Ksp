import krpc
import time
import math

# Подключение к серверу KSP
conn = krpc.connect(name='KSP Autopilot')  # Подключаемся к игре KSP с помощью библиотеки krpc
vessel = conn.space_center.active_vessel  # Получаем активный корабль в игре

# Ускорение свободного падения и другие параметры
G = 6.67430e * 10**(-11)  # гравитационная постоянная
M_kerbin = 5,2915158*10**22  # масса Кербина (в кг)
R_kerbin = 600000  # радиус Кербина (в м)

# Параметры ступеней ракеты
stages = [
    {"thrust": 2150000, "burn_time": 135},  # Первая ступень с тягою 2,15 млн Н и временем сгорания 60 сек
    {"thrust": 1000000, "burn_time": 150},  # Вторая ступень с тягою 1 млн Н и временем сгорания 50 сек
    {"thrust": 500000, "burn_time": 40}   # Третья ступень с тягою 500 тыс. Н и временем сгорания 40 сек
]

def calculate_orbital_speed(altitude):
    """Рассчитывает орбитальную скорость на заданной высоте."""
    r = R_kerbin + altitude  # Расстояние от центра Кербина до корабля
    return math.sqrt(G * M_kerbin / r)  # Формула для расчета орбитальной скорости

def set_pitch(vessel, pitch):
    """Устанавливает тангаж (угол наклона) ракеты."""
    ap = vessel.auto_pilot  # Получаем автопилот корабля
    ap.target_pitch_and_heading(pitch, 90)  # Устанавливаем тангаж и азимут (90 - по оси востока)
    ap.engage()  # Включаем автопилот

def stage():
    """Активирует следующую ступень ракеты."""
    vessel.control.activate_next_stage()  # Переход к следующей ступени ракеты

def log_telemetry(telemetry, elapsed_time, altitude, speed, thrust, mass):
    """Записывает телеметрию (данные о полете)."""
    telemetry.append({
        "time": elapsed_time,  # Время полета
        "altitude": altitude,  # Высота
        "speed": speed,  # Скорость
        "thrust": thrust,  # Тяга
        "mass": mass  # Масса корабля
    })

# Исходные параметры
telemetry = []  # Список для хранения телеметрии
target_altitude = 90000  # Целевая высота орбиты (в м)
turn_start_altitude = 45000  # Высота начала поворота (в м)
turn_end_altitude = 90000  # Высота окончания поворота (в м)

# Предварительная настройка автопилота
vessel.auto_pilot.engage()  # Включаем автопилот
vessel.auto_pilot.target_pitch_and_heading(90, 90)  # Устанавливаем начальный тангаж 90° и азимут 90°
vessel.auto_pilot.reference_frame = vessel.surface_reference_frame  # Устанавливаем систему отсчета для автопилота
# vessel.auto_pilot.stopping_time = (0.5, 0.5, 0.5)  # Время на стабилизацию вращения
# vessel.auto_pilot.max_rotation_rate = (0.1, 0.1, 0.1)  # Ограничение максимальной скорости вращения
vessel.control.rcs = True  # Включаем систему реактивного управления для стабилизации
vessel.control.sas = True  # Включаем систему стабилизации (SAS)
vessel.control.throttle = 1.0  # Устанавливаем максимальный уровень тяги

# Старт
print("Запуск...")  # Сообщение о запуске ракеты
vessel.control.activate_next_stage()  # Активируем первую ступень ракеты
start_time = time.time()  # Записываем время старта

# Основной цикл
current_stage = 0  # Индекс текущей ступени
stage_burn_start = time.time()  # Время начала сгорания текущей ступени

while True:
    elapsed_time = time.time() - start_time  # Время полета (с момента старта)
    altitude = vessel.flight().mean_altitude  # Высота корабля
    velocity = vessel.flight().speed  # Скорость корабля
    thrust = vessel.available_thrust  # Доступная тяга
    mass = vessel.mass  # Масса корабля

    # Телеметрия
    log_telemetry(telemetry, elapsed_time, altitude, velocity, thrust, mass)  # Записываем данные
    print(f"Время: {elapsed_time:.1f} с, Высота: {altitude:.1f} м, Скорость: {velocity:.1f} м/с")  # Выводим информацию

    # Поворот к горизонту
    if altitude > turn_start_altitude and altitude < turn_end_altitude:  # Если высота в пределах для поворота
        frac = (altitude - turn_start_altitude) / (turn_end_altitude - turn_start_altitude)  # Вычисляем долю от общей высоты
        target_pitch = 90 - frac * 90  # Рассчитываем целевой угол тангажа
        set_pitch(vessel, target_pitch)  # Устанавливаем целевой угол тангажа

    # Смена ступеней
    if elapsed_time - stage_burn_start > stages[current_stage]["burn_time"]:  # Если время сгорания ступени истекло
        current_stage += 1  # Переходим к следующей ступени
        if current_stage < len(stages):  # Если еще есть ступени
            stage()  # Активируем следующую ступень
            stage_burn_start = time.time()  # Обновляем время начала сгорания
        else:
            print("Все ступени использованы.")  # Сообщение о завершении использования ступеней
            vessel.control.throttle = 0.0  # Останавливаем тягу
            break  # Выход из цикла

    # Выход на орбиту
    if altitude >= target_altitude:  # Если высота достигла целевой
        orbital_speed = calculate_orbital_speed(target_altitude)  # Рассчитываем орбитальную скорость
        current_speed = vessel.flight(vessel.orbit.body.reference_frame).speed  # Получаем текущую скорость
        if current_speed >= orbital_speed:  # Если скорость больше или равна орбитальной
            print("Орбита достигнута!")  # Сообщение о достижении орбиты
            vessel.control.throttle = 0.0  # Останавливаем тягу
            break  # Выход из цикла

    time.sleep(0.1)  # Задержка 0.1 секунды между итерациями цикла

# Завершение
vessel.auto_pilot.disengage()  # Отключаем автопилот
vessel.control.sas = True  # Включаем стабилизацию SAS после выхода на орбиту
vessel.auto_pilot.stopping_time = (1, 1, 1)  # Устанавливаем время стабилизации автопилота
print("Программа завершена.")  # Сообщение о завершении программы


