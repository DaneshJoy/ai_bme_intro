# -*- coding: utf-8 -*-
"""جلسه ۱۷ — منطق گزاره‌ای و سیستم‌های خبره

این اسکریپت سه کار آموزشی می‌کند:
1) جدول درستی (Truth Table) عملگرهای منطقی گزاره‌ای را چاپ می‌کند.
2) یک موتور استنتاج روبه‌جلو (Forward Chaining) ساده روی قاعده‌های پزشکیِ
   آموزشی اجرا می‌کند: پایگاه قاعده + حافظه کاری + موتور استنتاج.
3) با «مجزا» (Resolution) به روش ردّ (Refutation) نشان می‌دهد چرا
   مجموعه‌دانش، هدفِ پرسیده‌شده را نتیجه می‌دهد.

فقط از کتابخانه استاندارد پایتون استفاده می‌شود.
خروجی قطعی (Deterministic) است: هیچ اتفاقی (Random) در کار نیست.
کد آموزشی است و هیچ کاربرد تشخیصی یا بالینی ندارد.
"""

# ---------------- بخش ۱: جدول درستی عملگرها ----------------

def implies(p, q):
    """همستان (Implication) پ → q: فقط وقتی p درست و q نادرست است، نادرست."""
    return (not p) or q


def truth_table():
    print("بخش ۱: جدول درستی عملگرهای گزاره‌ای")
    print("%-3s %-3s | %-4s %-4s %-4s %-5s %-5s" %
          ("P", "Q", "~P", "P&Q", "P|Q", "P->Q", "P<->Q"))
    print("-" * 40)
    for p in (True, False):
        for q in (True, False):
            print("%-3s %-3s | %-4s %-4s %-4s %-5s %-5s" % (
                "T" if p else "F",
                "T" if q else "F",
                "T" if (not p) else "F",
                "T" if (p and q) else "F",
                "T" if (p or q) else "F",
                "T" if implies(p, q) else "F",
                "T" if (p == q) else "F"))
    print()
    return True


# ---------------- بخش ۲: موتور استنتاج روبه‌جلو (سیستم خبره) ----------------
# قاعده‌ها کاملاً آموزشی و ساختگی‌اند؛ هیچ ارزش تشخیصی ندارند.

RULES = [
    ("R1", frozenset({"تب", "سرفه"}), "التهاب_تنفسی_محتمل"),
    ("R2", frozenset({"سرفه", "خلط_غیرعادی"}), "التهاب_تنفسی_محتمل"),
    ("R3", frozenset({"التهاب_تنفسی_محتمل", "سن_بالاتر_از_۶۵"}), "ارجاع_برای_بررسی_بیشتر"),
    ("R4", frozenset({"التهاب_تنفسی_محتمل", "اشباع_اکسیژن_پایین"}), "ارجاع_برای_بررسی_بیشتر"),
    ("R5", frozenset({"ارجاع_برای_بررسی_بیشتر"}), "اولویت_ویزیت_فوری"),
]

INITIAL_FACTS = ("تب", "سرفه", "سن_بالاتر_از_۶۵")


def forward_chain(rules, facts):
    """استنتاج روبه‌جلو: از حقایق اولیه تا رسیدن به نتیجه‌های تازه.

    تا وقتی قاعده‌ای بتواند نتیجه جدیدی تولید کند، حل می‌زنیم.
    ترتیب بررسی قاعده‌ها ثابت است؛ پس خروجی همیشه قطعی است.
    خروجی: (مجموعه نهایی حقایق، فهرست گام‌های اثبات)
    """
    known = set(facts)
    steps = []
    changed = True
    round_no = 0
    while changed:
        changed = False
        round_no += 1
        for name, premises, conclusion in rules:
            if conclusion in known:
                continue
            if premises <= known:
                known.add(conclusion)
                steps.append((name, sorted(premises), conclusion, round_no))
                changed = True
    return known, steps


def expert_system_demo():
    print("بخش ۲: سیستم خبره — استنتاج روبه‌جلو (Forward Chaining)")
    print("قاعده‌ها:")
    for name, premises, conclusion in RULES:
        print("  %s: {%s} => %s" % (name, " و ".join(sorted(premises)), conclusion))
    print("حقایق اولیه حافظه کاری: %s" % ", ".join(INITIAL_FACTS))
    print()

    known, steps = forward_chain(RULES, INITIAL_FACTS)

    print("گام‌های استنتاج:")
    for name, premises, conclusion, rnd in steps:
        print("  گام %d | %s فعال شد: {%s} => %s" %
              (rnd, name, " و ".join(premises), conclusion))
    print()
    print("حافظه کاری نهایی: %s" % ", ".join(sorted(known)))
    print()
    return True


# ---------------- بخش ۳: مجزا و اثبات با ردّ (Resolution / Refutation) ----------------
# گزاره‌ها با حروف لاتین کوتاه نمایش داده می‌شوند:
#   F = تب ، C = سرفه ، I = مشکل تنفسی محتمل
# نقیض با پیشوند ~ نشان داده می‌شود. هر بند (Clause) مجموعه‌ای از رویون‌هاست.

def resolve(c1, c2):
    """همه بندهای حاصل از مجزای دو بند را برمی‌گرداند."""
    resolvents = set()
    for l1 in c1:
        for l2 in c2:
            if l1 == negate(l2):
                merged = (c1 - {l1}) | (c2 - {l2})
                resolvents.add(frozenset(merged))
    return resolvents


def negate(lit):
    return lit[1:] if lit.startswith("~") else "~" + lit


def pl_resolution(clauses, goal_lit, max_rounds=50):
    """اثبات با ردّ: نقیض هدف را به مجموعه‌دانش اضافه کن و بندهای تازه بساز.

    اگر بند تهی ({} به‌دست آید، یعنی تناقض رخ داده و هدف نتیجه KB است.
    خروجی: (نتیجه درست/غلط، فهرست مراحل برای چاپ)
    """
    clauses = set(frozenset(c) for c in clauses)
    clauses.add(frozenset([negate(goal_lit)]))
    steps = [("بند اولیه", sorted(clauses, key=lambda c: sorted(c)))]
    for _ in range(max_rounds):
        new_clauses = set()
        clist = sorted(clauses, key=lambda c: sorted(c))
        for i in range(len(clist)):
            for j in range(i + 1, len(clist)):
                for res in resolve(clist[i], clist[j]):
                    if res not in clauses and res not in new_clauses:
                        new_clauses.add(res)
                        steps.append(("مجزای %s و %s" %
                                      (fmt_clause(clist[i]), fmt_clause(clist[j])),
                                      [res]))
                    if not res:
                        return True, steps
        if not new_clauses:
            return False, steps
        clauses |= new_clauses
    return False, steps


def fmt_clause(clause):
    if not clause:
        return "تهی"
    return "{" + ", ".join(sorted(clause)) + "}"


def resolution_demo():
    print("بخش ۳: مجزا و اثبات با ردّ (Resolution Refutation)")
    kb = [
        frozenset(["~F", "C"]),   # F -> C : تب نتیجه می‌دهد سرفه
        frozenset(["~C", "I"]),   # C -> I : سرفه نتیجه می‌دهد مشکل تنفسی محتمل
        frozenset(["F"]),         # تب داریم
    ]
    goal = "I"
    print("مجموعه‌دانش (KB):")
    print("  بند ۱: {~F, C}   (یعنی F -> C)")
    print("  بند ۲: {~C, I}   (یعنی C -> I)")
    print("  بند ۳: {F}       (تب داریم)")
    print("هدف اثبات: %s  (روش ردّ: نقیض هدف را اضافه می‌کنیم)" % goal)
    print()

    proved, steps = pl_resolution(kb, goal)
    step_no = 0
    for title, produced in steps:
        for res in produced:
            step_no += 1
            print("  گام %2d | %s => %s" % (step_no, title, fmt_clause(res)))
    print()
    if proved:
        print("بند تهی به‌دست آمد => تناقض؛ پس KB نتیجه می‌دهد I. اثبات کامل شد.")
    else:
        print("بند تهی حاصل نشد؛ اثبات شکست خورد.")
    print()

    # نمونه نقض: هدفی که از KB نتیجه نمی‌شود (T = سردرد)
    proved_t, _ = pl_resolution(kb, "T")
    print("کنترل منفی: هدف T (سردرد) که در KB نیست => نتیجه KB؟ %s" %
          ("بله" if proved_t else "خیر (بند تهی حاصل نشد)"))
    print()
    return True


def main():
    print("=" * 66)
    print("جلسه ۱۷ — منطق گزاره‌ای و سیستم‌های خبره")
    print("=" * 66)
    print()
    ok = truth_table()
    ok = expert_system_demo() and ok
    ok = resolution_demo() and ok
    assert ok
    print("نتیجه آموزشی:")
    print("- جدول درستی رفتار پنج عملگر پایه را دقیق تعریف می‌کند.")
    print("- استنتاج روبه‌جلو از حقایق شروع می‌کند و قاعده‌ها را روشن می‌کند (Data-driven).")
    print("- مجزا با ردّ، اثبات را به جست‌وجوی تناقض تبدیل می‌کند؛ در این اجرا")
    print("  بند تهی حاصل شد و هدف I اثبات شد، ولی هدف T اثبات نشد.")
    print()
    print("این کد فقط آموزشی است و هیچ کاربرد تشخیصی یا بالینی ندارد.")


if __name__ == "__main__":
    main()
