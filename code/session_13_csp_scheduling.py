# -*- coding: utf-8 -*-
"""جلسه ۱۳ — حل CSP و مسئله زمان‌بندی: برنامه شیفت پرستاری

سناریوی آموزشی: بخشی از یک بیمارستان با ۴ پرستار (P1 تا P4).
- هفت روز هفته، هر روز دو شیفت: صبح (M) و شب (N) — یعنی ۱۴ متغیر.
- هر شیفت باید دقیقاً توسط یک پرستار پوشش داده شود (Coverage).
- قیدهای سخت:
  1) هیچ پرستاری در یک روز هم صبح و هم شب نگیرد (شیفت دوبل ممنوع).
  2) هیچ پرستاری شبِ یک روز و صبحِ روز بعد نگیرد (شیفت متوالی ممنوع).
- قید نرم: تعادل بار کاری — پرستار کم‌بار زودتر امتحان می‌شود.

این اسکریپت:
1) مسئله را به‌صورت CSP (متغیر/دامنه/قید) صورت‌بندی می‌کند.
2) آن را با Backtracking + MRV حل می‌کند.
3) جدول شیفت نهایی و بار کاری هر پرستار را چاپ می‌کند و در پایان
   همه قیدهای سخت را روی راه‌حل بازبینی می‌کند (assert).

فقط از کتابخانه استاندارد پایتون استفاده می‌شود.
کد آموزشی است و هیچ کاربرد تشخیصی یا بالینی ندارد.
"""

# ---------------- داده‌های مسئله ----------------

DAYS = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]
SHIFTS = ["M", "N"]          # M = صبح، N = شب
NURSES = ["P1", "P2", "P3", "P4"]

VARIABLES = [(d, s) for d in range(len(DAYS)) for s in SHIFTS]

# جفت‌های متغیری که قید دوتایی بین‌شان داریم
PAIRS = set()
for d in range(len(DAYS)):
    PAIRS.add(((d, "M"), (d, "N")))              # شیفت دوبل در یک روز
    if d + 1 < len(DAYS):
        PAIRS.add(((d, "N"), (d + 1, "M")))      # شیفت متوالی شب -> صبح فردا


def day_name(var):
    return "%s (%s)" % (DAYS[var[0]], var[1])


# ---------------- بررسی قیدها ----------------

def consistent(var, value, assignment):
    """آیا تخصیص var=value با تخصیص‌های فعلی سازگار است؟
    فقط جفت‌های دارای قید بررسی می‌شوند (بازبینی بخشی، نه کل جدول).
    """
    for other, other_value in assignment.items():
        if (var, other) in PAIRS or (other, var) in PAIRS:
            if other_value == value:
                return False
    return True


def consistent_values(var, assignment):
    return [n for n in NURSES if consistent(var, n, assignment)]


# ---------------- هیوریستیک‌ها ----------------

def mrv_variable(assignment):
    """MRV: متغیر با کمترین مقادیر باقی‌مانده؛ تساوی با ترتیب متغیرها."""
    best, best_count = None, None
    for var in VARIABLES:
        if var in assignment:
            continue
        count = len(consistent_values(var, assignment))
        if best is None or count < best_count:
            best, best_count = var, count
    return best


def order_values(assignment):
    """ترتیب مقادیر بر اساس قید نرم: بار کاری کمتر زودتر؛ تساوی با کد پرستار."""
    load = {n: 0 for n in NURSES}
    for value in assignment.values():
        load[value] += 1
    return sorted(NURSES, key=lambda n: (load[n], n))


# ---------------- حل با Backtracking ----------------

def backtrack(assignment, stats):
    if len(assignment) == len(VARIABLES):
        return dict(assignment)
    var = mrv_variable(assignment)
    for value in order_values(assignment):
        if consistent(var, value, assignment):
            stats["nodes"] += 1          # شمارش تخصیص‌های سازگاری که امتحان شد
            assignment[var] = value
            result = backtrack(assignment, stats)
            if result is not None:
                return result
            del assignment[var]          # بن‌بست: بازگشت به عقب
    return None


# ---------------- بازبینی راه‌حل ----------------

def verify(schedule):
    """همه قیدهای سخت را روی راه‌حل نهایی چک می‌کند (خودآزمون با assert)."""
    assert len(schedule) == len(VARIABLES)
    for d in range(len(DAYS)):
        assert schedule[(d, "M")] != schedule[(d, "N")], "شیفت دوبل در روز %d" % d
        if d + 1 < len(DAYS):
            assert schedule[(d, "N")] != schedule[(d + 1, "M")], \
                "شیفت متوالی بین روز %d و %d" % (d, d + 1)


# ---------------- چاپ خروجی ----------------

def print_schedule(schedule):
    print("  روز           صبح (M)   شب (N)")
    print("  " + "-" * 34)
    for d in range(len(DAYS)):
        print("  %-13s %-8s %-8s" % (DAYS[d], schedule[(d, "M")], schedule[(d, "N")]))
    print()
    load = {n: 0 for n in NURSES}
    for value in schedule.values():
        load[value] += 1
    print("  بار کاری هفتگی هر پرستار (قید نرم: تعادل):")
    for n in NURSES:
        print("  %s: %d شیفت" % (n, load[n]))
    print()


def main():
    print("=" * 50)
    print("جلسه ۱۳ — برنامه شیفت پرستاری به‌عنوان CSP")
    print("=" * 50)
    print("متغیرها: %d شیفت در هفته" % len(VARIABLES))
    print("دامنه: [%s]" % ", ".join(NURSES))
    print("قیدها: پوشش کامل + بدون شیفت دوبل در یک روز + بدون شیفت متوالی")
    print()

    stats = {"nodes": 0}
    schedule = backtrack({}, stats)
    if schedule is None:
        print("راه‌حلی یافت نشد! (مسئله بیش‌قید / over-constrained)")
        return
    print("راه‌حل پیدا شد (تعداد گره‌های جست‌وجو: %d)" % stats["nodes"])
    print()
    print_schedule(schedule)
    verify(schedule)
    print("بررسی نهایی قیدها: همه درست است.")
    print()
    print("این کد فقط آموزشی است و هیچ کاربرد تشخیصی یا بالینی ندارد.")


if __name__ == "__main__":
    main()
