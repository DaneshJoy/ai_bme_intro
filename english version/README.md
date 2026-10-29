# Introduction to Artificial Intelligence and Its Applications in Biomedical Engineering

A 29-session course for undergraduate Biomedical Engineering students: from the foundations of AI and intelligent agents to machine learning, deep learning, and biomedical applications — with hands-on code and a group project.

## Repository Structure

| Path | Contents |
|:--|:--|
| `session_01_*.md` to `session_29_*.md` | Session files (course content + homeworks) |
| `code/` | Runnable teaching code; guide: `code/README.md`, dependencies: `code/requirements.txt` |
| `project/project-brief_en.md` | Group project proposal + evaluation + grade weights |
| `code/python_selfstudy_en.ipynb` | Python self-study notebook (preparation assignment for Session 4) |

## Session List

| Session | Topic | Title | File |
|:-:|:--|:--|:--|
| 1 | Foundations and Preparation | Course Introduction and Getting to Know AI | [session_01_intro_to_ai_en.md](session_01_intro_to_ai_en.md) |
| 2 | Foundations and Preparation | Intelligent Agents and Environments; Introduction to LLMs | [session_02_agents_and_llm_en.md](session_02_agents_and_llm_en.md) |
| 3 | Foundations and Preparation | Biological and Health Data; Big Data and Generative AI | [session_03_health_data_and_genai_en.md](session_03_health_data_and_genai_en.md) |
| 4 | Foundations and Preparation | Introductory Python and Data Workshop | [session_04_python_workshop_en.md](session_04_python_workshop_en.md) |
| 5 | Search and Problem Solving | Formulating Search Problems; BFS and DFS | [session_05_search_bfs_dfs_en.md](session_05_search_bfs_dfs_en.md) |
| 6 | Search and Problem Solving | Other Uninformed Search Methods; IDS and UCS | [session_06_uninformed_search_ucs_ids_en.md](session_06_uninformed_search_ucs_ids.md) |
| 7 | Search and Problem Solving | Informed Search and Heuristic Functions | [session_07_informed_heuristics_en.md](session_07_informed_heuristics.md) |
| 8 | Search and Problem Solving | The A* Algorithm | [session_08_a_star_en.md](session_08_a_star.md) |
| 9 | Search and Problem Solving | Search Algorithms Implementation Workshop | [session_09_search_workshop_en.md](session_09_search_workshop.md) |
| 10 | Optimization and Constraints | Local Search and Genetic Algorithms | [session_10_local_search_genetic_en.md](session_10_local_search_genetic.md) |
| 11 | Optimization and Constraints | Search in Continuous Spaces and Gradient Descent | [session_11_continuous_gradient_descent_en.md](session_11_continuous_gradient_descent.md) |
| 12 | Optimization and Constraints | Constraint Satisfaction Problems (CSP) | [session_12_csp_en.md](session_12_csp.md) |
| 13 | Optimization and Constraints | Solving CSPs and the Scheduling Problem | [session_13_csp_scheduling_en.md](session_13_csp_scheduling.md) |
| 14 | Optimization and Constraints | Problem-Solving Session 1: Search, A*, Optimization, and CSP | [session_14_problem_solving_1_en.md](session_14_problem_solving_1.md) |
| 15 | Adversarial Decisions and Midterm 1 | Adversarial Search; Minimax and Alpha–Beta Pruning | [session_15_adversarial_minimax_en.md](session_15_adversarial_minimax.md) |
| 16 | Adversarial Decisions and Midterm 1 | Midterm 1 (covers Sessions 1–15) | [session_16_midterm_1_en.md](session_16_midterm_1.md) |
| 17 | Logic and Decisions under Uncertainty | Propositional and First-Order Logic; Expert Systems | [session_17_logic_expert_systems_en.md](session_17_logic_expert_systems.md) |
| 18 | Logic and Decisions under Uncertainty | Markov Decision Processes (MDP) | [session_18_mdp_en.md](session_18_mdp.md) |
| 19 | Logic and Decisions under Uncertainty | Reinforcement Learning and Q-learning | [session_19_reinforcement_learning_en.md](session_19_reinforcement_learning.md) |
| 20 | Logic and Decisions under Uncertainty | Bayesian Networks and Markov Models | [session_20_bayesian_markov_en.md](session_20_bayesian_markov.md) |
| 21 | Machine Learning | Machine Learning Basics and Model Evaluation | [session_21_ml_basics_evaluation_en.md](session_21_ml_basics_evaluation.md) |
| 22 | Machine Learning | Machine Learning Workshop with scikit-learn | [session_22_sklearn_workshop_en.md](session_22_sklearn_workshop.md) |
| 23 | Machine Learning | Problem-Solving Session 2: Logic, MDP, Probabilistic Models, and ML | [session_23_problem_solving_2_en.md](session_23_problem_solving_2.md) |
| 24 | Deep Learning and Medical Applications | Neural Networks and Deep Learning | [session_24_neural_networks_deep_learning_en.md](session_24_neural_networks_deep_learning.md) |
| 25 | Deep Learning and Medical Applications | AI in Biosignals and BCI | [session_25_ai_biosignals_bci_en.md](session_25_ai_biosignals_bci.md) |
| 26 | Deep Learning and Medical Applications | AI in Medical Imaging | [session_26_ai_medical_imaging_en.md](session_26_ai_medical_imaging.md) |
| 27 | Deep Learning and Medical Applications | Other AI Applications in Biomedical Engineering; Ethics and Validation | [session_27_ai_bme_ethics_validation_en.md](session_27_ai_bme_ethics_validation.md) |
| 28 | Wrap-up and Project | Midterm 2 / Second Mid-term Assessment (covers Sessions 17–26) | [session_28_midterm_2_en.md](session_28_midterm_2.md) |
| 29 | Wrap-up and Project | The Future of AI in Medicine and Project Presentations | [session_29_future_of_ai_medicine_en.md](session_29_future_of_ai_medicine.md) |

> [!IMPORTANT]
> All 29 session files are ready and linked from the table above.

## Project and Grading

- Description of the group project, timeline, 100-point evaluation, and suggested course grade weights: [project/project-brief_en.md](project/project-brief_en.md)
- The project topic is announced in Session 1 and groups are formed in Session 5; final presentations take place in Session 29.
- Teaching code for each session is placed in the [`code/`](code) folder; the full code map is in `code/README.md`.

## 60/90-Minute Timing Guide

- Each session file is written for a session of up to 90 minutes and also includes a condensed 60-minute plan;
- If the class is only 60 minutes, we shorten the group activities and move optional parts to homework;
- For Session 4, the Python self-study prerequisite is important. If students have truly no prior exposure, we run the NumPy/Pandas workshop.

## Course References

List of 11 references (books, papers, and instructor content)

| Ref. No. | Reference and Year | Author(s) |
|:-:|:--|:--|
| 1 | Artificial Intelligence: A Modern Approach (2016) | Stuart J. Russell; Peter Norvig |
| 2 | Artificial Intelligence in Medicine: Technical Basis and Clinical Applications (2021) | Bradley J. Erickson |
| 3 | Advances in Artificial Intelligence, Computation, and Data Science (2021) | T. D. Pham; H. Yan; M. W. Ashraf; F. Sjöberg |
| 4 | Medical Robotics and AI-Assisted Diagnostics for a High-Tech Healthcare Industry (2024) | A. Khang |
| 5 | Artificial Intelligence in Tissue and Organ Regeneration (2023) | C. P. Sharma; T. Chandy; V. Thomas |
| 6 | AI and IoT-Based Technologies for Precision Medicine (2023) | A. Khang |
| 7 | Application of Artificial Intelligence in Tissue Engineering (2024) | R. Bagherpour; G. Bagherpour; P. Mohamadi |
| 8 | Machine Learning in Tissue Engineering (2023) | J. L. Guo; M. Januszyk; M. T. Longaker |
| 9 | Artificial Intelligence in Biomedical Engineering and Informatics: An Introduction and Review (2010) | Y. Peng; Y. Zhang; L. Wang |
| 10 | Python Machine Learning by Example (2017) | Y. H. Liu |
| 11 | Content produced by the instructor (2026) | Saeed Mohaghegh |

The references for each session are listed in the "References for this session" line at the top of that file.

## Safety Reminder

All examples, datasets, and code in this course are **educational and non-diagnostic** and must not be used for clinical decision-making about real patients.
