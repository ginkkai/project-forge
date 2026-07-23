# Industrial AI Knowledge Assistant

# Prototype 0.1 Data Dictionary


## 1. Purpose

This document defines the data structure required for the first prototype of the Industrial AI Knowledge Assistant.

The goal is to build an AI assistant that can answer industrial engineering questions based on company-specific knowledge.


---

# 2. Knowledge Base Structure



---

# 3. Data Categories


## 3.1 Equipment Knowledge

Purpose:

Provide fundamental information about industrial equipment.


Examples:

- Equipment manuals
- Technical specifications
- Operating parameters
- Maintenance requirements


Data Fields:

| Field | Description |
|---|---|
| Equipment Name | Name of machine |
| Model | Equipment model |
| Manufacturer | Equipment supplier |
| Specification | Technical parameters |
| Maintenance Cycle | Required maintenance interval |
| Common Errors | Known error codes |



---


## 3.2 SOP Documents

Purpose:

Provide standardized operation procedures.


Examples:

- Startup procedure
- Shutdown procedure
- Safety procedure
- Inspection checklist


Data Fields:

| Field | Description |
|---|---|
| Process Name | SOP name |
| Steps | Operation sequence |
| Safety Requirements | Safety instructions |
| Responsible Role | Operator/Engineer |



---


## 3.3 Failure Cases

Purpose:

Provide troubleshooting knowledge.


Examples:

- Error codes
- Failure symptoms
- Root causes
- Solutions


Data Fields:

| Field | Description |
|---|---|
| Equipment | Related machine |
| Error Code | Alarm code |
| Symptom | Observed problem |
| Root Cause | Failure reason |
| Solution | Recommended action |



---


## 3.4 Maintenance History

Purpose:

Capture historical repair experience.


Data Fields:

| Field | Description |
|---|---|
| Date | Maintenance date |
| Equipment | Machine name |
| Problem | Failure description |
| Cause | Root cause |
| Repair Action | Solution |
| Result | Final status |



---


## 3.5 Expert Knowledge

Purpose:

Capture undocumented engineer experience.


Examples:

- Troubleshooting tips
- Expert notes
- Best practices


This category represents the company's accumulated engineering knowledge.


---


# 4. Prototype 0.1 Dataset Target


| Data Type | Quantity |
|---|---:|
| Equipment | 5 |
| SOP Documents | 10 |
| Failure Cases | 50 |
| Maintenance Records | 100 |
| Expert Knowledge Notes | 30 |


---

# 5. Data Usage in AI System


Data Flow:


Company Documents

↓

Document Processing

↓

Knowledge Base

↓

Vector Database

↓

AI Retrieval

↓

Answer Generation


---

# 6. Prototype Goal


The first prototype should demonstrate:

1. AI can understand industrial documents.

2. AI can retrieve relevant knowledge.

3. AI can answer engineering questions with references.

4. AI responses are based on company knowledge rather than general information.

