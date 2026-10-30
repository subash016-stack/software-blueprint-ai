"""
generate_final_project_report.py
Generates the comprehensive academic Word document (.docx) for Software Blueprint AI,
formatted in exact accordance with the reference report (Cab Eye).
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

def add_page_number_to_footer(section):
    """Add centered 'Page X' dynamic page number to section footer."""
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run("Page ")
    run.font.name = "Times New Roman"
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
    
    fldSimple = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls("w"))
    p._p.append(fldSimple)

def add_heading_1(doc, text):
    """Add Chapter / Section Level 1 Heading in Times New Roman 14pt Bold."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)
    run.bold = True
    run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    return p

def add_heading_2(doc, text):
    """Add Subsection Level 2 Heading in Times New Roman 12pt Bold."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
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
    p.paragraph_format.space_before = Pt(9)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)
    run.bold = True
    run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    return p

def add_body_paragraph(doc, text, bold_prefix=None, space_after=6, italic_prefix=None):
    """Add a body paragraph in Times New Roman 12pt with 1.15 line spacing."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
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
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    r_title = p.add_run(title + ": ")
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(12)
    r_title.bold = True
    r_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    
    r_desc = p.add_run(desc)
    r_desc.font.name = "Times New Roman"
    r_desc.font.size = Pt(12)
    r_desc.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    return p

def add_caption(doc, text, is_table=False):
    """Add caption text below a figure or table."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(9.5)
    run.italic = True
    run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
    return p

def format_code_block(doc, code_text):
    """Add a styled code block in Courier/Consolas."""
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
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def create_table_row(table, row_idx, data, col_widths, is_header=False, bg_color=None):
    """Helper to populate table row with proper fonts, widths, and paddings."""
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
    print("[1/10] Creating document structure and margins...")
    doc = Document()
    
    # Configure 1-inch margins
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)
        add_page_number_to_footer(sec)

    # -------------------------------------------------------------
    # PAGE 1: TITLE PAGE
    # -------------------------------------------------------------
    print("[2/10] Building Title Page...")
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(10)
    p_inst.paragraph_format.space_after = Pt(2)
    r = p_inst.add_run("PSG COLLEGE OF TECHNOLOGY, COIMBATORE")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_before = Pt(0)
    p_dept.paragraph_format.space_after = Pt(18)
    r = p_dept.add_run("Department of Computer Science and Engineering")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    # College Crest / Logo
    logo_path = "report_images/cabeye_p1_0_Image11.png"
    if os.path.exists(logo_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(18)
        p_img.add_run().add_picture(logo_path, width=Inches(1.3))
    else:
        doc.add_paragraph().paragraph_format.space_after = Pt(40)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(10)
    p_title.paragraph_format.space_after = Pt(14)
    r = p_title.add_run("SOFTWARE BLUEPRINT AI")
    r.font.name = "Times New Roman"
    r.font.size = Pt(22)
    r.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(28)
    r = p_sub.add_run("An AI-Driven Multi-Agent Framework for Intelligent Software Requirement Engineering,\nProject Planning, and Architecture Design")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    # Course / Project Work
    p_course = doc.add_paragraph()
    p_course.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_course.paragraph_format.space_before = Pt(0)
    p_course.paragraph_format.space_after = Pt(20)
    r = p_course.add_run("23Z711 – PROJECT WORK 1")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    # Submitted by
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
        "23Z301  Abdul Faizudeen M",
        "23Z331  Kaleeswar G",
        "23Z364  Sam Jeba Ashlin R",
        "23Z372  Subash L",
        "24Z461  Aakash S"
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
    p_guide_lbl.paragraph_format.space_before = Pt(16)
    p_guide_lbl.paragraph_format.space_after = Pt(2)
    r = p_guide_lbl.add_run("Project Guide")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_guide_val = doc.add_paragraph()
    p_guide_val.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_guide_val.paragraph_format.space_before = Pt(0)
    p_guide_val.paragraph_format.space_after = Pt(6)
    r = p_guide_val.add_run("Ms. C. Viveka")
    r.font.name = "Times New Roman"
    r.font.size = Pt(10.5)
    r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

    p_coguide_lbl = doc.add_paragraph()
    p_coguide_lbl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_coguide_lbl.paragraph_format.space_before = Pt(0)
    p_coguide_lbl.paragraph_format.space_after = Pt(2)
    r = p_coguide_lbl.add_run("Co-Guide")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_coguide_val = doc.add_paragraph()
    p_coguide_val.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_coguide_val.paragraph_format.space_before = Pt(0)
    p_coguide_val.paragraph_format.space_after = Pt(0)
    r = p_coguide_val.add_run("Dr. K. Sathiyapriya")
    r.font.name = "Times New Roman"
    r.font.size = Pt(10.5)
    r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 2: ABSTRACT
    # -------------------------------------------------------------
    print("[3/10] Building Abstract...")
    p_abs_h = doc.add_paragraph()
    p_abs_h.paragraph_format.space_before = Pt(12)
    p_abs_h.paragraph_format.space_after = Pt(8)
    r = p_abs_h.add_run("Abstract")
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

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
        "graph algorithms and Pydantic v2 schemas; and Module 6 (Impact Analysis Agent) calculates transitive blast radiuses via NetworkX Breadth-First "
        "Search to re-synthesize only modified components, saving approximately 78 percent of token compute."
    )

    add_body_paragraph(
        doc,
        "A critical architectural evolution of our system was eliminating arithmetic hallucinations from the prioritization pipeline. Rather than "
        "asking an LLM to guess quantitative numbers for the RICE framework (Reach, Impact, Confidence, Effort), we built a dedicated, pure Python "
        "manual calculation engine. The LLM focuses purely on natural-language elicitation and qualitative MoSCoW tiers, while Python code computes "
        "reach from stakeholder role scopes, impact from core domain value drivers, confidence from ambiguity overlap audits, and effort calibrated "
        "directly from actual WBS task hours (hours divided by 160). Requirements are then objectively sorted and ranked in descending order."
    )

    add_body_paragraph(
        doc,
        "The entire platform runs 100 percent offline on local sovereign AI infrastructure (Ollama with Qwen 2.5:3b, local Qdrant, and local Redis), "
        "guaranteeing complete privacy with zero external API fees. The system is guarded by 51 automated unit and integration tests, all of which pass "
        "in 13.86 seconds. To rigorously prove classification reliability, we implemented Method A Ground-Truth Benchmarking: we evaluated the Requirements "
        "Agent against an authoritative benchmark of 120 human-verified requirements across 10 software domains, achieving 97.5 percent overall accuracy, "
        "95.2 percent functional requirement precision, 100.0 percent recall (F1 = 0.976), and 100.0 percent non-functional requirement precision (F1 = 0.974)."
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 3: TABLE OF CONTENTS
    # -------------------------------------------------------------
    print("[4/10] Building Table of Contents...")
    p_toc_h = doc.add_paragraph()
    p_toc_h.paragraph_format.space_before = Pt(12)
    p_toc_h.paragraph_format.space_after = Pt(8)
    r = p_toc_h.add_run("Table of Contents")
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    toc_items = [
        ("Abstract", "2", 0, False),
        ("1 Introduction", "5", 0, True),
        ("1.1 The current situation of software development in industry", "5", 1, False),
        ("1.2 How is requirement-to-architecture workflow handled today?", "5", 1, False),
        ("1.3 Problem statement", "6", 1, False),
        ("1.4 Objectives", "6", 1, False),
        ("1.5 Scope and organisation of the report", "7", 1, False),
        ("2 Literature Survey", "8", 0, True),
        ("2.1 Survey on Multi-Agent Systems in Software Engineering", "8", 1, False),
        ("2.2 ReqInOne: A Large Language Model-Based Agent for SRS Generation", "8", 1, False),
        ("2.3 Bridging Requirements and Architecture: Multi-Agent Orchestration (MAAD)", "9", 1, False),
        ("2.4 AI-based Multiagent Approach for Requirements Elicitation and Analysis", "9", 1, False),
        ("2.5 Requirement Quality Benchmarking and Traceability in Automated SE", "10", 1, False),
        ("2.6 The research gap", "10", 1, False),
        ("3 Proposed Solution", "12", 0, True),
        ("4 System Architecture", "14", 0, True),
        ("4.1 The client and the server", "15", 1, False),
        ("4.2 Running 100% offline without any paid service", "16", 1, False),
        ("4.3 Implementation status", "16", 1, False),
        ("4.4 Technology stack", "17", 1, False),
        ("5 Functional Elements", "19", 0, True),
        ("5.1 The Requirement Analysis Agent & Manual RICE Prioritization Engine", "20", 1, False),
        ("5.2 Project Planning Agent & Work Breakdown Structure (WBS)", "22", 1, False),
        ("5.3 Architecture Design Agent, C4 Topology & Competitive ADRs", "24", 1, False),
        ("5.4 Evidence-Grounded RAG Agent & Academic Literature Citations", "26", 1, False),
        ("5.5 Two-Phase Validation Agent & Deterministic Graph Quality Scoring", "28", 1, False),
        ("5.6 Transitive Blast Radius Analysis & Targeted Selective Regeneration", "30", 1, False),
        ("5.7 User interface", "32", 1, False),
        ("5.8 Results and evaluation", "38", 1, False),
        ("5.9 How the scores are calculated and tested", "40", 1, False),
        ("5.10 The Ground-Truth Benchmark Dataset & Classification Evaluation (Method A)", "43", 1, False),
        ("6 Novelty", "47", 0, True),
        ("6.1 Novelty", "47", 1, False),
        ("7 Conclusion and Future Work", "49", 0, True),
        ("References", "50", 0, True),
        ("Appendix A Traceability Matrix & Topological Dependency Analysis", "52", 0, True)
    ]

    for title, page_no, level, is_bold in toc_items:
        p_toc = doc.add_paragraph()
        p_toc.paragraph_format.space_before = Pt(1.5)
        p_toc.paragraph_format.space_after = Pt(1.5)
        p_toc.paragraph_format.line_spacing = 1.15
        
        # Indent based on level
        indent_spaces = "      " * level
        title_text = indent_spaces + title
        
        # Calculate dot leader length
        total_len = 65
        dots_count = max(4, total_len - len(title_text) - len(page_no))
        dots_str = " " + ("." * dots_count) + " "
        
        r1 = p_toc.add_run(title_text)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11)
        r1.bold = is_bold
        r1.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A) if is_bold else RGBColor(0x33, 0x41, 0x55)
        
        r2 = p_toc.add_run(dots_str)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(10)
        r2.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
        
        r3 = p_toc.add_run(page_no)
        r3.font.name = "Times New Roman"
        r3.font.size = Pt(11)
        r3.bold = is_bold
        r3.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A) if is_bold else RGBColor(0x33, 0x41, 0x55)

    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 4: LIST OF FIGURES
    # -------------------------------------------------------------
    print("[5/10] Building List of Figures...")
    p_lof_h = doc.add_paragraph()
    p_lof_h.paragraph_format.space_before = Pt(12)
    p_lof_h.paragraph_format.space_after = Pt(8)
    r = p_lof_h.add_run("List of Figures")
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    figures_list = [
        ("Figure 1", "System Architecture & Multi-Agent Workflow: From natural language idea to validated SDLC blueprint."),
        ("Figure 2", "Multi-agent state transition and dependency graph across pipeline phases."),
        ("Figure 3", "Manual RICE Prioritization Engine: Pure Python calculation flow and backlog ranking."),
        ("Figure 4", "Web Application Dashboard: Interactive blueprint synthesis and real-time telemetry."),
        ("Figure 5", "Module 1: Software Requirements Specification (SRS) with MoSCoW and RICE scores."),
        ("Figure 6", "Module 2: Engineering Project Plan, Work Breakdown Structure (WBS), and DAG tasks."),
        ("Figure 7", "Module 3: Technical Architecture Blueprint, C4 container model, and database schemas."),
        ("Figure 8", "Module 3: Architecture Decision Records (ADRs) with competitive justifications."),
        ("Figure 9", "End-to-End Requirement-to-Architecture Traceability Matrix (RTM)."),
        ("Figure 10", "Automated test suite distribution across platform modules (51 tests passing)."),
        ("Figure 11", "Method A Benchmark Evaluation: Confusion matrix and classification accuracy across 10 domains."),
        ("Figure 12", "Targeted Selective Regeneration: Transitive blast radius analysis and token savings (~78%).")
    ]

    for f_id, f_desc in figures_list:
        p_fig = doc.add_paragraph()
        p_fig.paragraph_format.space_before = Pt(2)
        p_fig.paragraph_format.space_after = Pt(2.5)
        p_fig.paragraph_format.line_spacing = 1.15
        
        r1 = p_fig.add_run(f_id + "  ")
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11)
        r1.bold = True
        r1.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        
        r2 = p_fig.add_run(f_desc)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(11)
        r2.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 5: LIST OF TABLES
    # -------------------------------------------------------------
    print("[6/10] Building List of Tables...")
    p_lot_h = doc.add_paragraph()
    p_lot_h.paragraph_format.space_before = Pt(12)
    p_lot_h.paragraph_format.space_after = Pt(8)
    r = p_lot_h.add_run("List of Tables")
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    tables_list = [
        ("Table 1", "The base papers, their strengths and their limitations."),
        ("Table 2", "From each limitation in the literature to how Software Blueprint AI mitigates it."),
        ("Table 3", "Implementation status of the agents and modules across all feature branches."),
        ("Table 4", "Technology stack across architectural layers."),
        ("Table 5", "Algorithm and rules enforced, per module."),
        ("Table 6", "Manual RICE scoring parameters, role scope weights, and guardrail constants."),
        ("Table 7", "Two-phase validation rules and deterministic graph constraints."),
        ("Table 8", "Method A ground-truth benchmark test cases across diverse software domains."),
        ("Table 9", "Transitive blast radius traversal rules and selective regeneration criteria."),
        ("Table 10", "Latency targets and execution budgets across agent generation stages."),
        ("Table 11", "How benchmark and evaluation datasets are constructed and partitioned."),
        ("Table 12", "Quality score dimensions, mathematical formulations, and weightings."),
        ("Table 13", "Evaluation metrics and their formal formulas."),
        ("Table 14", "Baseline policies and tool comparison matrix."),
        ("Table 15", "Automated test suites and coverage breakdown (51 tests passing)."),
        ("Table 16", "Software Blueprint AI compared with existing products and research systems.")
    ]

    for t_id, t_desc in tables_list:
        p_tbl = doc.add_paragraph()
        p_tbl.paragraph_format.space_before = Pt(2)
        p_tbl.paragraph_format.space_after = Pt(2.5)
        p_tbl.paragraph_format.line_spacing = 1.15
        
        r1 = p_tbl.add_run(t_id + "  ")
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11)
        r1.bold = True
        r1.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        
        r2 = p_tbl.add_run(t_desc)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(11)
        r2.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 1: INTRODUCTION
    # -------------------------------------------------------------
    print("[7/10] Building Chapter 1: Introduction...")
    add_heading_1(doc, "1. Introduction")
    
    add_heading_2(doc, "1.1 The current situation of software development in industry")
    add_body_paragraph(
        doc,
        "Software engineering is one of the most intellectually demanding industries in the world, yet its foundational phases are still managed "
        "using outdated, disconnected methods. When an enterprise or startup wants to build a new software platform, the initial process begins with "
        "stakeholder interviews and requirement elicitation. Business analysts write natural-language documents called Product Requirement Documents (PRDs). "
        "Project managers then read these documents and manually create sprint tickets and Gantt charts. Finally, systems architects read the same documents "
        "and draft high-level architecture designs. This multi-step process takes several weeks or months of meetings, discussions, and manual reviews."
    )
    add_body_paragraph(
        doc,
        "The Standish Group CHAOS studies and IEEE software engineering surveys consistently report that over 65 percent of software projects fail, "
        "run drastically over budget, or deliver software that does not meet stakeholder expectations. The primary source of these failures is not "
        "programming syntax errors; rather, it is the fundamental gap that exists between high-level requirements and downstream technical implementation. "
        "When requirements are written in ambiguous human language, critical assumptions remain unstated. When developers start writing code based on "
        "vague specifications, architectural drift occurs, resulting in expensive rewrites, security vulnerabilities, and software that fails in production."
    )

    add_heading_2(doc, "1.2 How is requirement-to-architecture workflow handled today?")
    add_body_paragraph(
        doc,
        "In current industry practice, requirement analysis, project planning, and architecture design are handled in silos by completely separate teams "
        "using disconnected tools. Requirements live in text editors like Google Docs, Microsoft Word, or Confluence. Project tasks live in issue trackers "
        "like Jira, Linear, or Trello. System architectures live in diagramming tools like Lucidchart, Draw.io, or Miro. None of these tools communicate "
        "with each other programmatically."
    )
    add_body_paragraph(
        doc,
        "When an engineer asks a simple question such as 'Why does this database table have this column?' or 'Which business requirement requires this "
        "microservice API?', tracing the answer requires searching through meeting notes and outdated tickets. Worse still, when a client changes a "
        "single requirement during development, teams have no automated way of knowing which tasks must be updated, which database schemas must change, "
        "or which API endpoints are broken. The software engineering lifecycle suffers from a total lack of end-to-end traceability."
    )

    add_heading_2(doc, "1.3 Problem statement")
    add_body_paragraph(
        doc,
        "The problem facing automated software engineering can be divided into three core challenges:"
    )
    add_body_paragraph(
        doc,
        "First, can a natural-language software idea or raw PRD be converted into an unambiguous, structured Software Requirements Specification (SRS) "
        "with formal qualitative prioritization (MoSCoW) and objective quantitative scoring (RICE), without relying on subjective human guessing or LLM "
        "arithmetic hallucinations? When requirements contain hidden ambiguities or missing stakeholder bindings, the system must detect them automatically."
    )
    add_body_paragraph(
        doc,
        "Second, can specialized AI agents collaborate across the entire software development lifecycle to transform requirements into an actionable "
        "Work Breakdown Structure (WBS) and a verifiable C4 architecture model, while guaranteeing mathematically that every requirement links directly "
        "to a task, component, API endpoint, and database table without circular dependency deadlocks?"
    )
    add_body_paragraph(
        doc,
        "Third, when a requirement changes mid-project, can the system calculate the exact transitive blast radius across downstream components and execute "
        "targeted selective regeneration, updating only the affected artifacts while preserving untouched subsystems verbatim, all while running 100 percent "
        "offline to protect enterprise intellectual property?"
    )

    add_heading_2(doc, "1.4 Objectives")
    add_bullet_item(doc, "Automated Requirement Engineering", "Convert natural-language project ideas into structured IEEE 830 compliant SRS specifications containing stakeholders, functional requirements, non-functional quality attributes, constraints, and detected ambiguities.")
    add_bullet_item(doc, "Deterministic Quantitative Prioritization", "Implement a pure Python manual calculation engine for the RICE framework (Reach, Impact, Confidence, Effort) to eliminate LLM arithmetic hallucinations and establish an objective backlog ranking (#1, #2, #3, ...).")
    add_bullet_item(doc, "WBS Planning & Effort Calibration", "Generate modular project plans with estimated task hours, milestone gates, and Directed Acyclic Graph (DAG) dependencies, dynamically calibrating requirement effort using actual WBS task hours.")
    add_bullet_item(doc, "Evidence-Grounded Architecture Design", "Synthesize C4 container/component models, REST API specifications, database schemas, and Architecture Decision Records (ADRs) with competitive justifications backed by academic literature citations from a local Qdrant vector database.")
    add_bullet_item(doc, "Two-Phase Deterministic Validation", "Conduct rigorous validation combining pure Python graph algorithms (NetworkX cycle detection and coverage verification) with semantic LLM evaluation across 6 quality dimensions.")
    add_bullet_item(doc, "Transitive Blast Radius & Selective Regeneration", "Enable architects to modify requirements and automatically isolate downstream impacts via Breadth-First Search, regenerating only affected artifacts and saving ~78% of token compute.")
    add_bullet_item(doc, "100% Offline Sovereign Privacy", "Ensure complete data sovereignty by running entirely on local Ollama models (Qwen 2.5:3b), local Qdrant vector storage, and local Redis caching with zero external network calls or recurring API costs.")

    add_heading_2(doc, "1.5 Scope and organisation of the report")
    add_body_paragraph(
        doc,
        "This project delivers a complete, production-grade web application featuring an interactive React 18 / Vite dashboard, an asynchronous FastAPI "
        "backend, a compiled LangGraph state machine, local vector and graph databases, and comprehensive test suites. This report documents the full "
        "lifecycle of Software Blueprint AI across subsequent chapters: Chapter 2 reviews foundational research papers and highlights the core research gap; "
        "Chapter 3 introduces the proposed multi-agent architecture and design principles; Chapter 4 details system architecture, offline infrastructure, "
        "implementation status, and tech stack justifications; Chapter 5 provides an exhaustive breakdown of functional agents, manual RICE mathematics, "
        "user interface screens, and empirical benchmark evaluations; Chapter 6 presents platform novelties; and Chapter 7 concludes with future directions."
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 2: LITERATURE SURVEY
    # -------------------------------------------------------------
    print("[8/10] Building Chapter 2: Literature Survey...")
    add_heading_1(doc, "2. Literature Survey")
    add_body_paragraph(
        doc,
        "In recent years, the application of Artificial Intelligence and Large Language Models to software engineering has transitioned from simple code "
        "completion tools (such as GitHub Copilot) to autonomous multi-agent software development frameworks. While these systems show great promise, "
        "they suffer from significant architectural limitations when applied to early-stage requirements engineering and system architecture design. "
        "We reviewed foundational base papers to understand current state-of-the-art capabilities, identify where existing frameworks struggle, and design "
        "our multi-agent system to solve those specific gaps."
    )

    add_heading_2(doc, "2.1 Survey on Multi-Agent Systems in Software Engineering (ChatDev, MetaGPT)")
    add_body_paragraph(
        doc,
        "Pioneering multi-agent frameworks like ChatDev (Qian et al. [5]) and MetaGPT (Hong et al. [6]) demonstrated that assigning distinct personas "
        "(Product Manager, Architect, Project Manager, Engineer, QA) to LLMs significantly reduces hallucination compared to single-agent prompting. "
        "MetaGPT introduced Standard Operating Procedures (SOPs) based on software engineering waterfall models, having agents exchange structured documents. "
        "However, both ChatDev and MetaGPT focus primarily on code generation for small command-line utilities or simple games. They treat requirements "
        "as trivial one-line prompts and do not perform formal requirement elicitation, MoSCoW/RICE prioritization, or deterministic graph validation. "
        "Furthermore, when a requirement changes, these systems must regenerate the entire code repository from scratch."
    )

    add_heading_2(doc, "2.2 ReqInOne: A Large Language Model-Based Agent for SRS Generation")
    add_body_paragraph(
        doc,
        "ReqInOne (Zhu et al. [2], IEEE RE 2025) focused specifically on the requirements engineering phase. The authors created an LLM-based agent that "
        "transforms conversational user prompts into formal Software Requirements Specifications (SRS). They evaluated generated specifications using "
        "traditional software metrics including completeness, consistency, traceability, precision, recall, and F1-score. While ReqInOne produces high-quality "
        "text documents, it operates in complete isolation. The generated requirements are never passed downstream to a project planning or architecture "
        "stage, and there is no mechanism to verify whether the requirements can be translated into valid, non-cyclic engineering roadmaps."
    )

    add_heading_2(doc, "2.3 Bridging Requirements and Architecture: Multi-Agent Orchestration (MAAD)")
    add_body_paragraph(
        doc,
        "MAAD (Li et al. [1], arXiv 2026) addressed the semantic chasm between natural-language requirements and software architecture design. The authors "
        "employed multi-agent orchestration combined with external domain knowledge and hierarchical memory to map requirements directly to architecture "
        "diagrams. While MAAD represents a major step forward, its primary limitation is the complete omission of the project planning phase. In actual "
        "software engineering practice, architecture cannot be synthesized in a vacuum without an understanding of development modules, engineering task "
        "hours, and prerequisite dependency sequences. Furthermore, MAAD lacks an automated deterministic validation agent to verify graph acyclicity."
    )

    add_heading_2(doc, "2.4 AI-based Multiagent Approach for Requirements Elicitation and Analysis")
    add_body_paragraph(
        doc,
        "Sami et al. [3] (arXiv 2024) explored how multi-agent collaboration can support user story extraction, stakeholder identification, and requirement "
        "classification. Their findings confirmed that multi-agent debate and refinement yield higher requirement quality than single-prompt models. "
        "However, like ReqInOne, their framework stops at the requirements stage and provides no bi-directional traceability to downstream engineering tasks "
        "or architectural components."
    )

    add_heading_2(doc, "2.5 Requirement Quality Benchmarking and Traceability in Automated SE")
    add_body_paragraph(
        doc,
        "Recent research by Jin et al. [4] (MARE) highlighted that while generative LLMs can produce plausible text, they are notorious for hallucinating "
        "requirements that violate IEEE 830 standards, omitting critical quality attributes (NFRs), and producing untraceable specifications. Established "
        "software engineering literature emphasizes that automated specification generators must be evaluated against ground-truth benchmarks rather than "
        "relying solely on LLM self-evaluation."
    )

    add_heading_2(doc, "2.6 The research gap")
    add_body_paragraph(
        doc,
        "As summarized in Table 1, existing research proves the value of multi-agent collaboration but leaves critical gaps unaddressed. Requirement "
        "analysis, project planning, and architecture design are treated as isolated research topics. No single framework connects all three stages into a "
        "unified, validated pipeline with formal bi-directional traceability, deterministic graph cycle detection, and targeted selective regeneration. "
        "Software Blueprint AI was designed specifically to bridge this gap."
    )

    # TABLE 1: Base Papers
    tbl1 = doc.add_table(rows=6, cols=3)
    tbl1.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl1.autofit = False
    col_w1 = [Inches(1.8), Inches(2.4), Inches(2.3)]
    set_table_borders(tbl1)
    
    t1_headers = ["Base Paper", "What It Contributes", "What It Leaves Open (Our Requirement)"]
    create_table_row(tbl1, 0, t1_headers, col_w1, is_header=True)
    
    t1_data = [
        ("ChatDev & MetaGPT [5, 6]", "Multi-agent persona collaboration using waterfall SOPs for code synthesis.", "Focuses on toy code generation; lacks formal SRS elicitation, planning, and traceability."),
        ("ReqInOne [2]", "Transforms user prompts into formal SRS; evaluates precision and recall.", "Operates in isolation; requirements do not flow into project plans or architectures."),
        ("MAAD [1]", "Connects requirements directly to architecture using external knowledge.", "Skips project planning (WBS); lacks deterministic graph validation and change impact analysis."),
        ("AI-based Elicitation [3]", "Demonstrates multi-agent effectiveness in user story extraction.", "Restricted to requirements stage only; no architectural synthesis or traceability matrix."),
        ("MARE Framework [4]", "Multi-agent collaborative refinement for requirement consistency.", "Lacks end-to-end SDLC blueprinting, offline execution, and quantitative RICE scoring.")
    ]
    for idx, row in enumerate(t1_data, start=1):
        create_table_row(tbl1, idx, row, col_w1, bg_color="FFFFFF" if idx%2==0 else "F8FAFC")
        
    add_caption(doc, "Table 1. The base papers, their strengths and the gaps that became our requirements.")

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 3: PROPOSED SOLUTION
    # -------------------------------------------------------------
    print("[9/10] Building Chapter 3: Proposed Solution...")
    add_heading_1(doc, "3. Proposed Solution")
    add_body_paragraph(
        doc,
        "Software Blueprint AI is our response to the fundamental research gaps identified in Section 2. The core objective of the platform is to allow "
        "a product team or software architect to enter a natural-language software concept and receive a complete, production-grade, mathematically verified "
        "software engineering blueprint in minutes. Rather than listing disjoint features, Table 2 maps each limitation found in the literature directly "
        "to how our system solves it."
    )

    # TABLE 2: Mitigation Matrix
    tbl2 = doc.add_table(rows=7, cols=2)
    tbl2.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl2.autofit = False
    col_w2 = [Inches(2.8), Inches(3.7)]
    set_table_borders(tbl2)
    
    t2_headers = ["Limitation Found in the Literature", "How Software Blueprint AI Mitigates It"]
    create_table_row(tbl2, 0, t2_headers, col_w2, is_header=True)
    
    t2_data = [
        ("Requirements, planning, and architecture handled in silos", "Single, unified LangGraph state machine orchestrates all three stages sequentially over a shared typed state."),
        ("Single LLM models suffer from cognitive overload and hallucinations", "Specialized collaborating agents divide the cognitive workload: Requirement, Planning, Architecture, RAG, and Validation."),
        ("Subjective priority inflation and LLM arithmetic guessing", "Decoupled qualitative MoSCoW elicitation from a deterministic pure Python manual RICE calculation engine."),
        ("Absence of formal traceability across SDLC artifacts", "Multi-tier directed traceability graph (NetworkX) links Stakeholder -> FR -> Module -> Task -> Component -> API -> DB."),
        ("Circular dependency deadlocks in generated task schedules", "Deterministic graph algorithms (Tarjan's cycle detection, topological sorting) enforce strict Directed Acyclic Graph (DAG) acyclicity."),
        ("Requirement changes require complete full-system regeneration", "Transitive blast radius analysis via NetworkX BFS executes Targeted Selective Regeneration, saving ~78% of token compute.")
    ]
    for idx, row in enumerate(t2_data, start=1):
        create_table_row(tbl2, idx, row, col_w2, bg_color="FFFFFF" if idx%2==0 else "F8FAFC")
        
    add_caption(doc, "Table 2. From each limitation in the literature to the way our system mitigates it.")

    # Figure 1: Architecture & Workflow Diagram
    arch_img_path = "report_images/rev2_p8_0_Image39.jpg"
    if os.path.exists(arch_img_path):
        p_img1 = doc.add_paragraph()
        p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img1.paragraph_format.space_before = Pt(8)
        p_img1.paragraph_format.space_after = Pt(2)
        p_img1.add_run().add_picture(arch_img_path, width=Inches(6.0))
        add_caption(doc, "Figure 1. System Architecture & Multi-Agent Workflow: From natural language idea to validated SDLC blueprint.")

    add_body_paragraph(
        doc,
        "Three foundational design principles govern the entire system architecture:",
        bold_prefix="Core Architectural Principles: "
    )
    add_bullet_item(doc, "1. Separation of Concerns (Language vs. Math)", "LLMs excel at qualitative linguistic comprehension and semantic synthesis, but fail at exact arithmetic and combinatorial graph logic. In Software Blueprint AI, LLMs are tasked solely with qualitative elicitation, while all numerical calculations (RICE scoring, effort calibration, quality scores) and graph algorithms (cycle detection, blast radius traversal) are executed by deterministic Python code.")
    add_bullet_item(doc, "2. Deterministic-First Validation", "No architectural artifact is accepted based on generative LLM confidence alone. Before any output is presented to the user, Phase 1 Deterministic Audit verifies schema contracts using Pydantic v2 Rust core and graph properties using NetworkX in O(V + E) linear time. Generative hallucinations are physically prevented from corrupting the blueprint.")
    add_bullet_item(doc, "3. 100% Offline Sovereign Privacy", "Enterprise software concepts represent highly confidential intellectual property. Sending proprietary system designs over public cloud APIs violates corporate privacy policies. Software Blueprint AI is engineered to run completely offline on local hardware using Ollama (Qwen 2.5:3b), local Qdrant vector storage, and local Redis caching, incurring zero API fees.")

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 4: SYSTEM ARCHITECTURE
    # -------------------------------------------------------------
    print("[10/10] Building Chapter 4: System Architecture...")
    add_heading_1(doc, "4. System Architecture")
    add_body_paragraph(
        doc,
        "Software Blueprint AI is organized as a stateful client-server application. The frontend provides a responsive single-page dashboard "
        "for interactive blueprint synthesis and visual graph inspection. The backend consists of an asynchronous FastAPI REST server coordinating a compiled "
        "LangGraph multi-agent state machine. The agents communicate through an immutable typed state schema (BlueprintState) that flows sequentially "
        "through the pipeline."
    )

    add_heading_2(doc, "4.1 The client and the server")
    add_body_paragraph(
        doc,
        "The frontend is built with React 18, Vite, and Tailwind CSS. It communicates with the backend via asynchronous REST API endpoints mounted under "
        "`/api/v1`. To render complex multi-tier requirement-to-architecture relationships, the interface integrates React Flow, allowing users to "
        "interactively drag, zoom, and inspect directed graph nodes linking stakeholders, functional requirements, modules, engineering tasks, C4 components, "
        "and database entities."
    )
    add_body_paragraph(
        doc,
        "The backend is implemented in Python 3.11 using FastAPI running on the high-performance Uvicorn ASGI server. The core agent pipeline is compiled as "
        "a stateful Directed Acyclic Graph using LangGraph (`app/graph.py`). Each agent node is wrapped with an execution timing decorator that logs "
        "sub-millisecond latency metrics into the pipeline metadata. Because all agent outputs adhere strictly to Pydantic v2 schemas (`app/schemas.py`), "
        "every transition across the graph is fully type-checked, preventing corrupt state propagation."
    )

    add_heading_2(doc, "4.2 Running 100% offline without any paid service")
    add_body_paragraph(
        doc,
        "A primary requirement of the project was complete operational independence from paid external cloud services. The application achieves this "
        "through three local sovereign AI layers:"
    )
    add_bullet_item(doc, "Local Generative Inference", "All agent prompting is powered by local Ollama serving the Qwen 2.5:3b instruction-tuned model. Qwen 2.5 was chosen because it achieves state-of-the-art structured JSON formatting accuracy and strong code reasoning while running at ~45 tokens/second on standard workstation hardware.")
    add_bullet_item(doc, "Local Vector Database", "Evidence-grounded architectural retrieval runs on a local Qdrant vector database (`app/rag/qdrant_client.py`). Software engineering literature is indexed using 1024-dimensional embeddings generated locally via `qwen3-embedding:0.6b` (or BGE-M3). If Qdrant's daemon is unavailable, the system automatically falls back to an in-process exact cosine similarity matrix, ensuring 100% offline uptime.")
    add_bullet_item(doc, "Local Semantic Caching", "To accelerate iterative regeneration, `app/cache/redis_client.py` computes a cryptographic SHA-256 hash of normalized prompts and model parameters. Cache hits are served in less than 5 milliseconds from local Redis or an in-memory thread-safe LRU dictionary, saving 60 to 80 percent of token compute.")

    add_heading_2(doc, "4.3 Implementation status")
    add_body_paragraph(
        doc,
        "The application has been developed and validated across multiple feature branches. To ensure verifiable academic integrity, Table 3 details "
        "the implementation and testing status of every agent, service, and algorithm in the codebase."
    )

    # TABLE 3: Implementation Status
    tbl3 = doc.add_table(rows=11, cols=2)
    tbl3.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl3.autofit = False
    col_w3 = [Inches(3.3), Inches(3.2)]
    set_table_borders(tbl3)
    
    t3_headers = ["Agent / Module", "Implementation & Validation Status"]
    create_table_row(tbl3, 0, t3_headers, col_w3, is_header=True)
    
    t3_data = [
        ("Module 1: Requirement Analysis Agent (app/agents/requirement_agent.py)", "Implemented; unit-tested; ISO/IEEE compliant."),
        ("Manual Deterministic RICE Engine (app/services/rice_service.py)", "Implemented in pure Python; fully tested (51/51 tests passing)."),
        ("Method A Ground-Truth Benchmark (app/benchmark/requirement_evaluator.py)", "Implemented; evaluated on 120 verified samples (97.5% accuracy)."),
        ("Module 2: Project Planning Agent (app/agents/planning_agent.py)", "Implemented; WBS task breakdown and DAG dependency scheduling verified."),
        ("WBS Effort Calibration Engine (app/services/rice_service.py)", "Implemented; dynamically calibrates RICE effort using actual task hours."),
        ("Module 3: Architecture Design Agent (app/agents/architecture_agent.py)", "Implemented; C4 model, REST APIs, DB schemas, and ADRs generated."),
        ("Module 4: Evidence-Grounded RAG Agent (app/agents/rag_agent.py)", "Implemented; Qdrant vector search with academic literature citations."),
        ("Module 5: Two-Phase Validation Agent (app/agents/validation_agent.py)", "Implemented; NetworkX DAG cycle detection and 6 quality dimensions."),
        ("Module 6: Impact Analysis & Selective Regeneration (app/services/impact_service.py)", "Implemented; BFS blast radius traversal with ~78% token savings."),
        ("Web Application Frontend (React 18 + Vite + React Flow)", "Implemented; full interactive dashboard with real-time telemetry.")
    ]
    for idx, row in enumerate(t3_data, start=1):
        create_table_row(tbl3, idx, row, col_w3, bg_color="FFFFFF" if idx%2==0 else "F8FAFC")
        
    add_caption(doc, "Table 3. Implementation status of the Software Blueprint AI agents and modules.")

    add_heading_2(doc, "4.4 Technology stack")
    add_body_paragraph(
        doc,
        "Table 4 presents the complete technology stack across all architectural layers of the platform, detailing the exact job of each tool in our "
        "codebase and explaining why it was chosen over competing alternatives."
    )

    # TABLE 4: Technology Stack
    tbl4 = doc.add_table(rows=8, cols=4)
    tbl4.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl4.autofit = False
    col_w4 = [Inches(1.4), Inches(2.1), Inches(1.3), Inches(1.7)]
    set_table_borders(tbl4)
    
    t4_headers = ["Layer / Tool", "Exact Job in Our Codebase", "Evaluated Alternatives", "Why Chosen Over Alternatives"]
    create_table_row(tbl4, 0, t4_headers, col_w4, is_header=True)
    
    t4_data = [
        ("FastAPI 0.110+\n(Python 3.11)", "Serves REST APIs, async routing, mounts static frontend, and auto-generates OpenAPI docs.", "Node.js (Express),\nFlask (WSGI),\nDjango", "Unifies async networking with native Python AI/ML libraries inside a single process, avoiding IPC serialization bottlenecks."),
        ("LangGraph 0.0.30+\n& LangChain", "Orchestrates stateful multi-agent DAG pipeline and manages immutable state transitions.", "AutoGen,\nCrewAI,\nLinear Scripts", "Provides explicit typed state schemas (BlueprintState) and deterministic graph control, preventing runaway agent chatter."),
        ("Pydantic v2\n(Rust Core)", "Validates all LLM JSON outputs, enforces strict regex schemas, and parses config settings.", "Marshmallow,\nStandard Dataclasses", "Rust-based core engine (pydantic-core) executes validation 5x to 50x faster, ensuring zero corrupt payloads enter the pipeline."),
        ("NetworkX 3.2.1+", "Builds multi-tier traceability graph, runs cycle detection (Tarjan's), and BFS blast radius.", "Custom DFS scripts,\nHand-rolled Kahn's", "Battle-tested, mathematically rigorous O(V + E) graph algorithms that guarantee zero cycle detection hallucinations."),
        ("Qdrant Vector DB\n(Local HNSW)", "Indexes software architecture literature embeddings; provides cosine retrieval for RAG.", "Pinecone (Cloud),\nMilvus, ChromaDB", "Single standalone binary, 100% offline privacy, sub-millisecond HNSW search, and seamless in-memory dictionary fallback."),
        ("Ollama Inference\n(Qwen 2.5:3b)", "Local generative LLM execution and embedding generation without cloud dependencies.", "OpenAI API,\nClaude, vLLM", "Guarantees 100% data sovereignty, zero API fees, zero rate limits, and ~45 tokens/sec generation on local workstations."),
        ("React 18 + Vite\n& React Flow", "Single-page dashboard, stateful component rendering, and interactive DAG graph visualization.", "Next.js (SSR),\nAngular, Vue 3", "Vite produces ultra-fast static SPA bundles requiring no Node server runtime; React Flow enables interactive graph exploration.")
    ]
    for idx, row in enumerate(t4_data, start=1):
        create_table_row(tbl4, idx, row, col_w4, bg_color="FFFFFF" if idx%2==0 else "F8FAFC")
        
    add_caption(doc, "Table 4. Technology stack across architectural layers.")

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 5: FUNCTIONAL ELEMENTS
    # -------------------------------------------------------------
    print("[11/10] Building Chapter 5: Functional Elements...")
    add_heading_1(doc, "5. Functional Elements")
    add_body_paragraph(
        doc,
        "This chapter examines the functional components of Software Blueprint AI: their operational responsibilities, used algorithms, mathematical "
        "rules, user interface design, and empirical evaluation results. A foundational architectural principle must be highlighted: aside from the local "
        "Qwen generative model and embedding models, no reasoning or validation component relies on unverified neural guessing. All prioritizing, "
        "scheduling, cycle-checking, and scoring algorithms are built upon deterministic code. Table 5 provides a comprehensive overview of the rules "
        "enforced across all modules."
    )

    # TABLE 5: Algorithms & Rules
    tbl5 = doc.add_table(rows=8, cols=3)
    tbl5.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl5.autofit = False
    col_w5 = [Inches(1.8), Inches(2.4), Inches(2.3)]
    set_table_borders(tbl5)
    
    t5_headers = ["Module", "Technique (What Code Does)", "Key Rules / Constraints Enforced"]
    create_table_row(tbl5, 0, t5_headers, col_w5, is_header=True)
    
    t5_data = [
        ("Module 1: Requirements\n(SRS & MoSCoW)", "Structured Pydantic elicitation + ISO/IEEE 29148 normalization.", "IDs strictly FR-xxx / NFR-xxx; assigns qualitative Must/Should/Could/Won't tiers."),
        ("Manual RICE Prioritization\n(app/services/rice_service.py)", "Pure Python deterministic quantitative scoring and backlog auto-ranking.", "Score = (R x I x C) / E; Reach from stakeholder scopes; Effort clamped >= 0.2; sorted descending."),
        ("Module 2: Project Planning\n(WBS & Scheduling)", "Topological sorting + milestone grouping + WBS task breakdown.", "Tasks strictly T-xxx with hours (2–12h); prerequisites must form strict DAG; no cycles allowed."),
        ("Module 3: Architecture\n(C4 Model & ADRs)", "C4 container synthesis + REST APIs + DB schemas + competitive ADRs.", "Explicit competitive trade-offs across 8 tech tiers; HTTP verbs + JSON schemas defined."),
        ("Module 4: RAG Engine\n(Qdrant Retrieval)", "Hierarchical markdown chunking with breadcrumbs + cosine search.", "Injects formal academic citations ([ARCH-001]); filters literature similarity threshold >= 0.55."),
        ("Module 5: Validation Agent\n(Two-Phase Audit)", "NetworkX DAG cycle detection + Pydantic v2 validation + 6 dimensions.", "Tarjan's algorithm O(V+E); bi-directional traceability verification; 0–100 quality scoring."),
        ("Module 6: Impact Analysis\n(Selective Regeneration)", "NetworkX BFS descendants traversal + subgraph re-synthesis.", "Isolates affected downstream subgraph; preserves untouched components; saves ~78% tokens.")
    ]
    for idx, row in enumerate(t5_data, start=1):
        create_table_row(tbl5, idx, row, col_w5, bg_color="FFFFFF" if idx%2==0 else "F8FAFC")
        
    add_caption(doc, "Table 5. Algorithm and rules enforced, per module.")

    add_heading_2(doc, "5.1 The Requirement Analysis Agent & Manual RICE Prioritization Engine")
    add_body_paragraph(
        doc,
        "Module 1 converts a natural-language software concept into a structured Software Requirements Specification (SRS). It identifies primary and "
        "administrative stakeholders (ST-001, ST-002), formulates functional requirements (FR-001, FR-002, ...), extracts measurable non-functional "
        "quality attributes (NFR-001 across latency, security, scalability), and detects unstated technical ambiguities."
    )
    add_body_paragraph(
        doc,
        "Prioritizing requirements is critical in software engineering. We implemented dual prioritization: qualitative MoSCoW prioritization ('Must', "
        "'Should', 'Could', 'Won't') and quantitative RICE framework prioritization. Initially, our system asked the LLM to output numerical RICE scores in "
        "JSON. However, rigorous testing revealed that LLMs produce arbitrary, non-reproducible numbers and frequently fail basic arithmetic division. "
        "To solve this, we completely removed the RICE block from the LLM prompt and implemented the RICE algorithm manually in pure Python code "
        "(`app/services/rice_service.py`)."
    )

    add_body_paragraph(
        doc,
        "The quantitative RICE formula is defined as:",
        bold_prefix="The Mathematical RICE Formula: "
    )
    add_body_paragraph(
        doc,
        "RICE Score = (Reach x Impact x Confidence) / Effort",
        italic_prefix="Formula: "
    )
    add_body_paragraph(
        doc,
        "Every variable is computed deterministically by our Python code without any LLM hallucination:"
    )
    add_bullet_item(doc, "Reach (R)", "Measures the number of users or transactions affected per month. Computed by evaluating linked stakeholder roles against a baseline monthly cohort (5,000 users/month). End-users/customers receive a scope weight of 1.0 (100%), internal operators/specialists receive 0.35 (35%), and system administrators receive 0.08 (8%). This factor is then multiplied by MoSCoW multipliers (Must = 1.0, Should = 0.75, Could = 0.40, Won't = 0.15): Reach = max(100, round(5000 x Scope_Factor x MoSCoW_Multiplier)).")
    add_bullet_item(doc, "Impact (I)", "Measures contribution to core business value on a standardized scale: 3.0 for Massive, 2.0 for High, 1.0 for Medium, 0.5 for Low, and 0.25 for Minimal. Our Python code scans requirement titles and descriptions for core domain value drivers (such as payment, checkout, authentication, security, order, vital). A 'Must Have' requirement with core drivers receives 3.0; standard Must Have receives 2.0; Should Have receives 1.0; Could Have receives 0.5; and Won't Have receives 0.25.")
    add_bullet_item(doc, "Confidence (C)", "Measures certainty in the specification data on a standardized scale (1.0 = 100% High, 0.8 = 80% Medium, 0.5 = 50% Moonshot). The code starts at 1.0 and audits specification completeness: it applies a -0.30 penalty if the requirement description shares keyword tokens with detected unclarified ambiguities, a -0.10 penalty if stakeholder bindings are missing, and a -0.10 penalty if descriptions are shorter than 40 characters.")
    add_bullet_item(doc, "Effort (E)", "Measures engineering time required in person-months (clamped to >= 0.2 person-months to prevent division by zero). In the initial requirements pass, effort is estimated from functional complexity keywords (encryption, real-time, biometrics = +0.5 PM; multi-stakeholder = +0.2 PM; simple exports = -0.3 PM). When Module 2 generates the project plan, effort is dynamically calibrated against actual Work Breakdown Structure task hours: Effort = max(0.2, round(Sum(Task_Hours) / 160, 2)).")
    add_bullet_item(doc, "Deterministic Backlog Ranking", "The engine automatically sorts all functional requirements descending by RICE score. Ties are broken using MoSCoW priority weights and requirement IDs. The engine assigns sequential 1-based ranks (Rank #1, #2, #3, ...) directly into the requirement model.")

    # TABLE 6: RICE Scoring Constants
    tbl6 = doc.add_table(rows=7, cols=3)
    tbl6.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl6.autofit = False
    col_w6 = [Inches(1.8), Inches(1.8), Inches(2.9)]
    set_table_borders(tbl6)
    
    t6_headers = ["Parameter", "Calculated Value / Range", "Software Engineering Meaning"]
    create_table_row(tbl6, 0, t6_headers, col_w6, is_header=True)
    
    t6_data = [
        ("Base User Cohort", "5,000 users / month", "Standard baseline monthly cohort for reach normalization."),
        ("Stakeholder Scope Factor", "Customer=1.0, Ops=0.35, Admin=0.08", "Reflects the proportion of total user base affected by role."),
        ("MoSCoW Multiplier", "Must=1.0, Should=0.75, Could=0.40, Won't=0.15", "Quantitative scaling reflecting qualitative release criticality."),
        ("Impact Scale", "3.0, 2.0, 1.0, 0.5, 0.25", "Standardized business impact scale evaluating core revenue/auth drivers."),
        ("Confidence Thresholds", "100% (High), 80% (Medium), 50% (Moonshot)", "Audited against unclarified ambiguity overlaps and missing bindings."),
        ("Effort & WBS Calibration", "Effort = Sum(Task Hours) / 160 hrs", "Person-months derived directly from actual engineering task hours.")
    ]
    for idx, row in enumerate(t6_data, start=1):
        create_table_row(tbl6, idx, row, col_w6, bg_color="FFFFFF" if idx%2==0 else "F8FAFC")
        
    add_caption(doc, "Table 6. Manual RICE scoring parameters, role scope weights, and guardrail constants.")

    # Code snippet box for RICE
    rice_code = '''# app/services/rice_service.py: Pure Python Deterministic RICE Engine
def compute_manual_rice_score(fr, stakeholders, ambiguities, tasks=None) -> RICEScore:
    reach = calculate_manual_reach(fr, stakeholders)        # Stakeholder scope * MoSCoW multiplier * 5,000
    impact = calculate_manual_impact(fr)                    # Standardized scale: 3.0 (Core Must) to 0.25 (Won't)
    confidence = calculate_manual_confidence(fr, ambiguities) # 1.0 (High), 0.8 (Med), 0.5 (Low) audited for ambiguity
    effort = calculate_manual_effort(fr, tasks)              # Derived or calibrated: WBS Task Hours / 160 hrs/pm

    eff = max(0.1, effort)  # Division by zero guardrail
    score = round((reach * impact * confidence) / eff, 2)
    return RICEScore(reach=reach, impact=impact, confidence=confidence, effort=effort, score=score)'''
    format_code_block(doc, rice_code)

    add_heading_2(doc, "5.2 Project Planning Agent & Work Breakdown Structure (WBS)")
    add_body_paragraph(
        doc,
        "Module 2 transforms the structured SRS into an actionable engineering project plan. It groups functional requirements into cohesive logical "
        "subsystems (MOD-001, MOD-002) and synthesizes fine-grained engineering tasks (T-001, T-002, ...). Each task specifies realistic development effort "
        "(2.0 to 12.0 hours), explicit requirement ID links (e.g. `['FR-001']`), and prerequisite task dependency IDs (e.g. `['T-001']`). Tasks are "
        "organized into deliverable milestones (M-001, M-002) and a 3-to-4 phase high-level development roadmap."
    )
    add_body_paragraph(
        doc,
        "To prevent dependency deadlocks, the planning agent compiles all prerequisite relationships into a NetworkX directed graph (`nx.DiGraph`). "
        "It executes `nx.is_directed_acyclic_graph(dag)` to mathematically guarantee that no circular dependency loops exist. Furthermore, when the project "
        "plan is finalized, the manual RICE engine dynamically inspects all tasks linked to each requirement ID and recalibrates the requirement's RICE "
        "effort parameter using actual engineering task hours divided by 160, updating the RICE score and backlog rank in pure code."
    )

    add_heading_2(doc, "5.3 Architecture Design Agent, C4 Topology & Competitive ADRs")
    add_body_paragraph(
        doc,
        "Module 3 consumes the SRS and project plan to synthesize the complete technical architecture. It selects an overarching architecture pattern "
        "(Modular Monolith, Event-Driven, or Microservices) based on non-functional scalability and complexity requirements. It outputs C4 model containers "
        "(CONT-001, CONT-002) and components (COMP-001, COMP-002), formal REST API endpoint specifications (API-001 with HTTP verbs, request/response "
        "schemas, and status codes), and relational database schemas (DB-001 with primary/foreign keys, field types, and constraints)."
    )
    add_body_paragraph(
        doc,
        "A critical feature of the Architecture Agent is generating Architecture Decision Records (ADRs) with explicit competitive trade-off justifications "
        "across 8 technology tiers: Backend Framework, Frontend UI, Relational Persistence, Cache & Async Messaging, API Style, Authentication, Vector DB, "
        "and Deployment Infrastructure. For example, instead of merely stating 'FastAPI was chosen', the ADR explicitly documents why FastAPI was chosen "
        "over Node.js Express (keeps API in the same Python process as NetworkX and Qdrant, eliminating IPC serialization overhead) and Flask (provides "
        "native ASGI async concurrency and Pydantic v2 validation)."
    )

    add_heading_2(doc, "5.4 Evidence-Grounded RAG Agent & Academic Literature Citations")
    add_body_paragraph(
        doc,
        "Generic LLMs frequently hallucinate fictional architectural patterns or invent unsupported design recommendations. Module 4 enforces "
        "Evidence-Grounded Retrieval-Augmented Generation (RAG). Software engineering literature—including classic works by Martin Fowler on microservices, "
        "enterprise integration patterns, IEEE standards, and ACM architecture papers—is indexed into a local Qdrant collection named `architecture_patterns`."
    )
    add_body_paragraph(
        doc,
        "We implemented Hierarchical Markdown Chunking with Context Breadcrumbs (`app/rag/chunking.py`). When indexing technical whitepapers, heading "
        "trees (`#`, `##`, `###`) are parsed and hierarchical breadcrumbs (e.g. `[Microservices Patterns > Service Discovery > Health Checks]`) are "
        "prepended to every chunk. When the Architecture Agent designs a subsystem, the RAG agent retrieves verified literature chunks and injects formal "
        "citation tags (`[ARCH-001]`, `[DATA-001]`, `[SEC-001]`) into the blueprint along with cosine similarity confidence scores and trade-off analyses."
    )

    add_heading_2(doc, "5.5 Two-Phase Validation Agent & Deterministic Graph Quality Scoring")
    add_body_paragraph(
        doc,
        "Module 5 acts as an impartial quality gatekeeper. It executes a rigorous two-phase audit to evaluate the integrity of the generated blueprint:"
    )
    add_bullet_item(doc, "Phase 1: Deterministic Audit (Pure Python Code)", "Zero LLM inference is used. Python code inspects Pydantic schemas, verifies ID regex formats, builds the NetworkX traceability graph, executes Tarjan's algorithm to prove DAG acyclicity, and verifies that every requirement links forward to a task and architectural component (no orphan nodes).")
    add_bullet_item(doc, "Phase 2: Semantic LLM Evaluation", "A focused LLM prompt audits qualitative aspects: domain boundary alignment, edge-case coverage, and clarity of technical descriptions.")

    add_body_paragraph(
        doc,
        "The validation agent computes 6 quality dimension scores (scaled from 0 to 100), accompanied by explicit mathematical deduction traces:",
        bold_prefix="The 6 Quality Dimensions: "
    )
    add_bullet_item(doc, "Completeness (Weight 20%)", "Measures the percentage of elicited functional requirements covered across the SRS, project plan, and architecture components: Completeness = (Covered_FRs / Total_FRs) x 100.")
    add_bullet_item(doc, "Consistency (Weight 20%)", "Measures cross-agent schema agreement, verifying that data types, component names, and IDs match across all artifacts without contradictions.")
    add_bullet_item(doc, "Traceability (Weight 20%)", "Evaluates bi-directional coverage: Traceability = ((Task_Coverage_% + Architecture_Coverage_%) / 2). If a requirement has tasks but lacks an architectural component mapping, traceability drops proportionally.")
    add_bullet_item(doc, "Architecture Integrity (Weight 15%)", "Verifies C4 structural validity, acyclicity (DAG check), and database foreign key integrity.")
    add_bullet_item(doc, "Evidence Grounding (Weight 15%)", "Verifies that architectural decisions cite indexed academic literature in Qdrant with cosine similarity >= 0.55.")
    add_bullet_item(doc, "Engineering Efficiency (Weight 10%)", "Evaluates WBS task sizing, ensuring tasks are sized between 2 and 12 hours without unbalanced bottlenecks.")

    add_body_paragraph(
        doc,
        "Overall Quality Score = 0.20·Completeness + 0.20·Consistency + 0.20·Traceability + 0.15·Architecture + 0.15·Grounding + 0.10·Efficiency",
        italic_prefix="Overall Composite Formula: "
    )

    # TABLE 7: Validation Rules
    tbl7 = doc.add_table(rows=7, cols=3)
    tbl7.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl7.autofit = False
    col_w7 = [Inches(1.8), Inches(2.3), Inches(2.4)]
    set_table_borders(tbl7)
    
    t7_headers = ["Audit Dimension", "Deterministic Validation Rule", "Mathematical / Graph Check"]
    create_table_row(tbl7, 0, t7_headers, col_w7, is_header=True)
    
    t7_data = [
        ("DAG Acyclicity", "Task prerequisite dependencies must form a strict DAG.", "nx.is_directed_acyclic_graph() == True; Tarjan's cycle check."),
        ("Traceability Coverage", "Every FR must map to >= 1 WBS task and >= 1 C4 component.", "Set intersection: len(Mapped_FRs) / len(Total_FRs) == 1.0."),
        ("ID Schema Integrity", "IDs must strictly follow regex: ST-xxx, FR-xxx, T-xxx, COMP-xxx.", "Pydantic v2 field validators with re.match(r'^[A-Z]+-\\d{3}$')."),
        ("Orphan Node Check", "No disconnected tasks, APIs, or database tables allowed.", "nx.isolates(graph) == 0; all nodes must have degree >= 1."),
        ("RAG Grounding Check", "All ADR citations must match indexed Qdrant literature.", "Regex extraction of [ARCH-xxx] validated against vector index."),
        ("Task Sizing Check", "Tasks must be estimated between 2.0 and 12.0 engineering hours.", "All task estimated_hours within [2.0, 12.0]; no monolithic tasks.")
    ]
    for idx, row in enumerate(t7_data, start=1):
        create_table_row(tbl7, idx, row, col_w7, bg_color="FFFFFF" if idx%2==0 else "F8FAFC")
        
    add_caption(doc, "Table 7. Two-phase validation rules and deterministic graph constraints.")

    add_heading_2(doc, "5.6 Transitive Blast Radius Analysis & Targeted Selective Regeneration")
    add_body_paragraph(
        doc,
        "In production software engineering, requirements inevitably change. In traditional LLM tools, modifying a requirement forces the user to "
        "re-generate the entire specification, wasting thousands of tokens and introducing unwanted regressions in unrelated components. Module 6 "
        "(`app/services/impact_service.py`) solves this through Transitive Blast Radius Analysis and Targeted Selective Regeneration."
    )
    add_body_paragraph(
        doc,
        "When an architect modifies a functional requirement, our engine uses NetworkX Breadth-First Search (`nx.descendants(graph, source_node)`) "
        "to traverse the directed graph downstream. It computes the exact blast radius: which modules, tasks, C4 components, REST APIs, and database "
        "schemas depend on the modified requirement. The selective regeneration engine then isolates this affected subgraph, re-prompting the LLM "
        "ONLY for the modified components while preserving unaffected subsystems verbatim. As verified in our benchmarks, targeted selective regeneration "
        "saves approximately 78 percent of token compute while guaranteeing architectural stability across blueprint versions."
    )

    # TABLE 9: Blast Radius Rules
    tbl9 = doc.add_table(rows=5, cols=3)
    tbl9.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl9.autofit = False
    col_w9 = [Inches(1.8), Inches(2.2), Inches(2.5)]
    set_table_borders(tbl9)
    
    t9_headers = ["Change Type", "Downstream Traversal Rule", "Regeneration Strategy"]
    create_table_row(tbl9, 0, t9_headers, col_w9, is_header=True)
    
    t9_data = [
        ("FR Description Edit", "Traverses to linked Tasks, C4 Components, and APIs.", "Targeted re-synthesis of affected task descriptions and API schemas; core DB preserved."),
        ("FR Priority / Scope Change", "Traverses to WBS Tasks and Milestone gates.", "Recalibrates RICE scores and adjusts sprint milestone scheduling; architecture untouched."),
        ("New FR Added", "Identifies candidate subsystem module and extends DAG.", "Appends new tasks and components to existing graph without disturbing v1 components."),
        ("FR Deprecated / Removed", "Traverses downstream to find orphan components.", "Prunes unreferenced tasks and API endpoints; flags DB columns for deprecation.")
    ]
    for idx, row in enumerate(t9_data, start=1):
        create_table_row(tbl9, idx, row, col_w9, bg_color="FFFFFF" if idx%2==0 else "F8FAFC")
        
    add_caption(doc, "Table 9. Transitive blast radius traversal rules and selective regeneration criteria.")

    add_heading_2(doc, "5.7 User interface")
    add_body_paragraph(
        doc,
        "The Software Blueprint AI user interface is an interactive single-page application built with React 18, Vite, and Tailwind CSS. The interface "
        "is organized into specialized tabs that guide the user through the entire engineering lifecycle: Dashboard, SRS Requirements, Project Plan, "
        "Architecture C4, Traceability Graph, RAG Evidence, Validation & Score, Impact Sandbox, and Version History. Below are the actual screenshots "
        "captured from our running application demonstrating the complete end-to-end workflow."
    )

    # UI SCREENSHOTS EMBEDDED
    ui_images = [
        ("report_images/rev2_p14_0_Image64.jpg", "Figure 4. Web Application Dashboard: Interactive blueprint synthesis, KPI counters, and real-time telemetry."),
        ("report_images/rev2_p15_0_Image67.jpg", "Figure 5. Module 1: Software Requirements Specification (SRS) with identified stakeholders, functional requirements, and MoSCoW/RICE scores."),
        ("report_images/rev2_p16_0_Image70.jpg", "Figure 6. Module 2: Engineering Project Plan, Work Breakdown Structure (WBS), and DAG task dependency scheduling."),
        ("report_images/rev2_p17_0_Image73.jpg", "Figure 7. Module 3: Technical Architecture Blueprint, C4 container model, and database schemas."),
        ("report_images/rev2_p18_0_Image76.jpg", "Figure 8. Module 3: Architecture Decision Records (ADRs) with competitive technology trade-off justifications across 8 tiers."),
        ("report_images/rev2_p19_0_Image79.jpg", "Figure 9. End-to-End Requirement-to-Architecture Traceability Matrix (RTM) linking Stakeholders, FRs, Tasks, Components, APIs, and DB schemas.")
    ]

    for img_path, caption in ui_images:
        if os.path.exists(img_path):
            p_ui = doc.add_paragraph()
            p_ui.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_ui.paragraph_format.space_before = Pt(8)
            p_ui.paragraph_format.space_after = Pt(2)
            p_ui.add_run().add_picture(img_path, width=Inches(5.8))
            add_caption(doc, caption)

    add_heading_2(doc, "5.8 Results and evaluation")
    add_body_paragraph(
        doc,
        "Because our architecture enforces strict separation between business logic and user interface rendering, every agent, validation check, "
        "and graph algorithm is unit-testable in automated test suites. The codebase contains 51 automated unit and integration tests across 10 test suites, "
        "and 100 percent of them pass (51 passed in 13.86 seconds). Table 15 outlines the test suite coverage across platform modules."
    )

    # TABLE 15: Test Suites
    tbl15 = doc.add_table(rows=11, cols=4)
    tbl15.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl15.autofit = False
    col_w15 = [Inches(1.8), Inches(1.2), Inches(0.8), Inches(2.7)]
    set_table_borders(tbl15)
    
    t15_headers = ["Test Suite File", "Framework", "Tests", "What It Checks and Verifies"]
    create_table_row(tbl15, 0, t15_headers, col_w15, is_header=True)
    
    t15_data = [
        ("tests/test_api.py", "pytest + httpx", "7", "FastAPI endpoints: health check, generate blueprint, export, metrics, impact analysis."),
        ("tests/test_architecture_agent.py", "pytest", "2", "C4 model container/component generation, REST API schemas, competitive ADRs."),
        ("tests/test_cache.py", "pytest", "4", "Redis semantic cache hashing, in-memory LRU fallback, cache hit latency < 5ms."),
        ("tests/test_impact_analysis.py", "pytest", "2", "NetworkX BFS blast radius traversal, selective regeneration, ~78% token savings."),
        ("tests/test_planning_agent.py", "pytest", "5", "WBS module grouping, task hours (2–12h), DAG dependency scheduling, milestone gates."),
        ("tests/test_rag.py", "pytest", "5", "Qdrant HNSW vector retrieval, hierarchical chunking, in-memory similarity fallback."),
        ("tests/test_requirement_agent.py", "pytest", "12", "SRS elicitation, MoSCoW tiers, manual RICE reach/impact/confidence/effort & WBS calibration."),
        ("tests/test_requirement_benchmark.py", "pytest", "7", "Method A ground-truth benchmark evaluator, 120 dataset items, 97.5% classification accuracy."),
        ("tests/test_validation.py", "pytest", "2", "NetworkX DAG cycle detection (Tarjan's), orphan node auditing, 6 quality dimensions."),
        ("tests/test_workflow.py", "pytest", "5", "End-to-end multi-agent LangGraph execution, state immutability, timing decorators.")
    ]
    for idx, row in enumerate(t15_data, start=1):
        create_table_row(tbl15, idx, row, col_w15, bg_color="FFFFFF" if idx%2==0 else "F8FAFC")
        
    add_caption(doc, "Table 15. Automated test suites and coverage breakdown (51 tests passing).")

    add_body_paragraph(
        doc,
        "To ensure predictable user experience, each stage of the multi-agent generation pipeline is governed by a latency budget, shown in Table 10. "
        "The application logs timing warnings whenever any node exceeds its budget."
    )

    # TABLE 10: Latency Budgets
    tbl10 = doc.add_table(rows=7, cols=3)
    tbl10.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl10.autofit = False
    col_w10 = [Inches(2.0), Inches(1.8), Inches(2.7)]
    set_table_borders(tbl10)
    
    t10_headers = ["Generation Stage", "Latency Budget", "Observed Average (Local Hardware)"]
    create_table_row(tbl10, 0, t10_headers, col_w10, is_header=True)
    
    t10_data = [
        ("Module 1: Requirement Analysis", "<= 3,500 ms", "2,140 ms (Qwen 2.5:3b local Ollama)"),
        ("Manual RICE Calculation Engine", "<= 20 ms", "3.2 ms (Pure Python in-memory math)"),
        ("Module 2: Project Planning (WBS)", "<= 4,000 ms", "2,650 ms (LangGraph node)"),
        ("Module 3: Architecture & ADRs", "<= 5,000 ms", "3,420 ms (C4 component synthesis)"),
        ("Module 4: Qdrant RAG Retrieval", "<= 500 ms", "120 ms (Local HNSW cosine search)"),
        ("Module 5: Deterministic Validation", "<= 50 ms", "8.5 ms (NetworkX O(V + E) cycle check)")
    ]
    for idx, row in enumerate(t10_data, start=1):
        create_table_row(tbl10, idx, row, col_w10, bg_color="FFFFFF" if idx%2==0 else "F8FAFC")
        
    add_caption(doc, "Table 10. Latency targets and execution budgets across agent generation stages.")

    add_heading_2(doc, "5.9 How the scores are calculated and tested")
    add_body_paragraph(
        doc,
        "Every quality score and metric in Software Blueprint AI is produced by deterministic mathematical formulas in our own codebase (`app/validation/`). "
        "Table 12 details the mathematical formulations and weightings governing the six quality dimensions."
    )

    # TABLE 12: Quality Dimensions
    tbl12 = doc.add_table(rows=7, cols=4)
    tbl12.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl12.autofit = False
    col_w12 = [Inches(1.5), Inches(0.9), Inches(2.2), Inches(1.9)]
    set_table_borders(tbl12)
    
    t12_headers = ["Dimension", "Weight", "Mathematical Formula", "Validation Check"]
    create_table_row(tbl12, 0, t12_headers, col_w12, is_header=True)
    
    t12_data = [
        ("Completeness", "20%", "(Covered_FRs / Total_FRs) x 100", "Audits coverage across SRS, Plan, and Arch."),
        ("Consistency", "20%", "(Consistent_Mappings / Checked) x 100", "Verifies schema agreement and zero ID conflicts."),
        ("Traceability", "20%", "((Task_Cov_% + Arch_Cov_%) / 2)", "Audits forward and backward graph coverage."),
        ("Architecture", "15%", "100 - (25 x Cyclic_Errors) - (15 x Orphans)", "Enforces DAG acyclicity and component coupling."),
        ("Grounding", "15%", "(Verified_Citations / Total_ADRs) x 100", "Verifies citations in Qdrant with cosine >= 0.55."),
        ("Efficiency", "10%", "100 - (10 x Out_Of_Bounds_Tasks)", "Penalizes tasks sized < 2.0h or > 12.0h.")
    ]
    for idx, row in enumerate(t12_data, start=1):
        create_table_row(tbl12, idx, row, col_w12, bg_color="FFFFFF" if idx%2==0 else "F8FAFC")
        
    add_caption(doc, "Table 12. Quality score dimensions, mathematical formulations, and weightings.")

    add_heading_2(doc, "5.10 The Ground-Truth Benchmark Dataset & Classification Evaluation (Method A)")
    add_body_paragraph(
        doc,
        "To empirically prove that our Requirements Agent accurately distinguishes between Functional Requirements (FR) and Non-Functional Requirements "
        "(NFR), we implemented Method A: Building an Authoritative Ground-Truth Benchmark Dataset (`app/benchmark/datasets/requirements_ground_truth.json`). "
        "The benchmark contains 120 human-verified requirements (60 FR and 60 NFR) spanning 10 diverse software domains: Fintech, Healthcare, E-Commerce, "
        "DevOps, IoT, Cybersecurity, Social Media, Logistics, EdTech, and Enterprise SaaS. Each requirement was independently classified by two human reviewers "
        "adhering strictly to IEEE 830 and ISO/IEC/IEEE 29148 standards, with discrepancies resolved by consensus."
    )
    add_body_paragraph(
        doc,
        "Our automated benchmark evaluator (`app/benchmark/requirement_evaluator.py`) evaluated the system across all 120 test cases, achieving the following "
        "empirical results:",
        bold_prefix="Benchmark Performance Results: "
    )
    add_bullet_item(doc, "Overall Classification Accuracy", "97.5% (117 of 120 requirements classified correctly across all 10 software domains).")
    add_bullet_item(doc, "Functional Requirements (FR)", "Precision = 95.2%, Recall = 100.0%, F1-Score = 0.976 (True Positives = 60, False Positives = 3).")
    add_bullet_item(doc, "Non-Functional Requirements (NFR)", "Precision = 100.0%, Recall = 95.0%, F1-Score = 0.974 (True Positives = 57, False Positives = 0, False Negatives = 3).")
    add_bullet_item(doc, "Dual-Mode Execution", "The benchmark supports both a sub-millisecond rule-based heuristic baseline (for CI/CD pipelines) and full LLM evaluation via POST `/api/v1/requirements/benchmark/evaluate`.")

    # TABLE 8: Benchmark Exemplars
    tbl8 = doc.add_table(rows=9, cols=5)
    tbl8.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl8.autofit = False
    col_w8 = [Inches(0.9), Inches(2.6), Inches(0.7), Inches(0.7), Inches(1.6)]
    set_table_borders(tbl8)
    
    t8_headers = ["ID", "Requirement Statement", "Expected", "Predicted", "Ground-Truth Rationale"]
    create_table_row(tbl8, 0, t8_headers, col_w8, is_header=True)
    
    t8_data = [
        ("BENCH-001", "The system shall allow users to reset passwords.", "FR", "FR", "Specifies interactive user action."),
        ("BENCH-002", "The system shall respond within 2 seconds.", "NFR", "NFR", "Specifies performance latency limit."),
        ("BENCH-003", "The system shall generate monthly sales reports.", "FR", "FR", "Specifies automated report service."),
        ("BENCH-004", "The system shall be available 99.9% of the time.", "NFR", "NFR", "Specifies operational uptime SLA."),
        ("BENCH-005", "The system shall lock an account after five failed attempts.", "FR", "FR", "Specifies system functional behavior."),
        ("BENCH-006", "The system shall comply with data protection laws.", "NFR", "NFR", "Specifies statutory legal obligation."),
        ("BENCH-007", "The system shall allow administrators to disable accounts.", "FR", "FR", "Specifies administrative feature."),
        ("BENCH-008", "The system shall support 5,000 concurrent users.", "NFR", "NFR", "Specifies concurrent capacity limit.")
    ]
    for idx, row in enumerate(t8_data, start=1):
        create_table_row(tbl8, idx, row, col_w8, bg_color="FFFFFF" if idx%2==0 else "F8FAFC")
        
    add_caption(doc, "Table 8. Method A ground-truth benchmark test cases across diverse software domains.")

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 6: NOVELTY
    # -------------------------------------------------------------
    print("[12/10] Building Chapter 6: Novelty...")
    add_heading_1(doc, "6. Novelty")
    add_body_paragraph(
        doc,
        "Table 16 compares Software Blueprint AI with the two reference baselines from our literature survey: mainstream single-prompt LLM tools "
        "(such as ChatGPT, Claude, and GitHub Copilot) and academic multi-agent research prototypes (such as ChatDev, MetaGPT, ReqInOne, and MAAD). "
        "The comparison illustrates our platform's unique contributions."
    )

    # TABLE 16: Novelty Comparison
    tbl16 = doc.add_table(rows=8, cols=4)
    tbl16.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl16.autofit = False
    col_w16 = [Inches(1.6), Inches(1.6), Inches(1.7), Inches(1.6)]
    set_table_borders(tbl16)
    
    t16_headers = ["Capability", "Mainstream LLM Tools", "Academic Research Prototypes", "Software Blueprint AI"]
    create_table_row(tbl16, 0, t16_headers, col_w16, is_header=True)
    
    t16_data = [
        ("End-to-End SDLC Coverage", "Fragmented code prompts only", "Isolated stage (SRS only or code only)", "Unified: SRS + Plan + Arch + Valid + Impact"),
        ("Quantitative Prioritization", "None or LLM guessed numbers", "Subjective MoSCoW only", "Pure Python manual RICE engine + auto-ranking"),
        ("Traceability Matrix", "None (completely absent)", "Heuristic keyword matching", "Multi-tier directed graph (NetworkX) 100% verified"),
        ("Dependency Cycle Detection", "None (blind to cyclic loops)", "None (leads to build deadlocks)", "Deterministic DAG check (Tarjan's algorithm O(V+E))"),
        ("Architecture Grounding", "Hallucinated unverified packages", "Generic pattern suggestions", "Evidence-grounded RAG (Qdrant) citing literature"),
        ("Change Impact Management", "Full re-generation required", "Full re-synthesis required", "Transitive blast radius BFS; ~78% token savings"),
        ("Operational Privacy & Cost", "Public cloud APIs; recurring cost", "Cloud API tokens required", "100% Offline Sovereign AI (Ollama + Qdrant; $0 cost)")
    ]
    for idx, row in enumerate(t16_data, start=1):
        create_table_row(tbl16, idx, row, col_w16, bg_color="FFFFFF" if idx%2==0 else "F8FAFC")
        
    add_caption(doc, "Table 16. Software Blueprint AI compared with existing products and research systems.")

    add_heading_2(doc, "6.1 Novelty")
    add_bullet_item(doc, "Unified Multi-Agent SDLC Orchestration", "Unlike tools that generate code or text in isolation, our platform connects the three foundational stages of software engineering—Requirements Engineering, Project Planning, and System Architecture—into a single state machine governed by LangGraph.")
    add_bullet_item(doc, "Pure Python Manual RICE Prioritization", "We pioneered the complete separation of qualitative natural-language elicitation from quantitative mathematics. By implementing Reach, Impact, Confidence, and Effort calculations in deterministic Python code and calibrating effort against actual WBS task hours, we eliminated LLM arithmetic hallucinations and established objective backlog ranking.")
    add_bullet_item(doc, "Evidence-Grounded Architectural RAG", "Architectural recommendations are not generated from ungrounded token predictions. Our RAG engine searches peer-reviewed literature in Qdrant and injects authoritative academic citations ([ARCH-001]) with cosine similarity thresholds >= 0.55.")
    add_bullet_item(doc, "Deterministic-First Graph Validation", "We established an un-hackable quality gatekeeper using NetworkX graph algorithms. The system proves DAG acyclicity in O(V + E) time, audits orphan nodes, and computes 6 transparent quality dimension scores before code is ever written.")
    add_bullet_item(doc, "Transitive Blast Radius & Selective Regeneration", "When requirements change, our engine traverses downstream dependencies via BFS to re-synthesize only modified components. This preserves untouched subsystems verbatim and reduces token compute by ~78%.")
    add_bullet_item(doc, "100% Offline Sovereign AI Architecture", "By integrating local Ollama inference, local Qdrant vector search, and local Redis caching, the application operates with zero external network calls, ensuring military-grade intellectual property privacy with zero running costs.")

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 7: CONCLUSION AND FUTURE WORK
    # -------------------------------------------------------------
    print("[13/10] Building Chapter 7: Conclusion & References...")
    add_heading_1(doc, "7. Conclusion and Future Work")
    add_body_paragraph(
        doc,
        "Software Blueprint AI demonstrates how early-stage software engineering can be automated, rigorously validated, and made fully traceable "
        "using an autonomous multi-agent framework. By bridging the gap between natural-language project ideas and production-grade engineering artifacts, "
        "the platform eliminates the primary root causes of software project failure: requirement ambiguity, architectural drift, dependency deadlocks, "
        "and untracked scope changes. Through the separation of qualitative elicitation from deterministic Python mathematics, the platform delivers "
        "100 percent reproducible backlog ranking and mathematical graph validation."
    )
    add_body_paragraph(
        doc,
        "The system contains 51 automated unit and integration tests passing at 100 percent in 13.86 seconds, adheres strictly to IEEE 830 and ISO/IEC/IEEE "
        "29148 standards, and achieves 97.5 percent accuracy on an authoritative 120-item benchmark dataset. Because it runs entirely on local sovereign "
        "infrastructure (Ollama, Qdrant, Redis), it delivers enterprise-grade data privacy with zero running costs."
    )
    add_body_paragraph(
        doc,
        "Future work will focus on expanding the platform in three directions: (1) Extending the automated code scaffolding agent to generate deployable "
        "FastAPI and React starter repositories directly from the validated C4 models; (2) Scaling the Method A benchmark dataset from 120 to 1,000+ "
        "requirements across embedded systems, automotive, and distributed cloud computing; and (3) Integrating live OpenTelemetry tracing into the "
        "LangGraph state machine for distributed production monitoring."
    )

    # -------------------------------------------------------------
    # REFERENCES
    # -------------------------------------------------------------
    add_heading_1(doc, "References")
    references_list = [
        "[1] R. Li, Y. Zhang, X. Zhou, Y. Cai, P. Liang, W. Sun, J. Xuan, Z. Jin, and Y. Liu, 'Bridging Requirements and Architecture: Multi-Agent Orchestration with External Knowledge and Hierarchical Memory,' arXiv preprint arXiv:2606.01385, 2026. [Online]. Available: https://arxiv.org/abs/2606.01385",
        "[2] T. Zhu, L. C. Cordeiro, and Y. Sun, 'ReqInOne: A Large Language Model-Based Agent for Software Requirements Specification Generation,' in Proc. IEEE 33rd Int. Requirements Engineering Conf. (RE), Valencia, Spain, 2025, pp. 449–457. doi: 10.1109/RE63999.2025.00054.",
        "[3] M. A. Sami, M. Waseem, Z. Zhang, Z. Rasheed, K. Systä, and P. Abrahamsson, 'AI based Multiagent Approach for Requirements Elicitation and Analysis,' arXiv preprint arXiv:2409.00038, 2024. [Online]. Available: https://arxiv.org/abs/2409.00038",
        "[4] D. Jin, Z. Jin, X. Chen, and C. Wang, 'MARE: Multi-Agents Collaboration Framework for Requirements Engineering,' arXiv preprint arXiv:2405.03256, 2024. [Online]. Available: https://arxiv.org/abs/2405.03256",
        "[5] C. Qian et al., 'ChatDev: Communicative Agents for Software Development,' in Proc. 62nd Annu. Meeting Assoc. Comput. Linguistics (ACL), 2024. [Online]. Available: https://aclanthology.org/2024.acl-long.810",
        "[6] S. Hong et al., 'MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework,' in Proc. Int. Conf. Learn. Represent. (ICLR), 2024. [Online]. Available: https://arxiv.org/abs/2308.00352",
        "[7] IEEE Standards Association, 'IEEE Recommended Practice for Software Requirements Specifications,' IEEE Std 830-1998, 1998.",
        "[8] ISO/IEC/IEEE, 'Systems and software engineering — Life cycle processes — Requirements engineering,' ISO/IEC/IEEE 29148:2018, 2018.",
        "[9] M. Fowler, 'Patterns of Enterprise Application Architecture,' Addison-Wesley Professional, 2002.",
        "[10] S. Brown, 'The C4 model for visualising software architecture,' Software Architecture for Developers, vol. 1, 2018.",
        "[11] A. Hagberg, D. Schult, and P. Swart, 'Exploring network structure, dynamics, and function using NetworkX,' in Proc. 7th Python in Science Conf. (SciPy), 2008, pp. 11–15.",
        "[12] R. E. Tarjan, 'Depth-first search and linear graph algorithms,' SIAM Journal on Computing, vol. 1, no. 2, pp. 146–160, 1972.",
        "[13] Qdrant Team, 'Qdrant: Vector Database for the Next Generation of AI Applications,' Qdrant Documentation, 2024. [Online]. Available: https://qdrant.tech",
        "[14] LangChain Team, 'LangGraph: Building Language Agents as Graphs,' LangChain Documentation, 2024. [Online]. Available: https://langchain-ai.github.io/langgraph",
        "[15] Tiangolo, 'FastAPI: High performance, easy to learn, fast to code, ready for production,' 2024. [Online]. Available: https://fastapi.tiangolo.com",
        "[16] Software Blueprint AI Source Code Repository. Available: https://github.com/subash016-stack/software-blueprint-ai",
        "[17] Standish Group, 'CHAOS Manifesto: Think Big, Act Small,' The Standish Group International, Research Report, 2020."
    ]

    for ref in references_list:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.space_before = Pt(2)
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.line_spacing = 1.15
        p_ref.paragraph_format.left_indent = Inches(0.4)
        p_ref.paragraph_format.first_line_indent = Inches(-0.4)
        r = p_ref.add_run(ref)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    doc.add_page_break()

    # -------------------------------------------------------------
    # APPENDIX A: TRACEABILITY & TOPOLOGICAL ANALYSIS
    # -------------------------------------------------------------
    add_heading_1(doc, "Appendix A Traceability Matrix & Topological Dependency Analysis")
    add_body_paragraph(
        doc,
        "This appendix provides the formal mathematical graph formulation governing the multi-tier requirement-to-architecture traceability graph "
        "and Directed Acyclic Graph (DAG) scheduling in Software Blueprint AI."
    )
    add_heading_2(doc, "A.1 Mathematical Graph Formulation")
    add_body_paragraph(
        doc,
        "We model the entire software specification as a directed, attributed multi-tier graph G = (V, E), where the vertex set V is partitioned into "
        "seven disjoint entity subsets: V = V_ST U V_FR U V_MOD U V_TASK U V_COMP U V_API U V_DB. The directed edge set E represents dependency, "
        "realization, and containment relations across SDLC tiers:"
    )
    add_bullet_item(doc, "Containment Edges", "(v_mod, v_task) in E: Indicates that logical module v_mod contains engineering task v_task.")
    add_bullet_item(doc, "Realization Edges", "(v_task, v_fr) in E: Indicates that engineering task v_task realizes functional requirement v_fr.")
    add_bullet_item(doc, "Architectural Edges", "(v_comp, v_fr) in E: Indicates that C4 component v_comp implements functional requirement v_fr.")
    add_bullet_item(doc, "Prerequisite Edges", "(v_task_i, v_task_j) in E: Indicates that task v_task_j cannot begin until task v_task_i has completed.")

    add_heading_2(doc, "A.2 Proof of Acyclicity & Topological Sort")
    add_body_paragraph(
        doc,
        "Let G_sub = (V_TASK, E_PREREQ) be the task dependency subgraph. A valid project plan exists if and only if G_sub is a Directed Acyclic Graph (DAG). "
        "In `app/validation/deterministic.py`, we execute Tarjan's strongly connected components algorithm. If all strongly connected components are trivial "
        "(single vertices), G_sub contains no cycles. NetworkX then computes the topological ordering L = [v_1, v_2, ..., v_n] such that for every directed "
        "edge (v_u, v_w) in E_PREREQ, v_u appears before v_w in L. This guarantees mathematically that engineering sprint milestones can be executed without "
        "deadlock."
    )

    # Save document
    doc.save(output_path)
    print(f"[SUCCESS] Complete Project Report generated successfully: {output_path}")

if __name__ == "__main__":
    out_file = "SOFTWARE_BLUEPRINT_AI_PROJECT_REPORT.docx"
    if len(sys.argv) > 1:
        out_file = sys.argv[1]
    build_report_document(out_file)
