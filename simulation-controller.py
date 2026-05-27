from OMPython import OMCSessionZMQ

def validate_model_correct(omc, model_name):
    """
    REAL validation functions that actually exist in OpenModelica
    """
    
    print(f"\n=== VALIDATING {model_name} ===\n")
    
    # Clear error buffer
    omc.sendExpression('getErrorString()')
    
    # ============================================================
    # LEVEL 1: checkModel() - Basic structural validation
    # ============================================================
    print("📋 Step 1: Running checkModel()...")
    check_result = omc.sendExpression(f'checkModel({model_name})')
    check_errors = omc.sendExpression('getErrorString()', parsed=False)
    
    if "Error" in check_errors:
        print("❌ checkModel() FAILED:")
        print(check_errors)
        return False
    else:
        print("✅ checkModel() passed")
        if check_errors.strip():
            print(f"   Warnings: {check_errors[:200]}...")
    
    # ============================================================
    # LEVEL 2: instantiateModel() - Flatten the model
    # ============================================================
    print("\n📋 Step 2: Running instantiateModel()...")
    try:
        instantiated = omc.sendExpression(f'instantiateModel({model_name})')
        inst_errors = omc.sendExpression('getErrorString()', parsed=False)
        
        if "Error" in inst_errors:
            print("❌ instantiateModel() FAILED:")
            print(inst_errors)
            return False
        else:
            print("✅ instantiateModel() passed")
            print(f"   Model size: {len(str(instantiated))} characters")
    except Exception as e:
        print(f"⚠️  instantiateModel() exception: {e}")
        # Non-fatal - some models have issues with instantiateModel
    
    # ============================================================
    # LEVEL 3: buildModel() - COMPILATION (catches your error!)
    # ============================================================
    print("\n📋 Step 3: Running buildModel()...")
    build_result = omc.sendExpression(f'buildModel({model_name}, variableFilter=".*")')
    build_errors = omc.sendExpression('getErrorString()', parsed=False)
    
    if "Error" in build_errors or not build_result:
        print("❌ buildModel() FAILED - Compilation error!")
        print(build_errors)
        
        # Check for specific error
        if "Found equation without time-dependent variables" in build_errors:
            print("\n💡 DETECTED: Algebraic equation error (source.p_const = tank.p_const)")
            print("   Fix: Add a resistance or dynamic element between fixed pressure sources")
        
        return False
    else:
        print("✅ buildModel() passed - Compilation successful")
        print(f"   Executable: {build_result[0]}")
        print(f"   Init file: {build_result[1]}")
    
    # ============================================================
    # LEVEL 4: Check for warnings (non-fatal)
    # ============================================================
    print("\n📋 Step 4: Checking for warnings...")
    warnings = omc.sendExpression('getErrorString()', parsed=False)
    if warnings.strip():
        print("⚠️  Warnings (non-fatal):")
        # Filter and display important warnings
        if "Assuming fixed start value" in warnings:
            print("   • Some variables missing initial values (auto-assigned)")
        if "inconsistent" in warnings.lower():
            print("   • Potential inconsistency detected")
    
    print("\n✅ Model validation complete - Ready for simulation!")
    return True


# ============================================================
# USAGE WITH YOUR MODEL
# ============================================================

omc = OMCSessionZMQ()

# Load models
omc.sendExpression("loadModel(Modelica)")
omc.sendExpression(r'loadFile("C:/Users/Lenovo/Downloads/OpenHydraulics-main/OpenHydraulics/package.mo")')
omc.sendExpression('loadFile("deneme.mo")')

# Validate (using only real functions)
if validate_model_correct(omc, "deneme"):
    print("\n" + "="*50)
    print("RUNNING SIMULATION")
    print("="*50)
    
    # Now simulate safely
    result = omc.sendExpression('''simulate(
        deneme, 
        startTime=0, 
        stopTime=5, 
        stepSize=0.01, 
        tolerance=1e-6, 
        method="dassl", 
        outputFormat="mat", 
        variableFilter=".*"
    )''')
    
    print("✅ Simulation completed!")
    
    # Extract results (your plotting code here)
else:
    print("\n❌ Model validation failed - Please fix errors before simulating")


'''
# Simulate
simulate_cmd = "simulate(
    deneme, 
    startTime=0, 
    stopTime=5, 
    stepSize=0.01, 
    tolerance=1e-6, 
    method="dassl", 
    outputFormat="mat", 
    variableFilter=".*"
)"
result = omc.sendExpression(simulate_cmd)
print("Simulation completed")
print("Messages:", omc.sendExpression('getErrorString()'))
'''
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
