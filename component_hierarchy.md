# Component Hierarchy

* Main Content
    * Projects Tab Content
        * New Project Form
            * Form Title
            * Text Inputs
        * Project List
            * Project List Row (single project description)
    * Datasets Tab Content
        * New dataset form
            * Form title
            * Form inputs (text, files, selects)
        * Transform existing dataset form
            * Form title
            * Form inputs (selects)
    * Featurize Tab Content
        * Featurize existing dataset form
            * Form Title
            * Form inputs (text, selects, checkboxes)
        * Upload features form
            * Form Title
            * Form inputs (files, text, selects)
        * Plot existing featureset form
            * Form Title Row
            * Form inputs (selects)
        * Features plot(s)
    * Models tab content
        * Build model form
            * Form title
            * Form inputs (selects, text, checkboxes)
        * Results/status message
    * Predict tab content
        * Predict form
            * Form title
            * Form inputs (selects)
        * Status message/prediction results table

# State:

* Projects Tab: Projects, projects form input, user auth
* Datasets Tab: Projects, Datasets, datasets form inputs (text/files), available transformations, job status/results info?, user auth
* Featurize Tab: Projects, Datasets, Featuresets, available features, Featurize Form Inputs, Job Status/Results info, Plots, user auth
* Models Tab: Projects, Featuresets, available model types & hyperparams, job status/results info, user auth
* Predict Tab: Projects, Models, Datasets, job status/results info, user auth

Proposal: Server-provided state (projects, datasets, featuresets, models, predictions, results/status message, plots, user auth, etc) live in "Main Content" root component, and tab-specific form field values live in respective parent tab components

# Considerations

* How generic & reusable (fewer types) vs. specific (many different types) components should be (e.g. form input rows - lots of variations in layout & type)
* Should server own all state, even intermediary form field values (Stefan - Google Docs - (throttled) sync w/ every change)?
* Tabs vs. separate pages
