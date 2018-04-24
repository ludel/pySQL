from Enum.operatorEnum import Operator


class Condition:

    def __init__(self, right, operator: Operator, left):
        self.right = right
        self.operator = operator
        self.left = left

    def __str__(self):
        return f"{self.right} {self.operator.value} {self.left}"
