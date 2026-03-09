
# Utility Bill Automation System

A modular automation system designed to log into utility provider portals, download billing statements, extract key billing data, and compile structured reports for recurring processing.

> **Proposal Demo Repository**  
> This repository demonstrates the architecture for automating utility bill retrieval across multiple providers using a scalable Python automation framework.

---

# Live Demo

**Demo Website**

https://adamhumen123-blip.github.io/utility-bill-automation-demo/

**GitHub Repository**

https://github.com/adamhumen123-blip/utility-bill-automation-demo

The demo includes:

• A simulated provider portal  
• Sample downloadable bill data  
• Example extracted billing output  
• Demonstration of the automation workflow  

---

# Demo Simulation

This repository includes a simulated environment to demonstrate how the automation system works before connecting to real provider portals.

### Demo Files

`demo_portal.html`  
Simulated utility provider login portal used for testing automation logic.

`sample_bill.txt`  
Example downloadable bill file used to demonstrate data extraction.

`simulation_demo.py`  
Example script that parses billing data and converts it into structured output.

`index.html`  
Demo landing page that simulates the final automation dashboard.

---

# System Overview

The automation system handles the entire lifecycle of utility bill processing.

### Workflow

1. Login to each provider portal using securely stored credentials  
2. Navigate to the billing section  
3. Locate the latest bill  
4. Download the bill file automatically  
5. Extract key billing fields  
6. Consolidate all provider data into a central report  
7. Export results to Google Sheets, Excel, or CSV  
8. Run automatically on a recurring schedule

---

# Key Features

| Feature | Description |
|------|------|
| Portal Automation | Automated login and navigation using browser automation |
| Bill Download | Automatically retrieves the latest bill for each account |
| Data Extraction | Extracts billing fields such as amount due and usage |
| Multi Provider Support | Modular design for adding new providers easily |
| Central Reporting | Consolidates all providers into structured datasets |
| Cloud Ready | Can run on cloud infrastructure or scheduled workflows |
| Secure Credentials | Uses environment variables instead of hardcoded secrets |
| Error Isolation | Failures from one provider do not affect others |

---

# Architecture

Main Automation Runner  
        ↓  
Run Providers Pipeline  
        ↓  
Provider Modules (electricity, gas, water)  
        ↓  
Bill Extraction Engine  
        ↓  
Structured Billing Data  
        ↓  
Report Generation  
        ↓  
Google Sheets / Excel / CSV  

---

# Repository Structure

utility-bill-automation-demo

README.md  
requirements.txt  

main.py  
simulation_demo.py  

base_provider.py  
electricity_provider.py  

demo_portal.html  
sample_bill.txt  

index.html  

---

# Provider Architecture

Each utility provider is handled by a separate module.

Example provider modules:

electricity_provider.py  
gas_provider.py  
water_provider.py  

Each module contains the automation logic for:

• Portal login  
• Billing navigation  
• Bill detection  
• File download  

If a provider changes its portal layout, only that provider module needs updating.

---

# Example Extracted Output

| Provider | Account Number | Billing Period | Amount Due | Due Date | Usage |
|------|------|------|------|------|------|
| Demo Electricity Provider | ACC-100245 | Jan 2026 | $143.22 | 2026-02-10 | 845 kWh |
| Demo Gas Provider | ACC-100987 | Jan 2026 | $88.12 | 2026-02-12 | 120 Therms |

---

# Adding a New Provider

Adding a new utility provider requires creating a single provider module.

providers/
   electricity_provider.py
   gas_provider.py
   water_provider.py
   new_provider.py

Each provider handles its own portal logic, allowing the system to scale to dozens of providers.

---

# Scaling to 50 Providers

The architecture supports scaling from a few providers to dozens.

| Scale | Implementation |
|------|------|
| 3 Providers | Current demo structure |
| 10 Providers | Add additional provider modules |
| 50 Providers | Run providers concurrently using parallel execution |

Because providers are isolated, changes to one portal never break the others.

---

# Running the System

Clone the repository

git clone https://github.com/adamhumen123-blip/utility-bill-automation-demo  
cd utility-bill-automation-demo  

Install dependencies

pip install -r requirements.txt  

Run the demo extraction

python simulation_demo.py  

Run the automation runner

python main.py  

---

# Deployment Options

This automation system can run in multiple environments.

• Local automation server  
• Cloud virtual machines  
• Docker containers  
• Scheduled GitHub workflows  
• Cloud automation platforms  

---

# Security

Credentials are never stored in code.

Sensitive information should be stored using:

• Environment variables  
• Secret management tools  
• Cloud credential vaults  

---

# Maintenance

If a provider portal changes its layout:

1. Update the provider module selectors  
2. Adjust the navigation steps  
3. Re-run the automation  

No other files need to be modified.

---

# Technologies Used

Python  
Automation scripting  
Browser automation frameworks  
Data extraction tools  
Cloud automation workflows  

---

# Purpose of This Repository

This repository demonstrates the architecture for a scalable automation system capable of handling dozens of utility providers while remaining maintainable and easy to update.

The included demo simulation illustrates the full concept before connecting the system to real provider portals.

---

Automation Concept

Portal Login → Bill Retrieval → Data Extraction → Structured Reporting → Automated Recurring Processing
