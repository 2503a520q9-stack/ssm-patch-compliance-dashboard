"""
Run this script to automatically generate the PowerPoint presentation file (.pptx):
   python -m pip install python-pptx
   python generate_ppt.py
"""

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
except ImportError:
    print("Please install python-pptx first: python -m pip install python-pptx")
    exit(1)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Color Palette
DARK_BG = RGBColor(17, 21, 28)
CARD_BG = RGBColor(30, 36, 48)
TEXT_LIGHT = RGBColor(240, 244, 248)
TEXT_MUTED = RGBColor(148, 163, 184)
GREEN = RGBColor(0, 230, 118)
YELLOW = RGBColor(255, 214, 0)
RED = RGBColor(255, 23, 68)
BLUE = RGBColor(41, 182, 246)

def set_slide_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = DARK_BG

# Slide 1: Title
slide_layout = prs.slide_layouts[6]
s1 = prs.slides.add_slide(slide_layout)
set_slide_background(s1)

title_box = s1.shapes.add_textbox(Inches(1.5), Inches(2.0), Inches(10.33), Inches(3.5))
tf = title_box.text_frame
tf.word_wrap = True

p1 = tf.paragraphs[0]
p1.text = "🛡️ Patch Compliance Light Board"
p1.font.size = Pt(44)
p1.font.bold = True
p1.font.color.rgb = TEXT_LIGHT
p1.alignment = PP_ALIGN.CENTER

p2 = tf.add_paragraph()
p2.text = "A Serverless Fleet Compliance Monitor and 3-LED Operations Dashboard\npowered by AWS Systems Manager & AWS Lambda"
p2.font.size = Pt(20)
p2.font.color.rgb = TEXT_MUTED
p2.alignment = PP_ALIGN.CENTER

p3 = tf.add_paragraph()
p3.text = "\nEnvironment: AWS Learner Lab  |  Interface: Streamlit & VS Code"
p3.font.size = Pt(14)
p3.font.color.rgb = BLUE
p3.alignment = PP_ALIGN.CENTER

# Slide 2: Problem Statement
s2 = prs.slides.add_slide(slide_layout)
set_slide_background(s2)

tb = s2.shapes.add_textbox(Inches(1), Inches(0.8), Inches(11.3), Inches(1))
p = tb.text_frame.paragraphs[0]
p.text = "⚠️ Problem Statement & Challenges"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = TEXT_LIGHT

content_box = s2.shapes.add_textbox(Inches(1), Inches(2.2), Inches(11.3), Inches(4.5))
tf = content_box.text_frame
tf.word_wrap = True

points = [
    ("🚨 Enterprise Patching Risks", "Unpatched operating systems are the #1 attack vector for security breaches and CVE exploits. Auditing servers manually is slow, inconsistent, and error-prone."),
    ("🔍 The Operational Gap", "Navigating deep AWS cloud consoles to inspect compliance takes too long during critical patching windows. Operations teams need an instant, glanceable status board."),
    ("⏳ The Reboot Blindspot", "Servers often install patches but remain vulnerable until rebooted. Without clear 'Pending Reboot' tracking, systems remain exposed to exploits.")
]

for title, desc in points:
    p_t = tf.add_paragraph()
    p_t.text = title
    p_t.font.size = Pt(20)
    p_t.font.bold = True
    p_t.font.color.rgb = BLUE
    
    p_d = tf.add_paragraph()
    p_d.text = desc + "\n"
    p_d.font.size = Pt(15)
    p_d.font.color.rgb = TEXT_MUTED

# Slide 3: The 3-LED Concept
s3 = prs.slides.add_slide(slide_layout)
set_slide_background(s3)

tb = s3.shapes.add_textbox(Inches(1), Inches(0.8), Inches(11.3), Inches(1))
p = tb.text_frame.paragraphs[0]
p.text = "💡 The Solution: 3-LED Operations Light Board"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = TEXT_LIGHT

states = [
    ("🟢 COMPLIANT", "100% of managed instances satisfy baseline patch policies. Zero missing security updates and zero pending reboots.", GREEN, Inches(1)),
    ("🟡 PENDING", "Updates are installed requiring a system reboot (InstalledPendingRebootCount > 0), or a scan is in progress.", YELLOW, Inches(5)),
    ("🔴 NON-COMPLIANT", "One or more instances are missing critical or high security patches (MissingCount > 0).", RED, Inches(9))
]

for title, desc, color, left in states:
    box = s3.shapes.add_textbox(left, Inches(2.2), Inches(3.3), Inches(4.2))
    tf = box.text_frame
    tf.word_wrap = True
    
    pt = tf.paragraphs[0]
    pt.text = title
    pt.font.size = Pt(22)
    pt.font.bold = True
    pt.font.color.rgb = color
    
    pd = tf.add_paragraph()
    pd.text = "\n" + desc
    pd.font.size = Pt(15)
    pd.font.color.rgb = TEXT_MUTED

# Slide 4: System Architecture
s4 = prs.slides.add_slide(slide_layout)
set_slide_background(s4)

tb = s4.shapes.add_textbox(Inches(1), Inches(0.8), Inches(11.3), Inches(1))
p = tb.text_frame.paragraphs[0]
p.text = "🏗️ End-to-End System Architecture"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = TEXT_LIGHT

cb = s4.shapes.add_textbox(Inches(1), Inches(2.0), Inches(11.3), Inches(4.5))
tf = cb.text_frame
tf.word_wrap = True

arch_steps = [
    "1. EC2 Fleet (Amazon Linux): Runs AWS SSM Agent; communicates over outbound HTTPS 443 with LabRole.",
    "2. AWS Systems Manager (Patch Manager): Scans nodes against AWS-DefaultPatchBaseline and stores compliance states.",
    "3. AWS Lambda Backend (PatchComplianceEvaluator): Queries SSM APIs, executes 3-LED decision logic.",
    "4. Lambda Function URL: Public HTTPS endpoint with CORS enabled; eliminates client AWS credential storage.",
    "5. Streamlit Frontend (VS Code): Renders glowing 3-LED panel, KPI counters, and interactive instance breakdown table."
]

for step in arch_steps:
    p = tf.add_paragraph()
    p.text = step + "\n"
    p.font.size = Pt(16)
    p.font.color.rgb = TEXT_LIGHT

# Slide 5: Results & Conclusion
s5 = prs.slides.add_slide(slide_layout)
set_slide_background(s5)

tb = s5.shapes.add_textbox(Inches(1), Inches(0.8), Inches(11.3), Inches(1))
p = tb.text_frame.paragraphs[0]
p.text = "🎯 Validation & Project Conclusion"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = TEXT_LIGHT

cb = s5.shapes.add_textbox(Inches(1), Inches(2.0), Inches(11.3), Inches(4.5))
tf = cb.text_frame
tf.word_wrap = True

results = [
    ("✅ 100% Learner Lab Compatible", "Successfully bypassed session token restrictions by decoupling frontend via Lambda Function URL."),
    ("✅ True 3-Tier Serverless Architecture", "Zero server maintenance costs for the API layer; zero open inbound ports on EC2."),
    ("✅ Instant Glanceable Visibility", "Replaced multi-step AWS console navigation with a real-time, interactive 3-LED operations light board.")
]

for title, desc in results:
    pt = tf.add_paragraph()
    pt.text = title
    pt.font.size = Pt(20)
    pt.font.bold = True
    pt.font.color.rgb = GREEN
    
    pd = tf.add_paragraph()
    pd.text = desc + "\n"
    pd.font.size = Pt(15)
    pd.font.color.rgb = TEXT_MUTED

prs.save("Patch_Compliance_Light_Board_Presentation.pptx")
print("✅ Presentation saved as Patch_Compliance_Light_Board_Presentation.pptx")
