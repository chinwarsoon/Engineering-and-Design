with open('eks/workplan/phase_4_retrieval_pipeline_workplan.md', 'r', encoding='utf-8') as f:
    c = f.read()

PLANNED = '\U0001f537 PLANNED'
OLD = f'| R38 | Retrieval Pipeline | Asset-Aware Retrieval            | Filter and expand context by asset attributes and asset-to-document graph relationships | {PLANNED} |\n\n**Status Legend:**'
NEW = f'| R38 | Retrieval Pipeline | Asset-Aware Retrieval            | Filter and expand context by asset attributes and asset-to-document graph relationships | {PLANNED} |\n| R40 | Retrieval Pipeline | Asset Semantic Search            | Query `eks_assets` Qdrant collection for fuzzy/semantic asset property queries; merge with Neo4j structured results before scoring | {PLANNED} |\n\n**Status Legend:**'

assert OLD in c, "Target not found"
c = c.replace(OLD, NEW, 1)

with open('eks/workplan/phase_4_retrieval_pipeline_workplan.md', 'w', encoding='utf-8') as f:
    f.write(c)
print("R40 scope row inserted")
