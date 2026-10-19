# Teaching Code for the Course "Introduction to Artificial Intelligence and Its Applications in Biomedical Engineering"

This folder contains the runnable teaching code for the course sessions. Each file corresponds to one of the course sessions and is referenced from that session's file.

> [!NOTE]
> Sessions 1 to 3 and Sessions 16, 28, and 29 have no separate code file (the code for Sessions 1 to 3 is inside the session file text; Sessions 16 and 28 are review and exams; Session 29 is project presentations). The files for Sessions 5 to 29 are added to this folder at the same time as the content of those sessions is produced.

## Dependencies

```bash
pip install -r code/requirements.txt
```

Contents of `requirements.txt`: `numpy`, `pandas`, `matplotlib`, `scikit-learn` (no TensorFlow/PyTorch).

All code runs **offline**: it uses only the datasets bundled with scikit-learn or synthetic/artificial data, and no internet download is needed.

## How to Run

- Scripts:

```bash
python code/session_05_bfs_dfs_en.py
```

- Notebooks (`ipynb`): open them in Google Colab (**File > Upload notebook**) or run them locally with Jupyter.

> [!TIP]
> In Google Colab these libraries are pre-installed and no `pip install` is needed.

## Code Map by Session

| Session | File | Topic |
|:-:|:--|:--|
| 5 | `session_05_bfs_dfs_en.py` | BFS and DFS search on a hospital network graph / maze |
| 6 | `session_06_uninformed_search_ucs_ids_en.py` | UCS and IDDFS; comparing cost and node count |
| 7 | `session_07_informed_heuristics_en.py` | Informed search; admissible heuristics and comparing h functions |
| 8 | `session_08_a_star_en.py` | The A* algorithm on a network; checking heuristic admissibility and optimality |
| 9 | `session_09_search_workshop_en.ipynb` and `session_09_search_workshop_en.py` | Workshop: comparing BFS, DFS, UCS, and A* |
| 10 | `session_10_local_search_genetic_en.py` | Local search: Hill Climbing, Simulated Annealing, and the genetic algorithm |
| 11 | `session_11_gradient_descent_en.py` | Gradient descent and its variants on a fitting function |
| 12 | `session_12_csp_backtracking_en.py` | CSP with Backtracking, FC, and MRV on a guard/assignment problem |
| 13 | `session_13_csp_scheduling_en.py` | Nursing shift scheduling with CSP |
| 14 | `session_14_solutions_en.py` | Code solutions for Problem-Solving Session 1 |
| 15 | `session_15_minimax_alphabeta_en.py` | Minimax and alpha–beta pruning on Tic-Tac-Toe with node counting |
| 17 | `session_17_logic_expert_system_en.py` | Forward chaining and a simple medical rule engine |
| 18 | `session_18_mdp_value_iteration_en.py` | Value Iteration and Policy Iteration on a mini medical MDP |
| 19 | `session_19_q_learning_en.py` | Tabular Q-learning on a grid environment |
| 20 | `session_20_bayes_markov_en.py` | Simple Bayesian inference and Markov model/HMM |
| 21 | `session_21_ml_metrics_en.py` | Accuracy, sensitivity, specificity, ROC, and the confusion matrix |
| 22 | `session_22_sklearn_workshop_en.ipynb` and `session_22_sklearn_workshop_en.py` | Machine learning workshop with scikit-learn (breast cancer dataset) |
| 23 | `session_23_solutions_en.py` | Code solutions for Problem-Solving Session 2 |
| 24 | `session_24_nn_from_scratch_en.py` | From-scratch implementation of a perceptron and an MLP for XOR, with no external dependencies |
| 25 | `session_25_biosignal_bci_en.py` | Synthetic ECG signal, feature extraction, and classification |
| 26 | `session_26_medical_imaging_en.py` | Synthetic imaging and a nearest-centroid classifier on synthetic data |
| 27 | `session_27_ethics_fairness_en.py` | An example of bias and fairness, and model validation |

## Safety Reminder

All code and datasets in this folder are **educational and non-diagnostic**. No output from this code should be used for decision-making about a real patient.
