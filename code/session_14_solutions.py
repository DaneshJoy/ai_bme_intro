# -*- coding: utf-8 -*-
"""جلسه ۱۴ — جلسه حل تمرین ۱: راه‌حل‌های مرجع

تمرین‌های این فایل دقیقاً همان تمرین‌های جلسه ۱۴ هستند و هر تابع، راه‌حل
مرجع یکی از تمرین‌ها است. در پایان، همه‌ی خودآزمون‌ها با assert اجرا می‌شوند؛
اگر همه‌ی مقایسه‌ها درست باشند، «ALL CHECKS PASSED» چاپ می‌شود.

فقط از کتابخانه استاندارد پایتون استفاده می‌شود.
کد آموزشی است و هیچ کاربرد تشخیصی یا بالینی ندارد.
"""

import heapq


# ---------------- تمرین ۱: BFS و DFS روی یک گراف ----------------

def bfs(graph, start, goal):
    """جست‌وجوی عرض اول: کوتاه‌ترین مسیر بر حسب تعداد یال."""
    if start == goal:
        return [start]
    queue = [start]
    visited = {start}
    parent = {start: None}
    while queue:
        node = queue.pop(0)
        for neighbor in sorted(graph.get(node, [])):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = node
                if neighbor == goal:
                    path = []
                    while neighbor is not None:
                        path.append(neighbor)
                        neighbor = parent[neighbor]
                    return path[::-1]
                queue.append(neighbor)
    return None


def dfs(graph, start, goal):
    """جست‌وجوی عمق اول با پشته صریح."""
    stack = [start]
    visited = set()
    parent = {start: None}
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        if node == goal:
            path = []
            while node is not None:
                path.append(node)
                node = parent[node]
            return path[::-1]
        for neighbor in sorted(graph.get(node, []), reverse=True):
            if neighbor not in visited and neighbor not in parent:
                parent[neighbor] = node
                stack.append(neighbor)
    return None


GRAPH_T1 = {
    "S": ["A", "B"],
    "A": ["C", "D"],
    "B": ["D", "E"],
    "C": ["F"],
    "D": ["F"],
    "E": ["F"],
    "F": [],
}


# ---------------- تمرین ۲: UCS و A* روی همان گراف با هزینه ----------------

GRAPH_T2 = {
    "S": [("A", 2), ("B", 5)],
    "A": [("C", 4), ("D", 7)],
    "B": [("D", 3), ("E", 6)],
    "C": [("F", 3)],
    "D": [("F", 2)],
    "E": [("F", 7)],
    "F": [],
}

H_T2 = {"S": 9, "A": 7, "B": 5, "C": 3, "D": 2, "E": 7, "F": 0}


def ucs(graph, start, goal):
    """جست‌وجوی هزینه یکنواخت: صف اولویت بر اساس g."""
    frontier = [(0, start)]
    g_cost = {start: 0}
    parent = {start: None}
    expanded = 0
    while frontier:
        _, node = heapq.heappop(frontier)
        if node == goal:
            path = []
            while node is not None:
                path.append(node)
                node = parent[node]
            return path[::-1], g_cost[goal], expanded
        expanded += 1
        for neighbor, weight in graph.get(node, []):
            new_cost = g_cost[node] + weight
            if new_cost < g_cost.get(neighbor, float("inf")):
                g_cost[neighbor] = new_cost
                parent[neighbor] = node
                heapq.heappush(frontier, (new_cost, neighbor))
    return None, float("inf"), expanded


def a_star(graph, start, goal, h):
    """A*: صف اولویت بر اساس f(n) = g(n) + h(n)."""
    frontier = [(h(start, goal), 0, start)]
    g_cost = {start: 0}
    parent = {start: None}
    expanded = 0
    counter = 0
    while frontier:
        f, _, node = heapq.heappop(frontier)
        if node == goal:
            path = []
            while node is not None:
                path.append(node)
                node = parent[node]
            return path[::-1], g_cost[goal], expanded
        expanded += 1
        for neighbor, weight in graph.get(node, []):
            new_cost = g_cost[node] + weight
            if new_cost < g_cost.get(neighbor, float("inf")):
                g_cost[neighbor] = new_cost
                parent[neighbor] = node
                counter += 1
                heapq.heappush(frontier, (new_cost + h(neighbor, goal), counter, neighbor))
    return None, float("inf"), expanded


def zero_h(node, goal):
    return 0


def h_t2(node, goal):
    return H_T2.get(node, 0)


# ---------------- تمرین ۳: بررسی مجاز بودن هیوریستیک ----------------

def true_costs(graph, goal):
    """هزینه‌ی واقعی کمینه هر گره تا هدف (با Dijkstra) — برای سنجش h*."""
    dist = {goal: 0}
    pq = [(0, goal)]
    while pq:
        d, node = heapq.heappop(pq)
        if d > dist.get(node, float("inf")):
            continue
        for neighbor, weight in graph.get(node, []):
            # یال‌ها را دوطرفه در نظر می‌گیریم تا h* برای همه گره‌ها معنی‌دار باشد
            nd = d + weight
            if nd < dist.get(neighbor, float("inf")):
                dist[neighbor] = nd
                heapq.heappush(pq, (nd, neighbor))
        for src, edges in graph.items():
            for n2, w in edges:
                if n2 == node and d + w < dist.get(src, float("inf")):
                    dist[src] = d + w
                    heapq.heappush(pq, (d + w, src))
    return dist


def check_admissible(graph, goal, h):
    """برای هر گره: آیا h(n) ≤ h*(n) است؟ خروجی: دیکشنری گره -> (h, h*, مجاز؟)"""
    hstar = true_costs(graph, goal)
    result = {}
    for node in {src for src in graph} | {dst for edges in graph.values() for dst, _ in edges}:
        hh = h(node, goal)
        hs = hstar.get(node, float("inf"))
        result[node] = (hh, hs, hh <= hs)
    return result


# ---------------- تمرین ۴: گرادیان کاهشی ----------------

def gradient_descent(lr, n_iters, x0, grad=lambda x: 2 * x):
    """گرادیان کاهشی ساده برای کمینه‌سازی f با گرادیان grad."""
    x = x0
    trajectory = [x0]
    for _ in range(n_iters):
        x = x - lr * grad(x)
        trajectory.append(x)
    return x, trajectory


# ---------------- تمرین ۵: CSP — رنگ‌آمیزی نقشه ----------------

def solve_map_coloring(regions, neighbors, colors):
    """CSP رنگ‌آمیزی نقشه با Backtracking ساده."""
    assignment = {}

    def is_consistent(var, color):
        for other in neighbors.get(var, []):
            if other in assignment and assignment[other] == color:
                return False
        return True

    def backtrack(index):
        if index == len(regions):
            return dict(assignment)
        var = regions[index]
        for color in colors:
            if is_consistent(var, color):
                assignment[var] = color
                result = backtrack(index + 1)
                if result is not None:
                    return result
                del assignment[var]
        return None

    return backtrack(0)


REGIONS_T5 = ["A", "B", "C", "D"]
NEIGHBORS_T5 = {"A": ["B", "C"], "B": ["A", "C", "D"], "C": ["A", "B", "D"], "D": ["B", "C"]}
COLORS_T5 = ["قرمز", "سبز", "آبی"]


# ---------------- تمرین ۶: CSP زمان‌بندی کلاس ----------------

def solve_class_schedule(classes, slots, preferences):
    """CSP زمان‌بندی: هر کلاس یک اسلات می‌گیرد؛ هیچ دو کلاس در یک اسلات نیستند.
    preferences: دیکشنری کلاس -> مجموعه اسلات‌های مجاز.
    """
    assignment = {}

    def is_consistent(cls, slot):
        for other, other_slot in assignment.items():
            if other_slot == slot:
                return False
        return slot in preferences[cls]

    def backtrack(index):
        if index == len(classes):
            return dict(assignment)
        cls = classes[index]
        for slot in slots:
            if is_consistent(cls, slot):
                assignment[cls] = slot
                result = backtrack(index + 1)
                if result is not None:
                    return result
                del assignment[cls]
        return None

    return backtrack(0)


CLASSES_T6 = ["آناتومی", "فیزیولوژی", "بیوشیمی"]
SLOTS_T6 = ["۸ صبح", "۱۰ صبح", "۱۲ ظهر"]
PREFS_T6 = {
    "آناتومی": {"۸ صبح", "۱۰ صبح"},
    "فیزیولوژی": {"۱۰ صبح", "۱۲ ظهر"},
    "بیوشیمی": {"۸ صبح"},
}


# ---------------- تمرین ۷: بررسی سازگاری هیوریستیک (Consistency) ----------------

def check_consistency(graph, goal, h):
    """برای هر یال (u, v): آیا h(u) ≤ w(u,v) + h(v) است؟"""
    result = {}
    for u, edges in graph.items():
        for v, w in edges:
            hu = h(u, goal)
            hv = h(v, goal)
            result[(u, v)] = (hu, w, hv, hu <= w + hv)
    return result


# ---------------- تمرین ۸: جست‌وجوی محلی (Hill Climbing) ----------------

def hill_climbing(x0, step=0.5, n_iters=50, f=lambda x: (x - 3) ** 2):
    """جست‌وجوی محلی برای کمینه‌سازی f(x) = (x-3)^2 با حرکت‌های گسسته."""
    x = x0
    history = [x]
    for _ in range(n_iters):
        candidates = [x + step, x - step]
        f_current = f(x)
        best_x, best_f = x, f_current
        for cx in candidates:
            if f(cx) < best_f:
                best_x, best_f = cx, f(cx)
        if best_x == x:  # بهینه محلی پیدا شد
            break
        x = best_x
        history.append(x)
    return x, f(x), history


# ---------------- تمرین ۹: جست‌وجوی غیرآگاهانه (IDDFS) ----------------

def iddfs(graph, start, goal, max_depth=10):
    """جست‌وجوی عمق‌افزایشی: در هر عمق یک DFS محدود اجرا می‌کند."""
    def dls(node, goal, depth, path):
        if depth == 0:
            return path if node == goal else None
        if node == goal:
            return path
        for neighbor in sorted(graph.get(node, [])):
            if neighbor not in path:
                res = dls(neighbor, goal, depth - 1, path + [neighbor])
                if res is not None:
                    return res
        return None

    for depth in range(1, max_depth + 1):
        res = dls(start, goal, depth, [start])
        if res is not None:
            return res, depth
    return None, max_depth


# ---------------- تمرین ۱۰: نمونه‌سؤال شبیه میان‌ترم ----------------
# ترکیب: جست‌وجو (UCS/A*) + CSP (زمان‌بندی)
# بخش الف: UCS روی گراف T2 (همان گراف تمرین ۲)
# بخش ب: زمان‌بندی سه جراحی در سه بازه با قید یکتایی: یک جراحی در هر بازه

OR_SURGERIES = ["S1", "S2", "S3"]
OR_SLOTS = [1, 2, 3]  # سه بازه زمانی


# ---------------- خودآزمون‌ها با assert ----------------

def run_self_checks():
    # --- تمرین ۱ ---
    path_bfs = bfs(GRAPH_T1, "S", "F")
    assert path_bfs == ["S", "A", "C", "F"], "مسیر BFS نادرست: %s" % path_bfs
    assert len(path_bfs) == 4, "طول مسیر BFS باید 4 باشد"
    path_dfs = dfs(GRAPH_T1, "S", "F")
    assert path_dfs is not None, "DFS مسیر پیدا نکرد"
    assert path_dfs[0] == "S" and path_dfs[-1] == "F", "مسیر DFS از شروع به هدف نمی‌رسد"
    print("تمرین ۱ (BFS/DFS)  : BFS =", " -> ".join(path_bfs), "| DFS =", " -> ".join(path_dfs))

    # --- تمرین ۲ ---
    ucs_path, ucs_cost, ucs_exp = ucs(GRAPH_T2, "S", "F")
    assert ucs_path == ["S", "A", "C", "F"], "مسیر UCS نادرست: %s" % ucs_path
    assert ucs_cost == 9, "هزینه UCS باید 9 باشد، ولی %s است" % ucs_cost
    astar_path, astar_cost, astar_exp = a_star(GRAPH_T2, "S", "F", h_t2)
    assert astar_path == ucs_path, "A* باید مسیر بهینه UCS را بدهد"
    assert astar_cost == 9, "هزینه A* باید 9 باشد، ولی %s است" % astar_cost
    print("تمرین ۲ (UCS/A*)   : مسیر =", " -> ".join(ucs_path),
          "| هزینه =", ucs_cost, "| گره‌های بسط UCS =", ucs_exp, "| A* =", astar_exp)

    # --- تمرین ۳ ---
    adm = check_admissible(GRAPH_T2, "F", h_t2)
    assert all(ok for _, _, ok in adm.values()), "هیوریستیک h_t2 باید مجاز باشد"
    assert adm["S"][0] <= adm["S"][1], "h(S) باید ≤ h*(S) باشد"
    print("تمرین ۳ (مجاز بودن): همه گره‌ها h(n) ≤ h*(n) → هیوریستیک مجاز",
          "| h(S)=%d, h*(S)=%d" % (adm["S"][0], adm["S"][1]))

    # --- تمرین ۴ ---
    x_final, traj = gradient_descent(lr=0.1, n_iters=20, x0=5.0)
    assert abs(x_final) < 0.1, "گرادیان کاهشی باید به نزدیک صفر همگرا شود، ولی %s است" % x_final
    assert len(traj) == 21, "مسیر باید 21 نقطه داشته باشد (شروع + 20 گام)"
    print("تمرین ۴ (Gradient) : x نهایی = %.6f" % x_final)

    # --- تمرین ۵ ---
    coloring = solve_map_coloring(REGIONS_T5, NEIGHBORS_T5, COLORS_T5)
    assert coloring is not None, "رنگ‌آمیزی شکست خورد"
    for region, nb_list in NEIGHBORS_T5.items():
        for nb in nb_list:
            assert coloring[region] != coloring[nb], "همسایه‌های %s و %s هم‌رنگ شدند" % (region, nb)
    assert len(set(coloring.values())) <= len(COLORS_T5)
    print("تمرین ۵ (رنگ‌آمیزی): ", coloring)

    # --- تمرین ۶ ---
    schedule = solve_class_schedule(CLASSES_T6, SLOTS_T6, PREFS_T6)
    assert schedule is not None, "زمان‌بندی کلاس شکست خورد"
    assert len(set(schedule.values())) == len(CLASSES_T6), "دو کلاس در یک اسلات قرار گرفتند"
    for cls, slot in schedule.items():
        assert slot in PREFS_T6[cls], "کلاس %s در اسلات غیرمجاز قرار گرفت" % cls
    print("تمرین ۶ (زمان‌بندی): ", schedule)

    # --- تمرین ۷ ---
    cons = check_consistency(GRAPH_T2, "F", h_t2)
    assert all(ok for _, _, _, ok in cons.values()), "هیوریستیک h_t2 باید سازگار باشد"
    print("تمرین ۷ (سازگاری): همه یال‌ها h(u) ≤ w(u,v) + h(v) → سازگار")

    # --- تمرین ۸ ---
    x_opt, f_opt, hist = hill_climbing(x0=0.0, step=0.5, n_iters=50)
    assert abs(x_opt - 3.0) < 0.5, "Hill Climbing باید به نزدیک 3 همگرا شود، ولی %s است" % x_opt
    print("تمرین ۸ (Hill Climbing): x نهایی = %.4f | f = %.4f | تعداد گام = %d"
          % (x_opt, f_opt, len(hist) - 1))

    # --- تمرین ۹ ---
    path_iddfs, depth = iddfs(GRAPH_T1, "S", "F", max_depth=10)
    assert path_iddfs == ["S", "A", "C", "F"], "مسیر IDDFS نادرست: %s" % path_iddfs
    assert depth == 3, "عمق IDDFS باید ۳ باشد، ولی %s است" % depth
    print("تمرین ۹ (IDDFS)   : مسیر =", " -> ".join(path_iddfs), "| عمق =", depth)

    # --- تمرین ۱۰ ---
    # بخش الف: UCS (همان تمرین ۲)
    assert ucs_cost == 9 and ucs_path == ["S", "A", "C", "F"], "UCS در میان‌ترم ناموفق"
    # بخش ب: CSP زمان‌بندی سه جراحی در سه بازه؛ قید سخت: هر بازه فقط یک جراحی
    or_sched = solve_class_schedule(OR_SURGERIES, OR_SLOTS, {s: set(OR_SLOTS) for s in OR_SURGERIES})
    assert or_sched is not None, "زمان‌بندی بازه‌ها شکست خورد"
    assert len(set(or_sched.values())) == len(OR_SURGERIES), "دو جراحی در یک بازه قرار گرفتند"
    print("تمرین ۱۰ (میان‌ترم): UCS هزینه = 9 | CSP زمان‌بندی =", or_sched)

    print()
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    print("=" * 50)
    print("جلسه ۱۴ — جلسه حل تمرین ۱: راه‌حل‌های مرجع")
    print("=" * 50)
    print()
    run_self_checks()
