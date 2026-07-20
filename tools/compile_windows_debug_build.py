import subprocess
import sys
import os
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
MINGW_FIX_DIR = os.path.join(PARENT_DIR, ".mingw-fix")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def check_mingw():
    """Check if MinGW compiler works and fix broken alternatives symlinks."""
    try:
        result = subprocess.run(
            ["x86_64-w64-mingw32-g++", "--version"],
            capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0, None
    except FileNotFoundError:
        return False, "not_found"
    except Exception as e:
        return False, str(e)


def setup_mingw_fix():
    """Create a workaround for broken MinGW alternatives symlinks."""
    os.makedirs(os.path.join(MINGW_FIX_DIR, "bin"), exist_ok=True)

    tools = {
        "x86_64-w64-mingw32-g++": "x86_64-w64-mingw32-g++-win32",
        "x86_64-w64-mingw32-gcc": "x86_64-w64-mingw32-gcc-win32",
        "x86_64-w64-mingw32-gcc-ar": "x86_64-w64-mingw32-gcc-ar-win32",
        "x86_64-w64-mingw32-ranlib": "x86_64-w64-mingw32-gcc-ranlib-win32",
    }

    for link_name, target in tools.items():
        link_path = os.path.join(MINGW_FIX_DIR, "bin", link_name)
        target_path = os.path.join("/usr/bin", target)
        if os.path.exists(link_path):
            os.remove(link_path)
        os.symlink(target_path, link_path)

    print("Created temporary symlink workaround for MinGW in .mingw-fix/")
    return MINGW_FIX_DIR


def run_scons_build(env):
    try:
        process = subprocess.Popen(
            ["scons", "platform=windows", "target=template_debug", "arch=x86_64", "compiledb=yes"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=PARENT_DIR,
            env=env
        )

        stdout_lines = []
        stderr_lines = []

        while True:
            output = process.stdout.readline()
            if output:
                print(output, end="")
                stdout_lines.append(output)
            elif process.poll() is not None:
                break

        remaining_out, remaining_err = process.communicate()
        if remaining_out:
            print(remaining_out, end="")
            stdout_lines.append(remaining_out)
        if remaining_err:
            stderr_lines.append(remaining_err)

        if process.returncode == 0:
            print("\nCompilation finished successfully.")
            print("A Windows x86_64 debug build was added to the bin folder.")
            print("The compile_commands.json file was also updated to improve IntelliSense support.")
        else:
            print("\nCompilation FAILED:")
            print(''.join(stderr_lines).strip() or "Unknown error occurred.")

    except FileNotFoundError:
        print("Error: 'scons' command not found. Make sure SCons is installed and available in your PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    input("\nPress any key to continue...")


if __name__ == "__main__":
    clear_screen()

    ok, err = check_mingw()
    env = os.environ.copy()

    if ok:
        print("MinGW compiler detected.")
    elif err == "not_found":
        print("MinGW cross-compiler not found.")
        print("Install it with: sudo apt install mingw-w64")
        input("\nPress any key to continue...")
        sys.exit(1)
    else:
        print(f"MinGW compiler issue detected: {err}")
        print("Attempting workaround...")
        fix_dir = setup_mingw_fix()
        env["PATH"] = os.path.join(fix_dir, "bin") + os.pathsep + env["PATH"]

    run_scons_build(env)
