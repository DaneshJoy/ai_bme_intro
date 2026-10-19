# -*- coding: utf-8 -*-
"""جلسه ۵ — BFS و DFS روی شبکه انتقال بیمار بین بخش‌های بیمارستان.

فقط کتابخانه استاندارد پایتون (collections.deque).
وزن هر یال = زمان انتقال بیمار به دقیقه (داده فرضی و صرفاً آموزشی).
"""

from collections import deque

# گراف شبکه انتقال بیمار (بی‌جهت، وزن‌دار)
GRAPH = {
    "ER":     [("RAD", 4), ("LAB", 2), ("PHARM", 1)],
    "PHARM":  [("ER", 1)],
    "RAD":    [("ER", 4), ("ICU", 5), ("LAB", 3)],
    "LAB":    [("ER", 2), ("RAD", 3), ("OR", 2)],
    "OR":     [("LAB", 2), ("ICU", 1)],
    "ICU":    [("RAD", 5), ("OR", 1), ("WARD_B", 2)],
    "WARD_B": [("ICU", 2)],
}

FA = {
    "ER": "اورژانس", "RAD": "تصویربرداری", "LAB": "آزمایشگاه",
    "OR": "اتاق عمل", "ICU": "مراقبت ویژه", "WARD_B": "بخش بستری B",
    "PHARM": "داروخانه",
}


def reconstruct_path(came_from, goal):
    """بازسازی مسیر از دیکشنری والد‌ها."""
    node, path = goal, []
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return path


def path_cost(graph, path):
    """جمع وزن یال‌های مسیر (زمان انتقال)."""
    cost = 0
    for u, v in zip(path, path[1:]):
        cost += dict(graph[u])[v]
    return cost


def bfs(graph, start, goal):
    """جست‌وجوی سطح‌اول: صف FIFO، کمترین تعداد گام را می‌یابد."""
    frontier = deque([start])
    came_from = {start: None}
    expansions = 0
    while frontier:
        node = frontier.popleft()
        expansions += 1
        if node == goal:
            return reconstruct_path(came_from, goal), expansions
        for nbr, _w in graph.get(node, []):
            if nbr not in came_from:
                came_from[nbr] = node
                frontier.append(nbr)
    return None, expansions


def dfs(graph, start, goal):
    """جست‌وجوی عمق‌اول: پشته LIFO، یک شاخه را تا انتها می‌رود."""
    stack = [start]
    came_from = {start: None}
    expansions = 0
    while stack:
        node = stack.pop()
        expansions += 1
        if node == goal:
            return reconstruct_path(came_from, goal), expansions
        for nbr, _w in graph.get(node, []):
            if nbr not in came_from:
                came_from[nbr] = node
                stack.append(nbr)
    return None, expansions


def describe(title, path, expansions):
    if path is None:
        print(title, ": مسیری یافت نشد")
        return
    print(title, ":")
    print("  مسیر :", " -> ".join(path))
    print("  تعداد گام :", len(path) - 1)
    print("  هزینه مسیر (دقیقه) :", path_cost(GRAPH, path))
    print("  گره‌های بسط‌داده‌شده :", expansions)


def main():
    start, goal = "ER", "WARD_B"
    print("مسئله: انتقال بیمار از", FA[start], "به", FA[goal])
    print("-" * 40)

    path, exp = bfs(GRAPH, start, goal)
    describe("BFS", path, exp)
    print("-" * 40)

    path, exp = dfs(GRAPH, start, goal)
    describe("DFS", path, exp)
    print("-" * 40)

    print("نکته: BFS کمترین تعداد گام را می‌یابد ولی وزن‌ها را نمی‌بیند.")
    print("DFS به ترتیب همسایه‌ها وابسته است و هیچ تضمینی برای مسیر بهینه ندارد.")
    print("BFS و DFS فقط از وجود یال استفاده می‌کنند؛ وزن‌ها فقط در محاسبه هزینه مسیر به‌کار رفتند.")


if __name__ == "__main__":
    main()
