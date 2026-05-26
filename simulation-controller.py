from OMPython import ModelicaSystem
import matplotlib.pyplot as plt
import numpy as np

# Create ModelicaSystem instance
mod = ModelicaSystem(
    fileName="deneme.mo",
    modelName="deneme",
    lmodel=["Modelica", "OpenHydraulics"]
)

# Set simulation options matching OMEdit
simulation_options = {
    "startTime": 0,
    "stopTime": 5,
    "stepSize": 0.01,
    "tolerance": 1e-6,
    "solver": "dassl",
    "outputFormat": "mat",
    "variableFilter": ".*"
}
mod.setSimulationOptions(**simulation_options)

# Simulate
mod.simulate()

# Get results
time = np.linspace(0, 5, 500)
pos = [mod.getSolutions(f"position at time={t}") for t in time]  # Note: You'll need to use proper value extraction
# Better way - extract from result file
result = mod.getSolutions()
# Or use specific variables

# Plotting
plt.figure()
plt.plot(time, pos)
plt.title("Cylinder Position")
plt.xlabel("Time [s]")
plt.ylabel("Position [m]")
plt.show()
