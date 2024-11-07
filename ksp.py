import krpc
import time


conn = krpc.connect(name='Sputnik 1 Launch', address='127.0.0.1', port=50000, password='ksp')
vessel = conn.space_center.active_vessel


target_apoapsis = 900000  # в метрах
target_periapsis = 215000  # ---"---

vessel.control.throttle = 1.0
print("Запуск ракеты...")
vessel.control.activate_next_stage()

while vessel.flight().mean_altitude < 1000:
    time.sleep(0.1)

#Начало гравитационного поворота
turn_angle = 0

while vessel.flight().mean_altitude < target_apoapsis * 0.5:
    turn_angle = min(45, vessel.flight().mean_altitude / (target_apoapsis * 0.5) * 45)
    vessel.auto_pilot.target_pitch_and_heading(90 - turn_angle, 90)
    time.sleep(1)

if len(vessel.parts.stages) > 1:
    # Отделение первой ступени
    vessel.control.activate_next_stage()

while vessel.orbit.apoapsis_altitude < target_apoapsis:
    time.sleep(1)

vessel.control.throttle = 0
#Целевая высота апоцентра достигнута. Ожидание апоцентра для круговой орбиты

while vessel.orbit.time_to_apoapsis > 30:
    time.sleep(1)

#Маневр для повышения перицентра
vessel.control.throttle = 1.0

while vessel.orbit.periapsis_altitude < target_periapsis:
    time.sleep(1)

vessel.control.throttle = 0
print("Спутник выведен на орбиту с перицентром:", vessel.orbit.periapsis_altitude / 1000, "км и апоцентром:", vessel.orbit.apoapsis_altitude / 1000, "км.")

print("Конец")
