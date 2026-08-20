with open('eks/knowledge.json', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the problematic pattern
# The line has ... resolved."" but should be ... resolved."
fixed = content.replace(' resolved."""', ' resolved."')

with open('eks/knowledge.json', 'w', encoding='utf-8') as f:
    f.write(fixed)

print('Fixed.')