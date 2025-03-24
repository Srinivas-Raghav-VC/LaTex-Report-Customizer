import os
import sys
import shutil
import subprocess
from PyQt5.QtWidgets import QMessageBox
import tempfile

def check_latex_installation():
    """Check if LaTeX (pdflatex) is installed and accessible"""
    # Try to find pdflatex in system PATH
    pdflatex_path = shutil.which('pdflatex')
    
    if (pdflatex_path):
        # Verify it's working by trying to get its version
        try:
            result = subprocess.run([pdflatex_path, '--version'], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE,
                                    timeout=3)
            if (result.returncode == 0):
                return True, pdflatex_path
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
    
    # Check common installation paths
    common_paths = []
    
    # Windows-specific paths
    if (sys.platform == 'win32'):
        program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
        program_files_x86 = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
        
        common_paths.extend([
            os.path.join(program_files, 'MiKTeX', 'miktex', 'bin', 'x64', 'pdflatex.exe'),
            os.path.join(program_files_x86, 'MiKTeX', 'miktex', 'bin', 'pdflatex.exe'),
            os.path.join(program_files, 'texlive', 'bin', 'win32', 'pdflatex.exe'),
        ])
    
    # macOS-specific paths
    elif (sys.platform == 'darwin'):
        common_paths.extend([
            '/Library/TeX/texbin/pdflatex',
            '/usr/texbin/pdflatex',
            '/usr/local/bin/pdflatex'
        ])
    
    # Linux-specific paths
    else:
        common_paths.extend([
            '/usr/bin/pdflatex',
            '/usr/local/bin/pdflatex'
        ])
    
    # Check each path
    for path in common_paths:
        if (os.path.isfile(path) and os.access(path, os.X_OK)):
            try:
                result = subprocess.run([path, '--version'], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE,
                                        timeout=3)
                if (result.returncode == 0):
                    return True, path
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
    
    return False, None

def show_latex_installation_dialog():
    """Show a dialog with instructions for installing LaTeX"""
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("LaTeX Installation Required")
    msg.setText("LaTeX (pdflatex) is required but not found on your system.")
    
    installation_instructions = """
    To install LaTeX:
    
    Windows:
    - Run this command in an administrative PowerShell:
      choco install miktex -y
    
    macOS:
    - Run this command in Terminal:
      brew install --cask mactex
    
    Linux:
    - Run this command in Terminal:
      sudo apt-get install texlive-full
    
    After installation, restart this application.
    """
    
    msg.setInformativeText(installation_instructions)
    msg.setStandardButtons(QMessageBox.Ok)
    return msg.exec_()

def create_temp_pdf():
    """Create a temporary file for PDF generation with improved reliability"""
    try:
        # Create a temporary directory without spaces
        temp_dir = tempfile.mkdtemp(prefix="latextemp_")
        
        # Use a simple filename without special characters
        temp_file = os.path.join(temp_dir, "preview.pdf")
        
        # Touch the file to ensure it can be created
        with open(temp_file, 'w') as f:
            pass
            
        return temp_file
    except Exception as e:
        print(f"Error creating temporary PDF file: {str(e)}")
        # Fallback to tempfile's method but with a simple name
        handle, path = tempfile.mkstemp(suffix='.pdf', prefix='preview_')
        os.close(handle)
        return path
