#!/usr/bin/env python3
"""
Example usage of the Confluence client
"""

from confluence_client import ConfluenceClient
import os


def example_usage():
    # Configuration - replace with your actual values
    CONFLUENCE_URL = "https://yourcompany.atlassian.net"  # or your server URL
    USERNAME = "your-email@company.com"
    API_TOKEN = "your-api-token"  # Generate from Atlassian Account Settings

    # You can also use environment variables for security
    # CONFLUENCE_URL = os.getenv('CONFLUENCE_URL')
    # USERNAME = os.getenv('CONFLUENCE_USERNAME')
    # API_TOKEN = os.getenv('CONFLUENCE_API_TOKEN')

    # Initialize client
    client = ConfluenceClient(CONFLUENCE_URL, USERNAME, API_TOKEN)

    try:
        # Example 1: List all spaces
        print("=== Available Spaces ===")
        spaces = client.get_spaces()
        for space in spaces[:5]:  # Show first 5 spaces
            print(f"Space: {space['name']} (Key: {space['key']})")

        # Example 2: Get pages from a specific space
        if spaces:
            space_key = spaces[0]['key']
            print(f"\n=== Pages in Space '{space_key}' ===")
            pages = client.get_pages_in_space(space_key, limit=10)
            for page in pages:
                print(f"Page: {page['title']} (ID: {page['id']})")

        # Example 3: Search for content
        print(f"\n=== Search Results ===")
        search_results = client.search_content("text ~ 'meeting'", limit=5)
        for result in search_results:
            print(f"Found: {result['title']} in space {result['space']['key']}")

        # Example 4: Get specific page content
        if pages:
            page_id = pages[0]['id']
            print(f"\n=== Exporting Page ===")
            client.export_page_to_file(page_id, 'exported_pages')

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure to:")
        print("1. Update the CONFLUENCE_URL, USERNAME, and API_TOKEN variables")
        print("2. Generate an API token from your Atlassian account settings")
        print("3. Ensure you have access to the Confluence instance")


if __name__ == "__main__":
    example_usage()