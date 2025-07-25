
print("this is the build script")

import os
import platform
import urllib.request
import zipfile
import tarfile
import shutil
import subprocess
from pathlib import Path

SDL_VENDOR_DIR = Path("vendors/sdl")
IMGUI_VENDOR_DIR = Path("vendors/imgui")
SDL_VERSION = "3.2.18"  
IMGUI_VERSION = "v1.92.1"  
IMGUI_REPO = "https://github.com/ocornut/imgui"

def download_and_extract(url, dest, archive_type):
    archive_name = dest / url.split("/")[-1]
    print(f"Downloading {url}...")
    urllib.request.urlretrieve(url, archive_name)

    print(f"Extracting {archive_name}...")

    if archive_type == "zip":
        with zipfile.ZipFile(archive_name, "r") as zf:
            zf.extractall(dest)
    elif archive_type == "tar.gz":
        with tarfile.open(archive_name, "r:gz") as tf:
            tf.extractall(dest)
    else:
        raise ValueError("Unsupported archive type")

    archive_name.unlink()
    print("Done.")

def setup_sdl():
    print("---Begining sdl setup---")
    if SDL_VENDOR_DIR.exists() and len(os.listdir(SDL_VENDOR_DIR)) > 0:
        print(f"{SDL_VENDOR_DIR} already exists. Skipping download.")
        return

    SDL_VENDOR_DIR.mkdir(parents=True, exist_ok=True)

    system = platform.system()
    if system == "Windows":
        url = f"https://github.com/libsdl-org/SDL/releases/download/release-{SDL_VERSION}/SDL3-devel-{SDL_VERSION}-VC.zip"
        archive_type = "zip"
    elif system == "Darwin":
        url = f"https://github.com/libsdl-org/SDL/releases/download/release-{SDL_VERSION}/SDL3-{SDL_VERSION}.dmg"
        print("DMG installer not yet supported. Please install via Homebrew: `brew install sdl3`")
        return
    elif system == "Linux":
        url = f"https://github.com/libsdl-org/SDL/releases/download/release-{SDL_VERSION}/SDL3-{SDL_VERSION}.tar.gz"
        archive_type = "tar.gz"
    else:
        raise RuntimeError("Unsupported OS")

    download_and_extract(url, SDL_VENDOR_DIR, archive_type)

    # (Windows) move the extracted folder contents up
    if system == "Windows":
        subdirs = list(SDL_VENDOR_DIR.glob("SDL3*"))
        if subdirs:
            extracted_dir = subdirs[0]
            for item in extracted_dir.iterdir():
                shutil.move(str(item), str(SDL_VENDOR_DIR))
            shutil.rmtree(extracted_dir)

    print(f"SDL setup complete in {SDL_VENDOR_DIR}")
    
def setup_imgui():
    print("---Begining imgui setup---")
    if IMGUI_VENDOR_DIR.exists() and len(os.listdir(IMGUI_VENDOR_DIR)) > 0:
        print(f"{IMGUI_VENDOR_DIR} already exists. Skipping download.")
        return

    IMGUI_VENDOR_DIR.mkdir(parents=True, exist_ok=True)

    system = platform.system()
    if system == "Windows":
        url = f"{IMGUI_REPO}/archive/refs/tags/{IMGUI_VERSION}.zip"
        archive_type = "zip"
    else:
        url = f"{IMGUI_REPO}/archive/refs/tags/{IMGUI_VERSION}.tar.gz"
        archive_type = "tar.gz"

    download_and_extract(url, IMGUI_VENDOR_DIR, archive_type)

    # Move contents up from imgui-<version>/ to vendors/imgui/
    extracted_folder = IMGUI_VENDOR_DIR / f"imgui-{IMGUI_VERSION.lstrip('v')}"
    if extracted_folder.exists():
        for item in extracted_folder.iterdir():
            shutil.move(str(item), str(IMGUI_VENDOR_DIR))
        shutil.rmtree(extracted_folder)

    print(f"ImGui setup complete in {IMGUI_VENDOR_DIR}")
    
def copy_sdl_dll(sdl_platform):
    src = Path(f"vendors/sdl/lib/{sdl_platform}/SDL3.dll")
    dst_dir = Path("build")
    dst = dst_dir / src.name

    # Create the destination directory if it doesn't exist
    dst_dir.mkdir(parents=True, exist_ok=True)

    try:
        shutil.copy2(src, dst)
        print(f"Copied {src} → {dst}")
    except FileNotFoundError:
        print(f"Error: Source file {src} not found.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        
def get_architecture():
    arch = platform.machine().lower()
    if 'arm' in arch:
        return 'ARM'
    elif 'x86_64' in arch or 'amd64' in arch:
        return 'x64'
    elif 'i386' in arch or 'i686' in arch:
        return 'x86'
    else:
        return f'Unknown ({arch})'
    
def build_main():
    src = [
        "src/main.cpp",
        "vendors/imgui/imgui.cpp",
        "vendors/imgui/imgui_draw.cpp",
        "vendors/imgui/imgui_widgets.cpp",
        "vendors/imgui/imgui_tables.cpp",
        "vendors/imgui/backends/imgui_impl_sdl3.cpp",
        "vendors/imgui/backends/imgui_impl_sdlrenderer3.cpp",  # your SDL3 backend here
    ]
    includes = [
        "-Ivendors/imgui",
        "-Ivendors/imgui/backends",
        "-Ivendors/sdl/include",
    ]
    platform_flags = []
    system = platform.system()
    machine = platform.machine().lower()


    
    if platform.system() == "Linux":
        platform_flags += ["-lSDL3", "-lGL"]
        copy_sdl_dll("x64")
    elif platform.system() == "Darwin":
        platform_flags += ["-L/opt/homebrew/lib",
                           "-I/opt/homebrew/include",
                           "-lSDL3", "-framework",
                           "OpenGL"]
        copy_sdl_dll("x64")
    elif platform.system() == "Windows":
        if "arm" in machine:
            sdl_arch = "arm64"
        else:
            sdl_arch = "x64"

        platform_flags += [
            f"-Lvendors/sdl/lib/{sdl_arch}",
            "-lSDL3",
            "-lopengl32"
        ]
        copy_sdl_dll(sdl_arch)


        
    Path("build").mkdir(exist_ok=True)

    cmd = ["g++", "-std=c++17", "-O2"] + src + includes + platform_flags + ["-o", "build/app"]
    print("Building:\n", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
    except:
        print("error")
    print("Build complete: run `build/app.exe`")
    subprocess.run("cd build && dir")
    
    
def main():
    setup_sdl()
    setup_imgui()
    build_main()
    
if __name__ == "__main__":
    main()
