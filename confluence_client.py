#!/usr/bin/env python3
"""
Confluence Document Retrieval Tool

This script connects to Confluence and retrieves documents using the REST API.
Supports both Confluence Cloud and Server instances.
"""

import requests
from requests.auth import HTTPBasicAuth
import json
import os
from typing import Dict, List, Optional
import argparse
import yaml
from dotenv import load_dotenv
from html_to_markdown import ConfluenceMarkdownConverter


class ConfluenceClient:
    """Client for accessing Confluence REST API"""

    def __init__(self, base_url: str, username: str, api_token: str):
        """
        Initialize Confluence client

        Args:
            base_url: Confluence instance URL (e.g., https://yourcompany.atlassian.net)
            username: Username or email for authentication
            api_token: API token or password
        """
        self.base_url = base_url.rstrip('/')
        self.auth = HTTPBasicAuth(username, api_token)
        self.session = requests.Session()
        self.session.auth = self.auth

    def get_spaces(self) -> List[Dict]:
        """Get all available spaces"""
        url = f"{self.base_url}/rest/api/space"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json().get('results', [])

    def get_pages_in_space(self, space_key: str, limit: int = 50) -> List[Dict]:
        """
        Get pages in a specific space

        Args:
            space_key: Space key (e.g., 'DEMO')
            limit: Maximum number of pages to retrieve
        """
        url = f"{self.base_url}/rest/api/content"
        params = {
            'spaceKey': space_key,
            'type': 'page',
            'limit': limit,
            'expand': 'space,body.storage,version,ancestors'
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json().get('results', [])

    def get_page_by_id(self, page_id: str) -> Dict:
        """
        Get a specific page by ID

        Args:
            page_id: Page ID
        """
        url = f"{self.base_url}/rest/api/content/{page_id}"
        params = {
            'expand': 'space,body.storage,version,ancestors,history,metadata.labels,metadata.properties'
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_page_with_metadata(self, page_id: str) -> Dict:
        """
        Get a page with comprehensive metadata

        Args:
            page_id: Page ID
        """
        url = f"{self.base_url}/rest/api/content/{page_id}"
        params = {
            'expand': 'space,body.storage,version,ancestors,history.lastUpdated,history.contributors,metadata.labels,metadata.properties,children.comment'
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def search_content(self, query: str, limit: int = 25) -> List[Dict]:
        """
        Search for content using CQL (Confluence Query Language)

        Args:
            query: CQL query string
            limit: Maximum number of results
        """
        url = f"{self.base_url}/rest/api/content/search"
        params = {
            'cql': query,
            'limit': limit,
            'expand': 'space,body.storage,version'
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json().get('results', [])

    def get_page_content(self, page_id: str) -> str:
        """
        Get the HTML content of a page

        Args:
            page_id: Page ID
        """
        page = self.get_page_by_id(page_id)
        return page.get('body', {}).get('storage', {}).get('value', '')

    def export_page_to_file(self, page_id: str, output_dir: str = 'output'):
        """
        Export a page to a local file

        Args:
            page_id: Page ID
            output_dir: Output directory
        """
        page = self.get_page_by_id(page_id)
        title = page.get('title', 'untitled')
        content = page.get('body', {}).get('storage', {}).get('value', '')

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Sanitize filename
        filename = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filepath = os.path.join(output_dir, f"{filename}.html")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"<!DOCTYPE html>\n<html>\n<head>\n<title>{title}</title>\n</head>\n<body>\n")
            f.write(content)
            f.write("\n</body>\n</html>")

        print(f"Page exported to: {filepath}")
        return filepath

    def export_page_to_markdown(self, page_id: str, output_dir: str = 'output'):
        """
        Export a page to a Markdown file

        Args:
            page_id: Page ID
            output_dir: Output directory
        """
        # Get page with comprehensive metadata
        page = self.get_page_with_metadata(page_id)
        title = page.get('title', 'untitled')
        content = page.get('body', {}).get('storage', {}).get('value', '')

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Initialize markdown converter
        converter = ConfluenceMarkdownConverter()

        # Sanitize filename
        filename = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filepath = os.path.join(output_dir, f"{filename}.md")

        # Convert and save with metadata
        converter.convert_to_file(content, title, filepath, page)

        print(f"Page exported to Markdown: {filepath}")
        return filepath

    def export_space_to_markdown(self, space_key: str, output_dir: str = 'output', limit: int = 50):
        """
        Export all pages in a space to Markdown files

        Args:
            space_key: Space key
            output_dir: Output directory
            limit: Maximum number of pages to export
        """
        pages = self.get_pages_in_space(space_key, limit)
        exported_files = []

        # Create space-specific output directory
        space_output_dir = os.path.join(output_dir, f"space_{space_key}")
        os.makedirs(space_output_dir, exist_ok=True)

        print(f"Exporting {len(pages)} pages from space '{space_key}' to Markdown...")

        for i, page in enumerate(pages, 1):
            try:
                print(f"[{i}/{len(pages)}] Exporting: {page['title']}")
                filepath = self.export_page_to_markdown(page['id'], space_output_dir)
                exported_files.append(filepath)
            except Exception as e:
                print(f"Error exporting page '{page['title']}': {e}")

        print(f"Exported {len(exported_files)} pages to: {space_output_dir}")
        return exported_files


def load_config():
    """Load configuration from config.yaml or environment variables"""
    config = {}

    # Try to load from .env file
    load_dotenv()

    # Try to load from config.yaml
    config_file = 'config.yaml'
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            yaml_config = yaml.safe_load(f)
            if yaml_config and 'confluence' in yaml_config:
                config.update(yaml_config['confluence'])
                # Also load settings if available
                if 'settings' in yaml_config:
                    config.update(yaml_config['settings'])

    # Environment variables override config file
    if os.getenv('CONFLUENCE_URL'):
        config['base_url'] = os.getenv('CONFLUENCE_URL')
    if os.getenv('CONFLUENCE_USERNAME'):
        config['username'] = os.getenv('CONFLUENCE_USERNAME')
    if os.getenv('CONFLUENCE_API_TOKEN'):
        config['api_token'] = os.getenv('CONFLUENCE_API_TOKEN')

    return config


def main():
    """Main function for command-line usage"""
    # Load configuration first
    config = load_config()

    parser = argparse.ArgumentParser(description='Confluence Document Retrieval Tool')
    parser.add_argument('--base-url',
                       default=config.get('base_url'),
                       help='Confluence base URL (can be set in config.yaml or .env)')
    parser.add_argument('--username',
                       default=config.get('username'),
                       help='Username/email (can be set in config.yaml or .env)')
    parser.add_argument('--token',
                       default=config.get('api_token'),
                       help='API token (can be set in config.yaml or .env)')
    parser.add_argument('--space', help='Space key to list pages from')
    parser.add_argument('--page-id', help='Specific page ID to retrieve')
    parser.add_argument('--search', help='Search query (CQL)')
    parser.add_argument('--output-dir',
                       default=config.get('output_dir', 'output'),
                       help='Output directory for exported files')
    parser.add_argument('--format',
                       choices=['html', 'markdown', 'both'],
                       default='html',
                       help='Output format for exported pages')
    parser.add_argument('--export-space',
                       help='Export all pages from specified space to files')

    args = parser.parse_args()

    # Validate required arguments
    if not args.base_url:
        print("Error: --base-url is required. Set it via command line, config.yaml, or .env file")
        return 1
    if not args.username:
        print("Error: --username is required. Set it via command line, config.yaml, or .env file")
        return 1
    if not args.token:
        print("Error: --token is required. Set it via command line, config.yaml, or .env file")
        return 1

    # Initialize client
    client = ConfluenceClient(args.base_url, args.username, args.token)

    try:
        if args.export_space:
            # Export all pages from space
            print(f"Exporting all pages from space: {args.export_space}")
            if args.format in ['markdown', 'both']:
                client.export_space_to_markdown(args.export_space, args.output_dir)
            if args.format in ['html', 'both']:
                # Export to HTML as well if requested
                pages = client.get_pages_in_space(args.export_space)
                space_output_dir = os.path.join(args.output_dir, f"space_{args.export_space}")
                for page in pages:
                    client.export_page_to_file(page['id'], space_output_dir)

        elif args.space:
            # List pages in space
            print(f"Getting pages from space: {args.space}")
            pages = client.get_pages_in_space(args.space)
            for page in pages:
                print(f"- {page['title']} (ID: {page['id']})")

        elif args.page_id:
            # Get specific page
            print(f"Retrieving page ID: {args.page_id}")
            if args.format in ['html', 'both']:
                client.export_page_to_file(args.page_id, args.output_dir)
            if args.format in ['markdown', 'both']:
                client.export_page_to_markdown(args.page_id, args.output_dir)

        elif args.search:
            # Search content
            print(f"Searching for: {args.search}")
            results = client.search_content(args.search)
            for result in results:
                print(f"- {result['title']} (ID: {result['id']}, Space: {result['space']['key']})")

        else:
            # List all spaces
            print("Available spaces:")
            spaces = client.get_spaces()
            for space in spaces:
                print(f"- {space['name']} (Key: {space['key']})")

    except requests.exceptions.RequestException as e:
        print(f"Error accessing Confluence: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()