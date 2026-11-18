# 🛡️ AWS SSM Patch Compliance Light Board Pro

An enterprise NOC-style patch monitoring system powered by **AWS Systems Manager (SSM)** and a serverless **AWS Lambda** backend, visualized with a high-tech **3-LED Panel** (Green / Yellow / Red) built in **Streamlit**.

---

## 🌟 New Interactive Features

* **3 UI Color Themes**: Cyber NOC (Default), Matrix Terminal, and Midnight Blue.
* **Interactive Fleet Simulator**: Dynamically test any fleet size (1–20 nodes) with custom slider controls.
* **Audible Alert Engine**: Emits an alert tone when the system transitions to the 🔴 RED state.
* **DevOps Action Center**: 1-click simulation triggers for SSM Scans, Auto-Remediation, and Reboots.
* **Instance Explorer**: Real-time search by Instance ID/OS and filter by status.
* **Fleet Health Progress Gauge**: Visual percentage bar calculating overall compliance score.
* **Audit Hub & Export**: 1-click download of compliance telemetry in **CSV** and **JSON**.
* **Auto-Refresh Engine**: Configurable polling intervals (5s to 60s).

---

## 🚀 Quick Start in Visual Studio Code

### 1. Open in VS Code
1. Open Visual Studio Code.
2. Go to **File** → **Open Folder...** and select this extracted folder (`patch-dashboard`).

### 2. Open Terminal
* Press `Ctrl + ` ` (backtick) or go to **Terminal** → **New Terminal**.

### 3. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 4. Run the Light Board Dashboard
```bash
python -m streamlit run app.py
```
*(Or double-click `run_dashboard.bat`)*

---

## 🏗️ Architecture

```
EC2 Fleet (Amazon Linux + SSM Agent)
         ↓
AWS Systems Manager (Patch Manager)
         ↓
AWS Lambda Function (PatchComplianceEvaluator)
         ↓
Lambda Function URL (HTTPS REST API)
         ↓
Streamlit Light Board Pro (VS Code)
```

## 💡 The 3-LED Indicator Logic

* 🟢 **GREEN (Compliant)**: 100% of managed instances satisfy baseline patch policies with 0 missing patches and 0 pending reboots.
* 🟡 **YELLOW (Pending)**: Updates are pending a system reboot (`InstalledPendingRebootCount > 0`) or instances require a baseline scan.
* 🔴 **RED (Non-Compliant)**: One or more instances are missing critical/security patches (`MissingCount > 0`).

---

## 📁 Project Contents

* `app.py`: High-tech Streamlit frontend with 3-LED panel, themes, search, and export.
* `lambda_function.py`: AWS Lambda backend code that queries SSM and computes compliance states.
* `presentation.html`: 9-slide interactive keynote presentation ready to open in any browser.
* `generate_ppt.py`: Python script to generate PowerPoint `.pptx` slides.
* `requirements.txt`: Python package dependencies.
* `run_dashboard.bat`: Windows 1-click launcher.
