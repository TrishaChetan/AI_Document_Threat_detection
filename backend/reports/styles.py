from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()


TITLE_STYLE = styles["Title"].clone("GuardexTitle")
TITLE_STYLE.alignment = TA_CENTER
TITLE_STYLE.textColor = HexColor("#0B5394")
TITLE_STYLE.fontSize = 28
TITLE_STYLE.spaceAfter = 20


SUBTITLE_STYLE = styles["Heading2"].clone("GuardexSubtitle")
SUBTITLE_STYLE.alignment = TA_CENTER
SUBTITLE_STYLE.textColor = HexColor("#555555")
SUBTITLE_STYLE.fontSize = 16
SUBTITLE_STYLE.spaceAfter = 25


HEADING_STYLE = styles["Heading1"].clone("GuardexHeading")
HEADING_STYLE.textColor = HexColor("#1F4E79")
HEADING_STYLE.spaceBefore = 15
HEADING_STYLE.spaceAfter = 10


SUBHEADING_STYLE = styles["Heading2"].clone("GuardexSubheading")
SUBHEADING_STYLE.textColor = HexColor("#2F75B5")
SUBHEADING_STYLE.spaceBefore = 10
SUBHEADING_STYLE.spaceAfter = 6


BODY_STYLE = styles["BodyText"].clone("GuardexBody")
BODY_STYLE.leading = 20
BODY_STYLE.spaceAfter = 8


FOOTER_STYLE = styles["Normal"].clone("GuardexFooter")
FOOTER_STYLE.alignment = TA_CENTER
FOOTER_STYLE.fontSize = 8
FOOTER_STYLE.textColor = HexColor("#666666")