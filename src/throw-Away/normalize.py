def normalize_percentages(percentages):
    total = sum(percentages)
    return [(p / total) * 100 for p in percentages]

# Example usage:
percentages = [28.32, 17.21]
normalized_percentages = normalize_percentages(percentages)

print(normalized_percentages)

