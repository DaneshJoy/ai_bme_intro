# Proposed Group Project Brief for the Course

> [!IMPORTANT]
> **This document is a "proposal" and must be reviewed and edited by the instructor before it is presented to students.** The grading details, project topic, and dates can be changed according to the conditions of the class. The instructor announces this document in Session 1 and publishes the final version.

---

## 1. Proposed Project Topic

**"Designing and Evaluating a Small AI Agent or Model for a Biomedical Engineering Problem"**

Each group (2 to 3 people) chooses a realistic but educational problem and builds a small Prototype. Suggested examples (a sample list, not a limit):

| Sample topic | Input | Output |
|---|---|---|
| Classifying a synthetic ECG signal into normal/abnormal groups | Synthetic signal or a public educational dataset | A label and one evaluation measure |
| Classifying synthetic laboratory data for educational screening | A table of synthetic features | A class label |
| Scheduling nursing shifts for a ward with informed search | Number of nurses, shift constraints | A valid shift schedule |
| A rule-based agent for generating alarms on a synthetic signal | A synthetic heart or respiration signal | An alarm at a defined event |

> [!WARNING]
> All projects are **educational and non-diagnostic**. Using real patient data is not permitted; only synthetic or artificial data, or public educational datasets (such as the datasets bundled with scikit-learn), may be used. Under no circumstances is the project's output a tool for diagnosis or clinical decision-making.

---

## 2. Rules and Constraints

- **Team size:** 2 to 3 people; each member must write their own contribution in the report.
- **Tools:** Python 3 with the libraries `numpy`, `pandas`, `matplotlib`, and `scikit-learn`. No GPU or large models required.
- **Offline execution:** The code must run without any internet download (only datasets bundled with the libraries, or synthetic data).
- **Transparency in the use of AI tools:** Any help taken from language models in the code or report must be disclosed in a short section of the report.
- **Educational and readable code:** The code must be runnable, documented, and short; long examples or heavy models are prohibited.

---

## 3. Project Deliverables

1. **Code:** A Colab notebook or Python script with a short explanation of each part.
2. **Report:** 4 to 6 pages including: problem definition, description of the data or environment, method (algorithm/model), evaluation, limitations, and a responsible discussion of the medical application.
3. **Presentation:** 5 to 8 minutes in Session 29, followed by questions and answers.

---

## 4. Weekly Timeline (Proposed)

| Week (Session) | Expected work |
|---|---|
| Session 5 | Form groups and choose a topic; register the topic with the instructor |
| Session 10 | Initial problem formulation (input, output, success criterion) |
| Session 15 | Draft prototype code; brief instructor feedback |
| Session 21 | Runnable version and initial evaluation |
| Session 26 | Complete the code and draft the report |
| Session 29 | Final submission of code and report, and presentation in class |

---

## 5. Project Grading Criteria (100 Points)

| Criterion | Description | Points |
|---|---|---|
| Problem definition and motivation | The problem is clear, realistic, and appropriate to the course | 15 |
| Design and implementation | An appropriate method is chosen and correctly implemented | 25 |
| Evaluation | An appropriate evaluation measure is used and the results are reported with numbers | 20 |
| Code quality | The code is runnable, readable, and documented | 15 |
| Report and presentation | The report is well organized and the presentation is clear | 15 |
| Teamwork and accountability | Members' contributions are transparent; use of AI tools is disclosed | 10 |
| **Total** | | **100** |

---

## 6. Proposed Course Grade Weights

| Component | Proposed weight |
|---|---|
| Assignments and in-class activities | 25% |
| Group project | 25% |
| Midterm 1 (Session 16) | 20% |
| Midterm 2 (Session 28) | 20% |
| Participation and active attendance | 10% |

These weights can be adjusted by the instructor. Before the final announcement, check them against the faculty's policy.
