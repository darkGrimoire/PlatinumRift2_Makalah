import sys
import math
import heapq
import time
import random
from collections import deque

""" SETUP PHASE """
PLAYER_COUNT, MY_ID, ZONE_COUNT, LINK_COUNT = [int(i) for i in input().split()]
ENEMY_ID = (MY_ID+1)%2
for i in range(ZONE_COUNT):
    ZONE_ID, PLATINUM_SOURCE = [int(j) for j in input().split()]

""" mengubah list of edges menjadi adjacency lists """
adj_map = {}
for i in range(LINK_COUNT):
    ZONE_1, ZONE_2 = [int(j) for j in input().split()]
    adj_map.setdefault(ZONE_1, []).append(ZONE_2)
    adj_map.setdefault(ZONE_2, []).append(ZONE_1)

MY_BASE = -1
ENEMY_BASE = -1
MY_PODS = 1
ENEMY_PODS = 2
AT = 0
COUNTER = -1
TURN = 0

""" UTILITIES """
class Node():
    """ Kelas untuk melakukan pathfinding, yang akan menyimpan simpul
        sebelumnya dari suatu simpul beserta nilainya.
    """ 
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0
    
    def __eq__(self, other):
        return self.position == other.position

class PriorityQueue:
    """ Kelas sebagai implementasi dari PriorityQueue maxHeap dengan menggunakan
        library heapq pada python
    """
    def __init__(self):
        self.pq = []
        heapq.heapify(self.pq)
        self.count = 0

    def enqueue(self, item, priority=0):
        """ Memasukkan sesuatu ke dalam priority queue. -1 digunakan untuk
            membalik default dari heapq yaitu minHeap agar menjadi maxHeap
        """
        self.count += 1
        entry = [-1*priority, self.count, item]
        heapq.heappush(self.pq, entry)

    def dequeue(self):
        """ Mengeluarkan sesuatu dari priority queue. """
        if len(self.pq) > 0:
            priority, count, item = heapq.heappop(self.pq)
            return item
        else:
            print("Priority Queue is Empty!", file=sys.stderr)
    
    def isEmpty(self):
        """ Mengecek apakah priority queue kosong. """
        return len(self.pq) == 0
    
    def printPQ(self):
        """ Melihat isi dari priority queue. """
        pq = self.pq.copy()
        while len(pq) > 0:
            priority, count, item = heapq.heappop(pq)
            print(f'{priority}:\n"{item}"')
    

""" GAME MECHANICS """
def reconstruct_path(node: Node, branch_raised: int, path: list):
    """ Mengkonstruksi kembali jalur yang dilewati dari node yang telah sampai pada finish. """
    if node.parent is None:
        # print(f"Branch raised: {branch_raised}", file=sys.stderr) # LOGGING PURPOSE
        # print("Path: ", end="", file=sys.stderr) # LOGGING PURPOSE
        return
    path.append(node.position)
    reconstruct_path(node.parent, branch_raised, path)
    # print(f"{node.position} ", end="", file=sys.stderr) # LOGGING PURPOSE

def calculatePathBFS(source: int, target: int):
    """ Mendapatkan jalur terpendek dari source dengan menggunakan algoritma BFS """
    branch_raised = 0
    queue = deque()
    visited = []
    start_node = Node(None, source)
    finish_node = Node(None, target)
    queue.append(start_node)
    while queue:
        cur_node = queue.popleft()
        visited.append(cur_node.position)
        for child_pos in adj_map[cur_node.position]:
            if child_pos in visited:
                continue
            visited.append(child_pos)
            child_node = Node(cur_node, child_pos)
            child_node.g = cur_node.g+1
            child_node.f = child_node.g + child_node.h
            queue.append(child_node)
            branch_raised += 1
            if child_node == finish_node:
                result = []
                reconstruct_path(child_node, branch_raised, result)
                result.append(source)
                return result[::-1]

def calculatePathMSBFS(source: list, target: int) -> dict:
    """ Mendapatkan jalur terpendek dari source dengan menggunakan algoritma Multi-source BFS (MS-BFS) """
    branch_raised = 0
    results = {}
    queue = deque()
    visited = []
    start_nodes = [Node(None, x) for x in source]
    finish_node = Node(None, target)
    queue.append(finish_node)
    while queue:
        cur_node = queue.popleft()
        visited.append(cur_node.position)
        for child_pos in adj_map[cur_node.position]:
            if child_pos in visited:
                continue
            visited.append(child_pos)
            child_node = Node(cur_node, child_pos)
            child_node.g = cur_node.g+1
            child_node.f = child_node.g + child_node.h
            queue.append(child_node)
            branch_raised += 1
            if child_node in start_nodes:
                src = next(x.position for x in start_nodes if x == child_node)
                start_nodes.remove(child_node)
                path = []
                reconstruct_path(child_node, branch_raised, path)
                path.append(target)
                results.setdefault(src, []).extend(path)
        if start_nodes == []:
            break
    print(f"Branch raised: {branch_raised}", end="",file=sys.stderr) # LOGGING PURPOSE
    return results

def invadeEnemyBaseGuerilla(attackers: list, enemy_zone):
    """ Strategi menggerakkan seluruh PODs pada arena menuju markas lawan
        dengan pencarian jalur terpendek menggunakan algoritma BFS
    """
    path = []
    for attacker in attackers:
        if attacker[MY_PODS] == 0:
            continue
        if path == []:
            path = calculatePathBFS(attacker[AT], ENEMY_BASE)
        else:
            if attacker[AT] not in path:
                path = calculatePathBFS(attacker[AT], ENEMY_BASE)
        if attacker[ENEMY_PODS] > 0:
            #find a way to retreat
            if attacker[AT] != ENEMY_BASE and attacker[AT] != path[-1] and path[path.index(attacker[AT])+1] not in enemy_zone:
                flee_node = path[path.index(attacker[AT])+1]
            else:
                for x in adj_map[attacker[AT]]:
                    if x not in enemy_zone:
                        flee_node = x
                        break
                else:
                    flee_node = attacker[AT]
            if attacker[MY_PODS]-attacker[ENEMY_PODS] > 0:
                print(f"{attacker[MY_PODS]-attacker[ENEMY_PODS]} {attacker[AT]} {flee_node} ", end="")
        if attacker[AT] != ENEMY_BASE and attacker[AT] != path[-1]:
            print(f"{attacker[MY_PODS]} {attacker[AT]} {path[path.index(attacker[AT])+1]} ", end="")

def invadeEnemyBaseGuerillaMSBFS(attackers: list, enemy_zone):
    """ Strategi menggerakkan seluruh PODs pada arena menuju markas lawan
        dengan pencarian jalur terpendek menggunakan algoritma MS-BFS
    """
    attackers_pos = [x[AT] for x in attackers]
    path = calculatePathMSBFS(attackers_pos, ENEMY_BASE)
    for attacker in attackers:
        if attacker[MY_PODS] == 0:
            continue
        if attacker[ENEMY_PODS] > 0:
            #find a way to retreat
            if attacker[AT] != ENEMY_BASE and attacker[AT] != path[attacker[AT]][-1] and path[attacker[AT]][path[attacker[AT]].index(attacker[AT])+1] not in enemy_zone:
                flee_node = path[attacker[AT]][path[attacker[AT]].index(attacker[AT])+1]
            else:
                for x in adj_map[attacker[AT]]:
                    if x not in enemy_zone:
                        flee_node = x
                        break
                else:
                    flee_node = attacker[AT]
            if attacker[MY_PODS]-attacker[ENEMY_PODS] > 0:
                print(f"{attacker[MY_PODS]-attacker[ENEMY_PODS]} {attacker[AT]} {flee_node} ", end="")
        if attacker[AT] != ENEMY_BASE and attacker[AT] != path[attacker[AT]][-1]:
            print(f"{attacker[MY_PODS]} {attacker[AT]} {path[attacker[AT]][path[attacker[AT]].index(attacker[AT])+1]} ", end="")

def findResources(pods: list, zones: dict):
    """ Strategi menggerakkan seluruh PODs pada arena untuk mencari platinum,
        petak lawan, petak netral, atau memilih jalur acak.
    """
    for pod_group in pods:
        resource_path = PriorityQueue()
        capture_path = []
        neutral_path = []
        all_path = []
        for pos in adj_map[pod_group[AT]]:
            if zones[pos][0] != MY_ID and zones[pos][1] > 0:
                resource_path.enqueue(pos, int(zones[pos][1]))
            elif zones[pos][0] == ENEMY_ID and pod_group[MY_PODS] > zones[pos][2]:
                capture_path.append(pos)
            elif zones[pos][0] == -1:
                neutral_path.append(pos)
            all_path.append(pos)
        for i in range(pod_group[MY_PODS]):
            if not resource_path.isEmpty():
                print(f"1 {pod_group[AT]} {resource_path.dequeue()} ", end="")
            elif capture_path != []:
                print(f"1 {pod_group[AT]} {capture_path.pop()} ", end="")
            elif neutral_path != []:
                print(f"1 {pod_group[AT]} {neutral_path.pop()} ", end="")
            else:
                print(f"1 {pod_group[AT]} {random.choice(all_path)} ", end="")
        

""" GAME LOOP """
while True:
    visible_zone = {}
    pods = []
    my_zone = []
    enemy_zone = []
    MY_PLATINUM = int(input())
    for i in range(ZONE_COUNT):
        """ Loop untuk mendapatkan informasi terkait petak-petak yang bisa kita peroleh informasinya. """
        z_id, owner_id, pods_p0, pods_p1, visible, platinum = [int(j) for j in input().split()]
        if visible:
            if visible:
                visible_zone.setdefault(z_id, []).extend([owner_id, platinum, pods_p0 if ENEMY_ID==0 else pods_p1])
            if ENEMY_BASE == -1 and owner_id == ENEMY_ID:
                ENEMY_BASE = z_id
            if MY_BASE == -1 and owner_id == MY_ID:
                MY_BASE = z_id
            if owner_id == MY_ID:
                my_zone.append(z_id)
            else:
                enemy_zone.append(z_id)
        if MY_ID == 0:
            if pods_p0 > 0:
                pods.append([z_id, pods_p0, pods_p1])
        else:
            if pods_p1 > 0:
                pods.append([z_id, pods_p1, pods_p0])

    """ STRATEGY DECIDER """
    """ Terdapat dua strategi:
        1. invadeEnemyBaseGuerilla
            strategi menginvasi daerah lawan dengan cara menggerakkan seluruh PODs menuju
            daerah lawan secara serempak.
        2. findResources
            strategi mencari platinum untuk menambah sumber daya atau menaklukkan daerah-daerah lawan.
        Strategi invadeEnemyBaseGuerilla dilakukan apabila platinum sudah mencukupi (50), area yang ditaklukkan
        sudah 1/3 arena, dan akan dilakukan pada interval 25 turn dengan 20 turn invasi dan 5 turn mencari platinum.
        Strategi findResources akan dilakukan apabila kondisi untuk menginvasi belum terpenuhi. Namun, apabila 20 turn
        telah lewat dan kondisi belum terpenuhi juga maka invasi akan dilakukan pada interval 20 turn yaitu 10 turn invasi
        dan 10 turn mencari platinum.
    """
    if MY_PLATINUM > 50 or len(my_zone) > ZONE_COUNT//3:
        if COUNTER == -1:
            COUNTER = 6
        if COUNTER % 25 > 5:
            start_time = time.perf_counter()
            invadeEnemyBaseGuerillaMSBFS(pods, enemy_zone)
            end_time = time.perf_counter()
            print("\nGuerilla:", end_time - start_time, file=sys.stderr)
        else:
            findResources(pods, visible_zone)
    else:
        TURN += 1
        print(TURN, file=sys.stderr)
        COUNTER = -1
        if TURN >= 20 and TURN % 20 < 10:
            start_time = time.perf_counter()
            invadeEnemyBaseGuerillaMSBFS(pods, enemy_zone)
            end_time = time.perf_counter()
            print("\nGuerilla:", end_time - start_time, file=sys.stderr)
        else:
            findResources(pods, visible_zone)

    if COUNTER != -1:
        COUNTER += 1
    print(COUNTER, file=sys.stderr)
    print()
    print("WAIT")
