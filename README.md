# مقدمه‌ای بر هوش مصنوعی و کاربرد آن در مهندسی پزشکی

درس ۲۹ جلسه‌ای برای مقطع کارشناسی مهندسی پزشکی: از مبانی هوش مصنوعی و عامل‌های هوشمند تا یادگیری ماشین، یادگیری عمیق و کاربردهای زیست‌پزشکی — همراه با کدهای آموزشی و پروژه گروهی.

## ساختار مخزن

<div dir="rtl">

| مسیر | محتوا |
|--:|--:|
| `session_01_*.md` تا `session_29_*.md` | فایل جلسات (محتوای درس + تکالیف) |
| `code/` | کدهای آموزشی؛ راهنما: `code/README.md`، وابستگی‌ها: `code/requirements.txt` |
| `project/project-brief.md` | سند پیشنهادی پروژه گروهی + ارزیابی + وزن نمره |
| `code/python_selfstudy.ipynb` | نوت‌بوک خودآموز پایتون (تکلیف آمادگی جلسه ۴) |

</div>

## فهرست جلسات

<div dir="rtl">

| جلسه | موضوع | عنوان | فایل |
|--:|--:|--:|:--|
| ۱ | مبانی و آمادگی | معرفی درس و آشنایی با هوش مصنوعی | [session_01_intro_to_ai.md](session_01_intro_to_ai.md) |
| ۲ | مبانی و آمادگی | عامل‌های هوشمند و محیط؛ آشنایی مقدماتی با LLM | [session_02_agents_and_llm.md](session_02_agents_and_llm.md) |
| ۳ | مبانی و آمادگی | داده‌های زیستی و سلامت؛ Big Data و Generative AI | [session_03_health_data_and_genai.md](session_03_health_data_and_genai.md) |
| ۴ | مبانی و آمادگی | کارگاه مقدماتی پایتون و داده | [session_04_python_workshop.md](session_04_python_workshop.md) |
| ۵ | جست‌وجو و حل مسئله | صورت‌بندی مسئله جست‌وجو؛ BFS و DFS | [session_05_search_bfs_dfs.md](session_05_search_bfs_dfs.md) |
| ۶ | جست‌وجو و حل مسئله | روش‌های دیگر جست‌وجوی ناآگاهانه؛ ID و UCS | [session_06_uninformed_search_ucs_ids.md](session_06_uninformed_search_ucs_ids.md) |
| ۷ | جست‌وجو و حل مسئله | جست‌وجوی آگاهانه و توابع ابتکاری | [session_07_informed_heuristics.md](session_07_informed_heuristics.md) |
| ۸ | جست‌وجو و حل مسئله | الگوریتم A* | [session_08_a_star.md](session_08_a_star.md) |
| ۹ | جست‌وجو و حل مسئله | کارگاه پیاده‌سازی الگوریتم‌های جست‌وجو | [session_09_search_workshop.md](session_09_search_workshop.md) |
| ۱۰ | بهینه‌سازی و قیود | جست‌وجوی محلی و الگوریتم ژنتیک | [session_10_local_search_genetic.md](session_10_local_search_genetic.md) |
| ۱۱ | بهینه‌سازی و قیود | جست‌وجو در فضای پیوسته و گرادیان کاهشی | [session_11_continuous_gradient_descent.md](session_11_continuous_gradient_descent.md) |
| ۱۲ | بهینه‌سازی و قیود | مسائل ارضای محدودیت (CSP) | [session_12_csp.md](session_12_csp.md) |
| ۱۳ | بهینه‌سازی و قیود | حل CSP و مسئله زمان‌بندی | [session_13_csp_scheduling.md](session_13_csp_scheduling.md) |
| ۱۴ | بهینه‌سازی و قیود | حل تمرین ۱: جست‌وجو، A*، بهینه‌سازی و CSP | [session_14_problem_solving_1.md](session_14_problem_solving_1.md) |
| ۱۵ | تصمیم مقابله‌ای و میان‌ترم ۱ | جست‌وجوی مقابله‌ای؛ Minimax و هرس آلفا–بتا | [session_15_adversarial_minimax.md](session_15_adversarial_minimax.md) |
| ۱۶ | تصمیم مقابله‌ای و میان‌ترم ۱ | میان‌ترم اول (پوشش ۱ تا ۱۵) | [session_16_midterm_1.md](session_16_midterm_1.md) |
| ۱۷ | منطق و تصمیم زیر عدم قطعیت | منطق گزاره‌ای و مرتبه اول؛ سیستم‌های خبره | [session_17_logic_expert_systems.md](session_17_logic_expert_systems.md) |
| ۱۸ | منطق و تصمیم زیر عدم قطعیت | فرایند تصمیم مارکوف (MDP) | [session_18_mdp.md](session_18_mdp.md) |
| ۱۹ | منطق و تصمیم زیر عدم قطعیت | یادگیری تقویتی و Q-learning | [session_19_reinforcement_learning.md](session_19_reinforcement_learning.md) |
| ۲۰ | منطق و تصمیم زیر عدم قطعیت | شبکه‌های بیزین و مدل‌های مارکوف | [session_20_bayesian_markov.md](session_20_bayesian_markov.md) |
| ۲۱ | یادگیری ماشین | مبانی یادگیری ماشین و ارزیابی مدل | [session_21_ml_basics_evaluation.md](session_21_ml_basics_evaluation.md) |
| ۲۲ | یادگیری ماشین | کارگاه یادگیری ماشین با scikit-learn | [session_22_sklearn_workshop.md](session_22_sklearn_workshop.md) |
| ۲۳ | یادگیری ماشین | حل تمرین ۲: منطق، MDP، مدل‌های احتمالاتی و ML | [session_23_problem_solving_2.md](session_23_problem_solving_2.md) |
| ۲۴ | یادگیری عمیق و کاربردهای پزشکی | شبکه‌های عصبی و یادگیری عمیق | [session_24_neural_networks_deep_learning.md](session_24_neural_networks_deep_learning.md) |
| ۲۵ | یادگیری عمیق و کاربردهای پزشکی | هوش مصنوعی در سیگنال‌های زیستی و BCI | [session_25_ai_biosignals_bci.md](session_25_ai_biosignals_bci.md) |
| ۲۶ | یادگیری عمیق و کاربردهای پزشکی | هوش مصنوعی در تصاویر پزشکی | [session_26_ai_medical_imaging.md](session_26_ai_medical_imaging.md) |
| ۲۷ | یادگیری عمیق و کاربردهای پزشکی | سایر کاربردهای AI در مهندسی پزشکی؛ اخلاق و اعتبارسنجی | [session_27_ai_bme_ethics_validation.md](session_27_ai_bme_ethics_validation.md) |
| ۲۸ | جمع‌بندی و پروژه | میان‌ترم دوم / ارزیابی میان‌دوره‌ای دوم (پوشش جلسات ۱۷ تا ۲۶) | [session_28_midterm_2.md](session_28_midterm_2.md) |
| ۲۹ | جمع‌بندی و پروژه | آینده هوش مصنوعی در پزشکی و ارائه پروژه‌ها | [session_29_future_of_ai_medicine.md](session_29_future_of_ai_medicine.md) |

</div>

> [!IMPORTANT]
> هر ۲۹ فایل جلسه آماده و از جدول بالا پیوند شده‌اند.

## پروژه و نمره‌دهی

- شرح پروژه گروهی، جدول زمانی، ارزیابی صد نمره‌ای و وزن‌های پیشنهادی نمره درس: [project/project-brief.md](project/project-brief.md)
- موضوع پروژه در جلسه ۱ اعلام و در جلسه ۵ گروه‌ها تشکیل می‌شوند؛ ارائه نهایی در جلسه ۲۹.
- کدهای آموزشی هر جلسه در پوشه [`code/`](code) قرار می‌گیرند؛ نقشه کامل کد در `code/README.md` آمده است.

## راهنمای زمان‌بندی ۶۰/۹۰ دقیقه

- هر فایل جلسه برای جلسه‌ای با سقف ۹۰ دقیقه نوشته شده و یک برنامه فشرده ۶۰ دقیقه‌ای هم دارد؛
- اگر کلاس فقط ۶۰ دقیقه است، فعالیت‌های گروهی را کوتاه و بخش‌های اختیاری را به تکلیف منتقل می‌کنیم؛
- برای جلسه ۴، پیش‌نیاز خودآموز پایتون مهم است. اگر دانشجویان واقعاً هیچ آشنایی ندارند، کارگاه NumPy/Pandas را برگزار می‌کنیم.

## منابع درس

فهرست ۱۱ منبع (کتاب، مقاله و محتوای مدرس)

<div dir="rtl">

| شماره منبع | منبع و سال انتشار                                            | نویسنده یا نویسندگان                         |
| :--------: | :----------------------------------------------------------- | :------------------------------------------- |
|     ۱      | Artificial Intelligence: A Modern Approach (2016)            | Stuart J. Russell؛ Peter Norvig              |
|     ۲      | Artificial Intelligence in Medicine: Technical Basis and Clinical Applications (2021) | Bradley J. Erickson                          |
|     ۳      | Advances in Artificial Intelligence, Computation, and Data Science (2021) | T. D. Pham؛ H. Yan؛ M. W. Ashraf؛ F. Sjöberg |
|     ۴      | Medical Robotics and AI-Assisted Diagnostics for a High-Tech Healthcare Industry (2024) | A. Khang                                     |
|     ۵      | Artificial Intelligence in Tissue and Organ Regeneration (2023) | C. P. Sharma؛ T. Chandy؛ V. Thomas           |
|     ۶      | AI and IoT-Based Technologies for Precision Medicine (2023)  | A. Khang                                     |
|     ۷      | Application of Artificial Intelligence in Tissue Engineering (2024) | R. Bagherpour؛ G. Bagherpour؛ P. Mohamadi    |
|     ۸      | Machine Learning in Tissue Engineering (2023)                | J. L. Guo؛ M. Januszyk؛ M. T. Longaker       |
|     ۹      | Artificial Intelligence in Biomedical Engineering and Informatics: An Introduction and Review (2010) | Y. Peng؛ Y. Zhang؛ L. Wang                   |
|     ۱۰     | Python Machine Learning by Example (2017)                    | Y. H. Liu                                    |
|     ۱۱     | محتوای تولید شده توسط مدرس (2026)                            | سعید محققی                                   |

</div>

ارجاع هر جلسه در خط «منابع این جلسه» ابتدای همان فایل آمده است.

## یادآوری ایمنی

همه مثال‌ها، دیتاست‌ها و کدهای این درس **آموزشی و غیرتشخیصی** هستند و نباید برای تصمیم‌گیری بالینی درباره بیمار واقعی به کار روند.

## وب‌سایت درس و توسعه محلی

وب‌سایت ایستای فارسی درس در مخزن مستقل [DaneshJoy/ai_bme_intro](https://github.com/DaneshJoy/ai_bme_intro) نگه‌داری می‌شود؛ فایل‌های کد و نوت‌بوک از [فهرست کدها](https://github.com/DaneshJoy/ai_bme_intro/tree/main/code) و پیوندهای هر جلسه مستقیماً در GitHub قابل مشاهده‌اند. آدرس مورد انتظار سایت پس از پیکربندی انتشار: [daneshjoy.github.io/ai_bme_intro](https://daneshjoy.github.io/ai_bme_intro/).

برای اجرای محلی به Node.js نسخهٔ ۲۴ نیاز دارید:

```sh
npm ci
npm run dev
```

پیش از تغییرات و انتشار، `npm run check` را اجرا کنید؛ این فرمان اعتبارسنجی، ساخت و آزمون‌ها را اجرا می‌کند. فایل‌های `session_*.md`، `code/` و `course.json` منابع دست‌نویس‌اند. پوشه‌های `generated/` و `dist/` خروجی تولیدشده و نادیده‌گرفته‌شده هستند؛ آن‌ها را دستی ویرایش نکنید.

**مرز انتشار دانشجویی:** جلسه‌های ۱ تا ۵ تأیید شده‌اند که فقط محتوای دانشجویی دارند. در جلسه‌های ۶ تا ۲۹، سایت فقط محتوای پیش از نشانگر دقیق راهنمای مدرس را می‌سازد؛ نشانگر ناموجود یا مبهم باید ساخت را متوقف کند. راهنمای مدرس، پاسخ‌ها و اسناد پروژه نباید در سایت دانشجویی منتشر شوند. جزئیات مالکیت فایل‌ها و قواعد فارسی/RTL در [`AGENTS.md`](AGENTS.md) آمده است.

برای فعال‌کردن انتشار در GitHub، مالک مخزن باید در **Settings → Pages → Build and deployment**، گزینهٔ **Source: GitHub Actions** را انتخاب کند. گردش‌کار [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) با push به `main` یا اجرای دستی، بررسی‌ها را انجام می‌دهد و `dist/` را به GitHub Pages می‌فرستد. این مستندات به‌تنهایی به معنی فعال‌بودن Pages یا انتشار موفق سایت نیست.
