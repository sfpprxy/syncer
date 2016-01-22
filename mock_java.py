# 根据三边长动态求长方体体积
class Box:
    def calculate(self, w, d, h):
        return w * d * h

box1 = Box()
print(box1.calculate(2, 3, 4))