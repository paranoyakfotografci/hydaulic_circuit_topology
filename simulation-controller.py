from OMPython import OMCSessionZMQ
import matplotlib.pyplot as plt
import numpy as np

omc = OMCSessionZMQ()

# Load models
omc.sendExpression("loadModel(Modelica)")
omc.sendExpression(r'loadFile("C:/Users/Lenovo/Downloads/OpenHydraulics-main/OpenHydraulics/package.mo")')
omc.sendExpression('loadFile("deneme.mo")')

# Enable initialization debugging
omc.sendExpression('setCommandLineOptions("-d=initialization")')

# Check model
check = omc.sendExpression('checkModel(deneme)')
print("Check:", check)
print("Warnings:", omc.sendExpression('getErrorString()'))

# Simulate
simulate_cmd = '''simulate(
    deneme, 
    startTime=0, 
    stopTime=5, 
    stepSize=0.01, 
    tolerance=1e-6, 
    method="dassl", 
    outputFormat="mat", 
    variableFilter=".*"
)'''
result = omc.sendExpression(simulate_cmd)
print("Simulation completed")
print("Messages:", omc.sendExpression('getErrorString()'))

# Extract results using CORRECT variable names from the list
time_points = np.linspace(0, 5, 500)

# Position (piston position) - use doubleActingCylinder.piston.s
position = [float(omc.sendExpression(f'val(doubleActingCylinder.piston.s, {t})')) for t in time_points]

# Velocity (piston velocity) - use doubleActingCylinder.piston.v
velocity = [float(omc.sendExpression(f'val(doubleActingCylinder.piston.v, {t})')) for t in time_points]

# Pressure in chamber A (head side) - use doubleActingCylinder.cylinderChamberHead.p_vol
pressureA = [float(omc.sendExpression(f'val(doubleActingCylinder.cylinderChamberHead.p_vol, {t})')) for t in time_points]

# Pressure in chamber B (rod side) - use doubleActingCylinder.cylinderChamberRod.p_vol
pressureB = [float(omc.sendExpression(f'val(doubleActingCylinder.cylinderChamberRod.p_vol, {t})')) for t in time_points]

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(time_points, position)
plt.title("Cylinder Piston Position")
plt.xlabel("Time [s]")
plt.ylabel("Position [m]")
plt.grid(True)

plt.figure(figsize=(10, 6))
plt.plot(time_points, velocity)
plt.title("Cylinder Piston Velocity")
plt.xlabel("Time [s]")
plt.ylabel("Velocity [m/s]")
plt.grid(True)

plt.figure(figsize=(10, 6))
plt.plot(time_points, pressureA, label="Chamber A (Head Side)", linewidth=2)
plt.plot(time_points, pressureB, label="Chamber B (Rod Side)", linewidth=2)
plt.legend()
plt.title("Chamber Pressures")
plt.xlabel("Time [s]")
plt.ylabel("Pressure [Pa]")
plt.grid(True)

plt.show()
