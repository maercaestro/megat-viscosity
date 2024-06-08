import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
from  PIL import Image
import pandas as pd

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

def calculate_vbn(vi):
    return 14.534 * math.log(math.log(vi + 0.8)) + 10.975

def calculate_viscosity_mixture(viscosities, fractions):
    vbns = [calculate_vbn(vi) for vi in viscosities]
    vbn_mixture = sum(xi * vbni for xi, vbni in zip(fractions, vbns))
    viscosity_mixture = math.exp(math.exp((vbn_mixture - 10.975) / 14.534)) - 0.8
    return viscosity_mixture

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

# Radio button for navigation
mode = st.sidebar.radio("Select Mode", ["Viscosity and Temperature Relations", "Viscosity of a Mixture"])

# Main Streamlit app



if mode == "Viscosity and Temperature Relations":
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

elif mode == "Viscosity of a Mixture":
    st.title('MEGAT Viscosity of Mixture')
    st.write("Refutas (2000) proposed a method by which the kinematic viscosity (ν) of a mixture of two or more liquids is calculated. The Viscosity Blending Number (VBN) of each component is first calculated and then used to determine the VBN of the liquid mixture as shown below:")
    st.latex(r"""
    VBN_i = 14.534 \times \ln(\ln(\nu_i + 0.8)) + 10.975
    """)
    st.latex(r"""
    VBN_{mixture} = \sum_{i=0}^N x_i \times VBN_i
    """)
    st.latex(r"""
    \nu_{mixture} = \exp\left(\exp\left(\frac{VBN_{mixture} - 10.975}{14.534}\right)\right) - 0.8
    """)
# Creating a dataframe for input
    data = {
        "Viscosity (cSt)": [0.0] * 5,
        "Mass Fraction": [0.0] * 5
    }
    df = pd.DataFrame(data)
    
    edited_df = st.data_editor(df, num_rows="dynamic")

    if st.button('Calculate Viscosity of Mixture'):
        try:
            viscosities = edited_df["Viscosity (cSt)"].tolist()
            fractions = edited_df["Fraction"].tolist()

            total_fraction = sum(fractions)
            if total_fraction != 1.0:
                st.error("The sum of the fractions must equal 1.0.")
            else:
                # Filter out zero viscosities and their corresponding fractions
                viscosities = [v for v in viscosities if v > 0]
                fractions = [f for f in fractions if f > 0]
                viscosity_mixture = calculate_viscosity_mixture(viscosities, fractions)
                st.write(f"Viscosity of the mixture: {viscosity_mixture:.4f} cSt")
        except ValueError as e:
            st.error(f"Error in calculation: {e}")

