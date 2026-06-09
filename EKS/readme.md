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
3. Integration of pipeine for search, retreival, scoring, searching adjustment, filtering,  and AI answering
4. consider SSOT and schema driven approach. allow user to add new document, metadata without modification of codes.

## Metadata
1. Metedata for project, discipline, department, document, etc. will have same schema setup as in dcc/config/schemas
2. source location metadata shall be considered for document:
- file name
- file location
- section or paragraph
- page
3. Enigneering object metadata (on hold)
4. cross-reference metadata will provide relationship between related document and tags.
5. consider different levels for project metadata, document metadata, and chunk metadata.

## Embedding Strategy
1. avoid embedding polution by separating metadata, admistravtive data, and primarily vector embedding
2. consdier hybrid approac. For metadata that affects meaning, prepend a small contextual header before embedding. but store full metadata separately.
3. vector database to consider structure: embedding, text, and metadata