# LaTeX Report Customizer

## Project Overview
The **LaTeX Report Customizer** is a desktop application that allows users to generate custom LaTeX reports by selecting specific components they wish to include. Built with **PyQt**, this tool provides an intuitive graphical interface for tailoring LaTeX documents to user needs.

## Features
- **Interactive Component Selection**: Users can view and select specific sections and subsections from a LaTeX file.
- **Light/Dark Mode**: Toggle between light and dark themes for comfortable viewing in different environments.
- **PDF Generation**: Direct generation of PDF files from selected LaTeX components.
- **TEX Export**: Option to export modified TEX files for further editing.
- **Preview Support**: View how selected components will appear before generating final output.

## Dependencies
### Python Dependencies
- PyQt5
- PyLaTeX

### System Dependencies
#### LaTeX Distribution
- **Windows**: MiKTeX or TeX Live
- **macOS**: MacTeX
- **Linux**: TeX Live

#### PDF Viewer
- Any modern PDF reader (for viewing generated reports)

## Installation Instructions
### 1. Python Environment Setup
Ensure you have Python 3.6+ installed and set up a virtual environment if needed.

### 2. LaTeX Distribution Installation
#### Windows:
- Download and install **MiKTeX** or **TeX Live**.
- During installation, select **"Install missing packages automatically"**.

#### macOS:
- Download and install **MacTeX**.

#### Linux:
- Install **TeX Live** using the package manager (`sudo apt install texlive-full` or equivalent).

## Running the Application
### From Source Code
1. Clone the repository.
2. Install dependencies using `pip install -r requirements.txt`.
3. Run the application with `python main.py`.

### Using the Executable (After Packaging)
1. Download the pre-built executable.
2. Run the executable file to launch the application.

## Usage Instructions
1. Launch the application using one of the methods above.
2. Open a LaTeX file via **File → Open LaTeX File** (or press `Ctrl+O`).
3. Select components you want to include in the final report.
4. Generate PDF via **File → Generate PDF** (or press `Ctrl+G`).
5. The custom **PDF** with only selected components will be created.

## Troubleshooting Common Issues
### LaTeX Engine Not Found
- Ensure your LaTeX distribution is properly installed.
- Make sure LaTeX binaries are in your system **PATH**.
- Restart the application after installing LaTeX.

### Missing LaTeX Packages
- If using **MiKTeX**, enable **"Install missing packages on the fly"**.
- For **TeX Live/MacTeX**, run `tlmgr install <package-name>` for any missing packages.

### PDF Generation Fails
- Check the application logs for specific LaTeX errors.
- Ensure the input LaTeX file is valid and compiles independently.
- Verify you have write permissions in the output directory.

## Building Executable Packages
- The executable will be available in the **dist** directory after packaging.

## Technical Implementation
### Frontend (GUI)
- Built with **PyQt5** for a responsive and modern user interface.
- Component organization with checkboxes for easy selection.
- Menu-based navigation for essential functions.
- Theme customization capabilities.

### Backend Processing
- LaTeX parsing to identify document sections and components.
- Custom component assembly based on user selections.
- PDF generation through **LaTeX engine integration**.
- Temporary file handling for processing.

## Future Enhancements
- Component preview in the selection interface.
- Drag-and-drop reordering of sections.

This tool streamlines the process of generating custom reports by allowing users to include only relevant information from comprehensive LaTeX documents, saving time and improving document clarity.
