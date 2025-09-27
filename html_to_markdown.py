#!/usr/bin/env python3
"""
HTML to Markdown Converter

Converts Confluence HTML content to Markdown format.
Handles Confluence-specific elements and formatting.
"""

import re
from typing import Dict, List, Optional
from html import unescape
import html2text


class ConfluenceMarkdownConverter:
    """Converter for Confluence HTML to Markdown"""

    def __init__(self):
        self.h2t = html2text.HTML2Text()
        self._configure_html2text()

    def _configure_html2text(self):
        """Configure html2text settings for better Confluence conversion"""
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.ignore_emphasis = False
        self.h2t.body_width = 0  # No line wrapping
        self.h2t.unicode_snob = True
        self.h2t.escape_snob = True
        self.h2t.bypass_tables = False
        self.h2t.ignore_tables = False
        self.h2t.single_line_break = False

    def convert_confluence_html(self, html_content: str, title: str = "", page_metadata: Dict = None) -> str:
        """
        Convert Confluence HTML to Markdown

        Args:
            html_content: Raw HTML content from Confluence
            title: Page title
            page_metadata: Additional page metadata from Confluence API

        Returns:
            Converted Markdown content
        """
        # Pre-process Confluence-specific elements
        processed_html = self._preprocess_confluence_html(html_content)

        # Convert to markdown using html2text
        markdown = self.h2t.handle(processed_html)

        # Post-process the markdown
        markdown = self._postprocess_markdown(markdown, title, page_metadata)

        return markdown

    def _preprocess_confluence_html(self, html_content: str) -> str:
        """
        Pre-process Confluence-specific HTML elements

        Args:
            html_content: Raw HTML from Confluence

        Returns:
            Processed HTML ready for conversion
        """
        # Handle Confluence macros
        html_content = self._handle_confluence_macros(html_content)

        # Handle Confluence-specific classes and elements
        html_content = self._handle_confluence_elements(html_content)

        # Clean up common HTML issues
        html_content = self._clean_html(html_content)

        return html_content

    def _handle_confluence_macros(self, html_content: str) -> str:
        """Handle Confluence macros like info, warning, code blocks"""

        # Handle date/time elements
        html_content = re.sub(
            r'<time datetime="([^"]*)"[^>]*/>',
            r'📅 \1',
            html_content
        )

        # Handle user mentions - convert to readable format
        html_content = re.sub(
            r'<ac:link><ri:user ri:account-id="[^"]*"\s*/></ac:link>',
            r'@user',  # Generic placeholder - could be enhanced to look up actual user names from API
            html_content
        )

        # Handle Confluence emoticons/emojis
        emoji_map = {
            'calendar_spiral': '📅',
            'busts_in_silhouette': '👥',
            'goal': '🥅',
            'art': '🎨',
            'speaking_head': '🗣️',
            'white_check_mark': '✅',
            'arrow_heading_up': '⤴️',
            'card_box': '🗃️',
        }

        for shortname, emoji in emoji_map.items():
            html_content = re.sub(
                f'<ac:emoticon[^>]*ac:emoji-shortname=":{shortname}:"[^>]*/>',
                emoji,
                html_content
            )

        # Handle placeholders
        html_content = re.sub(
            r'<ac:placeholder>(.*?)</ac:placeholder>',
            r'*\1*',
            html_content,
            flags=re.DOTALL
        )

        # Info macro
        html_content = re.sub(
            r'<div[^>]*class="[^"]*aui-message[^"]*info[^"]*"[^>]*>(.*?)</div>',
            r'> ℹ️ **Info:** \1',
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Warning macro
        html_content = re.sub(
            r'<div[^>]*class="[^"]*aui-message[^"]*warning[^"]*"[^>]*>(.*?)</div>',
            r'> ⚠️ **Warning:** \1',
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Error macro
        html_content = re.sub(
            r'<div[^>]*class="[^"]*aui-message[^"]*error[^"]*"[^>]*>(.*?)</div>',
            r'> ❌ **Error:** \1',
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Success macro
        html_content = re.sub(
            r'<div[^>]*class="[^"]*aui-message[^"]*success[^"]*"[^>]*>(.*?)</div>',
            r'> ✅ **Success:** \1',
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Code macro
        html_content = re.sub(
            r'<div[^>]*class="[^"]*code[^"]*"[^>]*><pre[^>]*>(.*?)</pre></div>',
            r'```\n\1\n```',
            html_content,
            flags=re.DOTALL
        )

        # Task list items
        html_content = re.sub(
            r'<li[^>]*class="[^"]*task-list-item[^"]*"[^>]*>.*?<input[^>]*type="checkbox"[^>]*checked[^>]*>.*?<span[^>]*>(.*?)</span>.*?</li>',
            r'- [x] \1',
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )

        html_content = re.sub(
            r'<li[^>]*class="[^"]*task-list-item[^"]*"[^>]*>.*?<input[^>]*type="checkbox"[^>]*>.*?<span[^>]*>(.*?)</span>.*?</li>',
            r'- [ ] \1',
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )

        return html_content

    def _handle_confluence_elements(self, html_content: str) -> str:
        """Handle other Confluence-specific elements"""

        # Confluence panels
        html_content = re.sub(
            r'<div[^>]*class="[^"]*panel[^"]*"[^>]*>(.*?)</div>',
            r'<blockquote>\1</blockquote>',
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Confluence tables (preserve structure)
        # This is handled by html2text, but we can add specific processing if needed

        # Remove Confluence metadata
        html_content = re.sub(
            r'<div[^>]*class="[^"]*page-metadata[^"]*"[^>]*>.*?</div>',
            '',
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Remove Confluence navigation elements
        html_content = re.sub(
            r'<div[^>]*class="[^"]*ia-splitter[^"]*"[^>]*>.*?</div>',
            '',
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )

        return html_content

    def _clean_html(self, html_content: str) -> str:
        """Clean up HTML content"""

        # Remove script and style tags
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

        # Remove comments
        html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)

        # Clean up excessive whitespace
        html_content = re.sub(r'\n\s*\n\s*\n', '\n\n', html_content)

        # Unescape HTML entities
        html_content = unescape(html_content)

        return html_content

    def _postprocess_markdown(self, markdown: str, title: str = "", page_metadata: Dict = None) -> str:
        """
        Post-process the converted markdown

        Args:
            markdown: Raw markdown from conversion
            title: Page title to add as header
            page_metadata: Page metadata from Confluence API

        Returns:
            Cleaned up markdown
        """
        lines = markdown.split('\n')
        processed_lines = []

        # Add title as H1 if provided
        if title:
            processed_lines.append(f"# {title}")
            processed_lines.append("")

        # Add metadata section if provided
        if page_metadata:
            metadata_section = self._generate_metadata_section(page_metadata)
            if metadata_section:
                processed_lines.extend(metadata_section)
                processed_lines.append("")

        for line in lines:
            # Clean up excessive empty lines
            if line.strip() == '' and processed_lines and processed_lines[-1].strip() == '':
                continue

            # Fix markdown formatting issues
            line = self._fix_markdown_formatting(line)

            processed_lines.append(line)

        # Remove trailing empty lines
        while processed_lines and processed_lines[-1].strip() == '':
            processed_lines.pop()

        return '\n'.join(processed_lines)

    def _fix_markdown_formatting(self, line: str) -> str:
        """Fix common markdown formatting issues"""

        # Fix spacing around headers
        line = re.sub(r'^(#+)\s*(.+)', r'\1 \2', line)

        # Fix list formatting
        line = re.sub(r'^(\s*)-\s+', r'\1- ', line)
        line = re.sub(r'^(\s*)\*\s+', r'\1* ', line)
        line = re.sub(r'^(\s*)\d+\.\s+', lambda m: m.group(1) + re.sub(r'(\d+)\.', r'\1. ', m.group(0).strip()) + ' ', line)

        # Fix emphasis formatting
        line = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', line)
        line = re.sub(r'\*([^*]+)\*', r'*\1*', line)

        return line

    def _generate_metadata_section(self, page_metadata: Dict) -> List[str]:
        """
        Generate metadata section for the markdown

        Args:
            page_metadata: Page metadata from Confluence API

        Returns:
            List of markdown lines for metadata section
        """
        metadata_lines = []

        # Document metadata header
        metadata_lines.append("## 📄 Document Information")
        metadata_lines.append("")

        # Basic info
        if page_metadata.get('id'):
            metadata_lines.append(f"**Page ID:** {page_metadata['id']}")

        if page_metadata.get('space', {}).get('name'):
            metadata_lines.append(f"**Space:** {page_metadata['space']['name']}")

        # Version and dates
        version = page_metadata.get('version', {})
        history = page_metadata.get('history', {})

        if history.get('createdDate'):
            created_date = self._format_date(history['createdDate'])
            metadata_lines.append(f"**Created:** {created_date}")

        if history.get('createdBy', {}).get('displayName'):
            creator = history['createdBy']['displayName']
            metadata_lines.append(f"**Created by:** {creator}")

        # Last updated info
        last_updated = history.get('lastUpdated', {})
        if last_updated.get('when'):
            updated_date = self._format_date(last_updated['when'])
            metadata_lines.append(f"**Last Updated:** {updated_date}")

        if last_updated.get('by', {}).get('displayName'):
            updater = last_updated['by']['displayName']
            metadata_lines.append(f"**Last Updated by:** {updater}")

        if version.get('number'):
            metadata_lines.append(f"**Version:** {version['number']}")

        # Labels
        metadata = page_metadata.get('metadata', {})
        if metadata.get('labels', {}).get('results'):
            labels = [label['name'] for label in metadata['labels']['results']]
            labels_str = ', '.join([f"`{label}`" for label in labels])
            metadata_lines.append(f"**Labels:** {labels_str}")

        # Contributors
        contributors = history.get('contributors', {})
        if contributors.get('publishers', {}).get('users'):
            contributor_names = [user['displayName'] for user in contributors['publishers']['users']]
            if len(contributor_names) > 1:  # Don't show if only one contributor (usually the creator)
                contributors_str = ', '.join(contributor_names)
                metadata_lines.append(f"**Contributors:** {contributors_str}")

        return metadata_lines

    def _format_date(self, date_string: str) -> str:
        """
        Format ISO date string to readable format

        Args:
            date_string: ISO format date string

        Returns:
            Formatted date string
        """
        from datetime import datetime
        try:
            # Parse ISO format: 2025-09-27T10:35:38.911Z
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        except Exception:
            return date_string  # Return original if parsing fails

    def convert_to_file(self, html_content: str, title: str, output_path: str, page_metadata: Dict = None):
        """
        Convert HTML to Markdown and save to file

        Args:
            html_content: HTML content to convert
            title: Page title
            output_path: Output file path
            page_metadata: Page metadata from Confluence API
        """
        markdown = self.convert_confluence_html(html_content, title, page_metadata)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

        return output_path


def convert_html_file_to_markdown(html_file_path: str, output_path: str = None) -> str:
    """
    Convert an HTML file to Markdown

    Args:
        html_file_path: Path to HTML file
        output_path: Output markdown file path (auto-generated if None)

    Returns:
        Path to output markdown file
    """
    converter = ConfluenceMarkdownConverter()

    # Read HTML file
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Extract title from HTML if possible
    title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
    title = title_match.group(1) if title_match else ""

    # Generate output path if not provided
    if output_path is None:
        output_path = html_file_path.rsplit('.', 1)[0] + '.md'

    # Convert and save
    converter.convert_to_file(html_content, title, output_path)

    return output_path


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description='Convert HTML to Markdown')
    parser.add_argument('input_file', help='Input HTML file path')
    parser.add_argument('-o', '--output', help='Output markdown file path')
    parser.add_argument('--title', help='Page title to add as header')

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        exit(1)

    try:
        output_path = convert_html_file_to_markdown(args.input_file, args.output)
        print(f"Converted to: {output_path}")
    except Exception as e:
        print(f"Error converting file: {e}")
        exit(1)