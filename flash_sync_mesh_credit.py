#!/usr/bin/env python3
# Flash Sync - Mesh Credit Whitepaper Scanner
# Scans and indexes the Mesh Credit whitepaper and economy system

import datetime
import hashlib
import json
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("mesh_credit_sync.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mesh_credit_sync")


def calculate_hash(content):
    """Calculate SHA-256 hash of content"""
    return hashlib.sha256(content.encode('utf-8') if isinstance(content, str) else content).hexdigest()


def scan_directory(directory):
    """Scan a directory for files and calculate their hashes"""
    results = {}
    if not os.path.exists(directory):
        logger.warning(f"Directory not found: {directory}")
        return results

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                file_hash = calculate_hash(content)
                rel_path = os.path.relpath(file_path, directory)
                results[rel_path] = {
                    "hash": file_hash,
                    "size": len(content),
                    "last_modified": datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                }
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")

    return results


def extract_key_concepts(json_files):
    """Extract key concepts from JSON files"""
    concepts = {}

    for file_path, file_info in json_files.items():
        try:
            if not file_path.endswith('.json'):
                continue

            # Read the JSON file
            with open(os.path.join('economy/mesh_credit', file_path), 'r') as f:
                data = json.load(f)

            # Extract key concepts based on file name
            if 'manifest.json' in file_path:
                concepts['currency_details'] = {
                    "name": data.get("name"),
                    "symbol": data.get("symbol"),
                    "max_supply": data.get("properties", {}).get("max_supply"),
                    "cosmetics_only": data.get("rules", {}).get("cosmetics_only"),
                    "time_savers_only": data.get("rules", {}).get("time_savers_only"),
                    "pay_to_win": data.get("rules", {}).get("pay_to_win")
                }
                concepts['mint_triggers'] = data.get(
                    "rules", {}).get("mint_triggers", [])
                concepts['burn_triggers'] = data.get(
                    "rules", {}).get("burn_triggers", [])

            elif 'pricing.json' in file_path:
                concepts['exchange_rates'] = data.get("exchange_rates", {})
                concepts['item_categories'] = list(data.get("categories", {}).keys())
                concepts['special_offers'] = list(data.get("special_offers", {}).keys())

            elif 'yield_curve.json' in file_path:
                concepts['yield_model'] = data.get("model")
                concepts['epoch_length'] = data.get("epoch_length_days")
                concepts['validator_bonus'] = data.get("validator_bonus_rate")

            elif 'wallet_spec.json' in file_path:
                concepts['wallet_format'] = data.get(
                    "wallet_format", {}).get("encryption")
                concepts['operations'] = list(data.get("operations", {}).keys())

        except Exception as e:
            logger.error(f"Error extracting concepts from {file_path}: {str(e)}")

    return concepts


def generate_summary(scan_results, concepts):
    """Generate a summary of the scan results and concepts"""
    total_files = len(scan_results)
    total_size = sum(info['size'] for info in scan_results.values())

    summary = {
        "scan_timestamp": datetime.datetime.now().isoformat(),
        "total_files": total_files,
        "total_size_bytes": total_size,
        "file_types": {},
        "key_concepts": concepts
    }

    # Count file types
    for file_path in scan_results:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in summary["file_types"]:
            summary["file_types"][ext] += 1
        else:
            summary["file_types"][ext] = 1

    return summary


def save_results(scan_results, concepts, summary):
    """Save scan results to files"""
    os.makedirs('economy/mesh_credit/sync', exist_ok=True)

    with open('economy/mesh_credit/sync/file_inventory.json', 'w') as f:
        json.dump(scan_results, f, indent=2)

    with open('economy/mesh_credit/sync/concepts.json', 'w') as f:
        json.dump(concepts, f, indent=2)

    with open('economy/mesh_credit/sync/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    # Generate Markdown report
    with open('economy/mesh_credit/sync/mesh_credit_whitepaper_summary.md', 'w') as f:
        f.write("# Mesh Credit Whitepaper Summary\n\n")
        f.write(f"*Generated: {datetime.datetime.now().isoformat()}*\n\n")

        f.write("## System Overview\n\n")
        f.write(
            f"- **Currency Name**: {concepts.get('currency_details', {}).get('name', 'Mesh Credit')}\n")
        f.write(
            f"- **Symbol**: {concepts.get('currency_details', {}).get('symbol', 'MESH')}\n")
        f.write(
            f"- **Max Supply**: {concepts.get('currency_details', {}).get('max_supply', 'N/A')}\n")
        f.write(
            f"- **Fair-by-Design**: Cosmetics-only: {concepts.get('currency_details', {}).get('cosmetics_only', True)}, ")
        f.write(
            f"Time-savers only: {concepts.get('currency_details', {}).get('time_savers_only', True)}, ")
        f.write(
            f"Pay-to-win: {concepts.get('currency_details', {}).get('pay_to_win', False)}\n\n")

        f.write("## Tokenomics\n\n")
        f.write("### Mint Triggers\n\n")
        for trigger in concepts.get('mint_triggers', []):
            f.write(f"- {trigger}\n")

        f.write("\n### Burn Triggers\n\n")
        for trigger in concepts.get('burn_triggers', []):
            f.write(f"- {trigger}\n")

        f.write("\n## Yield Model\n\n")
        f.write(f"- **Model Type**: {concepts.get('yield_model', 'N/A')}\n")
        f.write(f"- **Epoch Length**: {concepts.get('epoch_length', 'N/A')} days\n")
        f.write(
            f"- **Validator Bonus Rate**: {concepts.get('validator_bonus', 'N/A')}\n\n")

        f.write("## Exchange Rates\n\n")
        for key, value in concepts.get('exchange_rates', {}).items():
            f.write(f"- **{key}**: {value}\n")

        f.write("\n## Supported Item Categories\n\n")
        for category in concepts.get('item_categories', []):
            f.write(f"- {category}\n")

        f.write("\n## Special Offers\n\n")
        for offer in concepts.get('special_offers', []):
            f.write(f"- {offer}\n")

        f.write("\n## Wallet Operations\n\n")
        for op in concepts.get('operations', []):
            f.write(f"- {op}\n")

        f.write("\n## Files Scanned\n\n")
        f.write(f"- Total Files: {summary['total_files']}\n")
        f.write(f"- Total Size: {summary['total_size_bytes']} bytes\n")
        f.write("- File Types:\n")
        for ext, count in summary.get('file_types', {}).items():
            f.write(f"  - {ext}: {count}\n")


def main():
    """Main function to perform the flash sync"""
    logger.info("Starting Mesh Credit Whitepaper flash sync")

    directory = 'economy/mesh_credit'

    if not os.path.exists(directory):
        logger.error(f"Mesh Credit directory not found: {directory}")
        return

    logger.info(f"Scanning directory: {directory}")
    scan_results = scan_directory(directory)
    logger.info(f"Found {len(scan_results)} files")

    logger.info("Extracting key concepts")
    concepts = extract_key_concepts(scan_results)

    logger.info("Generating summary")
    summary = generate_summary(scan_results, concepts)

    logger.info("Saving results")
    save_results(scan_results, concepts, summary)

    logger.info("Flash sync complete")
    logger.info(
        f"Summary available at: economy/mesh_credit/sync/mesh_credit_whitepaper_summary.md")


if __name__ == "__main__":
    main()
