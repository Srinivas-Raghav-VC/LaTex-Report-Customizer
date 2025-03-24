import os
import re
import subprocess
import shutil
from PyQt5.QtCore import QThread, pyqtSignal
import pdflatex

class LaTeXProcessingThread(QThread):
    progress_update = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, input_file, output_file, selected_components, pdflatex_path=None):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.selected_components = selected_components
        self.pdflatex_path = pdflatex_path if pdflatex_path else 'pdflatex'
        
    def run(self):
        try:
            # Read the LaTeX file
            with open(self.input_file, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Progress update
            self.progress_update.emit(10)
            
            # Create a new LaTeX file with only selected components
            modified_content = self.process_latex_content(content)
            
            # Progress update
            self.progress_update.emit(30)
            
            # Write the modified content to a temporary file
            temp_file = self.output_file.replace('.pdf', '_temp.tex')
            with open(temp_file, 'w', encoding='utf-8') as file:
                file.write(modified_content)
                
            # Progress update
            self.progress_update.emit(50)
            
            # Compile the LaTeX file to PDF
            self.compile_latex(temp_file)
            
            # Progress update
            self.progress_update.emit(100)
            
            # Signal completion
            self.finished_signal.emit(True, "PDF generated successfully!")
            
        except Exception as e:
            self.finished_signal.emit(False, f"Error: {str(e)}")
    
    import re

    def process_latex_content(self, content):
        # Identify document begin and end
        doc_start = content.find('\\begin{document}')
        doc_end = content.find('\\end{document}')
        
        if doc_start == -1 or doc_end == -1:
            raise ValueError("Could not find document begin/end tags")
        
        # Get the preamble (everything before \begin{document})
        preamble = content[:doc_start + len('\\begin{document}')]
        
        # Get the document content (everything between \begin{document} and \end{document})
        doc_content = content[doc_start + len('\\begin{document}'):doc_end]
        
        # Debug selected components
        print(f"DEBUG: Selected components: {self.selected_components}")
        
        processed_content = ""
        
        # Split into fragments based on section or subsection headers
        sections = re.split(r'(\\section{[^}]*}|\\subsection{[^}]*})', doc_content)
        
        # Always include the first fragment (which may include your header, page style, or other settings)
        if sections:
            processed_content += sections[0]
            print(f"DEBUG: Including pre-section content")
        
        current_section = None
        section_selected = False
        include_content = False
        
        # First pass: identify which sections are selected
        selected_sections = set()
        for comp in self.selected_components:
            if " - " not in comp:  # It's a main section
                selected_sections.add(comp)
        
        # Process remaining fragments in pairs (header, content)
        for i in range(1, len(sections)):
            fragment = sections[i]
            # Check if this fragment is a section/subsection header
            if fragment.startswith('\\section{') or fragment.startswith('\\subsection{'):
                # Extract the title using regex
                title_match = re.search(r'\\(?:sub)?section{([^}]*)}', fragment)
                if not title_match:
                    continue  # Skip if header format is unexpected
                    
                title = title_match.group(1).strip()
                
                if fragment.startswith('\\section{'):
                    current_section = title
                    section_selected = (current_section in selected_sections)
                    include_content = section_selected
                    print(f"DEBUG: Section '{title}' found, selected={section_selected}, include={include_content}")
                
                elif fragment.startswith('\\subsection{'):
                    # If parent section is not selected, automatically skip this subsection
                    if not section_selected or current_section is None:
                        include_content = False
                        print(f"DEBUG: Subsection '{title}' skipped because parent section not selected")
                    else:
                        # Only include if parent section is selected AND either:
                        # 1. No specific subsections were selected for this parent (meaning include all)
                        # 2. This specific subsection was selected
                        subsection_key = f"{current_section} - {title}"
                        
                        # Check if any subsections of this section were specifically selected
                        has_selected_subsections = any(comp.startswith(f"{current_section} - ") for comp in self.selected_components)
                        
                        if has_selected_subsections:
                            # Only include specifically selected subsections
                            include_content = (subsection_key in self.selected_components)
                        else:
                            # Include all subsections for this selected section
                            include_content = True
                        
                        print(f"DEBUG: Subsection '{subsection_key}', has_selected_subs={has_selected_subsections}, include={include_content}")
                
                # Append the header if content is to be included
                if include_content:
                    processed_content += fragment
                    print(f"DEBUG: Including header: {fragment}")
            else:
                # For content fragments, include them if the flag is True
                if include_content:
                    processed_content += fragment
                    print(f"DEBUG: Including content fragment ({len(fragment)} chars)")
        
        # Reconstruct the full document by adding the ending tag
        final_content = preamble + processed_content + '\\end{document}'
        return final_content

    
    def compile_latex(self, tex_file):
        try:
            # Get the directory and filename
            tex_dir = os.path.dirname(tex_file)
            tex_filename = os.path.basename(tex_file)
            
            # Fix: Remove _temp from output filename if present
            base_output_file = self.output_file.replace('_temp.pdf', '.pdf')
            output_pdf = os.path.splitext(base_output_file)[0] + '.pdf'
            
            # Create a safer temporary directory without spaces or special characters
            import tempfile
            temp_working_dir = tempfile.mkdtemp(prefix="latex_")
            safe_tex_file = os.path.join(temp_working_dir, "document.tex")
            
            # Copy the tex file to the safe location
            with open(tex_file, 'r', encoding='utf-8') as src:
                content = src.read()
            with open(safe_tex_file, 'w', encoding='utf-8') as dst:
                dst.write(content)
            
            print(f"Working in temporary directory: {temp_working_dir}")
            
            # Method 2: Use subprocess directly (more reliable)
            try:
                # Run pdflatex in the safe directory
                print("Running pdflatex...")
                result = subprocess.run(
                    [self.pdflatex_path, '-interaction=nonstopmode', 'document.tex'],
                    cwd=temp_working_dir,
                    check=True, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE
                )
                print("First pdflatex run completed")
                
                # Run again for references
                subprocess.run(
                    [self.pdflatex_path, '-interaction=nonstopmode', 'document.tex'],
                    cwd=temp_working_dir,
                    check=True, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE
                )
                print("Second pdflatex run completed")
                
                # Check if PDF was created in temp directory
                temp_pdf = os.path.join(temp_working_dir, "document.pdf")
                print(f"Looking for PDF at: {temp_pdf}")
                
                if os.path.exists(temp_pdf) and os.path.getsize(temp_pdf) > 0:
                    print(f"PDF found ({os.path.getsize(temp_pdf)} bytes), copying to: {output_pdf}")
                    # Copy to the desired output location
                    if os.path.exists(output_pdf):
                        os.remove(output_pdf)
                    shutil.copy2(temp_pdf, output_pdf)
                    print("PDF successfully copied")
                    return
                else:
                    print(f"PDF not found in temp directory: {os.listdir(temp_working_dir)}")
                    raise RuntimeError(f"PDF not created in temp directory")
                    
            except Exception as e:
                print(f"LaTeX compilation error: {str(e)}")
                raise RuntimeError(f"LaTeX compilation failed: {str(e)}")
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"LaTeX compilation failed: {str(e)}")
        finally:
            # Clean up temp directory
            try:
                if 'temp_working_dir' in locals() and os.path.exists(temp_working_dir):
                    shutil.rmtree(temp_working_dir, ignore_errors=True)
                    print(f"Cleaned up temporary directory")
            except:
                pass
    
    def process_latex_file(self, input_file, output_file, selected_components):
        try:
            # Read the original LaTeX file
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove draft option from documentclass to enable colors and images
            content = content.replace('\\documentclass[draft]{article}', '\\documentclass{article}')
            
            # Extract preamble (everything before \begin{document})
            doc_start = content.find('\\begin{document}')
            if doc_start == -1:
                return False, "Could not find \\begin{document} tag"
            
            preamble = content[:doc_start]
            
            # Extract document content
            doc_end = content.find('\\end{document}')
            if doc_end == -1:
                return False, "Could not find \\end{document} tag"
            
            document_body = content[doc_start:doc_end]
            
            # Find content before any sections (this contains important style elements)
            first_section_pos = float('inf')
            section_types = ['\\chapter{', '\\section{', '\\subsection{']
            for section_type in section_types:
                pos = document_body.find(section_type)
                if pos != -1 and pos < first_section_pos:
                    first_section_pos = pos
            
            if first_section_pos == float('inf'):
                # No sections found, keep all content
                filtered_content = document_body
            else:
                # Extract pre-section content (crucial for formatting)
                pre_section_content = document_body[:first_section_pos]
                
                # Extract all sections and filter based on selected components
                sections = []
                remaining_content = document_body[first_section_pos:]
                
                # Identify all sections in the document
                current_pos = 0
                while current_pos < len(remaining_content):
                    # Find the next section start
                    next_section_pos = float('inf')
                    next_section_type = None
                    
                    for section_type in section_types:
                        pos = remaining_content.find(section_type, current_pos)
                        if pos != -1 and pos < next_section_pos:
                            next_section_pos = pos
                            next_section_type = section_type
                    
                    if next_section_pos == float('inf'):
                        # No more sections
                        break
                    
                    # Find the section title
                    title_start = next_section_pos + len(next_section_type)
                    title_end = remaining_content.find('}', title_start)
                    if title_end == -1:
                        break
                    
                    section_title = remaining_content[title_start:title_end]
                    
                    # Find the end of this section (start of next section or end of document)
                    section_end = float('inf')
                    for section_type in section_types:
                        pos = remaining_content.find(section_type, title_end)
                        if pos != -1 and pos < section_end:
                            section_end = pos
                    
                    if section_end == float('inf'):
                        # Last section, goes to the end
                        section_content = remaining_content[next_section_pos:]
                        current_pos = len(remaining_content)
                    else:
                        section_content = remaining_content[next_section_pos:section_end]
                        current_pos = section_end
                    
                    sections.append((section_title, section_content))
                
                # Filter sections based on selected components
                selected_sections = [content for title, content in sections if title in selected_components]
                
                # Combine everything with proper ordering
                filtered_content = pre_section_content + ''.join(selected_sections)
            
            # Construct the final document
            final_content = preamble + filtered_content + '\\end{document}'
            
            # Create custom directory with simple path
            temp_dir = tempfile.mkdtemp(prefix="latex_")
            print(f"Working in temporary directory: {temp_dir}")
            temp_tex_file = os.path.join(temp_dir, "document.tex")
            
            with open(temp_tex_file, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            # Compile the LaTeX file
            success = self.compile_latex(temp_tex_file)
            return success, output_file
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Error processing LaTeX: {str(e)}"
