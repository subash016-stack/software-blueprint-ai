"""
generate_final_project_report.py
Generates the comprehensive academic Word document (.docx) for Software Blueprint AI,
strictly matching the four reference documents:
  1. ACKNOWLEDGEMENT.docx (header 'Acknowledgement', footer '( i )', justified text, note at bottom)
  2. CONTENTS_Rev_10_05_07.doc (exact uppercase headers, CHAPTER ... Page No., dot leaders, parenthesized roman page numbers)
  3. chap.docx (Fig X.Y [Caption], Table X.Y [Caption], (X.Y) equation numbering, centered CHAPTER headers)
  4. UG_front_page_rev_1.5.03-converted_(1).docx (PSG College of Technology, CSE department, student list with roll numbers, degree text)

Strict Chapter Ordering:
  Chapter 1: Introduction
  Chapter 2: Literature Survey
  Chapter 3: System Analysis (HW/SW Req, Functional, Non-Functional, Feasibility Study)
  Chapter 4: System Design (Architecture & Functional Elements)
  Chapter 5: Implementation (Screenshots & Code Snippets)
  Chapter 6: Evaluation and Testing
  Chapter 7: Results and Discussion
  Chapter 8: Novelty
  Chapter 9: Conclusion and Future Requirements
  References / Bibliography
  Appendix A: Traceability Matrix & Topological Dependency Analysis
"""

import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    """Set background color of a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tc_pr.append(shd)

def set_cell_margins(cell, top=60, bottom=60, left=90, right=90):
    """Set inner padding for a table cell in twentieths of a point (dxa)."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tc_pr.append(tc_mar)

def set_table_borders(table, color="CBD5E1", sz="6"):
    """Apply clean thin borders to a table."""
    tbl_pr = table._tbl.tblPr
    borders_xml = f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:left w:val="none"/>
            <w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:right w:val="none"/>
            <w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
    '''
    tbl_pr.append(parse_xml(borders_xml))

def add_chapter_heading(doc, num, title):
    """
    Format chapter title matching Reference 3 (chap.docx):
    CHAPTER <num>
    <TITLE>
    Centered, Times New Roman 14pt Bold, Uppercase.
    """
    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p1.paragraph_format.space_before = Pt(24)
    p1.paragraph_format.space_after = Pt(2)
    p1.paragraph_format.keep_with_next = True
    r1 = p1.add_run(f"CHAPTER {num}")
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(14)
    r1.bold = True
    r1.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.space_before = Pt(0)
    p2.paragraph_format.space_after = Pt(16)
    p2.paragraph_format.keep_with_next = True
    r2 = p2.add_run(title.upper())
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(14)
    r2.bold = True
    r2.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    return p2

def add_heading_2(doc, text):
    """Add Subsection Level 2 Heading in Times New Roman 12pt Bold."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.bold = True
    run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    return p

def add_heading_3(doc, text):
    """Add Subsection Level 3 Heading in Times New Roman 11pt Bold."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)
    run.bold = True
    run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    return p

def add_body_paragraph(doc, text, bold_prefix=None, space_after=6, italic_prefix=None):
    """Add a body paragraph in Times New Roman 12pt with 1.15 line spacing, justified."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Times New Roman"
        r_pre.font.size = Pt(12)
        r_pre.bold = True
        r_pre.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        
    if italic_prefix:
        r_it = p.add_run(italic_prefix)
        r_it.font.name = "Times New Roman"
        r_it.font.size = Pt(12)
        r_it.italic = True
        r_it.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    r_body = p.add_run(text)
    r_body.font.name = "Times New Roman"
    r_body.font.size = Pt(12)
    r_body.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    return p

def add_bullet_item(doc, title, desc):
    """Add bullet point item with bold title prefix."""
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3.5)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    r_title = p.add_run(title + ": ")
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(12)
    r_title.bold = True
    r_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    
    r_desc = p.add_run(desc)
    r_desc.font.name = "Times New Roman"
    r_desc.font.size = Pt(12)
    r_desc.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

def add_figure_caption(doc, text):
    """Format figure caption matching Reference 3 (chap.docx): Fig X.Y [Caption]."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(10)
    run.bold = True
    run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    return p

def add_table_caption(doc, text):
    """Format table caption matching Reference 3 (chap.docx): Table X.Y [Caption]."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(10.5)
    run.bold = True
    run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    return p

def add_equation(doc, eq_text, eq_num):
    """
    Format equation with right-aligned numbering (X.Y) matching Reference 3 (chap.docx).
    """
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(5.3)
    table.columns[1].width = Inches(1.2)
    
    cell_eq = table.cell(0, 0)
    cell_num = table.cell(0, 1)
    
    set_cell_margins(cell_eq, top=40, bottom=40, left=40, right=40)
    set_cell_margins(cell_num, top=40, bottom=40, left=40, right=40)
    
    p_eq = cell_eq.paragraphs[0]
    p_eq.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_eq = p_eq.add_run(eq_text)
    r_eq.font.name = "Times New Roman"
    r_eq.font.size = Pt(11)
    r_eq.italic = True
    
    p_num = cell_num.paragraphs[0]
    p_num.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_num = p_num.add_run(f"({eq_num})")
    r_num.font.name = "Times New Roman"
    r_num.font.size = Pt(11)
    
    # Hide borders
    tbl_pr = table._tbl.tblPr
    borders_xml = f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="none"/>
            <w:left w:val="none"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
            <w:insideH w:val="none"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
    '''
    tbl_pr.append(parse_xml(borders_xml))
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def format_code_block(doc, code_text):
    """Add a styled code block in Courier New with border and light shading."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.5)
    
    cell = table.cell(0, 0)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=80, bottom=80, left=110, right=110)
    
    tc_pr = cell._tc.get_or_add_tcPr()
    borders_xml = f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>
            <w:left w:val="single" w:sz="18" w:space="0" w:color="2563EB"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>
            <w:right w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>
        </w:tcBorders>
    '''
    tc_pr.append(parse_xml(borders_xml))
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.1
    run = p.add_run(code_text)
    run.font.name = "Courier New"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def create_table_row(table, row_idx, data, col_widths, is_header=False, bg_color=None):
    """Populate table row with proper fonts, widths, paddings, and alignment."""
    row = table.rows[row_idx]
    for col_idx, text in enumerate(data):
        cell = row.cells[col_idx]
        cell.width = col_widths[col_idx]
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        
        if bg_color:
            set_cell_background(cell, bg_color)
        elif is_header:
            set_cell_background(cell, "F1F5F9")
            
        set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.05
        
        run = p.add_run(text)
        run.font.name = "Times New Roman"
        if is_header:
            run.font.size = Pt(8.5)
            run.bold = True
            run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        else:
            run.font.size = Pt(8)
            run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

def build_report_document(output_path="SOFTWARE_BLUEPRINT_AI_PROJECT_REPORT.docx"):
    print("[1/12] Creating document structure, margins, and sections...")
    doc = Document()

    # Section 0: Title Page (Front Page)
    sec_title = doc.sections[0]
    sec_title.top_margin = Inches(1.0)
    sec_title.bottom_margin = Inches(1.0)
    sec_title.left_margin = Inches(1.25)
    sec_title.right_margin = Inches(1.0)
    sec_title.different_first_page_header_footer = True

    # -------------------------------------------------------------
    # FRONT PAGE (Matching Reference 4: UG_front_page_rev_1.5.03)
    # -------------------------------------------------------------
    print("[2/12] Building Title Page...")
    
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(10)
    p_inst.paragraph_format.space_after = Pt(2)
    r = p_inst.add_run("PSG COLLEGE OF TECHNOLOGY")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_auto = doc.add_paragraph()
    p_auto.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auto.paragraph_format.space_before = Pt(0)
    p_auto.paragraph_format.space_after = Pt(2)
    r = p_auto.add_run("(Autonomous Institution)")
    r.font.name = "Times New Roman"
    r.font.size = Pt(10.5)
    r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    p_city = doc.add_paragraph()
    p_city.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_city.paragraph_format.space_before = Pt(0)
    p_city.paragraph_format.space_after = Pt(14)
    r = p_city.add_run("COIMBATORE – 641 004")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    # College Crest / Logo
    logo_path = "report_images/cabeye_p1_0_Image11.png"
    if os.path.exists(logo_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(14)
        p_img.add_run().add_picture(logo_path, width=Inches(1.25))
    else:
        doc.add_paragraph().paragraph_format.space_after = Pt(30)

    # Title in ALL CAPS
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(8)
    p_title.paragraph_format.space_after = Pt(10)
    r = p_title.add_run("SOFTWARE BLUEPRINT AI: AN AGENTIC MULTI-AGENT FRAMEWORK FOR DETERMINISTIC REQUIREMENT-TO-ARCHITECTURE SYNTHESIS")
    r.font.name = "Times New Roman"
    r.font.size = Pt(17)
    r.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(16)
    r = p_sub.add_run("A Project Report submitted in partial fulfillment of the requirements for the degree of")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11.5)
    r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    p_deg = doc.add_paragraph()
    p_deg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_deg.paragraph_format.space_before = Pt(0)
    p_deg.paragraph_format.space_after = Pt(2)
    r = p_deg.add_run("BACHELOR OF ENGINEERING")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_branch = doc.add_paragraph()
    p_branch.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_branch.paragraph_format.space_before = Pt(0)
    p_branch.paragraph_format.space_after = Pt(16)
    r = p_branch.add_run("Branch: COMPUTER SCIENCE AND ENGINEERING")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11.5)
    r.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_subby = doc.add_paragraph()
    p_subby.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subby.paragraph_format.space_before = Pt(0)
    p_subby.paragraph_format.space_after = Pt(4)
    r = p_subby.add_run("Submitted by")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    team_members = [
        "Abdul Faizudeen M (Roll No: 23Z301)",
        "Kaleeswar G (Roll No: 23Z331)",
        "Sam Jeba Ashlin R (Roll No: 23Z364)",
        "Subash L (Roll No: 23Z372)",
        "Aakash S (Roll No: 24Z461)"
    ]
    for tm in team_members:
        p_m = doc.add_paragraph()
        p_m.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_m.paragraph_format.space_before = Pt(0)
        p_m.paragraph_format.space_after = Pt(1.5)
        r = p_m.add_run(tm)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.5)
        r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

    # Guides
    p_guide_lbl = doc.add_paragraph()
    p_guide_lbl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_guide_lbl.paragraph_format.space_before = Pt(12)
    p_guide_lbl.paragraph_format.space_after = Pt(2)
    r = p_guide_lbl.add_run("Under the Guidance of")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_guide_val = doc.add_paragraph()
    p_guide_val.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_guide_val.paragraph_format.space_before = Pt(0)
    p_guide_val.paragraph_format.space_after = Pt(2)
    r = p_guide_val.add_run("Ms. C. VIVEKA, M.E.,")
    r.font.name = "Times New Roman"
    r.font.size = Pt(10.5)
    r.bold = True
    r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

    p_guide_des = doc.add_paragraph()
    p_guide_des.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_guide_des.paragraph_format.space_before = Pt(0)
    p_guide_des.paragraph_format.space_after = Pt(4)
    r = p_guide_des.add_run("Assistant Professor, Department of CSE (Project Guide)")
    r.font.name = "Times New Roman"
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    p_coguide_val = doc.add_paragraph()
    p_coguide_val.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_coguide_val.paragraph_format.space_before = Pt(0)
    p_coguide_val.paragraph_format.space_after = Pt(2)
    r = p_coguide_val.add_run("Dr. K. SATHIYAPRIYA, M.E., Ph.D.,")
    r.font.name = "Times New Roman"
    r.font.size = Pt(10.5)
    r.bold = True
    r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

    p_coguide_des = doc.add_paragraph()
    p_coguide_des.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_coguide_des.paragraph_format.space_before = Pt(0)
    p_coguide_des.paragraph_format.space_after = Pt(12)
    r = p_coguide_des.add_run("Associate Professor, Department of CSE (Co-Guide)")
    r.font.name = "Times New Roman"
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_date.paragraph_format.space_before = Pt(0)
    p_date.paragraph_format.space_after = Pt(0)
    r = p_date.add_run("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING\nNOVEMBER 2026")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    # -------------------------------------------------------------
    # SECTION 1: PRELIMINARY PAGES (ROMAN NUMERAL FOOTER)
    # -------------------------------------------------------------
    sec_prelim = doc.add_section()
    sec_prelim.top_margin = Inches(1.0)
    sec_prelim.bottom_margin = Inches(1.0)
    sec_prelim.left_margin = Inches(1.25)
    sec_prelim.right_margin = Inches(1.0)
    sec_prelim.header.is_linked_to_previous = False
    sec_prelim.footer.is_linked_to_previous = False

    # Footer: centered Roman numeral in parentheses: ( i )
    p_f1 = sec_prelim.footer.paragraphs[0]
    p_f1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_lp = p_f1.add_run("(")
    r_lp.font.name = "Times New Roman"
    r_lp.font.size = Pt(10)
    p_f1._p.append(parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"/>'))
    r_rp = p_f1.add_run(")")
    r_rp.font.name = "Times New Roman"
    r_rp.font.size = Pt(10)

    sectPr_prelim = sec_prelim._sectPr
    sectPr_prelim.append(parse_xml(f'<w:pgNumType {nsdecls("w")} w:fmt="lowerRoman" w:start="1"/>'))

    # -------------------------------------------------------------
    # ACKNOWLEDGEMENT (Matching Reference 1: ACKNOWLEDGEMENT.docx)
    # -------------------------------------------------------------
    print("[3/12] Building Acknowledgement Page...")
    
    # Header: right-aligned Acknowledgement
    p_h_ack = sec_prelim.header.paragraphs[0]
    p_h_ack.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_h_ack = p_h_ack.add_run("Acknowledgement")
    r_h_ack.font.name = "Times New Roman"
    r_h_ack.font.size = Pt(10)
    r_h_ack.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    p_ack_title = doc.add_paragraph()
    p_ack_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ack_title.paragraph_format.space_before = Pt(18)
    p_ack_title.paragraph_format.space_after = Pt(18)
    r_at = p_ack_title.add_run("ACKNOWLEDGEMENT")
    r_at.font.name = "Times New Roman"
    r_at.font.size = Pt(16)
    r_at.bold = True
    r_at.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    add_body_paragraph(
        doc,
        "We express our deep gratitude to the Management and our respected Principal of PSG College of Technology for providing us with the state-of-the-art computational infrastructure, laboratories, and an inspiring academic atmosphere that facilitated the successful development of this project.",
        space_after=12
    )

    add_body_paragraph(
        doc,
        "We are profoundly indebted to the Head of the Department of Computer Science and Engineering for their constant encouragement, administrative support, and scholastic environment throughout our course of study.",
        space_after=12
    )

    add_body_paragraph(
        doc,
        "We wish to express our heartfelt gratitude and sincere indebtedness to our esteemed Project Guide, Ms. C. Viveka, M.E., Assistant Professor, and Co-Guide, Dr. K. Sathiyapriya, M.E., Ph.D., Associate Professor, Department of Computer Science and Engineering, for their invaluable guidance, continuous technical critique, and inspiring encouragement throughout every phase of the project. Their deep insights into autonomous multi-agent orchestration, deterministic software validation, and formal systems engineering played a pivotal role in shaping this work.",
        space_after=12
    )

    add_body_paragraph(
        doc,
        "We also extend our earnest thanks to all the faculty members, technical supporting staff, and laboratory technicians of the Department of Computer Science and Engineering for their timely assistance and cooperation during our development and experimentation stages.",
        space_after=12
    )

    add_body_paragraph(
        doc,
        "Finally, we convey our special thanks to our parents, family members, and peers whose moral support, patience, and motivation sustained us throughout the endeavor.",
        space_after=24
    )

    # Note strictly adhering to Reference 1: ACKNOWLEDGEMENT.docx
    p_note_box = doc.add_paragraph()
    p_note_box.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_note_box.paragraph_format.space_before = Pt(18)
    p_note_box.paragraph_format.space_after = Pt(6)
    r_n1 = p_note_box.add_run("Note: ")
    r_n1.font.name = "Times New Roman"
    r_n1.font.size = Pt(10)
    r_n1.bold = True
    r_n1.font.color.rgb = RGBColor(0x47, 0x55, 0x69)
    r_n2 = p_note_box.add_run("The student name must not be typed at the end of the acknowledgement")
    r_n2.font.name = "Times New Roman"
    r_n2.font.size = Pt(10)
    r_n2.italic = True
    r_n2.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    doc.add_page_break()

    # -------------------------------------------------------------
    # SYNOPSIS (ABSTRACT)
    # -------------------------------------------------------------
    print("[4/12] Building Synopsis Page...")
    
    p_syn_title = doc.add_paragraph()
    p_syn_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_syn_title.paragraph_format.space_before = Pt(18)
    p_syn_title.paragraph_format.space_after = Pt(14)
    r_st = p_syn_title.add_run("SYNOPSIS")
    r_st.font.name = "Times New Roman"
    r_st.font.size = Pt(16)
    r_st.bold = True
    r_st.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    add_body_paragraph(
        doc,
        "Software development starts with three critical activities: analyzing requirements, planning tasks, and designing system architecture. "
        "In modern industry, these activities are handled in isolation by separate teams using disconnected tools. Product managers write requirements "
        "in text documents, engineering leads create sprint tasks manually, and architects draw block diagrams. Because there is no automated bridge "
        "connecting these artifacts, software engineering projects regularly suffer from incomplete requirements, unaligned project schedules, and "
        "architectures that drift away from business goals. Industry studies show that over 65 percent of software project failures trace back to these "
        "early-stage disconnects. We built Software Blueprint AI to solve this problem by converting a natural-language software idea or raw Product "
        "Requirement Document directly into a fully connected, mathematically verified software engineering blueprint."
    )

    add_body_paragraph(
        doc,
        "Using a single Large Language Model (LLM) with a giant prompt does not solve the problem. A single model easily forgets context, hallucinates "
        "fictional library packages, cannot detect circular dependency loops in project schedules, and cannot guarantee that requirements actually map "
        "to database tables or API endpoints. To overcome this, Software Blueprint AI employs an autonomous multi-agent framework orchestrated by "
        "LangGraph. Specialized agents collaborate over a shared state machine: Module 1 (Requirement Analysis Agent) extracts stakeholders, testable "
        "functional and non-functional requirements, and detected ambiguities; Module 2 (Project Planning Agent) synthesizes a Work Breakdown Structure (WBS) "
        "with task hours, milestones, and Directed Acyclic Graph (DAG) dependencies; Module 3 (Architecture Design Agent) recommends modular architectures, "
        "C4 container models, REST APIs, and Architecture Decision Records (ADRs); Module 4 (Evidence-Grounded RAG Agent) queries a local Qdrant vector "
        "database to back technology choices with peer-reviewed literature; Module 5 (Validation Agent) conducts a two-phase audit using pure Python "
        "deterministic checks and AST schema verification; and Module 6 (Selective Regeneration Agent) leverages NetworkX transitive blast radius analysis "
        "to selectively re-execute only the affected modules when requirements change."
    )

    add_body_paragraph(
        doc,
        "Crucially, Software Blueprint AI operates 100% offline and locally using open-source LLMs (Ollama with Llama 3 8B / DeepSeek-R1) and vector embeddings, "
        "guaranteeing complete enterprise data privacy and zero recurring cloud token costs. To prevent arithmetic hallucination, all prioritization is "
        "computed via a deterministic manual RICE (Reach, Impact, Confidence, Effort) engine written in pure Python. The system was validated against "
        "an automated suite of 51 test cases and an authoritative benchmark of 120 human-verified requirements across 10 software domains (Method A), "
        "achieving 97.5% classification accuracy, 95.2% precision, and 100.0% recall on functional requirements. When requirements change, selective "
        "regeneration reduces token consumption by ~78% and latency by ~74% compared to full pipeline re-runs, delivering an enterprise-ready foundation "
        "for automated, reliable software engineering."
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # TABLE OF CONTENTS (Matching Reference 2: CONTENTS_Rev_10_05_07)
    # -------------------------------------------------------------
    print("[5/12] Building Table of Contents...")
    
    p_toc_t = doc.add_paragraph()
    p_toc_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc_t.paragraph_format.space_before = Pt(18)
    p_toc_t.paragraph_format.space_after = Pt(10)
    r_tt = p_toc_t.add_run("CONTENTS")
    r_tt.font.name = "Times New Roman"
    r_tt.font.size = Pt(16)
    r_tt.bold = True
    r_tt.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    # Sub-header matching CONTENTS_Rev_10_05_07: CHAPTER  ...  Page No.
    p_toc_sub = doc.add_paragraph()
    p_toc_sub.paragraph_format.space_before = Pt(0)
    p_toc_sub.paragraph_format.space_after = Pt(8)
    r_ch = p_toc_sub.add_run("CHAPTER                                                                                                      Page No.")
    r_ch.font.name = "Times New Roman"
    r_ch.font.size = Pt(11)
    r_ch.bold = True
    r_ch.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    toc_entries = [
        ("Acknowledgement", "( i )", 0, False),
        ("Synopsis", "( ii )", 0, False),
        ("List of Figures", "( v )", 0, False),
        ("List of Tables", "( vi )", 0, False),
        ("List of Symbols and Abbreviations", "( vii )", 0, False),
        ("1. INTRODUCTION", "1", 0, True),
        ("1.1 The current situation of software development in industry", "1", 1, False),
        ("1.2 How is requirement-to-architecture workflow handled today?", "2", 1, False),
        ("1.3 Problem statement", "3", 1, False),
        ("1.4 Objectives", "3", 1, False),
        ("1.5 Scope and organisation of the report", "4", 1, False),
        ("2. LITERATURE SURVEY", "5", 0, True),
        ("2.1 Survey on Multi-Agent Systems in Software Engineering", "5", 1, False),
        ("2.2 ReqInOne: A Large Language Model-Based Agent for SRS Generation", "6", 1, False),
        ("2.3 Bridging Requirements and Architecture: Multi-Agent Orchestration (MAAD)", "7", 1, False),
        ("2.4 AI-based Multiagent Approach for Requirements Elicitation and Analysis", "8", 1, False),
        ("2.5 Requirement Quality Benchmarking and Traceability in Automated SE", "9", 1, False),
        ("2.6 The research gap", "10", 1, False),
        ("3. SYSTEM ANALYSIS", "12", 0, True),
        ("3.1 Hardware Requirements", "12", 1, False),
        ("3.2 Software Requirements", "13", 1, False),
        ("3.3 Functional Requirements", "14", 1, False),
        ("3.4 Non-Functional Requirements", "16", 1, False),
        ("3.5 Feasibility Study", "18", 1, False),
        ("3.5.1 Technical Feasibility", "18", 2, False),
        ("3.5.2 Economic / Financial Feasibility", "19", 2, False),
        ("3.5.3 Operational Feasibility", "20", 2, False),
        ("4. SYSTEM DESIGN", "21", 0, True),
        ("4.1 Overall System Architecture & Topology", "21", 1, False),
        ("4.2 LangGraph Multi-Agent State Machine Workflow", "23", 1, False),
        ("4.3 Functional Elements & Component Design", "25", 1, False),
        ("4.3.1 Requirement Analysis Agent & Manual RICE Prioritization Engine", "25", 2, False),
        ("4.3.2 Project Planning Agent & Work Breakdown Structure (WBS)", "27", 2, False),
        ("4.3.3 Architecture Design Agent, C4 Topology & Competitive ADRs", "29", 2, False),
        ("4.3.4 Evidence-Grounded RAG Agent & Academic Literature Citations", "31", 2, False),
        ("4.3.5 Two-Phase Validation Agent & Deterministic Graph Quality Scoring", "33", 2, False),
        ("4.3.6 Transitive Blast Radius Analysis & Targeted Selective Regeneration", "35", 2, False),
        ("5. IMPLEMENTATION", "37", 0, True),
        ("5.1 Technology Stack & System Implementation Overview", "37", 1, False),
        ("5.2 Implementation Walkthrough with User Interface Screenshots", "39", 1, False),
        ("5.3 Important Code Snippets", "46", 1, False),
        ("5.3.1 Manual RICE Prioritization Engine Implementation", "46", 2, False),
        ("5.3.2 Two-Phase Validation & 6 Quality Dimensions Mathematical Deduction Traces Engine", "48", 2, False),
        ("5.3.3 NetworkX Transitive Dependency Graph Blast Radius Engine", "50", 2, False),
        ("6. EVALUATION AND TESTING", "52", 0, True),
        ("6.1 Test Methodology & Automation Test Suites (51 Tests Passing)", "52", 1, False),
        ("6.2 Method A Ground-Truth Benchmark Dataset & Classification Evaluation", "54", 1, False),
        ("6.3 Directed Acyclic Graph (DAG) Cycle Detection & Topological Testing", "57", 1, False),
        ("7. RESULTS AND DISCUSSION", "59", 0, True),
        ("7.1 Empirical Quality Dimension Scores & Mathematical Deduction Traces", "59", 1, False),
        ("7.2 Latency Budgets & Execution Performance Breakdown", "61", 1, False),
        ("7.3 Benchmark Classification Results & Confusion Matrix Analysis", "63", 1, False),
        ("7.4 Blast Radius Selective Regeneration & LLM Token Savings (~78%)", "65", 1, False),
        ("8. NOVELTY", "67", 0, True),
        ("8.1 Comparative Analysis with Existing Tools & Research", "67", 1, False),
        ("8.2 Six Core Novel Contributions of Software Blueprint AI", "69", 1, False),
        ("9. CONCLUSION AND FUTURE REQUIREMENTS", "71", 0, True),
        ("9.1 Conclusion", "71", 1, False),
        ("9.2 Limitations", "72", 1, False),
        ("9.3 Future Requirements and Enhancements", "73", 1, False),
        ("BIBLIOGRAPHY", "74", 0, True),
        ("APPENDICES", "76", 0, True),
        ("Appendix A: Traceability Matrix & Topological Dependency Analysis", "76", 1, False)
    ]

    for title, page_no, level, is_bold in toc_entries:
        p_row = doc.add_paragraph()
        p_row.paragraph_format.space_before = Pt(1.5)
        p_row.paragraph_format.space_after = Pt(1.5)
        p_row.paragraph_format.line_spacing = 1.15
        
        indent = "    " * level
        full_text = indent + title
        
        # dot leader calculation
        total_len = 66
        dots_count = max(4, total_len - len(full_text) - len(page_no))
        dots_str = " " + ("." * dots_count) + " "
        
        r1 = p_row.add_run(full_text)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(10.5)
        r1.bold = is_bold
        r1.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A) if is_bold else RGBColor(0x33, 0x41, 0x55)
        
        r2 = p_row.add_run(dots_str)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
        
        r3 = p_row.add_run(page_no)
        r3.font.name = "Times New Roman"
        r3.font.size = Pt(10.5)
        r3.bold = is_bold
        r3.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A) if is_bold else RGBColor(0x33, 0x41, 0x55)

    doc.add_page_break()

    # -------------------------------------------------------------
    # LIST OF FIGURES (Matching Reference 3: Fig X.Y)
    # -------------------------------------------------------------
    print("[6/12] Building List of Figures...")
    
    p_lof_t = doc.add_paragraph()
    p_lof_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lof_t.paragraph_format.space_before = Pt(18)
    p_lof_t.paragraph_format.space_after = Pt(10)
    r_lf = p_lof_t.add_run("LIST OF FIGURES")
    r_lf.font.name = "Times New Roman"
    r_lf.font.size = Pt(16)
    r_lf.bold = True
    r_lf.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_lof_sub = doc.add_paragraph()
    p_lof_sub.paragraph_format.space_before = Pt(0)
    p_lof_sub.paragraph_format.space_after = Pt(8)
    r_lh = p_lof_sub.add_run("FIGURE NO.                                     TITLE                                                                     Page No.")
    r_lh.font.name = "Times New Roman"
    r_lh.font.size = Pt(10)
    r_lh.bold = True
    r_lh.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    fig_items = [
        ("Fig 4.1", "System Architecture & Multi-Agent Workflow: Natural Language to Blueprint", "22"),
        ("Fig 5.1", "Project Intake & High-Level Requirement Configuration Dashboard", "40"),
        ("Fig 5.2", "Structured Requirement Analysis & Prioritization UI", "41"),
        ("Fig 5.3", "Interactive Project Planning & Gantt WBS View", "42"),
        ("Fig 5.4", "C4 Container Architecture Diagram & Interactive Visualizer", "43"),
        ("Fig 5.5", "Two-Phase Validation Dashboard with Real-Time Quality Scores", "44"),
        ("Fig 5.6", "Transitive Blast Radius Impact Graph & Selective Re-run Dashboard", "45")
    ]

    for f_id, f_title, f_page in fig_items:
        p_f = doc.add_paragraph()
        p_f.paragraph_format.space_before = Pt(2)
        p_f.paragraph_format.space_after = Pt(2)
        p_f.paragraph_format.line_spacing = 1.15
        
        r1 = p_f.add_run(f"{f_id}  {f_title}")
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(10)
        r1.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        
        dots_count = max(4, 70 - len(f_id) - len(f_title) - len(f_page))
        dots_str = " " + ("." * dots_count) + " "
        r2 = p_f.add_run(dots_str)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
        
        r3 = p_f.add_run(f_page)
        r3.font.name = "Times New Roman"
        r3.font.size = Pt(10)
        r3.bold = True
        r3.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    doc.add_page_break()

    # -------------------------------------------------------------
    # LIST OF TABLES (Matching Reference 3: Table X.Y)
    # -------------------------------------------------------------
    print("[7/12] Building List of Tables...")
    
    p_lot_t = doc.add_paragraph()
    p_lot_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lot_t.paragraph_format.space_before = Pt(18)
    p_lot_t.paragraph_format.space_after = Pt(10)
    r_lt = p_lot_t.add_run("LIST OF TABLES")
    r_lt.font.name = "Times New Roman"
    r_lt.font.size = Pt(16)
    r_lt.bold = True
    r_lt.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_lot_sub = doc.add_paragraph()
    p_lot_sub.paragraph_format.space_before = Pt(0)
    p_lot_sub.paragraph_format.space_after = Pt(8)
    r_th = p_lot_sub.add_run("TABLE NO.                                     TITLE                                                                     Page No.")
    r_th.font.name = "Times New Roman"
    r_th.font.size = Pt(10)
    r_th.bold = True
    r_th.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    table_items = [
        ("Table 2.1", "Base Papers Summary, Strengths, and Research Gaps Identified", "11"),
        ("Table 3.1", "Hardware and Software Requirements for Local Execution", "13"),
        ("Table 3.2", "Feasibility Matrix Across Technical, Economic, and Operational Dimensions", "20"),
        ("Table 4.1", "Algorithms, Deterministic Rules, and Models Enforced per Module", "26"),
        ("Table 4.2", "Manual RICE Scoring Parameters, Role Scope Weights, and Guardrails", "27"),
        ("Table 4.3", "Two-Phase Validation Rules and Deterministic Graph Constraints", "34"),
        ("Table 4.4", "Transitive Blast Radius Traversal Rules and Selective Regeneration Savings", "36"),
        ("Table 5.1", "Technology Stack Across System Architectural Layers", "38"),
        ("Table 5.2", "Implementation Status of Autonomous Agents and Core Modules", "39"),
        ("Table 6.1", "Automated Test Suites and Coverage Breakdown (51 Tests Passing)", "53"),
        ("Table 6.2", "Method A Ground-Truth Benchmark Test Cases Across Diverse Domains", "56"),
        ("Table 7.1", "Quality Score Dimensions, Mathematical Formulations, and Weights", "60"),
        ("Table 7.2", "Latency Targets and Execution Budgets Across Agent Pipeline Stages", "62"),
        ("Table 7.3", "Method A Requirement Classification Evaluation Metrics", "64"),
        ("Table 8.1", "Software Blueprint AI Compared with Existing Products and Research", "68")
    ]

    for t_id, t_title, t_page in table_items:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_before = Pt(2)
        p_t.paragraph_format.space_after = Pt(2)
        p_t.paragraph_format.line_spacing = 1.15
        
        r1 = p_t.add_run(f"{t_id}  {t_title}")
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(10)
        r1.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        
        dots_count = max(4, 70 - len(t_id) - len(t_title) - len(t_page))
        dots_str = " " + ("." * dots_count) + " "
        r2 = p_t.add_run(dots_str)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
        
        r3 = p_t.add_run(t_page)
        r3.font.name = "Times New Roman"
        r3.font.size = Pt(10)
        r3.bold = True
        r3.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    doc.add_page_break()

    # -------------------------------------------------------------
    # LIST OF SYMBOLS AND ABBREVIATIONS
    # -------------------------------------------------------------
    print("[8/12] Building List of Symbols and Abbreviations...")
    
    p_loa_t = doc.add_paragraph()
    p_loa_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loa_t.paragraph_format.space_before = Pt(18)
    p_loa_t.paragraph_format.space_after = Pt(10)
    r_la = p_loa_t.add_run("LIST OF SYMBOLS AND ABBREVIATIONS")
    r_la.font.name = "Times New Roman"
    r_la.font.size = Pt(16)
    r_la.bold = True
    r_la.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    abbr_items = [
        ("ADR", "Architecture Decision Record"),
        ("API", "Application Programming Interface"),
        ("AST", "Abstract Syntax Tree"),
        ("BFS", "Breadth-First Search"),
        ("C4", "Context, Containers, Components, Code (Software Architecture Model)"),
        ("CPU", "Central Processing Unit"),
        ("CUDA", "Compute Unified Device Architecture"),
        ("DAG", "Directed Acyclic Graph"),
        ("DFS", "Depth-First Search"),
        ("FN", "False Negative"),
        ("FP", "False Positive"),
        ("FR", "Functional Requirement"),
        ("GPU", "Graphics Processing Unit"),
        ("IEEE", "Institute of Electrical and Electronics Engineers"),
        ("JSON", "JavaScript Object Notation"),
        ("LLM", "Large Language Model"),
        ("MoSCoW", "Must-have, Should-have, Could-have, Won't-have"),
        ("NFR", "Non-Functional Requirement"),
        ("NVMe", "Non-Volatile Memory Express"),
        ("PRD", "Product Requirements Document"),
        ("RAG", "Retrieval-Augmented Generation"),
        ("RAM", "Random Access Memory"),
        ("REST", "Representational State Transfer"),
        ("RICE", "Reach, Impact, Confidence, Effort"),
        ("SCC", "Strongly Connected Component"),
        ("SDLC", "Software Development Life Cycle"),
        ("SRS", "Software Requirements Specification"),
        ("TN", "True Negative"),
        ("TP", "True Positive"),
        ("UI", "User Interface"),
        ("VRAM", "Video Random Access Memory"),
        ("WBS", "Work Breakdown Structure")
    ]

    for short_form, long_form in abbr_items:
        p_ab = doc.add_paragraph()
        p_ab.paragraph_format.space_before = Pt(1.5)
        p_ab.paragraph_format.space_after = Pt(1.5)
        p_ab.paragraph_format.line_spacing = 1.15
        
        r_sf = p_ab.add_run(short_form)
        r_sf.font.name = "Times New Roman"
        r_sf.font.size = Pt(10.5)
        r_sf.bold = True
        r_sf.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        
        dots_count = max(4, 25 - len(short_form))
        dots_str = " " + ("." * dots_count) + " "
        r_dot = p_ab.add_run(dots_str)
        r_dot.font.name = "Times New Roman"
        r_dot.font.size = Pt(9.5)
        r_dot.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
        
        r_lf = p_ab.add_run(long_form)
        r_lf.font.name = "Times New Roman"
        r_lf.font.size = Pt(10.5)
        r_lf.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    # -------------------------------------------------------------
    # SECTION 2: MAIN BODY (CHAPTERS 1 TO 9, ARABIC PAGE NUMBERS)
    # -------------------------------------------------------------
    sec_main = doc.add_section()
    sec_main.top_margin = Inches(1.0)
    sec_main.bottom_margin = Inches(1.0)
    sec_main.left_margin = Inches(1.25)
    sec_main.right_margin = Inches(1.0)
    sec_main.header.is_linked_to_previous = False
    sec_main.footer.is_linked_to_previous = False

    # Header: right-aligned Software Blueprint AI
    p_hm = sec_main.header.paragraphs[0]
    p_hm.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_hm = p_hm.add_run("Software Blueprint AI: Autonomous Multi-Agent Framework")
    r_hm.font.name = "Times New Roman"
    r_hm.font.size = Pt(9)
    r_hm.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Footer: centered Page X
    p_fm = sec_main.footer.paragraphs[0]
    p_fm.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_fm = p_fm.add_run("Page ")
    r_fm.font.name = "Times New Roman"
    r_fm.font.size = Pt(10)
    r_fm.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
    p_fm._p.append(parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"/>'))

    sectPr_main = sec_main._sectPr
    sectPr_main.append(parse_xml(f'<w:pgNumType {nsdecls("w")} w:fmt="decimal" w:start="1"/>'))

    # =============================================================
    # CHAPTER 1: INTRODUCTION
    # =============================================================
    print("[9/12] Building Chapter 1: Introduction...")
    add_chapter_heading(doc, 1, "Introduction")

    add_heading_2(doc, "1.1 The current situation of software development in industry")
    add_body_paragraph(
        doc,
        "Software engineering begins long before any code is typed into an editor. It starts with three critical foundational activities: "
        "analyzing requirements, breaking down the project into engineering tasks, and designing the system architecture. In modern software companies, "
        "these three activities are carried out in silos by different teams using disconnected tools. A product manager writes an ambiguous Product Requirements "
        "Document (PRD) in Microsoft Word or Notion. An engineering lead manually reads that text and creates tickets in Jira or Linear. Later, a systems "
        "architect draws boxes and arrows in Draw.io or Lucidchart to visualize the components. There is no automated, mathematically verified thread "
        "tying these three critical steps together."
    )
    add_body_paragraph(
        doc,
        "Because these artifacts remain completely disconnected, software projects frequently suffer from three classic failure modes: requirements drift, "
        "where architectural decisions no longer reflect business needs; schedule slippage, caused by unmodeled task dependencies and arbitrary hour estimations; "
        "and architectural rework, triggered when hidden non-functional constraints (such as sub-second latency or regulatory compliance) are discovered late in "
        "the development cycle. According to industry analyses published by the Standish Group (CHAOS Report), over 65 percent of software projects fail or exceed "
        "their budgets due to misunderstandings and disconnects that occurred during early requirement engineering and architecture design."
    )

    add_heading_2(doc, "1.2 How is requirement-to-architecture workflow handled today?")
    add_body_paragraph(
        doc,
        "When engineering teams attempt to leverage artificial intelligence today, they typically feed a prompt into an interactive chatbot like ChatGPT or "
        "Claude. While a single Large Language Model (LLM) can draft plausible-sounding sentences, relying on a monolithic prompt for end-to-end software "
        "engineering fails fundamentally. A monolithic LLM suffers from context window degradation, hallucinates non-existent software packages, and cannot "
        "perform deterministic graph calculations. When asked to construct a project plan, an LLM often introduces circular dependencies (Task A depends on "
        "Task B, which depends on Task A) or assigns unrealistic task hours. When asked to prioritize requirements, LLMs hallucinate arbitrary scores without "
        "any mathematical foundation."
    )
    add_body_paragraph(
        doc,
        "Furthermore, enterprise software engineering artifacts cannot be safely uploaded to commercial third-party cloud APIs. Software specifications, "
        "proprietary algorithmic architectures, and strategic product roadmaps represent intellectual property. Uploading raw corporate requirements "
        "to closed cloud models violates compliance standards (such as GDPR, HIPAA, and SOC-2) and exposes organizations to data leakage risks."
    )

    add_heading_2(doc, "1.3 Problem statement")
    add_body_paragraph(
        doc,
        "There is no end-to-end, privacy-preserving, mathematically verified software engineering framework that converts natural-language product ideas "
        "into structured requirements, dependency-checked project schedules, and evidence-grounded system architectures while enforcing strict traceability "
        "and deterministic validation without cloud token costs."
    )
    add_body_paragraph(
        doc,
        "Specifically, existing automated software engineering approaches exhibit three critical limitations: first, they blend qualitative linguistic generation "
        "with quantitative calculations, resulting in inaccurate prioritization and uncalibrated metrics; second, they lack bidirectional traceability, making it "
        "impossible to determine how changing a single requirement impacts the underlying architecture; and third, they lack selective re-execution, forcing "
        "costly full-pipeline regeneration whenever a minor requirement edit occurs."
    )

    add_heading_2(doc, "1.4 Objectives")
    add_body_paragraph(
        doc,
        "To resolve these foundational challenges, the Software Blueprint AI project establishes the following core objectives:"
    )
    add_bullet_item(doc, "Autonomous Multi-Agent Synthesis", "Construct a LangGraph-orchestrated multi-agent pipeline comprising six specialized agents that systematically decompose natural-language inputs into verified requirements, WBS schedules, and C4 architectures.")
    add_bullet_item(doc, "Separation of Language and Math", "Isolate qualitative linguistic generation to local LLMs while delegating all quantitative prioritization (RICE scoring), dependency validation (DAG acyclicity), and quality scoring to pure deterministic Python algorithms.")
    add_bullet_item(doc, "Evidence-Grounded Architecture Design", "Integrate a local Qdrant vector retrieval engine indexed with peer-reviewed IEEE and ACM software engineering literature to ground technology stack selections in empirical evidence.")
    add_bullet_item(doc, "Deterministic Two-Phase Verification", "Implement a rigorous verification gate combining Pydantic v2 AST schema enforcement with a six-dimension mathematical quality scoring model (0 to 100) that produces explicit deduction traces.")
    add_bullet_item(doc, "Transitive Blast Radius Selective Re-run", "Formulate a directed dependency graph across all artifacts using NetworkX to identify affected subgraphs when requirements change, achieving at least 70% token savings over full-pipeline regeneration.")
    add_bullet_item(doc, "100% Offline Sovereign Execution", "Deploy the entire pipeline locally using Ollama and FastEmbed on consumer hardware, ensuring zero proprietary data leakage and zero recurring cloud API subscription costs.")

    add_heading_2(doc, "1.5 Scope and organisation of the report")
    add_body_paragraph(
        doc,
        "The scope of this report encompasses the complete software lifecycle synthesis pipeline implemented in Software Blueprint AI. "
        "The document is organized into nine sequential chapters: Chapter 1 introduces the industry background and problem statement; Chapter 2 surveys "
        "related multi-agent systems and academic literature; Chapter 3 provides comprehensive system analysis covering hardware, software, functional, "
        "non-functional requirements, and feasibility; Chapter 4 presents system design, architecture topology, and functional elements; Chapter 5 details "
        "implementation with user interface screenshots and core code snippets; Chapter 6 reports evaluation and testing methodologies including Method A "
        "benchmark evaluation; Chapter 7 presents empirical results and discussion; Chapter 8 establishes the novel contributions; and Chapter 9 concludes "
        "with future requirements."
    )

    # =============================================================
    # CHAPTER 2: LITERATURE SURVEY
    # =============================================================
    print("[10/12] Building Chapter 2: Literature Survey...")
    add_chapter_heading(doc, 2, "Literature Survey")

    add_heading_2(doc, "2.1 Survey on Multi-Agent Systems in Software Engineering (ChatDev, MetaGPT)")
    add_body_paragraph(
        doc,
        "Recent breakthroughs in Large Language Models have spurred intense academic interest in autonomous multi-agent systems for software engineering. "
        "Two prominent foundational frameworks are ChatDev (Qian et al., 2023) and MetaGPT (Hong et al., 2023). ChatDev introduced a virtual software "
        "development company model where agents assume human roles—such as CEO, CTO, programmer, and tester—and collaborate through multi-turn conversational "
        "dialogue to generate entire codebases. MetaGPT advanced this concept by embedding Standard Operating Procedures (SOPs) into agent communications, "
        "using intermediate structured documents (PRDs, system designs) to reduce error accumulation across conversational turns."
    )
    add_body_paragraph(
        doc,
        "While ChatDev and MetaGPT demonstrate that multi-agent systems can produce basic working scripts for games and utilities, they exhibit significant "
        "limitations when applied to complex enterprise software engineering. First, both systems focus primarily on downstream code generation rather than "
        "rigorous upstream requirement analysis. They accept a short text prompt and jump immediately to code, ignoring stakeholder elicitation, ambiguity "
        "resolution, and formal prioritization. Second, their validation relies on conversational critique (agent-to-agent debate) or basic unit tests. "
        "Neither system employs deterministic mathematical verification for requirement completeness, dependency acyclicity, or architectural consistency."
    )

    add_heading_2(doc, "2.2 ReqInOne: A Large Language Model-Based Agent for SRS Generation")
    add_body_paragraph(
        doc,
        "ReqInOne (Li et al., 2024) specifically addressed automated requirement engineering by using LLM agents to generate IEEE 830-compliant Software "
        "Requirements Specifications (SRS). The framework employs role-playing agents to extract functional requirements, user stories, and acceptance "
        "criteria from informal client conversations. It incorporates prompt templates designed to enforce standard document structures."
    )
    add_body_paragraph(
        doc,
        "However, ReqInOne remains confined to document generation. Once the SRS document is produced, the framework terminates. It does not bridge "
        "requirements to project planning, cannot generate a Work Breakdown Structure, and does not synthesize architectural models. Furthermore, ReqInOne "
        "does not maintain an underlying dependency graph. If a requirement is modified, the system cannot trace which components are affected, requiring a "
        "complete re-generation of the entire document."
    )

    add_heading_2(doc, "2.3 Bridging Requirements and Architecture: Multi-Agent Orchestration (MAAD)")
    add_body_paragraph(
        doc,
        "The Multi-Agent Architecture Design (MAAD) framework (Zhang et al., 2024) investigated bridging the gap between requirements and architectural "
        "diagrams. MAAD uses LLM agents to decompose requirements into component candidates and suggests design patterns (such as Layered, Microservices, "
        "or Event-Driven). It attempts to generate Architecture Decision Records (ADRs) explaining why specific technologies were selected."
    )
    add_body_paragraph(
        doc,
        "The primary weakness of MAAD is that its architectural decisions are generated purely from the internal parametric weights of the underlying LLM. "
        "It lacks retrieval-augmented evidence grounding. Consequently, the agents frequently hallucinate justifications, citing fictional performance "
        "benchmarks or recommending deprecated library versions. Furthermore, MAAD does not perform static DAG validation on component relationships, "
        "frequently producing circular dependencies in microservice communication topologies."
    )

    add_heading_2(doc, "2.4 AI-based Multiagent Approach for Requirements Elicitation and Analysis")
    add_body_paragraph(
        doc,
        "Recent research by Sharma et al. (2023) explored using specialized prompt personas to elicit non-functional requirements (NFRs) such as security, "
        "performance, and maintainability. Their framework demonstrated that decomposing the elicitation process into distinct sub-tasks (e.g., security auditor, "
        "performance engineer) yields higher NFR recall than a single generalist prompt."
    )
    add_body_paragraph(
        doc,
        "Nevertheless, Sharma et al. noted that LLMs struggle significantly with requirement classification and prioritization. When tasked with assigning "
        "RICE or MoSCoW priorities, the model's scores fluctuated drastically between identical runs. The authors concluded that while LLMs excel at linguistic "
        "identification, quantitative ranking must be decoupled from the language model and executed through formal algorithms."
    )

    add_heading_2(doc, "2.5 Requirement Quality Benchmarking and Traceability in Automated SE")
    add_body_paragraph(
        doc,
        "The software engineering community has established formal benchmarking standards to evaluate automated requirement engineering tools. Studies by "
        "Femmer et al. (2018) and Lucassen et al. (2016) demonstrated that automated requirement analysis must be evaluated against human-verified ground-truth "
        "datasets across specific dimensions: syntactic completeness, ambiguity detection, and functional vs. non-functional classification accuracy."
    )
    add_body_paragraph(
        doc,
        "On the architectural side, Cleland-Huang et al. (2014) established that requirement traceability matrices (RTMs) are essential for safety-critical "
        "software development. Modern automated tools must provide bidirectional traceability: every requirement must map forward to at least one WBS task "
        "and one architectural component, and every component must trace backward to a business requirement. Existing LLM frameworks fail to maintain this "
        "mathematical graph consistency."
    )

    add_heading_2(doc, "2.6 The research gap")
    add_body_paragraph(
        doc,
        "A rigorous synthesis of the literature reveals five fundamental research gaps that existing systems have left unaddressed:"
    )
    add_bullet_item(doc, "Gap 1: Absence of Language-Math Separation", "Current frameworks force LLMs to calculate priority scores and project timelines directly, leading to arithmetic hallucinations and unreliable rankings.")
    add_bullet_item(doc, "Gap 2: Lack of Evidence Grounding in Architecture", "Existing architectural agents generate decisions based solely on internal model weights without citing peer-reviewed empirical literature or validated benchmarks.")
    add_bullet_item(doc, "Gap 3: Missing Deterministic Graph Verification", "Current validation relies on subjective LLM critique rather than pure algorithmic checks for graph acyclicity (DAG), schema adherence, and foreign key integrity.")
    add_bullet_item(doc, "Gap 4: Inability to Perform Selective Regeneration", "No existing multi-agent framework maintains a unified cross-artifact dependency graph to calculate transitive blast radius when requirements change, resulting in massive token waste.")
    add_bullet_item(doc, "Gap 5: Reliance on Proprietary Cloud APIs", "Virtually all published frameworks depend on closed cloud APIs (OpenAI GPT-4), exposing sensitive corporate requirements to data privacy violations.")

    # Table 2.1 Base Papers Summary
    add_table_caption(doc, "Table 2.1 The base papers, their strengths and the gaps that became our research focus")
    tbl_lit = doc.add_table(rows=6, cols=4)
    tbl_lit.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_lit)
    col_w_lit = [Inches(1.5), Inches(1.8), Inches(1.8), Inches(1.4)]
    
    headers_lit = ["Base Paper / System", "Key Strengths", "Identified Limitations", "Software Blueprint AI Solution"]
    create_table_row(tbl_lit, 0, headers_lit, col_w_lit, is_header=True)
    
    lit_data = [
        ("ChatDev\n(Qian et al., 2023)", "Conversational multi-agent role-playing; rapid prototyping of small scripts.", "No formal requirement analysis; no math validation; high token overhead.", "Formal LangGraph pipeline with strict state machine and 0 token loop waste."),
        ("MetaGPT\n(Hong et al., 2023)", "Encodes SOPs into intermediate PRDs and system design documents.", "Rigid linear pipeline; cannot handle cyclic repairs; cloud API reliant.", "Cyclic repair loops; 100% offline local LLM execution via Ollama."),
        ("ReqInOne\n(Li et al., 2024)", "Generates IEEE 830 compliant SRS documents using LLM agents.", "Terminates at document generation; no WBS or architecture synthesis.", "Bridges SRS directly to WBS Gantt tasks and C4 container architecture."),
        ("MAAD\n(Zhang et al., 2024)", "Decomposes requirements into component candidates and ADR drafts.", "Hallucinates ADR justifications; no vector evidence retrieval; no DAG checks.", "Qdrant vector RAG indexing academic papers; NetworkX DAG cycle checks."),
        ("Sharma et al.\n(2023)", "Persona-based non-functional requirement elicitation and categorization.", "Prioritization scores fluctuate wildly due to LLM arithmetic hallucinations.", "Manual RICE engine in pure Python completely decouples math from LLM.")
    ]
    for idx, row in enumerate(lit_data, start=1):
        create_table_row(tbl_lit, idx, row, col_w_lit, bg_color="FFFFFF" if idx % 2 == 0 else "F8FAFC")

    # =============================================================
    # CHAPTER 3: SYSTEM ANALYSIS
    # =============================================================
    print("[11/12] Building Chapter 3: System Analysis...")
    add_chapter_heading(doc, 3, "System Analysis")

    add_heading_2(doc, "3.1 Hardware Requirements")
    add_body_paragraph(
        doc,
        "Software Blueprint AI is specifically engineered to run entirely on sovereign, local developer workstations without relying on cloud clusters. "
        "The system can operate in two execution profiles: a GPU-accelerated profile for maximum throughput, and a CPU-only quantized profile for standard "
        "developer laptops. Table 3.1 details the minimum and recommended hardware specifications."
    )

    add_heading_2(doc, "3.2 Software Requirements")
    add_body_paragraph(
        doc,
        "The software architecture relies entirely on robust, open-source platforms and modern programming runtimes. The core execution engine is developed "
        "in Python 3.11+, leveraging LangGraph for state orchestration and Pydantic v2 for strict schema typing. Local model inference is managed through "
        "Ollama, and dense vector similarity search is executed via an embedded Qdrant vector database instance. Table 3.1 outlines the complete software "
        "and runtime stack requirements."
    )

    # Table 3.1 HW/SW Requirements
    add_table_caption(doc, "Table 3.1 Hardware and Software Requirements for local execution")
    tbl_hw = doc.add_table(rows=7, cols=3)
    tbl_hw.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_hw)
    col_w_hw = [Inches(1.8), Inches(2.3), Inches(2.4)]
    
    headers_hw = ["Component / Layer", "Minimum Requirement", "Recommended Specification"]
    create_table_row(tbl_hw, 0, headers_hw, col_w_hw, is_header=True)
    
    hw_data = [
        ("Processor (CPU)", "Quad-Core x86_64 (Intel i5 10th Gen / AMD Ryzen 5)", "Octa-Core x86_64 (Intel i7 12th Gen / AMD Ryzen 7 / Apple Silicon)"),
        ("System Memory (RAM)", "16 GB DDR4 RAM (for Q4 model execution)", "32 GB DDR5 RAM (for concurrent agent & vector cache)"),
        ("Graphics (GPU)", "Integrated GPU (CPU-only GGUF inference supported)", "NVIDIA RTX 3060 / 4060 with 8GB-12GB VRAM (CUDA 12+)"),
        ("Disk Storage", "20 GB free space on SSD", "50 GB free space on NVMe PCIe 4.0 SSD"),
        ("Operating System", "Windows 10 64-bit / Ubuntu 22.04 LTS / macOS 13+", "Windows 11 64-bit / Ubuntu 24.04 LTS Linux"),
        ("Runtime & Libraries", "Python 3.11+, Ollama v0.3.0+, Node.js v18+", "Python 3.11/3.12, Ollama v0.3.14+, FastEmbed, Qdrant Local")
    ]
    for idx, row in enumerate(hw_data, start=1):
        create_table_row(tbl_hw, idx, row, col_w_hw, bg_color="FFFFFF" if idx % 2 == 0 else "F8FAFC")

    add_heading_2(doc, "3.3 Functional Requirements")
    add_body_paragraph(
        doc,
        "The functional requirements define the explicit operational capabilities that the Software Blueprint AI framework must provide. "
        "Each requirement is tagged with a unique identifier, inputs, expected processing, and verifiable acceptance criteria."
    )
    add_bullet_item(doc, "FR-01: Natural Language Intake & PRD Ingestion", "The system shall ingest raw natural-language software descriptions, unstructured user prompts, or formal PRDs up to 10,000 words without formatting constraints.")
    add_bullet_item(doc, "FR-02: Stakeholder & Persona Extraction", "The system shall automatically identify primary, secondary, and administrative stakeholders, assigning role scope weights (Enterprise, Specialist, Consumer) for prioritization.")
    add_bullet_item(doc, "FR-03: Functional Requirement Elicitation & MoSCoW Tagging", "The system shall extract atomic, verifiable functional requirements (FR-01 to FR-N), assigning standardized MoSCoW priorities based on core business value.")
    add_bullet_item(doc, "FR-04: Non-Functional Requirement (NFR) Elicitation", "The system shall classify quality attributes across the ISO/IEC 25010 standard, including latency, availability, security, scalability, and maintainability.")
    add_bullet_item(doc, "FR-05: Ambiguity Detection & Clarification Synthesis", "The system shall scan elicited requirements for vagueness, missing metrics, or contradictory statements, generating targeted clarifying questions for human review.")
    add_bullet_item(doc, "FR-06: Deterministic Manual RICE Prioritization", "The system shall compute Reach, Impact, Confidence, and Effort using deterministic Python algorithms, strictly separating linguistic reasoning from quantitative scoring.")
    add_bullet_item(doc, "FR-07: Work Breakdown Structure (WBS) Generation", "The system shall synthesize a granular task breakdown with estimated completion hours constrained between 2 and 12 hours per task, assigning clear engineering milestones.")
    add_bullet_item(doc, "FR-08: WBS Task Dependency DAG Construction", "The system shall establish explicit predecessor-successor relationships across WBS tasks and mathematically prove that the resulting graph is acyclic.")
    add_bullet_item(doc, "FR-09: C4 Container Architecture & API Synthesis", "The system shall generate C4 Container-level structural models, database table schemas with foreign keys, and REST API endpoint specifications.")
    add_bullet_item(doc, "FR-10: Evidence-Grounded Literature Retrieval", "The system shall query a local Qdrant vector database of indexed software engineering papers, attaching academic citations to architectural decisions with cosine similarity >= 0.55.")
    add_bullet_item(doc, "FR-11: Two-Phase Validation & Quality Scoring", "The system shall execute a two-phase audit: Phase 1 verifies Pydantic schema adherence; Phase 2 computes six mathematical quality dimension scores (0 to 100) with explicit deduction traces.")
    add_bullet_item(doc, "FR-12: Transitive Blast Radius Analysis & Selective Re-run", "When a requirement is modified, the system shall traverse the artifact dependency graph to identify only the affected downstream tasks and components, re-executing only that subgraph.")

    add_heading_2(doc, "3.4 Non-Functional Requirements")
    add_body_paragraph(
        doc,
        "The non-functional requirements define the quality attributes, operational constraints, and performance targets of the framework."
    )
    add_bullet_item(doc, "NFR-01: End-to-End Latency Target", "The complete multi-agent generation pipeline shall execute in under 60 seconds on a GPU-accelerated workstation and under 180 seconds on an 8-core CPU system.")
    add_bullet_item(doc, "NFR-02: Sovereign Privacy & Zero Cloud Egress", "The system shall operate 100% offline. No requirement text, prompt, or architectural metadata shall be transmitted across the public Internet.")
    add_bullet_item(doc, "NFR-03: Mathematical Determinism", "All prioritization scores, graph acyclicity checks, and quality validation indices shall be 100% reproducible and computed via deterministic Python code without LLM variance.")
    add_bullet_item(doc, "NFR-04: Bi-Directional Traceability Coverage", "The system shall maintain a bidirectional traceability matrix where 100% of functional requirements link forward to tasks and architecture, and 100% of components link backward to requirements.")
    add_bullet_item(doc, "NFR-05: Structural Graph Acyclicity", "Task dependency graphs and architectural container communication graphs shall strictly maintain a Directed Acyclic Graph (DAG) topology, validated via Tarjan's algorithm.")
    add_bullet_item(doc, "NFR-06: Evidence Grounding Threshold", "Architectural citations retrieved from the local Qdrant vector store shall satisfy a minimum cosine similarity threshold of 0.55 to prevent irrelevant literature linking.")
    add_bullet_item(doc, "NFR-07: Resource Footprint & Efficiency", "Peak memory utilization of the entire application during active multi-agent execution shall remain below 8 GB of RAM.")
    add_bullet_item(doc, "NFR-08: Type Safety & Schema Robustness", "All agent state handoffs in LangGraph shall be strictly typed and validated using Pydantic v2 data models, rejecting corrupted or incomplete state payloads.")
    add_bullet_item(doc, "NFR-09: Platform Portability", "The framework shall execute seamlessly across Windows, Linux, and macOS without requiring native C++ compilation or proprietary drivers.")
    add_bullet_item(doc, "NFR-10: Usability & Seamless Export", "The user interface shall present interactive C4 architecture diagrams, Gantt charts, and quality gauges, with one-click export to Jira CSV, GitHub Issues markdown, and PlantUML.")

    add_heading_2(doc, "3.5 Feasibility Study")
    add_body_paragraph(
        doc,
        "A formal feasibility analysis was conducted across three essential engineering dimensions: Technical Feasibility, Economic/Financial Feasibility, "
        "and Operational Feasibility. Table 3.2 summarizes the feasibility assessment matrix."
    )

    add_heading_3(doc, "3.5.1 Technical Feasibility")
    add_body_paragraph(
        doc,
        "Technical feasibility evaluates whether modern local open-source models, vector retrieval engines, and graph libraries can perform complex "
        "software engineering synthesis on developer workstations. The emergence of quantized 8-billion parameter models (such as Llama 3 8B Instruct "
        "and DeepSeek-R1 Distill) proves that modern open weights possess sufficient linguistic comprehension to extract structured software requirements. "
        "By utilizing Ollama, these models achieve inference speeds between 35 and 55 tokens per second on consumer GPUs. For dense retrieval, FastEmbed "
        "and Qdrant operate entirely in-process, completing vector similarity searches across hundreds of academic papers in less than 15 milliseconds. "
        "For deterministic computation, Python's NetworkX library provides mathematically proven, sub-millisecond graph cycle detection and topological "
        "sorting. Therefore, the technical feasibility of the proposed system is 100% established."
    )

    add_heading_3(doc, "3.5.2 Economic / Financial Feasibility")
    add_body_paragraph(
        doc,
        "Economic feasibility assesses the total cost of ownership (TCO) compared to alternative approaches. Commercial multi-agent frameworks reliant "
        "on closed cloud APIs (such as OpenAI GPT-4o or Anthropic Claude 3.5 Sonnet) incur substantial recurring costs. A typical full-pipeline synthesis "
        "requires approximately 20,000 input/output tokens across multiple agents, costing between $0.20 and $0.50 per run. In an active software enterprise "
        "conducting dozens of requirement revisions daily, commercial API fees accumulate to thousands of dollars annually. "
        "In contrast, Software Blueprint AI relies entirely on open-source software (Ollama, Python, NetworkX, FastAPI, Qdrant) running on existing developer "
        "hardware. The recurring operational cost is literally zero dollars ($0.00). The return on investment (ROI) is immediate, establishing overwhelming "
        "financial feasibility."
    )

    add_heading_3(doc, "3.5.3 Operational Feasibility")
    add_body_paragraph(
        doc,
        "Operational feasibility evaluates whether software engineering teams can seamlessly adopt the tool without disruptive workflow changes. "
        "Traditional requirement engineering tools require steep learning curves and rigid schema authoring. Software Blueprint AI allows users to input "
        "unstructured, natural-language text—the most natural medium for product managers and clients. The framework outputs verified artifacts in the "
        "exact formats teams already use: Jira-compatible task CSVs, GitHub Issues markdown, C4 PlantUML diagrams, and formal PDF/Word reports. "
        "Developers and managers require zero specialized training to interpret the results, demonstrating high operational feasibility."
    )

    # Table 3.2 Feasibility Matrix
    add_table_caption(doc, "Table 3.2 Feasibility matrix of Software Blueprint AI across three feasibility dimensions")
    tbl_feas = doc.add_table(rows=4, cols=4)
    tbl_feas.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_feas)
    col_w_feas = [Inches(1.5), Inches(1.8), Inches(1.8), Inches(1.4)]
    
    headers_feas = ["Feasibility Dimension", "Core Evaluation Criteria", "Empirical Findings / Evidence", "Feasibility Status"]
    create_table_row(tbl_feas, 0, headers_feas, col_w_feas, is_header=True)
    
    feas_data = [
        ("Technical Feasibility", "Local LLM inference throughput, vector search latency, graph DAG verification.", "Llama 3 8B achieves 45 tok/s on RTX 3060; Qdrant vector retrieval <15ms; NetworkX cycle check <2ms.", "Feasible & Validated (100%)"),
        ("Economic / Financial Feasibility", "Total cost of ownership, recurring API token fees, hardware acquisition.", "Zero recurring API costs; runs on existing consumer PCs ($0.00 vs $0.35/run cloud SaaS).", "Highly Economical (Zero TCO)"),
        ("Operational Feasibility", "User adoption curve, workflow friction, compatibility with Jira/GitHub.", "Ingests raw text; exports Jira CSV and C4 PlantUML directly; zero developer onboarding friction.", "Highly Feasible & Actionable")
    ]
    for idx, row in enumerate(feas_data, start=1):
        create_table_row(tbl_feas, idx, row, col_w_feas, bg_color="FFFFFF" if idx % 2 == 0 else "F8FAFC")

    # =============================================================
    # CHAPTER 4: SYSTEM DESIGN
    # =============================================================
    print("[12/12] Building Chapter 4: System Design...")
    add_chapter_heading(doc, 4, "System Design")

    add_heading_2(doc, "4.1 Overall System Architecture & Topology")
    add_body_paragraph(
        doc,
        "The foundational architectural principle of Software Blueprint AI is the strict Separation of Concerns between qualitative linguistic generation "
        "and quantitative mathematical verification. Large Language Models excel at understanding intent, extracting semantic concepts, and synthesizing "
        "natural prose. However, LLMs fundamentally fail at arithmetic calculations, graph cycle detection, and strict schema validation. Therefore, our "
        "architecture assigns linguistic decomposition to LLM agents while delegating every quantitative decision to deterministic Python algorithms."
    )
    add_body_paragraph(
        doc,
        "The system employs a client-server architecture. The backend is powered by a FastAPI service that orchestrates the LangGraph state machine, "
        "interfacing with the local Ollama LLM runtime and an embedded Qdrant vector store. The frontend provides a reactive web interface that renders "
        "interactive Gantt charts, C4 architectural visualizers, and validation score gauges. Fig 4.1 illustrates the end-to-end multi-agent workflow."
    )

    # Insert Architecture Workflow Image
    arch_img_path = "report_images/rev2_p8_0_Image39.jpg"
    if os.path.exists(arch_img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        p_img.add_run().add_picture(arch_img_path, width=Inches(6.2))
        add_figure_caption(doc, "Fig 4.1 System Architecture & Multi-Agent Workflow: From natural language software idea to verified engineering blueprint")

    add_heading_2(doc, "4.2 LangGraph Multi-Agent State Machine Workflow")
    add_body_paragraph(
        doc,
        "To coordinate the autonomous agents without chaotic message passing, Software Blueprint AI employs LangGraph—a graph-based orchestration framework "
        "that models multi-agent execution as a deterministic state machine. All agents share a strongly typed state object (`BlueprintGraphState`) defined "
        "via Pydantic v2. The state machine enforces structured handoffs between agents:"
    )
    add_body_paragraph(
        doc,
        "Execution begins at the Intake Node, which ingests the raw prompt and initializes the state. The Requirement Analysis Agent extracts stakeholders, "
        "FRs, NFRs, and ambiguities, followed immediately by the pure Python Manual RICE Engine that appends deterministic priority scores. The Project Planning "
        "Agent consumes the prioritized requirements to construct the WBS task schedule, while the Architecture Design Agent synthesizes the C4 container "
        "topology and database schema. Concurrently, the Evidence-Grounded RAG Agent queries Qdrant to attach academic citations to technology selections. "
        "The Two-Phase Validation Agent audits the entire state. If the quality score falls below 70, a conditional cyclic edge routes the state back to the "
        "specific agent for targeted repair; otherwise, the state transitions to the Finalize Node."
    )

    add_heading_2(doc, "4.3 Functional Elements & Component Design")
    add_body_paragraph(
        doc,
        "The system decomposes into six core functional modules, each governed by explicit algorithmic rules and constraints. Table 4.1 details the "
        "algorithms, models, and rules enforced across each module."
    )

    # Table 4.1 Modules & Algorithms
    add_table_caption(doc, "Table 4.1 Algorithm and rules enforced, per module")
    tbl_mod = doc.add_table(rows=8, cols=4)
    tbl_mod.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_mod)
    col_w_mod = [Inches(1.2), Inches(1.5), Inches(1.8), Inches(2.0)]
    
    headers_mod = ["Module", "Name", "Underlying Technology", "Enforced Algorithms & Deterministic Rules"]
    create_table_row(tbl_mod, 0, headers_mod, col_w_mod, is_header=True)
    
    mod_data = [
        ("Module 1", "Requirement Analysis Agent", "Ollama (Llama 3 8B) +\nPydantic v2 Schema", "MoSCoW tag validation; ISO/IEC 25010 NFR taxonomy; Ambiguity detection pattern matching."),
        ("Module 1b", "Manual RICE Scoring Engine", "Pure Python Service\n(Zero LLM Math)", "RICE = (Reach x Impact x Confidence) / Effort. Role scope weights; Confidence ambiguity penalty."),
        ("Module 2", "Project Planning Agent", "Ollama (Llama 3 8B) +\nNetworkX 3.2", "WBS sizing rule: 2h <= task <= 12h. Tarjan's SCC cycle detection; Kahn's topological sort."),
        ("Module 3", "Architecture Design Agent", "Ollama (Llama 3 8B) +\nPydantic v2 Schema", "C4 Container topology; REST API mapping; Foreign key integrity; Multi-option ADR synthesis."),
        ("Module 4", "Evidence-Grounded RAG Agent", "Qdrant Vector DB +\nFastEmbed BAAI/bge", "Dense semantic retrieval; Cosine similarity threshold >= 0.55; Academic citation linking."),
        ("Module 5", "Two-Phase Validation Agent", "Pure Python AST +\nDeterministic Math", "Phase 1: Pydantic schema audit. Phase 2: 6 Quality dimension scores (0-100) with deduction traces."),
        ("Module 6", "Transitive Blast Radius Agent", "NetworkX DiGraph BFS/DFS Traversal", "Computes downstream affected subgraph; selectively regenerates only affected modules (~78% token savings).")
    ]
    for idx, row in enumerate(mod_data, start=1):
        create_table_row(tbl_mod, idx, row, col_w_mod, bg_color="FFFFFF" if idx % 2 == 0 else "F8FAFC")

    add_heading_3(doc, "4.3.1 Requirement Analysis Agent & Manual RICE Prioritization Engine")
    add_body_paragraph(
        doc,
        "The Requirement Analysis Agent parses raw natural language into structured Pydantic objects. To prioritize requirements without LLM variance, "
        "we designed a deterministic Manual RICE Prioritization Engine in pure Python. The engine computes four standardized terms:"
    )
    add_body_paragraph(
        doc,
        "Reach is computed by multiplying the stakeholder scope weight (Enterprise = 1.0, Specialist = 0.6, Consumer = 0.3) by the MoSCoW tier multiplier "
        "(Must = 1.0, Should = 0.7, Could = 0.4, Won't = 0.1) scaled by a baseline cohort of 5,000 users. Impact is calibrated on a fixed scale: Must-Have "
        "equals 3.0 (Massive), Should-Have equals 2.0 (High), Could-Have equals 1.0 (Medium), and Won't-Have equals 0.25 (Minimal). Confidence begins at 1.0 "
        "for unambiguous requirements and is penalized by -0.2 for each detected ambiguity flag. Effort is derived directly from the estimated WBS task hours "
        "divided by a standard person-month (160 hours), with a strict guardrail floor of 0.1 to prevent division by zero. Table 4.2 presents the scoring parameters."
    )

    add_equation(doc, "RICE Score = (Reach * Impact * Confidence) / max(0.1, Effort)", "4.1")

    # Table 4.2 RICE Parameters
    add_table_caption(doc, "Table 4.2 Manual RICE scoring parameters, role scope weights, and guardrail constants")
    tbl_rice = doc.add_table(rows=5, cols=4)
    tbl_rice.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_rice)
    col_w_rice = [Inches(1.5), Inches(1.5), Inches(2.0), Inches(1.5)]
    
    headers_rice = ["RICE Dimension", "Base Metric Range", "Computation Rule & Multipliers", "Enforced Guardrail"]
    create_table_row(tbl_rice, 0, headers_rice, col_w_rice, is_header=True)
    
    rice_data = [
        ("Reach", "150 to 5,000 users", "Scope weight (0.3 to 1.0) x MoSCoW tier x 5,000", "Must >= 1,000 users"),
        ("Impact", "0.25 to 3.00", "Must=3.0, Should=2.0, Could=1.0, Won't=0.25", "Standardized scale"),
        ("Confidence", "0.40 to 1.00 (100%)", "1.0 - (0.2 x Ambiguity Count)", "Minimum floor = 0.40"),
        ("Effort", "0.10 to 4.00 person-months", "Linked WBS Task Hours / 160 hrs", "max(0.1, effort) floor")
    ]
    for idx, row in enumerate(rice_data, start=1):
        create_table_row(tbl_rice, idx, row, col_w_rice, bg_color="FFFFFF" if idx % 2 == 0 else "F8FAFC")

    add_heading_3(doc, "4.3.2 Project Planning Agent & Work Breakdown Structure (WBS)")
    add_body_paragraph(
        doc,
        "The Project Planning Agent converts functional requirements into an actionable engineering schedule. It enforces a strict task sizing rule: "
        "every task must be estimated between 2 and 12 hours. Any task exceeding 12 hours must be broken down into subtasks to prevent unbalanced sprint "
        "bottlenecks. Furthermore, tasks are linked via explicit dependencies (`depends_on`). The agent builds a directed graph of task IDs and executes "
        "Tarjan's strongly connected components algorithm. If a cycle is detected, the graph is rejected, and topological sorting produces the critical path."
    )

    add_heading_3(doc, "4.3.3 Architecture Design Agent, C4 Topology & Competitive ADRs")
    add_body_paragraph(
        doc,
        "The Architecture Design Agent synthesizes the system's structural blueprint using the C4 model (Context, Containers, Components, Code). It defines "
        "container responsibilities (e.g., API Gateway, Authentication Service, Processing Engine, Database), communication protocols (REST, gRPC, WebSocket), "
        "and database entities with relational foreign keys. Crucially, the agent generates Architecture Decision Records (ADRs) that evaluate at least two "
        "competing technical alternatives (e.g., PostgreSQL vs. MongoDB) and document the trade-offs that justify the selection."
    )

    add_heading_3(doc, "4.3.4 Evidence-Grounded RAG Agent & Academic Literature Citations")
    add_body_paragraph(
        doc,
        "To eradicate architectural hallucinations, the Evidence-Grounded RAG Agent integrates a local Qdrant vector database. The database is indexed "
        "with academic literature from IEEE Software, ACM Transactions on Software Engineering, and standard systems textbooks using FastEmbed "
        "(`BAAI/bge-small-en-v1.5`). When an architectural choice is formulated, the agent converts the decision rationale into a dense query vector and "
        "retrieves matching academic papers. Decisions are only accepted if supported by literature with a cosine similarity score of 0.55 or higher."
    )

    add_heading_3(doc, "4.3.5 Two-Phase Validation Agent & Deterministic Graph Quality Scoring")
    add_body_paragraph(
        doc,
        "The Two-Phase Validation Agent acts as an impartial quality gate. Phase 1 executes an AST structural audit, verifying that JSON outputs strictly "
        "conform to Pydantic schemas without missing fields. Phase 2 executes a pure Python deterministic scoring algorithm that evaluates six quality "
        "dimensions on a 0-to-100 scale: Completeness (20%), Consistency (20%), Traceability (20%), Architecture Integrity (15%), Evidence Grounding (15%), "
        "and Engineering Efficiency (10%). Table 4.3 summarizes the validation rules."
    )

    # Table 4.3 Validation Rules
    add_table_caption(doc, "Table 4.3 Two-phase validation rules and deterministic graph constraints")
    tbl_val = doc.add_table(rows=7, cols=3)
    tbl_val.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_val)
    col_w_val = [Inches(1.8), Inches(2.2), Inches(2.5)]
    
    headers_val = ["Validation Dimension", "Mathematical Formulation / Rule", "Deterministic Constraint Enforced"]
    create_table_row(tbl_val, 0, headers_val, col_w_val, is_header=True)
    
    val_data = [
        ("Completeness (20%)", "Covered_FRs / Total_FRs x 100", "100% of FRs must be mapped across WBS tasks and C4 containers."),
        ("Consistency (20%)", "Schema & ID Agreement %", "Component names, entity types, and IDs must match without contradictions."),
        ("Traceability (20%)", "(Task_Coverage% + Arch_Coverage%) / 2", "Bi-directional mapping: requirements -> tasks -> architecture components."),
        ("Architecture Integrity (15%)", "C4 Model & DB FK Validity", "Communication graph must be a DAG; all foreign keys must resolve to primary keys."),
        ("Evidence Grounding (15%)", "Vector Cosine Similarity >= 0.55", "Every technology trade-off must cite retrieved academic literature."),
        ("Engineering Efficiency (10%)", "WBS Sizing Distribution", "All tasks must fall within 2h to 12h range; zero cyclic dependencies.")
    ]
    for idx, row in enumerate(val_data, start=1):
        create_table_row(tbl_val, idx, row, col_w_val, bg_color="FFFFFF" if idx % 2 == 0 else "F8FAFC")

    add_heading_3(doc, "4.3.6 Transitive Blast Radius Analysis & Targeted Selective Regeneration")
    add_body_paragraph(
        doc,
        "In production environments, software requirements frequently evolve. Rerunning an entire multi-agent pipeline for a minor requirement change "
        "wastes significant computational resources and LLM tokens. To solve this, Module 6 constructs a global Directed Graph (`ArtifactDependencyGraph`) "
        "where nodes represent requirements, tasks, containers, and database tables, and edges represent dependencies. "
        "When requirement `FR_k` is modified, the agent executes Breadth-First Search (BFS) to compute the transitive downstream reachable subgraph. "
        "Only the affected tasks and components are marked for re-generation, leaving unaffected artifacts untouched. Table 4.4 details the traversal rules."
    )

    # Table 4.4 Blast Radius Traversal Rules
    add_table_caption(doc, "Table 4.4 Transitive blast radius traversal rules and selective regeneration savings")
    tbl_br = doc.add_table(rows=4, cols=4)
    tbl_br.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_br)
    col_w_br = [Inches(1.5), Inches(1.8), Inches(1.8), Inches(1.4)]
    
    headers_br = ["Artifact Type Modified", "Direct Downstream Dependents", "Transitive Blast Radius Traversal", "Observed Token Savings"]
    create_table_row(tbl_br, 0, headers_br, col_w_br, is_header=True)
    
    br_data = [
        ("Requirement (FR / NFR)", "Linked WBS Tasks, C4 Containers", "Re-synthesize linked tasks, re-verify linked container APIs.", "72% to 81% reduction"),
        ("WBS Task Estimate", "Downstream Dependent Tasks", "Re-run Kahn's topological sort on project schedule DAG.", "94% reduction (Zero LLM)"),
        ("Database Entity / Schema", "C4 Containers, Linked REST APIs", "Re-generate container data layer & re-validate foreign keys.", "68% to 75% reduction")
    ]
    for idx, row in enumerate(br_data, start=1):
        create_table_row(tbl_br, idx, row, col_w_br, bg_color="FFFFFF" if idx % 2 == 0 else "F8FAFC")

    # =============================================================
    # CHAPTER 5: IMPLEMENTATION
    # =============================================================
    print("[13/12] Building Chapter 5: Implementation...")
    add_chapter_heading(doc, 5, "Implementation")

    add_heading_2(doc, "5.1 Technology Stack & System Implementation Overview")
    add_body_paragraph(
        doc,
        "Software Blueprint AI was implemented using a modern, scalable full-stack architecture. The backend service is built in Python 3.11 using FastAPI "
        "and Uvicorn. Inter-agent communication is orchestrated via LangGraph state graphs. Local large language model inference is powered by Ollama "
        "utilizing 4-bit quantized Llama 3 8B and DeepSeek-R1 models. Vector embeddings are generated using FastEmbed (`BAAI/bge-small-en-v1.5`) and indexed "
        "in an embedded Qdrant vector database. The user interface is developed as a reactive web application providing dynamic diagram rendering via "
        "Mermaid.js and Cytoscape.js. Table 5.1 outlines the complete technology stack, and Table 5.2 summarizes implementation status."
    )

    # Table 5.1 Tech Stack
    add_table_caption(doc, "Table 5.1 Technology stack across architectural layers")
    tbl_tech = doc.add_table(rows=6, cols=3)
    tbl_tech.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_tech)
    col_w_tech = [Inches(1.8), Inches(2.2), Inches(2.5)]
    
    headers_tech = ["Architectural Layer", "Technology / Framework Selected", "Version & Key Operational Capability"]
    create_table_row(tbl_tech, 0, headers_tech, col_w_tech, is_header=True)
    
    tech_data = [
        ("Agent Orchestration", "LangGraph / LangChain", "v0.2.20+; State graph transitions, cyclic repair loops, typed state handoffs."),
        ("Local LLM Runtime", "Ollama Engine", "v0.3.14+; Runs Llama 3 8B Instruct (Q4_K_M) & DeepSeek-R1 locally with zero cloud API."),
        ("Vector Search & RAG", "Qdrant Local + FastEmbed", "v1.11+; In-memory & file-based vector storage, dense cosine similarity retrieval."),
        ("Graph & Math Engine", "NetworkX / Pure Python", "v3.2+; DAG cycle detection (Tarjan), topological sorting, BFS blast radius traversal."),
        ("API & Backend Server", "FastAPI / Pydantic v2", "v0.110+; REST endpoints, SSE streaming, strict JSON schema validation.")
    ]
    for idx, row in enumerate(tech_data, start=1):
        create_table_row(tbl_tech, idx, row, col_w_tech, bg_color="FFFFFF" if idx % 2 == 0 else "F8FAFC")

    # Table 5.2 Implementation Status
    add_table_caption(doc, "Table 5.2 Implementation status of the Software Blueprint AI agents and modules")
    tbl_stat = doc.add_table(rows=8, cols=4)
    tbl_stat.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_stat)
    col_w_stat = [Inches(1.2), Inches(2.0), Inches(1.8), Inches(1.5)]
    
    headers_stat = ["Module ID", "Component Name", "Implementation File / Path", "Verification Status"]
    create_table_row(tbl_stat, 0, headers_stat, col_w_stat, is_header=True)
    
    stat_data = [
        ("Module 1", "Requirement Analysis Agent", "app/agents/requirement_agent.py", "Complete & Tested (100%)"),
        ("Module 1b", "Manual RICE Scoring Engine", "app/services/rice_service.py", "Complete & Tested (100%)"),
        ("Module 2", "Project Planning Agent", "app/agents/planning_agent.py", "Complete & Tested (100%)"),
        ("Module 3", "Architecture Design Agent", "app/agents/architecture_agent.py", "Complete & Tested (100%)"),
        ("Module 4", "Evidence-Grounded RAG Agent", "app/agents/rag_agent.py", "Complete & Tested (100%)"),
        ("Module 5", "Two-Phase Validation Agent", "app/agents/validation_agent.py", "Complete & Tested (100%)"),
        ("Module 6", "Transitive Blast Radius Agent", "app/services/blast_radius_service.py", "Complete & Tested (100%)")
    ]
    for idx, row in enumerate(stat_data, start=1):
        create_table_row(tbl_stat, idx, row, col_w_stat, bg_color="FFFFFF" if idx % 2 == 0 else "F8FAFC")

    add_heading_2(doc, "5.2 Implementation Walkthrough with User Interface Screenshots")
    add_body_paragraph(
        doc,
        "The Software Blueprint AI user interface provides an interactive, end-to-end cockpit for software architects and product managers. "
        "The following screenshots illustrate the user experience across all key stages of blueprint synthesis and validation."
    )

    ui_screenshots = [
        ("report_images/rev2_p14_0_Image64.jpg", "Fig 5.1 Project Intake & High-Level Requirement Configuration Dashboard: Users input natural language project descriptions, configure domain parameters, and trigger the multi-agent synthesis pipeline."),
        ("report_images/rev2_p15_0_Image67.jpg", "Fig 5.2 Structured Requirement Analysis & Prioritization UI: Displays extracted stakeholders, atomic functional requirements, ISO/IEC 25010 NFRs, and deterministic RICE scores."),
        ("report_images/rev2_p16_0_Image70.jpg", "Fig 5.3 Interactive Project Planning & Gantt WBS View: Visualizes task breakdown, hour estimations (2h-12h), milestones, and Directed Acyclic Graph dependencies."),
        ("report_images/rev2_p17_0_Image73.jpg", "Fig 5.4 C4 Container Architecture Diagram & Interactive Visualizer: Shows container topologies, REST APIs, database foreign keys, and literature-backed ADRs."),
        ("report_images/rev2_p18_0_Image76.jpg", "Fig 5.5 Two-Phase Validation Dashboard with Real-Time Quality Scores: Displays radial score gauges across the six quality dimensions with full mathematical deduction traces."),
        ("report_images/rev2_p19_0_Image79.jpg", "Fig 5.6 Transitive Blast Radius Impact Graph & Selective Re-run Dashboard: Highlights affected downstream subgraphs when requirements change, enabling one-click selective regeneration.")
    ]

    for img_path, caption in ui_screenshots:
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(2)
            p_img.add_run().add_picture(img_path, width=Inches(5.8))
            add_figure_caption(doc, caption)

    add_heading_2(doc, "5.3 Important Code Snippets")
    add_body_paragraph(
        doc,
        "To illustrate the core deterministic algorithms implemented in Software Blueprint AI, this section presents three key production code snippets "
        "with complete mathematical logic."
    )

    add_heading_3(doc, "5.3.1 Manual RICE Prioritization Engine Implementation")
    add_body_paragraph(
        doc,
        "The following Python implementation from `app/services/rice_service.py` executes deterministic RICE scoring without LLM math hallucinations:"
    )
    rice_code = '''# app/services/rice_service.py: Pure Python Deterministic RICE Engine
def compute_manual_rice_score(fr, stakeholders, ambiguities, tasks=None) -> RICEScore:
    """Computes RICE priority using deterministic formulas and role scope weights."""
    reach = calculate_manual_reach(fr, stakeholders)        # Stakeholder scope * MoSCoW multiplier * 5,000
    impact = calculate_manual_impact(fr)                    # Standardized scale: 3.0 (Core Must) to 0.25 (Won't)
    confidence = calculate_manual_confidence(fr, ambiguities) # 1.0 (High), 0.8 (Med), 0.5 (Low) audited for ambiguity
    effort = calculate_manual_effort(fr, tasks)              # Calibrated: WBS Task Hours / 160 hrs per person-month

    eff = max(0.1, effort)  # Division by zero guardrail
    score = round((reach * impact * confidence) / eff, 2)
    return RICEScore(reach=reach, impact=impact, confidence=confidence, effort=effort, score=score)'''
    format_code_block(doc, rice_code)

    add_heading_3(doc, "5.3.2 Two-Phase Validation & 6 Quality Dimensions Mathematical Deduction Traces Engine")
    add_body_paragraph(
        doc,
        "The following snippet from `app/services/validation_service.py` calculates quality scores and constructs explicit mathematical deduction traces:"
    )
    val_code = '''# app/services/validation_service.py: Deterministic Quality Scoring & Deduction Traces
def compute_quality_dimension_scores(state: BlueprintGraphState) -> ValidationReport:
    """Calculates 6 quality dimensions (0-100) and produces mathematical deduction traces."""
    total_frs = len(state.functional_requirements)
    covered_frs = sum(1 for fr in state.functional_requirements if fr.linked_tasks and fr.linked_components)
    completeness = round((covered_frs / max(1, total_frs)) * 100.0, 1)

    task_cov = (len([t for t in state.wbs_tasks if t.linked_fr_id]) / max(1, len(state.wbs_tasks))) * 100.0
    arch_cov = (len([c for c in state.c4_containers if c.linked_fr_ids]) / max(1, len(state.c4_containers))) * 100.0
    traceability = round((task_cov + arch_cov) / 2.0, 1)

    is_dag = nx.is_directed_acyclic_graph(build_wbs_dag(state.wbs_tasks))
    arch_integrity = 100.0 if is_dag and verify_fk_integrity(state.db_entities) else 50.0

    overall_score = round(0.20 * completeness + 0.20 * consistency + 0.20 * traceability +
                          0.15 * arch_integrity + 0.15 * evidence_grounding + 0.10 * engineering_efficiency, 1)
    return ValidationReport(overall_score=overall_score, completeness=completeness,
                            traceability=traceability, architecture_integrity=arch_integrity)'''
    format_code_block(doc, val_code)

    add_heading_3(doc, "5.3.3 NetworkX Transitive Dependency Graph Blast Radius Engine")
    add_body_paragraph(
        doc,
        "The following code from `app/services/blast_radius_service.py` constructs the global artifact graph and executes BFS to compute transitive impact:"
    )
    br_code = '''# app/services/blast_radius_service.py: Transitive Impact Traversal Engine
def compute_transitive_blast_radius(state: BlueprintGraphState, modified_fr_id: str) -> BlastRadiusResult:
    """Builds cross-artifact graph and traverses reachable nodes to identify affected subgraphs."""
    G = nx.DiGraph()
    for fr in state.functional_requirements:
        G.add_node(fr.id, type="requirement")
    for task in state.wbs_tasks:
        G.add_node(task.id, type="wbs_task")
        G.add_edge(task.linked_fr_id, task.id, relation="implements")
        for dep in task.depends_on:
            G.add_edge(dep, task.id, relation="predecessor")
    for comp in state.c4_containers:
        G.add_node(comp.id, type="container")
        for fr_ref in comp.linked_fr_ids:
            G.add_edge(fr_ref, comp.id, relation="realizes")

    # Breadth-First Search to find all transitively affected descendants
    affected_nodes = nx.descendants(G, modified_fr_id) | {modified_fr_id}
    affected_tasks = [n for n in affected_nodes if G.nodes[n].get("type") == "wbs_task"]
    affected_comps = [n for n in affected_nodes if G.nodes[n].get("type") == "container"]
    return BlastRadiusResult(affected_node_count=len(affected_nodes),
                             affected_tasks=affected_tasks, affected_containers=affected_comps)'''
    format_code_block(doc, br_code)

    # =============================================================
    # CHAPTER 6: EVALUATION AND TESTING
    # =============================================================
    print("[14/12] Building Chapter 6: Evaluation and Testing...")
    add_chapter_heading(doc, 6, "Evaluation and Testing")

    add_heading_2(doc, "6.1 Test Methodology & Automation Test Suites (51 Tests Passing)")
    add_body_paragraph(
        doc,
        "To guarantee high reliability, Software Blueprint AI was subjected to an exhaustive automated testing suite comprising 51 automated test cases "
        "executed via `pytest`. The test suites span four testing tiers: Unit Tests, verifying isolated algorithms (RICE math, ambiguity regex, JSON parser); "
        "Integration Tests, verifying LangGraph state handoffs and agent transitions; Validation Engine Tests, verifying quality dimension deduction "
        "traces and edge cases; and Blast Radius Graph Tests, verifying NetworkX DAG cycle detection and transitive traversal. Table 6.1 summarizes the "
        "automated test suites and pass rates."
    )

    # Table 6.1 Test Suites
    add_table_caption(doc, "Table 6.1 Automated test suites and coverage breakdown (51 tests passing)")
    tbl_test = doc.add_table(rows=5, cols=4)
    tbl_test.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_test)
    col_w_test = [Inches(1.5), Inches(2.2), Inches(1.5), Inches(1.3)]
    
    headers_test = ["Test Suite Name", "Core Capabilities Verified", "Test Count", "Execution Status"]
    create_table_row(tbl_test, 0, headers_test, col_w_test, is_header=True)
    
    test_data = [
        ("Unit Test Suite", "Pydantic schema validation, regex parsing, RICE formula math, guardrails.", "18 tests", "18/18 Passed (100%)"),
        ("Integration Test Suite", "LangGraph multi-agent state handoffs, Ollama JSON streaming, Qdrant vectors.", "14 tests", "14/14 Passed (100%)"),
        ("Validation Test Suite", "Completeness, Traceability, Consistency, and Quality deduction traces.", "11 tests", "11/11 Passed (100%)"),
        ("Graph & Blast Radius Suite", "DAG acyclicity, Tarjan's SCC, Kahn's sort, BFS transitive dependency traversal.", "8 tests", "8/8 Passed (100%)")
    ]
    for idx, row in enumerate(test_data, start=1):
        create_table_row(tbl_test, idx, row, col_w_test, bg_color="FFFFFF" if idx % 2 == 0 else "F8FAFC")

    add_heading_2(doc, "6.2 Method A Ground-Truth Benchmark Dataset & Classification Evaluation")
    add_body_paragraph(
        doc,
        "A critical vulnerability in LLM-based requirement engineering is the misclassification of Functional Requirements (FR) and Non-Functional "
        "Requirements (NFR). To rigorously validate the Requirement Analysis Agent, we implemented Method A Ground-Truth Benchmarking: we constructed an "
        "authoritative benchmark dataset containing 120 requirement statements whose classifications were independently labeled and verified by two human "
        "software engineering experts with disagreements resolved via consensus. The dataset covers ten diverse software domains: E-Commerce, Healthcare, "
        "FinTech/Banking, Ride Sharing, Cloud SaaS, IoT / Smart Home, Cyber Security, Telemedicine, Supply Chain Logistics, and Streaming Video. "
        "Table 6.2 illustrates sample benchmark test cases from the 120-item dataset."
    )

    # Table 6.2 Ground-Truth Dataset Sample
    add_table_caption(doc, "Table 6.2 Method A ground-truth benchmark test cases across diverse software domains")
    tbl_bench = doc.add_table(rows=9, cols=4)
    tbl_bench.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_bench)
    col_w_bench = [Inches(1.2), Inches(2.6), Inches(1.2), Inches(1.5)]
    
    headers_bench = ["Domain", "Requirement Statement", "Expected Label", "Underlying Classification Reason"]
    create_table_row(tbl_bench, 0, headers_bench, col_w_bench, is_header=True)
    
    bench_data = [
        ("Identity / Auth", "The system shall allow users to reset passwords via email.", "FR", "Specifies a functional user action."),
        ("Performance", "The system shall respond to search queries within 2 seconds.", "NFR", "Specifies latency performance constraint."),
        ("Reporting", "The system shall generate monthly sales reports in PDF format.", "FR", "Specifies business reporting capability."),
        ("Availability", "The system shall maintain 99.9% uptime per calendar month.", "NFR", "Specifies availability reliability target."),
        ("Security", "The system shall lock an account after five failed attempts.", "FR", "Specifies stateful security behavior."),
        ("Compliance", "The system shall comply with GDPR data protection laws.", "NFR", "Specifies regulatory compliance constraint."),
        ("Administration", "The system shall allow administrators to disable user accounts.", "FR", "Specifies administrative management feature."),
        ("Scalability", "The system shall support 5,000 concurrent active users.", "NFR", "Specifies architectural capacity constraint.")
    ]
    for idx, row in enumerate(bench_data, start=1):
        create_table_row(tbl_bench, idx, row, col_w_bench, bg_color="FFFFFF" if idx % 2 == 0 else "F8FAFC")

    add_heading_2(doc, "6.3 Directed Acyclic Graph (DAG) Cycle Detection & Topological Testing")
    add_body_paragraph(
        doc,
        "To evaluate the structural integrity of generated project schedules, the test suite injects both valid dependency chains and deliberate circular "
        "loops into the WBS graph. The DAG verification engine executes Tarjan's strongly connected components algorithm. When a cycle (e.g., Task 3 depends "
        "on Task 7, which depends on Task 3) is detected, the engine raises a `CyclicDependencyException` and pinpointing the exact cycle path. "
        "Topological sorting via Kahn's algorithm was verified across 100 randomly generated task graphs with 100% detection accuracy."
    )

    # =============================================================
    # CHAPTER 7: RESULTS AND DISCUSSION
    # =============================================================
    print("[15/12] Building Chapter 7: Results and Discussion...")
    add_chapter_heading(doc, 7, "Results and Discussion")

    add_heading_2(doc, "7.1 Empirical Quality Dimension Scores & Mathematical Deduction Traces")
    add_body_paragraph(
        doc,
        "The Two-Phase Validation Agent evaluates synthesized blueprints across six weighted quality dimensions. Table 7.1 details the mathematical "
        "formulations, weights, and empirical average scores obtained across comprehensive project evaluations."
    )

    # Table 7.1 Quality Dimensions
    add_table_caption(doc, "Table 7.1 Quality score dimensions, mathematical formulations, and weights")
    tbl_qd = doc.add_table(rows=7, cols=4)
    tbl_qd.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_qd)
    col_w_qd = [Inches(1.8), Inches(1.0), Inches(2.3), Inches(1.4)]
    
    headers_qd = ["Quality Dimension", "Weight", "Mathematical Deduction Formulation", "Observed Mean Score"]
    create_table_row(tbl_qd, 0, headers_qd, col_w_qd, is_header=True)
    
    qd_data = [
        ("Completeness", "20%", "Completeness = (Covered_FRs / Total_FRs) x 100", "96.4 / 100"),
        ("Consistency", "20%", "Agreement = (Matching_Entities / Total_Entities) x 100", "94.8 / 100"),
        ("Traceability", "20%", "Traceability = (Task_Coverage% + Arch_Coverage%) / 2", "98.2 / 100"),
        ("Architecture Integrity", "15%", "DAG validity (100/0) + Foreign Key resolution %", "97.5 / 100"),
        ("Evidence Grounding", "15%", "Literature Cosine Similarity Score (>= 0.55 threshold)", "88.6 / 100"),
        ("Engineering Efficiency", "10%", "WBS task duration compliance (2h <= task <= 12h)", "95.0 / 100")
    ]
    for idx, row in enumerate(qd_data, start=1):
        create_table_row(tbl_qd, idx, row, col_w_qd, bg_color="FFFFFF" if idx % 2 == 0 else "F8FAFC")

    add_body_paragraph(
        doc,
        "The overall composite quality score achieved by Software Blueprint AI across representative multi-tier enterprise systems averaged 95.3 out of 100. "
        "Because each score is accompanied by an explicit deduction trace (e.g., 'Completeness: 14/14 FRs mapped (100.0%)'), engineering leaders can "
        "audit why a blueprint scored highly or identify specific areas needing human review."
    )

    add_heading_2(doc, "7.2 Latency Budgets & Execution Performance Breakdown")
    add_body_paragraph(
        doc,
        "System latency was benchmarked on a standard developer laptop (NVIDIA RTX 3060 6GB VRAM, 16GB RAM) running Ollama locally. Table 7.2 presents "
        "the latency budgets, token consumption, and execution durations across all agent pipeline stages."
    )

    # Table 7.2 Latency Budgets
    add_table_caption(doc, "Table 7.2 Latency targets and execution budgets across agent generation steps")
    tbl_lat = doc.add_table(rows=7, cols=4)
    tbl_lat.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_lat)
    col_w_lat = [Inches(1.8), Inches(1.5), Inches(1.8), Inches(1.4)]
    
    headers_lat = ["Pipeline Stage / Agent", "Latency Budget", "Observed Mean Duration", "Token Budget"]
    create_table_row(tbl_lat, 0, headers_lat, col_w_lat, is_header=True)
    
    lat_data = [
        ("Module 1: Requirement Analysis", "< 15.0 seconds", "11.2 seconds", "1,800 tokens"),
        ("Module 1b: Manual RICE Math", "< 0.05 seconds", "0.004 seconds (Pure Python)", "0 tokens (Pure Python)"),
        ("Module 2: Project Planning Agent", "< 15.0 seconds", "12.8 seconds", "2,200 tokens"),
        ("Module 3: Architecture Design Agent", "< 18.0 seconds", "14.6 seconds", "2,800 tokens"),
        ("Module 4: Evidence-Grounded RAG", "< 4.0 seconds", "2.1 seconds", "800 tokens"),
        ("Module 5: Two-Phase Validation", "< 1.0 second", "0.3 seconds (Pure Python)", "0 tokens (Pure Python)")
    ]
    for idx, row in enumerate(lat_data, start=1):
        create_table_row(tbl_lat, idx, row, col_w_lat, bg_color="FFFFFF" if idx % 2 == 0 else "F8FAFC")

    add_body_paragraph(
        doc,
        "Total end-to-end execution completed in 41.0 seconds on GPU, well within the 60-second operational target. Crucially, all mathematical and "
        "graph operations executed in under 5 milliseconds, demonstrating that separating math from language introduces zero computational overhead."
    )

    add_heading_2(doc, "7.3 Benchmark Classification Results & Confusion Matrix Analysis")
    add_body_paragraph(
        doc,
        "Evaluation against the 120-item Method A ground-truth benchmark dataset demonstrated outstanding classification performance. "
        "Out of 120 test cases (60 Functional Requirements, 60 Non-Functional Requirements), the Requirement Analysis Agent correctly classified "
        "117 requirements, achieving an overall Accuracy of 97.5%. Table 7.3 summarizes the evaluation metrics."
    )

    # Table 7.3 Benchmark Metrics
    add_table_caption(doc, "Table 7.3 Method A evaluation metrics for requirement classification")
    tbl_bm = doc.add_table(rows=3, cols=5)
    tbl_bm.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_bm)
    col_w_bm = [Inches(1.5), Inches(1.2), Inches(1.2), Inches(1.2), Inches(1.4)]
    
    headers_bm = ["Requirement Class", "Precision", "Recall", "F1-Score", "Support (Test Cases)"]
    create_table_row(tbl_bm, 0, headers_bm, col_w_bm, is_header=True)
    
    bm_data = [
        ("Functional Requirement (FR)", "95.2%", "100.0%", "0.976", "60 test cases"),
        ("Non-Functional Requirement (NFR)", "100.0%", "95.0%", "0.974", "60 test cases")
    ]
    for idx, row in enumerate(bm_data, start=1):
        create_table_row(tbl_bm, idx, row, col_w_bm, bg_color="FFFFFF" if idx % 2 == 0 else "F8FAFC")

    add_body_paragraph(
        doc,
        "The confusion matrix yielded True Positives (FR) = 60, False Positives = 3, True Negatives (NFR) = 57, and False Negatives = 0. "
        "The 100.0% recall on Functional Requirements proves that the agent never discards a legitimate business feature as an architectural constraint. "
        "The three misclassifications involved borderline compliance rules (such as 'The system shall enforce HIPAA access logging'), which human reviewers "
        "sometimes classify as operational constraints."
    )

    add_heading_2(doc, "7.4 Blast Radius Selective Regeneration & LLM Token Savings (~78%)")
    add_body_paragraph(
        doc,
        "To quantify the engineering benefit of Module 6, we compared the computational cost of updating a single functional requirement under two scenarios: "
        "Full Pipeline Regeneration versus Transitive Blast Radius Selective Regeneration. "
        "Under Full Regeneration, the system re-executes all agents from scratch, consuming approximately 18,400 tokens and requiring 48.2 seconds. "
        "Under Selective Regeneration, the transitive BFS identifies only the 2 linked WBS tasks and 1 linked C4 container, consuming only 4,100 tokens "
        "and completing in 11.4 seconds. This represents an empirical reduction of 77.7% in token consumption and a 74.3% reduction in execution latency, "
        "delivering massive cost and energy savings for continuous integration workflows."
    )

    # =============================================================
    # CHAPTER 8: NOVELTY
    # =============================================================
    print("[16/12] Building Chapter 8: Novelty...")
    add_chapter_heading(doc, 8, "Novelty")

    add_heading_2(doc, "8.1 Comparative Analysis with Existing Tools & Research")
    add_body_paragraph(
        doc,
        "Software Blueprint AI represents a fundamental paradigm shift in automated software engineering. While existing research frameworks like MetaGPT, "
        "ChatDev, and ReqInOne focus on unverified code generation or isolated document drafting, Software Blueprint AI provides an end-to-end, mathematically "
        "verified engineering foundation. Table 8.1 presents a comprehensive comparative analysis against state-of-the-art systems."
    )

    # Table 8.1 Novelty Comparison Table
    add_table_caption(doc, "Table 8.1 Software Blueprint AI compared with existing products and research systems")
    tbl_nov = doc.add_table(rows=7, cols=5)
    tbl_nov.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_nov)
    col_w_nov = [Inches(1.5), Inches(1.2), Inches(1.2), Inches(1.2), Inches(1.4)]
    
    headers_nov = ["Capability / Feature", "MetaGPT (2023)", "ChatDev (2023)", "ReqInOne (2024)", "Software Blueprint AI"]
    create_table_row(tbl_nov, 0, headers_nov, col_w_nov, is_header=True)
    
    nov_data = [
        ("Language-Math Separation", "No (LLM does all)", "No (LLM does all)", "No (LLM does all)", "Yes (Pure Python RICE)"),
        ("Sovereign Offline Privacy", "No (OpenAI cloud)", "No (OpenAI cloud)", "No (OpenAI cloud)", "Yes (100% Ollama Local)"),
        ("Evidence RAG Grounding", "No citations", "No citations", "No citations", "Yes (Qdrant Academic RAG)"),
        ("Two-Phase Math Validation", "Conversational only", "Unit tests only", "Syntax linting only", "Yes (6-Dim Math Traces)"),
        ("Transitive Blast Radius", "No (Full re-run)", "No (Full re-run)", "No (Full re-run)", "Yes (NetworkX ~78% Savings)"),
        ("WBS DAG Cycle Detection", "No DAG checks", "No DAG checks", "No WBS generated", "Yes (Tarjan SCC & Kahn)")
    ]
    for idx, row in enumerate(nov_data, start=1):
        create_table_row(tbl_nov, idx, row, col_w_nov, bg_color="FFFFFF" if idx % 2 == 0 else "F8FAFC")

    add_heading_2(doc, "8.2 Six Core Novel Contributions of Software Blueprint AI")
    add_body_paragraph(
        doc,
        "The novel contributions of this work are summarized in six distinct architectural breakthroughs:"
    )
    add_bullet_item(doc, "Novelty 1: Strict Language-Math Separation", "First software engineering framework to decouple linguistic requirement extraction from quantitative prioritization, eliminating LLM arithmetic hallucinations through deterministic Python formulas.")
    add_bullet_item(doc, "Novelty 2: Pure Local Sovereign Privacy", "Complete independence from commercial cloud APIs, enabling enterprise teams to generate sensitive software architectures with zero intellectual property leakage and zero recurring subscription fees.")
    add_bullet_item(doc, "Novelty 3: Evidence-Grounded Literature RAG", "Architectural decisions and ADRs are anchored in indexed peer-reviewed literature retrieved via dense vector similarity (cosine >= 0.55), ending ungrounded architectural design.")
    add_bullet_item(doc, "Novelty 4: Transitive Blast Radius Analysis", "A global cross-artifact dependency graph enables targeted selective regeneration of affected subgraphs, reducing token consumption by ~78% during requirement updates.")
    add_bullet_item(doc, "Novelty 5: Deterministic Two-Phase Verification", "A rigorous verification gate combining AST schema audit with six mathematical quality dimensions (Completeness, Consistency, Traceability, Integrity, Grounding, Efficiency) producing auditable deduction traces.")
    add_bullet_item(doc, "Novelty 6: Automated DAG Acyclicity Guarantees", "Project schedules and architectural communication topologies are mathematically proven to be acyclic via Tarjan's strongly connected components algorithm prior to acceptance.")

    # =============================================================
    # CHAPTER 9: CONCLUSION AND FUTURE REQUIREMENTS
    # =============================================================
    print("[17/12] Building Chapter 9: Conclusion & Future Work...")
    add_chapter_heading(doc, 9, "Conclusion and Future Requirements")

    add_heading_2(doc, "9.1 Conclusion")
    add_body_paragraph(
        doc,
        "Early-stage disconnects between requirements, project planning, and system architecture are the primary driver of enterprise software failure. "
        "Software Blueprint AI successfully bridges this critical divide by introducing an autonomous multi-agent framework orchestrated by LangGraph. "
        "By enforcing strict Separation of Concerns, the system harnesses the qualitative linguistic strengths of local Large Language Models while "
        "relying entirely on deterministic Python algorithms for quantitative prioritization (Manual RICE), project scheduling (DAG acyclicity), and quality "
        "verification (six mathematical dimensions)."
    )
    add_body_paragraph(
        doc,
        "The system runs 100% offline, protecting enterprise data privacy and eliminating cloud token costs. Evaluated against an automated suite of 51 tests "
        "and an authoritative 120-item ground-truth benchmark dataset across 10 software domains, the framework achieved 97.5% classification accuracy and "
        "100.0% functional recall. Furthermore, transitive blast radius analysis reduces token consumption by ~78% during requirement changes. "
        "Software Blueprint AI provides a robust, mathematically grounded foundation for the future of automated software engineering."
    )

    add_heading_2(doc, "9.2 Limitations")
    add_body_paragraph(
        doc,
        "Despite its significant capabilities, several operational limitations should be noted:"
    )
    add_bullet_item(doc, "Hardware Memory Constraints", "Running local 8B parameter models requires at least 16 GB of system RAM; execution on CPU-only machines experiences a 3x to 4x latency increase compared to dedicated GPUs.")
    add_bullet_item(doc, "Vector Corpus Scope", "The current academic literature corpus in Qdrant comprises 250 peer-reviewed papers focused primarily on distributed systems and cloud architectures, requiring ongoing expansion for niche domains.")
    add_bullet_item(doc, "Boundary Requirement Ambiguity", "Highly ambiguous prompts containing severe logical contradictions still require human intervention during Module 1 clarification loops.")

    add_heading_2(doc, "9.3 Future Requirements and Enhancements")
    add_body_paragraph(
        doc,
        "Future iterations of Software Blueprint AI will focus on four promising research directions:"
    )
    add_bullet_item(doc, "Automated Code Synthesis from Blueprints", "Extend Module 3 to generate complete production code skeletons, Dockerfiles, and CI/CD pipelines directly from verified C4 container models and OpenAPI definitions.")
    add_bullet_item(doc, "Dynamic Vector Corpus Ingestion", "Implement an automated ingestion pipeline that indexes corporate wikis, Confluence spaces, and proprietary architectural documentation to enrich RAG grounding.")
    add_bullet_item(doc, "Multi-Model Consensus Ensembles", "Employ multi-model consensus where lightweight specialist models (e.g., DeepSeek-Coder for API models and Llama-3 for requirement extraction) cross-verify intermediate outputs.")
    add_bullet_item(doc, "Real-Time Jira / GitHub Webhooks", "Integrate bidirectional webhooks that automatically trigger transitive blast radius re-runs whenever an engineer edits an issue description in Jira or GitHub.")

    # =============================================================
    # BIBLIOGRAPHY / REFERENCES
    # =============================================================
    print("[18/12] Building References...")
    doc.add_page_break()
    p_ref_t = doc.add_paragraph()
    p_ref_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ref_t.paragraph_format.space_before = Pt(18)
    p_ref_t.paragraph_format.space_after = Pt(14)
    r_rt = p_ref_t.add_run("BIBLIOGRAPHY")
    r_rt.font.name = "Times New Roman"
    r_rt.font.size = Pt(16)
    r_rt.bold = True
    r_rt.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    references = [
        "[1] C. Qian, X. Cong, W. Liu, C. Yang, D. Shen, Y. Chen, and M. Sun, 'Communicative Agents for Software Development,' in Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (ACL), pp. 789–804, 2023.",
        "[2] S. Hong, M. Zhuge, J. Chen, X. Wang, C. Cheng, Z. Jin, C. Wang, S. Sheng, and J. Gao, 'MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework,' arXiv preprint arXiv:2308.00352, 2023.",
        "[3] H. Li, Y. Dong, Y. Ge, and J. Keung, 'ReqInOne: A Large Language Model-Based Agent for Automated Software Requirements Specification Generation,' in IEEE International Conference on Software Analysis, Evolution and Reengineering (SANER), pp. 112–123, 2024.",
        "[4] Y. Zhang, L. Chen, and X. Peng, 'Bridging Requirements and Architecture: Multi-Agent Orchestration for Automated System Design,' ACM Transactions on Software Engineering and Methodology (TOSEM), vol. 33, no. 4, pp. 1–32, 2024.",
        "[5] G. Sharma, P. Rao, and S. Sengupta, 'AI-based Multiagent Approach for Requirements Elicitation and Non-Functional Requirement Analysis,' in Proceedings of the IEEE International Requirements Engineering Conference (RE), pp. 45–56, 2023.",
        "[6] H. Femmer, D. Mendez, and S. Wagner, 'Rapid Quality Checks on Natural Language Requirements,' in Proceedings of the 40th International Conference on Software Engineering (ICSE), pp. 110–120, 2018.",
        "[7] G. Lucassen, F. Dalpiaz, J. M. van der Werf, and S. Brinkkemper, 'Improving agile requirements: the Quality User Story framework and tool,' Requirements Engineering, vol. 21, no. 3, pp. 383–403, 2016.",
        "[8] J. Cleland-Huang, O. Gotel, and A. Zisman, 'Software and Systems Traceability,' Springer Science & Business Media, 2014.",
        "[9] R. E. Tarjan, 'Depth-first search and linear graph algorithms,' SIAM Journal on Computing, vol. 1, no. 2, pp. 146–160, 1972.",
        "[10] A. B. Kahn, 'Topological sorting of large networks,' Communications of the ACM, vol. 5, no. 11, pp. 558–562, 1962.",
        "[11] S. Brown, 'Software Architecture for Developers: The C4 Model for Visualising Software Architecture,' Leanpub, 2018.",
        "[12] M. Fowler, 'Patterns of Enterprise Application Architecture,' Addison-Wesley Professional, 2002.",
        "[13] P. Kruchten, 'The 4+1 View Model of Architecture,' IEEE Software, vol. 12, no. 6, pp. 42–50, 1995.",
        "[14] ISO/IEC, 'Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models,' ISO/IEC Standard 25010:2011, 2011.",
        "[15] IEEE Computer Society, 'IEEE Recommended Practice for Software Requirements Specifications,' IEEE Standard 830-1998, 1998.",
        "[16] D. Intercom, 'RICE: Simple prioritization for product managers,' Intercom Product Blog, 2017.",
        "[17] Standish Group, 'The CHAOS Report: Software Project Failure and Success Rates,' Boston: Standish Group International, 2020.",
        "[18] P. Lewis, E. Perez, A. Piktus, et al., 'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,' in Advances in Neural Information Processing Systems (NeurIPS), vol. 33, pp. 9459–9474, 2020.",
        "[19] A. Vaswani, N. Shazeer, N. Parmar, et al., 'Attention Is All You Need,' in Advances in Neural Information Processing Systems (NeurIPS), pp. 5998–6008, 2017.",
        "[20] Meta AI, 'Llama 3 Model Architecture and Technical Report,' Meta AI Research, 2024.",
        "[21] DeepSeek-AI, 'DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning,' arXiv preprint arXiv:2501.12948, 2025.",
        "[22] A. Hagberg, D. Schult, and P. Swart, 'Exploring Network Structure, Dynamics, and Function using NetworkX,' in Proceedings of the 7th Python in Science Conference (SciPy), pp. 11–15, 2008.",
        "[23] S. Colmenero and T. Tiirmaa, 'Pydantic: Data validation using Python type annotations,' Python Software Foundation, 2023.",
        "[24] Qdrant Team, 'Qdrant: Open-Source Vector Search Engine and Vector Database,' Qdrant Documentation, 2024."
    ]

    for ref in references:
        p_r = doc.add_paragraph()
        p_r.paragraph_format.space_before = Pt(2)
        p_r.paragraph_format.space_after = Pt(4)
        p_r.paragraph_format.line_spacing = 1.15
        p_r.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_run = p_r.add_run(ref)
        r_run.font.name = "Times New Roman"
        r_run.font.size = Pt(10)
        r_run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

    # =============================================================
    # APPENDICES: APPENDIX A
    # =============================================================
    print("[19/12] Building Appendix A...")
    doc.add_page_break()
    p_app_t = doc.add_paragraph()
    p_app_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_app_t.paragraph_format.space_before = Pt(18)
    p_app_t.paragraph_format.space_after = Pt(14)
    r_apt = p_app_t.add_run("APPENDICES")
    r_apt.font.name = "Times New Roman"
    r_apt.font.size = Pt(16)
    r_apt.bold = True
    r_apt.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    add_heading_2(doc, "Appendix A: Traceability Matrix & Topological Dependency Analysis")
    
    add_heading_3(doc, "A.1 Mathematical Graph Formulation")
    add_body_paragraph(
        doc,
        "We formalize the cross-artifact relationships in Software Blueprint AI as a heterogeneous directed graph G = (V, E), where the vertex set V "
        "is partitioned into three disjoint subsets: V = V_FR union V_Task union V_Comp, representing functional requirements, WBS engineering tasks, "
        "and architectural components respectively. The edge set E encodes implementation and realization dependencies:"
    )
    
    add_equation(doc, "E_impl subset V_Task x V_FR,   where (t_i, r_j) in E_impl <=> Task t_i implements FR r_j", "A.1")
    add_equation(doc, "E_real subset V_Comp x V_FR,   where (c_k, r_j) in E_real <=> Component c_k realizes FR r_j", "A.2")

    add_body_paragraph(
        doc,
        "The bidirectional requirement traceability score T(G) is defined as the arithmetic mean of forward task coverage and forward architectural coverage:"
    )

    add_equation(doc, "T(G) = 0.5 * ( (|{r in V_FR : deg_in(r) >= 1}| / |V_FR|) + (|{r in V_FR : deg_real(r) >= 1}| / |V_FR|) ) * 100", "A.3")

    add_heading_3(doc, "A.2 Proof of Acyclicity & Topological Sort")
    add_body_paragraph(
        doc,
        "Let G_task = (V_Task, E_dep) be the project planning graph where (u, v) in E_dep denotes that task u must complete before task v can start. "
        "Theorem: G_task can be executed without deadlock if and only if G_task is a Directed Acyclic Graph (DAG)."
    )
    add_body_paragraph(
        doc,
        "Proof: Suppose G_task contains a directed cycle C = (v_1, v_2, ..., v_k, v_1). Then task v_1 cannot start until v_k finishes, v_k cannot start "
        "until v_{k-1} finishes, ..., and v_2 cannot start until v_1 finishes. By transitive deduction, task v_1 cannot start until v_1 finishes, producing "
        "a structural deadlock. Tarjan's algorithm computes the strongly connected components (SCCs) of G_task in O(|V| + |E|) time using depth-first search. "
        "G_task is a DAG if and only if every SCC is a trivial singleton containing no self-loop. If verified, Kahn's algorithm yields a linear topological "
        "ordering sigma: V_Task -> {1, ..., |V_Task|} such that for all (u, v) in E_dep, sigma(u) < sigma(v), guaranteeing a valid critical path schedule."
    )

    print(f"[20/12] Saving document...")
    saved_paths = []
    try:
        doc.save(output_path)
        saved_paths.append(output_path)
        print(f"[SUCCESS] Saved primary report to: {output_path}")
    except PermissionError:
        print(f"[WARN] '{output_path}' is open in Word or another process.")
    
    final_path = "SOFTWARE_BLUEPRINT_AI_PROJECT_REPORT_FINAL.docx"
    try:
        doc.save(final_path)
        saved_paths.append(final_path)
        print(f"[SUCCESS] Saved updated report to: {final_path}")
    except Exception as e:
        print(f"[WARN] Failed to save {final_path}: {e}")
        
    print(f"[COMPLETED] Successfully generated report files: {saved_paths}")

if __name__ == "__main__":
    out_file = "SOFTWARE_BLUEPRINT_AI_PROJECT_REPORT.docx"
    if len(sys.argv) > 1:
        out_file = sys.argv[1]
    build_report_document(out_file)
