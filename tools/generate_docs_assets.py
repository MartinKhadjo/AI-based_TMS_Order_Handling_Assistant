# Copyright (c) 2026 Martin Khadjavian. All rights reserved.
# Website: https://martinkhadjavian.com

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import html
import math
import re
import textwrap

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image as RLImage,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
GENERATED = DOCS / "generated"
DIAGRAMS = GENERATED / "diagrams"
MANUAL_MD = DOCS / "manual.md"
MANUAL_PDF = GENERATED / "LogiSense_Demo_Lite_Manual.pdf"
IMPLEMENTATION_MD = DOCS / "implementation_learning_manual.md"
IMPLEMENTATION_PDF = GENERATED / "LogiSense_Demo_Lite_Implementation_Learning_Manual.pdf"
COPYRIGHT_NOTICE = "Copyright (c) 2026 Martin Khadjavian. All rights reserved."
COPYRIGHT_WEBSITE = "https://martinkhadjavian.com"

BG = "#f4f7f6"
CARD = "#ffffff"
CARD_ALT = "#fbfdfc"
TEAL = "#177e89"
TEAL_LIGHT = "#e8f2ef"
DARK = "#15201c"
TEXT = "#24332f"
MUTED = "#66736f"
BORDER = "#9fc8bf"
YELLOW = "#fff0cf"
RED = "#fde7e3"
GREEN = "#e5f6ed"


@dataclass(frozen=True)
class Box:
    x: int
    y: int
    w: int
    h: int
    title: str
    lines: tuple[str, ...] = ()
    fill: str = CARD
    accent: str = TEAL

    @property
    def left(self) -> tuple[int, int]:
        return (self.x, self.y + self.h // 2)

    @property
    def right(self) -> tuple[int, int]:
        return (self.x + self.w, self.y + self.h // 2)

    @property
    def top(self) -> tuple[int, int]:
        return (self.x + self.w // 2, self.y)

    @property
    def bottom(self) -> tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h)

    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h // 2)


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    candidates = []
    if mono:
        candidates.extend(
            [
                Path("C:/Windows/Fonts/consola.ttf"),
                Path("C:/Windows/Fonts/cour.ttf"),
            ]
        )
    elif bold:
        candidates.extend(
            [
                Path("C:/Windows/Fonts/segoeuib.ttf"),
                Path("C:/Windows/Fonts/arialbd.ttf"),
            ]
        )
    else:
        candidates.extend(
            [
                Path("C:/Windows/Fonts/segoeui.ttf"),
                Path("C:/Windows/Fonts/arial.ttf"),
            ]
        )
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


FONT_TITLE = font(52, bold=True)
FONT_SUBTITLE = font(26, bold=True)
FONT_H = font(24, bold=True)
FONT_BODY = font(21)
FONT_SMALL = font(18)
FONT_MONO = font(17, mono=True)


def new_canvas(width: int, height: int, title: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    draw.text((50, 35), title, fill=DARK, font=FONT_TITLE)
    draw.line((50, 105, width - 50, 105), fill="#cddbd7", width=3)
    return image, draw


def draw_footer(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    text = f"{COPYRIGHT_NOTICE}  {COPYRIGHT_WEBSITE}"
    bbox = draw.textbbox((0, 0), text, font=FONT_SMALL)
    draw.text(
        ((width - (bbox[2] - bbox[0])) // 2, height - 42),
        text,
        fill=MUTED,
        font=FONT_SMALL,
    )


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), candidate, font=font_obj)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_box(draw: ImageDraw.ImageDraw, box: Box) -> None:
    xy = (box.x, box.y, box.x + box.w, box.y + box.h)
    draw.rounded_rectangle(xy, radius=18, fill=box.fill, outline=BORDER, width=3)
    draw.rounded_rectangle((box.x, box.y, box.x + 12, box.y + box.h), radius=8, fill=box.accent)
    draw.text((box.x + 28, box.y + 18), box.title, fill=DARK, font=FONT_H)
    y = box.y + 58
    for line in box.lines:
        for wrapped in wrap_text(draw, line, FONT_BODY, box.w - 54):
            draw.text((box.x + 28, y), wrapped, fill=TEXT, font=FONT_BODY)
            y += 28


def arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    label: str | None = None,
    color: str = TEAL,
    width: int = 4,
) -> None:
    draw.line((start, end), fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    size = 16
    points = [
        end,
        (
            int(end[0] - size * math.cos(angle - math.pi / 7)),
            int(end[1] - size * math.sin(angle - math.pi / 7)),
        ),
        (
            int(end[0] - size * math.cos(angle + math.pi / 7)),
            int(end[1] - size * math.sin(angle + math.pi / 7)),
        ),
    ]
    draw.polygon(points, fill=color)
    if label:
        mx = (start[0] + end[0]) // 2
        my = (start[1] + end[1]) // 2
        text_bbox = draw.textbbox((0, 0), label, font=FONT_SMALL)
        pad = 7
        bg_xy = (
            mx - (text_bbox[2] - text_bbox[0]) // 2 - pad,
            my - 17,
            mx + (text_bbox[2] - text_bbox[0]) // 2 + pad,
            my + 14,
        )
        draw.rounded_rectangle(bg_xy, radius=8, fill=BG)
        draw.text((bg_xy[0] + pad, bg_xy[1] + 4), label, fill=DARK, font=FONT_SMALL)


def save(image: Image.Image, name: str) -> Path:
    DIAGRAMS.mkdir(parents=True, exist_ok=True)
    path = DIAGRAMS / name
    draw_footer(ImageDraw.Draw(image), image.width, image.height)
    image.save(path, "PNG")
    return path


def diagram_system_architecture() -> Path:
    image, draw = new_canvas(1800, 1160, "System Architecture")
    boxes = {
        "user": Box(80, 190, 300, 130, "User", ("Dispatcher / interview demo",)),
        "frontend": Box(80, 450, 330, 150, "Svelte Frontend", ("Dashboard", "AI assistant", "Operational query")),
        "api": Box(520, 450, 320, 150, "Django REST API", ("ViewSets", "AI endpoints", "Status endpoint")),
        "services": Box(960, 450, 350, 170, "Domain Services", ("OrderService", "ValidationService", "ToolCallingService")),
        "db": Box(1420, 450, 300, 150, "Database", ("PostgreSQL in Docker", "SQLite for quick local dev"), fill=TEAL_LIGHT),
        "ai": Box(520, 750, 320, 150, "AI Layer", ("Mock extraction", "Future LLM adapter")),
        "log": Box(960, 760, 350, 130, "AIExtractionLog", ("Raw input", "Extracted JSON", "Validation issues"), fill=YELLOW),
    }
    for box in boxes.values():
        draw_box(draw, box)
    arrow(draw, boxes["user"].bottom, boxes["frontend"].top, "uses")
    arrow(draw, boxes["frontend"].right, boxes["api"].left, "JSON HTTP")
    arrow(draw, boxes["api"].right, boxes["services"].left, "business actions")
    arrow(draw, boxes["services"].right, boxes["db"].left, "ORM")
    arrow(draw, boxes["api"].bottom, boxes["ai"].top, "extract")
    arrow(draw, boxes["ai"].right, boxes["log"].left, "audit")
    arrow(draw, boxes["log"].right, (1420, 820), "persist")
    arrow(draw, (1420, 820), boxes["db"].bottom, color=TEAL)
    return save(image, "01_system_architecture.png")


def diagram_backend_components() -> Path:
    image, draw = new_canvas(1800, 1180, "Backend Components")
    boxes = [
        Box(80, 210, 320, 150, "URLs / Router", ("tms/urls.py", "DRF DefaultRouter")),
        Box(520, 210, 330, 150, "Views", ("ViewSets", "APIView endpoints")),
        Box(970, 210, 330, 150, "Serializers", ("JSON representation", "Nested details")),
        Box(1420, 210, 300, 150, "Models", ("Django ORM", "Domain entities")),
        Box(300, 560, 340, 150, "AIExtractionService", ("Freitext -> Draft", "Mock provider")),
        Box(760, 560, 340, 150, "ValidationService", ("Required fields", "VIN/date checks")),
        Box(1220, 560, 340, 150, "OrderService", ("Create customer", "Vehicle", "TransportOrder")),
        Box(760, 850, 340, 150, "ToolCallingService", ("Operational query", "Tool selection")),
        Box(1420, 850, 300, 150, "Database", ("Orders", "Vehicles", "AI logs"), fill=TEAL_LIGHT),
    ]
    for box in boxes:
        draw_box(draw, box)
    for left, right in [(0, 1), (1, 2), (2, 3)]:
        arrow(draw, boxes[left].right, boxes[right].left)
    arrow(draw, boxes[1].bottom, boxes[4].top, "extract")
    arrow(draw, boxes[4].right, boxes[5].left, "validate")
    arrow(draw, boxes[1].bottom, boxes[6].top, "confirm draft")
    arrow(draw, boxes[1].bottom, boxes[7].top, "query")
    arrow(draw, boxes[6].right, boxes[8].left, "write")
    arrow(draw, boxes[7].right, boxes[8].left, "read")
    return save(image, "02_backend_components.png")


def diagram_frontend_components() -> Path:
    image, draw = new_canvas(1800, 1080, "Frontend Components")
    boxes = [
        Box(720, 180, 360, 150, "App.svelte", ("Loads dashboard data", "Coordinates refreshes")),
        Box(720, 470, 360, 150, "lib/api.ts", ("Typed fetch wrapper", "Backend base URL")),
        Box(80, 760, 310, 150, "Order List", ("Status changes", "Tracking preview")),
        Box(430, 760, 310, 150, "Vehicle List", ("Fleet state", "Locations")),
        Box(780, 760, 310, 150, "AI Assistant", ("Extract draft", "Confirm draft")),
        Box(1130, 760, 310, 150, "Tool Query", ("Run tool route", "Show answer/data")),
        Box(1480, 760, 260, 150, "Manual Form", ("Classic order creation",)),
    ]
    for box in boxes:
        draw_box(draw, box)
    arrow(draw, boxes[0].bottom, boxes[1].top, "uses")
    for box in boxes[2:]:
        arrow(draw, boxes[0].bottom, box.top)
        arrow(draw, box.top, boxes[1].bottom, "API", color="#4f8e85")
    return save(image, "03_frontend_components.png")


def diagram_domain_model() -> Path:
    image, draw = new_canvas(1900, 1280, "Domain Model / UML")
    boxes = {
        "customer": Box(80, 230, 350, 230, "Customer", ("id", "name", "contact_email", "company_type")),
        "vehicle": Box(80, 560, 350, 260, "Vehicle", ("vin", "brand", "model", "status", "current_location")),
        "carrier": Box(80, 900, 350, 210, "Carrier", ("name", "contact_email", "phone", "active")),
        "order": Box(650, 500, 480, 330, "TransportOrder", ("customer, vehicle, carrier", "pickup_location", "delivery_location", "requested dates", "status, priority", "created_by_ai")),
        "tracking": Box(1400, 240, 390, 230, "TrackingEvent", ("event_type", "location", "timestamp", "description")),
        "invoice": Box(1400, 570, 390, 230, "Invoice", ("invoice_number", "amount", "currency", "status")),
        "log": Box(1400, 900, 390, 230, "AIExtractionLog", ("raw_input", "extracted_json", "confidence_score", "validation_errors")),
    }
    for box in boxes.values():
        draw_box(draw, box)
    arrow(draw, boxes["customer"].right, (650, 585), "1 to many")
    arrow(draw, boxes["vehicle"].right, boxes["order"].left, "1 to many")
    arrow(draw, boxes["carrier"].right, (650, 750), "optional")
    arrow(draw, boxes["order"].right, boxes["tracking"].left, "events")
    arrow(draw, boxes["order"].right, boxes["invoice"].left, "invoice")
    arrow(draw, boxes["order"].right, boxes["log"].left, "audit")
    return save(image, "04_domain_model_uml.png")


def sequence_diagram(name: str, title: str, participants: list[str], messages: list[tuple[int, int, str]]) -> Path:
    width = 1900
    height = 300 + len(messages) * 82
    image, draw = new_canvas(width, height, title)
    left_margin = 90
    spacing = (width - 2 * left_margin) // (len(participants) - 1)
    xs = [left_margin + i * spacing for i in range(len(participants))]
    top = 170
    bottom = height - 80
    for x, participant in zip(xs, participants):
        box = Box(x - 120, top, 240, 70, participant)
        draw_box(draw, box)
        draw.line((x, top + 70, x, bottom), fill="#b7cbc6", width=3)
    y = top + 135
    for source, target, label in messages:
        start = (xs[source], y)
        end = (xs[target], y)
        if source == target:
            draw.arc((xs[source] - 20, y - 8, xs[source] + 130, y + 48), 270, 90, fill=TEAL, width=4)
            draw.text((xs[source] + 30, y - 30), label, fill=DARK, font=FONT_SMALL)
        else:
            arrow(draw, start, end, label, color=TEAL if source < target else "#4f8e85")
        y += 82
    return save(image, name)


def diagram_sequences() -> list[Path]:
    paths = []
    paths.append(
        sequence_diagram(
            "05_sequence_ai_extraction.png",
            "Sequence: AI Extraction",
            ["User", "Frontend", "Django API", "AI Service", "Validation", "Database"],
            [
                (0, 1, "paste customer request"),
                (1, 2, "POST /api/ai/extract-order/"),
                (2, 3, "extract_transport_order(message)"),
                (3, 3, "mock parse / future LLM call"),
                (3, 4, "validate_draft(draft)"),
                (4, 3, "missing fields, warnings"),
                (3, 2, "draft + confidence"),
                (2, 5, "insert AIExtractionLog"),
                (2, 1, "draft response"),
                (1, 0, "editable draft"),
            ],
        )
    )
    paths.append(
        sequence_diagram(
            "06_sequence_draft_confirmation.png",
            "Sequence: Draft Confirmation",
            ["User", "Frontend", "Django API", "Validation", "OrderService", "Database"],
            [
                (0, 1, "confirm reviewed draft"),
                (1, 2, "POST /api/ai/create-order-draft/"),
                (2, 3, "validate_draft(draft)"),
                (3, 2, "valid"),
                (2, 4, "create_order_from_draft"),
                (4, 5, "get_or_create Customer"),
                (4, 5, "get_or_create Vehicle"),
                (4, 5, "create TransportOrder"),
                (4, 5, "create TrackingEvent + AI log"),
                (4, 2, "TransportOrder"),
                (2, 1, "created order JSON"),
                (1, 0, "queue refreshed"),
            ],
        )
    )
    paths.append(
        sequence_diagram(
            "07_sequence_tool_calling.png",
            "Sequence: Tool Calling",
            ["User", "Frontend", "Django API", "Tool Service", "Database"],
            [
                (0, 1, "ask operational question"),
                (1, 2, "POST /api/ai/query-orders/"),
                (2, 3, "answer_operational_query"),
                (3, 3, "route intent to tool"),
                (3, 4, "query operational data"),
                (4, 3, "result rows"),
                (3, 2, "tool + data + answer"),
                (2, 1, "response"),
                (1, 0, "answer + raw data"),
            ],
        )
    )
    return paths


def diagram_state_machine() -> Path:
    image, draw = new_canvas(1800, 1050, "Status State Machines")
    states1 = [
        Box(120, 250, 230, 90, "available", fill=GREEN),
        Box(470, 250, 230, 90, "assigned", fill=YELLOW),
        Box(820, 250, 230, 90, "in_transit", fill=TEAL_LIGHT),
        Box(1170, 250, 230, 90, "delivered", fill=GREEN),
        Box(470, 480, 230, 90, "blocked", fill=RED),
    ]
    states2 = [
        Box(120, 720, 210, 90, "open", fill=GREEN),
        Box(430, 720, 210, 90, "planned", fill=YELLOW),
        Box(740, 720, 210, 90, "in_transit", fill=TEAL_LIGHT),
        Box(1050, 720, 210, 90, "delivered", fill=GREEN),
        Box(1360, 720, 210, 90, "cancelled", fill=RED),
    ]
    draw.text((120, 185), "Vehicle status", fill=DARK, font=FONT_SUBTITLE)
    draw.text((120, 655), "Transport order status", fill=DARK, font=FONT_SUBTITLE)
    for box in states1 + states2:
        draw_box(draw, box)
    for a, b in [(0, 1), (1, 2), (2, 3)]:
        arrow(draw, states1[a].right, states1[b].left)
    arrow(draw, states1[0].bottom, states1[4].left, "block")
    arrow(draw, states1[4].right, states1[1].bottom, "release")
    for a, b in [(0, 1), (1, 2), (2, 3)]:
        arrow(draw, states2[a].right, states2[b].left)
    arrow(draw, states2[0].top, states2[4].top, "cancel", color="#b55345")
    return save(image, "08_status_state_machines.png")


def diagram_deployment() -> Path:
    image, draw = new_canvas(1800, 1120, "Deployment")
    draw.rounded_rectangle((70, 170, 1730, 1010), radius=30, fill="#eef4f2", outline=BORDER, width=4)
    draw.text((110, 205), "Developer Machine", fill=DARK, font=FONT_SUBTITLE)
    draw.rounded_rectangle((150, 300, 1650, 910), radius=26, fill="#ffffff", outline=BORDER, width=4)
    draw.text((190, 335), "Docker Compose", fill=DARK, font=FONT_SUBTITLE)
    frontend = Box(230, 480, 350, 170, "frontend container", ("Vite / Svelte", "port 5173"))
    backend = Box(725, 480, 350, 170, "backend container", ("Django API", "port 8000 or 8010 local"))
    db = Box(1220, 480, 350, 170, "db container", ("PostgreSQL", "port 5432"), fill=TEAL_LIGHT)
    for box in [frontend, backend, db]:
        draw_box(draw, box)
    arrow(draw, frontend.right, backend.left, "HTTP JSON")
    arrow(draw, backend.right, db.left, "SQL / ORM")
    return save(image, "09_deployment_diagram.png")


def generate_diagrams() -> list[Path]:
    paths = [
        diagram_system_architecture(),
        diagram_backend_components(),
        diagram_frontend_components(),
        diagram_domain_model(),
        *diagram_sequences(),
        diagram_state_machine(),
        diagram_deployment(),
    ]
    return paths


def markdown_inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", escaped)
    return escaped


def image_flowable(path: Path, max_width: float) -> KeepTogether:
    with Image.open(path) as image:
        width, height = image.size
    ratio = height / width
    return KeepTogether(
        [
            Spacer(1, 0.2 * cm),
            RLImage(str(path), width=max_width, height=max_width * ratio),
            Spacer(1, 0.35 * cm),
        ]
    )


def paragraph_from_buffer(buffer: list[str], style: ParagraphStyle, story: list) -> None:
    if not buffer:
        return
    text = " ".join(line.strip() for line in buffer if line.strip())
    if text:
        story.append(Paragraph(markdown_inline(text), style))
        story.append(Spacer(1, 0.12 * cm))
    buffer.clear()


def table_from_lines(lines: list[str], styles) -> Table:
    rows: list[list[Paragraph]] = []
    for line in lines:
        if re.match(r"^\s*\|?\s*:?-{3,}", line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append([Paragraph(markdown_inline(cell), styles["TableCell"]) for cell in cells])
    col_count = max(len(row) for row in rows)
    for row in rows:
        while len(row) < col_count:
            row.append(Paragraph("", styles["TableCell"]))
    table = Table(rows, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(TEAL_LIGHT)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor(DARK)),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#c7d8d4")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def build_pdf(
    source_path: Path,
    output_path: Path,
    cover_title: str,
    cover_subtitle: str,
    cover_description: str,
    diagram_by_mermaid_index: list[Path] | None = None,
) -> Path:
    GENERATED.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleMain", parent=styles["Title"], fontSize=28, leading=34, textColor=colors.HexColor(DARK), alignment=TA_CENTER, spaceAfter=16))
    styles.add(ParagraphStyle(name="Subtitle", parent=styles["BodyText"], fontSize=12, leading=16, textColor=colors.HexColor(MUTED), alignment=TA_CENTER, spaceAfter=20))
    styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontSize=20, leading=24, textColor=colors.HexColor(DARK), spaceBefore=16, spaceAfter=8))
    styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontSize=15, leading=19, textColor=colors.HexColor(TEAL), spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle(name="H3x", parent=styles["Heading3"], fontSize=12, leading=15, textColor=colors.HexColor(DARK), spaceBefore=8, spaceAfter=5))
    styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontSize=9.5, leading=13.2, spaceAfter=4))
    styles.add(ParagraphStyle(name="Bulletx", parent=styles["BodyText"], leftIndent=14, bulletIndent=4, fontSize=9.5, leading=13.2, spaceAfter=3))
    styles.add(ParagraphStyle(name="CodeBlock", parent=styles["Code"], fontSize=7.6, leading=9.3, leftIndent=4, rightIndent=4, spaceBefore=4, spaceAfter=7))
    styles.add(ParagraphStyle(name="TableCell", parent=styles["BodyText"], fontSize=7.5, leading=9.2))

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=1.35 * cm,
        leftMargin=1.35 * cm,
        topMargin=1.3 * cm,
        bottomMargin=1.3 * cm,
        title=cover_title,
        author="Codex",
    )
    max_width = A4[0] - doc.leftMargin - doc.rightMargin
    story: list = [
        Spacer(1, 4 * cm),
        Paragraph(cover_title, styles["TitleMain"]),
        Paragraph(cover_subtitle, styles["Subtitle"]),
        Paragraph(cover_description, styles["Subtitle"]),
        Paragraph(
            f"{COPYRIGHT_NOTICE}<br/>{COPYRIGHT_WEBSITE}",
            styles["Subtitle"],
        ),
        PageBreak(),
    ]

    if diagram_by_mermaid_index is None:
        diagram_by_mermaid_index = []
    mermaid_index = 0
    in_code = False
    code_lang = ""
    code_lines: list[str] = []
    paragraph_buffer: list[str] = []
    table_lines: list[str] = []

    lines = source_path.read_text(encoding="utf-8").splitlines()
    for line in lines:
        if line.startswith("```"):
            if not in_code:
                paragraph_from_buffer(paragraph_buffer, styles["Bodyx"], story)
                if table_lines:
                    story.append(table_from_lines(table_lines, styles))
                    story.append(Spacer(1, 0.25 * cm))
                    table_lines.clear()
                in_code = True
                code_lang = line.strip().removeprefix("```")
                code_lines = []
            else:
                if code_lang == "mermaid":
                    if mermaid_index < len(diagram_by_mermaid_index):
                        story.append(image_flowable(diagram_by_mermaid_index[mermaid_index], max_width))
                    mermaid_index += 1
                else:
                    code_text = "\n".join(code_lines)
                    story.append(Preformatted(code_text, styles["CodeBlock"]))
                in_code = False
                code_lang = ""
                code_lines = []
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not line.strip():
            paragraph_from_buffer(paragraph_buffer, styles["Bodyx"], story)
            if table_lines:
                story.append(table_from_lines(table_lines, styles))
                story.append(Spacer(1, 0.25 * cm))
                table_lines.clear()
            continue

        if line.lstrip().startswith("|") and "|" in line.rstrip()[1:]:
            paragraph_from_buffer(paragraph_buffer, styles["Bodyx"], story)
            table_lines.append(line)
            continue

        if table_lines:
            story.append(table_from_lines(table_lines, styles))
            story.append(Spacer(1, 0.25 * cm))
            table_lines.clear()

        image_match = re.match(r"^!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)$", line.strip())
        if image_match:
            paragraph_from_buffer(paragraph_buffer, styles["Bodyx"], story)
            raw_path = image_match.group("path")
            image_path = (source_path.parent / raw_path).resolve()
            if image_path.exists():
                story.append(image_flowable(image_path, max_width))
            continue

        heading_match = re.match(r"^(#{1,4})\s+(.*)$", line)
        if heading_match:
            paragraph_from_buffer(paragraph_buffer, styles["Bodyx"], story)
            level = len(heading_match.group(1))
            text = markdown_inline(heading_match.group(2))
            style = styles["H1x"] if level == 1 else styles["H2x"] if level == 2 else styles["H3x"]
            story.append(Paragraph(text, style))
            continue

        bullet_match = re.match(r"^\s*[-*]\s+(.*)$", line)
        if bullet_match:
            paragraph_from_buffer(paragraph_buffer, styles["Bodyx"], story)
            story.append(Paragraph(markdown_inline(bullet_match.group(1)), styles["Bulletx"], bulletText="-"))
            continue

        paragraph_buffer.append(line)

    paragraph_from_buffer(paragraph_buffer, styles["Bodyx"], story)
    if table_lines:
        story.append(table_from_lines(table_lines, styles))

    def add_page_number(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor(MUTED))
        canvas.drawString(1.35 * cm, 0.7 * cm, f"{COPYRIGHT_NOTICE} {COPYRIGHT_WEBSITE}")
        canvas.drawRightString(A4[0] - 1.35 * cm, 0.7 * cm, f"Page {document.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return output_path


def write_index(diagrams: list[Path], pdfs: list[Path]) -> Path:
    index = GENERATED / "README.md"
    lines = [
        "# Generated Documentation Assets",
        "",
        f"{COPYRIGHT_NOTICE}",
        "",
        f"Website: [{COPYRIGHT_WEBSITE}]({COPYRIGHT_WEBSITE})",
        "",
        "This folder contains compiled artifacts generated from the project documentation.",
        "",
        "- PDF manuals:",
        "",
    ]
    for pdf in pdfs:
        lines.append(f"  - [{pdf.name}]({pdf.name})")
    lines.extend(
        [
            "",
            "- PNG diagrams:",
            "",
        ]
    )
    for path in diagrams:
        lines.append(f"  - [{path.name}](diagrams/{path.name})")
    lines.extend(
        [
            "",
            "Regenerate with:",
            "",
            "```powershell",
            ".\\backend\\.venv\\Scripts\\python tools\\generate_docs_assets.py",
            "```",
        ]
    )
    index.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return index


def main() -> None:
    diagrams = generate_diagrams()
    manual_pdf = build_pdf(
        MANUAL_MD,
        MANUAL_PDF,
        "LogiSense Demo Lite",
        "AI-native TMS Order Handling Assistant",
        "Handbuch zum Verstehen, Erklaeren und Rekonstruieren der Architektur.",
        [
            DIAGRAMS / "01_system_architecture.png",
            DIAGRAMS / "04_domain_model_uml.png",
            DIAGRAMS / "02_backend_components.png",
            DIAGRAMS / "03_frontend_components.png",
            DIAGRAMS / "05_sequence_ai_extraction.png",
            DIAGRAMS / "06_sequence_draft_confirmation.png",
            DIAGRAMS / "07_sequence_tool_calling.png",
            DIAGRAMS / "08_status_state_machines.png",
            DIAGRAMS / "08_status_state_machines.png",
        ],
    )
    implementation_pdf = build_pdf(
        IMPLEMENTATION_MD,
        IMPLEMENTATION_PDF,
        "LogiSense Demo Lite",
        "Implementation Learning Manual",
        "Code-level guide to rebuild the architecture without AI assistance.",
        [
            DIAGRAMS / "01_system_architecture.png",
            DIAGRAMS / "02_backend_components.png",
        ],
    )
    pdfs = [manual_pdf, implementation_pdf]
    index = write_index(diagrams, pdfs)
    print("Generated diagrams:")
    for diagram in diagrams:
        print(f" - {diagram}")
    print("Generated PDFs:")
    for pdf in pdfs:
        print(f" - {pdf}")
    print(f"Generated index: {index}")


if __name__ == "__main__":
    main()
