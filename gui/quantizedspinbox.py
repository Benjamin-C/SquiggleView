import math
from typing import Tuple
from PyQt6.QtGui import QValidator
from PyQt6.QtWidgets import QDoubleSpinBox
import re

class QuantizedSpinBox(QDoubleSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__bigPre = "kMgt"
        self.__smallPre = "munpfa"

    def stepBy(self, count):
        self.setValue(((self.value() // self.singleStep()) + count) * self.singleStep())

    def textFromValue(self, value):
        neg = "-" if value < 0 else ""
        value = abs(value)
        bigPre = self.__bigPre
        smallPre = self.__smallPre
        if 1e3 <= value:
            for i in range(len(bigPre)-1):
                if value > 1e3:
                    value /= 1e3
                    bigPre = bigPre[1:]
            return f"{neg}{value:.3g}{bigPre[0]}"
        elif 1 <= value < 1e3:
            return f"{neg}{value:.3g}"
        elif 0 < value < 1:
            value *= 1e3
            for i in range(len(smallPre)-1):
                if value < 1:
                    value *= 1e3
                    smallPre = smallPre[1:]
            return f"{neg}{value:.3g}{smallPre[0]}"
        else:
            return "0"
        
    def valueFromText(self, text: str) -> float:
        if len(text) == 0:
            return 0
        neg = -1 if text[0] == "-" else 1
        factor = 1
        if text.endswith(self.suffix()):
            text = text[:-len(self.suffix())]
        if text[-1] in self.__smallPre:
            for i in range(len(self.__smallPre)):
                factor /= 1e3
                if self.__smallPre[i] == text[-1]:
                    break
            text = text[:-1]
        if text[-1] in self.__bigPre:
            for i in range(len(self.__bigPre)):
                factor *= 1e3
                if self.__bigPre[i] == text[-1]:
                    break
            text = text[:-1]
        num = float(text) * factor
        exp = math.log10(num)
        siz = math.trunc(exp)
        sig = round(10 ** (exp - siz), 2)
        num = neg * sig * (10 ** siz)
        return num
    
    def validate(self, input: str, pos: int) -> Tuple[QValidator.State, str, int]:
        regex = "^-?[0-9.]+[" + self.__smallPre + self.__bigPre + "]?(?:" + self.suffix().replace("/", "\\/") + ")?$"
        if len(input) > 0:
            res = re.search(regex, input)
            if res is not None:
                return (QValidator.State.Acceptable, input, pos)
            else:
                return (QValidator.State.Invalid, input, pos)
        return (QValidator.State.Acceptable, "", 0)