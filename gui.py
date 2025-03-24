import os
import re
import tempfile
import subprocess
import shutil  # For file operations with TEX files
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QCheckBox, QPushButton, QFileDialog, 
                            QMessageBox, QGroupBox, QScrollArea, QProgressBar, 
                            QStatusBar, QApplication, QAction, QSizePolicy,
                            QToolButton, QFrame, QSlider, QSpacerItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtSvg import QSvgWidget  # Add SVG support

from latex_processor import LaTeXProcessingThread
from utils import show_latex_installation_dialog

class LatexReportCustomizerGUI(QMainWindow):
    def __init__(self, latex_installed=True, latex_path=None):
        super().__init__()
        self.input_file = None
        self.output_file = None
        self.components = []
        self.component_checkboxes = []
        self.pdflatex_path = latex_path
        self.temp_pdf_file = None
        self.latex_installed = latex_installed
        self.dark_mode = False
        
        # Check if LaTeX is installed
        if not self.latex_installed:
            show_latex_installation_dialog()
        
        # Set application-wide font size
        self.app_font = QApplication.font()
        self.app_font.setPointSize(10)
        QApplication.setFont(self.app_font)
        
        # Set application icon if image exists
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image.png")
        if not os.path.exists(logo_path):
            # Try PNG as fallback
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image.png")
            
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
            
        self.init_ui()
        
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("LaTeX Report Customizer")
        self.setGeometry(100, 100, 850, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout as a horizontal layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(15)
        
        # Left side containing file selection, component selection
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        
        # Right side containing status and generate button
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)
        right_panel.setContentsMargins(0, 0, 0, 0)
        
        # Add logo at the top of left panel
        logo_layout = QHBoxLayout()
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image.png")
            
        if os.path.exists(logo_path):
            # Check if it's SVG or PNG and use appropriate widget
            if (logo_path.lower().endswith('.svg')):
                logo_widget = QSvgWidget(logo_path)
                logo_widget.setFixedSize(250, 100)
            else:
                logo_label = QLabel()
                pixmap = QPixmap(logo_path)
                # Resize the logo to a reasonable size if needed
                if pixmap.width() > 300:
                    pixmap = pixmap.scaledToWidth(250, Qt.SmoothTransformation)
                logo_label.setPixmap(pixmap)
                logo_label.setAlignment(Qt.AlignCenter)
                logo_widget = logo_label
                
            logo_layout.addStretch()
            logo_layout.addWidget(logo_widget)
            logo_layout.addStretch()
            left_panel.addLayout(logo_layout)
            left_panel.addSpacing(10)
        
        # File selection group
        file_group = QGroupBox("LaTeX Source File")
        file_layout = QHBoxLayout()
        file_layout.setContentsMargins(10, 15, 10, 10)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setWordWrap(True)
        
        self.file_button = QPushButton("Browse...")
        self.file_button.setFixedWidth(150)
        self.file_button.clicked.connect(self.select_file)
        
        file_layout.addWidget(self.file_label, 1)
        file_layout.addWidget(self.file_button)
        file_group.setLayout(file_layout)
        left_panel.addWidget(file_group)
        
        # Component selection group with better layout
        components_group = QGroupBox("Select Components to Include")
        components_layout = QVBoxLayout()
        components_layout.setContentsMargins(10, 15, 10, 10)
        components_layout.setSpacing(5)
        
        # Create a scroll area for components
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        scroll_widget = QWidget()
        self.components_layout = QVBoxLayout(scroll_widget)
        self.components_layout.setAlignment(Qt.AlignTop)
        self.components_layout.setSpacing(6)
        self.components_layout.setContentsMargins(5, 5, 5, 5)
        scroll_area.setWidget(scroll_widget)
        
        # Add placeholder message
        self.placeholder_label = QLabel("Load a LaTeX file to see available components")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setStyleSheet("color: #888888; font-style: italic; padding: 20px;")
        self.components_layout.addWidget(self.placeholder_label)
        
        components_layout.addWidget(scroll_area)
        components_group.setLayout(components_layout)
        left_panel.addWidget(components_group, 1)  # Give components stretch priority
        
        # Component selection buttons in a nicer layout
        selection_layout = QHBoxLayout()
        selection_layout.setSpacing(10)
        
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all_components)
        
        self.deselect_all_button = QPushButton("Deselect All")
        self.deselect_all_button.setProperty("secondary", True)
        self.deselect_all_button.clicked.connect(self.deselect_all_components)
        
        selection_layout.addStretch()
        selection_layout.addWidget(self.select_all_button)
        selection_layout.addWidget(self.deselect_all_button)
        selection_layout.addStretch()
        left_panel.addLayout(selection_layout)
        
        # =================== RIGHT PANEL ===================
        
        # Add spacer to push content down a bit to align with left panel
        right_panel.addSpacing(30)
        
        # Status group with LaTeX status
        status_group = QGroupBox("LaTeX Status")
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(10, 15, 10, 10)
        
        status_text = "LaTeX is installed and ready" if self.latex_installed else "LaTeX is not installed"
        status_color = "#27ae60" if self.latex_installed else "#e74c3c"
        
        self.latex_status_label = QLabel(status_text)
        self.latex_status_label.setStyleSheet(f"color: {status_color}; font-weight: bold; padding: 10px;")
        self.latex_status_label.setAlignment(Qt.AlignCenter)
        
        status_layout.addWidget(self.latex_status_label)
        status_group.setLayout(status_layout)
        right_panel.addWidget(status_group)
        
        # Generate PDF/TEX group
        generate_group = QGroupBox("Generate Output")
        generate_layout = QVBoxLayout()
        generate_layout.setContentsMargins(10, 15, 10, 15)
        
        # Generate PDF button - now more compact but with bigger text
        self.generate_button = QPushButton("GENERATE PDF")
        self.generate_button.setProperty("primary", True)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 15px;
                font-weight: bold;
                font-size: 16px;
                min-height: 50px;
                border-radius: 5px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #219955;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.generate_button.clicked.connect(self.generate_pdf)
        
        # Generate TEX button
        self.generate_tex_button = QPushButton("Export TEX File")
        self.generate_tex_button.setProperty("secondary", True) 
        self.generate_tex_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
                min-height: 40px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6da3;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.generate_tex_button.clicked.connect(self.generate_tex)
        
        # Progress bar with better styling
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(20)
        self.progress_bar.setTextVisible(True)
        
        generate_layout.addWidget(self.generate_button)
        generate_layout.addSpacing(10)
        generate_layout.addWidget(self.generate_tex_button)
        generate_layout.addSpacing(10)
        generate_layout.addWidget(self.progress_bar)
        generate_group.setLayout(generate_layout)
        right_panel.addWidget(generate_group)
        
        # Add stretching space to push everything up
        right_panel.addStretch(1)
        
        # Dark mode toggle moved to bottom right corner
        theme_layout = QHBoxLayout()
        
        # Create labels for light/dark
        dark_mode_label = QLabel("Dark Mode:")
        dark_mode_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Create small toggle switch with simpler design
        self.theme_toggle = QSlider(Qt.Horizontal)
        self.theme_toggle.setFixedWidth(40)
        self.theme_toggle.setFixedHeight(20)
        self.theme_toggle.setRange(0, 1)
        self.theme_toggle.setValue(0)  # Start with light mode (0)
        self.theme_toggle.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 10px;
                background: #f0f0f0;
                margin: 2px 0;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #4a86e8;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)
        self.theme_toggle.valueChanged.connect(self.toggle_theme_from_slider)
        
        theme_layout.addWidget(dark_mode_label)
        theme_layout.addWidget(self.theme_toggle)
        right_panel.addLayout(theme_layout)
        
        # Add panels to main layout
        main_layout.addLayout(left_panel, 7)  # Left panel gets 70% of space
        
        # Add a vertical separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #cccccc;")
        main_layout.addWidget(separator)
        
        main_layout.addLayout(right_panel, 3)  # Right panel gets 30% of space
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Disable buttons initially
        self.update_button_states()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Apply theme after all UI elements have been created
        self.apply_theme()
    
    def toggle_theme_from_slider(self, value):
        """Toggle theme based on slider value"""
        try:
            self.dark_mode = (value == 1)
            self.apply_theme()
        except Exception as e:
            print(f"Error toggling theme from slider: {str(e)}")
        
    def toggle_theme(self):
        """Toggle between light and dark mode (used by menu actions)"""
        try:
            self.dark_mode = not self.dark_mode
            # Temporarily disconnect to prevent recursive signals
            self.theme_toggle.valueChanged.disconnect(self.toggle_theme_from_slider)
            # Update slider to match the theme
            self.theme_toggle.setValue(1 if self.dark_mode else 0)
            # Reconnect the signal
            self.theme_toggle.valueChanged.connect(self.toggle_theme_from_slider)
            self.apply_theme()
        except Exception as e:
            print(f"Error toggling theme: {str(e)}")
        
    def apply_theme(self):
        """Apply the current theme (light or dark mode)"""
        try:
            QApplication.processEvents()  # Process any pending events first
            
            if self.dark_mode:
                # Dark mode styles
                self.setStyleSheet("""
                    QMainWindow, QWidget {
                        background-color: #2d2d2d;
                        color: #e0e0e0;
                    }
                    QGroupBox {
                        font-weight: bold;
                        font-size: 11pt;
                        border: 1px solid #444444;
                        border-radius: 6px;
                        margin-top: 1.5ex;
                        background-color: #333333;
                        padding: 8px;
                        color: #ffffff; /* Set text color for group box title */
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        subcontrol-position: top left;
                        padding: 0 5px;
                        color: #ffffff; /* Make title white in dark mode */
                    }
                    QPushButton {
                        background-color: #0c61c9;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-weight: bold;
                        min-height: 28px;
                        padding: 4px 16px;
                    }
                    QPushButton:hover {
                        background-color: #1471d9;
                    }
                    QPushButton:pressed {
                        background-color: #0a51a9;
                    }
                    QPushButton:disabled {
                        background-color: #555555;
                        color: #888888;
                    }
                    QPushButton[secondary="true"] {
                        background-color: #666666;
                    }
                    QPushButton[secondary="true"]:hover {
                        background-color: #777777;
                    }
                    QPushButton[secondary="true"]:pressed {
                        background-color: #555555;
                    }
                    QPushButton[primary="true"] {
                        background-color: #278c54;
                        color: white;
                        padding: 8px;
                        font-weight: bold;
                        font-size: 16px;
                        letter-spacing: 1px;
                    }
                    QPushButton[primary="true"]:hover {
                        background-color: #22774a;
                    }
                    QPushButton[primary="true"]:pressed {
                        background-color: #1d6940;
                    }
                    QPushButton[primary="true"]:disabled {
                        background-color: #555555;
                    }
                    QCheckBox {
                        spacing: 8px;
                        font-size: 10.5pt;
                        padding: 2px 0;
                        color: #cccccc;
                    }
                    QCheckBox::indicator {
                        width: 16px;
                        height: 16px;
                    }
                    QScrollArea, QScrollBar {
                        border: none;
                        background-color: #333333;
                    }
                    QScrollBar:vertical {
                        border: none;
                        background: #444444;
                        width: 10px;
                        margin: 0;
                    }
                    QScrollBar::handle:vertical {
                        background: #666666;
                        min-height: 20px;
                        border-radius: 5px;
                    }
                    QProgressBar {
                        border: 1px solid #555555;
                        border-radius: 4px;
                        text-align: center;
                        background-color: #444444;
                    }
                    QProgressBar::chunk {
                        background-color: #0c61c9;
                        border-radius: 3px;
                    }
                    QStatusBar {
                        background-color: #333333;
                        color: #bbbbbb;
                    }
                    QLabel {
                        color: #e0e0e0;
                    }
                    QMenuBar {
                        background-color: #333333;
                        color: #e0e0e0;
                    }
                    QMenuBar::item {
                        background-color: #333333;
                        color: #e0e0e0;
                    }
                    QMenuBar::item:selected {
                        background-color: #444444;
                    }
                    QMenu {
                        background-color: #333333;
                        color: #e0e0e0;
                        border: 1px solid #444444;
                    }
                    QMenu::item:selected {
                        background-color: #444444;
                    }
                    QSlider::groove:horizontal {
                        border: 1px solid #444444;
                        height: 10px;
                        background: #333333;
                        margin: 2px 0;
                        border-radius: 5px;
                    }
                    QSlider::handle:horizontal {
                        background: #f39c12;
                        border: 1px solid #555555;
                        width: 18px;
                        margin: -5px 0;
                        border-radius: 9px;
                    }
                    QFrame[frameShape="4"] { /* VLine */
                        color: #555555;
                    }
                    QFileDialog {
                        background-color: #333333;
                        color: #e0e0e0;
                    }
                """)
                
                # Update specific elements that need targeted styling
                self.file_label.setStyleSheet("color: #e0e0e0;")
                self.placeholder_label.setStyleSheet("color: #999999; font-style: italic; padding: 20px;")
                
            else:
                # Light mode styles
                self.setStyleSheet("""
                    QMainWindow, QWidget {
                        background-color: #ffffff;
                        color: #333333;
                    }
                    QGroupBox {
                        font-weight: bold;
                        font-size: 11pt;
                        border: 1px solid #e1e1e1;
                        border-radius: 6px;
                        margin-top: 1.5ex;
                        background-color: #fafafa;
                        padding: 8px;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        subcontrol-position: top left;
                        padding: 0 5px;
                        color: #444444;
                    }
                    QPushButton {
                        background-color: #4a86e8;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-weight: bold;
                        min-height: 28px;
                        padding: 4px 16px;
                    }
                    QPushButton:hover {
                        background-color: #3a76d8;
                    }
                    QPushButton:pressed {
                        background-color: #2a66c8;
                    }
                    QPushButton:disabled {
                        background-color: #cccccc;
                        color: #888888;
                    }
                    QPushButton[secondary="true"] {
                        background-color: #3498db;
                    }
                    QPushButton[secondary="true"]:hover {
                        background-color: #2980b9;
                    }
                    QPushButton[secondary="true"]:pressed {
                        background-color: #1c6da3;
                    }
                    QPushButton[primary="true"] {
                        background-color: #27ae60;
                        color: white;
                        padding: 8px;
                        font-weight: bold;
                        font-size: 16px;
                        letter-spacing: 1px;
                    }
                    QPushButton[primary="true"]:hover {
                        background-color: #219955;
                    }
                    QPushButton[primary="true"]:pressed {
                        background-color: #1e8449;
                    }
                    QPushButton[primary="true"]:disabled {
                        background-color: #cccccc;
                    }
                    QCheckBox {
                        spacing: 8px;
                        font-size: 10.5pt;
                        padding: 2px 0;
                    }
                    QCheckBox::indicator {
                        width: 16px;
                        height: 16px;
                    }
                    QScrollArea {
                        border: none;
                        background-color: transparent;
                    }
                    QProgressBar {
                        border: 1px solid #e1e1e1;
                        border-radius: 4px;
                        text-align: center;
                        background-color: #f5f5f5;
                    }
                    QProgressBar::chunk {
                        background-color: #4a86e8;
                        border-radius: 3px;
                    }
                    QStatusBar {
                        background-color: #f5f5f5;
                        color: #444444;
                    }
                    QSlider::groove:horizontal {
                        border: 1px solid #cccccc;
                        height: 10px;
                        background: #f0f0f0;
                        margin: 2px 0;
                        border-radius: 5px;
                    }
                    QSlider::handle:horizontal {
                        background: #4a86e8;
                        border: 1px solid #5c5c5c;
                        width: 18px;
                        margin: -5px 0;
                        border-radius: 9px;
                    }
                    QFrame[frameShape="4"] { /* VLine */
                        color: #e1e1e1;
                    }
                """)
                
                # Update placeholder style
                self.placeholder_label.setStyleSheet("color: #888888; font-style: italic; padding: 20px;")
            
            # Use a single processEvents call after applying styles
            QApplication.processEvents()
        except Exception as e:
            print(f"Error applying theme: {str(e)}")

    def create_menu_bar(self):
        """Create application menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        open_action = QAction("&Open LaTeX File", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.select_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        generate_pdf_action = QAction("Generate &PDF", self)
        generate_pdf_action.setShortcut("Ctrl+G")
        generate_pdf_action.triggered.connect(self.generate_pdf)
        file_menu.addAction(generate_pdf_action)
        
        generate_tex_action = QAction("Export &TEX File", self)
        generate_tex_action.setShortcut("Ctrl+T")
        generate_tex_action.triggered.connect(self.generate_tex)
        file_menu.addAction(generate_tex_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menu_bar.addMenu("&View")
        
        theme_action = QAction("Toggle &Dark Mode", self)
        theme_action.setShortcut("Ctrl+D")
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def show_about_dialog(self):
        """Show about dialog"""
        QMessageBox.about(self, "About LaTeX Report Customizer",
            """<h2 style="color: #4a86e8;">LaTeX Report Customizer</h2>
            <p>Version 1.0</p>
            <p>A tool for customizing LaTeX reports by selecting specific components.</p>
            <p>Create custom PDFs by selecting only the sections you need.</p>""")

    def update_button_states(self):
        """Update button states based on current application state"""
        has_file = self.input_file is not None
        has_components = len(self.component_checkboxes) > 0
        has_selected = has_components and any(cb.isChecked() for cb in self.component_checkboxes)
        
        self.select_all_button.setEnabled(has_components)
        self.deselect_all_button.setEnabled(has_components and has_selected)
        self.generate_button.setEnabled(has_file and has_selected and self.latex_installed)
        self.generate_tex_button.setEnabled(has_file and has_selected)
    
    def select_file(self):
        """Open file dialog to select a LaTeX file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select LaTeX File", "", "LaTeX Files (*.tex)")
        
        if file_path:
            self.input_file = file_path
            self.file_label.setText(os.path.basename(file_path))
            
            # Clean up any existing temp files
            self.cleanup_temp_files()
            
            # Show loading in status bar and progress
            self.statusBar.showMessage("Reading LaTeX file...")
            self.progress_bar.setValue(10)
            QApplication.processEvents()
            
            # Parse components
            self.parse_components()
            
            # Update status
            self.statusBar.showMessage(f"Loaded: {os.path.basename(file_path)}")
            self.progress_bar.setValue(0)

    def cleanup_temp_files(self):
        """Clean up temporary files"""
        if hasattr(self, 'temp_pdf_file') and self.temp_pdf_file and os.path.exists(self.temp_pdf_file):
            try:
                os.remove(self.temp_pdf_file)
            except Exception as e:
                print(f"Failed to remove temp file: {str(e)}")
            
    def parse_components(self):
        """Parse sections and subsections from the LaTeX file"""
        try:
            # Clear existing components
            for i in reversed(range(self.components_layout.count())):
                widget = self.components_layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()
            
            self.components = []
            self.component_checkboxes = []
            
            # Read the LaTeX file
            with open(self.input_file, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Extract document content
            doc_start = content.find('\\begin{document}')
            doc_end = content.find('\\end{document}')
            
            if doc_start == -1 or doc_end == -1:
                raise ValueError("Could not find document begin/end tags")
                
            doc_content = content[doc_start + len('\\begin{document}'):doc_end]
            
            # Show progress
            self.progress_bar.setValue(40)
            QApplication.processEvents()
            
            # Find section commands
            pattern = r'\\(chapter|section|subsection|subsubsection){([^}]*)}'
            matches = list(re.finditer(pattern, doc_content))
            
            # Keep track of current section
            current_section = None
            section_count = 0
            
            if matches:
                for match in matches:
                    section_type = match.group(1)
                    section_title = match.group(2).strip()
                    
                    # Determine indentation level
                    indent_level = 0
                    if section_type == 'subsection':
                        indent_level = 1
                    elif section_type == 'subsubsection':
                        indent_level = 2
                    
                    # Add component checkbox
                    if section_type == 'section' or section_type == 'chapter':
                        current_section = section_title
                        self.add_component(section_title, indent=False)
                    else:
                        # For subsections, store the parent section relationship
                        if current_section:
                            title = f"{current_section} - {section_title}"
                            self.add_component(title, indent=True, indent_level=indent_level)
                        else:
                            self.add_component(section_title, indent=True, indent_level=indent_level)
                    
                    section_count += 1
            
            self.progress_bar.setValue(80)
            QApplication.processEvents()
            
            if section_count == 0:
                label = QLabel("No sections found in the document")
                label.setStyleSheet("color: #e74c3c; font-style: italic; padding: 20px;")
                label.setAlignment(Qt.AlignCenter)
                self.components_layout.addWidget(label)
            
            self.statusBar.showMessage(f"Found {section_count} components in the file")
            self.update_button_states()
            
            # Show progress complete
            self.progress_bar.setValue(100)
            QApplication.processEvents()
            self.progress_bar.setValue(0)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error parsing LaTeX file: {str(e)}")
            self.statusBar.showMessage("Error parsing LaTeX file")
            self.progress_bar.setValue(0)
    
    def add_component(self, title, indent=False, indent_level=0):
        """Add a component checkbox to the UI with improved styling"""
        checkbox = QCheckBox(title)
        checkbox.setChecked(True)
        
        if indent:
            # Create container for indented subsections
            container = QWidget()
            checkbox_layout = QHBoxLayout(container)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setSpacing(0)
            
            # Add indentation based on level
            checkbox_layout.addSpacing(20 * indent_level)
            checkbox_layout.addWidget(checkbox)
            
            # Don't set color here - will be handled by theme
            # Store subsection type in a property
            checkbox.setProperty("component-type", "subsection")
            
            self.components_layout.addWidget(container)
        else:
            # Add section with bold font but no color (handled by theme)
            font = checkbox.font()
            font.setBold(True)
            checkbox.setFont(font)
            # Store section type in a property
            checkbox.setProperty("component-type", "section")
            self.components_layout.addWidget(checkbox)
        
        # Connect checkbox to parent section handling
        checkbox.toggled.connect(self.on_component_toggled)
        self.component_checkboxes.append(checkbox)
    
    def on_component_toggled(self):
        """Handle component checkbox state changes"""
        sender = self.sender()
        if sender:
            # If it's a section checkbox, handle subsections
            if " - " not in sender.text():
                for checkbox in self.component_checkboxes:
                    # If this is a subsection of the toggled section
                    if checkbox.text().startswith(sender.text() + " - "):
                        checkbox.setEnabled(sender.isChecked())
                        if not sender.isChecked():
                            checkbox.setChecked(False)
        
        self.update_button_states()
    
    def select_all_components(self):
        """Select all components"""
        for checkbox in self.component_checkboxes:
            checkbox.setChecked(True)
            checkbox.setEnabled(True)  # Ensure all are enabled
        
        self.statusBar.showMessage("All components selected")
        self.update_button_states()
    
    def deselect_all_components(self):
        """Deselect all components"""
        for checkbox in self.component_checkboxes:
            checkbox.setChecked(False)
        
        self.statusBar.showMessage("All components deselected")
        self.update_button_states()
    
    def generate_pdf(self):
        """Generate the final PDF file"""
        if not self.input_file or not self.latex_installed:
            QMessageBox.warning(self, "Warning", 
                                "Please select a LaTeX file and ensure LaTeX is installed")
            return
            
        # Get selected components
        selected_components = [cb.text() for cb in self.component_checkboxes if cb.isChecked()]
        
        if not selected_components:
            QMessageBox.warning(self, "Warning", "Please select at least one component")
            return
        
        # Get output file path
        output_file, _ = QFileDialog.getSaveFileName(
            self, "Save PDF As", "", "PDF Files (*.pdf)")
        
        if not output_file:
            return
        
        # Add .pdf extension if not present
        if not output_file.lower().endswith('.pdf'):
            output_file += '.pdf'
            
        self.output_file = output_file
        
        # Disable UI elements during processing
        self.setEnabled(False)
        self.progress_bar.setValue(0)
        self.statusBar.showMessage("Generating PDF...")
        
        # Start processing thread
        self.process_thread = LaTeXProcessingThread(
            self.input_file, self.output_file, selected_components, self.pdflatex_path
        )
        self.process_thread.progress_update.connect(self.progress_bar.setValue)
        self.process_thread.finished_signal.connect(self.process_completed)
        self.process_thread.start()
    
    def process_completed(self, success, message):
        """Handle PDF generation completion"""
        self.setEnabled(True)
        
        if success:
            self.progress_bar.setValue(100)
            self.statusBar.showMessage("PDF generated successfully")
            
            response = QMessageBox.question(self, "Success", 
                                  "PDF generated successfully.\nWould you like to open it now?",
                                  QMessageBox.Yes | QMessageBox.No)
            
            # Open PDF if user clicks Yes
            if response == QMessageBox.Yes:
                try:
                    if os.path.exists(self.output_file):
                        os.startfile(self.output_file)
                except Exception:
                    pass
            
            self.progress_bar.setValue(0)
            return
        
        # Handle error
        self.progress_bar.setValue(0)
        self.statusBar.showMessage("Error generating PDF")
        QMessageBox.critical(self, "Error", f"Error generating PDF: {message}")
    
    def generate_tex(self):
        """Generate a customized TEX file based on selected components"""
        if not self.input_file:
            QMessageBox.warning(self, "Warning", "Please select a LaTeX file first")
            return
            
        # Get selected components
        selected_components = [cb.text() for cb in self.component_checkboxes if cb.isChecked()]
        
        if not selected_components:
            QMessageBox.warning(self, "Warning", "Please select at least one component")
            return
            
        # Get output file path
        output_file, _ = QFileDialog.getSaveFileName(
            self, "Save TEX File As", "", "LaTeX Files (*.tex)")
        
        if not output_file:
            return
        
        # Add .tex extension if not present
        if not output_file.lower().endswith('.tex'):
            output_file += '.tex'
            
        try:
            # Show processing
            self.setEnabled(False)
            self.progress_bar.setValue(10)
            self.statusBar.showMessage("Creating customized TEX file...")
            
            # Read the original LaTeX file
            with open(self.input_file, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Extract document preamble and ending
            doc_start = content.find('\\begin{document}')
            doc_end = content.find('\\end{document}')
            
            if doc_start == -1 or doc_end == -1:
                raise ValueError("Could not find document begin/end tags")
                
            preamble = content[:doc_start + len('\\begin{document}')]
            ending = content[doc_end:]
            doc_content = content[doc_start + len('\\begin{document}'):doc_end]
            
            self.progress_bar.setValue(30)
            
            # Filter the document content based on selected components
            result = []
            patterns = []
            
            # Create regex patterns for each selected component
            for component in selected_components:
                # If it's a subsection, get the parent section and subsection names
                if " - " in component:
                    section, subsection = component.split(" - ", 1)
                    # For subsections, keep the line containing the subsection
                    pattern = r'\\(subsection|subsubsection){' + re.escape(subsection) + r'}'
                    patterns.append((section, pattern))
                else:
                    # For main sections, keep the entire section including subsections
                    pattern = r'\\(section|chapter){' + re.escape(component) + r'}'
                    patterns.append((None, pattern))
            
            # Process document by lines
            lines = doc_content.split('\n')
            include_line = False
            current_section = None
            modified_content = []
            
            for line in lines:
                # Check for section headers
                for section_type in ['chapter', 'section', 'subsection', 'subsubsection']:
                    if f'\\{section_type}{{' in line:
                        section_match = re.search(r'\\' + section_type + r'{([^}]*)}', line)
                        if section_match:
                            section_title = section_match.group(1).strip()
                            
                            if section_type in ['chapter', 'section']:
                                current_section = section_title
                                # Check if this section is selected
                                include_line = any(parent is None and re.search(pattern, line) 
                                                  for parent, pattern in patterns)
                            else:  # subsection or subsubsection
                                if current_section:
                                    # Check if this subsection is selected
                                    include_line = any((parent == current_section and re.search(pattern, line))
                                                      for parent, pattern in patterns)
                                else:
                                    # No parent section, check by subsection name only
                                    include_line = any(parent is None and re.search(pattern, line)
                                                      for parent, pattern in patterns)
                
                if include_line:
                    modified_content.append(line)
            
            self.progress_bar.setValue(70)
            
            # Combine preamble, modified content, and ending
            final_content = preamble + '\n' + '\n'.join(modified_content) + '\n' + ending
            
            # Write the new TEX file
            with open(output_file, 'w', encoding='utf-8') as output:
                output.write(final_content)
                
            self.progress_bar.setValue(100)
            self.statusBar.showMessage(f"TEX file saved: {os.path.basename(output_file)}")
            
            QMessageBox.information(self, "Success", 
                                   f"Customized TEX file generated successfully:\n{output_file}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating TEX file: {str(e)}")
            self.statusBar.showMessage("Error creating TEX file")
        finally:
            self.setEnabled(True)
            self.progress_bar.setValue(0)
    
    def closeEvent(self, event):
        """Clean up temporary files when closing the application"""
        self.cleanup_temp_files()
        event.accept()