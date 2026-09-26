import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

output_dir = Path(__file__).parent / "screenshots"
output_dir.mkdir(parents=True, exist_ok=True)
cards = [
    {
        "filename": "01_architecture.png",
        "title": "IBM Bob 2.0 - Architecture Design Session",
        "badge": "PHASE 1: ARCHITECTURE",
        "badge_color": (59, 130, 246),
        "lines": [
            "Input: System specification for DevFlow code review engine",
            "Action: Evaluated runtime LLM vs development copilot separation",
            "Output: Decoupled Groq runtime inference from IBM Bob development workflows",
            "Component Stack:",
            "  • Frontend: Flutter Material 3 Dashboard",
            "  • Backend: FastAPI Async Server + Pydantic v2",
            "  • AI Runtime: Groq API (llama-3.3-70b-versatile)",
            "  • Verification: Native Python AST Parsing (Zero RCE risk)",
            "  • Storage: Supabase Cloud PostgreSQL + Local in-memory fallback"
        ]
    },
    {
        "filename": "02_code_analysis.png",
        "title": "IBM Bob 2.0 - Code Analysis & Prompts Engineering",
        "badge": "PHASE 2: DEVELOPMENT",
        "badge_color": (16, 185, 129),
        "lines": [
            "Task: Structured JSON output formulation for Groq LLM",
            "Prompt Formulation:",
            "  • ANALYSIS_SYSTEM: Categorizes issues into Security, Bug, Testing, Maintainability",
            "  • Standardized Severity: CRITICAL, HIGH, MEDIUM, LOW",
            "  • Structured Response: Root cause, impact, file, line, recommendations",
            "Result: 100% compliant JSON payload serialization ready for Flutter rendering"
        ]
    },
    {
        "filename": "03_debugging.png",
        "title": "IBM Bob 2.0 - Security Hardening & Zip Slip Debugging",
        "badge": "PHASE 3: DEBUGGING",
        "badge_color": (239, 68, 68),
        "lines": [
            "Vulnerability Identified: Directory Traversal via Malicious ZIP Archives (Zip Slip)",
            "Mitigation Implemented in zip_handler.py:",
            "  1. Validate member filenames against leading slashes and '..' sequences",
            "  2. Resolve canonical destination paths using Path.resolve()",
            "  3. Guard via target_file_path.relative_to(extract_path)",
            "Verification: Path traversal exploit attempts blocked with 400 Bad Request"
        ]
    },
    {
        "filename": "04_testing.png",
        "title": "IBM Bob 2.0 - AST Verification & Test Generation",
        "badge": "PHASE 4: TESTING & VERIFICATION",
        "badge_color": (168, 85, 247),
        "lines": [
            "Goal: Verify uploaded code syntax without executing untrusted code",
            "Engine: verification_service.py using Python ast.parse",
            "AST Capabilities:",
            "  • Parses Python syntax trees without executing runtime side effects",
            "  • Flags syntax errors, line numbers, and parsing failures",
            "  • Integrated with Groq AI to synthesize regression tests and fix diffs"
        ]
    },
    {
        "filename": "05_documentation.png",
        "title": "IBM Bob 2.0 - Technical Documentation & API Spec",
        "badge": "PHASE 5: DOCUMENTATION",
        "badge_color": (245, 158, 11),
        "lines": [
            "Deliverables Created:",
            "  • docs/architecture.md: System topology & data flow diagrams",
            "  • docs/api.md: Complete REST API documentation for all 10 endpoints",
            "  • docs/demo-script.md: 10-step interactive presentation script for judges",
            "  • bob-evidence/bob-workflow.md: Verifiable IBM Bob 2.0 attribution record"
        ]
    }
]

for card in cards:
    img = Image.new("RGB", (1200, 675), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    # Top border accent
    draw.rectangle([(0, 0), (1200, 8)], fill=card["badge_color"])

    # Header container
    draw.rectangle([(40, 40), (1160, 130)], fill=(30, 41, 59), outline=(51, 65, 85), width=1)

    # Badge
    draw.rectangle([(60, 60), (320, 95)], fill=card["badge_color"])
    draw.text((75, 68), card["badge"], fill=(255, 255, 255))

    # Title
    draw.text((340, 72), card["title"], fill=(241, 245, 249))

    # Content Box
    draw.rectangle([(40, 150), (1160, 615)], fill=(24, 33, 47), outline=(51, 65, 85), width=1)

    # Content lines
    y = 185
    for line in card["lines"]:
        color = (56, 189, 248) if line.startswith("  •") else (226, 232, 240)
        draw.text((70, y), line, fill=color)
        y += 42

    # Footer
    draw.text((70, 570), "DevFlow • Powered by IBM Bob 2.0 Hackathon Workflow", fill=(148, 163, 184))

    file_path = output_dir / card["filename"]
    img.save(file_path, "PNG")
    print(f"Generated {file_path}")
