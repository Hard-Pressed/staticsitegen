import os
import shutil


def copy_static_to_public(src_dir="static", dst_dir="public"):
    """Recursively copy all contents from `src_dir` to `dst_dir`.

    This will remove `dst_dir` entirely first to ensure a clean copy,
    then recreate it and copy every file and subdirectory. Each copied
    file path is printed for logging.
    """
    if not os.path.exists(src_dir):
        raise FileNotFoundError(f"Source directory not found: {src_dir}")

    # Remove destination completely if it exists
    if os.path.exists(dst_dir):
        print(f"Removing existing destination: {dst_dir}")
        shutil.rmtree(dst_dir)

    # Recreate destination directory
    os.makedirs(dst_dir, exist_ok=True)

    # Walk source tree and copy files/directories
    for root, dirs, files in os.walk(src_dir):
        # Compute the relative path from the source root
        rel_path = os.path.relpath(root, src_dir)
        if rel_path == ".":
            target_root = dst_dir
        else:
            target_root = os.path.join(dst_dir, rel_path)
            os.makedirs(target_root, exist_ok=True)

        for fname in files:
            src_path = os.path.join(root, fname)
            dst_path = os.path.join(target_root, fname)
            # Copy file metadata as well
            shutil.copy2(src_path, dst_path)
            print(f"Copied: {src_path} -> {dst_path}")


if __name__ == "__main__":
    copy_static_to_public()
