
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple
from time import perf_counter
import random
import string

# ========== 1) DATA STRUCTURES ==========

@dataclass
class Product:
    sku: str           # unique key (e.g., "SKU-0001")
    name: str
    category: str
    price: float
    stock: int

    def __str__(self) -> str:
        return f"[{self.sku}] {self.name} | {self.category} | RM{self.price:.2f} | stock: {self.stock}"

class HashTableSeparateChaining:
    """
    Hash table keyed by strings (e.g., SKU), using separate chaining via lists.
    """
    def __init__(self, capacity: int = 53) -> None:
        # Capacity should be a positive integer; prime-ish sizes reduce clustering a bit.
        self._capacity = max(5, capacity)
        self._buckets: List[List[Tuple[str, Any]]] = [[] for _ in range(self._capacity)]
        self._size = 0

    def _index(self, key: str) -> int:
        return hash(key) % self._capacity

    def _should_resize(self) -> bool:
        # Simple policy: resize when load factor > 0.75
        return self.load_factor() > 0.75

    def load_factor(self) -> float:
        return self._size / self._capacity

    def _resize(self, new_capacity: int) -> None:
        old_items = [(k, v) for bucket in self._buckets for (k, v) in bucket]
        self._capacity = max(5, new_capacity)
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0
        for k, v in old_items:
            self.insert(k, v, allow_update=True)

    def insert(self, key: str, value: Any, allow_update: bool = True) -> bool:
        idx = self._index(key)
        bucket = self._buckets[idx]

        for i, (k, _) in enumerate(bucket):
            if k == key:
                if allow_update:
                    bucket[i] = (key, value)
                    return True
                else:
                    return False  # key exists and updates not allowed
        bucket.append((key, value))
        self._size += 1

        if self._should_resize():
            self._resize(self._capacity * 2 + 1)

        return True

    def get(self, key: str) -> Optional[Any]:
        idx = self._index(key)
        for (k, v) in self._buckets[idx]:
            if k == key:
                return v
        return None

    def delete(self, key: str) -> bool:
        idx = self._index(key)
        bucket = self._buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self._size -= 1
                return True
        return False

    def contains(self, key: str) -> bool:
        return self.get(key) is not None

    def __len__(self) -> int:
        return self._size

    def items(self):
        for bucket in self._buckets:
            for k, v in bucket:
                yield (k, v)

# ========== 2) LOCAL STORAGE (BABY SHOP) + 3) CLI INVENTORY ==========

class InventorySystem:
    def __init__(self, capacity: int = 53) -> None:
        # Hash table as primary store
        self.table = HashTableSeparateChaining(capacity=capacity)
        # One-dimensional array (list) for performance comparison
        self.array: List[Product] = []
        # Preload some sample baby shop products
        self._seed_data()

    def _seed_data(self) -> None:
        samples = [
            Product("SKU-0001", "Baby Diapers (M, 52 pcs)", "Diapers", 45.90, 120),
            Product("SKU-0002", "Gentle Baby Wipes (80)", "Hygiene", 9.50, 300),
            Product("SKU-0003", "Infant Formula Stage 1 (900g)", "Nutrition", 89.00, 40),
            Product("SKU-0004", "Glass Baby Bottle (240ml)", "Feeding", 35.00, 75),
            Product("SKU-0005", "Silicone Pacifier (2-pack)", "Accessories", 18.00, 150),
            Product("SKU-0006", "Organic Baby Lotion (200ml)", "Hygiene", 24.50, 90),
            Product("SKU-0007", "Baby Shampoo (400ml)", "Hygiene", 21.90, 110),
            Product("SKU-0008", "Stroller Rain Cover", "Travel", 59.00, 25),
            Product("SKU-0009", "Convertible Car Seat", "Travel", 399.00, 10),
            Product("SKU-0010", "Cotton Onesies (3-pack)", "Clothing", 39.90, 80),
        ]
        for p in samples:
            self.table.insert(p.sku, p)
            self.array.append(p)

    # -------- CRUD --------
    def insert_product(self, p: Product) -> bool:
        ok = self.table.insert(p.sku, p, allow_update=False)
        if ok:
            self.array.append(p)
        return ok

    def search_by_sku(self, sku: str) -> Optional[Product]:
        return self.table.get(sku)

    def edit_product(self, sku: str, *, name=None, category=None, price=None, stock=None) -> bool:
        p = self.table.get(sku)
        if not p:
            return False
        if name is not None: p.name = name
        if category is not None: p.category = category
        if price is not None: p.price = float(price)
        if stock is not None: p.stock = int(stock)
        # Hash table already holds the same object; array list needs no change if we keep identity
        return True

    def delete_product(self, sku: str) -> bool:
        p = self.table.get(sku)
        if not p:
            return False
        self.table.delete(sku)
        # Remove from array (linear scan)
        for i, item in enumerate(self.array):
            if item.sku == sku:
                self.array.pop(i)
                break
        return True

    def list_products(self) -> List[Product]:
        # Items in hash table have no inherent order; show a nicely sorted view by SKU.
        return sorted((v for _, v in self.table.items()), key=lambda p: p.sku)

    # -------- Display helpers --------
    @staticmethod
    def print_products(products: List[Product]) -> None:
        if not products:
            print("\n(No products found.)")
            return
        print("\n" + "-" * 85)
        print(f"{'SKU':<10} | {'Name':<34} | {'Category':<12} | {'Price (RM)':>10} | {'Stock':>5}")
        print("-" * 85)
        for p in products:
            print(f"{p.sku:<10} | {p.name:<34} | {p.category:<12} | {p.price:>10.2f} | {p.stock:>5}")
        print("-" * 85)

    # -------- 4) PERFORMANCE COMPARISON --------
    def benchmark_search(self, n_extra: int = 20000, trials: int = 2000) -> None:
        """
        Insert additional random items (same items into both structures),
        then randomly look up keys and time hash vs array (linear scan).
        """
        # Generate unique random SKUs and insert
        new_items: List[Product] = []
        for _ in range(n_extra):
            sku = "SKU-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
            p = Product(sku, "Sample Item", "Misc", round(random.uniform(5, 500), 2), random.randint(0, 500))
            if self.table.contains(sku):
                continue  # extremely unlikely collision, but just in case
            self.table.insert(sku, p, allow_update=False)
            self.array.append(p)
            new_items.append(p)

        # Build a pool of existing keys for fair random lookups (half hits, half misses)
        existing_keys = [p.sku for p in self.array]
        miss_keys = ["MISS-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
                     for _ in range(trials // 2)]
        queries = []
        for _ in range(trials):
            if random.random() < 0.5:
                queries.append(random.choice(existing_keys))  # hit
            else:
                queries.append(random.choice(miss_keys))      # miss

        # Time hash table lookups
        t0 = perf_counter()
        for q in queries:
            _ = self.table.get(q)
        t_hash = perf_counter() - t0

        # Time array linear search
        def linear_search(sku: str) -> Optional[Product]:
            for p in self.array:
                if p.sku == sku:
                    return p
            return None

        t1 = perf_counter()
        for q in queries:
            _ = linear_search(q)
        t_array = perf_counter() - t1

        print("\n=== Search Performance Comparison ===")
        print(f"Records in table/array: {len(self.array):,}")
        print(f"Queries: {trials:,} (≈50% hits / 50% misses)")
        print(f"Hash table total time : {t_hash:.6f} s   (~{(t_hash/trials)*1e6:.2f} µs/query)")
        print(f"Array (linear) time   : {t_array:.6f} s   (~{(t_array/trials)*1e6:.2f} µs/query)")
        speedup = (t_array / t_hash) if t_hash > 0 else float('inf')
        print(f"Speedup (array / hash): {speedup:.2f}× (higher is better)")

        # Simple explanation
        print("\nWhy the difference?")
        print("- Hash table average lookup is O(1): it jumps straight to a bucket via hash(key).")
        print("- Array lookup is O(n): it scans item by item until it finds a match (or reaches the end).")
        print("- Separate chaining keeps collisions local to small bucket lists, so lookups stay fast at typical load factors.")

    # -------- CLI --------
    def run(self) -> None:
        while True:
            print("""
================= Baby Shop Inventory System =================
1) List all products
2) Insert a new product
3) Search product by SKU
4) Edit product (optional)
5) Delete product (optional)
6) Compare search performance (Hash Table vs Array)
0) Exit
================================================================
""")
            choice = input("Enter choice: ").strip()
            if choice == "1":
                self.print_products(self.list_products())

            elif choice == "2":
                print("\n-- Insert New Product --")
                sku = input("SKU (unique, e.g., SKU-1234): ").strip()
                if not sku:
                    print("SKU cannot be empty.")
                    continue
                if self.table.contains(sku):
                    print("SKU already exists.")
                    continue
                name = input("Name: ").strip()
                category = input("Category: ").strip()
                try:
                    price = float(input("Price (RM): ").strip())
                    stock = int(input("Stock qty: ").strip())
                except ValueError:
                    print("Invalid number for price or stock.")
                    continue

                ok = self.insert_product(Product(sku, name, category, price, stock))
                print("Inserted." if ok else "Insert failed (duplicate?).")

            elif choice == "3":
                sku = input("Enter SKU to search: ").strip()
                p = self.search_by_sku(sku)
                if p:
                    print("\nFound:\n" + str(p))
                else:
                    print("Not found.")

            elif choice == "4":
                sku = input("Enter SKU to edit: ").strip()
                if not self.table.contains(sku):
                    print("SKU not found.")
                    continue
                print("Leave fields empty to keep current value.")
                name = input("New name: ").strip()
                category = input("New category: ").strip()
                price_s = input("New price (RM): ").strip()
                stock_s = input("New stock: ").strip()

                kwargs = {}
                if name: kwargs["name"] = name
                if category: kwargs["category"] = category
                if price_s:
                    try: kwargs["price"] = float(price_s)
                    except ValueError: print("Invalid price; ignored.")
                if stock_s:
                    try: kwargs["stock"] = int(stock_s)
                    except ValueError: print("Invalid stock; ignored.")

                ok = self.edit_product(sku, **kwargs)
                print("Updated." if ok else "Update failed.")

            elif choice == "5":
                sku = input("Enter SKU to delete: ").strip()
                ok = self.delete_product(sku)
                print("Deleted." if ok else "Delete failed (not found).")

            elif choice == "6":
                print("\n-- Performance Benchmark --")
                try:
                    n_extra = int(input("How many extra random records to add (e.g., 20000): ").strip() or "20000")
                    trials = int(input("How many random searches to run (e.g., 2000): ").strip() or "2000")
                except ValueError:
                    print("Invalid numbers. Using defaults (20000, 2000).")
                    n_extra, trials = 20000, 2000
                self.benchmark_search(n_extra=n_extra, trials=trials)

            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")


# ========== ENTRY POINT ==========

if __name__ == "__main__":
    system = InventorySystem(capacity=97)  # pick a starting size; resizing will handle growth
    system.run()
