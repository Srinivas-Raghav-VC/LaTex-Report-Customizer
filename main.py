import sys
from PyQt5.QtWidgets import QApplication
from gui import LatexReportCustomizerGUI
from utils import check_latex_installation

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Check if LaTeX is installed properly
    latex_installed, latex_path = check_latex_installation()
    
    # Launch the main application
    window = LatexReportCustomizerGUI(latex_installed, latex_path)
    window.show()
    sys.exit(app.exec_())
