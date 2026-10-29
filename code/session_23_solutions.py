# -*- coding: utf-8 -*-
"""جلسه ۲۳ — جلسه حل تمرین ۲: راه‌حل‌های مرجع

چهار گروه تمرینِ جلسه ۲۳ (منطق، MDP، مدل‌های احتمالاتی، متریک‌های ML) در این
فایل پیاده‌سازی و اجرا می‌شود:

  تمرین ۱ — منطق: استنتاج روبه‌جلو (Forward Chaining) روی پایگاه قاعده‌ی جدید
  تمرین ۲ — منطق: درستی استدلال Modus Tollens با جدول درستی
  تمرین ۳ — MDP: یک مرور بلمن دستی و تکرار ارزش کامل با γ = 0.5
  تمرین ۴ — MDP: مقایسه γ = 0.9 با γ = 0.5 (همان مدل مینی‌پزشکی جلسه ۱۸)
  تمرین ۵ — قاعده‌ی بیز با کسر دقیق (Fraction) و بیز زنجیره‌ای (دو آزمون)
  تمرین ۶ — زنجیره‌ی مارکوف: توزیع گام‌به‌گام و توزیع مانا
  تمرین ۷ — متریک‌های ML: ماتریس درهم‌ریختگی و شش متریک (پیاده‌سازی مستقل)
  تمرین ۸ — نمونه‌سؤال شبیه میان‌ترم دوم: ترکیب هر چهار گروه

در پایان خودآزمون‌های assert اجرا می‌شود؛ مقادیر مورد انتظارِ MDP با حل دقیق
دستگاه خطیِ دومعادله‌دومجهول (با Fraction) از خود پارامترها ساخته می‌شود، پس
تغییر γ در تمرین‌های خودآزمایی اجرا را نمی‌شکند. اگر همه‌چیز درست باشد، پیام
«ALL CHECKS PASSED» چاپ می‌شود.

نکته تکرارپذیری: هیچ تصادفی در این اسکریپت نیست؛ بیز و مارکوف با کسر دقیق و
تکرار ارزش با اعداد اعشاری قطعی محاسبه می‌شوند.

فقط از کتابخانه استاندارد پایتون استفاده می‌شود.
کد آموزشی است و هیچ کاربرد تشخیصی یا بالینی ندارد.
"""

from fractions import Fraction

# ---------------- تمرین ۱: استنتاج روبه‌جلو ----------------
# اتم‌های لاتین:  F = تب ، C = سرفه ، I = عفونت تنفسی محتمل ،
# O = سن بالاتر از ۶۵ ، S = اشباع اکسیژن پایین ، D = درد هنگام تنفس ،
# R = ارجاع برای بررسی بیشتر ، Q = اولویت ویزیت فوری
RULES_T1 = [
    ("R1", frozenset({"F", "C"}), "I"),
    ("R2", frozenset({"I", "O"}), "R"),
    ("R3", frozenset({"I", "S"}), "R"),
    ("R4", frozenset({"R"}), "Q"),
    ("R5", frozenset({"D"}), "I"),
]
FACTS_T1 = ("F", "C", "O")


def forward_chain(rules, facts):
    """استنتاج روبه‌جلو: تا وقتی قاعده‌ای نتیجه‌ی تازه بسازد، حل می‌زنیم.

    ترتیب بررسی قاعده‌ها ثابت است؛ پس خروجی همیشه قطعی است.
    خروجی: (مجموعه‌ی نهایی حقایق، فهرست گام‌های اثبات)
    """
    known = set(facts)
    steps = []
    changed = True
    while changed:
        changed = False
        for name, premises, conclusion in rules:
            if conclusion in known:
                continue
            if premises <= known:
                known.add(conclusion)
                steps.append((name, sorted(premises), conclusion))
                changed = True
    return known, steps


def blocked_rules(rules, known, fired_names):
    """قاعده‌های فعال‌نشده و پیش‌فرض گم‌شده‌ی هرکدام.

    نکته: ممکن است نتیجه‌ی یک قاعده از مسیر قاعده‌ی دیگری به دست آمده باشد؛
    در هر صورت اگر قاعده خودش فعال نشده، علت را از پیش‌فرض‌های گم‌شده می‌گیریم.
    """
    out = []
    for name, premises, conclusion in rules:
        if name not in fired_names:
            out.append((name, sorted(premises - known)))
    return out


# ---------------- تمرین ۲: Modus Tollens با جدول درستی ----------------

def modus_tollens_table():
    """پیش‌فرض‌های I→R و ¬R و نتیجه‌ی ¬I را روی هر چهار ردیف می‌سنجد."""
    rows = []
    for i in (False, True):
        for r in (False, True):
            p1 = (not i) or r        # I → R
            p2 = (not r)             # ¬R
            concl = (not i)          # ¬I
            rows.append((i, r, p1, p2, concl))
    satisfying = [row for row in rows if row[2] and row[3]]
    valid = all(row[4] for row in satisfying)
    return rows, satisfying, valid


# ---------------- تمرین ۳ و ۴: MDP — همان مدل مینی‌پزشکی جلسه ۱۸ ----------------
# حالت‌ها: s1 = پایدار ، s2 = بدحال ، s3 = بهبود (پایانی)
# کنش‌ها : a1 = پایش ، a2 = بستری پیشگیرانه ، a3 = درمان مضاعف

STATES = ("s1", "s2", "s3")
GAMMA_T3 = 0.5   # تمرین ۳: افق کوتاه
GAMMA_T4 = 0.9   # تمرین ۴: بازگشت به مدل جلسه ۱۸ (تکلیف: مقدار را تغییر دهید)
TERMINAL = {"s3"}
STEP_COST = {"a1": 1.0, "a2": 6.0, "a3": 5.0}
RECOVERY_REWARD = 10.0

ACTIONS = {"s1": ("a1", "a2"), "s2": ("a1", "a3"), "s3": ()}

TRANSITIONS = {
    ("s1", "a1"): {"s1": 0.9, "s2": 0.05, "s3": 0.05},
    ("s1", "a2"): {"s1": 0.8, "s2": 0.1, "s3": 0.1},
    ("s2", "a1"): {"s1": 0.1, "s2": 0.9, "s3": 0.0},
    ("s2", "a3"): {"s1": 0.4, "s2": 0.3, "s3": 0.3},
}


def reward(s, a, s2):
    """پاداش گذار: منفی هزینه‌ی کنش + پاداش بهبودی در گذار به s3."""
    r = -STEP_COST[a]
    if s2 == "s3":
        r += RECOVERY_REWARD
    return r


def q_value(state, action, v, gamma):
    """Q(s, a) با تابع ارزش فعلی: Σ_s' P(s'|s,a) × [R + γ·V(s')]."""
    total = 0.0
    for s2, p in TRANSITIONS[(state, action)].items():
        total += p * (reward(state, action, s2) + gamma * v[s2])
    return total


def value_iteration(gamma, theta=1e-10, max_iter=10000):
    """تکرار ارزش: تکرار عملگر بلمن تا همگرایی؛ سپس استخراج سیاست."""
    v = {s: 0.0 for s in STATES}
    sweeps = 0
    for _ in range(max_iter):
        delta = 0.0
        new_v = {}
        for s in STATES:
            if s in TERMINAL or not ACTIONS[s]:
                new_v[s] = 0.0
                continue
            new_v[s] = max(q_value(s, a, v, gamma) for a in ACTIONS[s])
            delta = max(delta, abs(new_v[s] - v[s]))
        v = new_v
        sweeps += 1
        if delta < theta:
            break
    pi = {s: None for s in STATES}
    for s in STATES:
        if s in TERMINAL or not ACTIONS[s]:
            continue
        pi[s] = max((q_value(s, a, v, gamma), a) for a in ACTIONS[s])[1]
    return v, pi, sweeps


def bellman_sweep_hand(gamma):
    """اولین مرور بلمن با V0 = 0 (همان محاسبه‌ی دستی تمرین ۳)."""
    v0 = {s: 0.0 for s in STATES}
    qs = {}
    for s in ("s1", "s2"):
        for a in ACTIONS[s]:
            qs[(s, a)] = q_value(s, a, v0, gamma)
    v1 = {s: max(q_value(s, a, v0, gamma) for a in ACTIONS[s]) for s in ("s1", "s2")}
    return qs, v1


def exact_policy_values(pi, gamma):
    """حل دقیق دستگاه خطی V = c + A·V برای یک سیاست مشخص (با Fraction).

    برای هر حالت غیرپایانی: V(s) = Σ_s' P(s'|s,π(s))·[R(s,π(s),s') + γ·V(s')]
    دستگاه ۲×۲ با قاعده‌ی کرمر حل می‌شود؛ خروجی مقادیر دقیق V برای s1 و s2.
    """
    g = Fraction(str(gamma))
    frac = {}
    for key, tr in TRANSITIONS.items():
        frac[key] = {s2: Fraction(str(p)) for s2, p in tr.items()}

    def coef(s):
        a = pi[s]
        row = {}
        const = Fraction(0)
        for s2, p in frac[(s, a)].items():
            r = -Fraction(str(STEP_COST[a]))
            if s2 == "s3":
                r += Fraction(str(RECOVERY_REWARD))
            if s2 in TERMINAL:
                const += p * r
            else:
                row[s2] = row.get(s2, Fraction(0)) + p
                const += p * r
        return row, const

    (row1, c1), (row2, c2) = coef("s1"), coef("s2")
    a11, a12 = row1.get("s1", Fraction(0)) * g, row1.get("s2", Fraction(0)) * g
    a21, a22 = row2.get("s1", Fraction(0)) * g, row2.get("s2", Fraction(0)) * g
    det = (1 - a11) * (1 - a22) - a12 * a21
    v1 = (c1 * (1 - a22) + a12 * c2) / det
    v2 = (c2 * (1 - a11) + a21 * c1) / det
    return v1, v2


# ---------------- تمرین ۵: قاعده‌ی بیز با کسر دقیق ----------------

PRIOR = Fraction(4, 100)     # P(D): شیوع بیماری در جامعه (۴٪)
SENS = Fraction(19, 20)      # P(+ | D): حساسیت آزمون
FPR = Fraction(1, 20)        # P(+ | ¬D): نرخ مثبت کاذب (ویژگی = 19/20)


def bayes_update(prior):
    """یک گام بیز: P(D|+) = P(+|D)·P(D) / P(+) با کسر دقیق."""
    p_pos = SENS * prior + FPR * (1 - prior)
    posterior = (SENS * prior) / p_pos
    return p_pos, posterior


# ---------------- تمرین ۶: زنجیره‌ی مارکوف ----------------
# حالت‌ها: OK = سالم ، BAD = در حال خرابی (همان روایت دستگاه آزمایشگاهی جلسه ۲۰)

MARKOV_T = [[Fraction(4, 5), Fraction(1, 5)],    # از OK به [OK, BAD]
            [Fraction(2, 5), Fraction(3, 5)]]    # از BAD به [OK, BAD]
MARKOV_START = (Fraction(1), Fraction(0))        # شروع: قطعاً سالم


def markov_step(dist):
    """یک گام زنجیره: dist ← dist · T (ضرب بردار در ماتریس انتقال)."""
    return [sum(dist[i] * MARKOV_T[i][j] for i in range(2)) for j in range(2)]


def markov_run(steps=(1, 2, 3, 10), n_stationary=60):
    """توزیع گام‌به‌گام و توزیع مانا (تکرار ۶۰ گام)."""
    dist = MARKOV_START
    snapshots = {}
    for t in range(1, max(max(steps), n_stationary) + 1):
        dist = markov_step(dist)
        if t in steps:
            snapshots[t] = tuple(dist)
    return snapshots, tuple(dist)


# ---------------- تمرین ۷: متریک‌های ML (پیاده‌سازی مستقل) ----------------
# ماتریس درهم‌ریختگی تمرین ۷ (اعداد ساختگی و آموزشی)

CM_T7 = {"tp": 25, "fn": 5, "fp": 10, "tn": 60}


def metrics_fraction(tp, fn, fp, tn):
    """شش متریک با کسر دقیق — بازپیاده‌سازی مستقلِ کمک‌تابع‌های جلسه ۲۱."""
    def div(a, b):
        return Fraction(a, b) if b else None

    acc = div(tp + tn, tp + fn + fp + tn)
    sens = div(tp, tp + fn)
    spec = div(tn, tn + fp)
    ppv = div(tp, tp + fp)
    npv = div(tn, tn + fn)
    f1 = None
    if ppv is not None and sens is not None and (ppv + sens):
        f1 = Fraction(2) * ppv * sens / (ppv + sens)
    return {"acc": acc, "sens": sens, "spec": spec, "ppv": ppv, "npv": npv, "f1": f1}


# ---------------- خودآزمون‌ها و اجرا ----------------

def run_exercises():
    """اجرای هر هشت تمرین و چاپ نتایج؛ خروجی: دیکشنری نتایج برای خودآزمایی."""
    results = {}

    print("[تمرین ۱ — منطق: استنتاج روبه‌جلو]")
    known, steps = forward_chain(RULES_T1, FACTS_T1)
    for k, (name, premises, concl) in enumerate(steps, 1):
        print("  گام %d | %s فعال شد: {%s} => %s"
              % (k, name, " ، ".join(premises), concl))
    print("  حافظه کاری نهایی: %s" % " ، ".join(sorted(known)))
    blocked = blocked_rules(RULES_T1, known, {s[0] for s in steps})
    print("  قاعده‌های مسدود: " + " ، ".join(
        "%s (پیش‌فرض %s موجود نیست)" % (name, " و ".join(missing))
        for name, missing in blocked))
    results["t1"] = (known, steps, blocked)
    print()

    print("[تمرین ۲ — منطق: آزمون Modus Tollens]")
    print("  پیش‌فرض‌ها: I→R و ¬R ؛ نتیجه‌ی ادعایی: ¬I")
    rows, satisfying, valid = modus_tollens_table()
    for i, r, p1, p2, concl in rows:
        mark = "*" if (p1 and p2) else " "
        print("  %s I=%-5s R=%-5s | I→R=%-5s ¬R=%-5s | ¬I=%-5s"
              % (mark, i, r, p1, p2, concl))
    print("  ردیف‌های برقرارکننده‌ی هر دو پیش‌فرض: %d از %d" % (len(satisfying), len(rows)))
    print("  نتیجه: %s" % ("استدلال معتبر است (Modus Tollens)" if valid
                           else "استدلال معتبر نیست"))
    results["t2"] = (rows, satisfying, valid)
    print()

    print("[تمرین ۳ — MDP: مرور دستی + تکرار ارزش با γ = %s]" % GAMMA_T3)
    qs, v1 = bellman_sweep_hand(GAMMA_T3)
    print("  مرور اول با V0 = 0 (دستی):")
    for (s, a), q in sorted(qs.items()):
        print("    Q(%s, %s) = %+.4f" % (s, a, q))
    print("    V1(s1) = %+.4f | V1(s2) = %+.4f" % (v1["s1"], v1["s2"]))
    v05, pi05, sweeps05 = value_iteration(GAMMA_T3)
    print("  تکرار ارزش کامل: همگرا پس از %d مرور" % sweeps05)
    print("    V*(s1) = %+.4f | V*(s2) = %+.4f" % (v05["s1"], v05["s2"]))
    ex1, ex2 = exact_policy_values(pi05, GAMMA_T3)
    print("    حل دقیق سیاست: V*(s1) = %s = %.4f | V*(s2) = %s = %.4f"
          % (ex1, float(ex1), ex2, float(ex2)))
    print("    π*: از s1 → %s | از s2 → %s" % (pi05["s1"], pi05["s2"]))
    results["t3"] = (qs, v1, v05, pi05, sweeps05, (ex1, ex2))
    print()

    print("[تمرین ۴ — MDP: مقایسه γ = %s با γ = %s]" % (GAMMA_T4, GAMMA_T3))
    v09, pi09, sweeps09 = value_iteration(GAMMA_T4)
    ex1b, ex2b = exact_policy_values(pi09, GAMMA_T4)
    print("  γ = 0.9 : همگرا پس از %d مرور | V*(s1) = %s = %.4f | V*(s2) = %s = %.4f"
          % (sweeps09, ex1b, float(ex1b), ex2b, float(ex2b)))
    print("            π*: از s1 → %s | از s2 → %s" % (pi09["s1"], pi09["s2"]))
    print("  γ = %s : همگرا پس از %d مرور | π*: (%s، %s)"
          % (GAMMA_T3, sweeps05, pi05["s1"], pi05["s2"]))
    print("  درس: γ کوچک‌تر افق دید را کوتاه می‌کند و همگرایی را سریع‌تر.")
    results["t4"] = (v09, pi09, sweeps09, (ex1b, ex2b))
    print()

    print("[تمرین ۵ — قاعده‌ی بیز با کسر دقیق]")
    print("  P(D)=%s | P(+|D)=%s | P(+|سالم)=%s" % (PRIOR, SENS, FPR))
    p_pos1, post1 = bayes_update(PRIOR)
    print("  P(+) = %s = %.4f" % (p_pos1, float(p_pos1)))
    print("  پسین بعد از یک آزمون مثبت: P(D|+) = %s = %.4f" % (post1, float(post1)))
    p_pos2, post2 = bayes_update(post1)
    print("  بعد از آزمون دوم مستقل: P(+) = %s = %.4f | P(D|++) = %s = %.4f"
          % (p_pos2, float(p_pos2), post2, float(post2)))
    results["t5"] = (p_pos1, post1, post2)
    print()

    print("[تمرین ۶ — زنجیره‌ی مارکوف]")
    snapshots, stationary = markov_run()
    print("  ماتریس انتقال: OK→[4/5، 1/5] | BAD→[2/5، 3/5] | شروع: قطعاً OK")
    for t, dist in sorted(snapshots.items()):
        print("  گام %2d: P(OK)=%.4f  P(BAD)=%.4f" % (t, float(dist[0]), float(dist[1])))
    print("  توزیع مانا (تکرار ۶۰ گام): P(OK)=%.4f  P(BAD)=%.4f"
          % (float(stationary[0]), float(stationary[1])))
    print("  فرمول بسته: P(OK) = t(BAD→OK)/(t(OK→BAD)+t(BAD→OK)) = 2/3")
    results["t6"] = (snapshots, stationary)
    print()

    print("[تمرین ۷ — متریک‌های ML]")
    m = metrics_fraction(**CM_T7)
    print("  TP=%d ، FN=%d ، FP=%d ، TN=%d" % (CM_T7["tp"], CM_T7["fn"], CM_T7["fp"], CM_T7["tn"]))
    for key, label in (("acc", "Accuracy"), ("sens", "Sensitivity"),
                       ("spec", "Specificity"), ("ppv", "PPV"),
                       ("npv", "NPV"), ("f1", "F1")):
        print("  %-12s = %s = %.4f" % (label, m[key], float(m[key])))
    results["t7"] = m
    print()

    print("[تمرین ۸ — نمونه‌سؤال شبیه میان‌ترم دوم]")
    _, steps8 = results["t1"][0], results["t1"][1]
    print("  الف (منطق): قاعده‌های فعال‌شده به‌ترتیب = %s | طول زنجیره = %d گام"
          % (" ، ".join(name for name, _, _ in steps8), len(steps8)))
    print("  ب (MDP): Q(s2, a3) در مرور اول با γ = 0.5 = %+.4f | V1(s2) = %+.4f"
          % (qs[("s2", "a3")], v1["s2"]))
    print("  ج (بیز): پسین بعد از یک آزمون مثبت = %s = %.4f" % (post1, float(post1)))
    print("  د (متریک): F1 = %s = %.4f" % (m["f1"], float(m["f1"])))
    results["t8"] = (steps8, qs, v1, post1, m)
    print()
    return results


def run_self_checks(res):
    """خودآزمایی با assert — انتظارها یا ساختاری‌اند یا از خود پارامترها."""

    # تمرین ۱: زنجیره‌ی کامل و قاعده‌های مسدود
    known, steps, blocked = res["t1"]
    assert known == {"F", "C", "O", "I", "R", "Q"}, "حافظه کاری نهایی نادرست است"
    assert [s[0] for s in steps] == ["R1", "R2", "R4"], "ترتیب فعال‌سازی نادرست است"
    assert blocked == [("R3", ["S"]), ("R5", ["D"])], "قاعده‌های مسدود نادرست است"
    print("خودآزمایی تمرین ۱: OK — زنجیره R1→R2→R4 و دو قاعده‌ی مسدود تأیید شد")

    # تمرین ۲: معتبر بودن Modus Tollens
    rows, satisfying, valid = res["t2"]
    assert valid, "Modus Tollens باید معتبر باشد"
    assert len(satisfying) == 1 and satisfying[0][0] is False and satisfying[0][1] is False, \
        "تنها ردیف برقرارکننده باید I=False و R=False باشد"
    print("خودآزمایی تمرین ۲: OK — استدلال معتبر است (تنها ردیف برقرارکننده بررسی شد)")

    # تمرین ۳: γ = 0.5 — مرور دستی و مقادیر دقیق سیاست بهینه
    qs, v1, v05, pi05, sweeps05, exact05 = res["t3"]
    assert abs(qs[("s1", "a1")] - (-0.5)) < 1e-9, "Q(s1,a1) مرور اول باید -0.5 باشد"
    assert abs(qs[("s1", "a2")] - (-5.0)) < 1e-9, "Q(s1,a2) مرور اول باید -5.0 باشد"
    assert abs(qs[("s2", "a1")] - (-1.0)) < 1e-9, "Q(s2,a1) مرور اول باید -1.0 باشد"
    assert abs(qs[("s2", "a3")] - (-2.0)) < 1e-9, "Q(s2,a3) مرور اول باید -2.0 باشد"
    assert abs(v1["s1"] - (-0.5)) < 1e-9 and abs(v1["s2"] - (-1.0)) < 1e-9, \
        "V1 باید (-0.5، -1.0) باشد"
    # مقادیر دقیق از حل کرمرِ خود پارامترها (نه عدد هاردکد)
    assert abs(v05["s1"] - float(exact05[0])) < 1e-6, "V*(s1) با حل دقیق نمی‌خواند"
    assert abs(v05["s2"] - float(exact05[1])) < 1e-6, "V*(s2) با حل دقیق نمی‌خواند"
    assert pi05["s1"] == "a1" and pi05["s2"] == "a1", \
        "با γ=0.5 سیاست بهینه در هر دو حالت باید a1 (پایش) باشد"
    print("خودآزمایی تمرین ۳: OK — مرور دستی و V*/π* با حل دقیق کرمر تأیید شد")

    # تمرین ۴: γ = 0.9 — بازگشت به سیاست جلسه ۱۸ و مقایسه‌ی مرورها
    v09, pi09, sweeps09, exact09 = res["t4"]
    assert abs(v09["s1"] - float(exact09[0])) < 1e-6, "V*(s1) با حل دقیق نمی‌خواند"
    assert abs(v09["s2"] - float(exact09[1])) < 1e-6, "V*(s2) با حل دقیق نمی‌خواند"
    assert pi09["s1"] == "a1" and pi09["s2"] == "a3", \
        "با γ=0.9 سیاست بهینه باید (a1، a3) باشد"
    assert sweeps09 > sweeps05, "همگرایی با γ بزرگ‌تر باید کندتر باشد"
    print("خودآزمایی تمرین ۴: OK — سیاست γ=0.9 همان جلسه ۱۸ است و تعداد مرورها بیشتر شد")

    # تمرین ۵: برابری دقیق کسرها
    p_pos1, post1, post2 = res["t5"]
    assert p_pos1 == Fraction(43, 500), "P(+) باید دقیقاً 43/500 باشد"
    assert post1 == Fraction(19, 43), "پسین یک آزمون باید دقیقاً 19/43 باشد"
    assert post2 == Fraction(361, 385), "پسین دو آزمون باید دقیقاً 361/385 باشد"
    print("خودآزمایی تمرین ۵: OK — 43/500 ، 19/43 ، 361/385 به‌صورت دقیق تأیید شد")

    # تمرین ۶: گام‌های دقیق و فرمول بسته‌ی توزیع مانا
    snapshots, stationary = res["t6"]
    assert snapshots[1] == (Fraction(4, 5), Fraction(1, 5)), "گام ۱ نادرست است"
    assert snapshots[2] == (Fraction(18, 25), Fraction(7, 25)), "گام ۲ نادرست است"
    assert snapshots[3] == (Fraction(86, 125), Fraction(39, 125)), "گام ۳ نادرست است"
    pi_ok = MARKOV_T[1][0] / (MARKOV_T[0][1] + MARKOV_T[1][0])
    assert abs(float(stationary[0]) - float(pi_ok)) < 1e-9, \
        "توزیع مانا با فرمول بسته نمی‌خواند"
    print("خودآزمایی تمرین ۶: OK — گام‌های ۱ تا ۳ دقیق و مانا برابر 2/3 تأیید شد")

    # تمرین ۷: برابری دقیق متریک‌ها
    m = res["t7"]
    assert m["acc"] == Fraction(17, 20), "Accuracy باید دقیقاً 17/20 باشد"
    assert m["sens"] == Fraction(5, 6), "Sensitivity باید دقیقاً 5/6 باشد"
    assert m["spec"] == Fraction(6, 7), "Specificity باید دقیقاً 6/7 باشد"
    assert m["ppv"] == Fraction(5, 7), "PPV باید دقیقاً 5/7 باشد"
    assert m["npv"] == Fraction(12, 13), "NPV باید دقیقاً 12/13 باشد"
    assert m["f1"] == Fraction(10, 13), "F1 باید دقیقاً 10/13 باشد"
    print("خودآزمایی تمرین ۷: OK — هر شش متریک با کسر دقیق تأیید شد")

    # تمرین ۸: سازگاری اجزای ترکیبی با تمرین‌های قبلی
    steps8, qs8, v18, post18, m8 = res["t8"]
    assert len(steps8) == 3, "زنجیره‌ی منطق باید ۳ گام داشته باشد"
    assert abs(qs8[("s2", "a3")] - (-2.0)) < 1e-9, "Q(s2,a3) باید -2.0 باشد"
    assert abs(v18["s2"] - (-1.0)) < 1e-9, "V1(s2) باید -1.0 باشد"
    assert post18 == Fraction(19, 43), "پسین باید 19/43 باشد"
    assert m8["f1"] == Fraction(10, 13), "F1 باید 10/13 باشد"
    print("خودآزمایی تمرین ۸: OK — هر چهار بخش با نتایج تمرین‌های ۱ تا ۷ سازگار است")


def main():
    print("=" * 62)
    print("جلسه ۲۳ — جلسه حل تمرین ۲: راه‌حل‌های مرجع")
    print("=" * 62)
    print()
    res = run_exercises()
    print("-" * 62)
    run_self_checks(res)
    print()
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
