# LaTeX Report Customizer

## Project Overview
The **LaTeX Report Customizer** is a desktop application that allows users to generate custom LaTeX reports by selecting specific components they wish to include. Built with **PyQt**, this tool provides an intuitive graphical interface for tailoring LaTeX documents to user needs.

## Features
- **Interactive Component Selection**: Users can view and select specific sections and subsections from a LaTeX file.
- **Light/Dark Mode**: Toggle between light and dark themes for comfortable viewing in different environments.
- **PDF Generation**: Direct generation of PDF files from selected LaTeX components.
- **TEX Export**: Option to export modified TEX files for further editing.
- **Preview Support**: View how selected components will appear before generating final output.

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

## Requirements
- Python 3.6+
- PyQt5
- LaTeX distribution (**TeXLive, MiKTeX**, etc.)
- PyLaTeX for LaTeX file manipulation

## Usage Flow
1. Launch the application.
2. Open a LaTeX (.tex) file using the **File** menu or keyboard shortcut.
3. View extracted components in the main interface.
4. Select desired sections for inclusion.
5. Generate a custom **PDF** or export a modified **TEX** file.
6. View the resulting document with only selected components.

## Future Enhancements
- Drag-and-drop reordering of sections.
- LaTeX template library integration.
