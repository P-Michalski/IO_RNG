from typing import Tuple, Optional, Callable
import time
import os
import sys
import subprocess
import importlib.util
import json

# Dodaj bieżący folder do path aby móc importować moduły RNG
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def _mean(bits: list) -> float:
    return (sum(bits) / len(bits)) if bits else 0.0


def _load_python_modules() -> dict:
    """Dynamicznie ładuje wszystkie moduły RNG z bieżącego folderu."""
    modules = {}
    for filename in os.listdir(current_dir):
        if filename.endswith('.py') and filename not in ['tester.py', 'update_paths.py']:
            module_name = filename[:-3]
            filepath = os.path.join(current_dir, filename)
            try:
                spec = importlib.util.spec_from_file_location(module_name, filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                modules[module_name] = module
            except Exception as e:
                print(f"Warning: Nie udało się załadować {module_name}: {e}")
    return modules


def _get_bit_stream_function(module, module_name: str):
    """Znalezienie funkcji bit_stream w module (obsługuje różne nazwy)."""
    possible_names = [
        f'{module_name.lower()}_bit_stream',
        f'{module_name.lower().replace("_", "")}_bit_stream',
        'system_random_bit_stream',
        'python_random_bit_stream',
        'bbs_bit_stream',
    ]
    
    for func_name in possible_names:
        if hasattr(module, func_name):
            return func_name, getattr(module, func_name)
    
    return None, None


def _call_executable(exe_path: str, n_bits: int, seed: int = 12345) -> Tuple[float, float]:
    """Uruchamia zewnętrzny plik .exe i zwraca (elapsed, mean_bit)."""
    if not os.path.exists(exe_path):
        raise FileNotFoundError(f"Plik {exe_path} nie istnieje")
    
    try:
        start = time.perf_counter()
        result = subprocess.run([exe_path, str(seed), str(n_bits)], 
                              capture_output=True, text=True, timeout=60)
        elapsed = time.perf_counter() - start
        
        if result.returncode != 0:
            raise RuntimeError(f"Proces zwrócił kod błędu: {result.returncode}\n{result.stderr}")
        
        # Spróbuj sparsować JSON output
        try:
            data = json.loads(result.stdout)
            bits = data.get('bits', [])
            mean_bit = (sum(bits) / len(bits)) if bits else 0.0
        except json.JSONDecodeError:
            mean_bit = 0.0
        
        return elapsed, mean_bit
    except subprocess.TimeoutExpired:
        raise RuntimeError("Timeout - proces trwał zbyt długo")


def _find_executable(search_dir: str, exe_name: str) -> Optional[str]:
    """Szuka pliku .exe w katalogu i jego podkatalogach."""
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file == exe_name or file == exe_name + '.exe':
                return os.path.join(root, file)
    return None

def print_instructions(n_bits: int = 100000) -> None:
    """Wypisuje instrukcje i komendy do odpalenia każdego generatora."""
    print(f"\n{'='*80}")
    print(f"INSTRUKCJE DO IMPLEMENTACJI W BACKENDZIE")
    print(f"{'='*80}\n")
    
    testers_info: list[Tuple[str, str, str]] = []  # (nazwa, typ, komenda)
    
    # Załaduj moduły Python RNG
    print(f"Szukam modułów RNG w folderze: .")
    modules = _load_python_modules()
    print(f"Znaleziono {len(modules)} modułów: {list(modules.keys())}\n")
    
    # Instrukcje dla każdego modułu Python
    print("MODUŁY PYTHON:")
    print("-" * 80)
    
    for module_name, module in modules.items():
        func_name, func = _get_bit_stream_function(module, module_name)
        if func is None:
            print(f"✗ {module_name:20s} - Nie znaleziono funkcji bit_stream")
            continue
        
        # Parametry dla każdego modułu
        if module_name == 'LCG':
            params = "(seed=123456789, n_bits=100000, bits_per_value=31, msb_first=True)"
            cmd = f"python -m {module_name} {params}"
        elif module_name == 'Park_Miller':
            params = "(seed=123456789, n_bits=100000, bits_per_value=31, msb_first=True)"
            cmd = f"python -m {module_name} {params}"
        elif module_name == 'AWCG':
            params = "(seed=123456789, n_bits=100000, bits_per_value=32, msb_first=True)"
            cmd = f"python -m {module_name} {params}"
        elif module_name == 'PCG32':
            params = "(state=(42, 54), n_bits=100000, bits_per_value=32, msb_first=True)"
            cmd = f"python -m {module_name} {params}"
        elif module_name == 'SplitMix64':
            params = "(seed=123456789, n_bits=100000, bits_per_value=64, msb_first=True)"
            cmd = f"python -m {module_name} {params}"
        elif module_name == 'SystemRNG':
            params = "(seed=None, n_bits=100000, bits_per_value=32, msb_first=True)"
            cmd = f"python -m {module_name} {params}"
        elif module_name == 'PythonRNG':
            params = "(seed=12345, n_bits=100000, bits_per_value=32, msb_first=True)"
            cmd = f"python -m {module_name} {params}"
        elif module_name == 'BlumBlumShub':
            params = "(seed=12345, n_bits=100000, p=383, q=503, bits_per_value=4, msb_first=True)"
            cmd = f"python -m {module_name} {params}"
        else:
            params = "(seed=12345, n_bits=100000, bits_per_value=32, msb_first=True)"
            cmd = f"python -m {module_name} {params}"
        
        display_name = f"{func_name}({params})"
        print(f"✓ {module_name:20s} -> {func_name}")
        print(f"  Komenda: {cmd}")
        print(f"  Funkcja: {display_name}")
        testers_info.append((module_name, "Python", cmd))
    
    # Instrukcje dla .exe (Rust)
    print(f"\nFAJLY BINARNE (RUST/C#):")
    print("-" * 80)
    
    chacha_dir = os.path.join(current_dir, 'chacha20_rng')
    chacha_exe = _find_executable(chacha_dir, 'chacha20_rng')
    if chacha_exe:
        chacha_rel = os.path.relpath(chacha_exe, current_dir)
        cmd = f"{chacha_rel} <seed> <n_bits>"
        print(f"✓ ChaCha20 (Rust)")
        print(f"  Ścieżka: {chacha_rel}")
        print(f"  Komenda: {cmd}")
        print(f"  Oczekiwany output JSON: {{'bits': [...], 'time': 0.123456}}")
        testers_info.append(("ChaCha20", "Rust", cmd))
    
    xorshift_dir = os.path.join(current_dir, 'Xorshift256')
    xorshift_exe = _find_executable(xorshift_dir, 'Xoshiro256')
    if xorshift_exe:
        xorshift_rel = os.path.relpath(xorshift_exe, current_dir)
        cmd = f"{xorshift_rel} <seed> <n_bits>"
        print(f"✓ Xorshift256 (C#)")
        print(f"  Ścieżka: {xorshift_rel}")
        print(f"  Komenda: {cmd}")
        print(f"  Oczekiwany output JSON: {{'bits': [...], 'time': 0.123456}}")
        testers_info.append(("Xorshift256", "C#", cmd))
    
    print(f"\n{'='*80}")
    print(f"PODSUMOWANIE - {len(testers_info)} Generatorów do Implementacji")
    print(f"{'='*80}\n")
    
    for i, (name, lang, cmd) in enumerate(testers_info, 1):
        print(f"{i:2d}. {name:20s} ({lang:8s}) -> {cmd}")


def run_all(n_bits: int = 100000) -> None:
    testers: list[Tuple[str, Callable]] = []
    
    # Załaduj moduły Python RNG
    print(f"Szukam modułów RNG w folderze: .")
    modules = _load_python_modules()
    print(f"Znaleziono {len(modules)} modułów: {list(modules.keys())}\n")
    
    # Utwórz testery dla każdego znalezionego modułu
    for module_name, module in modules.items():
        try:
            func_name, func = _get_bit_stream_function(module, module_name)
            if func is None:
                print(f"✗ Nie znaleziono funkcji w {module_name}")
                continue
            
            # Zdefiniuj parametry dla każdego modułu
            if module_name == 'LCG':
                def make_lcg_tester(f):
                    def tester(n_bits):
                        bits, elapsed = f(123456789, 1103515245, 12345, 2**31, n_bits, bits_per_value=31, msb_first=True, return_time=True)
                        return elapsed, _mean(bits)
                    return tester
                tester_func = make_lcg_tester(func)
            elif module_name == 'Park_Miller':
                def make_pm_tester(f):
                    def tester(n_bits):
                        bits, elapsed = f(123456789, n_bits, bits_per_value=31, msb_first=True, return_time=True)
                        return elapsed, _mean(bits)
                    return tester
                tester_func = make_pm_tester(func)
            elif module_name == 'AWCG':
                def make_awcg_tester(f):
                    def tester(n_bits):
                        bits, elapsed = f(123456789, n_bits, r=24, s=10, base=2**32, bits_per_value=32, msb_first=True, return_time=True)
                        return elapsed, _mean(bits)
                    return tester
                tester_func = make_awcg_tester(func)
            elif module_name == 'PCG32':
                def make_pcg_tester(f):
                    def tester(n_bits):
                        bits, elapsed = f((42, 54), n_bits, bits_per_value=32, msb_first=True, return_time=True)
                        return elapsed, _mean(bits)
                    return tester
                tester_func = make_pcg_tester(func)
            elif module_name == 'SplitMix64':
                def make_sm_tester(f):
                    def tester(n_bits):
                        bits, elapsed = f(123456789, n_bits, bits_per_value=64, msb_first=True, return_time=True)
                        return elapsed, _mean(bits)
                    return tester
                tester_func = make_sm_tester(func)
            elif module_name == 'SystemRNG':
                def make_system_tester(f):
                    def tester(n_bits):
                        bits, elapsed = f(None, n_bits, bits_per_value=32, msb_first=True, return_time=True)
                        return elapsed, _mean(bits)
                    return tester
                tester_func = make_system_tester(func)
            elif module_name == 'PythonRNG':
                def make_python_tester(f):
                    def tester(n_bits):
                        bits, elapsed = f(12345, n_bits, bits_per_value=32, msb_first=True, return_time=True)
                        return elapsed, _mean(bits)
                    return tester
                tester_func = make_python_tester(func)
            elif module_name == 'BlumBlumShub':
                def make_bbs_tester(f):
                    def tester(n_bits):
                        bits, elapsed = f(12345, n_bits, p=383, q=503, bits_per_value=4, msb_first=True, return_time=True)
                        return elapsed, _mean(bits)
                    return tester
                tester_func = make_bbs_tester(func)
            else:
                def make_default_tester(f):
                    def tester(n_bits):
                        bits, elapsed = f(12345, n_bits, bits_per_value=32, msb_first=True, return_time=True)
                        return elapsed, _mean(bits)
                    return tester
                tester_func = make_default_tester(func)
            
            testers.append((f"{module_name} (Python)", tester_func))
            print(f"✓ Załadowano: {module_name}")
        except Exception as e:
            print(f"✗ Błąd przy ładowaniu {module_name}: {e}")
    
    # Szukaj .exe z chacha20_rng (Rust)
    print(f"\nSzukam chacha20_rng...")
    chacha_dir = os.path.join(current_dir, 'chacha20_rng')
    chacha_exe = _find_executable(chacha_dir, 'chacha20_rng')
    if chacha_exe:
        print(f"✓ Znaleziono: {chacha_exe}")
        def make_exe_tester(exe_path):
            def tester(n_bits):
                return _call_executable(exe_path, n_bits)
            return tester
        testers.append(("ChaCha20 (Rust)", make_exe_tester(chacha_exe)))
    else:
        print(f"✗ Nie znaleziono chacha20_rng w {chacha_dir}")
    
    # Szukaj .exe z Xorshift256 (C#)
    print(f"Szukam Xorshift256...")
    xorshift_dir = os.path.join(current_dir, 'Xorshift256')
    xorshift_exe = _find_executable(xorshift_dir, 'Xoshiro256')
    if xorshift_exe:
        print(f"✓ Znaleziono: {xorshift_exe}")
        def make_exe_tester_xor(exe_path):
            def tester(n_bits):
                return _call_executable(exe_path, n_bits)
            return tester
        testers.append(("Xorshift256 (C#)", make_exe_tester_xor(xorshift_exe)))
    else:
        print(f"✗ Nie znaleziono Xoshiro256 w {xorshift_dir}")
    
    print(f"\n{'='*80}")
    print(f"Uruchamiam {len(testers)} algorytmów dla {n_bits} bitów")
    print(f"{'='*80}\n")
    
    for name, fn in testers:
        try:
            start = time.perf_counter()
            elapsed, mean = fn(n_bits)
            total_elapsed = time.perf_counter() - start
            rate = n_bits / elapsed if elapsed > 0 else float("inf")
            print(f"{name:40s}: elapsed={elapsed:.6f}s  mean={mean:.6f}  bits/s={rate:>12.0f}")
        except Exception as e:
            print(f"{name:40s}: ERROR -> {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--benchmark":
        # Tryb benchmarku - uruchamia wszystkie testy
        n_bits = int(sys.argv[2]) if len(sys.argv) > 2 else 10000000
        run_all(n_bits)
    else:
        # Domyślnie - wypisuje instrukcje dla backendu
        print_instructions()

"""
Odpalanie w trybie domyślnym z instrukcjami:
python algorytmy/tester.py

Odpalanie w trybie benchmarku:
python algorytmy/tester.py --benchmark 1000000
"""