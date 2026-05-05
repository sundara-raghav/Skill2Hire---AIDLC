# Functional Design Clarifications: ML Pipeline Unit

## Purpose
Resolve ambiguities detected in functional design plan answers.

---

## Clarification Required

### Question 14 Follow-Up: Derived Features Specification

You selected **"B) Yes - Minimal"** for derived features, which means creating a few key derived features.

**Please specify which derived features should be created:**

Examples of possible derived features:
- **Skills_Total** = Programming_Skills + Communication_Skills
- **Experience_Score** = (Num_Projects * 0.4) + (Internship_Experience * 0.6)
- **Academic_Performance** = CGPA * Aptitude_Score
- **Overall_Profile_Score** = Weighted combination of all features
- **Has_Experience** = Boolean (Num_Projects > 0 OR Internship_Experience == True)
- **Skills_Average** = (Programming_Skills + Communication_Skills) / 2
- **Certification_Level** = Categorize certifications (None, Low, Medium, High)

**Please list the specific derived features you want to create:**

[Answer]: Total_Skills_Score
Experience_Score
CGPA_Project_Score

---

## Instructions

1. List the derived features you want to create (e.g., "Skills_Total, Experience_Score, Academic_Performance")
2. For each feature, briefly describe the calculation if not obvious
3. Type **"done"** when you've provided the details

---

**Status**: Awaiting clarification
