# Data validation at row level should consider:
1. purpose is to check internal consistency of data
2. six categories of validation:
   1. 'anchor' completeness: such as project_code should not be null
   2. conposite identity intergrity/consistency: such as document_id should matches its constituent fields
   3. temporal (date) sequence logic: such as submission_date <= review_return_date
   4. categorical inter-dependency / cross-field validation: such as approval_code = "APP" then submission_closed = "YES"
   5. status & version regrssion: such as revision should be incremented
   6. relational invariants / fact table rule: such as submission_session_subject should be same within forward fill boundary since this is one submission session package
   7. integrate those validations into row health score. may flag as critical, warning, informational.