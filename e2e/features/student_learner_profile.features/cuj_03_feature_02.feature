Feature: Search achievement, goal, learner account and learner profile data based on various Student Learner Profile attributes

    Scenario: SNHU Administrator wants to search for learner based on correct first name
        Given SNHU Administrator has access to SLP service to search learner by first name
            When SNHU Administrator wants to search learner based on correct first name
                Then the relevant learner corresponding to given first name is retrieved and returned to user
    
    Scenario: SNHU Administrator wants to search for learner based on incorrect first name
        Given SNHU Administrator has privilege to access SLP service to search learner by first name
            When SNHU Administrator wants to search learner based on incorrect first name
                Then SLP service will return empty response as no learner exists for given incorrect first name

    Scenario: SNHU Administrator wants to search for learner based on correct email address
        Given SNHU Administrator has access to SLP service to search learner by email address
            When SNHU Administrator wants to search learner based on correct email address
                Then the relevant learner corresponding to given email address is retrieved and returned to user

    Scenario: SNHU Administrator wants to search for learner based on incorrect email address format
        Given SNHU Administrator has access to SLP service to search learner by incorrect email address format
            When SNHU Administrator wants to search learner based on incorrect email address format
                Then getting error response learner email invalid
    
    Scenario: SNHU Administrator wants to search for learner based on incorrect email address
        Given SNHU Administrator has privilege to access SLP service to search learner by email address
            When SNHU Administrator wants to search learner based on incorrect email address
                Then SLP service will return empty response as no learner exists for given incorrect email address

    Scenario: SNHU Administrator wants to search for goal by providing correct goal name
        Given SNHU Administrator has access to SLP service to search goal by goal name
            When SNHU Administrator wants to search goal based on correct goal name
                Then the relevant goal corresponding to given goal name is retrieved and returned to user
    
    Scenario: SNHU Administrator wants to search for goal by providing an incorrect goal name
        Given SNHU Administrator has privilege to access SLP service to search goal by goal name
            When SNHU Administrator wants to search goal by providing an incorrect goal name
                Then SLP service will return empty response as no goal exists for given incorrect goal name

    Scenario: SNHU Administrator wants to search for achievements by providing achievement type
        Given SNHU Administrator has access to SLP service to search achievements by achievement type
            When SNHU Administrator wants to search achievements based on correct achievement type
                Then the relevant achievements corresponding to given achievement type is retrieved and returned to user

    Scenario: SNHU Administrator wants to search for learner profile by providing correct learner_id
        Given SNHU Administrator has access to SLP service to search learner profile by learner_id
            When SNHU Administrator wants to search learner profile based on correct learner_id
                Then the relevant learner profile corresponding to given learner_id is retrieved and returned to user
    
    Scenario: SNHU Administrator wants to search for learner profile by providing an incorrect learner_id
        Given SNHU Administrator has privilege to access SLP service to search learner profile by learner_id
            When SNHU Administrator wants to search learner profile by providing an incorrect learner_id
                Then SLP service will return empty response as no learner profile exists for given incorrect learner_id