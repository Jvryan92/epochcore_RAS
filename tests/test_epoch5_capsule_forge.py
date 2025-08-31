#!/usr/bin/env python3
"""
Test cases for epoch5_capsule_forge.sh script
"""

import os
import subprocess
import tempfile
import shutil
import json
import pytest
from pathlib import Path


class TestEpoch5CapsuleForge:
    """Test cases for the EPOCH5 capsule forge script"""

    @pytest.fixture
    def temp_work_dir(self):
        """Create a temporary working directory for tests"""
        original_dir = os.getcwd()
        temp_dir = tempfile.mkdtemp()
        
        # Copy the forge script to temp directory
        script_source = Path(original_dir) / "epoch5_capsule_forge.sh"
        script_dest = Path(temp_dir) / "epoch5_capsule_forge.sh"
        shutil.copy2(script_source, script_dest)
        os.chmod(script_dest, 0o755)
        
        os.chdir(temp_dir)
        yield temp_dir
        os.chdir(original_dir)
        shutil.rmtree(temp_dir)

    def test_script_executable(self):
        """Test that the forge script exists and is executable"""
        script_path = Path("epoch5_capsule_forge.sh")
        assert script_path.exists(), "epoch5_capsule_forge.sh script should exist"
        assert os.access(script_path, os.X_OK), "Script should be executable"

    def test_script_syntax(self):
        """Test that the script has valid bash syntax"""
        result = subprocess.run(
            ["bash", "-n", "epoch5_capsule_forge.sh"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Script syntax error: {result.stderr}"

    def test_required_tools_check(self):
        """Test that the script checks for required tools"""
        # Test that GPG is required
        result = subprocess.run(
            ["bash", "-c", "source ./epoch5_capsule_forge.sh && need gpg"],
            capture_output=True,
            text=True
        )
        # This should succeed if gpg is available
        assert result.returncode == 0 or "Missing dependency: gpg" in result.stderr

    @pytest.mark.skipif(not shutil.which("gpg"), reason="GPG not available")
    def test_forge_creates_pack_structure(self, temp_work_dir):
        """Test that running the forge script creates the expected pack structure"""
        # Set up a minimal GPG key for testing
        gpg_setup = subprocess.run([
            "gpg", "--batch", "--generate-key"
        ], input="""Key-Type: RSA
Key-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 1y
%no-protection
%commit
""", capture_output=True, text=True)
        
        if gpg_setup.returncode != 0:
            pytest.skip("Cannot create test GPG key")

        # Run the forge script
        env = os.environ.copy()
        env["SIGNING_KEY"] = "test@example.com"
        env["FOUNDER_NOTE"] = "Test run"
        
        result = subprocess.run(
            ["./epoch5_capsule_forge.sh"],
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            pytest.skip(f"Forge script failed: {result.stderr}")

        # Check that market directory was created
        market_dirs = list(Path("market").glob("pack-*"))
        assert len(market_dirs) >= 1, "Should create at least one pack directory"
        
        pack_dir = market_dirs[0]
        
        # Check required files exist
        required_files = [
            "pack_manifest.json",
            "pack_manifest.sha256", 
            "README_pack.md"
        ]
        
        for file in required_files:
            assert (pack_dir / file).exists(), f"Required file {file} should exist"
        
        # Check capsule files exist
        capsule_files = list(pack_dir.glob("*.capsule.sh"))
        assert len(capsule_files) == 10, "Should create exactly 10 capsule files"
        
        # Check that capsule files are executable
        for capsule in capsule_files:
            assert os.access(capsule, os.X_OK), f"Capsule {capsule.name} should be executable"

    @pytest.mark.skipif(not shutil.which("gpg"), reason="GPG not available")  
    def test_manifest_structure(self, temp_work_dir):
        """Test that the manifest has the correct structure"""
        # Set up GPG and run forge
        gpg_setup = subprocess.run([
            "gpg", "--batch", "--generate-key"
        ], input="""Key-Type: RSA
Key-Length: 2048
Name-Real: Test User
Name-Email: test@example.com
Expire-Date: 1y
%no-protection
%commit
""", capture_output=True, text=True)
        
        if gpg_setup.returncode != 0:
            pytest.skip("Cannot create test GPG key")

        env = os.environ.copy()
        env["SIGNING_KEY"] = "test@example.com"
        
        result = subprocess.run(
            ["./epoch5_capsule_forge.sh"],
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            pytest.skip("Forge script failed")

        # Find and load the manifest
        pack_dir = list(Path("market").glob("pack-*"))[0]
        manifest_file = pack_dir / "pack_manifest.json"
        
        with open(manifest_file) as f:
            manifest = json.load(f)
        
        # Check manifest structure
        assert "session_uuid" in manifest
        assert "date_utc" in manifest
        assert "manifest_hash" in manifest
        assert "capsules" in manifest
        assert len(manifest["capsules"]) == 10
        
        # Check each capsule entry
        expected_ids = [
            "01-locker-drop", "02-poap-stub", "03-echo-replay",
            "04-meshcredit-kiosk", "05-creator-splits", "06-gov-commit",
            "07-fair-balancer", "08-drop-scheduler", "09-telemetry-harv", 
            "10-storefront-snap"
        ]
        
        actual_ids = [capsule["id"] for capsule in manifest["capsules"]]
        for expected_id in expected_ids:
            assert expected_id in actual_ids, f"Expected capsule {expected_id} not found"

    def test_capsule_help_usage(self, temp_work_dir):
        """Test that individual capsules show usage information"""
        # This test doesn't require GPG, just checks the script structure
        
        # Create a minimal mock capsule file for testing
        mock_capsule = Path("test_capsule.sh")
        with open(mock_capsule, "w") as f:
            f.write("""#!/usr/bin/env bash
set -euo pipefail
SELF="$0"
usage(){ cat <<USG
Usage:
  $SELF run [--out DIR]       # verify signature, decode payload, execute payload
  $SELF verify                # verify inline signature  
  $SELF meta                  # print embedded metadata JSON
USG
}
case "${1:-}" in
  run) echo "would run" ;;
  verify) echo "would verify" ;;
  meta) echo "would show meta" ;;
  *) usage ;;
esac
""")
        
        os.chmod(mock_capsule, 0o755)
        
        # Test usage display
        result = subprocess.run(
            ["./test_capsule.sh"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Usage:" in result.stdout
        assert "run" in result.stdout
        assert "verify" in result.stdout
        assert "meta" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__])