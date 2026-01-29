import sys
from PyQt6.QtGui import QImage, QPainter, QColor, QFont
from PyQt6.QtCore import Qt

def create_icon(filename, symbol, color):
    # Create valid PNG image with QImage
    size = 64
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw simple symbol
    painter.setPen(QColor(color))
    font = painter.font()
    font.setPixelSize(40)
    font.setBold(True)
    painter.setFont(font)
    
    rect = image.rect()
    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, symbol)
    painter.end()
    
    image.save(filename)
    print(f"Created {filename}")

if __name__ == "__main__":
    from PyQt6.QtGui import QGuiApplication
    app = QGuiApplication(sys.argv)
    create_icon("assets/images/email_icon.png", "@", "#555555")
    create_icon("assets/images/password_icon.png", "🔒", "#555555")
