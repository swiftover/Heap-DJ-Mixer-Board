def smooth_value(previous: float, new: float, factor: float = 0.7):
    factor = max(0.0, min(1.0, factor))
    return previous * factor + new * (1.0 - factor)
