from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "share"
LOGO = ROOT / "branding" / "whitedns-tg-logo-approved.png"

BLUE = "147D91"
DARK = "163440"
TEAL = "0F9D94"
LIGHT_BLUE = "E8F3F5"
LIGHT_GRAY = "F3F6F7"
GOLD = "FFF4D6"
RED = "FCE8E6"
MUTED = "5B6B73"
WHITE = "FFFFFF"

DNS_ROWS = [
    ("A", "kws1", "149.154.175.50", "Proxied", "Auto"),
    ("A", "kws2", "149.154.167.51", "Proxied", "Auto"),
    ("A", "kws3", "149.154.175.100", "Proxied", "Auto"),
    ("A", "kws4", "149.154.167.91", "Proxied", "Auto"),
    ("A", "kws5", "149.154.171.5", "Proxied", "Auto"),
    ("A", "kws203", "91.105.192.100", "Proxied", "Auto"),
]


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=80, start=120, bottom=80, end=120):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for name, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{name}"))
        if node is None:
            node = OxmlElement(f"w:{name}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_geometry(table, widths_dxa, rtl=False):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(sum(widths_dxa)))
    tbl_w.set(qn("w:type"), "dxa")
    tbl_ind = tbl_pr.find(qn("w:tblInd"))
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd")
        tbl_pr.append(tbl_ind)
    tbl_ind.set(qn("w:w"), "120")
    tbl_ind.set(qn("w:type"), "dxa")
    layout = tbl_pr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tbl_pr.append(layout)
    layout.set(qn("w:type"), "fixed")
    if rtl:
        bidi = tbl_pr.find(qn("w:bidiVisual"))
        if bidi is None:
            bidi = OxmlElement("w:bidiVisual")
            tbl_pr.append(bidi)
        bidi.set(qn("w:val"), "1")
    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths_dxa:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(widths_dxa[idx]))
            tc_w.set(qn("w:type"), "dxa")
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def mark_header_row(row):
    tr_pr = row._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    tr_pr.append(repeat)


def set_picture_alt(shape, text):
    doc_pr = shape._inline.docPr
    doc_pr.set("descr", text)
    doc_pr.set("title", text)


def set_run_font(run, name="Calibri", size=11, color=None, bold=None, italic=None):
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:cs"), name)
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic


def set_rtl(paragraph):
    p_pr = paragraph._p.get_or_add_pPr()
    bidi = p_pr.find(qn("w:bidi"))
    if bidi is None:
        bidi = OxmlElement("w:bidi")
        p_pr.append(bidi)
    bidi.set(qn("w:val"), "1")
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT


def setup_style(style, font, size, color=None, bold=None, before=0, after=6, line=1.25, rtl=False):
    style.font.name = font
    style._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), font)
    style._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), font)
    style._element.get_or_add_rPr().rFonts.set(qn("w:cs"), font)
    style.font.size = Pt(size)
    if color:
        style.font.color.rgb = RGBColor.from_string(color)
    if bold is not None:
        style.font.bold = bold
    fmt = style.paragraph_format
    fmt.space_before = Pt(before)
    fmt.space_after = Pt(after)
    fmt.line_spacing = line
    if rtl:
        p_pr = style._element.get_or_add_pPr()
        bidi = OxmlElement("w:bidi")
        bidi.set(qn("w:val"), "1")
        p_pr.append(bidi)


def add_page_number(paragraph, rtl=False):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run("صفحه " if rtl else "Page ")
    set_run_font(run, size=9, color=MUTED)
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    paragraph._p.append(fld)


def configure_document(doc, rtl=False):
    section = doc.sections[0]
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)
    section.header_distance = Inches(0.35)
    section.footer_distance = Inches(0.35)

    font = "Arial" if rtl else "Calibri"
    setup_style(doc.styles["Normal"], font, 10.5 if rtl else 10.7, after=5, line=1.20, rtl=rtl)
    setup_style(doc.styles["Title"], font, 22, DARK, True, after=4, line=1.0, rtl=rtl)
    setup_style(doc.styles["Subtitle"], font, 11, MUTED, False, after=14, line=1.1, rtl=rtl)
    setup_style(doc.styles["Heading 1"], font, 15.5, BLUE, True, before=16, after=7, line=1.05, rtl=rtl)
    setup_style(doc.styles["Heading 2"], font, 12.5, DARK, True, before=10, after=4, line=1.05, rtl=rtl)
    setup_style(doc.styles["Heading 3"], font, 11.5, DARK, True, before=8, after=3, line=1.05, rtl=rtl)

    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT if rtl else WD_ALIGN_PARAGRAPH.LEFT
    if rtl:
        set_rtl(hp)
    hr = hp.add_run("WhiteDns TG  |  Private Front Setup")
    set_run_font(hr, font, 8.5, MUTED, True)

    footer = section.footer
    fp = footer.paragraphs[0]
    add_page_number(fp, rtl)

    props = doc.core_properties
    props.author = "WhiteDns TG"
    props.company = "WhiteDns TG"
    props.subject = "Private Cloudflare front setup guide"
    props.keywords = "WhiteDns TG, Telegram, private front, Cloudflare, DNS"


def add_title(doc, title, subtitle, rtl=False):
    if rtl:
        p = doc.add_paragraph()
        set_rtl(p)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        shape = p.add_run().add_picture(str(LOGO), width=Inches(0.82))
        set_picture_alt(shape, "WhiteDns TG logo")
        p.paragraph_format.space_after = Pt(4)
        p = doc.add_paragraph()
        set_rtl(p)
        r = p.add_run(title)
        set_run_font(r, "Arial", 21, DARK, True)
        p.paragraph_format.space_after = Pt(3)
        p = doc.add_paragraph()
        set_rtl(p)
        r = p.add_run(subtitle)
        set_run_font(r, "Arial", 10.5, MUTED)
        p.paragraph_format.space_after = Pt(2)
        line = doc.add_paragraph()
        line.paragraph_format.space_after = Pt(6)
        p_pr = line._p.get_or_add_pPr()
        borders = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "12")
        bottom.set(qn("w:space"), "1")
        bottom.set(qn("w:color"), TEAL)
        borders.append(bottom)
        p_pr.append(borders)
        return
    table = doc.add_table(rows=1, cols=2)
    set_table_geometry(table, [1540, 7820], rtl=rtl)
    for cell in table.row_cells(0):
        set_cell_shading(cell, WHITE)
    logo_cell, text_cell = table.row_cells(0)
    if rtl:
        logo_cell, text_cell = text_cell, logo_cell
    p = logo_cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    shape = p.add_run().add_picture(str(LOGO), width=Inches(0.84))
    set_picture_alt(shape, "WhiteDns TG logo")
    p = text_cell.paragraphs[0]
    if rtl:
        set_rtl(p)
    r = p.add_run(title)
    set_run_font(r, "Arial" if rtl else "Calibri", 22, DARK, True)
    p.paragraph_format.space_after = Pt(3)
    p2 = text_cell.add_paragraph()
    if rtl:
        set_rtl(p2)
    r = p2.add_run(subtitle)
    set_run_font(r, "Arial" if rtl else "Calibri", 10.5, MUTED)
    p2.paragraph_format.space_after = Pt(2)
    line = doc.add_paragraph()
    line.paragraph_format.space_after = Pt(6)
    p_pr = line._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "12")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), TEAL)
    borders.append(bottom)
    p_pr.append(borders)


def add_para(doc, text, rtl=False, bold_prefix=None, color=None, italic=False, after=5):
    p = doc.add_paragraph()
    if rtl:
        set_rtl(p)
    if bold_prefix and text.startswith(bold_prefix):
        r = p.add_run(bold_prefix)
        set_run_font(r, "Arial" if rtl else "Calibri", 10.5, color or DARK, True)
        text = text[len(bold_prefix):]
    r = p.add_run(text)
    set_run_font(r, "Arial" if rtl else "Calibri", 10.5, color, italic=italic)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.20
    return p


def add_heading(doc, text, level=1, rtl=False):
    p = doc.add_heading(text, level=level)
    if rtl:
        set_rtl(p)
    return p


def add_bullet(doc, text, rtl=False):
    p = doc.add_paragraph(style="List Bullet")
    if rtl:
        set_rtl(p)
    p.paragraph_format.left_indent = Inches(0.375)
    p.paragraph_format.first_line_indent = Inches(-0.188)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(text)
    set_run_font(r, "Arial" if rtl else "Calibri", 10.4)


def add_callout(doc, title, body, rtl=False, fill=LIGHT_BLUE):
    table = doc.add_table(rows=1, cols=1)
    set_table_geometry(table, [9360], rtl=rtl)
    cell = table.cell(0, 0)
    set_cell_shading(cell, fill)
    p = cell.paragraphs[0]
    if rtl:
        set_rtl(p)
    r = p.add_run(title)
    set_run_font(r, "Arial" if rtl else "Calibri", 10.4, DARK, True)
    r = p.add_run(body)
    set_run_font(r, "Arial" if rtl else "Calibri", 10.4, DARK)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)


def add_dns_table(doc, headers, rtl=False):
    table = doc.add_table(rows=1, cols=5)
    set_table_geometry(table, [760, 1420, 2500, 2500, 2180], rtl=rtl)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    mark_header_row(table.rows[0])
    for index, value in enumerate(headers):
        cell = hdr[index]
        set_cell_shading(cell, DARK)
        p = cell.paragraphs[0]
        if rtl:
            set_rtl(p)
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(value)
        set_run_font(r, "Arial" if rtl else "Calibri", 9.4, WHITE, True)
    for row in DNS_ROWS:
        cells = table.add_row().cells
        for index, value in enumerate(row):
            p = cells[index].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if rtl:
                set_rtl(p)
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(value)
            set_run_font(r, "Arial" if rtl else "Calibri", 9.4, DARK, index in (1, 2))
            if index == 3:
                set_cell_shading(cells[index], LIGHT_BLUE)
    return table


def add_checklist_table(doc, rows, rtl=False):
    table = doc.add_table(rows=1, cols=2)
    set_table_geometry(table, [820, 8540], rtl=rtl)
    table.style = "Table Grid"
    mark_header_row(table.rows[0])
    for index, title in enumerate((("Done", "Check") if not rtl else ("انجام", "بررسی"))):
        cell = table.rows[0].cells[index]
        set_cell_shading(cell, DARK)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if rtl:
            set_rtl(p)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(title)
        set_run_font(r, "Arial" if rtl else "Calibri", 9.5, WHITE, True)
    for item in rows:
        cells = table.add_row().cells
        p = cells[0].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run("☐")
        set_run_font(r, "Arial", 12, TEAL, True)
        p = cells[1].paragraphs[0]
        if rtl:
            set_rtl(p)
        r = p.add_run(item)
        set_run_font(r, "Arial" if rtl else "Calibri", 10.2, DARK)


def add_sources(doc, sources, rtl=False):
    add_heading(doc, "منابع رسمی" if rtl else "Official References", 1, rtl)
    for label, url in sources:
        add_bullet(doc, f"{label}: {url}", rtl)


def build_english():
    doc = Document()
    configure_document(doc)
    add_title(doc, "WhiteDns TG Private Front", "Beginner-friendly Cloudflare domain setup guide | English edition")
    add_callout(doc, "What you need: ", "one domain you own, a free Cloudflare account, and approximately 15 minutes. You do not need a VPS for this CfProxy method.")

    add_heading(doc, "1. Understand What You Are Building", 1)
    add_para(doc, "WhiteDns TG opens a local Telegram proxy on your phone. In Private front mode, the app sends Telegram WebSocket traffic through hostnames under your own Cloudflare-managed domain.")
    add_para(doc, "Example flow:")
    add_callout(doc, "", "Telegram -> WhiteDns TG -> kws2.example.com -> Cloudflare edge -> Telegram WebSocket data center", fill=LIGHT_GRAY)
    add_callout(doc, "Important: ", "The Telegram origin IP addresses go into Cloudflare DNS. Cloudflare edge IP addresses are selected automatically after you enable the orange-cloud Proxied option. Do not paste scanner results into DNS.", fill=GOLD)

    add_heading(doc, "2. Buy or Choose a Domain", 1)
    add_para(doc, "Use an inexpensive dedicated domain that you own, such as example.com. Do not reuse a domain that hosts an important website, login page, or email system.")
    add_bullet(doc, "Correct app input: example.com")
    add_bullet(doc, "Incorrect: https://example.com")
    add_bullet(doc, "Incorrect: kws2.example.com")
    add_bullet(doc, "Incorrect: example.com/apiws")

    add_heading(doc, "3. Add the Domain to Cloudflare", 1)
    for title, body in [
        ("Step 1", "Create or sign in to your account at https://dash.cloudflare.com/."),
        ("Step 2", "Click Add a domain, enter your domain, and choose the Free plan."),
        ("Step 3", "Cloudflare will show two nameservers. Open the website where you purchased the domain and replace the old nameservers with the two Cloudflare nameservers."),
        ("Step 4", "Return to Cloudflare and click Check nameservers. Continue only when the domain status becomes Active. Activation can take several minutes and occasionally up to 24 hours."),
    ]:
        add_heading(doc, title, 2)
        add_para(doc, body)

    add_heading(doc, "4. Configure Cloudflare", 1)
    add_heading(doc, "SSL/TLS", 2)
    add_para(doc, "Open SSL/TLS -> Overview and select Flexible. Then open SSL/TLS -> Edge Certificates and confirm that Universal SSL is enabled.")
    add_callout(doc, "Dedicated-domain rule: ", "Flexible mode is appropriate for this specific CfProxy setup. Do not use this domain for sensitive websites or account logins.", fill=GOLD)
    add_heading(doc, "WebSockets", 2)
    add_para(doc, "Open Network, find WebSockets, and turn it On.")

    add_heading(doc, "5. Create the Six DNS Records", 1)
    add_para(doc, "Open DNS -> Records. Click Add record for each row below. Every record must use the orange-cloud Proxied status and TTL Auto.")
    add_dns_table(doc, ("Type", "Name", "Origin IPv4", "Proxy status", "TTL"))
    add_callout(doc, "Do not add: ", "AAAA records, CNAME records, wildcard records, or manually selected Cloudflare edge IP addresses.", fill=RED)

    add_heading(doc, "6. Verify DNS Before Opening the App", 1)
    add_para(doc, "Wait approximately five minutes. On Windows, open PowerShell and run:")
    add_callout(doc, "", "Resolve-DnsName kws2.example.com", fill=LIGHT_GRAY)
    add_para(doc, "Replace example.com with your own domain.")
    add_para(doc, "Correct result: Cloudflare edge addresses such as 104.x.x.x or 172.67.x.x.")
    add_para(doc, "Incorrect result: 149.154.167.51. This means the record is DNS only. Return to Cloudflare and enable the orange cloud.")

    add_heading(doc, "7. Configure WhiteDns TG", 1)
    for title, body in [
        ("Step 1", "Open WhiteDns TG and stop the proxy if it is already running."),
        ("Step 2", "Open Settings and select Private front."),
        ("Step 3", "Enter only your base domain, such as example.com."),
        ("Step 4", "Tap Validate domain. Continue only when validation succeeds."),
        ("Step 5", "Return to Proxy, start the proxy, and tap Check."),
        ("Step 6", "When Route works appears, tap Apply in Telegram and confirm the proxy inside Telegram."),
    ]:
        add_heading(doc, title, 2)
        add_para(doc, body)

    add_heading(doc, "8. Troubleshooting", 1)
    problems = [
        ("DNS failed", "The domain is not active, a DNS record is missing, or the base domain was entered incorrectly."),
        ("Route failed or tcp_timeout", "The selected Cloudflare edge may be blocked on that network. Tap Check once and allow the adaptive selector to test a small bounded set of official Cloudflare edges."),
        ("websocket_read_timeout", "Confirm the six records are Proxied, SSL mode is Flexible, and WebSockets are enabled."),
        ("HTTP 403", "Disable restrictive WAF, bot, or rate-limit rules on this dedicated domain."),
        ("Certificate error", "Confirm Universal SSL is enabled, then wait for certificate issuance."),
        ("Works on one ISP only", "Test MCI, Irancell, Rightel, and home internet separately. No route is guaranteed to work on every network."),
    ]
    table = doc.add_table(rows=1, cols=2)
    set_table_geometry(table, [2450, 6910])
    table.style = "Table Grid"
    mark_header_row(table.rows[0])
    for idx, label in enumerate(("Message", "What to do")):
        set_cell_shading(table.rows[0].cells[idx], DARK)
        p = table.rows[0].cells[idx].paragraphs[0]
        r = p.add_run(label)
        set_run_font(r, size=9.5, color=WHITE, bold=True)
    for problem, action in problems:
        cells = table.add_row().cells
        r = cells[0].paragraphs[0].add_run(problem)
        set_run_font(r, size=9.5, color=DARK, bold=True)
        r = cells[1].paragraphs[0].add_run(action)
        set_run_font(r, size=9.5, color=DARK)

    add_heading(doc, "9. Final Checklist", 1)
    add_checklist_table(doc, [
        "Cloudflare shows the domain status as Active.",
        "SSL/TLS mode is Flexible and Universal SSL is enabled.",
        "WebSockets is On.",
        "All six DNS records exist and show the orange cloud.",
        "PowerShell resolves kws2.yourdomain.com to Cloudflare IP addresses.",
        "WhiteDns TG Validate domain succeeds.",
        "WhiteDns TG Check reports Route works on the target Iranian network.",
    ])
    add_callout(doc, "Operational advice: ", "Keep at least one separate backup domain. A private domain is less exposed than a shared public domain, but no CDN route can be guaranteed against every ISP or DPI policy.", fill=GOLD)

    add_sources(doc, [
        ("WhiteDns TG repository", "https://github.com/DarkPoesidon/WhiteDnsTelegramProxy"),
        ("Upstream CfProxy setup", "https://github.com/Flowseal/tg-ws-proxy/blob/main/docs/CfProxy.md"),
        ("Cloudflare DNS proxy status", "https://developers.cloudflare.com/dns/proxy-status/"),
        ("Cloudflare WebSockets", "https://developers.cloudflare.com/network/websockets/"),
    ])
    path = OUT / "WhiteDns-TG-Private-Front-Setup-EN.docx"
    doc.save(path)
    return path


def build_farsi():
    doc = Document()
    configure_document(doc, rtl=True)
    add_title(doc, "راهنمای ساخت Front خصوصی WhiteDns TG", "آموزش گام‌به‌گام تنظیم دامنه Cloudflare برای کاربران مبتدی | نسخه فارسی", True)
    add_callout(doc, "وسایل لازم: ", "یک دامنه که مالک آن هستید، یک حساب رایگان Cloudflare و حدود ۱۵ دقیقه زمان. برای این روش CfProxy نیازی به VPS ندارید.", True)

    add_heading(doc, "۱. ابتدا بدانید چه چیزی می‌سازید", 1, True)
    add_para(doc, "WhiteDns TG روی گوشی شما یک پروکسی محلی تلگرام ایجاد می‌کند. در حالت Front خصوصی، برنامه ترافیک WebSocket تلگرام را از زیردامنه‌های دامنه شخصی شما که روی Cloudflare قرار دارد عبور می‌دهد.", True)
    add_para(doc, "مسیر نمونه:", True)
    add_callout(doc, "", "Telegram -> WhiteDns TG -> kws2.example.com -> Cloudflare edge -> Telegram WebSocket data center", True, LIGHT_GRAY)
    add_callout(doc, "نکته بسیار مهم: ", "IPهای مبدا تلگرام را داخل DNS کلادفلر وارد می‌کنید. IPهای لبه Cloudflare بعد از روشن کردن ابر نارنجی به‌صورت خودکار انتخاب می‌شوند. نتیجه اسکنر IP را داخل DNS وارد نکنید.", True, GOLD)

    add_heading(doc, "۲. یک دامنه بخرید یا انتخاب کنید", 1, True)
    add_para(doc, "یک دامنه ارزان و اختصاصی که مالک آن هستید انتخاب کنید؛ مثلاً example.com. بهتر است این دامنه برای سایت مهم، صفحه ورود یا ایمیل استفاده نشود.", True)
    add_bullet(doc, "ورودی درست در برنامه: example.com", True)
    add_bullet(doc, "ورودی اشتباه: https://example.com", True)
    add_bullet(doc, "ورودی اشتباه: kws2.example.com", True)
    add_bullet(doc, "ورودی اشتباه: example.com/apiws", True)

    add_heading(doc, "۳. دامنه را به Cloudflare اضافه کنید", 1, True)
    for title, body in [
        ("گام ۱", "در آدرس https://dash.cloudflare.com/ حساب بسازید یا وارد حساب خود شوید."),
        ("گام ۲", "روی Add a domain بزنید، نام دامنه را وارد کنید و پلن Free را انتخاب کنید."),
        ("گام ۳", "کلادفلر دو Nameserver به شما نشان می‌دهد. وارد سایتی شوید که دامنه را از آن خریده‌اید و Nameserverهای قبلی را با این دو مورد جایگزین کنید."),
        ("گام ۴", "به کلادفلر برگردید و Check nameservers را بزنید. فقط وقتی وضعیت دامنه Active شد ادامه دهید. فعال‌سازی معمولاً چند دقیقه زمان می‌برد و گاهی ممکن است تا ۲۴ ساعت طول بکشد."),
    ]:
        add_heading(doc, title, 2, True)
        add_para(doc, body, True)

    add_heading(doc, "۴. تنظیمات Cloudflare را انجام دهید", 1, True)
    add_heading(doc, "SSL/TLS", 2, True)
    add_para(doc, "به SSL/TLS و سپس Overview بروید و حالت Flexible را انتخاب کنید. سپس در SSL/TLS -> Edge Certificates مطمئن شوید Universal SSL روشن است.", True)
    add_callout(doc, "قانون دامنه اختصاصی: ", "حالت Flexible برای همین روش CfProxy مناسب است. از این دامنه برای سایت حساس یا ورود به حساب کاربری استفاده نکنید.", True, GOLD)
    add_heading(doc, "WebSockets", 2, True)
    add_para(doc, "به بخش Network بروید، گزینه WebSockets را پیدا کنید و آن را روشن کنید.", True)

    add_heading(doc, "۵. شش رکورد DNS را بسازید", 1, True)
    add_para(doc, "به DNS -> Records بروید. برای هر ردیف جدول روی Add record بزنید. تمام رکوردها باید ابر نارنجی Proxied و TTL برابر Auto داشته باشند.", True)
    add_dns_table(doc, ("نوع", "نام", "IP مبدا", "وضعیت پروکسی", "TTL"), True)
    add_callout(doc, "اضافه نکنید: ", "رکورد AAAA، رکورد CNAME، رکورد wildcard یا IP لبه Cloudflare که با اسکنر پیدا شده است.", True, RED)

    add_heading(doc, "۶. قبل از باز کردن برنامه DNS را بررسی کنید", 1, True)
    add_para(doc, "حدود پنج دقیقه صبر کنید. در ویندوز PowerShell را باز کنید و دستور زیر را اجرا کنید:", True)
    add_callout(doc, "", "Resolve-DnsName kws2.example.com", True, LIGHT_GRAY)
    add_para(doc, "به‌جای example.com دامنه خودتان را وارد کنید.", True)
    add_para(doc, "نتیجه درست: IPهای کلادفلر مانند 104.x.x.x یا 172.67.x.x.", True)
    add_para(doc, "نتیجه اشتباه: 149.154.167.51. در این حالت رکورد DNS only است. به کلادفلر برگردید و ابر نارنجی را روشن کنید.", True)

    add_heading(doc, "۷. WhiteDns TG را تنظیم کنید", 1, True)
    for title, body in [
        ("گام ۱", "WhiteDns TG را باز کنید و اگر پروکسی روشن است ابتدا آن را Stop کنید."),
        ("گام ۲", "به Settings بروید و Front خصوصی را انتخاب کنید."),
        ("گام ۳", "فقط دامنه پایه را وارد کنید؛ برای مثال example.com."),
        ("گام ۴", "روی بررسی دامنه یا Validate domain بزنید. فقط اگر تست موفق شد ادامه دهید."),
        ("گام ۵", "به تب Proxy برگردید، پروکسی را روشن کنید و Check را بزنید."),
        ("گام ۶", "وقتی پیام Route works را دیدید، روی Apply in Telegram بزنید و پروکسی را داخل تلگرام تایید کنید."),
    ]:
        add_heading(doc, title, 2, True)
        add_para(doc, body, True)

    add_heading(doc, "۸. رفع خطاهای رایج", 1, True)
    problems = [
        ("DNS failed", "دامنه هنوز Active نشده، یکی از رکوردها وجود ندارد یا دامنه پایه را اشتباه وارد کرده‌اید."),
        ("Route failed یا tcp_timeout", "ممکن است IP لبه کلادفلر روی آن شبکه مسدود باشد. یک بار Check را بزنید تا انتخاب‌گر تطبیقی تعداد محدودی IP رسمی را تست کند."),
        ("websocket_read_timeout", "بررسی کنید هر شش رکورد Proxied باشند، SSL روی Flexible باشد و WebSockets روشن باشد."),
        ("HTTP 403", "قانون سخت‌گیرانه WAF، Bot یا Rate Limit را برای این دامنه اختصاصی غیرفعال کنید."),
        ("خطای گواهی", "روشن بودن Universal SSL را بررسی کنید و برای صدور گواهی کمی صبر کنید."),
        ("فقط روی یک اپراتور کار می‌کند", "همراه اول، ایرانسل، رایتل و اینترنت خانگی را جداگانه تست کنید. هیچ مسیری روی همه شبکه‌ها تضمین‌شده نیست."),
    ]
    table = doc.add_table(rows=1, cols=2)
    set_table_geometry(table, [2800, 6560], rtl=True)
    table.style = "Table Grid"
    mark_header_row(table.rows[0])
    for idx, label in enumerate(("پیام", "راه‌حل")):
        set_cell_shading(table.rows[0].cells[idx], DARK)
        p = table.rows[0].cells[idx].paragraphs[0]
        set_rtl(p)
        r = p.add_run(label)
        set_run_font(r, "Arial", 9.5, WHITE, True)
    for problem, action in problems:
        cells = table.add_row().cells
        p = cells[0].paragraphs[0]
        set_rtl(p)
        r = p.add_run(problem)
        set_run_font(r, "Arial", 9.5, DARK, True)
        p = cells[1].paragraphs[0]
        set_rtl(p)
        r = p.add_run(action)
        set_run_font(r, "Arial", 9.5, DARK)

    add_heading(doc, "۹. چک‌لیست نهایی", 1, True)
    add_checklist_table(doc, [
        "وضعیت دامنه در کلادفلر Active است.",
        "حالت SSL/TLS روی Flexible است و Universal SSL روشن است.",
        "گزینه WebSockets روشن است.",
        "هر شش رکورد DNS وجود دارند و ابر نارنجی دارند.",
        "PowerShell برای kws2.yourdomain.com IP کلادفلر نشان می‌دهد.",
        "گزینه بررسی دامنه در WhiteDns TG موفق می‌شود.",
        "گزینه Check روی شبکه ایرانی موردنظر پیام Route works نشان می‌دهد.",
    ], True)
    add_callout(doc, "پیشنهاد عملیاتی: ", "حداقل یک دامنه پشتیبان جداگانه داشته باشید. دامنه خصوصی کمتر از دامنه عمومی مشترک در معرض مسدود شدن است، اما هیچ مسیر CDN در برابر تمام سیاست‌های ISP یا DPI تضمین دائمی ندارد.", True, GOLD)

    add_sources(doc, [
        ("مخزن WhiteDns TG", "https://github.com/DarkPoesidon/WhiteDnsTelegramProxy"),
        ("راهنمای اصلی CfProxy", "https://github.com/Flowseal/tg-ws-proxy/blob/main/docs/CfProxy.md"),
        ("راهنمای DNS کلادفلر", "https://developers.cloudflare.com/dns/proxy-status/"),
        ("راهنمای WebSockets کلادفلر", "https://developers.cloudflare.com/network/websockets/"),
    ], True)
    path = OUT / "WhiteDns-TG-Private-Front-Setup-FA.docx"
    doc.save(path)
    return path


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    en = build_english()
    fa = build_farsi()
    print(en)
    print(fa)
