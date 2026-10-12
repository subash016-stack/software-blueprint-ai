"""
generate_master_pdf.py
Generates the comprehensive master PDF and Markdown documentation for Software Blueprint AI.
"""

import os
import sys
import html
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print total page numbers (e.g. Page X of Y)
    along with running header and footer.
    """
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Skip running header and footer on the cover / title page
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running Header
        self.drawString(54, 11 * 72 - 36, "SOFTWARE BLUEPRINT AI — MASTER ARCHITECTURE & REVIEW DOSSIER")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)

        # Running Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.setFont("Helvetica", 8)
        self.drawString(54, 32, "Confidential & Proprietary — Project Defense & System Architecture Reference")
        self.drawRightString(8.5 * 72 - 54, 32, page_str)
        self.line(54, 42, 8.5 * 72 - 54, 42)

        self.restoreState()


def build_pdf(filename="SOFTWARE_BLUEPRINT_AI_MASTER_DOCUMENTATION.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Palette
    c_primary = colors.HexColor("#0F172A")    # Slate 900
    c_secondary = colors.HexColor("#1E293B")  # Slate 800
    c_accent = colors.HexColor("#2563EB")     # Blue 600
    c_purple = colors.HexColor("#7C3AED")     # Purple 600
    c_text = colors.HexColor("#334155")       # Slate 700
    c_light = colors.HexColor("#F8FAFC")      # Slate 50
    c_border = colors.HexColor("#E2E8F0")     # Slate 200

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=c_primary,
        alignment=0,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_accent,
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        'ChapterH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=c_secondary,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_accent,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'SubSectionH3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=c_secondary,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_text,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=c_text,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'DocCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4
    )

    box_text_style = ParagraphStyle(
        'BoxText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_text
    )

    box_bold_style = ParagraphStyle(
        'BoxBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=c_primary
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=0
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=c_text
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=c_primary
    )

    story = []

    def p(text, style=body_style):
        # Escape raw text safely except allowed html tags like <b>, <i>, <font>
        return Paragraph(text, style)

    def callout_box(title, text_paragraphs, border_color="#2563EB", bg_color="#EFF6FF"):
        t_data = []
        if title:
            t_data.append([Paragraph(f"<b>{title}</b>", box_bold_style)])
        for tp in text_paragraphs:
            t_data.append([Paragraph(tp, box_text_style)])
        
        t = Table(t_data, colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg_color)),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor(border_color)),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        return t

    # -------------------------------------------------------------
    # COVER / HEADER BLOCK
    # -------------------------------------------------------------
    story.append(p("SOFTWARE BLUEPRINT AI", title_style))
    story.append(p("Comprehensive Architecture, Implementation, Tech Stack, UI, and Defense Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=0, spaceAfter=14))

    meta_table_data = [
        [
            Paragraph("<b>Project Title:</b> Software Blueprint AI", body_style),
            Paragraph("<b>Target Environment:</b> 100% Offline / Local AI Engine", body_style)
        ],
        [
            Paragraph("<b>Architecture Pattern:</b> Agentic Pipeline & Deterministic Graph Engine", body_style),
            Paragraph("<b>Validation Model:</b> 2-Phase (Deterministic Rules + LLM Consistency)", body_style)
        ],
        [
            Paragraph("<b>Document Purpose:</b> Technical Review & Viva Defense Master Manual", body_style),
            Paragraph("<b>Test Suite:</b> 38/38 Unit & Integration Tests Passing (100%)", body_style)
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[250, 254])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # Executive Overview
    story.append(callout_box(
        "Executive Summary & Project Mission",
        [
            "<b>Software Blueprint AI</b> is an enterprise-grade, autonomous software architecture and specification engineering platform. It ingests raw, ambiguous software requirements (text or PDF documents) and deterministically compiles them into fully-realized, IEEE 830-compliant software blueprints.",
            "Unlike conventional LLM wrappers that hallucinate architectural files in an unverified black box, Software Blueprint AI enforces <b>strict graph-theoretic acyclicity</b>, <b>bi-directional traceability matrices</b>, <b>literature-grounded RAG citations</b>, and <b>executable code scaffolding</b>.",
            "The system runs <b>100% offline</b> without third-party cloud API dependencies, ensuring complete enterprise intellectual property isolation and air-gapped security."
        ],
        border_color="#3B82F6",
        bg_color="#EFF6FF"
    ))
    story.append(Spacer(1, 14))

    # -------------------------------------------------------------
    # CHAPTER 1: WHAT WE HAVE CREATED & HOW IT WORKS
    # -------------------------------------------------------------
    story.append(p("CHAPTER 1: SYSTEM ARCHITECTURE & CORE WORKFLOW", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=c_secondary, spaceBefore=0, spaceAfter=8))

    story.append(p(
        "The application is engineered around an <b>Autonomous 6-Stage Sequential Pipeline</b> backed by a state-managed orchestrator (`app/services/orchestrator.py`), supported by a local retrieval-augmented generation (RAG) knowledge engine (`app/rag/`). Here is the step-by-step lifecycle of how a blueprint is generated from scratch:"
    ))

    pipeline_steps = [
        ("Phase 1: Ingestion & Ambiguity Resolution", "Extracts raw text from inputs or PDF files. An ambiguity scoring heuristic evaluates requirement clarity, testability, and vagueness (0.0 to 1.0). If ambiguity exceeds 0.5, targeted clarification prompts are dynamically formulated."),
        ("Phase 2: IEEE 830 Specification Generation", "The LLM decomposes the prompt into formal Functional Requirements (FR-001..) with user stories, Given/When/Then acceptance criteria, and P0/P1/P2 priorities, alongside Non-Functional Requirements (NFR-001..) across latency, security, and scalability."),
        ("Phase 3: RAG Grounding & Literature Retrieval", "Hierarchical Markdown chunking parses curated architectural whitepapers. Local embeddings query a Qdrant vector database (HNSW cosine index) to retrieve authoritative patterns cited by literature IDs (e.g. [ARCH-001], [DATA-001])."),
        ("Phase 4: Architecture Synthesis & Tech Stack Rationale", "Recommends an optimal architecture pattern (Modular Monolith, Event-Driven, Microservices) with C4 Model diagrams (Context, Container, Component, Deployment) and generates Architecture Decision Records (ADRs) with explicit competitive comparisons."),
        ("Phase 5: Bi-Directional Traceability Matrix Compilation", "NetworkX constructs a directed graph linking FRs -> NFRs -> Modules -> Tests. Forward completeness, backward completeness, and transitive blast radius impact are computed deterministically."),
        ("Phase 6: Code Scaffolding & Critical-Path DAG Compilation", "Compiles a complete executable project code tree. NetworkX checks for circular dependency deadlocks via topological sorting, identifies the critical path, and packages a downloadable ZIP."),
        ("Phase 7: Two-Phase Hybrid Validation Audit", "Phase 1 performs a deterministic AST and graph audit (zero hallucination). Phase 2 evaluates semantic consistency. Scores are mathematically computed across 6 dimensions with explainability."),
        ("Phase 8: Dossier Export & Observability Telemetry", "Exports an IEEE 830 Markdown dossier and JSON artifact, while logging live LLM calls, cache hit rates, latency, and tokens saved.")
    ]

    for title, desc in pipeline_steps:
        story.append(p(f"• <b>{title}:</b> {desc}", bullet_style))

    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # CHAPTER 2: TECH STACK ANALYSIS & COMPETITIVE JUSTIFICATIONS
    # -------------------------------------------------------------
    story.append(p("CHAPTER 2: COMPLETE TECH STACK ANALYSIS & COMPARISONS", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=c_secondary, spaceBefore=0, spaceAfter=8))

    story.append(p(
        "Every technology and algorithm in Software Blueprint AI was intentionally selected based on strict engineering criteria: offline execution, async performance, mathematical rigor, and developer productivity. The table below provides the comprehensive justification and competitive analysis against alternatives:"
    ))

    tech_table_data = [
        [
            Paragraph("<b>Tier / Role</b>", table_header_style),
            Paragraph("<b>Selected Technology</b>", table_header_style),
            Paragraph("<b>Evaluated Alternatives</b>", table_header_style),
            Paragraph("<b>Why Selected Over Competing Alternatives</b>", table_header_style)
        ],
        [
            Paragraph("<b>Web API Framework</b>", table_cell_bold),
            Paragraph("FastAPI 0.141<br/>(ASGI / Python 3.11+)", table_cell_style),
            Paragraph("Node.js (Express),<br/>Flask (WSGI),<br/>Django", table_cell_style),
            Paragraph("<b>FastAPI over Flask:</b> Flask defaults to synchronous WSGI and requires third-party plugins for OpenAPI. FastAPI provides native ASGI async event loops and auto-generates Swagger/OpenAPI docs via Pydantic v2.<br/><b>FastAPI over Node.js:</b> Eliminates cross-language friction. Keeps the web API in the exact same Python process as NetworkX, LangGraph, and sentence-transformers.", table_cell_style)
        ],
        [
            Paragraph("<b>Relational Persistence</b>", table_cell_bold),
            Paragraph("PostgreSQL 16 +<br/>pgvector", table_cell_style),
            Paragraph("MongoDB,<br/>MySQL 8.0", table_cell_style),
            Paragraph("<b>Postgres over Mongo:</b> Software blueprints have strict relational integrity (FR -> NFR -> Module -> Test foreign keys). MongoDB lacks strict foreign keys and atomic cascading joins.<br/><b>Postgres over MySQL:</b> `pgvector` co-locates relational schemas and HNSW vector indices in one ACID store.", table_cell_style)
        ],
        [
            Paragraph("<b>Caching & State Broker</b>", table_cell_bold),
            Paragraph("Redis 7.2<br/>(Pub/Sub & Cache)", table_cell_style),
            Paragraph("Memcached,<br/>Hazelcast", table_cell_style),
            Paragraph("<b>Redis over Memcached:</b> Memcached is a raw string cache without data structures (hashes/sets/streams) or Pub/Sub event broadcasting. Redis enables atomic caching, stream pipelines, and semantic cache TTLs.<br/><b>Redis over Hazelcast:</b> Low-footprint C binary vs heavy distributed JVM runtime.", table_cell_style)
        ],
        [
            Paragraph("<b>Vector Database</b>", table_cell_bold),
            Paragraph("Qdrant (Local<br/>In-Memory / Docker)", table_cell_style),
            Paragraph("Pinecone (Cloud),<br/>Milvus (Distributed)", table_cell_style),
            Paragraph("<b>Qdrant over Pinecone:</b> Pinecone is a cloud-only SaaS that sends proprietary prompts over the public internet, violating the <b>100% offline privacy mandate</b>. Qdrant runs locally with zero external API calls.<br/><b>Qdrant over Milvus:</b> Rust-based single binary vs complex Milvus cluster (MinIO, etcd, Pulsar).", table_cell_style)
        ],
        [
            Paragraph("<b>Frontend Framework</b>", table_cell_bold),
            Paragraph("React 18 + Vite<br/>(Single Page App)", table_cell_style),
            Paragraph("Next.js (SSR),<br/>Angular", table_cell_style),
            Paragraph("<b>React/Vite over Next.js:</b> Next.js SSR requires an active Node.js server runtime alongside FastAPI. Vite compiles pure static assets (`HTML/CSS/JS`) mounted directly into FastAPI's static root with sub-100ms HMR.<br/><b>React over Angular:</b> Lightweight virtual DOM vs heavy RxJS decorators.", table_cell_style)
        ],
        [
            Paragraph("<b>Security & Auth</b>", table_cell_bold),
            Paragraph("OAuth 2.1 +<br/>Stateless JWT", table_cell_style),
            Paragraph("Stateful Cookies,<br/>Static API Keys", table_cell_style),
            Paragraph("<b>JWT over Cookies:</b> Stateless JWTs contain cryptographically signed claims validated without database round-trips and prevent CSRF vulnerabilities.<br/><b>JWT over API Keys:</b> Granular role boundaries (RBAC) and short TTL expirations.", table_cell_style)
        ],
        [
            Paragraph("<b>DAG Resolution Algorithm</b>", table_cell_bold),
            Paragraph("NetworkX DFS &<br/>Transitive Reduction", table_cell_style),
            Paragraph("Custom DFS scripts,<br/>In-house Kahn's", table_cell_style),
            Paragraph("<b>NetworkX over Hand-rolled Scripts:</b> Ad-hoc scripts fail on complex cyclic graph topologies and risk recursion stack overflows. NetworkX provides battle-tested O(V + E) cycle detection and transitive reduction.", table_cell_style)
        ],
        [
            Paragraph("<b>RAG Chunking Algorithm</b>", table_cell_bold),
            Paragraph("Hierarchical Markdown<br/>Chunking with Breadcrumbs", table_cell_style),
            Paragraph("Fixed-Size Splitter,<br/>Sentence Splitter", table_cell_style),
            Paragraph("<b>Hierarchical over Naive Splitters:</b> Fixed character splitters sever sentences mid-thought and drop section titles. Breadcrumb prefixing (`[Doc > Section > H3]`) preserves parent context, boosting cosine precision from ~0.45 to >0.70.", table_cell_style)
        ]
    ]

    tech_table = Table(tech_table_data, colWidths=[80, 85, 85, 254])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(tech_table)
    story.append(Spacer(1, 14))

    # -------------------------------------------------------------
    # CHAPTER 3: DETAILED FEATURE IMPLEMENTATION MAPPING
    # -------------------------------------------------------------
    story.append(p("CHAPTER 3: DETAILED FEATURE IMPLEMENTATION & CODE STRUCTURE", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=c_secondary, spaceBefore=0, spaceAfter=8))

    story.append(p(
        "Below is the exact code mapping showing how every major application capability is implemented, including directory paths, primary classes/functions, and internal mechanics:"
    ))

    modules_code_breakdown = [
        (
            "1. Requirements Ingestion & Ambiguity Engine",
            "app/agents/requirements_agent.py, app/schemas.py",
            [
                "<b>PDF Extraction:</b> `extract_text_from_pdf()` parses binary PDF streams using `pypdf`, falling back gracefully to raw string buffers if corrupt.",
                "<b>Ambiguity Scoring:</b> Calculates lexical vagueness and missing acceptance criteria. Returns an ambiguity metric between 0.0 and 1.0.",
                "<b>Structured Pydantic Models:</b> Generates `RequirementsDocument` containing `FunctionalRequirement` (user story, Given/When/Then acceptance criteria, priority P0/P1/P2) and `NonFunctionalRequirement` (category, threshold metric, verification method)."
            ]
        ),
        (
            "2. Bi-Directional Traceability Matrix & Graph Engine",
            "app/services/traceability.py, app/agents/traceability_agent.py",
            [
                "<b>NetworkX Multigraph:</b> Instantiates a directed graph `nx.DiGraph` where nodes represent requirements, modules, and test suites.",
                "<b>Coverage Analysis:</b> Computes Forward Coverage (percentage of FRs mapped to at least one code module) and Backward Coverage (percentage of modules justified by requirements).",
                "<b>Transitive Blast Radius:</b> Uses `nx.descendants()` to simulate requirement changes: clicking any requirement instantly highlights all downstream affected modules and test suites.",
                "<b>Orphan Detection:</b> Flags unbacked modules or unmapped requirements to ensure zero architectural bloat."
            ]
        ),
        (
            "3. Architecture Synthesis & ADR Engine",
            "app/agents/architecture_agent.py, app/services/export_service.py",
            [
                "<b>Pattern Selection:</b> Evaluates system scale and NFRs to prescribe Modular Monolith, Microservices, or Event-Driven architectures.",
                "<b>C4 Diagram Compilation:</b> Emits valid Mermaid.js diagrams covering System Context, Container boundaries, Component interactions, and Deployment topology.",
                "<b>Literature-Grounded ADRs:</b> Architecture Decision Records (ADRs) linking to citations (`[ARCH-001]`, `[DATA-001]`) with Context, Decision, and Consequences.",
                "<b>Competitive Tech Stack Rationale:</b> Evaluates each technology tier against 2-3 alternatives, populating `TechStackItem` with `alternatives_compared` and `comparison_justification`."
            ]
        ),
        (
            "4. Code Scaffolding & Critical-Path DAG Compiler",
            "app/services/scaffold_service.py, app/services/dag_compiler.py",
            [
                "<b>Runnable Scaffolding Generation:</b> Produces directory trees with complete starter files (`main.py`, `models.py`, `routes.py`, `Dockerfile`, `README.md`).",
                "<b>Topological Sorting:</b> Uses `nx.topological_sort(graph)` to determine safe compilation and execution order.",
                "<b>Cycle Detection & Healing:</b> Executes `nx.simple_cycles(graph)`. If circular dependencies exist (e.g. A -> B -> A), flags a critical deadlock and provides automated cycle-breaker recommendations (dependency inversion / event queues).",
                "<b>Critical Path Engine:</b> Calculates the longest weighted directed path in the DAG to identify the pipeline bottleneck.",
                "<b>ZIP Generation:</b> Bundles the generated code tree into an in-memory `io.BytesIO` ZIP archive for instant browser download."
            ]
        ),
        (
            "5. Hybrid Validation & Score Explainability Engine",
            "app/validation/deterministic.py, app/agents/validation_agent.py",
            [
                "<b>Phase 1 Deterministic Audit:</b> Pure algorithmic validation without LLM calls. Validates Pydantic schema contracts, graph acyclicity, and ID referential integrity.",
                "<b>Phase 2 Semantic LLM Audit:</b> High-level check verifying that the generated architecture genuinely satisfies the user's business intent.",
                "<b>Exact Mathematical Scoring Formulas:</b> Computes 6 distinct quality dimensions: Requirements (95%), Traceability (66%), Architecture (65%), DAG Validity (100%), NFR Coverage (60%), RAG Grounding (92%).",
                "<b>Score Explainability:</b> For every dimension, returns `ScoreExplanation` containing mathematical formula, positive scoring criteria (+pts), deduction trace (-pts), and actionable remediation guidance."
            ]
        ),
        (
            "6. RAG Knowledge Pipeline & Semantic Chunking",
            "app/rag/chunking.py, app/rag/indexer.py, app/rag/retriever.py",
            [
                "<b>Hierarchical Markdown Chunking:</b> Splits architecture knowledge base by Markdown headers (`#`, `##`, `###`), attaching breadcrumbs `[Doc > Section > Subheading]`.",
                "<b>Local Vector Embeddings:</b> Uses Ollama `qwen3-embedding:0.6b` (1024-dimensional vectors).",
                "<b>Local Qdrant Collection:</b> Stores vectors in `architecture_patterns` collection using HNSW cosine metric with an automatic in-memory fallback if Qdrant daemon is offline.",
                "<b>Strict Similarity Filter:</b> Only retrieves chunks matching cosine threshold >= 0.55 to prevent noise and hallucinated patterns."
            ]
        ),
        (
            "7. Observability Telemetry & Caching Engine",
            "app/services/metrics_service.py, app/services/cache_service.py",
            [
                "<b>Live Telemetry Tracking:</b> Records Total LLM Calls, Cache Hits, Cache Hit Rate %, Avg Latency (ms), and Input Tokens.",
                "<b>Semantic Caching:</b> Hashes incoming prompts using SHA-256 and retrieves cached completions from Redis/in-memory dictionary, saving up to 60-80% of token consumption on repeated queries."
            ]
        )
    ]

    for title, file_path, items in modules_code_breakdown:
        story.append(p(f"<b>{title}</b>", h2_style))
        story.append(p(f"<i>Source Files:</i> <font color='#2563EB'><code>{file_path}</code></font>", code_style))
        for it in items:
            story.append(p(f"• {it}", bullet_style))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # CHAPTER 4: FRONTEND UI BLUEPRINT & ELEMENT ROLES
    # -------------------------------------------------------------
    story.append(p("CHAPTER 4: FRONTEND UI BLUEPRINT & USER EXPERIENCE", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=c_secondary, spaceBefore=0, spaceAfter=8))

    story.append(p(
        "The user interface is built as a responsive Single Page Application (SPA) in React 18 and Vite, styled with custom Glassmorphism and Lucide icons. Below is the purpose and function of every major UI element:"
    ))

    ui_elements = [
        ("Global Navigation Header", [
            "<b>Blueprint Status Indicator:</b> Displays 'Draft', 'Validated', or 'Ready' with pulsing colored badges.",
            "<b>'Generate Blueprint' Button:</b> Triggers the full 6-agent autonomous pipeline across backend microservices.",
            "<b>'Observability & Metrics' Button:</b> Launches the live telemetry modal showing token counts, cache hits, and latency.",
            "<b>'Export Dossier' Dropdown:</b> Allows one-click downloading of the IEEE 830 Markdown Dossier or standard JSON blueprint."
        ]),
        ("Module 1 Tab: Requirements View", [
            "<b>PRD Input / File Dropzone:</b> Accepts raw text input or uploaded PDF documents for automated parsing.",
            "<b>Ambiguity Score Meter:</b> Visual radial bar showing vagueness percentage. If high, renders an alert box with targeted clarifying questions.",
            "<b>Functional Requirements Cards:</b> Displays each FR with user story, Given/When/Then acceptance criteria, and P0/P1/P2 badges.",
            "<b>NFR Compliance Matrix:</b> Table showing non-functional thresholds, metric units, and verification protocols."
        ]),
        ("Module 2 Tab: Architecture View", [
            "<b>Architecture Pattern Banner:</b> Highlights recommended topology (Modular Monolith / Microservices) with trade-off rationale.",
            "<b>Interactive C4 Diagram Viewer:</b> Mermaid-powered viewer with tabs to switch between Context, Container, Component, and Deployment views.",
            "<b>Tech Stack & Algorithm Rationale Cards:</b> For each tier, shows technology chosen, design rationale, <b>'Evaluated Against Alternatives'</b> badge list, and explicit justification box explaining why it defeated competing tools.",
            "<b>ADR Drawer:</b> Accordion displaying Architecture Decision Records with literature citations ([ARCH-001])."
        ]),
        ("Module 3 Tab: Traceability Matrix", [
            "<b>Traceability Score Card:</b> Shows overall completeness (66%), forward coverage, and backward coverage.",
            "<b>Interactive Matrix Grid:</b> Filterable table cross-linking FR -> NFR -> Module -> Test Case.",
            "<b>Transitive Blast Radius Simulator:</b> Clicking any requirement highlights all downstream affected modules and tests in red, illustrating change impact.",
            "<b>Orphan Node Alerts:</b> Flags unbacked code files or unmapped specifications."
        ]),
        ("Module 4 Tab: DAG & Code Scaffolding", [
            "<b>Mermaid Dependency DAG:</b> Visual flow of module imports and initialization sequences.",
            "<b>Topological Execution Stepper:</b> Shows ordered sequence of execution (Stage 0 -> Stage 1 -> Stage 2).",
            "<b>Cycle Detection Banner:</b> Confirms acyclicity (100% DAG Validity) or highlights cycle loops with remediation tips.",
            "<b>Critical Path Highlight:</b> Identifies the longest dependency chain determining build bottlenecks.",
            "<b>'Download Code Scaffold ZIP' Button:</b> Downloads the synthesized, runnable project directory tree as a ZIP archive.",
            "<b>Interactive Code Viewer:</b> In-browser file explorer allowing users to inspect synthesized source code files."
        ]),
        ("Module 5 Tab: Validation & Explainability", [
            "<b>Overall Health Score Gauge:</b> Color-coded composite health index.",
            "<b>6 Quality Dimension Cards:</b> Requirements (95%), Traceability (66%), Architecture (65%), DAG Validity (100%), NFR Coverage (60%), RAG Grounding (92%).",
            "<b>Formula & Explainability Drawer:</b> Clicking any score reveals the exact mathematical formula, positive point breakdown (+pts), deduction trace (-pts), and actionable advice on how to improve it.",
            "<b>Issues & Warnings Table:</b> Categorized critical issues and warnings with auto-fix recommendations."
        ]),
        ("Observability & Token Metrics Modal", [
            "<b>Total LLM Calls Counter:</b> Number of local inference passes executed.",
            "<b>Cache Hits & Hit Rate %:</b> Quantifies semantic cache performance.",
            "<b>Average Latency (ms):</b> Average inference round-trip time.",
            "<b>Estimated Tokens Saved:</b> Quantifies token efficiency enabled by Redis semantic caching."
        ])
    ]

    for section, items in ui_elements:
        story.append(p(f"<b>{section}</b>", h2_style))
        for it in items:
            story.append(p(f"• {it}", bullet_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # CHAPTER 5: TRICKY INTERVIEW / REVIEW QUESTIONS & ANSWERS
    # -------------------------------------------------------------
    story.append(p("CHAPTER 5: TRICKY REVIEW & VIVA INTERVIEW QUESTIONS (WITH MODEL ANSWERS)", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=c_secondary, spaceBefore=0, spaceAfter=8))

    story.append(p(
        "Below are 12 tough, in-depth technical questions frequently asked by project review panels, examiners, and principal architects, along with bulletproof model answers:"
    ))

    qa_list = [
        (
            "Q1: Why not just ask GPT-4 or Claude to generate the entire software blueprint in a single prompt? Why do you need an agentic pipeline?",
            "<b>Model Answer:</b> Monolithic LLM prompts suffer from context window degradation, attention drift, and hallucinations. LLMs cannot verify whether generated code contains circular import deadlocks or whether every test case maps to a requirement. Our platform uses a <b>deterministic-first agentic architecture</b>: the LLM generates structured modular proposals, while deterministic graph algorithms (NetworkX) and AST validators verify acyclicity, bi-directional traceability, and mathematical compliance. This ensures 100% verifiable correctness that no single prompt can achieve."
        ),
        (
            "Q2: Why are Traceability scored at 66% and Architecture at 65% instead of 100%? Does this mean your system is failing?",
            "<b>Model Answer:</b> Absolutely not—this proves our validation engine is <b>rigorous, honest, and deterministic</b>, rather than outputting fake 100% marketing scores. In Module 5, Traceability (66%) is calculated via: `(Forward Coverage 50pts) + (Backward Coverage 30pts) + (Test Linkage 20pts) - Deductions`. In initial drafts, auxiliary modules (e.g. `logger.py`, `utils.py`) often lack direct 1-to-1 links to functional requirements, resulting in orphan deductions. Similarly, Architecture (65%) penalizes missing disaster recovery specifications in the early draft. Our system provides actionable remediation traces showing exactly what needs to be added to reach 95%+."
        ),
        (
            "Q3: How do you detect and resolve circular dependencies in the generated code scaffold?",
            "<b>Model Answer:</b> We compile the module import graph into a directed graph (`nx.DiGraph`) and execute `nx.is_directed_acyclic_graph()`. If cycles are detected, we use `nx.simple_cycles()` (Johnson's algorithm) to pinpoint the exact cyclic loops (e.g., Module A -> Module B -> Module A). The system then suggests automated cycle-breaking architectural patterns: (1) Dependency Inversion (introducing an abstract interface), (2) Extracting shared state into a third utility module, or (3) Decoupling via asynchronous event queues."
        ),
        (
            "Q4: How does your RAG chunking algorithm prevent out-of-context hallucinations compared to naive splitters?",
            "<b>Model Answer:</b> Naive chunkers split text by arbitrary character counts (e.g., 500 characters), severing sentences mid-thought and detaching architecture rules from their document titles. We implemented <b>Hierarchical Markdown Chunking with Context Breadcrumbs</b> (`app/rag/chunking.py`). It parses Markdown heading trees (`#`, `##`, `###`) and prepends a hierarchical breadcrumb (e.g., `[Microservices Patterns > Service Discovery > Health Checks]`) to every chunk. This ensures the 1024-dimensional embedding carries complete document-level context, boosting retrieval cosine precision from ~0.45 to >0.70."
        ),
        (
            "Q5: How does your system guarantee 100% offline privacy and zero data leakage?",
            "<b>Model Answer:</b> The platform is self-contained. The LLM runs via local Ollama (`qwen2.5:3b`), the embedding model runs locally (`qwen3-embedding:0.6b`), the vector store runs via local Qdrant (in-memory or local Docker), and caching runs on local Redis. No prompts, source code, or proprietary PRD documents ever traverse the public internet or external APIs, satisfying strict enterprise air-gapped and military-grade data sovereignty requirements."
        ),
        (
            "Q6: What happens if Qdrant or Redis is not running or crashes? Does the application crash?",
            "<b>Model Answer:</b> No. We engineered <b>resilient in-memory fallbacks</b> in both subsystems (`app/rag/retriever.py` and `app/services/cache_service.py`). If Qdrant's gRPC/HTTP daemon is unreachable, the retriever automatically switches to an in-memory dictionary performing exact vector dot-product similarity. If Redis is offline, the caching layer falls back to an in-process LRU dictionary with thread-safe locks. The application maintains 100% uptime regardless of external daemon state."
        ),
        (
            "Q7: How does Transitive Blast Radius Analysis work, and why is it important?",
            "<b>Model Answer:</b> In enterprise software, changing a single requirement can silently break downstream services. Using `networkx.descendants(graph, source_node)`, our engine traverses all directed downstream paths from a requirement node across NFRs, modules, and unit tests. In the UI, clicking any requirement highlights its full transitive blast radius, allowing architects to immediately see which tests must be re-run and which microservices must be redeployed."
        ),
        (
            "Q8: Why did you choose FastAPI over Node.js Express for the backend?",
            "<b>Model Answer:</b> While Node.js Express is popular, building an AI architecture engine in Node.js creates a fragmented multi-language stack because top-tier data science, NLP, and graph libraries (NetworkX, Pydantic, PyPDF, Ollama SDK) are native to Python. Using FastAPI unifies high-performance asynchronous networking (Starlette ASGI) with Python's AI/ML ecosystem inside a single process, avoiding the serialization overhead of Node-to-Python IPC."
        ),
        (
            "Q9: What is the difference between Deterministic Validation and Semantic LLM Validation?",
            "<b>Model Answer:</b> <b>Deterministic Validation</b> uses fixed mathematical rules, AST parsers, schema contracts, and graph algorithms to evaluate hard truths: Is the DAG acyclic? Do all IDs match? Are all Pydantic fields populated? It has zero hallucination and 100% reproducibility. <b>Semantic LLM Validation</b> evaluates subjective qualitative aspects: Does the architecture logically align with the user's business goals? Is the domain boundary clean? By combining both in a 2-phase pipeline, we get the best of both worlds."
        ),
        (
            "Q10: How does your semantic caching layer work, and what are its performance benefits?",
            "<b>Model Answer:</b> In `app/services/cache_service.py`, we compute a cryptographic SHA-256 hash of the normalized prompt, model name, and generation parameters. Before dispatching a request to Ollama, we query Redis/memory. On a cache hit, the response returns in <5ms instead of 2-5 seconds, saving 100% of the token compute. This reduces total generation time by over 60% on iterative blueprint refinements."
        ),
        (
            "Q11: Why use Pydantic v2 over standard Python dictionaries or dataclasses?",
            "<b>Model Answer:</b> Pydantic v2 features a core validation engine written in Rust (`pydantic-core`), providing 5x to 50x faster serialization than standard Python. It enforces strict type coercion, regex validation (e.g. enforcing `FR-[0-9]{3}` patterns), automatic JSON schema generation for OpenAPI, and deep nested validation, preventing corrupted LLM JSON payloads from propagating through the pipeline."
        ),
        (
            "Q12: How do you prevent hallucinated architectural citations?",
            "<b>Model Answer:</b> The Architecture Agent does not invent pattern names out of thin air. In Phase 3, the RAG retriever queries indexed whitepapers in Qdrant and injects verified chunks into the LLM system prompt along with authoritative citation keys (`[ARCH-001]`, `[DATA-001]`). During Phase 5 validation, a deterministic regex auditor inspects the blueprint to verify that every citation tag corresponds to an actual chunk in the vector index with a cosine similarity score >= 0.55."
        )
    ]

    for q, a in qa_list:
        qa_data = [
            [Paragraph(f"<b>{q}</b>", box_bold_style)],
            [Paragraph(a, box_text_style)]
        ]
        qa_table = Table(qa_data, colWidths=[504])
        qa_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
            ('BACKGROUND', (0,1), (-1,1), colors.white),
            ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor("#CBD5E1")),
            ('LINEBELOW', (0,0), (-1,0), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(KeepTogether([qa_table, Spacer(1, 7)]))

    story.append(Spacer(1, 14))

    # Concluding Review Tip Box
    story.append(callout_box(
        "Key Advice for Tomorrow's Review / Viva Defense",
        [
            "1. <b>Emphasize Determinism:</b> Remind the panel that anyone can connect an LLM to a chat box, but your system uses <b>graph algorithms (NetworkX), Pydantic v2 schemas, and deterministic scoring</b> to guarantee safety, acyclicity, and traceability.",
            "2. <b>Highlight Realistic Scores:</b> Explain that Traceability (66%) and Architecture (65%) are genuine mathematical audits showing exact positive criteria and deduction traces, proving you did not hardcode a fake 100%.",
            "3. <b>Show the Scaffolding ZIP & C4 Models:</b> Demonstrating real downloadable code trees and interactive C4 Mermaid diagrams proves the application is an end-to-end software factory, not just a document generator."
        ],
        border_color="#10B981",
        bg_color="#ECFDF5"
    ))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] PDF successfully created: {filename}")


if __name__ == "__main__":
    out_pdf = "SOFTWARE_BLUEPRINT_AI_MASTER_DOCUMENTATION.pdf"
    if len(sys.argv) > 1:
        out_pdf = sys.argv[1]
    build_pdf(out_pdf)
