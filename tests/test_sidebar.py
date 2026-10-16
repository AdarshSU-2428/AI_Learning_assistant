import unittest
from unittest.mock import MagicMock, patch
from frontend.ui.sidebar import SidebarManager, DEFAULT_SUBJECTS, LAB_SUBJECTS


class MockSessionState(dict):
    """Mock session state supporting both dict indexing and attribute access."""
    def __getattr__(self, key):
        return self.get(key)

    def __setattr__(self, key, value):
        self[key] = value


class TestSidebar(unittest.TestCase):
    def test_default_subjects_integrity(self):
        self.assertIn("DAA", DEFAULT_SUBJECTS)
        self.assertIn("DBMS", DEFAULT_SUBJECTS)
        self.assertIn("Operating system", DEFAULT_SUBJECTS)
        self.assertEqual(len(DEFAULT_SUBJECTS), 12)
        self.assertNotIn("All Subjects", DEFAULT_SUBJECTS)

    def test_lab_subjects_integrity(self):
        self.assertIn("COA", LAB_SUBJECTS)
        self.assertIn("DAA", LAB_SUBJECTS)
        self.assertIn("DBMS", LAB_SUBJECTS)
        self.assertIn("DEC", LAB_SUBJECTS)
        self.assertIn("IWT", LAB_SUBJECTS)
        self.assertIn("OOP Java", LAB_SUBJECTS)
        self.assertIn("OS", LAB_SUBJECTS)
        self.assertIn("Python", LAB_SUBJECTS)
        self.assertEqual(len(LAB_SUBJECTS), 8)
        self.assertNotIn("All Lab Subjects", LAB_SUBJECTS)

    @patch("streamlit.sidebar")
    def test_render_home_sidebar(self, mock_sidebar):
        with patch("streamlit.session_state", MockSessionState()):
            with patch("streamlit.button", return_value=False), \
                 patch("streamlit.markdown"), \
                 patch("streamlit.caption"), \
                 patch("streamlit.divider"):
                SidebarManager.render_home_sidebar()

    @patch("streamlit.sidebar")
    def test_render_learning_sidebar(self, mock_sidebar):
        state = MockSessionState()
        with patch("streamlit.session_state", state):
            with patch("streamlit.button", return_value=False), \
                 patch("streamlit.selectbox", return_value="DAA"), \
                 patch("streamlit.markdown"), \
                 patch("streamlit.caption"), \
                 patch("streamlit.divider"):
                SidebarManager.render_learning_sidebar()
                self.assertEqual(state.selected_subject, "DAA")

    @patch("streamlit.sidebar")
    def test_render_lab_sidebar(self, mock_sidebar):
        state = MockSessionState()
        with patch("streamlit.session_state", state):
            with patch("streamlit.button", return_value=False), \
                 patch("streamlit.selectbox", return_value="OS"), \
                 patch("streamlit.markdown"), \
                 patch("streamlit.caption"), \
                 patch("streamlit.divider"):
                SidebarManager.render_lab_sidebar()
                self.assertEqual(state.selected_lab_subject, "OS")

    @patch("streamlit.sidebar")
    def test_render_exam_sidebar(self, mock_sidebar):
        state = MockSessionState()
        mock_api = MagicMock()
        with patch("streamlit.session_state", state):
            with patch("streamlit.button", return_value=False), \
                 patch("streamlit.selectbox", return_value="DAA"), \
                 patch("streamlit.slider", return_value=5), \
                 patch("streamlit.markdown"), \
                 patch("streamlit.caption"), \
                 patch("streamlit.divider"):
                SidebarManager.render_exam_sidebar(mock_api)


if __name__ == "__main__":
    unittest.main()
