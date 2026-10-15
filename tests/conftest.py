"""ให้ pytest หาแพ็กเกจ wtc เจอโดยไม่ต้องติดตั้งโปรเจกต์"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
