Purpose for this workplan:
1. refer to foler dcc/config/schemas/,all schema files are reorganized, some are renamed.
2. changes to those schemas are proposed and recorded in recursive_schema_loader_workplan.md.
3. those schema files will be used by dcc_engine_pipeline.py which is under dcc/worflow folder.
4. dcc_engine_pipeline.py is designed to initiate, map, process the excel file 'submittal and rfi tracker lists.xlsx'.
5. the excel file is a dcc transmittal register.
6. the final output from dcc_engine_pipeline.py is to produce a processed data to eliminate nulls, validate data, perfomr calculatoin, error handling, etc.
7. dcc_engine_pipeline has initiation_engine, mapper_engine, processor_engine, reporting_engine, and schema_engine.
8. study all related details first.
9. prepared a workplan to integrate all changes from schema files into dcc_engine_pipeline, test the whole pipline. Changes form schema files may include:
- name, key, reference change,
- schema structure change,
- parameter change,
- workflow change,
10. in the workplan, list down all related functions, workflow charts, i/o, global paramters.
11. the plan must be segragated to test each function one by one since changes in schema files may cause misalignments and propergation of coding errors.