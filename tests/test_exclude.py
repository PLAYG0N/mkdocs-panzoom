"""Test the exclude module functionality."""

from mkdocs_panzoom_plugin.exclude import exclude


class TestExcludeFunctionality:
    """Test file exclusion functionality."""

    def test_exclude_no_patterns(self):
        """Test with no exclusion patterns."""
        result = exclude("test.md", [])
        assert result is False

    def test_exclude_exact_match(self):
        """Test exact file path match."""
        patterns = ["test.md", "other.md"]

        assert exclude("test.md", patterns) is True
        assert exclude("other.md", patterns) is True
        assert exclude("different.md", patterns) is False

    def test_exclude_directory_paths(self):
        """Test exclusion with directory paths."""
        patterns = ["docs/excluded.md", "examples/test.md"]

        assert exclude("docs/excluded.md", patterns) is True
        assert exclude("examples/test.md", patterns) is True
        assert exclude("docs/included.md", patterns) is False

    def test_exclude_nested_paths(self):
        """Test exclusion with nested directory paths."""
        patterns = ["deep/nested/path/file.md"]

        assert exclude("deep/nested/path/file.md", patterns) is True
        assert exclude("deep/nested/different/file.md", patterns) is False

    def test_exclude_wildcard_patterns(self):
        """Test exclusion with wildcard patterns."""
        patterns = ["*.tmp", "temp/*", "*/cache.md"]

        assert exclude("file.tmp", patterns) is True
        assert exclude("temp/anything.md", patterns) is True
        assert exclude("any/cache.md", patterns) is True
        assert exclude("file.md", patterns) is False

    def test_exclude_glob_patterns(self):
        """Test exclusion with glob-style patterns."""
        patterns = ["test*.md", "**/temp.md", "docs/**/*.tmp"]

        assert exclude("test1.md", patterns) is True
        assert exclude("test_file.md", patterns) is True
        assert exclude("deep/path/temp.md", patterns) is True
        assert exclude("docs/any/deep/file.tmp", patterns) is True
        assert exclude("other.md", patterns) is False

    def test_exclude_case_sensitivity(self):
        """Test case sensitivity in exclusion patterns."""
        patterns = ["Test.md", "UPPER.MD"]

        # Should be case sensitive
        assert exclude("Test.md", patterns) is True
        assert exclude("test.md", patterns) is False
        assert exclude("UPPER.MD", patterns) is True
        assert exclude("upper.md", patterns) is False

    def test_exclude_empty_file_path(self):
        """Test exclusion with empty file path."""
        patterns = ["test.md"]

        result = exclude("", patterns)
        assert result is False

    def test_exclude_empty_pattern(self):
        """Test exclusion with empty pattern in list."""
        patterns = ["", "test.md"]

        assert exclude("test.md", patterns) is True
        assert exclude("other.md", patterns) is False

    def test_exclude_special_characters(self):
        """Test exclusion with special characters in paths."""
        patterns = ["file-with-dashes.md", "file_with_underscores.md", "file with spaces.md"]

        assert exclude("file-with-dashes.md", patterns) is True
        assert exclude("file_with_underscores.md", patterns) is True
        assert exclude("file with spaces.md", patterns) is True

    def test_exclude_forward_vs_backward_slashes(self):
        """Test exclusion with different slash types."""
        patterns = ["path/to/file.md"]

        # Should handle forward slashes
        assert exclude("path/to/file.md", patterns) is True

        # Test with backslashes (if system supports)
        assert exclude("path\\to\\file.md", patterns) is False  # Different separator

    def test_exclude_relative_paths(self):
        """Test exclusion with relative path patterns."""
        patterns = ["./docs/file.md", "../parent/file.md"]

        assert exclude("./docs/file.md", patterns) is True
        assert exclude("../parent/file.md", patterns) is True
        assert exclude("docs/file.md", patterns) is False

    def test_exclude_multiple_matches(self):
        """Test file matching multiple patterns."""
        patterns = ["*.md", "test.*", "test.md"]

        # File matches multiple patterns, should still return True
        assert exclude("test.md", patterns) is True

    def test_exclude_performance_many_patterns(self):
        """Test exclusion performance with many patterns."""
        patterns = [f"file{i}.md" for i in range(1000)]
        patterns.append("target.md")

        # Should efficiently find the match
        assert exclude("target.md", patterns) is True
        assert exclude("notfound.md", patterns) is False

    def test_exclude_unicode_paths(self):
        """Test exclusion with unicode characters in paths."""
        patterns = ["файл.md", "文档.md", "café.md"]

        assert exclude("файл.md", patterns) is True
        assert exclude("文档.md", patterns) is True
        assert exclude("café.md", patterns) is True
        assert exclude("regular.md", patterns) is False
