import re
from typing import List, Dict, Optional, Tuple


class MarkdownBookParser:
    """Auto-detecting markdown parser for books with chapters"""
    
    def __init__(self, markdown_content: str):
        self.content = markdown_content
        self.lines = markdown_content.split('\n')
        self.detected_pattern = None
    
    def detect_book_title(self, provided_title: str = None, filename: str = None) -> str:
        """
        Auto-detect book title using multiple patterns.
        Returns detected title or provided_title or filename-based title.
        """
        if provided_title:
            return provided_title.strip()
        
        # Pattern 1: Bible format - # ** The Book of {Name} **
        pattern1 = r'#\s*\*\*\s*The\s+Book\s+of\s+([^*]+?)\s*\*\*'
        match = re.search(pattern1, self.content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Pattern 2: Standard H1 with "Book" - # The Book of {Name} or # Book: {Name}
        pattern2 = r'#\s+(?:The\s+)?Book(?:\s+of)?\s*:?\s*(.+)'
        match = re.search(pattern2, self.content, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # Remove markdown formatting
            title = re.sub(r'\*\*|\*|__|_', '', title).strip()
            if title:
                return title
        
        # Pattern 3: Simple H1 - # {Book Name}
        # Get first H1 that looks like a title (not a chapter)
        for line in self.lines[:50]:  # Check first 50 lines
            if line.strip().startswith('# '):
                title = line.strip()[2:].strip()
                # Remove markdown formatting
                title = re.sub(r'\*\*|\*|__|_', '', title).strip()
                # Skip if it looks like a chapter marker
                if not re.match(r'^(Chapter\s+)?\d+', title, re.IGNORECASE):
                    if title and len(title) < 100:  # Reasonable title length
                        return title
        
        # Fallback: Use filename
        if filename:
            # Remove extension and clean up
            title = filename.rsplit('.', 1)[0] if '.' in filename else filename
            title = title.replace('_', ' ').replace('-', ' ').title()
            return title
        
        return "Untitled Book"
    
    def detect_chapter_pattern(self) -> Tuple[str, List[Dict]]:
        """
        Auto-detect which chapter pattern is used.
        Returns: (pattern_type, list of chapter matches)
        """
        chapter_matches = []
        
        # Pattern 1: Bible format - __[{BookName} {Number}]__
        pattern1 = r'__\[([^\]]+?)\s+(\d+)\]__'
        matches1 = list(re.finditer(pattern1, self.content))
        if matches1:
            # Validate: check if numbers are sequential
            numbers = [int(m.group(2)) for m in matches1]
            if self._is_sequential(numbers):
                self.detected_pattern = 'bible_format'
                for match in matches1:
                    chapter_matches.append({
                        'line_number': self.content[:match.start()].count('\n') + 1,
                        'match_text': match.group(0),
                        'book_name': match.group(1).strip(),
                        'chapter_number': int(match.group(2)),
                        'chapter_title': f"{match.group(1).strip()} {match.group(2)}"
                    })
                return 'bible_format', chapter_matches
        
        # Pattern 2: Standard H1 - # Chapter {Number} or # Chapter {Number}: {Title}
        pattern2 = r'^#\s+Chapter\s+(\d+)(?:\s*:\s*(.+))?'
        matches2 = []
        for i, line in enumerate(self.lines):
            match = re.match(pattern2, line.strip(), re.IGNORECASE)
            if match:
                matches2.append({
                    'line_number': i + 1,
                    'match_text': line.strip(),
                    'chapter_number': int(match.group(1)),
                    'chapter_title': match.group(2).strip() if match.group(2) else f"Chapter {match.group(1)}"
                })
        if matches2:
            numbers = [m['chapter_number'] for m in matches2]
            if self._is_sequential(numbers):
                self.detected_pattern = 'h1_chapter'
                return 'h1_chapter', matches2
        
        # Pattern 3: Standard H2 - ## Chapter {Number} or ## {Number}
        pattern3 = r'^##\s+(?:Chapter\s+)?(\d+)(?:\s*:\s*(.+))?'
        matches3 = []
        for i, line in enumerate(self.lines):
            match = re.match(pattern3, line.strip())
            if match:
                matches3.append({
                    'line_number': i + 1,
                    'match_text': line.strip(),
                    'chapter_number': int(match.group(1)),
                    'chapter_title': match.group(2).strip() if match.group(2) else f"Chapter {match.group(1)}"
                })
        if matches3:
            numbers = [m['chapter_number'] for m in matches3]
            if self._is_sequential(numbers):
                self.detected_pattern = 'h2_chapter'
                return 'h2_chapter', matches3
        
        # Pattern 4: Numbered H1/H2 - # 1, # 2 or ## 1, ## 2
        pattern4 = r'^#{1,2}\s+(\d+)(?:\s+(.+))?'
        matches4 = []
        for i, line in enumerate(self.lines):
            match = re.match(pattern4, line.strip())
            if match:
                # Skip if it's the book title (usually first H1)
                if i == 0 or (i < 5 and not re.search(r'chapter|ch\.', line, re.IGNORECASE)):
                    continue
                matches4.append({
                    'line_number': i + 1,
                    'match_text': line.strip(),
                    'chapter_number': int(match.group(1)),
                    'chapter_title': match.group(2).strip() if match.group(2) else f"Chapter {match.group(1)}"
                })
        if matches4:
            numbers = [m['chapter_number'] for m in matches4]
            if self._is_sequential(numbers) and len(matches4) >= 2:
                self.detected_pattern = 'numbered_heading'
                return 'numbered_heading', matches4
        
        # Pattern 5: Bracketed format - [Chapter {Number}] or [{Number}]
        pattern5 = r'\[(?:Chapter\s+)?(\d+)\]'
        matches5 = []
        for i, line in enumerate(self.lines):
            match = re.search(pattern5, line)
            if match:
                matches5.append({
                    'line_number': i + 1,
                    'match_text': line.strip(),
                    'chapter_number': int(match.group(1)),
                    'chapter_title': f"Chapter {match.group(1)}"
                })
        if matches5:
            numbers = [m['chapter_number'] for m in matches5]
            if self._is_sequential(numbers) and len(matches5) >= 2:
                self.detected_pattern = 'bracketed'
                return 'bracketed', matches5
        
        # Pattern 6: Generic numbered list - 1. Chapter Title
        pattern6 = r'^(\d+)\.\s+(.+)'
        matches6 = []
        for i, line in enumerate(self.lines):
            match = re.match(pattern6, line.strip())
            if match:
                matches6.append({
                    'line_number': i + 1,
                    'match_text': line.strip(),
                    'chapter_number': int(match.group(1)),
                    'chapter_title': match.group(2).strip()
                })
        if matches6:
            numbers = [m['chapter_number'] for m in matches6]
            if self._is_sequential(numbers) and len(matches6) >= 2:
                self.detected_pattern = 'numbered_list'
                return 'numbered_list', matches6
        
        # No pattern detected
        return None, []
    
    def _is_sequential(self, numbers: List[int], tolerance: int = 2) -> bool:
        """Check if numbers are sequential (allowing small gaps)"""
        if len(numbers) < 2:
            return False
        sorted_nums = sorted(set(numbers))
        # Check if numbers are mostly sequential
        gaps = [sorted_nums[i+1] - sorted_nums[i] for i in range(len(sorted_nums)-1)]
        # Allow gaps of 1 (sequential) or small gaps (tolerance)
        return all(gap <= tolerance for gap in gaps) and sorted_nums[0] == 1
    
    def parse_chapters(self, book_title: str = None) -> List[Dict]:
        """
        Parse all chapters from markdown.
        Returns: List of {chapter_number, chapter_title, content, content_order}
        """
        pattern_type, chapter_matches = self.detect_chapter_pattern()
        
        if not chapter_matches:
            return []
        
        chapters = []
        lines = self.lines
        
        for idx, match_info in enumerate(chapter_matches):
            chapter_number = match_info['chapter_number']
            chapter_title = match_info['chapter_title']
            start_line = match_info['line_number'] - 1  # Convert to 0-based index
            
            # Find end line (next chapter marker or end of file)
            if idx + 1 < len(chapter_matches):
                end_line = chapter_matches[idx + 1]['line_number'] - 1
            else:
                end_line = len(lines)
            
            # Extract content (include the chapter marker line)
            chapter_lines = lines[start_line:end_line]
            content = '\n'.join(chapter_lines)
            
            # Count verses if Bible format (optional)
            verse_count = None
            if pattern_type == 'bible_format':
                verse_count = self.count_verses_in_chapter(content, chapter_number)
            
            chapters.append({
                'chapter_number': chapter_number,
                'chapter_title': chapter_title,
                'content': content,
                'content_order': chapter_number,
                'verse_count': verse_count,
                'metadata': {
                    'pattern_type': pattern_type,
                    'raw_marker': match_info['match_text']
                }
            })
        
        return chapters
    
    def count_verses_in_chapter(self, content: str, chapter_number: int) -> Optional[int]:
        """Count verses in content (for Bible format: {chapter:verse})"""
        pattern = rf'\{{{chapter_number}:\d+\}}'
        matches = re.findall(pattern, content)
        return len(matches) if matches else None
    
    def get_parsing_info(self) -> Dict:
        """Get information about the parsing process"""
        return {
            'pattern_detected': self.detected_pattern,
            'total_lines': len(self.lines),
            'content_length': len(self.content)
        }

