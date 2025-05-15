import matplotlib.pyplot as plt
import csv
import random
import pandas as pd

class CacheBlock:
    def __init__(self):
        self.valid = False
        self.tag = None
        self.last_used = -1  # For LRU
        self.inserted_at = -1  # For FIFO

class CacheLevel:
    def __init__(self, size, block_size, associativity, access_latency, level_name, replacement_policy='LRU'):
        self.block_size = block_size
        self.associativity = associativity
        self.num_blocks = size // block_size
        self.num_sets = self.num_blocks // associativity
        self.access_latency = access_latency
        self.level_name = level_name
        self.replacement_policy = replacement_policy.upper()

        self.cache = [[CacheBlock() for _ in range(associativity)] for _ in range(self.num_sets)]
        self.time = 0
        self.hits = 0
        self.access_log = []

        self.cold_misses = 0  # Count cold misses

    def access(self, address):
        block_addr = address // self.block_size
        set_index = block_addr % self.num_sets
        tag = block_addr // self.num_sets

        self.time += 1
        cache_set = self.cache[set_index]

        # Check for hit
        for block in cache_set:
            if block.valid and block.tag == tag:
                block.last_used = self.time
                self.hits += 1
                self.access_log.append((address, set_index, True))
                return True, self.access_latency

        # Miss: check for cold miss (invalid block available)
        invalid_blocks = [b for b in cache_set if not b.valid]
        if invalid_blocks:
            self.cold_misses += 1

        # Replacement
        if self.replacement_policy == 'LRU':
            if invalid_blocks:
                block_to_replace = invalid_blocks[0]
            else:
                block_to_replace = min(cache_set, key=lambda b: b.last_used)
            block_to_replace.valid = True
            block_to_replace.tag = tag
            block_to_replace.last_used = self.time
        elif self.replacement_policy == 'FIFO':
            if invalid_blocks:
                block_to_replace = invalid_blocks[0]
            else:
                block_to_replace = min(cache_set, key=lambda b: b.inserted_at)
            block_to_replace.valid = True
            block_to_replace.tag = tag
            block_to_replace.inserted_at = self.time
        else:
            raise ValueError(f"Unknown replacement policy {self.replacement_policy}")

        self.access_log.append((address, set_index, False))
        return False, self.access_latency

    def get_cold_misses(self):
        return self.cold_misses

class MultiLevelCacheSimulator:
    def __init__(self, l1_config, l2_config, memory_latency, l1_policy='LRU', l2_policy='LRU'):
        self.L1 = CacheLevel(*l1_config, level_name="L1", replacement_policy=l1_policy)
        self.L2 = CacheLevel(*l2_config, level_name="L2", replacement_policy=l2_policy)
        self.memory_latency = memory_latency
        self.total_accesses = 0
        self.total_cycles = 0
        self.full_log = []

    def access(self, address):
        self.total_accesses += 1

        hit_l1, latency_l1 = self.L1.access(address)
        if hit_l1:
            self.total_cycles += latency_l1
            self.full_log.append((address, "L1", latency_l1, "Hit"))
            return

        hit_l2, latency_l2 = self.L2.access(address)
        if hit_l2:
            # L2 hit means L1 miss but L2 hit
            self.total_cycles += latency_l1 + latency_l2
            self.full_log.append((address, "L2", latency_l1 + latency_l2, "Hit"))
            # On L2 hit, load block into L1
            self.L1.access(address)
        else:
            # Miss in both caches - go to memory
            total_latency = latency_l1 + latency_l2 + self.memory_latency
            self.total_cycles += total_latency
            self.full_log.append((address, "Memory", total_latency, "Miss"))
            # Load block into L2 and L1 on memory miss
            self.L2.access(address)
            self.L1.access(address)

    def run_simulation(self, address_list):
        for addr in address_list:
            self.access(addr)

    def stats(self):
        hit_rate_l1 = self.L1.hits / self.total_accesses if self.total_accesses else 0
        l1_misses = self.total_accesses - self.L1.hits
        hit_rate_l2 = self.L2.hits / l1_misses if l1_misses > 0 else 0
        amat = self.total_cycles / self.total_accesses if self.total_accesses else 0

        cold_misses_l1 = self.L1.get_cold_misses()
        cold_misses_l2 = self.L2.get_cold_misses()

        return hit_rate_l1, hit_rate_l2, amat, cold_misses_l1, cold_misses_l2

def generate_workload(pattern="looping", size=100, stride=4):
    if pattern == "sequential":
        return list(range(0, size * stride, stride))
    elif pattern == "looping":
        loop_size = 16
        return [(i % loop_size) * stride for i in range(size)]
    elif pattern == "random":
        return [random.randint(0, 255) * stride for _ in range(size)]
    else:
        raise ValueError("Invalid pattern")

def run_experiments():
    cache_sizes = [64, 128]
    associativities = [1, 2, 4]
    block_sizes = [4, 8]
    workloads = ["sequential", "looping", "random"]
    policies = ['LRU', 'FIFO']
    memory_latency = 50

    results = []

    for l1_size in cache_sizes:
        for l2_size in cache_sizes:
            for l1_assoc in associativities:
                for l2_assoc in associativities:
                    for block_size in block_sizes:
                        for workload in workloads:
                            for policy in policies:
                                l1_config = (l1_size, block_size, l1_assoc, 1)
                                l2_config = (l2_size, block_size, l2_assoc, 5)

                                addresses = generate_workload(workload, size=100, stride=block_size)
                                sim = MultiLevelCacheSimulator(l1_config, l2_config, memory_latency, policy, policy)
                                sim.run_simulation(addresses)
                                hit1, hit2, amat, cold1, cold2 = sim.stats()

                                results.append({
                                    "L1 Size": l1_size,
                                    "L2 Size": l2_size,
                                    "L1 Assoc": l1_assoc,
                                    "L2 Assoc": l2_assoc,
                                    "Block Size": block_size,
                                    "Workload": workload,
                                    "Policy": policy,
                                    "L1 Hit Rate": hit1,
                                    "L2 Hit Rate": hit2,
                                    "AMAT": amat,
                                    "L1 Cold Misses": cold1,
                                    "L2 Cold Misses": cold2
                                })

                                print(f"Done: L1 {l1_size}B, L2 {l2_size}B, L1 Assoc {l1_assoc}, L2 Assoc {l2_assoc}, "
                                      f"Blk {block_size}, WL {workload}, Policy {policy} | "
                                      f"L1 Hit: {hit1:.2f}, L2 Hit: {hit2:.2f}, AMAT: {amat:.2f}, "
                                      f"L1 Cold Misses: {cold1}, L2 Cold Misses: {cold2}")

    # Save results to CSV
    keys = results[0].keys()
    with open("cache_performance_comparison.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(results)

    # Plotting AMAT
    df = pd.DataFrame(results)

    plt.figure(figsize=(14, 8))
    markers = {'sequential':'o', 'looping':'s', 'random':'^'}
    colors = {'LRU':'tab:blue', 'FIFO':'tab:orange'}

    for workload in workloads:
        for policy in policies:
            subset = df[(df['Workload'] == workload) & (df['Policy'] == policy)]
            grouped = subset.groupby('Block Size')['AMAT'].mean().reset_index()
            plt.plot(grouped['Block Size'], grouped['AMAT'],
                     marker=markers[workload],
                     color=colors[policy],
                     linestyle='-' if policy=='LRU' else '--',
                     label=f"{workload.capitalize()} - {policy}")

    plt.title("Average Memory Access Time (AMAT) vs Block Size\nfor Various Workloads and Replacement Policies")
    plt.xlabel("Block Size (Bytes)")
    plt.ylabel("AMAT (cycles)")
    plt.xticks(block_sizes)
    plt.legend()
    plt.grid(True)

    summary_lines = ["Analysis Summary:\n"]
    for workload in workloads:
        for policy in policies:
            subset = df[(df['Workload'] == workload) & (df['Policy'] == policy)]
            avg_amat = subset['AMAT'].mean()
            min_amat = subset['AMAT'].min()
            max_amat = subset['AMAT'].max()
            summary_lines.append(f"{workload.capitalize()} + {policy}: Avg={avg_amat:.2f}, Min={min_amat:.2f}, Max={max_amat:.2f}")

    summary_text = "\n".join(summary_lines)

    plt.gcf().text(0.5, 0.40, summary_text,
               fontsize=10,
               verticalalignment='bottom',
               horizontalalignment='left',
               bbox=dict(facecolor='white', alpha=0.85, edgecolor='gray', boxstyle='round,pad=0.5'))

    print("\n===== Analysis Summary =====")
    for workload in workloads:
        for policy in policies:
            subset = df[(df['Workload'] == workload) & (df['Policy'] == policy)]
            avg_amat = subset['AMAT'].mean()
            max_amat = subset['AMAT'].max()
            min_amat = subset['AMAT'].min()
            print(f"{workload.capitalize()} workload with {policy} policy:")
            print(f"  Average AMAT: {avg_amat:.2f} cycles")
            print(f"  Min AMAT: {min_amat:.2f} cycles")
            print(f"  Max AMAT: {max_amat:.2f} cycles\n")

    plt.tight_layout(rect=[0, 0.1, 1, 1])
    plt.savefig("amat_comparison_with_summary.png")
    plt.show()

if __name__ == "__main__":
    run_experiments()
