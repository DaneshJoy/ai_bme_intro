# Session 4: Introductory Python and Data Workshop

> **Course:** Introduction to Artificial Intelligence and Its Applications in Biomedical Engineering
> **Suggested duration:** 60 to 90 minutes (hands-on workshop) · **Level:** Introductory
> **Tool:** Google Colab (colab.research.google.com)
> **References for this session:** Ref. 10 (Liu, 2017), Ref. 11 (instructor content)

---

## Session Objectives
By the end of this session, students will be able to:
1. Create a notebook in Colab and run a code cell.
2. Read and modify short Python code (variables, conditionals, loops, functions, lists, dictionaries).
3. Load and inspect a dataset with NumPy and Pandas.
4. Identify Missing Values and compute simple statistics.
5. Use an LLM responsibly to explain and debug code.

> [!IMPORTANT]
> The goal of this session is not to teach Python completely. The goal is preparation for reading and modifying short code in later sessions.

**Suggested prerequisite:** Before the session, students should have reviewed the self-study notebook `python_selfstudy.ipynb` (running cells, variables, conditionals, lists, functions). If this prerequisite has not been met, simplify the Python review section and run NumPy/Pandas as a demonstration.

---

## 1. Getting Started with Colab
1. Go to colab.research.google.com and sign in with a Google account.
2. Click **New notebook**.
3. In a code cell, type the following and run it with `Shift + Enter`:

```python
print("Hello, world of artificial intelligence!")
```

## 2. Quick Python Review

**Variables and data types:**
```python
heart_rate = 78          # integer
temperature = 36.8       # float
patient = "Ali"          # string
is_alarm = False         # boolean
```

**Conditionals:**
```python
if heart_rate > 100:
    print("Above the sample threshold")
elif heart_rate < 50:
    print("Below the sample threshold")
else:
    print("Within the sample range")
```

**Loops and lists:**
```python
rates = [72, 80, 95, 110, 65]
for r in rates:
    print(r)
print(len(rates), max(rates), sum(rates) / len(rates))
```

**Functions:**
```python
def classify_hr(hr):
    if hr > 100:
        return "Above the sample threshold"
    elif hr < 50:
        return "Below the sample threshold"
    return "Within the sample range"

print(classify_hr(110))
```

> [!WARNING]
> The thresholds of 50 and 100 are only for practicing conditionals and are not a diagnostic rule or medical recommendation.

**Dictionaries:**
```python
patient_info = {"name": "Ali", "age": 45, "hr": 78}
print(patient_info["age"])
patient_info["hr"] = 90
```

## 3. NumPy and Pandas

```python
import numpy as np
import pandas as pd

x = np.array([72, 80, 95, 110, 65])
print(x.mean(), x.std(), x.max())
```

**Loading the breast cancer dataset** (a scikit-learn educational dataset, no download needed):

```python
from sklearn.datasets import load_breast_cancer

data = load_breast_cancer(as_frame=True)
df = data.frame
```

> [!TIP]
> Put each of the blocks below in a **separate cell**. Colab only displays the value of the last expression in each cell; to see several outputs in one cell, use `print`.

```python
df.head()          # first five rows
```
```python
print(df.shape)    # (number of rows, number of columns)
```
```python
df.info()          # column types (prints its own output)
```
```python
df.describe()      # descriptive statistics
```

**Checking missing values and class distribution:**
```python
print(df.isna().sum().sum())      # total number of missing values
print(df["target"].value_counts())  # class distribution
print(data.target_names)          # ['malignant' 'benign']
```

> [!WARNING]
> In this dataset, `target = 0` means **malignant** and `target = 1` means **benign**. This dataset is for programming practice; the labels or model outputs must not be used for decisions about a real patient.

**Comparing the mean of a feature between two classes:**
```python
df.groupby("target")["mean radius"].mean()
```

**Missing values exercise** (this dataset has no missing values; for practice we deliberately remove a few values):
```python
df_missing = df.copy()
df_missing.loc[[0, 5, 10], "mean radius"] = np.nan

print(df_missing["mean radius"].isna().sum())     # 3

mean_val = df_missing["mean radius"].mean()
df_missing["mean radius"] = df_missing["mean radius"].fillna(mean_val)
print(df_missing["mean radius"].isna().sum())     # 0
```

> [!NOTE]
> Replacing with the mean is only a simple method and is not always appropriate. It will be discussed further in later sessions.

**Drawing a simple plot:**
```python
import matplotlib.pyplot as plt
df.boxplot(column="mean radius", by="target")
plt.show()
```

## 4. Responsible Use of LLMs in Coding

**You may:**
- Ask an LLM to explain an error or describe code line by line.
- Use it to get ideas and write an initial prototype.

**You must:**
1. Read and understand the code before running it.
2. Manually check the result on a simple input.
3. Be skeptical of unexpected results.
4. Report your use of the tool transparently.

**Example of a good prompt:**
> "Explain this Python code line by line for a beginner student, and tell me what error occurs if the target column does not exist: ..."

---

## 🔬 Connection to Biomedical Engineering
The `load_breast_cancer` dataset contains features measured from tumor tissue (such as `mean radius` and `mean area`) and, in teaching, provides a real example of the "malignant/benign classification" problem. In Session 21, this same dataset is used again to teach model evaluation measures. Important reminder: working with this dataset is a programming exercise and none of its output has diagnostic use.

## 💻 Teaching Code
All the code of this session runs cell by cell within this file; this session has no separate code file. The session prerequisite is the notebook `code/python_selfstudy.ipynb` in the course root. The list of libraries required for the whole course is in `code/requirements.txt` (`numpy`, `pandas`, `matplotlib`, `scikit-learn`), which are pre-installed in Colab and Anaconda.

---

## ✍️ Workshop Activity
Do the following in Colab and note the results:
1. Load the dataset and report its dimensions.
2. Find the number of samples in each class. Is the data balanced?
3. Compute the mean of `mean area` for both classes.
4. Write a function that returns the mean and standard deviation of a column.
5. (Optional) Ask an LLM to write a histogram plot for `mean radius`, review and run the code, and say what you corrected.

### End-of-Session Checklist
- [ ] I ran the notebook.
- [ ] I know the difference between a list and a dictionary.
- [ ] I can open a dataset with Pandas and run `head`, `info`, and `describe`.
- [ ] I can count missing values.

### Common Errors

| Error | Usual cause |
|:--|:--|
| `NameError` | A variable is not defined or the previous cell was not run |
| `KeyError` | The column name or key is wrong |
| `IndentationError` | The code indentation is incorrect |
| `ModuleNotFoundError` | The library is not installed or not imported |

## 📘 Glossary

| Term | Meaning |
|:--|:--|
| Cell (notebook) | The unit of executing code or text in Colab |
| DataFrame | A data table in Pandas |
| NaN | Missing value (Not a Number) |
| Library | A ready-made collection of code, such as NumPy |
| Prompt | The input text given to a language model |

## ❓ Self-Assessment Questions
1. What is the difference between a list and a dictionary in Python? For what kind of data is each suitable?
2. What does the output of `df.shape` show, and why is counting missing values important?
3. Why does `target = 0` mean malignant in this dataset? How can we be sure using `data.target_names`?

> The answer key is in the "Instructor's Guide" section at the end of the file.

## 📝 Assignment
Complete the notebook and submit exercises 1 to 4 with their outputs. If you used an LLM, write your prompt and your corrections in a text cell.

## 📚 Suggested Reading
- Liu (2017), Python Machine Learning by Example: the introductory chapters on Python and NumPy (the sections relevant to preparation)
- Short NumPy and Pandas documentation for beginners (optional)
