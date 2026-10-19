# -*- coding: utf-8 -*-
"""جلسه ۱۸ — فرایند تصمیم مارکوف (MDP): Value Iteration و Policy Iteration

سناریوی آموزشی: یک مدل مینی‌اتم تصمیم درمانی/پایش بیمار (کاملاً ساختگی و
غیرتشخیصی) با سه حالت:
  - «پایدار»: بیمار وضعیت پایدار دارد.
  - «بدحال»: وضعیت بدتر شده است.
  - «بهبود»: حالت پایانی (ترخیص با بهبودی).

در هر مرحله (مراحل زمانی گسسته) یک «کنش» انتخاب می‌شود:
  - از پایدار: «پایش» (هزینه کم) یا «بستری_پیشگیرانه» (هزینه زیاد، فایده اندک)
  - از بدحال:  «پایش» یا «درمان_مضاعف» (هزینه متوسط، اثر درمانی واقعی)

پاداش هر گذار = منفی هزینه مرحله + پاداش مثبت در صورت رسیدن به «بهبود».
هر دو الگوریتم Value Iteration و Policy Iteration پیاده‌سازی شده‌اند و
تابع ارزش بهینه V* و سیاست بهینه π* چاپ می‌شوند.

فقط از کتابخانه استاندارد پایتون استفاده می‌شود؛ خروجی قطعی است.
کد آموزشی است و هیچ کاربرد تشخیصی یا بالینی ندارد.
"""

GAMMA = 0.9      # ضریب تنزیل
THETA = 1e-10    # آستانه همگرایی
MAX_ITER = 1000

# ---------------- تعریف MDP ----------------

STATES = ("پایدار", "بدحال", "بهبود")
TERMINAL = {"بهبود"}          # حالت‌های پایانی: V = 0
STEP_COST = {"پایش": 1.0, "بستری_پیشگیرانه": 6.0, "درمان_مضاعف": 5.0}
RECOVERY_REWARD = 10.0        # پاداش رسیدن به «بهبود»

ACTIONS = {
    "پایدار": ("پایش", "بستری_پیشگیرانه"),
    "بدحال": ("پایش", "درمان_مضاعف"),
    "بهبود": (),                  # حالت پایانی
}

# احتمال‌های گذار P(s' | s, a) — برای هر (s, a) جمع احتمال‌ها = ۱
TRANSITIONS = {
    ("پایدار", "پایش"): {"پایدار": 0.9, "بدحال": 0.05, "بهبود": 0.05},
    ("پایدار", "بستری_پیشگیرانه"): {"پایدار": 0.8, "بدحال": 0.1, "بهبود": 0.1},
    ("بدحال", "پایش"): {"پایدار": 0.1, "بدحال": 0.9, "بهبود": 0.0},
    ("بدحال", "درمان_مضاعف"): {"پایدار": 0.4, "بدحال": 0.3, "بهبود": 0.3},
}


def reward(s, a, s2):
    """پاداش گذار R(s, a, s'): منفی هزینه کنش + پاداش بهبودی."""
    r = -STEP_COST[a]
    if s2 == "بهبود":
        r += RECOVERY_REWARD
    return r


def q_value(state, action, v):
    """Q(s, a) با تابع ارزش فعلی v."""
    total = 0.0
    for s2, p in TRANSITIONS[(state, action)].items():
        total += p * (reward(state, action, s2) + GAMMA * v[s2])
    return total


# ---------------- Value Iteration ----------------

def value_iteration():
    v = {s: 0.0 for s in STATES}
    sweeps = 0
    for _ in range(MAX_ITER):
        delta = 0.0
        new_v = {}
        for s in STATES:
            if s in TERMINAL or not ACTIONS[s]:
                new_v[s] = 0.0
                continue
            new_v[s] = max(q_value(s, a, v) for a in ACTIONS[s])
            delta = max(delta, abs(new_v[s] - v[s]))
        v = new_v
        sweeps += 1
        if delta < THETA:
            break
    pi = {s: None for s in STATES}
    for s in STATES:
        if s in TERMINAL or not ACTIONS[s]:
            continue
        q_values = [(q_value(s, a, v), a) for a in ACTIONS[s]]
        pi[s] = max(q_values)[1]          # بیشینه روی Q؛ در تساوی Q، مقایسه نام کنش (ترتیب یونیکد) تصمیم می‌گیرد
    return v, pi, sweeps


# ---------------- Policy Iteration ----------------

def policy_evaluation(pi, v0=None):
    """ارزیابی دقیق سیاست با حل تکراری معادله خطی V = R + gamma * P V."""
    v = dict(v0) if v0 else {s: 0.0 for s in STATES}
    for _ in range(MAX_ITER):
        delta = 0.0
        new_v = {}
        for s in STATES:
            if s in TERMINAL or not ACTIONS[s]:
                new_v[s] = 0.0
                continue
            new_v[s] = q_value(s, pi[s], v)
            delta = max(delta, abs(new_v[s] - v[s]))
        v = new_v
        if delta < THETA:
            break
    return v


def policy_iteration():
    pi = {s: (ACTIONS[s][0] if ACTIONS[s] else None) for s in STATES}
    v = {s: 0.0 for s in STATES}
    outer = 0
    while True:
        outer += 1
        v = policy_evaluation(pi, v)
        stable = True
        for s in STATES:
            if s in TERMINAL or not ACTIONS[s]:
                continue
            q_values = [(q_value(s, a, v), a) for a in ACTIONS[s]]
            best = max(q_values)[1]
            if best != pi[s]:
                pi[s] = best
                stable = False
        if stable:
            break
    return v, pi, outer


# ---------------- چاپ نتایج ----------------

def main():
    print("=" * 66)
    print("جلسه ۱۸ — MDP مینی‌پزشکی: Value Iteration و Policy Iteration")
    print("=" * 66)
    print("حالت‌ها :", "، ".join(STATES))
    print("کنش‌ها  :")
    for s in STATES:
        if ACTIONS[s]:
            print("   از «%s»: %s" % (s, " / ".join(ACTIONS[s])))
    print("γ = %.1f ، پاداش بهبودی = %.0f ، هزینه پایش = %.0f ،"
          % (GAMMA, RECOVERY_REWARD, STEP_COST["پایش"]))
    print("هزینه بستری پیشگیرانه = %.0f ، هزینه درمان مضاعف = %.0f"
          % (STEP_COST["بستری_پیشگیرانه"], STEP_COST["درمان_مضاعف"]))
    print()

    v_vi, pi_vi, sweeps = value_iteration()
    print("Value Iteration: همگرا پس از %d مرور کامل حالت‌ها" % sweeps)
    print("V* (Value Iteration):")
    for s in STATES:
        print("   V(%s) = %8.4f" % (s, v_vi[s]))
    print("π* (Value Iteration):")
    for s in STATES:
        if pi_vi[s] is not None:
            print("   π(%s) = %s" % (s, pi_vi[s]))
    print()

    v_pi, pi_pi, outer = policy_iteration()
    print("Policy Iteration: همگرا پس از %d تکرار بیرونی" % outer)
    print("V* (Policy Iteration):")
    for s in STATES:
        print("   V(%s) = %8.4f" % (s, v_pi[s]))
    print("π* (Policy Iteration):")
    for s in STATES:
        if pi_pi[s] is not None:
            print("   π(%s) = %s" % (s, pi_pi[s]))
    print()

    max_diff = max(abs(v_vi[s] - v_pi[s]) for s in STATES)
    same_policy = all(pi_vi[s] == pi_pi[s] for s in STATES if ACTIONS[s])
    print("مقایسه دو الگوریتم:")
    print("   بیشینه اختلاف V: %.2e" % max_diff)
    print("   سیاست بهینه یکسان: %s" % ("بله" if same_policy else "خیر"))
    print()
    print("نتیجه آموزشی:")
    print("- Value Iteration روی همه کنش‌ها بیشینه می‌گیرد؛ Policy Iteration")
    print("  بین ارزیابی و بهبود سیاست یکی در میان حرکت می‌کند؛ هر دو به V* و π*")
    print("  یکسان همگرا شدند.")
    print("- در این مدل، از حالت «پایدار» پایش کم‌هزینه کافی است، ولی از")
    print("  «بدحال» درمان مضاعف با وجود هزینه بیشتر، ارزش موردانتظار")
    print("  بالاتری دارد: هزینه بالا با بهبود وضعیت جبران می‌شود.")
    print()
    print("این کد فقط آموزشی است و هیچ کاربرد تشخیصی یا بالینی ندارد.")


if __name__ == "__main__":
    main()
