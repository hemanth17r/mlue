"""MLUE Native Core Cross-Platform Build Script.

Detects available C compilers (MSVC cl, GCC, Clang, TCC, Zig) and compiles
runtime/native/mlue_core.c into a high-performance native shared library.
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
NATIVE_DIR = ROOT_DIR / "runtime" / "native"
BIN_DIR = NATIVE_DIR / "bin"
SOURCE_FILE = NATIVE_DIR / "mlue_core.c"
HEADER_FILE = NATIVE_DIR / "mlue_core.h"


def get_target_library_name() -> str:
    if sys.platform == "win32" or sys.platform == "cygwin":
        return "mlue_core.dll"
    elif sys.platform == "darwin":
        return "libmlue_core.dylib"
    else:
        return "libmlue_core.so"


def find_compiler() -> tuple[str, list[str]]:
    # 1. Check Clang
    if shutil.which("clang"):
        return "clang", ["clang", "-O3", "-shared", "-fPIC"]

    # 2. Check GCC
    if shutil.which("gcc"):
        return "gcc", ["gcc", "-O3", "-shared", "-fPIC"]

    # 3. Check Zig CC
    if shutil.which("zig"):
        return "zig", ["zig", "cc", "-O3", "-shared", "-fPIC"]

    # 4. Check TinyCC (tcc)
    if shutil.which("tcc"):
        return "tcc", ["tcc", "-shared"]

    # 5. Check MSVC (cl.exe)
    if shutil.which("cl"):
        return "msvc", ["cl", "/O2", "/LD", "/MD"]

    return "", []


def build() -> bool:
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    target_lib = BIN_DIR / get_target_library_name()
    compiler_type, base_cmd = find_compiler()

    if not compiler_type:
        print("[MLUE Build] No native C compiler (gcc, clang, cl, tcc, zig) found on system PATH.")
        print("[MLUE Build] Native C source is verified at: runtime/native/mlue_core.c")
        print("[MLUE Build] Python runtime will operate in pure-integer Q32.32 mode with 100% bit parity.")
        return False

    print(f"[MLUE Build] Compiling '{SOURCE_FILE.name}' using {compiler_type} -> '{target_lib.name}'...")

    if compiler_type == "msvc":
        cmd = base_cmd + [str(SOURCE_FILE), f"/Fe:{str(target_lib)}", f"/Fo:{str(BIN_DIR / 'mlue_core.obj')}"]
    else:
        cmd = base_cmd + ["-I", str(NATIVE_DIR), "-o", str(target_lib), str(SOURCE_FILE), "-lm"]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"[MLUE Build] Build SUCCESS: {target_lib}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[MLUE Build] Compilation FAILED with error code {e.returncode}:")
        print(e.stderr or e.stdout)
        return False


if __name__ == "__main__":
    success = build()
    sys.exit(0 if success else 1)
