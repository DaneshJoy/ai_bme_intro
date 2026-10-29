# -*- coding: utf-8 -*-
"""جلسه ۶ — UCS و IDDFS روی شبکه انتقال بیمار، با مقایسه BFS.

فقط کتابخانه استاندارد پایتون (heapq).
وزن هر یال = زمان انتقال بیمار به دقیقه (داده فرضی و صرفاً آموزشی).
"""

import heapq

# همان گراف جلسه ۵ (بی‌جهت، وزن‌دار)
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
    node, path = goal, []
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return path


def path_cost(graph, path):
    cost = 0
    for u, v in zip(path, path[1:]):
        cost += dict(graph[u])[v]
    return cost


def bfs(graph, start, goal):
    """جست‌وجوی سطح‌اول: صف FIFO، کمترین تعداد گام را می‌یابد."""
    frontier = [start]
    came_from = {start: None}
    expansions = 0
    while frontier:
        node = frontier.pop(0)
        expansions += 1
        if node == goal:
            return reconstruct_path(came_from, goal), expansions
        for nbr, _w in graph.get(node, []):
            if nbr not in came_from:
                came_from[nbr] = node
                frontier.append(nbr)
    return None, expansions


def ucs(graph, start, goal):
    """جست‌وجوی هزینه یکنواخت: صف اولویت با heapq، کمترین هزینه را می‌یابد."""
    frontier = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    expansions = 0
    while frontier:
        cost, node = heapq.heappop(frontier)
        if cost > cost_so_far.get(node, float("inf")):
            continue  # ورودی قدیمی و غیربهینه در صف
        expansions += 1
        if node == goal:
            return reconstruct_path(came_from, goal), cost, expansions
        for nbr, w in graph.get(node, []):
            new_cost = cost + w
            if new_cost < cost_so_far.get(nbr, float("inf")):
                cost_so_far[nbr] = new_cost
                came_from[nbr] = node
                heapq.heappush(frontier, (new_cost, nbr))
    return None, float("inf"), expansions


def dls(graph, node, goal, depth, path, counter):
    """جست‌وجوی محدود به عمق (بازگشتی). counter برای شمارش بسط‌ها."""
    counter[0] += 1
    if node == goal:
        return path + [node]
    if depth == 0:
        return None
    for nbr, _w in graph.get(node, []):
        if nbr not in path:  # جلوگیری از چرخه در همان شاخه
            result = dls(graph, nbr, goal, depth - 1, path + [node], counter)
            if result is not None:
                return result
    return None


def iddfs(graph, start, goal, max_depth=10):
    """تکثیر عمق: اجرای مکرر جست‌وجوی محدود با عمق صفر تا max_depth."""
    counter = [0]
    for depth in range(max_depth + 1):
        result = dls(graph, start, goal, depth, [], counter)
        if result is not None:
            return result, counter[0]
    return None, counter[0]


def main():
    start, goal = "ER", "WARD_B"
    print("مسئله: انتقال بیمار از", FA[start], "به", FA[goal])
    print("-" * 40)

    path, cost, exp = ucs(GRAPH, start, goal)
    if path is None:
        print("UCS : مسیری یافت نشد")
    else:
        print("UCS :")
        print("  مسیر :", " -> ".join(path))
        print("  هزینه نهایی (دقیقه) :", cost)
        print("  گره‌های بسط‌داده‌شده :", exp)
    print("-" * 40)

    path, exp = iddfs(GRAPH, start, goal)
    if path is None:
        print("IDDFS : مسیری یافت نشد")
    else:
        print("IDDFS :")
        print("  مسیر :", " -> ".join(path))
        print("  تعداد گام :", len(path) - 1)
        print("  هزینه مسیر (دقیقه) :", path_cost(GRAPH, path))
        print("  گره‌های بسط‌داده‌شده :", exp)
    print("-" * 40)

    path, exp = bfs(GRAPH, start, goal)
    if path is None:
        print("BFS : مسیری یافت نشد")
    else:
        print("BFS :")
        print("  مسیر :", " -> ".join(path))
        print("  تعداد گام :", len(path) - 1)
        print("  هزینه مسیر (دقیقه) :", path_cost(GRAPH, path))
        print("  گره‌های بسط‌داده‌شده :", exp)
    print("-" * 40)

    print("نتیجه: UCS کمترین هزینه را تضمین می‌کند؛ BFS و IDDFS کمترین تعداد گام را.")
    print("IDDFS حافظه‌ی کم مصرف می‌کند ولی گره‌ها را چند بار بسط می‌دهد.")


if __name__ == "__main__":
    main()
