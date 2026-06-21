import time
import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Used Car Price Prediction",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load Model ────────────────────────────────────────────────
@st.cache_resource
def load_model():
    model = joblib.load("car_price_prediction_model.pkl")
    model_columns = joblib.load("model_columns.pkl")
    return model, model_columns

model, model_columns = load_model()

# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.title("🚗 Car Price AI")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "🚗 Predict Price", "📊 Model Performance", "👨‍💻 About"],
    label_visibility="collapsed",
)
st.sidebar.markdown("---")
st.sidebar.caption("Built with Streamlit · Random Forest · Scikit-Learn")


# ════════════════════════════════════════════════════════════
# 🏠 HOME PAGE
# ════════════════════════════════════════════════════════════
if page == "🏠 Home":
    st.title("🚗 AI-Powered Used Car Price Prediction")
    st.markdown("Predict the resale value of any used car instantly using a trained **Random Forest** model.")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Dataset", "15,411 Cars")
    col2.metric("🤖 Algorithm", "Random Forest")
    col3.metric("🎯 Best R²", "93.89%")
    col4.metric("⚡ Prediction", "Real Time")

    st.markdown("---")
    st.subheader("🛠️ Technologies Used")
    techs = ["Python", "Pandas", "NumPy", "Scikit-Learn", "Streamlit", "Plotly", "Joblib", "Random Forest"]
    cols = st.columns(len(techs))
    for col, tech in zip(cols, techs):
        col.success(tech)


# ════════════════════════════════════════════════════════════
# 🚗 PREDICT PAGE
# ════════════════════════════════════════════════════════════
elif page == "🚗 Predict Price":
    st.title("🚗 Predict Used Car Price")
    st.markdown("Fill in the details below and click **Predict Price**.")
    st.markdown("---")

    with st.form("prediction_form"):
        st.subheader("🚙 Vehicle Details")
        col1, col2 = st.columns(2)

        with col1:
            vehicle_age = st.number_input("Vehicle Age (Years)", min_value=0, max_value=30, value=5)
            km_driven = st.number_input("Kilometers Driven", min_value=0, value=50000)
            mileage = st.number_input("Mileage (km/l)", value=18.0)
            brand = st.selectbox("Brand", [
                "Maruti", "Hyundai", "Honda", "Toyota", "BMW",
                "Mercedes-Benz", "Tata", "Mahindra", "Ford",
                "Volkswagen", "Renault", "Kia", "Volvo", "Skoda", "Audi"
            ])
            model_name = st.text_input("Model Name")

        with col2:
            engine = st.number_input("Engine (CC)", value=1200)
            max_power = st.number_input("Max Power (bhp)", value=90.0)
            seats = st.selectbox("Seats", [2, 4, 5, 6, 7, 8, 9, 10])
            seller_type = st.selectbox("Seller Type", ["Dealer", "Individual", "Trustmark Dealer"])
            fuel_type = st.selectbox("Fuel Type", ["Petrol", "Diesel", "CNG", "Electric", "LPG"])
            transmission_type = st.selectbox("Transmission", ["Manual", "Automatic"])

        submitted = st.form_submit_button("🔍 Predict Price", use_container_width=True)

    # ── Prediction Logic (unchanged) ──────────────────────────
    if submitted:
        with st.spinner("Predicting price..."):
            start = time.time()

            input_data = pd.DataFrame(columns=model_columns)
            input_data.loc[0] = 0

            input_data["vehicle_age"] = vehicle_age
            input_data["km_driven"] = km_driven
            input_data["mileage"] = mileage
            input_data["engine"] = engine
            input_data["max_power"] = max_power
            input_data["seats"] = seats

            brand_col = f"brand_{brand}"
            if brand_col in input_data.columns:
                input_data[brand_col] = 1

            model_col = f"model_{model_name}"
            if model_col in input_data.columns:
                input_data[model_col] = 1

            seller_col = f"seller_type_{seller_type}"
            if seller_col in input_data.columns:
                input_data[seller_col] = 1

            fuel_col = f"fuel_type_{fuel_type}"
            if fuel_col in input_data.columns:
                input_data[fuel_col] = 1

            trans_col = f"transmission_type_{transmission_type}"
            if trans_col in input_data.columns:
                input_data[trans_col] = 1

            prediction = model.predict(input_data)
            price = prediction[0]
            elapsed = round(time.time() - start, 3)

        st.markdown("---")
        st.subheader("📊 Prediction Results")

        category = "Budget" if price < 300000 else "Mid Range" if price < 800000 else "Premium"

        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Estimated Price", f"₹ {price:,.0f}")
        c2.metric("🏷️ Category", category)
        c3.metric("⏱️ Prediction Time", f"{elapsed}s")

        # Gauge Chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=price,
            title={"text": "Estimated Selling Price (₹)"},
            gauge={
                "axis": {"range": [0, 2000000]},
                "bar": {"color": "#2ECC71"},
                "steps": [
                    {"range": [0, 300000], "color": "#AED6F1"},
                    {"range": [300000, 800000], "color": "#85C1E9"},
                    {"range": [800000, 2000000], "color": "#2980B9"},
                ],
            },
        ))
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
        st.success(f"✅ Estimated Selling Price: ₹ {price:,.0f}")


# ════════════════════════════════════════════════════════════
# 📊 MODEL PERFORMANCE PAGE
# ════════════════════════════════════════════════════════════
elif page == "📊 Model Performance":
    st.title("📊 Model Performance Comparison")
    st.markdown("Comparing three ML models trained on the used car dataset.")
    st.markdown("---")

    models = ["Linear Regression", "Decision Tree", "Random Forest"]
    r2_scores = [0.800, 0.885, 0.939]
    rmse_scores = [387994, 293574, 214528]

    # Metric Cards
    col1, col2, col3 = st.columns(3)
    for col, name, r2, rmse in zip([col1, col2, col3], models, r2_scores, rmse_scores):
        with col:
            label = f"⭐ {name}" if name == "Random Forest" else name
            st.metric(label, f"R² = {r2}", f"RMSE = {rmse:,}")

    st.markdown("---")

    # R² Bar Chart
    fig1 = go.Figure(go.Bar(
        x=models,
        y=r2_scores,
        marker_color=["#AED6F1", "#85C1E9", "#2ECC71"],
        text=[f"{v:.3f}" for v in r2_scores],
        textposition="outside",
    ))
    fig1.update_layout(title="R² Score Comparison (Higher is Better)", yaxis_range=[0, 1.1], height=350)
    st.plotly_chart(fig1, use_container_width=True)

    # RMSE Bar Chart
    fig2 = go.Figure(go.Bar(
        x=models,
        y=rmse_scores,
        marker_color=["#AED6F1", "#85C1E9", "#2ECC71"],
        text=[f"{v:,}" for v in rmse_scores],
        textposition="outside",
    ))
    fig2.update_layout(title="RMSE Comparison (Lower is Better)", height=350)
    st.plotly_chart(fig2, use_container_width=True)

    st.success("✅ Random Forest is the best model with R² = 93.89% and lowest RMSE.")


# ════════════════════════════════════════════════════════════
# 👨‍💻 ABOUT PAGE
# ════════════════════════════════════════════════════════════
elif page == "👨‍💻 About":
    st.title("👨‍💻 About This Project")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📁 Project Info")
        st.write("**Project:** Used Car Price Prediction")
        st.write("**Dataset:** 15,411 used car records")
        st.write("**Model:** Random Forest Regressor")
        st.write("**Best R²:** 93.89%")

        st.subheader("⚙️ ML Workflow")
        st.write("1. Data Collection & Cleaning")
        st.write("2. Exploratory Data Analysis")
        st.write("3. Feature Engineering & Encoding")
        st.write("4. Model Training & Evaluation")
        st.write("5. Streamlit Deployment")

    with col2:
        st.subheader("🛠️ Technologies")
        for tech in ["Python", "Pandas", "NumPy", "Scikit-Learn", "Random Forest", "Streamlit", "Plotly"]:
            st.write(f"• {tech}")

    st.markdown("---")
    st.subheader("👤 Developer")
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Name:** Abhay Dwivedi")
        st.write("**Degree:** B.Tech CSE (Cyber Security)")
        st.write("**College:** SIRT Bhopal (RGPV)")
    with c2:
        st.write("**Skills:** Python · Pandas · NumPy · ML · Streamlit")
        st.write("**GitHub:** [github.com/AbhayDwivedi](https://github.com)")
        st.write("**LinkedIn:** [linkedin.com/in/AbhayDwivedi](https://linkedin.com)")