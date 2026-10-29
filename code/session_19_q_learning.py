# -*- coding: utf-8 -*-
"""جلسه ۱۹ — یادگیری تقویتی و Q-learning جدولی (Tabular Q-learning)

سناریوی آموزشی: تکنسین از «ایستگاه پرستاری» (0,0) باید به «اتاق تجهیزات» (4,4)
برسد؛ همان شبکه ۵×۵ جلسات جست‌وجو، اما این‌بار:
- هیچ نقشه‌ای به عامل نمی‌دهیم؛ فقط پاداش/جریمه را تجربه می‌کند و یاد می‌گیرد.
- اتاق آلوده (2,3) جریمه سنگین دارد؛ عامل باید خودش یاد بگیرد از آن دور بزند.
- خانه‌های «#» بسته‌اند و عبور از آن‌ها ممکن نیست (حرکتِ به سمت دیوار = ماندن درجا).

نکته تکرارپذیری: از random با seed ثابت استفاده می‌کنیم، اما seed به‌صورت
«به‌ازای هر قسمت (episode)» ساخته می‌شود؛ یعنی نتیجه به تعداد و ترتیب
فراخوانی توابع بستگی ندارد و اجرای هر بار به‌تنهایی همان عددهای این فایل را می‌دهد.

فقط از کتابخانه استاندارد پایتون (random با seed ثابت) استفاده می‌شود.
کد آموزشی است و هیچ کاربرد تشخیصی یا بالینی ندارد.
"""

import random

# ---------------- محیط: طبقه بیمارستان (همان شبکه ۵×۵) ----------------

N = 5
START = (0, 0)              # ایستگاه پرستاری
GOAL = (4, 4)               # اتاق تجهیزات
BLOCKED = {(1, 1), (2, 1), (3, 3)}   # اتاق‌های بسته
HAZARD = (2, 3)             # اتاق آلوده (جریمه سنگین)

STEP_COST = -1.0            # هزینه هر گام
HAZARD_PENALTY = -6.0       # جریمه ورود به اتاق آلوده
GOAL_REWARD = 10.0          # پاداش رسیدن به اتاق تجهیزات

# اقدام‌ها: 0=بالا  1=پایین  2=چپ  3=راست
ACTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
ACTION_NAMES = ["UP", "DOWN", "LEFT", "RIGHT"]

# ---------------- فراپارامترهای Q-learning ----------------

EPISODES = 400       # تعداد قسمت‌های تمرین
MAX_STEPS = 100      # سقف گام در هر قسمت
ALPHA = 0.5          # نرخ یادگیری
GAMMA = 0.9          # ضریب تنزیل
EPS_START = 1.0      # شروع با اکتشاف کامل
EPS_DECAY = 0.99     # افت نمایی اپسیلون بر حسب شماره قسمت
EPS_MIN = 0.05       # حداقل اکتشاف

# seed پایه؛ هر قسمت ep امین seed مستقل SEED_BASE + ep را می‌گیرد.
# (اگر seed یک‌بار در ابتدای برنامه گرفته می‌شد، خروجی به ترتیب اجرای توابع
#  وابسته می‌شد — خطای رایج در تکرارپذیری.)
SEED_BASE = 2026


def step(state, action_idx):
    """انتقال قطعی محیط: (وضعیت بعدی، پاداش، پایان قسمت)."""
    r, c = state
    dr, dc = ACTIONS[action_idx]
    nr, nc = r + dr, c + dc
    # دیوار یا لبه نقشه → درجا می‌ماند (اما هزینه گام را می‌دهد)
    if not (0 <= nr < N and 0 <= nc < N) or (nr, nc) in BLOCKED:
        nr, nc = r, c
    nxt = (nr, nc)
    reward = STEP_COST
    if nxt == HAZARD:
        reward += HAZARD_PENALTY
    done = (nxt == GOAL)
    if done:
        reward += GOAL_REWARD
    return nxt, reward, done


def eps_for_episode(ep):
    """اپسیلون فقط تابع شماره قسمت است؛ نه تاریخچه اجرا."""
    return max(EPS_MIN, EPS_START * (EPS_DECAY ** ep))


def q_row(Q, state):
    """مقدار Q یک وضعیت؛ اگر نبود، ردیف صفر بساز."""
    return Q.setdefault(state, [0.0] * len(ACTIONS))


def choose_action(rng, Q, state, eps):
    """ε-greedy: با احتمال eps اقدام تصادفی، وگرنه بهترین اقدام."""
    if rng.random() < eps:
        return rng.randrange(len(ACTIONS))
    vals = q_row(Q, state)
    best = max(vals)
    return vals.index(best)   # تساوی‌ها: نخستین اقدام در ترتیب ثابت


def train():
    """حلقه Q-learning؛ جدول Q را برمی‌گرداند.

    seed هر قسمت مستقل است (SEED_BASE + ep) و اپسیلون هم تابع ep است؛
    بنابراین این تابع هرجا صدا زده شود همان جدول Q را می‌سازد.
    """
    Q = {}
    for ep in range(EPISODES):
        rng = random.Random(SEED_BASE + ep)
        eps = eps_for_episode(ep)
        state = START
        for _ in range(MAX_STEPS):
            a = choose_action(rng, Q, state, eps)
            nxt, reward, done = step(state, a)
            # به‌روزرسانی بل: r + gamma * max_a' Q(s',a')
            target = reward if done else reward + GAMMA * max(q_row(Q, nxt))
            vals = q_row(Q, state)
            vals[a] += ALPHA * (target - vals[a])
            state = nxt
            if done:
                break
    return Q


def greedy_policy(Q):
    """سیاست حاصل از Q: برای هر وضعیت بهترین اقدام (تساوی: ترتیب ثابت)."""
    policy = {}
    for r in range(N):
        for c in range(N):
            s = (r, c)
            if s in BLOCKED:
                policy[s] = "#"
            elif s == GOAL:
                policy[s] = "G"
            else:
                vals = q_row(Q, s)
                policy[s] = ACTION_NAMES[vals.index(max(vals))]
    return policy


def print_q_table(Q):
    """چاپ جدول Q برای همه وضعیت‌ها (به‌ازای هر وضعیت، چهار مقدار)."""
    print("جدول Q نهایی (هر ردیف: مقادیر UP/DOWN/LEFT/RIGHT):")
    print("%-8s%s" % ("state", "".join("%9s" % n for n in ACTION_NAMES)))
    for r in range(N):
        for c in range(N):
            s = (r, c)
            if s in BLOCKED:
                print("%-8s%s" % ("(%d,%d)" % (r, c), "دیوار"))
                continue
            vals = q_row(Q, s)
            cells = "".join("%9.2f" % v for v in vals)
            print("%-8s%s" % ("(%d,%d)" % (r, c), cells))


def print_policy_grid(policy):
    """چاپ نقشه سیاست: ^ v < > برای اقدام، # دیوار، G هدف، S شروع."""
    arrows = {"UP": "^", "DOWN": "v", "LEFT": "<", "RIGHT": ">"}
    print("\nسیاست آموخته‌شده (^ بالا، v پایین، < چپ، > راست):")
    print("      c0  c1  c2  c3  c4")
    for r in range(N):
        cells = []
        for c in range(N):
            s = (r, c)
            if s == START:
                cells.append(" S ")
            elif s == GOAL:
                cells.append(" G ")
            elif s in BLOCKED:
                cells.append(" # ")
            elif s == HAZARD:
                cells.append(" ! ")
            else:
                cells.append(" %s " % arrows[policy[s]])
        print("r%d  %s" % (r, "".join(cells)))
    print("( ! = اتاق آلوده با جریمه، سیاست معمولاً دور آن می‌زند)")


def rollout(Q, max_steps=30):
    """اجرای سیاست حریصانه از شروع تا هدف؛ مسیر و مجموع پاداش."""
    state = START
    path = [state]
    total = 0.0
    for _ in range(max_steps):
        vals = q_row(Q, state)
        a = vals.index(max(vals))
        state, reward, done = step(state, a)
        total += reward
        path.append(state)
        if done:
            break
    return path, total


def self_check(Q, path, total):
    """آزمون خودکار نتیجه: مسیر بهینه ۸ گام، بدون اتاق آلوده."""
    # قاعده‌ی انتقالِ مورد استفاده‌ی فعالیت ۱ درس‌نامه: از (4,2) «پایین» به لبه‌ی
    # نقشه می‌خورد و عامل درجا می‌ماند؛ فقط «راست» به (4,3) می‌رسد.
    assert step((4, 2), 1)[0] == (4, 2), "«پایین» از (4,2) باید حلقه‌ی درجا باشد"
    assert step((4, 2), 3)[0] == (4, 3), "«راست» از (4,2) باید به (4,3) برسد"
    # عددهای فعالیت ۱ درس‌نامه (در متن گرد شده: 3.85 / 5.39 / 7.10) فقط برای
    # اجرای پیش‌فرض (gamma = 0.9) برقرارند؛ تکلیف، gamma را 0.5 می‌کند و در آن
    # حالت این آزمون اجرا نمی‌شود (قاعده‌ی دیوار در دو خط بالا مستقل از پارامتر است).
    if GAMMA == 0.9:
        row42 = q_row(Q, (4, 2))
        assert abs(row42[0] - 3.85) < 5e-3 and abs(row42[1] - 5.39) < 5e-3 \
            and abs(row42[3] - 7.10) < 5e-3, "ردیف Q(4,2) با عددهای فعالیت ۱ نمی‌خواند"
    path_set = set(path)
    steps = len(path) - 1
    assert path[-1] == GOAL, "سیاست حریصانه به هدف نمی‌رسد"
    # این شرط فقط وقتی معنا دارد که جریمه اتاق آلوده فعال باشد
    # (تکلیف جلسه: با HAZARD_PENALTY = 0 این شرط حذف می‌شود)
    if HAZARD_PENALTY < 0:
        assert HAZARD not in path_set, "سیاست حریصانه وارد اتاق آلوده شده است"
    assert steps == 8, "مسیر بهینه باید ۸ گام باشد"
    # ۷ گام معمولی (۷×−۱) + گام آخر (−۱ + ۱۰ = +۹) → مجموع ۲+
    assert abs(total - 2.0) < 1e-9, "مجموع پاداش باید دقیقاً +۲ باشد"
    checks = ["مسیر ۸ گام", "قاعده‌ی دیوار در (4,2)", "مجموع پاداش +۲"]
    if GAMMA == 0.9:
        checks.insert(1, "ردیف Q(4,2) با عددهای فعالیت ۱")
    if HAZARD_PENALTY < 0:
        checks.insert(2, "بدون ورود به اتاق آلوده")
    print("\nخودآزمایی کد: OK — " + "، ".join(checks))


def main():
    print("=" * 64)
    print("Q-learning جدولی روی شبکه «رسیدن به اتاق تجهیزات»")
    print("پارامترها: episodes=%d, alpha=%.1f, gamma=%.1f,"
          " eps: %.2f->%.2f (decay %.2f)"
          % (EPISODES, ALPHA, GAMMA, EPS_START, EPS_MIN, EPS_DECAY))
    print("=" * 64)

    Q = train()
    print_q_table(Q)
    policy = greedy_policy(Q)
    print_policy_grid(policy)

    path, total = rollout(Q)
    print("\nاجرای سیاست حریصانه از (0,0):")
    print("  " + " → ".join(str(p) for p in path))
    print("طول مسیر: %d گام، مجموع پاداش: %.1f" % (len(path) - 1, total))

    self_check(Q, path, total)


if __name__ == "__main__":
    main()
