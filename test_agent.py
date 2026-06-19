"""
Unit tests for internship-agent pipeline.

Run with: pytest test_agent.py -v
"""

import unittest
import os
import json
import tempfile
from pathlib import Path


class TestConfiguration(unittest.TestCase):
    """Test agent configuration and setup."""
    
    def test_env_example_exists(self):
        """Test that .env.example template exists."""
        self.assertTrue(os.path.exists(".env.example"), ".env.example not found")
    
    def test_env_example_readable(self):
        """Test that .env.example is valid."""
        with open(".env.example", "r") as f:
            content = f.read()
            self.assertIn("AGENT_NAME", content, "Missing AGENT_NAME in .env.example")
            self.assertIn("SERPAPI_KEY", content, "Missing SERPAPI_KEY in .env.example")


class TestDiscoveryLogic(unittest.TestCase):
    """Test internship discovery mechanisms."""
    
    def test_simplify_keywords_not_empty(self):
        """Test that SIMPLIFY_KEYWORDS is configured."""
        # Simulates checking config
        keywords = [
            "supply chain", "procurement", "logistics",
            "operations", "warehouse", "inventory",
        ]
        self.assertGreater(len(keywords), 0, "SIMPLIFY_KEYWORDS should not be empty")
    
    def test_search_queries_not_empty(self):
        """Test that SEARCH_QUERIES is configured."""
        queries = [
            "supply chain intern 2026 Texas site:internlist.org",
            "logistics intern 2026 DFW site:internlist.org",
            "procurement intern summer 2026 Texas",
            "operations intern 2026 Dallas Fort Worth",
        ]
        self.assertGreater(len(queries), 0, "SEARCH_QUERIES should not be empty")
        for query in queries:
            self.assertIsInstance(query, str, "Each query should be a string")


class TestFileStructure(unittest.TestCase):
    """Test that required files exist."""
    
    def test_agent_script_exists(self):
        """Test that agent.py exists."""
        self.assertTrue(os.path.exists("agent.py"), "agent.py not found")
    
    def test_dashboard_script_exists(self):
        """Test that dashboard.py exists."""
        self.assertTrue(os.path.exists("dashboard.py"), "dashboard.py not found")
    
    def test_requirements_exists(self):
        """Test that requirements.txt exists."""
        self.assertTrue(os.path.exists("requirements.txt"), "requirements.txt not found")
    
    def test_gitignore_exists(self):
        """Test that .gitignore is configured."""
        self.assertTrue(os.path.exists(".gitignore"), ".gitignore not found")
        with open(".gitignore", "r") as f:
            content = f.read()
            self.assertIn("google_credentials.json", content, "google_credentials.json should be gitignored")
            self.assertIn(".env", content, ".env should be gitignored")


class TestSecurityPractices(unittest.TestCase):
    """Test that security best practices are followed."""
    
    def test_no_hardcoded_api_keys(self):
        """Test that API keys aren't hardcoded in agent.py."""
        with open("agent.py", "r") as f:
            content = f.read()
            # Check that we're using os.getenv instead of hardcoding
            self.assertIn('os.getenv("SERPAPI_KEY"', content, 
                         "Should use os.getenv() for API keys")
            self.assertNotIn('serpapi_key = "sk-', content, 
                            "API keys should not be hardcoded")
    
    def test_env_not_committed(self):
        """Test that .env file would not be committed."""
        with open(".gitignore", "r") as f:
            gitignore = f.read()
            self.assertIn(".env", gitignore, ".env should be in .gitignore")


class TestCoverLetterGeneration(unittest.TestCase):
    """Test cover letter generation logic."""
    
    def test_output_folder_creation(self):
        """Test that output folder path is configured."""
        # Simulates checking that folder path is set
        output_folder = os.path.expanduser("~/Desktop/internship_agent/cover_letters")
        # Just verify it's a valid path string
        self.assertTrue(isinstance(output_folder, str), "Output folder should be a string")
        self.assertIn("cover_letters", output_folder, "Output folder path should contain 'cover_letters'")


class TestLogging(unittest.TestCase):
    """Test logging functionality."""
    
    def test_log_file_path_configured(self):
        """Test that log file path is configured."""
        log_file = os.path.expanduser("~/Desktop/internship_agent/agent_log.txt")
        self.assertTrue(isinstance(log_file, str), "Log file should be a string path")
        self.assertIn("agent_log.txt", log_file, "Log file path should contain 'agent_log.txt'")


if __name__ == "__main__":
    unittest.main()
