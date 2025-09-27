#!/usr/bin/env python3
"""
Test script to analyze Confluence page metadata
"""

import json
from confluence_client import ConfluenceClient, load_config

def analyze_page_metadata(page_id: str):
    """Analyze and display page metadata structure"""
    config = load_config()
    client = ConfluenceClient(config['base_url'], config['username'], config['api_token'])

    try:
        # Get page with metadata
        page_data = client.get_page_with_metadata(page_id)

        print("=== Page Metadata Analysis ===")
        print(f"Title: {page_data.get('title')}")
        print(f"ID: {page_data.get('id')}")
        print(f"Type: {page_data.get('type')}")
        print(f"Status: {page_data.get('status')}")
        print(f"Space: {page_data.get('space', {}).get('name')}")

        # Version information
        version = page_data.get('version', {})
        print(f"\n=== Version Info ===")
        print(f"Version Number: {version.get('number')}")
        print(f"Created Date: {version.get('when')}")
        print(f"Created By: {version.get('by', {}).get('displayName')}")
        print(f"Message: {version.get('message', 'No message')}")

        # History information
        history = page_data.get('history', {})
        print(f"\n=== History Info ===")
        print(f"Created Date: {history.get('createdDate')}")
        print(f"Created By: {history.get('createdBy', {}).get('displayName')}")

        last_updated = history.get('lastUpdated', {})
        print(f"Last Updated: {last_updated.get('when')}")
        print(f"Last Updated By: {last_updated.get('by', {}).get('displayName')}")

        # Contributors
        contributors = history.get('contributors', {})
        if contributors.get('publishers'):
            print("\n=== Contributors ===")
            for contributor in contributors['publishers']['users']:
                print(f"- {contributor.get('displayName')} ({contributor.get('username')})")

        # Metadata
        metadata = page_data.get('metadata', {})
        if metadata:
            print(f"\n=== Metadata ===")
            if 'labels' in metadata:
                labels = metadata['labels']['results']
                print(f"Labels: {[label['name'] for label in labels]}")

            if 'properties' in metadata:
                print(f"Properties: {metadata['properties']}")

        # Full JSON structure (for debugging)
        print(f"\n=== Full Structure (Keys) ===")
        print(f"Top-level keys: {list(page_data.keys())}")

        # Save full data for inspection
        with open('page_metadata_full.json', 'w', encoding='utf-8') as f:
            json.dump(page_data, f, indent=2, ensure_ascii=False)
        print(f"\nFull metadata saved to: page_metadata_full.json")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test with the meeting page
    analyze_page_metadata("163842")