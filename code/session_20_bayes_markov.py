# -*- coding: utf-8 -*-
"""جلسه ۲۰ — احتمال شرطی، قاعده‌ی بیز، زنجیره‌ی مارکوف و HMM (الگوریتم پیش‌رو)

سه بخش:
1) استنتاج بیزین روی مثال تشخیصی-آموزشی: یک آزمایش غربالگری با حساسیت/ویژگی
   مشخص؛ پوستر (احتمال پسین) با قاعده‌ی بیز — با کسر دقیق (fractions.Fraction).
2) زنجیره‌ی مارکوف: وضعیت «سالم / در حال خرابی» یک دستگاه آزمایشگاهی؛
   توزیع گام‌به‌گام و توزیع مانا (Stationary Distribution) با تکرار ساده.
3) مدل پنهان مارکوف (HMM): همان دستگاه، حالت واقعی پنهان است و فقط دمای
   موتور مشاهده می‌شود؛ الگوریتم پیش‌رو (Forward Algorithm) احتمال حالت‌های
   پنهان را پس از هر مشاهده به‌روز می‌کند.

نکته تکرارپذیری: هیچ تاس و تصادفی در این اسکریپت نیست؛ همه‌ی اعداد حاصل
محاسبات قطعی‌اند (برای بیز با کسر دقیق). پس اجرای هر بار به‌تنهایی
همان عددهای اجرای کامل main() را می‌دهد.

فقط از کتابخانه استاندارد پایتون استفاده می‌شود.
کد آموزشی است و هیچ کاربرد تشخیصی یا بالینی ندارد.
"""

from fractions import Fraction
from itertools import product

# ---------------- بخش ۱: قاعده‌ی بیز روی یک مثال تشخیصی ----------------

# غربالگری فرضی برای یک بیماری کم‌شیوع (اعداد ساختگی و آموزشی)
PRIOR = Fraction(1, 100)        # P(D): شیوع بیماری در جامعه
SENSITIVITY = Fraction(9, 10)   # P(+ | D): حساسیت آزمون
FALSE_POS = Fraction(1, 10)     # P(+ | ¬D): نرخ مثبت کاذب (۱ − ویژگی؛ ویژگی = 9/10)


def bayes_update(prior, p_pos_given_state, p_pos=None):
    """یک گام قاعده‌ی بیز: P(D|+) = P(+|D)P(D) / P(+).

    اگر p_pos (شاهد) از بیرون داده نشود، از قانون تمام احتمال ساخته می‌شود.
    خروجی: (شاهد، پسین) به‌صورت کسر دقیق.
    """
    if p_pos is None:
        p_pos = p_pos_given_state * prior + FALSE_POS * (1 - prior)
    posterior = (p_pos_given_state * prior) / p_pos
    return p_pos, posterior


def bayes_screening():
    """یک بار آزمایش مثبت؛ احتمال پسین را با کسر دقیق حساب و چاپ می‌کند."""
    print("=" * 64)
    print("بخش ۱ — قاعده‌ی بیز روی مثال تشخیصی-آموزشی")
    print("P(D)=%s  P(+|D)=%s  P(+|سالم)=%s  P(-|سالم)=%s"
          % (PRIOR, SENSITIVITY, FALSE_POS, 1 - FALSE_POS))
    p_pos, posterior = bayes_update(PRIOR, SENSITIVITY)
    print("شاهد: P(+) = P(+|D)P(D) + P(+|سالم)P(سالم)")
    print("      = %s × %s + %s × %s = %s ≈ %.4f"
          % (SENSITIVITY, PRIOR, FALSE_POS, 1 - PRIOR, p_pos, float(p_pos)))
    print("پسین: P(D|+) = %s ≈ %.4f  (فقط حدود %.1f٪!)"
          % (posterior, float(posterior), 100 * float(posterior)))
    return posterior


def sequential_tests(n_tests=2):
    """آزمایش دوم مستقل: پسین دیروز به پیشین امروز تبدیل می‌شود."""
    print("-" * 64)
    print("بیز زنجیره‌ای: نتیجه‌ی هر آزمون مستقل، پسین قبلی را پیشین می‌کند")
    prior = PRIOR
    for t in range(1, n_tests + 1):
        p_pos, posterior = bayes_update(prior, SENSITIVITY)
        print("بعد از آزمون %d: P(+)=%s ≈ %.4f  →  P(D|+) = %s ≈ %.4f"
              % (t, p_pos, float(p_pos), posterior, float(posterior)))
        prior = posterior
    return posterior


# ---------------- بخش ۲: زنجیره‌ی مارکوف ----------------

# دو حالت: 0 = سالم، 1 = در حال خرابی
TRANSITION = [[Fraction(9, 10), Fraction(1, 10)],   # از سالم به ...
              [Fraction(3, 10), Fraction(7, 10)]]   # از در حال خرابی به ...
START_DIST = [Fraction(4, 5), Fraction(1, 5)]       # توزیع اولیه

OBS_LABELS = ["داغ", "عادی"]                        # مشاهده‌ی دمای موتور
EMISSION = [[Fraction(2, 10), Fraction(8, 10)],     # سالم:     P(داغ), P(عادی)
            [Fraction(7, 10), Fraction(3, 10)]]     # خراب:     P(داغ), P(عادی)

# دنباله‌ی مشاهده‌ی دموی HMM؛ تکلیف ۲ همین ثابت را عوض می‌کند و خودآزمایی
# هم انتظار خودش را از همین ثابت می‌سازد (هیچ عددی هاردکد نیست).
DEMO_OBS = ("داغ", "داغ", "عادی")


def mat_vec(matrix, vector):
    """ضرب ماتریس در بردار (با کسر دقیق)."""
    n = len(vector)
    out = []
    for j in range(n):
        out.append(sum(matrix[i][j] * vector[i] for i in range(n)))
    return out


def markov_chain_demo(steps=(1, 2, 3, 10, 30)):
    """توزیع حالت در گام‌های بعد و توزیع مانا (تکرار ۳۰ گام)."""
    print("=" * 64)
    print("بخش ۲ — زنجیره‌ی مارکوف: وضعیت دستگاه (بدون مشاهده)")
    print("ماتریس انتقال: از سالم → [%s, %s] ؛ از خراب → [%s, %s]"
          % (TRANSITION[0][0], TRANSITION[0][1],
             TRANSITION[1][0], TRANSITION[1][1]))
    dist = START_DIST
    snapshots = {}
    for t in range(1, max(steps) + 1):
        dist = mat_vec(TRANSITION, dist)
        if t in steps:
            snapshots[t] = dist
            print("گام %2d: P(سالم)=%.4f  P(خراب)=%.4f"
                  % (t, float(dist[0]), float(dist[1])))
    print("توزیع مانا (حد تکرار): P(سالم)=%.4f  P(خراب)=%.4f"
          % (float(dist[0]), float(dist[1])))
    print("بیماری فراموش‌شونده (Forgetfulness): توزیع اولیه در توزیع مانا ذوب می‌شود")
    return dist


# ---------------- بخش ۳: HMM و الگوریتم پیش‌رو ----------------

def forward(obs_seq):
    """الگوریتم پیش‌رو با نرمال‌سازی گام‌به‌گام.

    خروجی: فهرستی از توزیع‌های باور (belief) پس از هر مشاهده؛
    هر درونداد توزیعی روی دو حالت پنهان (سالم، در حال خرابی) است.
    """
    beliefs = []
    # گام ۰: پیشین × آهنگ انتشار اولین مشاهده، سپس نرمال‌سازی
    belief = [START_DIST[i] * EMISSION[i][obs_seq[0]] for i in range(2)]
    z = sum(belief)
    belief = [b / z for b in belief]
    beliefs.append(belief)
    # گام‌های بعد: پیش‌بینی (انتقال) + تصحیح (انتشار) + نرمال‌سازی
    for o in obs_seq[1:]:
        predicted = mat_vec(TRANSITION, belief)
        belief = [predicted[i] * EMISSION[i][o] for i in range(2)]
        z = sum(belief)
        belief = [b / z for b in belief]
        beliefs.append(belief)
    return beliefs


def hmm_forward_demo(obs_names=None):
    """اجرای الگوریتم پیش‌رو روی دنباله‌ی مشاهده و چاپ باورها."""
    # اتصال دیرهنگام به DEMO_OBS؛ پیش‌فرض در زمان تعریف تابع قفل نمی‌شود
    if obs_names is None:
        obs_names = DEMO_OBS
    obs_seq = [OBS_LABELS.index(o) for o in obs_names]
    print("=" * 64)
    print("بخش ۳ — HMM: حالت واقعی پنهان است، فقط دمای موتور را می‌بینیم")
    print("مشاهده‌ها: " + " ، ".join(obs_names))
    beliefs = forward(obs_seq)
    for t, (o, belief) in enumerate(zip(obs_names, beliefs), 1):
        print("بعد از مشاهده‌ی %d («%s»): P(سالم)=%.4f  P(خراب)=%.4f"
              % (t, o, float(belief[0]), float(belief[1])))
    print("تفسیر: داغ پشت‌سرهم به «خرابی» می‌اندازد؛ یک «عادی» باور را "
          "به سمت سلامت برمی‌گرداند")
    return beliefs


def brute_force_last_state_posterior(obs_seq):
    """پسین حالتِ آخر با شمارش کامل همه‌ی توالی‌های حالت (مرجعِ مستقل از پیش‌رو)."""
    joint = [Fraction(0), Fraction(0)]
    for seq in product(range(2), repeat=len(obs_seq)):
        w = START_DIST[seq[0]] * EMISSION[seq[0]][obs_seq[0]]
        for t in range(1, len(obs_seq)):
            w *= TRANSITION[seq[t - 1]][seq[t]] * EMISSION[seq[t]][obs_seq[t]]
        joint[seq[-1]] += w
    z = sum(joint)
    return [j / z for j in joint]


def self_check(posterior1, posterior2, stationary, beliefs):
    """آزمون خودکار: انتظارها از خودِ پارامترهای فعلی ساخته می‌شوند.

    پسین‌ها با فرمول بسته‌ی بیز از PRIOR/SENSITIVITY/FALSE_POS، توزیع مانا با
    فرمول بسته‌ی زنجیره‌ی دوحالته از TRANSITION، و باور نهایی HMM با شمارش
    کامل توالی‌های حالت مقایسه می‌شود؛ پس تغییر پارامترها در تکلیف خودآزمایی
    را نمی‌شکند، ولی اگر محاسبات اشتباه باشد هنوز می‌ایستد.
    """
    # بخش ۱: پسین یک و دو آزمون با فرمول بسته
    p_pos = SENSITIVITY * PRIOR + FALSE_POS * (1 - PRIOR)
    expect1 = (SENSITIVITY * PRIOR) / p_pos
    assert posterior1 == expect1, "پسین یک آزمون با فرمول بسته نمی‌خواند"
    p_pos = SENSITIVITY * expect1 + FALSE_POS * (1 - expect1)
    expect2 = (SENSITIVITY * expect1) / p_pos
    assert posterior2 == expect2, "پسین دو آزمون با فرمول بسته نمی‌خواند"
    # بخش ۲: توزیع مانا؛ زنجیره‌ی دوحالته:
    # pi(سالم) = t(خراب→سالم) / (t(سالم→خراب) + t(خراب→سالم))
    pi_ok = TRANSITION[1][0] / (TRANSITION[0][1] + TRANSITION[1][0])
    assert abs(float(stationary[0]) - float(pi_ok)) < 1e-6, \
        "توزیع مانا با فرمول بسته نمی‌خواند"
    # بخش ۳: باور نهایی HMM در برابر شمارش کامل + اعتبار هر باور
    expect_belief = brute_force_last_state_posterior(
        [OBS_LABELS.index(o) for o in DEMO_OBS])
    for got, want in zip(beliefs[-1], expect_belief):
        assert abs(float(got) - float(want)) < 1e-9, \
            "باور نهایی HMM با شمارش کامل توالی‌ها نمی‌خواند"
    for b in beliefs:
        assert abs(float(b[0]) + float(b[1]) - 1.0) < 1e-9, "باورها باید جمعشان ۱ باشد"
    print("\nخودآزمایی کد: OK — پسین‌ها و توزیع مانا با فرمول بسته و "
          "باور نهایی HMM با شمارش کامل توالی‌های حالت می‌خواند")


def main():
    p1 = bayes_screening()
    p2 = sequential_tests()
    pi = markov_chain_demo()
    beliefs = hmm_forward_demo()
    self_check(p1, p2, pi, beliefs)


if __name__ == "__main__":
    main()
