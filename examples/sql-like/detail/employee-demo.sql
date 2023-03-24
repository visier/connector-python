SELECT 
    EmployeeID, 
    Union_Status, 
    Direct_Manager.Gender AS "DMG",
    Direct_Manager.Vaccination_Status
FROM Employee
WHERE isFemale = TRUE AND
    isHighPerformer = TRUE AND
    Visier_Time BETWEEN date("2020-01-01") AND date("2021-12-31")