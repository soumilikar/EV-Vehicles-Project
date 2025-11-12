# EV-Vehicles-Project : EV Model Suggestion
This project leverages the categorical nature of the data, especially the car's Segment and BodyStyle, to help potential buyers narrow down their choices early in the purchase funnel.

## Project Description
The core of this project will be a Classification Model that predicts a car's market segment based on its technical specifications. This allows the system to guide users who know the performance they want but are unsure what type of car it defines (e.g., is a 400 km range high-end or standard?).

* ***Project Goal:*** To build a Classification Model that predicts the Segment (e.g., C-Segment, B-Segment, E-Segment) of an electric vehicle based purely on its performance and efficiency features.
* ***Model Type:*** Multi-Class Classification (e.g., Logistic Regression, K-Nearest Neighbors, or a Decision Tree/Random Forest Classifier) will be used.
* ***Target Variable (y):*** Segment (The category of the car: A, B, C, D, E, F, N, S).
* ***Feature Variables (X):*** The quantitative specs like AccelSec, TopSpeed_KmH, Range_Km, Efficiency_WhKm, and PriceEuro.

### Key ML Deliverables
**Segment Prediction :** ***Predicts the market segment given a set of performance specs.***
  
Customer Guidance: A user can input their non-price priorities (e.g., "Max 6.0 sec acceleration, Min 400 km range, Max 200 Wh/km efficiency"). The model predicts the resulting Segment (e.g., 'D-Segment'), which instantly narrows down the relevant models. 

**EV-Assist Chatbot :** ***Creating a Chatbot to answer customer queries***

A user provides their desired specs (e.g., "I want a car with 500 range, 5-second acceleration, and a price under €60,000"). The chatbot then presents all cars in the database that meet those specs.
The chatbot can also compare segments directly: "Is the range difference between a C-Segment and D-Segment significant?" The answer is based on the trained model's feature importance and split points.

Sample Chatbot Conversation:

<img width="996" height="527" alt="Screenshot 2025-11-03 000750" src="https://github.com/user-attachments/assets/c31e4962-5932-49f1-a420-eb2790ca3d78" />

Final Project:

<img width="1475" height="795" alt="image" src="https://github.com/user-attachments/assets/5f667cca-e132-4ac4-aabe-d2deec535fb5" />

<img width="1688" height="913" alt="image" src="https://github.com/user-attachments/assets/4b8392bf-ac34-476b-a9a7-1b8c58af77e3" />

