#!/usr/bin/env bash
# EpochCore Business Ownership Verification System
# Creates SHA256 proof-of-work records with EIN verification

set -euo pipefail

# Configuration
BUSINESS_NAME="EpochCore"
BUSINESS_EIN="${EPOCHCORE_EIN:-}"  # Set EPOCHCORE_EIN env var with your EIN
OWNER="John Ryan"
LOCATION="Charlotte NC"
ROOT_DIR="${PWD}"
PROOF_DIR="$ROOT_DIR/.proof_of_work"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Create proof directory
mkdir -p "$PROOF_DIR"/{hashes,manifests,timestamps}

# Helper functions
sha256_file() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    else
        shasum -a 256 "$1" | awk '{print $1}'
    fi
}

sha256_string() {
    echo -n "$1" | (command -v sha256sum >/dev/null 2>&1 && sha256sum || shasum -a 256) | awk '{print $1}'
}

create_manifest() {
    local manifest="$PROOF_DIR/manifests/manifest_${TIMESTAMP}.json"
    
    # Generate file inventory with hashes
    {
        echo "{"
        echo "  \"business\": \"$BUSINESS_NAME\","
        echo "  \"ein\": \"$BUSINESS_EIN\","
        echo "  \"owner\": \"$OWNER\","
        echo "  \"location\": \"$LOCATION\","
        echo "  \"timestamp\": \"$TIMESTAMP\","
        echo "  \"files\": {"
        
        first=true
        while IFS= read -r -d '' file; do
            rel_path="${file#$ROOT_DIR/}"
            [[ "$rel_path" == .proof_of_work/* ]] && continue
            hash=$(sha256_file "$file")
            
            $first || echo ","
            first=false
            printf '    "%s": "%s"' "$rel_path" "$hash"
        done < <(find "$ROOT_DIR" -type f -print0 | sort -z)
        
        echo
        echo "  }"
        echo "}"
    } > "$manifest"
    
    # Create proof hash
    local proof_hash=$(sha256_file "$manifest")
    echo "$proof_hash" > "$PROOF_DIR/hashes/proof_${TIMESTAMP}.sha256"
    
    # Create timestamp record
    cat > "$PROOF_DIR/timestamps/record_${TIMESTAMP}.txt" <<EOL
BUSINESS: $BUSINESS_NAME
EIN: $BUSINESS_EIN
OWNER: $OWNER
LOCATION: $LOCATION
TIMESTAMP: $TIMESTAMP
MANIFEST: $(basename "$manifest")
PROOF HASH: $proof_hash
EOL
    
    echo "Created proof of work:"
    echo "- Timestamp: $TIMESTAMP"
    echo "- Proof Hash: $proof_hash"
    echo "- Manifest: $manifest"
    echo "- Record: $PROOF_DIR/timestamps/record_${TIMESTAMP}.txt"
}

verify_proof() {
    local timestamp="$1"
    local manifest="$PROOF_DIR/manifests/manifest_${timestamp}.json"
    local hash_file="$PROOF_DIR/hashes/proof_${timestamp}.sha256"
    
    if [[ ! -f "$manifest" || ! -f "$hash_file" ]]; then
        echo "Error: Proof files not found for timestamp: $timestamp"
        return 1
    fi
    
    local stored_hash=$(cat "$hash_file")
    local current_hash=$(sha256_file "$manifest")
    
    if [[ "$stored_hash" == "$current_hash" ]]; then
        echo "✅ Proof verified for $timestamp"
        echo "Hash: $current_hash"
        return 0
    else
        echo "❌ Proof verification failed for $timestamp"
        echo "Expected: $stored_hash"
        echo "Current:  $current_hash"
        return 1
    fi
}

list_proofs() {
    echo "Proof of Work Records:"
    echo "======================"
    for record in "$PROOF_DIR"/timestamps/record_*.txt; do
        [[ -f "$record" ]] || continue
        echo
        cat "$record"
    done
}

# Command processing
cmd="${1:-create}"
case "$cmd" in
    create)
        if [[ -z "$BUSINESS_EIN" ]]; then
            echo "Error: EPOCHCORE_EIN environment variable must be set"
            exit 1
        fi
        create_manifest
        ;;
    verify)
        timestamp="${2:-}"
        if [[ -z "$timestamp" ]]; then
            echo "Error: Timestamp required for verification"
            echo "Usage: $0 verify TIMESTAMP"
            exit 1
        fi
        verify_proof "$timestamp"
        ;;
    list)
        list_proofs
        ;;
    *)
        echo "Usage: $0 {create|verify TIMESTAMP|list}"
        exit 1
        ;;
esac
