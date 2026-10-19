# کد آموزشی درس «مقدمه‌ای بر هوش مصنوعی و کاربرد آن در مهندسی پزشکی»

این پوشه شامل کدهای آموزشی اجراشدنی جلسات درس است. هر فایل با یکی از جلسات درس مطابقت دارد و در فایل همان جلسه به آن ارجاع داده می‌شود.

> [!NOTE]
> جلسات ۱ تا ۳ و جلسات ۱۶، ۲۸ و ۲۹ فایل کد جداگانه ندارند (کد جلسات ۱ تا ۳ درون متن فایل جلسه است؛ جلسات ۱۶ و ۲۸ مرور و آزمون‌اند؛ جلسه ۲۹ ارائه پروژه است). فایل‌های جلسات ۵ تا ۲۹ هم‌زمان با تولید محتوای همان جلسات در این پوشه ساخته می‌شوند.

## وابستگی‌ها

```bash
pip install -r code/requirements.txt
```

محتوای `requirements.txt`: `numpy`، `pandas`، `matplotlib`، `scikit-learn` (بدون TensorFlow/PyTorch).

همه کدها **آفلاین** اجرا می‌شوند: فقط از دیتاست‌های همراه scikit-learn یا داده ساختگی/مصنوعی استفاده می‌شود و به دانلود اینترنتی نیاز نیست.

## نحوه اجرا

- اسکریپت‌ها:

```bash
python code/session_05_bfs_dfs.py
```

- نوت‌بوک‌ها (`ipynb`): در Google Colab باز کنید (**File > Upload notebook**) یا به‌صورت محلی با Jupyter اجرا کنید.

> [!TIP]
> در Google Colab این کتابخانه‌ها از قبل نصب‌اند و نیازی به `pip install` نیست.

## نقشه کد جلسات

| جلسه | فایل | موضوع |
|:-:|---|--:|
| 5 | `session_05_bfs_dfs.py` | جست‌وجوی BFS و DFS روی گراف شبکه بیمارستانی/ماز |
| 6 | `session_06_uninformed_search_ucs_ids.py` | UCS و IDDFS؛ مقایسه هزینه و شمار گره |
| 7 | `session_07_informed_heuristics.py` | جست‌وجوی آگاهانه؛ هیوریستیک مجاز و مقایسه توابع h |
| 8 | `session_08_a_star.py` | الگوریتم A* روی شبکه؛ بررسی مجاز بودن هیوریستیک و بهینگی |
| 9 | `session_09_search_workshop.ipynb` و `session_09_search_workshop.py` | کارگاه: مقایسه BFS، DFS، UCS و A* |
| 10 | `session_10_local_search_genetic.py` | جست‌وجوی محلی: Hill Climbing، Simulated Annealing و الگوریتم ژنتیک |
| 11 | `session_11_gradient_descent.py` | گرادیان کاهشی و نسخه‌های آن روی تابع برازش |
| 12 | `session_12_csp_backtracking.py` | CSP با Backtracking، FC و MRV روی مسئله نگهبانی/تخصیص |
| 13 | `session_13_csp_scheduling.py` | زمان‌بندی شیفت پرستاری با CSP |
| 14 | `session_14_solutions.py` | راه‌حل‌های کد حل تمرین ۱ |
| 15 | `session_15_minimax_alphabeta.py` | Minimax و هرس آلفا–بتا روی Tic-Tac-Toe با شمارش گره |
| 17 | `session_17_logic_expert_system.py` | استنتاج روبه‌جلو و موتور قاعده ساده پزشکی |
| 18 | `session_18_mdp_value_iteration.py` | Value Iteration و Policy Iteration روی MDP مینی‌پزشکی |
| 19 | `session_19_q_learning.py` | Q-learning جدولی روی محیط شبکه‌ای |
| 20 | `session_20_bayes_markov.py` | استنتاج بیزین ساده و مدل مارکوف/HMM |
| 21 | `session_21_ml_metrics.py` | دقت، حساسیت، ویژگی، ROC و ماتریس درهم‌ریختگی |
| 22 | `session_22_sklearn_workshop.ipynb` و `session_22_sklearn_workshop.py` | کارگاه یادگیری ماشین با scikit-learn (دیتاست سرطان سینه) |
| 23 | `session_23_solutions.py` | راه‌حل‌های کد حل تمرین ۲ |
| 24 | `session_24_nn_from_scratch.py` | پیاده‌سازی از صفر پرسپترون و MLP برای XOR، بدون وابستگی خارجی |
| 25 | `session_25_biosignal_bci.py` | سیگنال ECG مصنوعی، استخراج ویژگی و طبقه‌بندی |
| 26 | `session_26_medical_imaging.py` | تصویربرداری مصنوعی و طبقه‌بند نزدیک‌ترین مرکز روی داده مصنوعی |
| 27 | `session_27_ethics_fairness.py` | نمونه سوگیری و انصاف، و اعتبارسنجی مدل |

## یادآوری ایمنی

همه کدها و دیتاست‌های این پوشه **آموزشی و غیرتشخیصی** هستند. هیچ خروجی‌ای از این کدها نباید برای تصمیم‌گیری درباره بیمار واقعی به کار رود.
