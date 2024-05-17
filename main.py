import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
from  PIL import Image

def calculate_A_and_B(v1, v2, T1, T2):
    # Calculate B
    B_numerator = math.log(math.log(v2 + 0.7)) - math.log(math.log(v1 + 0.7))
    B_denominator = math.log(T1) - math.log(T2)
    B = B_numerator / B_denominator

    # Calculate A
    A = B * math.log(T1) + math.log(math.log(v1 + 0.7))

    return A, B

def calculate_viscosity(A, B, T):
    # Calculate v using the given A, B, and T
    log_v = A - B * math.log(T)
    v = math.exp(math.exp(log_v)) - 0.7
    return v

def plot_viscosity_vs_temperature(A, B, T_min=40, T_max=100):
    temperatures_C = np.linspace(T_min, T_max, 100)
    temperatures_K = temperatures_C + 273.15
    viscosities = [calculate_viscosity(A, B, T) for T in temperatures_K]

    plt.figure(figsize=(10, 6))
    plt.plot(temperatures_C, viscosities, label='Viscosity vs Temperature')
    plt.xlabel('Temperature (°C)')
    plt.ylabel('Kinematic Viscosity (cSt)')
    plt.title('Kinematic Viscosity vs Temperature')
    plt.legend()
    plt.grid(True)
    return plt

# Load the image
image = Image.open('MEGATLogo.png')

# Calculate the new dimensions based on the scale factor
scale_factor = 0.25  # 25% of the original size

# Calculate the new width and height
new_width = int(image.width * scale_factor)
new_height = int(image.height * scale_factor)

# Resize the image
resized_image = image.resize((new_width, new_height))

st.image(resized_image)
# Main Streamlit app
st.title('MEGAT Viscosity at Different Temperature')


st.write("""
This application calculates the kinematic viscosity at a given temperature based on the ASTM-D341 standard equation:
""")

st.latex(r"""
\log(\log(v + 0.7)) = A - B \log(T)
""")

st.write("The constants \( A \) and \( B \) are calculated as follows:")

st.latex(r"""
B = \frac{\log(\log(v_2 + 0.7)) - \log(\log(v_1 + 0.7))}{\log(T_1) - \log(T_2)}
""")
st.latex(r"""
A = B \log(T_1) + \log(\log(v_1 + 0.7))
""")    

st.write("### Input Parameters")

# Input values for v1, v2, T1, T2
v1 = st.number_input('Enter v1 (kinematic viscosity at T1) in cSt:', value=1.0)
v2 = st.number_input('Enter v2 (kinematic viscosity at T2) in cSt:', value=2.0)
T1_degC = st.number_input('Enter T1 (temperature in °C):', value=30.0)
T2_degC = st.number_input('Enter T2 (temperature in °C):', value=50.0)
T1 = T1_degC + 273.15
T2 = T2_degC + 273.15

# Calculate A and B based on the inputs
A, B = calculate_A_and_B(v1, v2, T1, T2)

# Input temperature for viscosity calculation
T_input_degC = st.number_input('Enter temperature (in °C) for viscosity calculation:', value=40.0)
T_input = T_input_degC + 273.15

if st.button('Calculate Viscosity'):
    try:
        viscosity = calculate_viscosity(A, B, T_input)
        st.write(f"Kinematic Viscosity (v) at T = {T_input_degC} °C is: {viscosity:.4f} cSt")

        # Plot the viscosity vs temperature graph
        plt = plot_viscosity_vs_temperature(A, B)
        st.pyplot(plt)
    except ValueError as e:
        st.error(f"Error in calculation: {e}")
