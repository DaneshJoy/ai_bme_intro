# -*- coding: utf-8 -*-
"""Backtracking + Forward Checking + MRV — جلسه ۱۲

مسئله نمونه «تخصیص دستگاه تصویربرداری به بیماران» (آموزشی و غیرتشخیصی):
چهار بیمار P1..P4 در یک روز باید به چهار دستگاه MRI، CT، US-1 و US-2
تخصیص یابند.

صورت‌بندی CSP:
  متغیرها:  P1, P2, P3, P4 (هر بیمار یک متغیر)
  دامنه‌ها:  دستگاه‌های مجاز هر بیمار (قید یکانی = محدودیت ارجاع)
  قیدها:    Alldifferent (سراسری) + قید دوتایی کنترل عفونت:
            بیماران P1 و P4 (نشان‌دار) باید در دو بلوک ساختمان
            متفاوت (A یا B) تصویربرداری شوند.

دو جست‌وجو مقایسه می‌شود:
  1) Backtracking ساده با ترتیب ثابت متغیرها و مقادیر (ترتیب اعلام)
  2) Backtracking + MRV (کمترین مقادیر باقی‌مانده) + FC (بررسی پیش‌رو)

اجرا:
    python3 code/session_12_csp_backtracking.py

فقط کتابخانه استاندارد پایتون. خروجی کاملاً قطعی است.
"""

# ------------------------------------------------ صورت‌بندی مسئله
DEVICES = ["MRI", "CT", "US-1", "US-2"]
BLOCK = {"MRI": "A", "CT": "A", "US-1": "B", "US-2": "B"}

PATIENTS = ["P1", "P2", "P3", "P4"]
# ترتیب مقادیر در هر دامنه = ترتیب اعلام (اولویت ارجاع)؛
# جست‌وجوی ساده همین ترتیب را امتحان می‌کند.
DOMAINS = {
    "P1": ["MRI"],            # فقط MRI (قید یکانی: محدودیت ارجاع)
    "P2": ["US-1", "CT"],     # اولویت سونوگرافی، جایگزین CT
    "P3": ["US-1", "US-2"],
    "P4": ["MRI", "CT", "US-2"],
}

# قیود دوتایی: (متغیر ۱، متغیر ۲، نام رابطه)
BINARY = [("P1", "P4", "different_block")]


def different_block(var_a, val_a, var_b, val_b):
    """قید کنترل عفونت: P1 و P4 در دو بلوک متفاوت تصویربرداری شوند."""
    return BLOCK[val_a] != BLOCK[val_b]


RELATIONS = {"different_block": different_block}


# ----------------------------------------- سازگاری جست‌وجوی ساده
def consistent(assignment):
    """بررسی کامل حالت فعلی: Alldifferent + همه‌ی قیود دوتایی مقدارگرفته."""
    values = list(assignment.values())
    if len(set(values)) != len(values):          # قید سراسری Alldifferent
        return False
    for a, b, rel in BINARY:                      # قیود دوتایی
        if a in assignment and b in assignment:
            if not RELATIONS[rel](a, assignment[a], b, assignment[b]):
                return False
    return True


def backtracking_plain(assignment=None, depth=0, stats=None, trace=None):
    """Backtracking ساده: ترتیب ثابت PATIENTS، مقادیر به ترتیب اعلام دامنه."""
    if assignment is None:
        assignment, stats, trace = {}, \
            {"attempts": 0, "assigns": 0, "dead_ends": 0}, []
    if len(assignment) == len(PATIENTS):
        return dict(assignment), stats, trace
    var = PATIENTS[depth]
    indent = "  " * depth
    for value in DOMAINS[var]:
        stats["attempts"] += 1
        assignment[var] = value
        if consistent(assignment):
            stats["assigns"] += 1
            trace.append(indent + f"{var} = {value}")
            result, stats, trace = backtracking_plain(
                assignment, depth + 1, stats, trace)
            if result:
                return result, stats, trace
            del assignment[var]                    # پس‌گرد
            stats["dead_ends"] += 1
            trace.append(indent + f"بن‌بست زیر {var} = {value} → پس‌گرد")
        else:
            del assignment[var]
            trace.append(indent + f"{var} = {value}  ✗ ناسازگار")
    return None, stats, trace


# -------------------------------- Forward Checking + انتخاب MRV
def forward_check(domains, var, value, assignment):
    """بررسی پیش‌رو: بعد از تخصیص value به var، مقادیر ناسازگار را از
    دامنه‌ی متغیرهای تخصیص‌ناشده حذف می‌کند.

    خروجی: دیکشنری دامنه‌های جدید، یا None اگر دامنه‌ای ته بماند.
    """
    new_domains = {p: set(d) for p, d in domains.items()}
    pruned = 0
    for other in PATIENTS:                       # انتشار قید سراسری Alldifferent
        if other != var and other not in assignment and value in new_domains[other]:
            new_domains[other].discard(value)
            pruned += 1
    for a, b, rel in BINARY:                     # انتشار قیود دوتایی
        if a == var:
            other = b
        elif b == var:
            other = a
        else:
            continue
        if other != var and other not in assignment:
            for w in sorted(new_domains[other]):
                if a == var:
                    ok = RELATIONS[rel](a, value, b, w)
                else:
                    ok = RELATIONS[rel](a, w, b, value)
                if not ok:
                    new_domains[other].discard(w)
                    pruned += 1
    if any(not d for d in new_domains.values()):
        return None, pruned
    return new_domains, pruned


def select_var_mrv(domains, assignment):
    """اکتشاف MRV: متغیر تخصیص‌ناشده با کمترین تعداد مقدار باقی‌مانده."""
    unassigned = [p for p in PATIENTS if p not in assignment]
    return min(unassigned, key=lambda p: (len(domains[p]), PATIENTS.index(p)))


def backtracking_fc_mrv(assignment=None, domains=None, stats=None):
    """Backtracking با FC + MRV: کمترین دامنه اول، و حذف زودهنگام مقادیر."""
    if assignment is None:
        assignment = {}
        domains = {p: set(d) for p, d in DOMAINS.items()}
        stats = {"attempts": 0, "assigns": 0, "backtracks": 0,
                 "prunes": 0, "fc_failures": 0}
    if len(assignment) == len(PATIENTS):
        return dict(assignment), stats
    var = select_var_mrv(domains, assignment)
    for value in sorted(domains[var], key=DOMAINS[var].index):
        stats["attempts"] += 1
        new_domains, pruned = forward_check(domains, var, value, assignment)
        stats["prunes"] += pruned
        if new_domains is None:
            stats["fc_failures"] += 1
            continue                             # مقدار زودتر رد می‌شود
        stats["assigns"] += 1
        assignment[var] = value
        result, stats = backtracking_fc_mrv(assignment, new_domains, stats)
        if result:
            return result, stats
        del assignment[var]
        stats["backtracks"] += 1
    return None, stats


# ------------------------------------------------------------- اجرا
def describe_problem():
    print("تخصیص دستگاه تصویربرداری به بیماران (آموزشی و غیرتشخیصی)")
    print("دستگاه‌ها و بلوک ساختمان:", ", ".join(
        f"{d}(بلوک {BLOCK[d]})" for d in DEVICES))
    print()
    print("متغیرها و دامنه‌ها (ترتیب اعلام = اولویت ارجاع):")
    for p in PATIENTS:
        print(f"  {p}: {' , '.join(DOMAINS[p])}")
    print()
    print("قیدها:")
    print("  سراسری: Alldifferent — هر دستگاه حداکثر به یک بیمار")
    for a, b, rel in BINARY:
        print(f"  دوتایی: {a} و {b} → {rel} (کنترل عفونت، بلوک متفاوت)")
    print()


def main():
    describe_problem()

    print("=== جست‌وجوی ۱: Backtracking ساده (ترتیب ثابت) ===")
    solution, stats, trace = backtracking_plain()
    for line in trace:
        print(line)
    print(f"حل: {solution}")
    print(f"آمار: {stats['attempts']} بار امتحان مقدار، "
          f"{stats['assigns']} تخصیص موقت، {stats['dead_ends']} پس‌گرد (بن‌بست)")
    print()

    print("=== جست‌وجوی ۲: Backtracking + MRV + Forward Checking ===")
    solution2, stats2 = backtracking_fc_mrv()
    print("ترتیب انتخاب متغیرها (MRV): P1 → P4 → P3 → P2  (کوچک‌ترین دامنه اول)")
    print(f"حل: {solution2}")
    print(f"آمار: {stats2['attempts']} بار امتحان مقدار، "
          f"{stats2['assigns']} تخصیص، {stats2['backtracks']} پس‌گرد، "
          f"{stats2['prunes']} مقدار حذف‌شده با FC، "
          f"{stats2['fc_failures']} شکست FC")
    print()

    print("=== مقایسه ===")
    header = "{:<28}{:>12}{:>12}{:>12}".format(
        "Search", "attempts", "assigns", "backtracks")
    print(header)
    print("-" * len(header))
    print("{:<28}{:>12}{:>12}{:>12}".format(
        "Backtracking ساده", stats["attempts"], stats["assigns"],
        stats["dead_ends"]))
    print("{:<28}{:>12}{:>12}{:>12}".format(
        "FC + MRV", stats2["attempts"], stats2["assigns"],
        stats2["backtracks"]))
    print()
    print("نکته‌ها:")
    print("1) هر دو روش به یک راه‌حل می‌رسند؛ FC + MRV با حذف زودهنگام")
    print("   مقادیر ناسازگار، شاخه‌های مرده را قبل از پیمایش حذف می‌کند.")
    print("2) MRV متغیرهایی را که قیودشان سخت‌تر است (دامنه کوچک‌تر) زودتر")
    print("   تخصیص می‌دهد؛ شکست‌ها پایین‌ترِ درخت رخ می‌کنند و درخت کوچک‌تر می‌شود.")


if __name__ == "__main__":
    main()
