# Solar Energy Forecasting System for Sri Lanka

An AI-based solar energy forecasting system developed for residential rooftop solar users in Sri Lanka.

The system uses historical weather data and modelled photovoltaic output together with machine learning to estimate future solar energy generation based on the user's location and installed solar system capacity.

## Live Application

https://solar-energy-forecasting-sri-lanka.streamlit.app/

## Main Features

- Location-based solar energy forecasting
- Automatic device location detection
- Manual location search
- Solar system capacity input
- Daily solar energy forecast
- Hourly solar generation forecast
- Weather-based forecasting
- Forecast charts and summary information
- Offline model explainability analysis using feature importance and SHAP

## Data Sources

- Open-Meteo
- PVGIS

The dataset covers representative locations from all 25 districts of Sri Lanka.

## Machine Learning

Several machine learning models were evaluated and compared. The final forecasting model was selected based on its performance using MAE, MSE, RMSE and R².

## Project Structure

- `app.py` – Streamlit web application
- `forecasting.py` – live forecasting functions
- `Notebooks/` – data preparation, EDA, feature engineering, modelling and explainability
- `Models/` – trained model and supporting files
- `Data/` – raw and processed datasets
- `Figures/` – model evaluation and explainability figures

## Technologies Used

Python, Streamlit, Pandas, NumPy, Scikit-learn, Altair, SHAP, Open-Meteo API and PVGIS.

