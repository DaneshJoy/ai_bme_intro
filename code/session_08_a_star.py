# -*- coding: utf-8 -*-
"""جلسه ۸ — الگوریتم A* (A-star) و مقایسه آن با UCS

سناریوی آموزشی: همان شبکه راهروهای طبقه بیمارستان جلسه ۷ (شبکه ۵×۵)
- هر خانه یک تقاطع/اتاق است و حرکت به چهار همسایه هزینه ۱ دارد.
- خانه‌های «#» به‌خاطر تعمیرات بسته‌اند: ستون ۱ در ردیف‌های ۰ تا ۲ و اتاق‌های (3,3) و (4,3).
- هدف: مسیر بهینه از اورژانس (0,0) تا اتاق عمل (4,4).

این اسکریپت سه کار می‌کند:
1) A* را با heapq پیاده‌سازی می‌کند و مسیر بهینه را چاپ می‌کند.
2) بهینگی را به‌صورت عملی بررسی می‌کند: هزینه A* با هیوریستیک مجاز برابر
   هزینه UCS (جست‌وجوی هزینه یکنواخت) درمی‌آید.
3) تعداد گره‌های بسط‌یافته UCS و A* را با چند هیوریستیک مقایسه می‌کند.

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

def a_star(graph, start, goal, h):
    """جست‌وجوی A* با صف اولویت بر اساس f(n) = g(n) + h(n).

    خروجی: (مسیر، هزینه مسیر، تعداد گره‌های بسط‌یافته، ترتیب بسط)
    """
    counter = 0                       # شکستن تساوی‌ها برای ترتیب پایدار
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
                heapq.heappush(frontier, (ng + h(v, goal), counter, v))
    return None, float("inf"), expanded, order


def ucs(graph, start, goal):
    """جست‌وجوی هزینه یکنواخت: همان A* با هیوریستیک صفر."""
    return a_star(graph, start, goal, zero)


def path_str(path):
    return " -> ".join("(%d,%d)" % p for p in path)


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

    print("نتیجه آموزشی:")
    print("- A* با هیوریستیک مجاز همان هزینه بهینه UCS را داد اما گره کمتری بسط داد (14 در برابر 20).")
    print("- UCS حالت خاص A* با h=0 است؛ هرچه h دقیق‌تر و مجازتر باشد، جست‌وجو هدفمندتر می‌شود.")
    print("- هیوریستیک غیرمجاز (2xManhattan) تضمین بهینگی را از بین می‌برد؛ در این اجرا")
    print("  اتفاقی مسیر بهینه پیدا شد، اما روی این قابل حساب نیست.")
    print()
    print("این کد فقط آموزشی است و هیچ کاربرد تشخیصی یا بالینی ندارد.")


if __name__ == "__main__":
    main()
