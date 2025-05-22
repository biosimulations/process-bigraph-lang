Metadata:
    name: "Caravagna2010 - Tumour suppression by immune system"
    level: 1
    version: 1
    Packages:
        BioSimulators[sbml, simulate, csv, kisao]
    Description:
        Ipsum Dolor
    Annotations: <None>

Dependencies:
    BIOMD0000000912_dependency:
        name: "Caravagna2010 - Tumour suppression by immune system"
        type: sbml::SBMLFile<2.4>
        Options:
            source: "Caravagna2010.xml"

Declaractions:
    Constants: <None>
    Templates:
        BIOMD0000000912:
            name: "Model: Caravagna2010.xml"
            type: sbml::model<sbml::SBMLFile<2.4>>
            bindings:
                Time: "kisao::0000832",
                T: "/sbml:sbml/sbml:model/sbml:listOfSpecies/sbml:species[@id='T']"
                E: "/sbml:sbml/sbml:model/sbml:listOfSpecies/sbml:species[@id='E']"
                I: "/sbml:sbml/sbml:model/sbml:listOfSpecies/sbml:species[@id='I']"

Inputs : <None>
Outputs:
    #createCSV,

Actions:
    importModelFile:
        name: "Fetch SBML data model"
        task: sbml::create_model
        options:
            source: #BIOMD0000000912_dependency,
            template: #BIOMD0000000912

    modifyModelFile:
        name: "Modify SBML data model",
        task: sbml::set_model_value,
        options:
            template: #BIOMD000000091",
            target: "/sbml:sbml/sbml:model/sbml:listOfParameters/sbml:parameter[@id='r2']/@value",
            newValue: 0.1799

    simulateUTC
        name: "Simulate (Uniform Time Course)",
        type: "simulate::nonspatial::UniformTimeCourse",
        options:
            model: #BIOMD0000000912,
            solver: kisao::0000019,
            initalTime: 0,
            outputStartTime: 0,
            outputEndTime: 1000,
            numberOfSteps: 5000
        Notes:
            "Actual Solver Name: CVODE"

    collectData:
        name: "Collect Data",
        type: simulate::results::createDataReport,
        options:
            MetaData:
                bogus: "values"
            DataSets:
                #simulateUTC.$model.*
    createCSV:
        name: "Create CSV Report",
        task: csv::createFromDataReport,
        options:
            source: #collectData,
            includeOriginModelIDs: true
