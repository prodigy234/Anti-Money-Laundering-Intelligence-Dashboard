
# 🏦 Anti-Money Laundering (AML) Intelligence Dashboard

## 🔗 Live App
https://antimoneylaundering.streamlit.app

---

## 📌 Project Overview

This project is a **full-scale Anti-Money Laundering (AML) Monitoring System** built using **Streamlit, Python, and advanced analytics techniques**.

It simulates how real financial institutions detect, monitor, and investigate suspicious financial activities.

---

## 🧠 Key Capabilities

- 🔍 Manual AML Screening (Fuzzy Matching)
- 📊 Interactive AML Dashboard
- 🚨 Alert Generation System
- 💳 Transaction Monitoring
- 📁 Case Management Workflow
- 🔄 Continuous Monitoring System

---

## 🏗️ System Architecture

Customer → Screening → AML Hit → Sanction Detail  
         → Transaction → Alert → Case  

---

## 📂 Dataset Structure

### 1. Customers Table
Stores customer identity (KYC data)

Columns:
- customer_id (Primary Key)
- full_name
- first_name
- last_name
- dob
- country
- created_at

---

### 2. Screenings Table
Each AML lookup generates a screening record

Columns:
- screening_id (Primary Key)
- customer_id (Foreign Key)
- screening_date
- risk_score (0–100)
- risk_level (LOW, MEDIUM, HIGH)
- status (NEW, REVIEWED, ESCALATED)

---

### 3. AML Hits Table
Stores matches against watchlists

Columns:
- hit_id (Primary Key)
- screening_id (Foreign Key)
- list_type (PEP, SANCTION, CRIME, WATCHLIST)
- match_type (exact, fuzzy)
- source (OFAC, Interpol, etc.)
- match_score

---

### 4. Sanctions Details Table
Provides deep intelligence about flagged individuals

Columns:
- sanction_id (Primary Key)
- hit_id (Foreign Key)
- name
- aliases
- date_of_birth
- nationality
- reason
- source_link

---

### 5. Transactions Table
Tracks financial activity

Columns:
- transaction_id
- customer_id
- amount
- location
- timestamp
- risk_flag

---

### 6. Monitoring Table
Controls continuous screening

Columns:
- monitoring_id
- customer_id
- is_active
- frequency (daily, weekly)
- last_checked

---

### 7. Alerts Table
Stores generated alerts

Columns:
- alert_id
- customer_id
- screening_id
- alert_type
- description
- created_at
- status

---

### 8. Cases Table
Manages investigations

Columns:
- case_id
- customer_id
- alert_id
- assigned_to
- status (OPEN, INVESTIGATING, CLOSED)
- decision
- created_at

---

## 🔄 Workflow

1. Customer is onboarded  
2. AML Screening is performed  
3. Potential matches (AML Hits) are detected  
4. Sanctions details provide deeper insights  
5. Transactions are monitored  
6. Alerts are generated  
7. Cases are created and investigated  

---

## 📊 Dashboard Features

- Risk Distribution Analysis  
- Status Tracking  
- Screening Trends  
- AML Hit Analysis  
- High-Risk Customer Identification  
- Real-Time Alerts  

---

## 🧪 Technologies Used

- Python
- Streamlit
- Pandas
- RapidFuzz
- Plotly
- Scikit-learn

---

## 🚀 Deployment

Deployed on Streamlit Cloud

---

## 🎯 Why This Project Matters

This project replicates a **real-world banking AML system**, enabling:

- Financial crime detection
- Compliance monitoring
- Risk assessment
- Data-driven decision-making

---

## 🧠 Interview Insight

This is not just a dashboard — it is a **complete AML lifecycle system**, covering:

- Data modeling
- Risk analytics
- Monitoring systems
- Investigation workflows

---

## 👨‍💻 Author

Built as an advanced AI & Data Engineering project for real-world AML simulation.
