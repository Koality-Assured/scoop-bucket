import json
from pathlib import Path
import subprocess
import sys

def main():
    manifest_path = Path("bucket/harness.json")
    if not manifest_path.exists():
        sys.exit("bucket/harness.json not found")

    content = json.loads(manifest_path.read_text(encoding="utf-8"))
    version = content.get("version")
    if not version:
        sys.exit("Version not found in bucket/harness.json")

    arch = content.get("architecture", {})
    hashes = {}
    for arch_name, info in arch.items():
        url = info.get("url", "")
        asset_name = url.split("/")[-1]
        hashes[asset_name] = info.get("hash")

    print(f"Manifest references {len(hashes)} assets for v{version}:")
    for asset, sha in hashes.items():
        print(f"  {asset}: {sha}")

    out = subprocess.check_output(
        ["gh", "release", "view", f"v{version}", "-R", "Koality-Assured/harness-cli", "--json", "assets"],
        text=True
    )
    assets_data = json.loads(out).get("assets", [])
    release_assets = {a["name"]: a["digest"].replace("sha256:", "") for a in assets_data if a.get("digest")}

    for asset, sha in hashes.items():
        expected = release_assets.get(asset)
        if not expected:
            sys.exit(f"Asset {asset} not found in release v{version}")
        if sha != expected:
            sys.exit(f"Checksum mismatch for {asset}: manifest has {sha}, release has {expected}")

    print("All Scoop manifest checksums verified successfully against official release assets.")

if __name__ == "__main__":
    main()
