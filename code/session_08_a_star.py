# -*- coding: utf-8 -*-
"""جلسه ۸ — الگوریتم A* (A-star) و مقایسه آن با UCS

سناریوی آموزشی: همان شبکه راهروهای طبقه بیمارستان جلسه ۷ (شبکه ۵×۵)
- هر خانه یک تقاطع/اتاق است و حرکت به چهار همسایه هزینه ۱ دارد.
- خانه‌های «#» به‌خاطر تعمیرات بسته‌اند: ستون ۱ در ردیف‌های ۰ تا ۲ و اتاق‌های (3,3) و (4,3).
- هدف: مسیر بهینه از اورژانس (0,0) تا اتاق عمل (4,4).

این اسکریپت شش کار می‌کند (گام‌ها با بخش‌های جزوه هماهنگ‌اند):
1) مجاز بودن و ثبات هیوریستیک‌ها را بررسی می‌کند.
2) A* را با heapq پیاده‌سازی می‌کند و مسیر بهینه را چاپ می‌کند.
3) بهینگی را عملی بررسی می‌کند: هزینه A* برابر هزینه UCS درمی‌آید.
4) تعداد گره‌های بسط‌یافته UCS و A* را با چند هیوریستیک مقایسه می‌کند.
5) جدول گام‌به‌گام A* روی شبکه را چاپ می‌کند (جدول بخش ۵ جزوه).
6) گراف کوچک بخش ۴ جزوه را با A*، UCS و Greedy اجرا می‌کند و اثر
   هیوریستیک غیرمجاز h(C)=6 را نشان می‌دهد.

فقط از کتابخانه استاندارد پایتون (heapq) استفاده می‌شود.
کد آموزشی است و هیچ کاربرد تشخیصی یا بالینی ندارد.
"""

import heapq

# ---------------- گراف: طبقه بیمارستان (همان جلسه ۷) ----------------

N = 5
START = (0, 0)             # اورژانس
GOAL = (4, 4)              # اتاق عمل
BLOCKED = {(0, 1), (1, 1), (2, 1), (3, 3), (4, 3)}

EPS = 1e-9


def build_graph():
    """ساخت گراف به‌صورت دیکشنری: گره -> فهرست (همسایه، هزینه)."""
    graph = {}
    for r in range(N):
        for c in range(N):
            node = (r, c)
            if node in BLOCKED:
                continue
            edges = []
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nxt = (r + dr, c + dc)
                if 0 <= nxt[0] < N and 0 <= nxt[1] < N and nxt not in BLOCKED:
                    edges.append((nxt, 1))
            graph[node] = edges
    return graph


def all_nodes(graph):
    return sorted(graph)


def print_map():
    print("      c0  c1  c2  c3  c4")
    for r in range(N):
        cells = []
        for c in range(N):
            node = (r, c)
            if node == START:
                cells.append(" S ")
            elif node == GOAL:
                cells.append(" G ")
            elif node in BLOCKED:
                cells.append(" # ")
            else:
                cells.append(" . ")
        print("r%d  %s" % (r, "".join(cells)))
    print()


# ---------------- توابع ابتکاری ----------------

def manhattan(a, b):
    """فاصله منهتن: جمع قدرمطلق اختلاف مختصات؛ روی این گراف مجاز و ثابت است."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidean(a, b):
    """فاصله اقلیدسی (خط مستقیم)."""
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def manhattan_x2(a, b):
    """دو برابر منهتن: عمداً بیش‌برآورد می‌کند (غیرمجاز) تا نقش مجاز بودن نشان داده شود."""
    return 2 * manhattan(a, b)


def zero(a, b):
    """هیوریستیک صفر: A* با h=0 دقیقاً همان UCS است."""
    return 0


HEURISTICS = [
    ("UCS", "h=0", zero),
    ("A*", "Manhattan", manhattan),
    ("A*", "Euclidean", euclidean),
    ("A*", "2xManhattan", manhattan_x2),
]


def fmt(x):
    if abs(x - round(x)) < EPS:
        return "%d" % round(x)
    return "%.2f" % x


# ---------------- h*: هزینه واقعی کمینه تا هدف (Dijkstra) ----------------

def true_costs(graph, goal):
    dist = {goal: 0}
    pq = [(0, goal)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, float("inf")):
            continue
        for v, w in graph[u]:
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist


# ---------------- A* ----------------

def a_star(graph, start, goal, h, trace=None, use_g=True):
    """جست‌وجوی A* با صف اولویت بر اساس f(n) = g(n) + h(n).

    trace: اگر فهرستی داده شود، هر گام (گره خارج‌شده و گره‌های تولیدشده) در آن ثبت می‌شود.
    use_g=False یعنی فقط بر اساس h مرتب شود (Greedy؛ فقط برای مقایسه آموزشی).

    خروجی: (مسیر، هزینه مسیر، تعداد گره‌های بسط‌یافته، ترتیب بسط)
    """
    counter = 0                       # شکستن تساوی‌ها: اول‌ورود، اول‌خروج
    g_cost = {start: 0}
    parent = {start: None}
    closed = set()
    frontier = [(h(start, goal), counter, start)]
    expanded = 0
    order = []
    while frontier:
        f, _, u = heapq.heappop(frontier)
        if u in closed:
            continue                  # نسخه کهنه‌تر این گره قبلاً بسط یافته است
        closed.add(u)
        expanded += 1
        order.append(u)
        step = None
        if trace is not None:
            step = {"node": u, "g": g_cost[u], "h": h(u, goal), "new": []}
            trace.append(step)
        if u == goal:
            path = []
            while u is not None:
                path.append(u)
                u = parent[u]
            return path[::-1], g_cost[goal], expanded, order
        for v, w in graph[u]:
            ng = g_cost[u] + w
            if ng < g_cost.get(v, float("inf")):
                g_cost[v] = ng
                parent[v] = u
                counter += 1
                prio = (ng if use_g else 0) + h(v, goal)
                heapq.heappush(frontier, (prio, counter, v))
                if step is not None:
                    step["new"].append((v, ng, h(v, goal)))
    return None, float("inf"), expanded, order


def ucs(graph, start, goal):
    """جست‌وجوی هزینه یکنواخت: همان A* با هیوریستیک صفر."""
    return a_star(graph, start, goal, zero)


def path_str(path):
    return " -> ".join("(%d,%d)" % p for p in path)


def print_trace(trace, name=lambda n: "(%d,%d)" % n):
    """چاپ جدول گام‌به‌گام: گره خارج‌شده (g,h,f) و گره‌های تولیدشده."""
    print("  گام  خارج‌شده (g,h,f)          تولیدشده (g,h,f)")
    for i, s in enumerate(trace, 1):
        out = "%s (%s,%s,%s)" % (name(s["node"]), fmt(s["g"]), fmt(s["h"]), fmt(s["g"] + s["h"]))
        new = "، ".join("%s (%s,%s,%s)" % (name(v), fmt(g), fmt(hv), fmt(g + hv))
                        for v, g, hv in s["new"]) or "-"
        print("  %-4d %-26s %s" % (i, out, new))


# ---------------- گراف کوچک بخش ۴ جزوه ----------------

SMALL_EDGES = [("S", "A", 1), ("S", "B", 4), ("S", "E", 2), ("A", "C", 2),
               ("A", "D", 5), ("B", "G", 6), ("C", "G", 4), ("D", "G", 2)]
SMALL_H = {"S": 5, "A": 4, "B": 2, "C": 2, "D": 2, "E": 7, "G": 0}


def small_graph():
    graph = {}
    for a, b, w in SMALL_EDGES:
        graph.setdefault(a, []).append((b, w))
        graph.setdefault(b, []).append((a, w))
    return graph


def small_demo():
    graph = small_graph()
    h_ok = lambda n, g: SMALL_H[n]
    bad = dict(SMALL_H)
    bad["C"] = 6                      # بیش‌برآورد: h*(C) = 4
    h_bad = lambda n, g: bad[n]
    zero_h = lambda n, g: 0
    hstar = true_costs(graph, "G")

    print("  h*(n) :", " ".join("%s=%s" % (n, hstar[n]) for n in sorted(graph)))
    print("  h(n)  :", " ".join("%s=%s" % (n, SMALL_H[n]) for n in sorted(graph)))
    print()
    print("  اجرای A* گام‌به‌گام (h مجاز):")
    trace = []
    a_star(graph, "S", "G", h_ok, trace=trace)
    print_trace(trace, name=lambda n: n)
    print()
    print("  %-22s %-14s %5s %9s" % ("الگوریتم", "مسیر", "هزینه", "بسط"))
    print("  " + "-" * 54)
    rows = [("UCS (h=0)", zero_h, True), ("Greedy (فقط h)", h_ok, False),
            ("A* با h مجاز", h_ok, True), ("A* با h(C)=6 غیرمجاز", h_bad, True)]
    for title, h, use_g in rows:
        p, c, e, _ = a_star(graph, "S", "G", h, use_g=use_g)
        print("  %-22s %-14s %5s %9d" % (title, "->".join(p), fmt(c), e))
    print()


def main():
    print("=" * 66)
    print("جلسه ۸ — الگوریتم A* و مقایسه با UCS")
    print("=" * 66)
    print_map()

    graph = build_graph()
    hstar = true_costs(graph, GOAL)

    # --- گام ۱: بررسی مجاز بودن و ثبات هیوریستیک‌ها ---
    print("گام ۱: بررسی مجاز بودن (Admissible) و ثبات (Consistent) هیوریستیک‌ها")
    for _, name, h in HEURISTICS[1:]:
        worst = max(h(n, GOAL) - hstar[n] for n in all_nodes(graph))
        admissible = worst <= EPS
        consistent = all(h(u, GOAL) <= w + h(v, GOAL) + EPS
                         for u in all_nodes(graph) for v, w in graph[u])
        print("  %-15s بیشینه h(n) - h*(n) = %5.2f  ->  مجاز: %s   ثابت: %s"
              % (name, worst, "بله" if admissible else "خیر", "بله" if consistent else "خیر"))
    print()

    # --- گام ۲: اجرای A* با هیوریستیک مجاز Manhattan ---
    print("گام ۲: اجرای A* با هیوریستیک Manhattan (مجاز و ثابت)")
    path, cost, expanded, order = a_star(graph, START, GOAL, manhattan)
    print("  مسیر بهینه :", path_str(path))
    print("  هزینه مسیر :", fmt(cost))
    print("  گره‌های بسط‌یافته :", expanded)
    print("  ترتیب بسط  :", " ".join("(%d,%d)" % p for p in order))
    print()

    # --- گام ۳: اثبات عملی بهینگی با مقایسه هزینه با UCS ---
    print("گام ۳: اثبات عملی بهینگی — مقایسه هزینه A* با هزینه UCS")
    ucs_path, ucs_cost, ucs_expanded, _ = ucs(graph, START, GOAL)
    print("  هزینه UCS (مسیر بهینه مرجع): %s" % fmt(ucs_cost))
    print("  هزینه A* با Manhattan      : %s" % fmt(cost))
    if cost == ucs_cost:
        print("  نتیجه: هزینه A* برابر هزینه بهینه UCS است -> A* با h مجاز بهینه عمل کرد.")
    else:
        print("  نتیجه: هزینه A* با هزینه بهینه برابر نیست!")
    print()

    # --- گام ۴: جدول مقایسه تعداد گره‌های بسط‌یافته ---
    print("گام ۴: مقایسه الگوریتم‌ها روی همین شبکه")
    print("%-8s %-12s %6s %10s %9s" % ("algo", "heuristic", "cost", "expanded", "optimal?"))
    print("-" * 60)
    for algo, name, h in HEURISTICS:
        p, c, e, _ = a_star(graph, START, GOAL, h)
        optimal = "بله" if c == ucs_cost else "خیر"
        note = ""
        if name == "2xManhattan":
            note = "  (شانس آورد؛ تضمینی نیست)"
        print("%-8s %-12s %6s %10d %9s%s" % (algo, name, fmt(c), e, optimal, note))
    print()

    # --- گام ۵: جدول گام‌به‌گام A* روی شبکه (بخش ۵ جزوه) ---
    print("گام ۵: ردیابی گام‌به‌گام A* با Manhattan (جدول بخش ۵ جزوه)")
    trace = []
    a_star(graph, START, GOAL, manhattan, trace=trace)
    print_trace(trace)
    print()

    # --- گام ۶: گراف کوچک بخش ۴ جزوه ---
    print("گام ۶: گراف کوچک بخش ۴ جزوه (A* و UCS و Greedy، و اثر h غیرمجاز)")
    small_demo()

    print("نتیجه آموزشی:")
    print("- A* با هیوریستیک مجاز همان هزینه بهینه UCS را داد اما گره کمتری بسط داد (14 در برابر 20).")
    print("- UCS حالت خاص A* با h=0 است؛ هرچه h دقیق‌تر و مجازتر باشد، جست‌وجو هدفمندتر می‌شود.")
    print("- هیوریستیک غیرمجاز (2xManhattan) تضمین بهینگی را از بین می‌برد؛ در این اجرا")
    print("  اتفاقی مسیر بهینه پیدا شد، اما روی این قابل حساب نیست.")
    print("- در گراف کوچک، h(C)=6 (بیش‌برآورد) A* را به مسیر هزینه 8 به‌جای 7 کشاند.")
    print()
    print("این کد فقط آموزشی است و هیچ کاربرد تشخیصی یا بالینی ندارد.")


if __name__ == "__main__":
    main()
