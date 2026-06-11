# Setion 1. Project Requirements
`EKS` is project folder for `Enigneering Knowledge System`. The purpose of EKS is to establish a hybrid RAG system to allow users to ask and retreive related data from:
1. a set of engineering document sush as standards, procedures, checklist, workflows, drawings, etc. or
2. a set of specific project engineering document such as project specifications, procedures, checklist, forms, datasheets, drawings, calculatoins, etc.

## EKS Architecture
Architecture of this `Engineering Knowledge System` should consider the following engines and layers:
1. Establishing knowledge base which should consider:
- Collection of orinignal documents in PDF, MS Word, MS Excel, AutoCAD Drawing, MicronStation Drawing template.
- Establishing document registry and store documnt metadata in structured database.
- Establishing chunk registry, consider parent-child chunking.
- Embedding and Establishing vector storage.
- Establishing knowledge relationship graph.
2. Building up standalone interactive user equiry interface.
3. Integration of retrieal and scoring pipeline for:
- metadata filtering
- relationship expansion
- vector or key words search
- searching adjustment
- retreival, scoring
- reranking
- contet assembly
- LLM answering
4. consider SSOT and schema driven approach. allow user to add new document, metadata without modification of codes.
5. consider canonical data model as foundation for metadata schems, relationship graphs, retriveal filters, and future integrations.
6. consider knowledge layers to be split into:
- `Raw Document` as soure of truth
- `Structured Metadata` for filtering
- `Vector Knowledge` for semantic search
- `Knowledge Graph` for relationship kowledge
- `Retrieval Cache` for performance
7. consider revision management for document
- preserve all revisions
- support latest revision filtering
- support superseded document lookup
- support revision-aaware retrieval
8. knowledge graph to consider relationship between:
- document to document
- document to engineering object
- engineering object to engineering object
- engineering object to metadata
- metadata to metadata
9. consider source traceability such as doucment_number, revision, page, section, chunk id, source file, etc.
10. consider plug-in architecture for
- document parsers for different document types such as df, docx, xlsx, dwg, dgn, etc.
- metadata extractor for different engineering objects or items, such as design document, equipment, instrument, vales, pipelines, etc.
- different embedding providers to consider openAI, ollama, or custom
- different vector database
11. consider database:
- postgreSQL or duckdb for metadate DB
- Qdrant or langchain for vector DB
- Neo4j for graph DB

## Metadata
1. Metedata for project, discipline, department, document, etc. will have same schema setup as in dcc/config/schemas
2. source location metadata shall be considered for document:
- file name
- file location
- section or paragraph
- page
3. Enigneering object and its metadata
- project_title and project_number
- area and area_code
- discipline and discipline_code
- department and department_code
- document_type and document_type_code
- document and document_number
- plant item and item tag
- item tag and its properties
4. cross-reference metadata will provide relationship between related document and tags.
5. consider different levels for project metadata, document metadata, and chunk metadata.

## Embedding Strategy
1. avoid embedding polution by separating metadata, admistravtive data, and primarily vector embedding
2. consdier hybrid approac. For metadata that affects meaning, prepend a small contextual header before embedding. but store full metadata separately.
3. vector database to consider structure: embedding, text, and metadata